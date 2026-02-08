# BidCraft

A lightweight MVP demo for an AI-powered bid prep tool:
Upload a bid doc → generate a draft estimate + commodity risk notes → download an export-ready bid summary.

## Features (MVP)
- Single-page web UI
- Upload: PDF / DOCX / TXT
- “AI extraction” (stubbed, structured so you can swap in OpenAI later)
- Commodity risk recommendations (stubbed)
- Export-ready bid summary download (`.txt`)
- No database (flat-file exports)

## Tech Stack
- Python + Flask
- Gunicorn (production server)
- Render hosting (via GitHub)

---

## Local Setup

### 1) Clone + install
```bash
git clone https://github.com/YOURUSER/bid-mvp.git
cd bid-mvp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
