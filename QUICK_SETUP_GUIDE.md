# BidCraft Subcontractor System - Quick Setup Guide

## ✅ What's Been Delivered

### Core Files
1. **streamlit_app_enhanced.py** - Main application with 3-tab interface
2. **subcontractor_engine.py** - Recommendation engine with confidence scoring
3. **subcontractors.csv** - Sample database with 20 Arizona subcontractors
4. **subcontractor_schema.json** - JSON schema for data validation
5. **requirements.txt** - Python dependencies
6. **SUBCONTRACTOR_SYSTEM_DOCS.md** - Comprehensive documentation
7. **README_updated.md** - Updated project README

## 🚀 Installation (5 minutes)

### Step 1: Setup Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Files
Make sure these files are in the same directory:
- ✓ streamlit_app_enhanced.py
- ✓ subcontractor_engine.py  
- ✓ subcontractors.csv
- ✓ requirements.txt

### Step 3: Run the App
```bash
streamlit run streamlit_app_enhanced.py
```

Opens automatically at http://localhost:8501

## 🎯 Testing the System

### Test Case 1: Medical Office Project
1. **Tab 1 - Bid Analysis**
   - Project Name: "Phoenix Medical Office Buildout"
   - Location: Phoenix
   - Project Type: "Medical Office"
   - Upload a text file with keywords: concrete, electrical, plumbing, hvac
   
2. **Tab 2 - Subcontractor Suggestions**
   - Click "Generate Subcontractor Recommendations"
   - Should see 4 trade categories with 3 recommendations each
   - Look for medical-specialized subcontractors with high confidence scores

3. **Tab 3 - Database Stats**
   - Should show 20 total subcontractors
   - 12 trades covered
   - Average rating ~4.7/5.0

### Expected Results
- **Concrete**: Valley Concrete Solutions (~90% confidence)
- **Electrical**: Bright Spark Electric (~99% confidence)
- **Plumbing**: Premier Plumbing AZ (~92% confidence)
- **HVAC**: Cool Breeze HVAC (~93% confidence)

## 📊 System Verification

Run this test to verify the engine works:

```bash
python -c "
from subcontractor_engine import SubcontractorRecommendationEngine

engine = SubcontractorRecommendationEngine('subcontractors.csv')
stats = engine.get_statistics()

print(f'✓ Loaded {stats[\"total_subcontractors\"]} subcontractors')
print(f'✓ Covering {stats[\"trades_covered\"]} trade categories')
print(f'✓ Average rating: {stats[\"avg_rating\"]:.2f}/5.0')
print('✓ System ready!')
"
```

Expected output:
```
✓ Loaded 20 subcontractors
✓ Covering 12 trade categories
✓ Average rating: 4.71/5.0
✓ System ready!
```

## 🎨 Key Features Delivered

### ✅ Trade Category Mapping
- Automatically maps detected scope keywords to trade categories
- Example: "concrete" detected → matches "concrete" trade subs

### ✅ Location-Based Filtering  
- Filters by service area coverage
- Example: Phoenix project → prioritizes Phoenix-serving subs

### ✅ Confidence Scoring (0-100)
- Trade match: 40 points
- Location: 20 points
- Rating: 15 points
- Experience: 10 points
- Bonding capacity: 10 points
- Specialty match: 5 points

### ✅ Interactive UI
- Three-tab interface
- Adjustable confidence threshold
- Expandable detail cards
- Export to text file

### ✅ Detailed Explanations
Each recommendation shows:
- Why it was matched (✓ indicators)
- Considerations (⚠ warnings)
- Contact information
- Specialties and service areas
- Confidence score breakdown

## 📝 Customization Guide

### Add More Subcontractors
Edit `subcontractors.csv` and add rows following this format:

```csv
company_name,trade_category,service_areas,contact_email,phone,specialties,rating,years_experience,license_number,bonding_capacity,notes
New Company,electrical,"Phoenix,Mesa",contact@new.com,602-555-0000,"commercial,industrial",4.5,10,ROC-999999,1000000,Fast turnaround
```

**Trade categories must be one of:**
concrete, steel, electrical, plumbing, hvac, framing, drywall, roof, flooring, sitework, demolition, paint

### Adjust Confidence Scoring
Edit `subcontractor_engine.py`, find `calculate_confidence_score()` method:

```python
# Example: Increase location importance
if matching_areas:
    score += 30  # Changed from 20
```

### Change UI Settings
Edit `streamlit_app_enhanced.py`:

```python
# Default minimum confidence
min_confidence = st.slider("Min Confidence Score", value=20)  # Changed from 30

# Default results per trade  
top_n = st.slider("Results per Trade", value=5)  # Changed from 3
```

## 🔧 Troubleshooting

### Issue: Module not found error
```bash
pip install streamlit==1.31.0
```

### Issue: CSV not loading
- Verify `subcontractors.csv` is in same directory
- Check for UTF-8 encoding
- Ensure no syntax errors in CSV

### Issue: No recommendations showing
- Lower minimum confidence threshold to 20%
- Check scope keywords are detected in Tab 1
- Verify location spelling matches service areas

### Issue: Confidence scores seem wrong
- Review CSV data (ratings should be 0-5, bonding in dollars)
- Check that service_areas include project location
- Validate years_experience is reasonable

## 📚 Documentation

- **Full System Docs**: `SUBCONTRACTOR_SYSTEM_DOCS.md`
- **Data Schema**: `subcontractor_schema.json`
- **Project README**: `README_updated.md`

## ✅ Deliverables Checklist

- [x] Working subcontractor recommendation engine
- [x] Trade category mapping system
- [x] Location-based filtering logic
- [x] Confidence scoring algorithm (0-100 scale)
- [x] Detailed match explanations
- [x] Subcontractor Suggestions tab functional
- [x] Interactive filtering controls
- [x] Export functionality
- [x] Database statistics dashboard
- [x] CSV schema (20 sample records)
- [x] JSON schema for validation
- [x] Comprehensive documentation

## 🎉 You're Ready!

The subcontractor recommendation system is fully functional and tested. The engine successfully:
- Loads 20 subcontractors covering 12 trades
- Maps scope keywords to trade categories
- Filters by location (Phoenix metro area)
- Calculates confidence scores (avg ~90% for good matches)
- Provides detailed explanations
- Exports recommendations

Start the app and test it with the medical office example above!

## 🆘 Support

If you encounter issues:
1. Check this guide first
2. Review `SUBCONTRACTOR_SYSTEM_DOCS.md`
3. Verify all files are present
4. Run the verification test above
5. Check Python version (3.8+ required)

**Next Steps:**
- Add more subcontractors to the CSV
- Customize confidence scoring weights
- Integrate with real bid documents
- Deploy to Streamlit Cloud
