"""User preferences for apartment scoring"""

from typing import Dict, List

class UserPreferences:
    def __init__(self):
        # Work location (for commute calculation)
        self.work_address = ""
        self.work_lat = None
        self.work_lng = None
        
        # Budget constraints
        self.max_rent = 2000
        self.min_rent = 0
        
        # Space requirements
        self.min_bedrooms = 1
        self.min_bathrooms = 1
        self.min_sqft = 0
        
        # Must-have amenities (not used in Phase 1, placeholder for future)
        self.required_amenities = []
        
        # Scoring weights (must sum to 100)
        self.weights = {
            'commute': 40,      # 40% weight on commute time
            'price_value': 30,  # 30% weight on price/value ratio
            'space': 20,        # 20% weight on size
            'location': 10,     # 10% weight on neighborhood
        }
    
    def set_work_location(self, address: str, lat: float = None, lng: float = None):
        """Set work location for commute calculations"""
        self.work_address = address
        self.work_lat = lat
        self.work_lng = lng
    
    def set_budget(self, min_rent: int = 0, max_rent: int = 2000):
        """Set rent budget range"""
        self.min_rent = min_rent
        self.max_rent = max_rent
    
    def set_space_requirements(self, bedrooms: float = 1, bathrooms: float = 1, sqft: int = 0):
        """Set minimum space requirements"""
        self.min_bedrooms = bedrooms
        self.min_bathrooms = bathrooms
        self.min_sqft = sqft
    
    def set_weights(self, commute: int = 40, price_value: int = 30, space: int = 20, location: int = 10):
        """Set scoring weights (must sum to 100)"""
        if commute + price_value + space + location != 100:
            raise ValueError("Weights must sum to 100")
        
        self.weights = {
            'commute': commute,
            'price_value': price_value,
            'space': space,
            'location': location,
        }
    
    def to_dict(self) -> Dict:
        """Convert preferences to dictionary"""
        return {
            'work_address': self.work_address,
            'work_lat': self.work_lat,
            'work_lng': self.work_lng,
            'max_rent': self.max_rent,
            'min_rent': self.min_rent,
            'min_bedrooms': self.min_bedrooms,
            'min_bathrooms': self.min_bathrooms,
            'min_sqft': self.min_sqft,
            'required_amenities': self.required_amenities,
            'weights': self.weights,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'UserPreferences':
        """Create preferences from dictionary"""
        prefs = UserPreferences()
        prefs.work_address = data.get('work_address', '')
        prefs.work_lat = data.get('work_lat')
        prefs.work_lng = data.get('work_lng')
        prefs.max_rent = data.get('max_rent', 2000)
        prefs.min_rent = data.get('min_rent', 0)
        prefs.min_bedrooms = data.get('min_bedrooms', 1)
        prefs.min_bathrooms = data.get('min_bathrooms', 1)
        prefs.min_sqft = data.get('min_sqft', 0)
        prefs.required_amenities = data.get('required_amenities', [])
        prefs.weights = data.get('weights', prefs.weights)
        return prefs
