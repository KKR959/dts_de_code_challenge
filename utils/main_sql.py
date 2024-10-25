# SQL Ussed in Main.py
CREATE_TABLE_REPAIR_ORDER = '''
    CREATE TABLE IF NOT EXISTS repair_orders (
        order_id TEXT PRIMARY KEY,
        date_time TEXT,
        status TEXT,
        cost REAL,
        technician TEXT,
        repair_parts TEXT,
        processed_at TEXT
    );
'''

# SQL query to insert a new record into the repair_orders table
INSERT_REPAIR_ORDER = """
INSERT OR REPLACE INTO repair_orders (order_id, date_time, status, cost, technician, repair_parts, processed_at)
VALUES (?, ?, ?, ?, ?, ?, ?);
"""