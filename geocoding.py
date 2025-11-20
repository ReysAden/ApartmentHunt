"""Geocoding and distance calculation utilities"""

import requests
import time
from typing import Optional, Tuple
from math import radians, cos, sin, asin, sqrt

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in miles
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in miles
    miles = 3959 * c
    return miles


def geocode_address_nominatim(address: str) -> Optional[Tuple[float, float]]:
    """
    Geocode an address using OpenStreetMap's Nominatim API (free, no API key)
    Returns (latitude, longitude) or None if not found
    """
    try:
        # Rate limiting - be respectful to free API
        time.sleep(1)
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'ApartmentHuntOptimizer/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return (lat, lon)
        
        return None
        
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
        return None


def estimate_commute_time(distance_miles: float, method: str = 'driving') -> int:
    """
    Estimate commute time in minutes based on distance and method
    
    Args:
        distance_miles: Distance in miles
        method: 'driving', 'transit', or 'walking'
    
    Returns:
        Estimated commute time in minutes
    """
    # Average speeds (mph)
    speeds = {
        'driving': 30,   # City driving with traffic
        'transit': 20,   # Public transit average
        'walking': 3,    # Walking speed
    }
    
    speed = speeds.get(method, 30)
    time_hours = distance_miles / speed
    time_minutes = int(time_hours * 60)
    
    return time_minutes


def get_coordinates_from_listing(listing: dict) -> Optional[Tuple[float, float]]:
    """
    Extract coordinates from listing data or geocode the address
    
    Args:
        listing: Apartment listing dictionary
    
    Returns:
        (latitude, longitude) tuple or None
    """
    # First try to get from listing data if available
    lat = listing.get('latitude')
    lng = listing.get('longitude')
    
    if lat and lng:
        return (float(lat), float(lng))
    
    # Otherwise geocode the address
    address = listing.get('address')
    if address:
        return geocode_address_nominatim(address)
    
    return None


if __name__ == "__main__":
    # Test geocoding
    coords = geocode_address_nominatim("Des Moines, IA")
    if coords:
        print(f"Des Moines coordinates: {coords}")
        
        # Test distance calculation
        other_coords = geocode_address_nominatim("Ames, IA")
        if other_coords:
            distance = haversine_distance(coords[0], coords[1], other_coords[0], other_coords[1])
            print(f"Distance to Ames: {distance:.1f} miles")
            print(f"Estimated drive time: {estimate_commute_time(distance, 'driving')} minutes")
