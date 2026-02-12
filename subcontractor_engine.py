"""
Subcontractor Recommendation Engine for BidCraft MVP
Matches detected bid scope to relevant subcontractors with confidence scoring
"""

import csv
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Subcontractor:
    """Data class for subcontractor information"""
    company_name: str
    trade_category: str
    service_areas: List[str]
    contact_email: str
    phone: str
    specialties: List[str]
    rating: float
    years_experience: int
    license_number: str
    bonding_capacity: int
    notes: str


# Trade category mapping: maps detected scope keywords to trade categories
TRADE_CATEGORY_MAP = {
    "concrete": ["concrete"],
    "steel": ["steel"],
    "electrical": ["electrical"],
    "plumbing": ["plumbing"],
    "hvac": ["hvac"],
    "framing": ["framing", "drywall"],
    "drywall": ["drywall", "framing"],
    "roof": ["roof"],
    "flooring": ["flooring"],
    "sitework": ["sitework"],
    "demolition": ["demolition"],
    "paint": ["paint"],
}


# Specialty keyword matching for enhanced recommendations
SPECIALTY_KEYWORDS = {
    "medical": ["medical", "healthcare", "hospital", "clinic"],
    "office": ["office", "commercial", "corporate"],
    "retail": ["retail", "store", "shopping"],
    "industrial": ["industrial", "warehouse", "manufacturing"],
    "institutional": ["school", "university", "government", "institutional"],
}


