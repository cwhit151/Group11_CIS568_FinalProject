# Subcontractor Recommendation System - Documentation

## Overview
The Subcontractor Recommendation System is a core component of BidCraft that matches detected bid scope to relevant subcontractors using intelligent filtering and confidence scoring.

## Architecture

### Components

1. **Subcontractor Database** (`subcontractors.csv`)
   - Flat-file CSV storage for MVP
   - Contains 20 sample Arizona subcontractors
   - Easily expandable without code changes

2. **Recommendation Engine** (`subcontractor_engine.py`)
   - Core matching logic
   - Confidence scoring algorithm
   - Trade category mapping
   - Location-based filtering

3. **Streamlit UI** (`streamlit_app_enhanced.py`)
   - Three-tab interface
   - Real-time recommendations
   - Interactive filtering
   - Export capabilities

## Features Implemented

### ✅ Trade Category Mapping
- Automatically maps detected scope keywords to trade categories
- Supports multi-category trades (e.g., framing/drywall)
- Extensible mapping system via `TRADE_CATEGORY_MAP`

**Supported Trade Categories:**
- Concrete
- Steel  
- Electrical
- Plumbing
- HVAC
- Framing
- Drywall
- Roofing
- Flooring
- Sitework
- Demolition
- Painting

### ✅ Location-Based Filtering
- Filters subcontractors by service area
- Supports multiple service areas per subcontractor
- Adjustable location override in UI
- Scoring bonus for location match

### ✅ Confidence Scoring Algorithm

**Score Breakdown (0-100 scale):**

| Factor | Max Points | Description |
|--------|-----------|-------------|
| Trade Match | 40 | Exact trade category match |
| Location | 20 | Services project location |
| Rating | 15 | Performance rating (0-5 scale) |
| Experience | 10 | Years in business (capped at 20 yrs) |
| Bonding Capacity | 10 | Adequate for project value |
| Specialty Match | 5 | Project type alignment |
| **TOTAL** | **100** | |

**Confidence Tiers:**
- 🟢 **80-100%**: Excellent match
- 🟡 **60-79%**: Good match
- 🟠 **30-59%**: Acceptable match
- ❌ **<30%**: Filtered out (adjustable)

### ✅ Explanation System
Each recommendation includes detailed explanations:
- Why the subcontractor was matched
- Strengths (✓) and considerations (⚠)
- Key differentiators
- Project-specific notes

### ✅ UI Features

**Tab 1: Bid Analysis**
- Upload bid documents
- Auto-detect scope keywords
- Generate cost estimates
- Commodity risk analysis

**Tab 2: Subcontractor Suggestions**
- Filtered recommendations by trade
- Confidence scoring with visual indicators
- Expandable detail cards
- Adjustable settings:
  - Minimum confidence threshold
  - Number of results per trade
  - Location override
- Export recommendations to text file

**Tab 3: Database Stats**
- Total subcontractor count
- Trade coverage metrics
- Average ratings & experience
- Service area coverage
- Database management instructions

## Data Schema

### CSV Format
```csv
company_name,trade_category,service_areas,contact_email,phone,specialties,rating,years_experience,license_number,bonding_capacity,notes
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| company_name | string | Yes | Business name |
| trade_category | enum | Yes | One of 12 standard trades |
| service_areas | string[] | Yes | Comma-separated cities |
| contact_email | email | Yes | Bid contact email |
| phone | string | Yes | Primary phone |
| specialties | string[] | Yes | Comma-separated specialties |
| rating | float | Yes | 0.0 - 5.0 scale |
| years_experience | int | Yes | Years in business |
| license_number | string | Yes | State license/ROC number |
| bonding_capacity | int | Yes | Max bonding in USD |
| notes | string | No | Additional context |

### JSON Schema
See `subcontractor_schema.json` for full JSON Schema definition with validation rules.

## Usage Guide

### Running the Application

1. **Install dependencies:**
   ```bash
   pip install streamlit==1.31.0
   ```

2. **Place files in same directory:**
   - `streamlit_app_enhanced.py`
   - `subcontractor_engine.py`
   - `subcontractors.csv`

3. **Run Streamlit:**
   ```bash
   streamlit run streamlit_app_enhanced.py
   ```

4. **Access UI:**
   - Opens automatically at `http://localhost:8501`

### Workflow

1. **Upload Bid Document** (Tab 1)
   - Enter project details (name, location, type)
   - Upload TXT/PDF/DOCX file
   - Review detected scope and estimates

2. **Get Recommendations** (Tab 2)
   - Navigate to Subcontractor Suggestions tab
   - Adjust filters if needed
   - Click "Generate Subcontractor Recommendations"
   - Review matches with confidence scores
   - Export recommendations

3. **Review Database** (Tab 3)
   - Check coverage statistics
   - Verify service areas
   - Plan database expansion

## Extending the System

### Adding More Subcontractors

**Option 1: Edit CSV directly**
```bash
# Open in spreadsheet software or text editor
vim subcontractors.csv
```

