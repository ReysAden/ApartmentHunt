"""Web scraper for Zillow apartment listings"""

import requests
from bs4 import BeautifulSoup
import time
import re
import json
from typing import List, Dict, Optional
from config import (
    USER_AGENT, REQUEST_TIMEOUT, REQUEST_DELAY,
    ZILLOW_SEARCH_URL, CITY, STATE
)


class ZillowScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def _parse_price(self, price_value) -> Optional[int]:
        """Parse price from various formats: int, '$1,200', '$1,200+', etc."""
        if price_value is None:
            return None
        
        if isinstance(price_value, (int, float)):
            return int(price_value)
        
        if isinstance(price_value, str):
            # Remove $, commas, +, /mo, etc
            cleaned = re.sub(r'[\$,+/mo\s]', '', price_value)
            try:
                return int(cleaned)
            except ValueError:
                return None
        
        return None
    
    def scrape_listings(self, max_pages: int = 3) -> List[Dict]:
        """
        Scrape apartment listings from Zillow
        Returns list of apartment data dictionaries
        """
        all_listings = []
        
        for page in range(1, max_pages + 1):
            print(f"\nScraping page {page}...")
            
            # Construct URL with pagination
            url = ZILLOW_SEARCH_URL
            if page > 1:
                url += f"{page}_p/"
            
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                listings = self._parse_page(response.text)
                print(f"Found {len(listings)} listings on page {page}")
                
                all_listings.extend(listings)
                
                # Rate limiting
                if page < max_pages:
                    time.sleep(REQUEST_DELAY)
                    
            except requests.RequestException as e:
                print(f"Error scraping page {page}: {e}")
                break
        
        return all_listings
    
    def _parse_page(self, html: str) -> List[Dict]:
        """Parse apartment listings from page HTML by extracting JSON data"""
        soup = BeautifulSoup(html, 'lxml')
        listings = []
        
        # Find the __NEXT_DATA__ script tag that contains JSON data
        script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
        
        if not script_tag:
            print("[ERROR] Could not find __NEXT_DATA__ script tag")
            return listings
        
        try:
            data = json.loads(script_tag.string)
            
            # Navigate to the search results
            # Path: props -> pageProps -> searchPageState -> cat1 -> searchResults -> listResults
            search_results = (
                data.get('props', {})
                .get('pageProps', {})
                .get('searchPageState', {})
                .get('cat1', {})
                .get('searchResults', {})
                .get('listResults', [])
            )
            
            for result in search_results:
                # Skip non-dict entries
                if not isinstance(result, dict):
                    continue
                
                try:
                    listing = self._parse_json_listing(result)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    # Silently skip errors
                    continue
                    
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
        
        return listings
    
    def _parse_json_listing(self, result: Dict) -> Optional[Dict]:
        """Parse individual listing from JSON data"""
        try:
            # Extract basic info
            zpid = result.get('zpid')
            if not zpid:
                return None
            
            # Address - can be a dict or a string
            address_data = result.get('address', {})
            if isinstance(address_data, str):
                # Address is already a formatted string
                full_address = address_data
                city = CITY
                state = STATE
                zip_code = None
            elif isinstance(address_data, dict):
                # Address is a dict with components
                street_address = address_data.get('streetAddress', '')
                city = address_data.get('city', CITY)
                state = address_data.get('state', STATE)
                zip_code = address_data.get('zipcode', '')
                full_address = f"{street_address}, {city}, {state} {zip_code}" if street_address else None
            else:
                full_address = None
                city = CITY
                state = STATE
                zip_code = None
            
            # Price - could be in different fields
            price_raw = result.get('price')
            if not price_raw:
                # Try alternative price fields
                price_raw = result.get('unformattedPrice')
            if not price_raw and 'units' in result and result['units']:
                # For multi-unit buildings, get min price
                price_raw = result['units'][0].get('price')
            
            price = self._parse_price(price_raw)
            
            # Beds/baths
            bedrooms = result.get('beds')
            bathrooms = result.get('baths')
            
            # Check units array for beds/baths if not in main result
            if (bedrooms is None or bathrooms is None) and 'units' in result and result['units']:
                unit = result['units'][0]
                if bedrooms is None:
                    bedrooms = unit.get('beds')
                if bathrooms is None:
                    bathrooms = unit.get('baths')
            
            # Square footage
            sqft = result.get('area')
            if not sqft:
                sqft = result.get('livingArea')
            
            # URL
            detail_url = result.get('detailUrl', '')
            listing_url = f"https://www.zillow.com{detail_url}" if detail_url.startswith('/') else detail_url
            
            # Only return if we have minimum required data
            if not full_address or not listing_url:
                return None
            
            return {
                'address': full_address,
                'city': city,
                'state': state,
                'zip_code': str(zip_code) if zip_code else None,
                'price': price,  # Already parsed as int
                'bedrooms': float(bedrooms) if bedrooms is not None else None,
                'bathrooms': float(bathrooms) if bathrooms is not None else None,
                'sqft': int(sqft) if sqft else None,
                'listing_url': listing_url,
                'source': 'Zillow',
                'amenities': None,
                'description': None
            }
            
        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None
    


if __name__ == "__main__":
    scraper = ZillowScraper()
    listings = scraper.scrape_listings(max_pages=1)
    
    print(f"\n\nTotal listings found: {len(listings)}")
    if listings:
        print("\nSample listing:")
        print(listings[0])
