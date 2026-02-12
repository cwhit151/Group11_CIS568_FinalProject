# BidCraft MVP

A lightweight MVP demo for an AI-powered bid prep tool with intelligent subcontractor recommendations:

**Upload a bid doc → generate draft estimate + commodity risk notes + get matched subcontractors → download export-ready summaries**

## Features

### Core Bid Analysis
- Single-page web UI with tabbed interface
- Upload: PDF / DOCX / TXT
- AI extraction (stubbed, structured for future OpenAI integration)
- Commodity risk recommendations
- Export-ready bid summary download (`.txt`)

### 🆕 Subcontractor Recommendation System
- **Intelligent Matching**: Automatically maps detected scope to relevant trade categories
- **Location Filtering**: Filters subcontractors by service area coverage
- **Confidence Scoring**: 0-100 scale scoring based on:
  - Trade match (40 pts)
  - Location coverage (20 pts)
  - Performance rating (15 pts)
  - Years of experience (10 pts)
  - Bonding capacity (10 pts)
  - Project specialty match (5 pts)
- **Detailed Explanations**: Each recommendation includes match analysis
- **Interactive UI**: Adjustable filters, expandable details, export capabilities
- **Database Stats**: Real-time analytics on subcontractor coverage

## Tech Stack
- Python 3.8+
- Streamlit 1.31.0
- CSV-based data storage (MVP)
- Deployable to Streamlit Cloud, Render, or any Python hosting

---

## Quick Start

### 1) Clone + Install
```bash
git clone https://github.com/YOURUSER/bid-mvp.git
cd bid-mvp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run Locally
```bash
streamlit run streamlit_app_enhanced.py
```

The app will open at `http://localhost:8501`

### 3) Usage Workflow

#### Step 1: Analyze Bid Document (Tab 1)
1. Enter project details:
   - Project name (e.g., "Phoenix Medical Office Buildout")
   - Project location (select from dropdown)
   - Project type (e.g., "Medical Office")
   - Notes/assumptions
2. Upload bid document (TXT recommended for MVP, PDF/DOCX stubbed)
3. Review detected scope and cost estimates

#### Step 2: Get Subcontractor Recommendations (Tab 2)
1. Navigate to "Subcontractor Suggestions" tab
2. Review project summary
3. Adjust settings (optional):
   - Override location
   - Set minimum confidence threshold
   - Adjust results per trade
4. Click "Generate Subcontractor Recommendations"
5. Review recommendations by trade category
6. Expand details to see:
   - Contact information
   - Specialties and service areas
   - Confidence score breakdown
   - Match analysis
7. Download recommendations as text file

#### Step 3: Review Database Coverage (Tab 3)
- View total subcontractors and trade coverage
- Check service areas
- See average ratings and experience
- Learn how to expand the database

---

## Project Structure

