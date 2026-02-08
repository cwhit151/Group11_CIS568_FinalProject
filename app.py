import os
import re
import uuid
from datetime import datetime
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

APP_NAME = "BidCraft MVP"
UPLOAD_DIR = "uploads"
EXPORT_DIR = "exports"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def naive_extract_scope(text: str) -> dict:
    """
    MVP stub: pretend we're extracting scope + quantities.
    Swap this with an LLM call later.
    """
    # Very basic keyword extraction to make the demo feel alive
    keywords = [
        "concrete", "steel", "electrical", "plumbing", "hvac", "framing",
        "drywall", "roof", "flooring", "sitework", "demolition", "paint"
    ]
    found = sorted({k for k in keywords if re.search(rf"\b{k}\b", text, re.I)})

    # Fake quantities/costs so it looks like a real estimator output
    line_items = []
    base_cost_map = {
        "concrete": 220000,
        "steel": 180000,
        "electrical": 95000,
        "plumbing": 88000,
        "hvac": 120000,
        "framing": 65000,
        "drywall": 48000,
        "roof": 72000,
        "flooring": 56000,
        "sitework": 140000,
        "demolition": 52000,
        "paint": 18000,
    }

    for item in found[:8]:
        line_items.append({
            "category": item.title(),
            "assumption": f"Included based on detected scope mention of '{item}'.",
            "estimated_cost": base_cost_map.get(item, 50000)
        })

    if not line_items:
        line_items = [{
            "category": "General Conditions",
            "assumption": "No obvious scope keywords found; defaulting to a generic estimate template.",
            "estimated_cost": 75000
        }]

    subtotal = sum(li["estimated_cost"] for li in line_items)
    contingency = round(subtotal * 0.08)  # 8% contingency for demo
    total = subtotal + contingency

    return {
        "detected_scope": found,
        "line_items": line_items,
        "subtotal": subtotal,
        "contingency": contingency,
        "total": total
    }


def commodity_risk_recommendations(detected_scope: list[str]) -> list[dict]:
    """
    MVP stub: commodity-aware suggestions.
    Later: replace with real commodity feeds + historical volatility.
    """
    risks = []
    if any(x.lower() in {"steel"} for x in detected_scope):
        risks.append({
            "commodity": "Steel",
            "risk": "Price volatility / lead times",
            "recommendation": "Lock pricing with escalation clause or alternate suppliers."
        })
    if any(x.lower() in {"concrete"} for x in detected_scope):
        risks.append({
            "commodity": "Concrete",
            "risk": "Regional supply constraints",
            "recommendation": "Confirm batch plant capacity; add schedule buffer."
        })

    if not risks:
        risks.append({
            "commodity": "General",
            "risk": "Unknown doc scope",
            "recommendation": "Request clarifications + add contingency until scope is confirmed."
        })

    return risks


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", app_name=APP_NAME)


@app.route("/analyze", methods=["POST"])
def analyze():
    project_name = (request.form.get("project_name") or "").strip() or "Untitled Project"
    notes = (request.form.get("notes") or "").strip()

    if "file" not in request.files:
        flash("No file part found. Try again.")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected. Choose a PDF/DOCX/TXT.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Unsupported file type. Use PDF, DOCX, or TXT.")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    file_id = str(uuid.uuid4())[:8]
    stored_name = f"{file_id}_{filename}"
    path = os.path.join(UPLOAD_DIR, stored_name)
    file.save(path)

    # MVP text input: real extraction from PDF/DOCX can come later
    # For now: read TXT, otherwise just use filename + user notes to drive the demo.
    extracted_text = ""
    if ext == "txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_text = f.read()
    else:
        extracted_text = f"Uploaded file: {filename}\nUser notes: {notes}\n(Parsing PDF/DOCX is stubbed for MVP.)"

    scope = naive_extract_scope(extracted_text)
    risks = commodity_risk_recommendations(scope["detected_scope"])

    summary = {
        "app": APP_NAME,
        "project_name": project_name,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "source_file": filename,
        "user_notes": notes,
        "detected_scope": scope["detected_scope"],
        "line_items": scope["line_items"],
        "subtotal": scope["subtotal"],
        "contingency": scope["contingency"],
        "total": scope["total"],
        "commodity_risks": risks
    }

    # Write export
    export_name = f"bid_summary_{file_id}.txt"
    export_path = os.path.join(EXPORT_DIR, export_name)
    with open(export_path, "w", encoding="utf-8") as out:
        out.write(f"{APP_NAME} — Export-Ready Bid Summary\n")
        out.write(f"Project: {summary['project_name']}\n")
        out.write(f"Created: {summary['created_at']}\n")
        out.write(f"Source: {summary['source_file']}\n\n")

        if summary["user_notes"]:
            out.write("Notes:\n")
            out.write(summary["user_notes"] + "\n\n")

        out.write("Detected Scope:\n")
        out.write(", ".join(summary["detected_scope"]) if summary["detected_scope"] else "None detected")
        out.write("\n\n")

        out.write("Estimate Draft:\n")
        for li in summary["line_items"]:
            out.write(f"- {li['category']}: ${li['estimated_cost']:,} ({li['assumption']})\n")
        out.write(f"\nSubtotal: ${summary['subtotal']:,}\n")
        out.write(f"Contingency (8%): ${summary['contingency']:,}\n")
        out.write(f"TOTAL: ${summary['total']:,}\n\n")

        out.write("Commodity Risks & Recommendations:\n")
        for r in summary["commodity_risks"]:
            out.write(f"- {r['commodity']}: {r['risk']} → {r['recommendation']}\n")

    # Render results page using same template
    return render_template("index.html", app_name=APP_NAME, summary=summary, export_file=export_name)


@app.route("/export/<filename>", methods=["GET"])
def export(filename):
    export_path = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(export_path):
        flash("Export not found.")
        return redirect(url_for("index"))
    return send_file(export_path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    # local dev
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
