"""
Smart Blood Distribution & Compatibility Optimization Engine.
Implements:
1. Biological blood compatibility cross-matching (Universal donor O-, recipient AB+).
2. Shelf-life expiry prioritization (transferring near-expiry stock to high-intake facilities to eliminate wastage).
3. Distance & emergency urgency scoring.
"""

from datetime import datetime, timedelta
import sqlite3

# Red Blood Cell (RBC) compatibility map
# Recipient: List of compatible donor groups (ordered by preference, exact match first)
RBC_COMPATIBILITY = {
    "O-": ["O-"],
    "O+": ["O+", "O-"],
    "A-": ["A-", "O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"]
}

# Standard safety threshold per hospital by bed capacity
def get_safety_stock_threshold(capacity_beds, blood_group):
    # Rare groups have smaller absolute reserves, common groups higher
    weight_multipliers = {
        "O+": 0.030,
        "B+": 0.025,
        "A+": 0.020,
        "AB+": 0.010,
        "O-": 0.010,
        "B-": 0.008,
        "A-": 0.005,
        "AB-": 0.003
    }
    multiplier = weight_multipliers.get(blood_group, 0.015)
    return max(3, int(round(capacity_beds * multiplier)))

class DistributionOptimizer:
    def __init__(self, db_conn):
        self.conn = db_conn

    def analyze_network_balance(self):
        """
        Scans all hospitals and blood banks.
        Calculates deficits, surpluses, and units at risk of expiration.
        """
        cursor = self.conn.cursor()
        today = datetime.now().date()

        # Get facilities
        cursor.execute("SELECT * FROM facilities")
        facilities = [dict(row) for row in cursor.fetchall()]
        facilities_by_id = {f["id"]: f for f in facilities}

        # Get all available inventory
        cursor.execute("""
            SELECT id, facility_id, blood_group, units, collection_date, expiry_date 
            FROM inventory 
            WHERE status = 'AVAILABLE'
        """)
        inventory = [dict(row) for row in cursor.fetchall()]

        # Aggregate current stock per facility and blood group
        stock_map = {f["id"]: {bg: 0 for bg in RBC_COMPATIBILITY.keys()} for f in facilities}
        expiring_soon_batches = [] # Expiry in <= 5 days

        for item in inventory:
            f_id = item["facility_id"]
            bg = item["blood_group"]
            u = item["units"]
            if f_id in stock_map and bg in stock_map[f_id]:
                stock_map[f_id][bg] += u

            # Check expiry
            exp_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d").date()
            days_left = (exp_date - today).days
            if days_left <= 5:
                item_copy = dict(item)
                item_copy["days_left"] = days_left
                item_copy["facility_name"] = facilities_by_id[f_id]["name"]
                item_copy["facility_type"] = facilities_by_id[f_id]["type"]
                expiring_soon_batches.append(item_copy)

        # Detect Hospital Deficits & Blood Bank Surpluses
        deficits = []
        surpluses = []

        for f in facilities:
            f_id = f["id"]
            if f["type"] == "HOSPITAL":
                for bg in RBC_COMPATIBILITY.keys():
                    cur_stock = stock_map[f_id][bg]
                    target_stock = get_safety_stock_threshold(f["capacity_beds"], bg)
                    if cur_stock < target_stock:
                        shortage = target_stock - cur_stock
                        severity = "CRITICAL" if cur_stock <= 2 else "WARNING"
                        deficits.append({
                            "facility_id": f_id,
                            "facility_name": f["name"],
                            "blood_group": bg,
                            "current_stock": cur_stock,
                            "target_stock": target_stock,
                            "shortage": shortage,
                            "severity": severity,
                            "distance_km": f["distance_km"]
                        })
            else:
                # Blood Bank: Anything above reserve buffer of 20 units is available for distribution
                for bg in RBC_COMPATIBILITY.keys():
                    cur_stock = stock_map[f_id][bg]
                    if cur_stock > 15:
                        surpluses.append({
                            "facility_id": f_id,
                            "facility_name": f["name"],
                            "blood_group": bg,
                            "available_surplus": cur_stock - 15,
                            "total_stock": cur_stock,
                            "distance_km": f["distance_km"]
                        })

        return {
            "deficits": sorted(deficits, key=lambda x: (0 if x["severity"] == "CRITICAL" else 1, -x["shortage"])),
            "surpluses": surpluses,
            "expiring_soon_batches": sorted(expiring_soon_batches, key=lambda x: x["days_left"]),
            "facilities": facilities_by_id
        }

    def generate_optimal_transfers(self):
        """
        Creates actionable transfer recommendations:
        1. Prioritize near-expiry batches to high-volume deficit facilities to eliminate wastage.
        2. Match remaining hospital deficits from nearest blood banks with compatible blood groups.
        """
        balance = self.analyze_network_balance()
        deficits = balance["deficits"]
        expiring_batches = balance["expiring_soon_batches"]
        surpluses = balance["surpluses"]
        facilities = balance["facilities"]

        recommended_transfers = []
        used_surplus_tracker = {}

        # 1. Wastage Prevention Matching: Route near-expiry units first
        for exp_batch in expiring_batches:
            if exp_batch["days_left"] < 0:
                continue # Already expired

            bg = exp_batch["blood_group"]
            units_available = exp_batch["units"]
            source_id = exp_batch["facility_id"]

            # Find matching deficit hospital
            for d in deficits:
                if d["shortage"] <= 0:
                    continue

                # Check compatibility: Can exp_batch blood go to d["blood_group"]?
                compatible_donors = RBC_COMPATIBILITY.get(d["blood_group"], [])
                if bg in compatible_donors:
                    transfer_qty = min(units_available, d["shortage"])
                    if transfer_qty > 0:
                        dist = abs(facilities[source_id]["distance_km"] - d["distance_km"]) + 2.0
                        eta_minutes = int(dist * 3.5 + 10)

                        recommended_transfers.append({
                            "source_id": source_id,
                            "source_name": facilities[source_id]["name"],
                            "target_id": d["facility_id"],
                            "target_name": d["facility_name"],
                            "blood_group": bg,
                            "units": transfer_qty,
                            "priority": "URGENT",
                            "reason": f"Wastage Prevention: Batch expires in {exp_batch['days_left']} days; rerouted to meet critical deficit",
                            "distance_km": round(dist, 1),
                            "eta_minutes": eta_minutes,
                            "compatibility_type": "Exact Match" if bg == d["blood_group"] else f"Universal Alternative ({bg} → {d['blood_group']})"
                        })

                        units_available -= transfer_qty
                        d["shortage"] -= transfer_qty
                        if units_available <= 0:
                            break

        # 2. Standard Deficit Replenishment from Blood Bank Surpluses
        for d in deficits:
            if d["shortage"] <= 0:
                continue

            compatible_groups = RBC_COMPATIBILITY.get(d["blood_group"], [d["blood_group"]])
            
            # Try exact match first, then compatible donors
            for donor_bg in compatible_groups:
                if d["shortage"] <= 0:
                    break

                for s in surpluses:
                    if s["blood_group"] == donor_bg:
                        key = (s["facility_id"], donor_bg)
                        claimed = used_surplus_tracker.get(key, 0)
                        available = s["available_surplus"] - claimed

                        if available > 0:
                            transfer_qty = min(available, d["shortage"])
                            dist = abs(facilities[s["facility_id"]]["distance_km"] - d["distance_km"]) + 2.5
                            eta_minutes = int(dist * 3.5 + 10)

                            priority = "CRITICAL_EMERGENCY" if d["severity"] == "CRITICAL" else "ROUTINE"

                            recommended_transfers.append({
                                "source_id": s["facility_id"],
                                "source_name": s["facility_name"],
                                "target_id": d["facility_id"],
                                "target_name": d["facility_name"],
                                "blood_group": donor_bg,
                                "units": transfer_qty,
                                "priority": priority,
                                "reason": f"Inventory Rebalance: Restoring safety reserve for {d['blood_group']}",
                                "distance_km": round(dist, 1),
                                "eta_minutes": eta_minutes,
                                "compatibility_type": "Exact Match" if donor_bg == d["blood_group"] else f"Compatible ({donor_bg} → {d['blood_group']})"
                            })

                            used_surplus_tracker[key] = claimed + transfer_qty
                            d["shortage"] -= transfer_qty
                            if d["shortage"] <= 0:
                                break

        return recommended_transfers

    def match_emergency_request(self, hospital_id, blood_group, units_needed):
        """
        Instant SOS Emergency Dispatch Matcher:
        Finds the closest blood bank with compatible units and lowest transit ETA.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM facilities WHERE id = ?", (hospital_id,))
        hospital = dict(cursor.fetchone())

        compatible_groups = RBC_COMPATIBILITY.get(blood_group, [blood_group])
        
        # Query blood banks with stock
        query = f"""
            SELECT f.id as facility_id, f.name, f.distance_km, f.contact_phone,
                   i.blood_group, SUM(i.units) as total_units
            FROM facilities f
            JOIN inventory i ON f.id = i.facility_id
            WHERE f.type = 'BLOOD_BANK' 
              AND i.status = 'AVAILABLE'
              AND i.blood_group IN ({','.join(['?']*len(compatible_groups))})
            GROUP BY f.id, i.blood_group
            HAVING total_units > 0
        """
        cursor.execute(query, compatible_groups)
        candidates = [dict(row) for row in cursor.fetchall()]

        if not candidates:
            return {"success": False, "message": f"No compatible units available in regional blood banks for {blood_group}!"}

        # Score candidates: exact match bonus, lowest distance
        scored_candidates = []
        for c in candidates:
            dist = abs(hospital["distance_km"] - c["distance_km"]) + 1.5
            eta = int(dist * 3.0 + 8)
            is_exact = 1 if c["blood_group"] == blood_group else 0
            # Higher score is better
            score = (100 if is_exact else 50) - (dist * 2) + min(c["total_units"], 20)
            scored_candidates.append({
                **c,
                "distance_km": round(dist, 1),
                "eta_minutes": eta,
                "is_exact_match": bool(is_exact),
                "score": score
            })

        scored_candidates.sort(key=lambda x: -x["score"])
        best = scored_candidates[0]
        allocated_units = min(units_needed, best["total_units"])

        return {
            "success": True,
            "best_match": best,
            "allocated_units": allocated_units,
            "hospital_name": hospital["name"],
            "requested_group": blood_group,
            "dispatched_group": best["blood_group"],
            "eta_minutes": best["eta_minutes"],
            "source_name": best["name"],
            "source_id": best["facility_id"]
        }