```
bid-mvp/
├── streamlit_app_enhanced.py       # Main Streamlit application
├── subcontractor_engine.py         # Recommendation engine logic
├── subcontractors.csv              # Subcontractor database (20 samples)
├── subcontractor_schema.json       # JSON schema for data validation
├── SUBCONTRACTOR_SYSTEM_DOCS.md    # Detailed system documentation
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

### Legacy Files (for reference)
- `streamlit_app.py` - Original simpler version
- `templates/index.html` - Flask template (deprecated)

---

## Subcontractor Database

### Current Coverage
The system includes **20 sample subcontractors** covering:
- Concrete (2)
- Steel (2)
- Electrical (2)
- Plumbing (2)
- HVAC (2)
- Framing (1)
- Drywall (2)
- Roofing (2)
- Flooring (2)
- Sitework (1)
- Demolition (1)
- Painting (1)

**Service Areas**: Phoenix, Scottsdale, Tempe, Mesa, Gilbert, Chandler, Glendale, Peoria, and more

### Adding More Subcontractors

**CSV Format:**
```csv
company_name,trade_category,service_areas,contact_email,phone,specialties,rating,years_experience,license_number,bonding_capacity,notes
```

**Example Row:**
```csv
ABC Plumbing,plumbing,"Phoenix,Mesa",info@abcplumbing.com,602-555-1234,"medical gas,fire sprinklers",4.7,12,ROC-123456,2000000,Certified for medical facilities
```

**Trade Categories (must match exactly):**
- concrete
- steel
- electrical
- plumbing
- hvac
- framing
- drywall
- roof
- flooring
- sitework
- demolition
- paint

See `SUBCONTRACTOR_SYSTEM_DOCS.md` for full schema documentation.

---

## Confidence Scoring Explained

Each subcontractor recommendation receives a 0-100 confidence score:

| Factor | Points | Description |
|--------|--------|-------------|
| **Trade Match** | 40 | Exact match for required trade |
| **Location** | 20 | Services project location |
| **Rating** | 15 | Based on 0-5 performance rating |
| **Experience** | 10 | Years in business (capped at 20) |
| **Bonding** | 10 | Adequate capacity for project value |
| **Specialty** | 5 | Project type alignment |

**Visual Indicators:**
- 🟢 80-100%: Excellent match
- 🟡 60-79%: Good match  
- 🟠 30-59%: Acceptable match
- Below 30%: Filtered out (adjustable)

---

## Deployment Options

### Streamlit Cloud (Recommended for MVP)
1. Push code to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Select `streamlit_app_enhanced.py` as main file
4. Deploy!

### Render
1. Create new Web Service
2. Build: `pip install -r requirements.txt`
3. Start: `streamlit run streamlit_app_enhanced.py --server.port=$PORT`

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app_enhanced.py"]
```

---

## Future Roadmap

### Phase 2: Enhanced Recommendations
- [ ] Historical performance tracking
- [ ] Automated bid solicitation emails
- [ ] Subcontractor availability calendar
- [ ] Price history analysis
- [ ] Machine learning score optimization

### Phase 3: Database Evolution
- [ ] Migrate to SQLite/PostgreSQL
- [ ] Full-text search on specialties
- [ ] Geospatial queries for service areas
- [ ] User-contributed ratings/reviews

### Phase 4: Integration
- [ ] Real AI extraction (OpenAI GPT-4)
- [ ] PDF/DOCX parsing (PyPDF2, python-docx)
- [ ] CRM integration (HubSpot, Salesforce)
- [ ] Email automation
- [ ] Calendar/scheduling integration

---

## Testing

### Sample Test Scenarios

**Medical Office Build (Phoenix)**
- Upload: Medical office bid document
- Expected Scope: electrical, plumbing, HVAC, framing, drywall
- Expected Results: Medical-specialized subcontractors with high confidence scores

**Retail Buildout (Scottsdale)**
- Upload: Retail space bid document  
- Expected Scope: framing, drywall, flooring, paint
- Expected Results: Finishes specialists in Scottsdale area

**Industrial Facility (Mesa)**
- Upload: Warehouse/industrial bid
- Expected Scope: steel, sitework, concrete
- Expected Results: Heavy civil/structural specialists

---

## Troubleshooting

### No Recommendations Showing
- Lower minimum confidence threshold (try 20-30%)
- Verify location matches service areas in database
- Check that scope keywords are detected in Tab 1

### Confidence Scores Seem Low
- Review subcontractor data quality in CSV
- Ensure bonding capacity values are appropriate
- Check that service areas include project location
- Verify ratings are on 0-5 scale

### CSV Not Loading
- Ensure `subcontractors.csv` is in same directory as Python files
- Check CSV format matches schema exactly
- Verify UTF-8 encoding
- Look for syntax errors (missing commas, quotes)

---

## Documentation

- **System Architecture**: See `SUBCONTRACTOR_SYSTEM_DOCS.md`
- **Data Schema**: See `subcontractor_schema.json`
- **API Reference**: In `SUBCONTRACTOR_SYSTEM_DOCS.md`

---

## Contributing

To extend the subcontractor database:
1. Download `subcontractors.csv`
2. Add rows following the schema
3. Validate with `subcontractor_schema.json`
4. Test in the app
5. Submit pull request

---

## License

© 2024 BidCraft - All rights reserved

---

## Support

For questions or issues:
1. Check `SUBCONTRACTOR_SYSTEM_DOCS.md`
2. Review CSV data format
3. Verify Python 3.8+ is installed
4. Test with sample data first

**Built with ❤️ for construction estimators**
