"""
BloodChain AI - Database Layer.
Provides SQLite database initialization, table creation, and sample data seeding.
Schema is 100% standard SQL, fully compatible with MySQL.

Tables:
1. hospitals
2. blood_banks
3. blood_inventory
4. demand_history
5. predictions
6. distributions
7. alerts
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "bloodchain.db")
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reset=False):
    if force_reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Hospitals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT DEFAULT 'Trichy',
        address TEXT,
        contact_phone TEXT,
        capacity_beds INTEGER DEFAULT 200,
        current_inpatient_count INTEGER DEFAULT 150,
        distance_km REAL DEFAULT 3.5
    )
    """)

    # 2. Blood Banks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blood_banks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT DEFAULT 'Trichy',
        address TEXT,
        contact_phone TEXT,
        storage_capacity_units INTEGER DEFAULT 1000,
        distance_km REAL DEFAULT 4.0
    )
    """)

    # 3. Blood Inventory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blood_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_type TEXT NOT NULL CHECK(facility_type IN ('HOSPITAL', 'BLOOD_BANK')),
        facility_id INTEGER NOT NULL,
        facility_name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        component_type TEXT DEFAULT 'RBC',
        units INTEGER NOT NULL,
        collection_date TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        status TEXT DEFAULT 'AVAILABLE' CHECK(status IN ('AVAILABLE', 'RESERVED', 'EXPIRED', 'TRANSFERRED'))
    )
    """)

    # 4. Demand History Table (for ML Training)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS demand_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_date TEXT NOT NULL,
        hospital_id INTEGER NOT NULL,
        blood_group TEXT NOT NULL,
        blood_units_used INTEGER NOT NULL,
        emergency_cases INTEGER NOT NULL,
        previous_demand INTEGER NOT NULL,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
    )
    """)

    # 5. Predictions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_id INTEGER NOT NULL,
        blood_group TEXT NOT NULL,
        prediction_period TEXT DEFAULT '7_DAYS',
        current_stock INTEGER NOT NULL,
        predicted_demand INTEGER NOT NULL,
        expected_shortage INTEGER NOT NULL,
        recommendation TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
    )
    """)

    # 6. Distributions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS distributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_blood_bank_id INTEGER NOT NULL,
        source_name TEXT NOT NULL,
        target_hospital_id INTEGER NOT NULL,
        target_name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        units INTEGER NOT NULL,
        priority TEXT DEFAULT 'HIGH' CHECK(priority IN ('ROUTINE', 'MEDIUM', 'HIGH', 'CRITICAL')),
        status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'APPROVED', 'DISPATCHED', 'COMPLETED')),
        created_at TEXT NOT NULL
    )
    """)

    # 7. Alerts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_type TEXT NOT NULL CHECK(alert_type IN ('CRITICAL', 'LOW_STOCK', 'EXPIRY_WARNING', 'ACTION')),
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        time_ago TEXT NOT NULL,
        blood_group TEXT,
        units INTEGER,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) as count FROM hospitals")
    if cursor.fetchone()["count"] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    today = datetime.now().date()

    # Seed 12 Hospitals
    hospitals_data = [
        ("Government Hospital", "Trichy", "Puthur Main Road", "+91 431 2415201", 850, 720, 2.5),
        ("Apollo Speciality Hospital", "Trichy", "Old Thanjavur Road", "+91 431 4077777", 350, 310, 5.8),
        ("SRM Medical College Hospital", "Trichy", "Irungalur", "+91 431 2258900", 600, 520, 11.5),
        ("KMC Speciality Hospital", "Trichy", "Collector Office Road", "+91 431 2414141", 280, 240, 4.1),
        ("Frontier Lifeline Emergency Hospital", "Trichy", "Cantonment", "+91 431 2460111", 180, 160, 3.8),
        ("Kauvery Hospital Trichy", "Trichy", "Tennur", "+91 431 4006600", 300, 270, 4.5),
        ("City Medical Center", "Trichy", "Thillai Nagar", "+91 431 2760000", 150, 130, 3.2),
        ("G. Viswanathan Memorial Hospital", "Trichy", "Babu Road", "+91 431 2702222", 200, 180, 4.0),
        ("Child Jesus Hospital", "Trichy", "Cantonment", "+91 431 2412345", 160, 140, 3.9),
        ("Maruti Medical Center", "Trichy", "Karur Bypass Road", "+91 431 2711122", 140, 110, 5.0),
        ("St. Joseph's Hospital", "Trichy", "Melapudur", "+91 431 2461999", 220, 190, 4.2),
        ("Trichy SRM Rural Health Center", "Trichy", "Samayapuram", "+91 431 2670100", 120, 95, 14.0)
    ]
    cursor.executemany("""
    INSERT INTO hospitals (name, city, address, contact_phone, capacity_beds, current_inpatient_count, distance_km)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, hospitals_data)

    # Seed 5 Blood Banks
    blood_banks_data = [
        ("Blood Bank B", "Trichy", "Medical District Zone B", "+91 431 2419988", 1200, 3.0),
        ("Red Cross Regional Blood Bank", "Trichy", "WB Road, Cantonment", "+91 431 2415000", 1500, 2.0),
        ("Rotary Central Community Blood Bank", "Trichy", "Thillai Nagar", "+91 431 2761200", 1200, 4.5),
        ("Saranathan Support Blood Bank", "Trichy", "Panjappur", "+91 431 2901000", 800, 7.0),
        ("Lions Club Voluntary Blood Bank", "Trichy", "Rockfort Road", "+91 431 2704500", 900, 5.2)
    ]
    cursor.executemany("""
    INSERT INTO blood_banks (name, city, address, contact_phone, storage_capacity_units, distance_km)
    VALUES (?, ?, ?, ?, ?, ?)
    """, blood_banks_data)

    # Seed Exact Blood Inventory matching Hackathon specifications
    # Government Hospital (facility_id = 1)
    # A+: 120 (Normal, 20 expiring soon)
    # A-: 18 (Low, 5 expiring soon)
    # B+: 75 (Normal, 10 expiring soon)
    # B-: 8 (Critical, 2 expiring soon)
    # O+: 150 (Normal, 15 expiring soon)
    # O-: 12 (Low, 4 expiring soon)
    # AB+: 30 (Normal, 6 expiring soon)
    # AB-: 5 (Low, 1 expiring soon)
    # Blood Bank B (facility_id = 1): 60 units B+ available
    # Total units across network = 540
    inventory_data = [
        # Gov Hospital
        ("HOSPITAL", 1, "Government Hospital", "A+", "RBC", 20, str(today - timedelta(days=39)), str(today + timedelta(days=3))),
        ("HOSPITAL", 1, "Government Hospital", "A+", "RBC", 100, str(today - timedelta(days=10)), str(today + timedelta(days=32))),
        ("HOSPITAL", 1, "Government Hospital", "A-", "RBC", 5, str(today - timedelta(days=38)), str(today + timedelta(days=4))),
        ("HOSPITAL", 1, "Government Hospital", "A-", "RBC", 13, str(today - timedelta(days=12)), str(today + timedelta(days=30))),
        ("HOSPITAL", 1, "Government Hospital", "B+", "RBC", 10, str(today - timedelta(days=39)), str(today + timedelta(days=3))),
        ("HOSPITAL", 1, "Government Hospital", "B+", "RBC", 65, str(today - timedelta(days=14)), str(today + timedelta(days=28))),
        ("HOSPITAL", 1, "Government Hospital", "B-", "RBC", 2, str(today - timedelta(days=40)), str(today + timedelta(days=2))),
        ("HOSPITAL", 1, "Government Hospital", "B-", "RBC", 6, str(today - timedelta(days=15)), str(today + timedelta(days=27))),
        ("HOSPITAL", 1, "Government Hospital", "O+", "RBC", 15, str(today - timedelta(days=38)), str(today + timedelta(days=4))),
        ("HOSPITAL", 1, "Government Hospital", "O+", "RBC", 135, str(today - timedelta(days=8)), str(today + timedelta(days=34))),
        ("HOSPITAL", 1, "Government Hospital", "O-", "RBC", 4, str(today - timedelta(days=39)), str(today + timedelta(days=3))),
        ("HOSPITAL", 1, "Government Hospital", "O-", "RBC", 8, str(today - timedelta(days=11)), str(today + timedelta(days=31))),
        ("HOSPITAL", 1, "Government Hospital", "AB+", "RBC", 6, str(today - timedelta(days=38)), str(today + timedelta(days=4))),
        ("HOSPITAL", 1, "Government Hospital", "AB+", "RBC", 24, str(today - timedelta(days=16)), str(today + timedelta(days=26))),
        ("HOSPITAL", 1, "Government Hospital", "AB-", "RBC", 1, str(today - timedelta(days=40)), str(today + timedelta(days=2))),
        ("HOSPITAL", 1, "Government Hospital", "AB-", "RBC", 4, str(today - timedelta(days=20)), str(today + timedelta(days=22))),

        # Blood Bank B (facility_id = 1)
        ("BLOOD_BANK", 1, "Blood Bank B", "B+", "RBC", 60, str(today - timedelta(days=5)), str(today + timedelta(days=37))),
        ("BLOOD_BANK", 1, "Blood Bank B", "O+", "RBC", 35, str(today - timedelta(days=7)), str(today + timedelta(days=35))),
        ("BLOOD_BANK", 1, "Blood Bank B", "A+", "RBC", 15, str(today - timedelta(days=6)), str(today + timedelta(days=36))),
        ("BLOOD_BANK", 1, "Blood Bank B", "O-", "RBC", 12, str(today - timedelta(days=8)), str(today + timedelta(days=34)))
    ]

    cursor.executemany("""
    INSERT INTO blood_inventory (facility_type, facility_id, facility_name, blood_group, component_type, units, collection_date, expiry_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'AVAILABLE')
    """, inventory_data)

    # Seed Demand History (Sample ML training data: Date, Hospital, Blood Group, Units Used, Emergency Cases, Previous Demand)
    demand_records = []
    for d in range(60, 0, -1):
        rec_date = str(today - timedelta(days=d))
        # B+ usage history
        prev_d = 70 + (d % 8) * 4
        units_u = prev_d + (3 if d % 3 == 0 else -2)
        emerg = 5 + (d % 4)
        demand_records.append((rec_date, 1, "B+", units_u, emerg, prev_d))

        # O+ usage history
        prev_o = 120 + (d % 6) * 5
        demand_records.append((rec_date, 1, "O+", prev_o + 4, emerg + 2, prev_o))

        # O- usage history
        demand_records.append((rec_date, 1, "O-", 18 + (d % 3), 4, 16))

        # B- usage history
        demand_records.append((rec_date, 1, "B-", 12 + (d % 2), 2, 10))

    cursor.executemany("""
    INSERT INTO demand_history (record_date, hospital_id, blood_group, blood_units_used, emergency_cases, previous_demand)
    VALUES (?, ?, ?, ?, ?, ?)
    """, demand_records)

    # Seed Dynamic Alerts matching requirement 9:
    # 🔴 CRITICAL: B- stock is only 8 units.
    # 🟡 LOW STOCK: O- stock is below required level.
    # 🟠 EXPIRY WARNING: 20 units of A+ may expire soon.
    # 🟢 ACTION: Transfer B+ from Blood Bank B -> Hospital A.
    alerts_data = [
        ("CRITICAL", "🔴 CRITICAL", "B- stock is only 8 units.", "2 hours ago", "B-", 8, str(datetime.now() - timedelta(hours=2))),
        ("LOW_STOCK", "🟡 LOW STOCK", "O- stock is below required level.", "4 hours ago", "O-", 12, str(datetime.now() - timedelta(hours=4))),
        ("EXPIRY_WARNING", "🟠 EXPIRY WARNING", "20 units of A+ may expire soon.", "6 hours ago", "A+", 20, str(datetime.now() - timedelta(hours=6))),
        ("ACTION", "🟢 ACTION", "Transfer B+ from Blood Bank B → Hospital A.", "8 hours ago", "B+", 35, str(datetime.now() - timedelta(hours=8)))
    ]
    cursor.executemany("""
    INSERT INTO alerts (alert_type, title, message, time_ago, blood_group, units, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, alerts_data)

    conn.commit()

if __name__ == "__main__":
    init_db(force_reset=True)
    print("BloodChain AI database initialized successfully at:", DB_PATH)