class SubcontractorRecommendationEngine:
    """Engine for recommending subcontractors based on bid scope and location"""
    
    def __init__(self, csv_path: str = "subcontractors.csv"):
        """Initialize the recommendation engine with subcontractor data"""
        self.subcontractors = []
        self.csv_path = csv_path
        self._load_subcontractors()
    
    def _load_subcontractors(self):
        """Load subcontractors from CSV file"""
        if not os.path.exists(self.csv_path):
            return
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sub = Subcontractor(
                    company_name=row['company_name'],
                    trade_category=row['trade_category'].lower(),
                    service_areas=[area.strip() for area in row['service_areas'].split(',')],
                    contact_email=row['contact_email'],
                    phone=row['phone'],
                    specialties=[s.strip() for s in row['specialties'].split(',')],
                    rating=float(row['rating']),
                    years_experience=int(row['years_experience']),
                    license_number=row['license_number'],
                    bonding_capacity=int(row['bonding_capacity']),
                    notes=row['notes']
                )
                self.subcontractors.append(sub)
    
    def get_trade_categories(self, detected_scope: List[str]) -> List[str]:
        """Map detected scope keywords to trade categories"""
        categories = set()
        for scope_item in detected_scope:
            scope_lower = scope_item.lower()
            if scope_lower in TRADE_CATEGORY_MAP:
                categories.update(TRADE_CATEGORY_MAP[scope_lower])
        return sorted(list(categories))
    
    def calculate_confidence_score(
        self,
        subcontractor: Subcontractor,
        trade_category: str,
        location: str = None,
        project_type: str = None,
        bid_value: int = None
    ) -> tuple[float, dict]:
        """
        Calculate confidence score for a subcontractor recommendation
        Returns: (score, explanation_dict)
        """
        score = 0.0
        explanation = {}
        
        # Base score for trade match (40 points)
        if subcontractor.trade_category == trade_category:
            score += 40
            explanation['trade_match'] = "✓ Exact trade match"
        
        # Location match (20 points)
        if location:
            location_lower = location.lower()
            matching_areas = [area for area in subcontractor.service_areas 
                            if location_lower in area.lower()]
            if matching_areas:
                score += 20
                explanation['location'] = f"✓ Services {', '.join(matching_areas)}"
            else:
                explanation['location'] = f"⚠ Service area: {', '.join(subcontractor.service_areas)}"
        
        # Rating score (15 points max)
        rating_score = (subcontractor.rating / 5.0) * 15
        score += rating_score
        explanation['rating'] = f"Rating: {subcontractor.rating}/5.0 ({rating_score:.1f} pts)"
        
        # Experience score (10 points max, capped at 20 years)
        exp_score = min(subcontractor.years_experience / 20.0 * 10, 10)
        score += exp_score
        explanation['experience'] = f"{subcontractor.years_experience} years experience ({exp_score:.1f} pts)"
        
        # Bonding capacity (10 points)
        if bid_value and subcontractor.bonding_capacity >= bid_value:
            score += 10
            explanation['bonding'] = f"✓ Bonding capacity: ${subcontractor.bonding_capacity:,}"
        elif bid_value:
            explanation['bonding'] = f"⚠ Bonding capacity: ${subcontractor.bonding_capacity:,} (bid: ${bid_value:,})"
        else:
            score += 5  # Half points if no bid value to compare
            explanation['bonding'] = f"Bonding capacity: ${subcontractor.bonding_capacity:,}"
        
        # Project type / specialty match (5 points)
        if project_type:
            project_lower = project_type.lower()
            for keyword_type, keywords in SPECIALTY_KEYWORDS.items():
                if any(kw in project_lower for kw in keywords):
                    if any(kw in ' '.join(subcontractor.specialties).lower() for kw in keywords):
                        score += 5
                        explanation['specialty'] = f"✓ {keyword_type.title()} project experience"
                        break
        
        # Normalize to 0-100 scale
        max_possible = 100
        normalized_score = (score / max_possible) * 100
        
        return normalized_score, explanation
    
    def recommend_subcontractors(
        self,
        detected_scope: List[str],
        location: str = "Phoenix",
        project_type: str = None,
        bid_value: int = None,
        min_confidence: float = 30.0,
        top_n: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recommend subcontractors for each trade category in the detected scope
        
        Args:
            detected_scope: List of detected scope keywords (e.g., ['concrete', 'steel'])
            location: Project location for service area filtering
            project_type: Type of project (e.g., 'Medical Office')
            bid_value: Total bid value for bonding capacity check
            min_confidence: Minimum confidence score to include (0-100)
            top_n: Number of top recommendations per trade
        
        Returns:
            Dictionary mapping trade categories to list of recommended subcontractors
        """
        trade_categories = self.get_trade_categories(detected_scope)
        recommendations = {}
        
        for trade in trade_categories:
            # Filter subcontractors by trade category
            candidates = [sub for sub in self.subcontractors 
                         if sub.trade_category == trade]
            
            # Calculate scores for each candidate
            scored_candidates = []
            for sub in candidates:
                score, explanation = self.calculate_confidence_score(
                    sub, trade, location, project_type, bid_value
                )
                
                if score >= min_confidence:
                    scored_candidates.append({
                        'subcontractor': sub,
                        'confidence_score': score,
                        'explanation': explanation
                    })
            
            # Sort by confidence score (descending) and take top N
            scored_candidates.sort(key=lambda x: x['confidence_score'], reverse=True)
            recommendations[trade] = scored_candidates[:top_n]
        
        return recommendations
    
    def get_all_service_areas(self) -> List[str]:
        """Get list of all unique service areas from subcontractor data"""
        areas = set()
        for sub in self.subcontractors:
            areas.update(sub.service_areas)
        return sorted(list(areas))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the subcontractor database"""
        trade_counts = defaultdict(int)
        for sub in self.subcontractors:
            trade_counts[sub.trade_category] += 1
        
        return {
            'total_subcontractors': len(self.subcontractors),
            'trades_covered': len(trade_counts),
            'trade_breakdown': dict(trade_counts),
            'service_areas': self.get_all_service_areas(),
            'avg_rating': sum(s.rating for s in self.subcontractors) / len(self.subcontractors) if self.subcontractors else 0,
            'avg_experience': sum(s.years_experience for s in self.subcontractors) / len(self.subcontractors) if self.subcontractors else 0
        }


def format_recommendation_for_display(recommendation: Dict[str, Any]) -> str:
    """Format a single recommendation for text display"""
    sub = recommendation['subcontractor']
    score = recommendation['confidence_score']
    explanation = recommendation['explanation']
    
    output = f"**{sub.company_name}** (Confidence: {score:.0f}%)\n"
    output += f"📞 {sub.phone} | ✉️ {sub.contact_email}\n"
    output += f"License: {sub.license_number} | Rating: {sub.rating}/5.0\n"
    output += f"Specialties: {', '.join(sub.specialties)}\n"
    
    output += "\n**Match Details:**\n"
    for key, value in explanation.items():
        output += f"- {value}\n"
    
    if sub.notes:
        output += f"\n💡 *{sub.notes}*\n"
    
    return output
