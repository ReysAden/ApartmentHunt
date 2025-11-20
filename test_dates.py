import sqlite3

conn = sqlite3.connect('apartments.db')
c = conn.cursor()

c.execute('''
    SELECT last_seen, 
           julianday("now") - julianday(last_seen) as days_diff,
           is_active
    FROM apartments 
    LIMIT 5
''')

for row in c.fetchall():
    print(f"Last seen: {row[0]}, Days diff: {row[1]:.4f}, Active: {row[2]}")

conn.close()