**Option 2: Programmatic import**
```python
import csv

new_subs = [
    {
        'company_name': 'New Company',
        'trade_category': 'electrical',
        'service_areas': 'Phoenix,Mesa',
        # ... other fields
    }
]

with open('subcontractors.csv', 'a', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=...)
    writer.writerows(new_subs)
```

### Adding New Trade Categories

1. **Update `TRADE_CATEGORY_MAP`** in `subcontractor_engine.py`:
   ```python
   TRADE_CATEGORY_MAP = {
       "concrete": ["concrete"],
       "new_trade": ["new_trade"],  # Add here
       # ...
   }
   ```

2. **Update scope detection** in `naive_extract_scope()`:
   ```python
   keywords = [
       "concrete", "steel", ..., "new_trade"  # Add here
   ]
   ```

3. **Add to JSON schema** in `subcontractor_schema.json`

### Customizing Confidence Scoring

Edit the `calculate_confidence_score()` method in `subcontractor_engine.py`:

```python
# Adjust point allocations
if subcontractor.trade_category == trade_category:
    score += 50  # Changed from 40
```

Scoring is flexible and can be tuned based on:
- Regional priorities
- Client preferences
- Historical performance data

### Adding New Filters

Example: Add insurance requirement filter

```python
def recommend_subcontractors(
    self,
    detected_scope: List[str],
    location: str = "Phoenix",
    min_insurance: int = 1000000,  # New parameter
    # ...
):
    # Add filtering logic
    candidates = [sub for sub in self.subcontractors 
                 if sub.insurance_coverage >= min_insurance]
```

## API Reference

### SubcontractorRecommendationEngine

**Methods:**

```python
__init__(csv_path: str = "subcontractors.csv")
```
Initialize engine with subcontractor data.

```python
get_trade_categories(detected_scope: List[str]) -> List[str]
```
Map scope keywords to trade categories.

```python
calculate_confidence_score(
    subcontractor: Subcontractor,
    trade_category: str,
    location: str = None,
    project_type: str = None,
    bid_value: int = None
) -> tuple[float, dict]
```
Calculate confidence score and explanation.

```python
recommend_subcontractors(
    detected_scope: List[str],
    location: str = "Phoenix",
    project_type: str = None,
    bid_value: int = None,
    min_confidence: float = 30.0,
    top_n: int = 3
) -> Dict[str, List[Dict[str, Any]]]
```
Generate recommendations for all trades in scope.

```python
get_all_service_areas() -> List[str]
```
Get unique service areas from database.

```python
get_statistics() -> Dict[str, Any]
```
Get database statistics.

## Testing

### Manual Testing Checklist

- [ ] Upload bid document with multiple scope items
- [ ] Verify correct scope detection
- [ ] Check recommendations appear for each trade
- [ ] Validate confidence scores are reasonable
- [ ] Test location filtering
- [ ] Adjust confidence threshold
- [ ] Change results per trade
- [ ] Export recommendations
- [ ] Review database statistics
- [ ] Test with different project locations

### Sample Test Cases

**Test Case 1: Medical Office Project**
- Scope: concrete, electrical, plumbing, HVAC
- Location: Phoenix
- Expected: High-confidence matches for medical-specialized subs

**Test Case 2: Retail Buildout**
- Scope: framing, drywall, flooring, paint
- Location: Scottsdale
- Expected: Matches for finishes trades

**Test Case 3: Industrial Facility**
- Scope: steel, sitework, concrete
- Location: Mesa
- Expected: Heavy civil/structural specialists

## Performance Considerations

- **CSV Loading**: Cached via `@st.cache_resource`
- **Search Complexity**: O(n) per trade category
- **Scaling**: Efficient up to ~1000 subcontractors
- **Future**: Migrate to SQLite/PostgreSQL for 10k+ records

## Future Enhancements

### Phase 2 Features
- [ ] Historical performance tracking
- [ ] Automated bid solicitation emails
- [ ] Subcontractor availability calendar
- [ ] Price history analysis
- [ ] Multi-project recommendations
- [ ] Machine learning score optimization

### Database Migration
- [ ] SQLite for local deployments
- [ ] PostgreSQL for production
- [ ] Full-text search on specialties
- [ ] Geospatial queries for service areas

### API Development
- [ ] REST API for recommendations
- [ ] Webhook integrations
- [ ] Mobile app support

## Troubleshooting

### Common Issues

**Issue: No recommendations appearing**
- Check minimum confidence threshold (lower it)
- Verify location spelling matches service areas
- Confirm scope keywords are detected

**Issue: Confidence scores seem wrong**
- Review scoring algorithm weights
- Check data quality in CSV
- Validate bonding capacity values

**Issue: CSV not loading**
- Verify file path in `get_recommendation_engine()`
- Check CSV format matches schema
- Look for encoding issues (use UTF-8)

## Support & Contact

For questions or issues with the subcontractor recommendation system:
- Review this documentation
- Check CSV data format
- Verify all required fields are present
- Test with sample data first

## License & Attribution

Part of BidCraft MVP - Bid Preparation Tool
© 2024 - All rights reserved
