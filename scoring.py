"""Apartment scoring algorithm"""

from typing import Dict, List, Optional
from preferences import UserPreferences
from geocoding import get_coordinates_from_listing, haversine_distance, estimate_commute_time


class ApartmentScorer:
    def __init__(self, preferences: UserPreferences):
        self.prefs = preferences
    
    def score_apartment(self, listing: Dict) -> Dict:
        """
        Score an apartment based on user preferences
        
        Returns:
            Dict with 'total_score', 'breakdown', and 'commute_info'
        """
        scores = {}
        breakdown = {}
        commute_info = None
        
        # 1. Commute Score (0-40 points)
        commute_score, commute_info = self._score_commute(listing)
        scores['commute'] = commute_score
        breakdown['commute'] = {
            'score': commute_score,
            'weight': self.prefs.weights['commute'],
            'info': commute_info
        }
        
        # 2. Price/Value Score (0-30 points)
        price_score = self._score_price_value(listing)
        scores['price_value'] = price_score
        breakdown['price_value'] = {
            'score': price_score,
            'weight': self.prefs.weights['price_value'],
            'info': f"${listing.get('price', 0)}/mo"
        }
        
        # 3. Space Score (0-20 points)
        space_score = self._score_space(listing)
        scores['space'] = space_score
        breakdown['space'] = {
            'score': space_score,
            'weight': self.prefs.weights['space'],
            'info': f"{listing.get('sqft', 'N/A')} sqft"
        }
        
        # 4. Location Score (0-10 points) - placeholder for now
        location_score = self._score_location(listing)
        scores['location'] = location_score
        breakdown['location'] = {
            'score': location_score,
            'weight': self.prefs.weights['location'],
            'info': 'Based on distance to downtown'
        }
        
        # Calculate weighted total
        total_score = sum(scores.values())
        
        return {
            'total_score': round(total_score, 1),
            'breakdown': breakdown,
            'commute_info': commute_info
        }
    
    def _score_commute(self, listing: Dict) -> tuple[float, Optional[Dict]]:
        """
        Score based on commute time
        40 points = 0-10 min commute
        30 points = 10-20 min
        20 points = 20-30 min
        10 points = 30-45 min
        0 points = 45+ min
        """
        if not self.prefs.work_lat or not self.prefs.work_lng:
            # No work location set, give neutral score
            return self.prefs.weights['commute'] / 2, None
        
        coords = get_coordinates_from_listing(listing)
        if not coords:
            # Can't geocode, give penalty
            return self.prefs.weights['commute'] * 0.3, {'error': 'Could not determine location'}
        
        # Calculate distance
        distance = haversine_distance(
            coords[0], coords[1],
            self.prefs.work_lat, self.prefs.work_lng
        )
        
        # Estimate commute time
        commute_minutes = estimate_commute_time(distance, 'driving')
        
        # Score based on commute time
        max_points = self.prefs.weights['commute']
        if commute_minutes <= 10:
            score = max_points
        elif commute_minutes <= 20:
            score = max_points * 0.75
        elif commute_minutes <= 30:
            score = max_points * 0.5
        elif commute_minutes <= 45:
            score = max_points * 0.25
        else:
            score = 0
        
        commute_info = {
            'distance_miles': round(distance, 1),
            'estimated_minutes': commute_minutes
        }
        
        return score, commute_info
    
    def _score_price_value(self, listing: Dict) -> float:
        """
        Score based on price relative to budget and size
        Better value = higher score
        """
        price = listing.get('price')
        if not price:
            return 0
        
        max_points = self.prefs.weights['price_value']
        
        # Factor 1: Price relative to max budget (60% of score)
        if price > self.prefs.max_rent:
            budget_score = 0  # Over budget = 0 points
        else:
            # Lower price = better score
            price_ratio = price / self.prefs.max_rent
            budget_score = (1 - price_ratio) * max_points * 0.6
        
        # Factor 2: Price per sqft (40% of score)
        sqft = listing.get('sqft')
        if sqft and sqft > 0:
            price_per_sqft = price / sqft
            # Typical range: $0.75 - $2.00 per sqft
            # Lower is better
            if price_per_sqft <= 0.75:
                value_score = max_points * 0.4
            elif price_per_sqft <= 1.00:
                value_score = max_points * 0.3
            elif price_per_sqft <= 1.50:
                value_score = max_points * 0.2
            else:
                value_score = max_points * 0.1
        else:
            # No sqft data, use just budget score
            value_score = max_points * 0.2  # Neutral
        
        return budget_score + value_score
    
    def _score_space(self, listing: Dict) -> float:
        """
        Score based on size (bedrooms, bathrooms, sqft)
        """
        max_points = self.prefs.weights['space']
        score = 0
        
        # Bedrooms (40% of space score)
        bedrooms = listing.get('bedrooms', 0)
        if bedrooms >= self.prefs.min_bedrooms:
            # Extra bedrooms add value
            bedroom_score = min(1.0, bedrooms / (self.prefs.min_bedrooms + 1))
            score += bedroom_score * max_points * 0.4
        
        # Bathrooms (30% of space score)
        bathrooms = listing.get('bathrooms', 0)
        if bathrooms and bathrooms >= self.prefs.min_bathrooms:
            bathroom_score = min(1.0, bathrooms / (self.prefs.min_bathrooms + 0.5))
            score += bathroom_score * max_points * 0.3
        
        # Square footage (30% of space score)
        sqft = listing.get('sqft', 0)
        if sqft:
            if sqft >= self.prefs.min_sqft:
                # Typical 1BR: 600-800 sqft, 2BR: 900-1200 sqft
                target_sqft = max(600, self.prefs.min_sqft)
                sqft_ratio = min(1.0, sqft / target_sqft)
                score += sqft_ratio * max_points * 0.3
        
        return score
    
    def _score_location(self, listing: Dict) -> float:
        """
        Score based on location quality
        For now, use distance to downtown Des Moines as proxy
        """
        max_points = self.prefs.weights['location']
        
        # Des Moines downtown coordinates (approximately)
        downtown_lat, downtown_lng = 41.5868, -93.6250
        
        coords = get_coordinates_from_listing(listing)
        if not coords:
            return max_points * 0.5  # Neutral score
        
        distance = haversine_distance(
            coords[0], coords[1],
            downtown_lat, downtown_lng
        )
        
        # Score based on distance to downtown
        if distance <= 2:
            score = max_points  # Downtown
        elif distance <= 5:
            score = max_points * 0.75  # Close to downtown
        elif distance <= 10:
            score = max_points * 0.5  # Suburbs
        else:
            score = max_points * 0.25  # Far suburbs
        
        return score


def filter_apartments(listings: List[Dict], preferences: UserPreferences) -> List[Dict]:
    """
    Filter apartments based on hard requirements
    
    Args:
        listings: List of apartment listings
        preferences: User preferences
    
    Returns:
        Filtered list of apartments that meet minimum requirements
    """
    filtered = []
    
    for listing in listings:
        # Check budget
        price = listing.get('price', 0)
        if price and (price < preferences.min_rent or price > preferences.max_rent):
            continue
        
        # Check bedrooms
        bedrooms = listing.get('bedrooms', 0)
        if bedrooms is not None and bedrooms < preferences.min_bedrooms:
            continue
        
        # Check bathrooms
        bathrooms = listing.get('bathrooms')
        if bathrooms and bathrooms < preferences.min_bathrooms:
            continue
        
        # Check sqft
        sqft = listing.get('sqft', 0)
        if sqft and sqft < preferences.min_sqft:
            continue
        
        filtered.append(listing)
    
    return filtered
