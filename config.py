"""Configuration settings for Apartment Hunt Optimizer"""

# Target city
CITY = "Des Moines"
STATE = "IA"

# Scraping settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_TIMEOUT = 10
REQUEST_DELAY = 2  # seconds between requests

# Database
DB_PATH = "apartments.db"

# Zillow search parameters
ZILLOW_BASE_URL = "https://www.zillow.com"
ZILLOW_SEARCH_URL = f"{ZILLOW_BASE_URL}/des-moines-ia/rentals/"
