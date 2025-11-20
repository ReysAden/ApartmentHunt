"""Main script to run apartment scraping and storage"""

import sys
from database import init_db, insert_apartment, get_all_apartments, mark_inactive_listings
from scraper import ZillowScraper


def run_scraper(max_pages: int = 3):
    """Run the scraper and store results"""
    print("Starting apartment scraper...")
    print("=" * 50)
    
    # Initialize scraper
    scraper = ZillowScraper()
    
    # Scrape listings
    listings = scraper.scrape_listings(max_pages=max_pages)
    
    print(f"\n{'=' * 50}")
    print(f"Scraping complete. Found {len(listings)} total listings")
    print("=" * 50)
    
    if not listings:
        print("No listings found. Check if scraper needs adjustment.")
        return
    
    # Store in database
    print("\nStoring listings in database...")
    new_count = 0
    updated_count = 0
    
    for listing in listings:
        is_new = insert_apartment(listing)
        if is_new:
            new_count += 1
        else:
            updated_count += 1
    
    print(f"\nNew listings: {new_count}")
    print(f"Updated listings: {updated_count}")
    
    # Mark old listings as inactive (only run if needed, not on first scrape)
    # mark_inactive_listings(days_old=2)


def view_listings(limit: int = 20, active_only: bool = True):
    """Display stored listings"""
    listings = get_all_apartments(active_only=active_only)
    
    if not listings:
        print("No listings found in database.")
        return
    
    print(f"\n{'=' * 80}")
    print(f"APARTMENT LISTINGS ({'Active only' if active_only else 'All'})")
    print(f"Total: {len(listings)} listings")
    print("=" * 80)
    
    for i, apt in enumerate(listings[:limit], 1):
        print(f"\n{i}. {apt['address']}")
        print(f"   Price: ${apt['price']}/mo | {apt['bedrooms']} bed | {apt['bathrooms']} bath", end="")
        if apt['sqft']:
            print(f" | {apt['sqft']} sqft")
        else:
            print()
        print(f"   URL: {apt['listing_url']}")
        print(f"   Status: {'Active' if apt['is_active'] else 'Inactive'} | First seen: {apt['first_seen']}")
    
    if len(listings) > limit:
        print(f"\n... and {len(listings) - limit} more listings")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Initialize database on first run
    init_db()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "scrape":
            pages = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            run_scraper(max_pages=pages)
        
        elif command == "view":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            view_listings(limit=limit)
        
        elif command == "all":
            view_listings(active_only=False)
        
        else:
            print("Unknown command. Use: scrape, view, or all")
    
    else:
        # Default: run scraper
        run_scraper(max_pages=3)
