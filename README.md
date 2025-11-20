# Apartment Hunt Optimizer

## The Problem

Apartment hunting is exhausting and inefficient:

**Fragmented Information**
- You have to check 5+ websites daily (Zillow, Apartments.com, Craigslist, Facebook Marketplace)
- Each site has different listings, so you can't afford to skip any
- By the time you see a good apartment, it's often already rented

**Manual Analysis Paralysis**
- You find 50 apartments in your budget
- Now you have to manually calculate commute times for each one
- Then compare price per square foot across neighborhoods
- Then research crime rates, school quality, walkability
- This takes hours per apartment

**Suboptimal Decision Making**
- You probably pick based on gut feeling after seeing 5-10 places
- You might miss a perfect apartment because it was listed on a site you didn't check that day
- You can't objectively compare all options at once

## The Solution

**Stop wasting 20 hours comparing apartments manually. Let the algorithm find your perfect place while you sleep.**

Automated apartment hunting with intelligent scoring:

1. **Aggregates listings** from all major sites automatically
2. **Scores each apartment** based on YOUR priorities (commute, price/value, amenities, safety)
3. **Ranks everything** so the best options rise to the top
4. **Alerts you immediately** when a great match appears

### You Input:
- Work address
- Budget
- Must-have amenities
- Priorities (rank importance of commute vs. price vs. space)

### You Get:
- A ranked list of EVERY available apartment in your area
- Each one scored on how well it matches YOUR needs
- Updated daily so you never miss new listings
- Side-by-side comparisons of your top choices

### Why This Matters

This isn't just about convenience—it's about making a better life decision. Where you live affects:
- Your daily stress (commute)
- Your finances (rent is usually your biggest expense)
- Your happiness (neighborhood quality, amenities)
- Your time (hours saved on commuting)

The right apartment can save you $200/month, 5 hours of commuting per week, and significantly improve your quality of life.

---

## Current Status: Phase 1 - Foundation & Data Collection

Basic scraper that collects apartment listings from Zillow (Des Moines, IA) and stores them in a local database.

### Setup

1. Create virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize database:
```bash
python database.py
```

### Usage

**Scrape apartments (default 3 pages):**
```bash
python main.py scrape
```

**Scrape specific number of pages:**
```bash
python main.py scrape 5
```

**View stored listings:**
```bash
python main.py view
```

**View all listings (including inactive):**
```bash
python main.py all
```

**Rank apartments by your preferences:**
```bash
# Basic ranking (no commute factor)
python rank.py

# With work location and budget
python rank.py "Iowa State Capitol, Des Moines, IA" 1200

# With work location, budget, and minimum bedrooms
python rank.py "500 E Grand Ave, Des Moines, IA" 1500 2
```

### Project Structure

```
apartment-hunt/
├── config.py          # Configuration settings
├── database.py        # SQLite database operations
├── scraper.py         # Zillow scraper
├── main.py           # Main orchestration script
├── rank.py           # Apartment ranking script
├── preferences.py     # User preferences class
├── scoring.py         # Scoring algorithm
├── geocoding.py       # Geocoding and distance utilities
├── requirements.txt   # Python dependencies
├── apartments.db      # SQLite database (created on first run)
└── README.md         # This file
```

### Database Schema

**apartments table:**
- address, city, state, zip_code
- price, bedrooms, bathrooms, sqft
- listing_url, source
- amenities, description
- first_seen, last_seen, is_active

## Images

<img width="1202" height="566" alt="Screenshot 2025-11-13 214726" src="https://github.com/user-attachments/assets/859d9a14-1721-4dc4-99f9-933ecf5003a2" />


<img width="1172" height="883" alt="Screenshot 2025-11-13 214734" src="https://github.com/user-attachments/assets/ed079804-92f3-41e2-8230-ce63838511d2" />

## Notes

- Scraper includes rate limiting (2 seconds between requests)
- Duplicate detection by address and listing URL
- Listings marked inactive after 1 day without update
