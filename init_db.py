import sqlite3
from datetime import datetime

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Location (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ProductMovement (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    from_location INTEGER,
    to_location INTEGER,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    FOREIGN KEY(product_id) REFERENCES Product(product_id),
    FOREIGN KEY(from_location) REFERENCES Location(location_id),
    FOREIGN KEY(to_location) REFERENCES Location(location_id)
)
''')

products = [("Laptop",), ("Phone",), ("Tablet",), ("Monitor",)]
cursor.executemany("INSERT INTO Product (product_name) VALUES (?)", products)

locations = [("Warehouse A",), ("Store B",), ("Depot C",), ("Shop D",)]
cursor.executemany("INSERT INTO Location (location_name) VALUES (?)", locations)

movements = [
    (None, 1, 50),       # Product 1 to Warehouse A
    (None, 2, 30),       # Product 2 to Warehouse A
    (None, 3, 20),       # Product 3 to Warehouse A
    (None, 4, 10),       # Product 4 to Warehouse A
    (1, 2, 10),          # Product 1 from Warehouse A to Store B
    (1, 3, 15),          # Product 1 from Warehouse A to Depot C
    (2, 2, 5),           # Product 2 from Warehouse A to Store B
    (2, 4, 10),          # Product 2 from Warehouse A to Shop D
    (3, 3, 5),           # Product 3 from Warehouse A to Depot C
    (4, 2, 3)            # Product 4 from Warehouse A to Store B
]
for m in movements:
    from_loc = m[0]
    to_loc = m[1]
    qty = m[2]
    product_id = movements.index(m) + 1 if movements.index(m) < 4 else (movements.index(m)-3)
    cursor.execute('''
        INSERT INTO ProductMovement (from_location, to_location, product_id, qty)
        VALUES (?, ?, ?, ?)
    ''', (from_loc, to_loc, product_id, qty))

conn.commit()
conn.close()
print("✅ inventory.db created with sample data!")
