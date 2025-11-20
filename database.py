"""Database operations for apartment listings"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from config import DB_PATH


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apartments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip_code TEXT,
            price INTEGER,
            bedrooms REAL,
            bathrooms REAL,
            sqft INTEGER,
            listing_url TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            amenities TEXT,
            description TEXT,
            first_seen DATE NOT NULL,
            last_seen DATE NOT NULL,
            is_active INTEGER DEFAULT 1,
            UNIQUE(address, city, state)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_price ON apartments(price)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_active ON apartments(is_active)
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")


def insert_apartment(apartment_data: Dict) -> bool:
    """
    Insert or update apartment listing
    Returns True if new listing, False if updated existing
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().date().isoformat()
    
    try:
        # Try to insert new listing
        cursor.execute("""
            INSERT INTO apartments (
                address, city, state, zip_code, price, bedrooms, bathrooms,
                sqft, listing_url, source, amenities, description,
                first_seen, last_seen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            apartment_data.get('address'),
            apartment_data.get('city'),
            apartment_data.get('state'),
            apartment_data.get('zip_code'),
            apartment_data.get('price'),
            apartment_data.get('bedrooms'),
            apartment_data.get('bathrooms'),
            apartment_data.get('sqft'),
            apartment_data.get('listing_url'),
            apartment_data.get('source'),
            apartment_data.get('amenities'),
            apartment_data.get('description'),
            today,
            today
        ))
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.IntegrityError:
        # Listing exists, update last_seen and reactivate if needed
        cursor.execute("""
            UPDATE apartments 
            SET last_seen = ?,
                is_active = 1,
                price = ?,
                sqft = ?,
                amenities = ?,
                description = ?
            WHERE listing_url = ?
        """, (
            today,
            apartment_data.get('price'),
            apartment_data.get('sqft'),
            apartment_data.get('amenities'),
            apartment_data.get('description'),
            apartment_data.get('listing_url')
        ))
        conn.commit()
        conn.close()
        return False


def get_all_apartments(active_only: bool = True) -> List[Dict]:
    """Retrieve all apartment listings"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM apartments"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY price ASC"
    
    cursor.execute(query)
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return results


def mark_inactive_listings(days_old: int = 2):
    """Mark listings as inactive if not seen in specified days"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE apartments
        SET is_active = 0
        WHERE julianday('now') - julianday(last_seen) >= ?
        AND is_active = 1
    """, (days_old,))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if affected > 0:
        print(f"Marked {affected} listing(s) as inactive")


if __name__ == "__main__":
    init_db()
