import streamlit as st
import os
import re
import uuid
from datetime import datetime
from subcontractor_engine import (
    SubcontractorRecommendationEngine,
    format_recommendation_for_display
)

APP_NAME = "BidCraft MVP"

st.set_page_config(page_title=APP_NAME, layout="wide")

# Initialize recommendation engine
@st.cache_resource
def get_recommendation_engine():
    """Initialize and cache the subcontractor recommendation engine"""
    csv_path = os.path.join(os.path.dirname(__file__), "subcontractors.csv")
    return SubcontractorRecommendationEngine(csv_path)

engine = get_recommendation_engine()

# Session state initialization
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

def naive_extract_scope(text: str) -> dict:
    """Extract scope from bid document text"""
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
    """Generate commodity risk recommendations"""
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


# Main UI
st.title(f"🏗️ {APP_NAME}")
st.markdown("Upload a bid doc → get a draft estimate + commodity risk notes + subcontractor recommendations")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📄 Bid Analysis", "👷 Subcontractor Suggestions", "📊 Database Stats"])

# ==================== TAB 1: BID ANALYSIS ====================
with tab1:
    st.subheader("Upload & Analyze Bid Document")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Project Name", placeholder="Phoenix Medical Office Buildout")
        location = st.selectbox(
            "Project Location",
            options=engine.get_all_service_areas(),
            index=0
        )
    
    with col2:
        project_type = st.text_input("Project Type", placeholder="Medical Office, Retail, Office, etc.")
        notes = st.text_area("Notes / Assumptions", placeholder="Anything the estimator should assume...", height=100)

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
            "location": location,
            "project_type": project_type,
            "detected_scope": scope["detected_scope"],
            "line_items": scope["line_items"],
            "subtotal": scope["subtotal"],
            "contingency": scope["contingency"],
            "total": scope["total"],
            "commodity_risks": risks
        }
        
        # Store in session state
        st.session_state.summary = summary

        # Display results
        st.success("✅ Bid document analyzed successfully!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Detected Scope")
            if summary["detected_scope"]:
                scope_badges = " ".join([f"`{s}`" for s in summary["detected_scope"]])
                st.markdown(scope_badges)
            else:
                st.info("None detected")

            st.subheader("Estimate Draft")
            for li in summary["line_items"]:
                with st.expander(f"**{li['category']}** — ${li['estimated_cost']:,}", expanded=False):
                    st.caption(li["assumption"])

        with col2:
            st.metric("Subtotal", f"${summary['subtotal']:,}")
            st.metric("Contingency (8%)", f"${summary['contingency']:,}")
            st.metric("TOTAL", f"${summary['total']:,}", delta=None)

        st.subheader("Commodity Risks & Recommendations")
        for r in summary["commodity_risks"]:
            with st.expander(f"⚠️ {r['commodity']}: {r['risk']}", expanded=False):
                st.write(r["recommendation"])

        # Export functionality
        export_text = f"""{APP_NAME} — Export-Ready Bid Summary
Project: {summary['project_name']}
Location: {summary['location']}
Type: {summary['project_type']}
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
            label="📥 Download Bid Summary",
            data=export_text,
            file_name=f"bid_summary_{file_id}.txt",
            mime="text/plain"
        )

# ==================== TAB 2: SUBCONTRACTOR SUGGESTIONS ====================
with tab2:
    st.subheader("🔍 Subcontractor Recommendations")
    
    if st.session_state.summary is None:
        st.info("👈 Please upload and analyze a bid document in the 'Bid Analysis' tab first.")
    else:
        summary = st.session_state.summary
        
        # Display project info
        st.markdown(f"""
        **Project:** {summary['project_name']}  
        **Location:** {summary['location']}  
        **Estimated Value:** ${summary['total']:,}  
        **Detected Scope:** {', '.join(summary['detected_scope']) if summary['detected_scope'] else 'None'}
        """)
        
        st.divider()
        
        # Recommendation settings
        with st.expander("⚙️ Recommendation Settings", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                override_location = st.selectbox(
                    "Override Location",
                    options=['Use Project Location'] + engine.get_all_service_areas(),
                    index=0
                )
            with col2:
                min_confidence = st.slider(
                    "Min Confidence Score",
                    min_value=0,
                    max_value=100,
                    value=30,
                    step=5,
                    help="Only show recommendations above this confidence threshold"
                )
            with col3:
                top_n = st.slider(
                    "Results per Trade",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="Number of subcontractors to show per trade category"
                )
        
        # Generate recommendations button
        if st.button("🎯 Generate Subcontractor Recommendations", type="primary"):
            location_to_use = summary['location'] if override_location == 'Use Project Location' else override_location
            
            with st.spinner("Analyzing subcontractor matches..."):
                recommendations = engine.recommend_subcontractors(
                    detected_scope=summary['detected_scope'],
                    location=location_to_use,
                    project_type=summary.get('project_type'),
                    bid_value=summary['total'],
                    min_confidence=min_confidence,
                    top_n=top_n
                )
                st.session_state.recommendations = recommendations
        
        # Display recommendations
        if st.session_state.recommendations:
            recommendations = st.session_state.recommendations
            
            if not recommendations:
                st.warning("No subcontractors found matching the criteria. Try lowering the confidence threshold.")
            else:
                st.success(f"✅ Found recommendations for {len(recommendations)} trade categories")
                
                # Create export data
                export_lines = [
                    f"{APP_NAME} — Subcontractor Recommendations",
                    f"Project: {summary['project_name']}",
                    f"Location: {summary['location']}",
                    f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                    "",
                    "="*80,
                    ""
                ]
                
                # Display by trade category
                for trade, subs in recommendations.items():
                    st.markdown(f"### 🔧 {trade.title()}")
                    
                    export_lines.append(f"\n{trade.upper()}")
                    export_lines.append("-" * 40)
                    
                    if not subs:
                        st.info(f"No subcontractors found for {trade}")
                        export_lines.append("No recommendations found.\n")
                    else:
                        for idx, rec in enumerate(subs, 1):
                            sub = rec['subcontractor']
                            score = rec['confidence_score']
                            explanation = rec['explanation']
                            
                            # UI Display
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"**{idx}. {sub.company_name}**")
                                    st.caption(f"📞 {sub.phone} | ✉️ {sub.contact_email}")
                                    st.caption(f"License: {sub.license_number} | ⭐ {sub.rating}/5.0 | {sub.years_experience} yrs exp")
                                
                                with col2:
                                    # Confidence badge with color
                                    if score >= 80:
                                        badge_color = "🟢"
                                    elif score >= 60:
                                        badge_color = "🟡"
                                    else:
                                        badge_color = "🟠"
                                    st.metric("Confidence", f"{badge_color} {score:.0f}%")
                                
                                # Expandable details
                                with st.expander("📋 View Details"):
                                    st.markdown(f"**Specialties:** {', '.join(sub.specialties)}")
                                    st.markdown(f"**Service Areas:** {', '.join(sub.service_areas)}")
                                    st.markdown(f"**Bonding Capacity:** ${sub.bonding_capacity:,}")
                                    
                                    st.markdown("**Match Analysis:**")
                                    for key, value in explanation.items():
                                        st.markdown(f"- {value}")
                                    
                                    if sub.notes:
                                        st.info(f"💡 {sub.notes}")
                            
                            st.divider()
                            
                            # Export text
                            export_lines.append(f"\n{idx}. {sub.company_name} (Confidence: {score:.0f}%)")
                            export_lines.append(f"   Phone: {sub.phone}")
                            export_lines.append(f"   Email: {sub.contact_email}")
                            export_lines.append(f"   License: {sub.license_number}")
                            export_lines.append(f"   Rating: {sub.rating}/5.0 | Experience: {sub.years_experience} years")
                            export_lines.append(f"   Specialties: {', '.join(sub.specialties)}")
                            export_lines.append(f"   Service Areas: {', '.join(sub.service_areas)}")
                            export_lines.append(f"   Bonding Capacity: ${sub.bonding_capacity:,}")
                            export_lines.append(f"   Notes: {sub.notes}")
                            export_lines.append("")
                
                # Download recommendations
                export_text = "\n".join(export_lines)
                st.download_button(
                    label="📥 Download Subcontractor Recommendations",
                    data=export_text,
                    file_name=f"subcontractor_recommendations_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )

# ==================== TAB 3: DATABASE STATS ====================
with tab3:
    st.subheader("📊 Subcontractor Database Statistics")
    
    stats = engine.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Subcontractors", stats['total_subcontractors'])
    with col2:
        st.metric("Trades Covered", stats['trades_covered'])
    with col3:
        st.metric("Avg Rating", f"{stats['avg_rating']:.1f}/5.0")
    with col4:
        st.metric("Avg Experience", f"{stats['avg_experience']:.0f} yrs")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Trade Category Breakdown")
        for trade, count in sorted(stats['trade_breakdown'].items()):
            st.markdown(f"**{trade.title()}:** {count} subcontractors")
    
    with col2:
        st.markdown("### Service Areas Covered")
        areas_text = ", ".join(stats['service_areas'])
        st.markdown(areas_text)
    
    st.divider()
    
    st.markdown("### 📁 Database Management")
    st.info("""
    The subcontractor database is stored in `subcontractors.csv`. To add more subcontractors:
    1. Download the current CSV file
    2. Add new rows following the same format
    3. Upload the updated CSV file
    
    **CSV Columns:** company_name, trade_category, service_areas, contact_email, phone, 
    specialties, rating, years_experience, license_number, bonding_capacity, notes
    """)
