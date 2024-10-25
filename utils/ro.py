import json
from datetime import datetime as dt
'''
RO Object used for storing Repair Order data before being inserted into database.
'''

class RO:
    def __init__(self, order_id, date_time, status, cost, technician, repair_parts):
        self.order_id = order_id
        # Convert date_time to a string format for compatibility with SQLite
        self.date_time = date_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(date_time, dt) else date_time
        self.status = status
        self.cost = cost
        self.technician = technician
        # Serialize repair_parts as a JSON string
        self.repair_parts = json.dumps(repair_parts) if isinstance(repair_parts, list) else repair_parts

    def to_tuple(self):
        processed_at = dt.now().strftime('%Y-%m-%d %H:%M:%S') # Adds a current timmestamp field as a string for record keeping in the db.
        return (self.order_id, self.date_time, self.status, self.cost, self.technician, self.repair_parts, processed_at)