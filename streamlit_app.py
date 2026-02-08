import streamlit as st
import os
import re
import uuid
from datetime import datetime

APP_NAME = "BidCraft MVP"

st.set_page_config(page_title=APP_NAME, layout="centered")

st.title(APP_NAME)
st.write("Upload a bid doc → get a draft estimate + commodity risk notes → export-ready summary.")

def naive_extract_scope(text: str) -> dict:
    keywords = [
        "concrete", "steel", "electrical", "plumbing", "hvac", "framing",
        "drywall", "roof", "flooring", "sitework", "demolition", "paint"
    ]
    found = sorted({k for k in keywords if re.search(rf"\b{k}\b", text, re.I)})

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

    line_items = []
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
    contingency = round(subtotal * 0.08)
    total = subtotal + contingency

    return {
        "detected_scope": found,
        "line_items": line_items,
        "subtotal": subtotal,
        "contingency": contingency,
        "total": total
    }


def commodity_risk_recommendations(detected_scope):
    risks = []
    if "steel" in [x.lower() for x in detected_scope]:
        risks.append({
            "commodity": "Steel",
            "risk": "Price volatility / lead times",
            "recommendation": "Lock pricing with escalation clause or alternate suppliers."
        })

    if "concrete" in [x.lower() for x in detected_scope]:
        risks.append({
            "commodity": "Concrete",
            "risk": "Regional supply constraints",
            "recommendation": "Confirm batch plant capacity; add schedule buffer."
        })

    if not risks:
        risks.append({
            "commodity": "General",
            "risk": "Unknown scope",
            "recommendation": "Request clarifications + add contingency."
        })

    return risks


project_name = st.text_input("Project Name", placeholder="Phoenix Medical Office Buildout")
notes = st.text_area("Notes / Assumptions", placeholder="Anything the estimator should assume...")

uploaded_file = st.file_uploader("Upload a doc (TXT recommended for MVP)", type=["pdf", "docx", "txt"])

if uploaded_file:
    file_id = str(uuid.uuid4())[:8]
    filename = uploaded_file.name

    if filename.endswith(".txt"):
        extracted_text = uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        extracted_text = f"Uploaded file: {filename}\nUser notes: {notes}\n(Parsing PDF/DOCX is stubbed.)"

    scope = naive_extract_scope(extracted_text)
    risks = commodity_risk_recommendations(scope["detected_scope"])

    summary = {
        "project_name": project_name or "Untitled Project",
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "source_file": filename,
        "notes": notes,
        "detected_scope": scope["detected_scope"],
        "line_items": scope["line_items"],
        "subtotal": scope["subtotal"],
        "contingency": scope["contingency"],
        "total": scope["total"],
        "commodity_risks": risks
    }

    st.subheader("Detected Scope")
    st.write(", ".join(summary["detected_scope"]) if summary["detected_scope"] else "None detected")

    st.subheader("Estimate Draft")
    for li in summary["line_items"]:
        st.write(f"**{li['category']}** — ${li['estimated_cost']:,}")
        st.caption(li["assumption"])

    st.markdown(f"""
    ### Totals
    - Subtotal: **${summary['subtotal']:,}**
    - Contingency (8%): **${summary['contingency']:,}**
    - TOTAL: **${summary['total']:,}**
    """)

    st.subheader("Commodity Risks & Recommendations")
    for r in summary["commodity_risks"]:
        st.write(f"**{r['commodity']}**: {r['risk']}")
        st.caption(r["recommendation"])

    export_text = f"""{APP_NAME} — Export-Ready Bid Summary
Project: {summary['project_name']}
Created: {summary['created_at']}
Source: {summary['source_file']}

Notes:
{summary['notes']}

Detected Scope:
{", ".join(summary['detected_scope']) if summary['detected_scope'] else "None detected"}

Estimate Draft:
"""    

    for li in summary["line_items"]:
        export_text += f"- {li['category']}: ${li['estimated_cost']:,} ({li['assumption']})\n"

    export_text += f"""
Subtotal: ${summary['subtotal']:,}
Contingency (8%): ${summary['contingency']:,}
TOTAL: ${summary['total']:,}

Commodity Risks & Recommendations:
"""

    for r in summary["commodity_risks"]:
        export_text += f"- {r['commodity']}: {r['risk']} → {r['recommendation']}\n"

    st.download_button(
        label="Download Export Summary",
        data=export_text,
        file_name=f"bid_summary_{file_id}.txt",
        mime="text/plain"
    )
