"""Rank apartments based on user preferences"""

import sys
from database import get_all_apartments
from preferences import UserPreferences
from scoring import ApartmentScorer, filter_apartments
from geocoding import geocode_address_nominatim


def rank_apartments(work_address: str = None, max_rent: int = 1500, min_bedrooms: float = 1):
    """
    Rank apartments based on user preferences
    
    Args:
        work_address: Work location for commute calculation
        max_rent: Maximum rent budget
        min_bedrooms: Minimum number of bedrooms
    """
    print("\n" + "=" * 80)
    print("APARTMENT RANKING")
    print("=" * 80)
    
    # Set up preferences
    prefs = UserPreferences()
    prefs.set_budget(max_rent=max_rent)
    prefs.set_space_requirements(bedrooms=min_bedrooms, bathrooms=1)
    
    # Geocode work address if provided
    if work_address:
        print(f"\nGeocoding work address: {work_address}...")
        coords = geocode_address_nominatim(work_address)
        if coords:
            prefs.set_work_location(work_address, lat=coords[0], lng=coords[1])
            print(f"✓ Work location set: {coords}")
        else:
            print("⚠ Could not geocode work address, proceeding without commute scoring")
    else:
        print("\n⚠ No work address provided, commute will not be factored into ranking")
    
    print(f"\nPreferences:")
    print(f"  Max Rent: ${max_rent}/mo")
    print(f"  Min Bedrooms: {min_bedrooms}")
    print(f"  Min Bathrooms: {prefs.min_bathrooms}")
    print(f"\nScoring Weights:")
    print(f"  Commute: {prefs.weights['commute']}%")
    print(f"  Price/Value: {prefs.weights['price_value']}%")
    print(f"  Space: {prefs.weights['space']}%")
    print(f"  Location: {prefs.weights['location']}%")
    
    # Get all apartments
    print(f"\nLoading apartments from database...")
    listings = get_all_apartments(active_only=True)
    print(f"Found {len(listings)} active listings")
    
    # Filter by requirements
    print(f"Filtering by requirements...")
    filtered = filter_apartments(listings, prefs)
    print(f"{len(filtered)} apartments match your requirements")
    
    if not filtered:
        print("\n⚠ No apartments match your criteria. Try adjusting your requirements.")
        return
    
    # Score apartments
    print(f"\nScoring apartments...")
    scorer = ApartmentScorer(prefs)
    
    ranked = []
    for listing in filtered:
        score_data = scorer.score_apartment(listing)
        ranked.append({
            'listing': listing,
            'score': score_data['total_score'],
            'breakdown': score_data['breakdown'],
            'commute_info': score_data['commute_info']
        })
    
    # Sort by score (highest first)
    ranked.sort(key=lambda x: x['score'], reverse=True)
    
    # Display top matches
    print("\n" + "=" * 80)
    print(f"TOP 10 MATCHES (out of {len(ranked)} qualifying apartments)")
    print("=" * 80)
    
    for i, item in enumerate(ranked[:10], 1):
        listing = item['listing']
        score = item['score']
        breakdown = item['breakdown']
        commute_info = item['commute_info']
        
        print(f"\n{i}. SCORE: {score:.1f}/100 - {listing['address']}")
        print(f"   ${listing['price']}/mo | {listing.get('bedrooms', '?')} bed | {listing.get('bathrooms', '?')} bath", end="")
        if listing.get('sqft'):
            print(f" | {listing['sqft']} sqft")
        else:
            print()
        
        # Show commute info if available
        if commute_info and 'distance_miles' in commute_info:
            print(f"   🚗 Commute: {commute_info['distance_miles']} mi (~{commute_info['estimated_minutes']} min)")
        
        # Show score breakdown
        print(f"   Score breakdown:", end="")
        for category, data in breakdown.items():
            print(f" {category.title()}: {data['score']:.1f}", end=" |")
        print()
        
        print(f"   {listing['listing_url']}")
    
    print("\n" + "=" * 80)
    
    # Show statistics
    if ranked:
        avg_score = sum(r['score'] for r in ranked) / len(ranked)
        print(f"\nAverage score: {avg_score:.1f}/100")
        print(f"Top score: {ranked[0]['score']:.1f}/100")
        if len(ranked) > 1:
            print(f"Lowest score: {ranked[-1]['score']:.1f}/100")


if __name__ == "__main__":
    # Parse command line arguments
    work_address = None
    max_rent = 1500
    min_bedrooms = 1
    
    if len(sys.argv) > 1:
        # First arg: work address
        work_address = sys.argv[1]
    
    if len(sys.argv) > 2:
        # Second arg: max rent
        try:
            max_rent = int(sys.argv[2])
        except ValueError:
            print(f"Invalid max rent: {sys.argv[2]}")
            sys.exit(1)
    
    if len(sys.argv) > 3:
        # Third arg: min bedrooms
        try:
            min_bedrooms = float(sys.argv[3])
        except ValueError:
            print(f"Invalid min bedrooms: {sys.argv[3]}")
            sys.exit(1)
    
    rank_apartments(work_address, max_rent, min_bedrooms)
