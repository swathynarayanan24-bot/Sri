# BloodChain AI – Predictive Blood Supply Management System

> **Predict • Optimize • Save Lives**  
> *A Healthcare Blood-Management Prototype for College Hackathons (Hackwell 2.0)*  
> **Team:** Outliers (#H2O080) • Saranathan College of Engineering

---

## 1. Project Goal

Healthcare facilities frequently struggle with unpredictable blood demand, leading to fatal emergency shortages on one hand and severe wastage due to shelf-life expiration on the other. 

**BloodChain AI** resolves this critical problem by creating an end-to-end predictive blood supply loop:
1. **Collects Blood Inventory & Usage Data** across regional hospitals and blood banks.
2. **Predicts Future Blood Demand** using machine learning (Scikit-learn) trained on historical usage, surgical volume, and emergency cases.
3. **Identifies Shortages & Excess Stock** automatically before critical care emergencies happen.
4. **Monitors Expiration & Shelf-Life** to prevent red blood cell wastage.
5. **Recommends & Dispatches Smart Blood Distribution** between surplus blood banks and deficit hospitals.

---

## 2. Technology Stack

- **Frontend:**
  - Modern Responsive Healthcare Dashboard UI
  - Tailwind CSS + HTML5 + Vanilla JS / React.js components
  - Chart.js for real-time visual analytics
  - Lucide Vector Icons
- **Backend:**
  - Python 3.9+
  - Flask REST API (Clean, modular REST endpoints)
- **Database:**
  - **SQLite (Default for Instant Demo):** Self-contained, zero configuration required.
  - **MySQL (Production Ready):** Clean standard SQL schema easily switchable via configuration.
- **AI / Machine Learning:**
  - Python, Pandas, Scikit-learn (`RandomForestRegressor` / `Ridge`)
  - Multi-variable demand forecasting based on admissions, emergency caseloads, and weekday factors.
  - Distinct **Statistical Fallback Method** when Scikit-learn is not installed or when data is scarce.

---

## 3. System Architecture & Complete Demo Scenario

The prototype demonstrates the complete end-to-end loop:

```
[Hospital Usage & Demand History] 
               │
               ▼
[Scikit-learn AI Forecasting Model] ──> Predicts 110 units needed for B+
               │
               ▼
[Inventory Monitor] ──> Detects Hospital A only has 75 units (Shortage: 35 units)
               │
               ▼
[Smart Distribution Engine] ──> Finds Blood Bank B has 60 units available
               │
               ▼
[AI Match Recommendation] ──> Transfer 35 units from Blood Bank B → Hospital A
               │
               ▼
[User Approves Distribution] ──> Updates DB, balances stock, triggers Action Alert
```

---

## 4. Application Pages & Menu Breakdown

1. **Dashboard:**
   - 4 Top KPI cards: Total Available Blood Units (`540`), Connected Hospitals (`12`), Blood Banks (`5`), Active Alerts (`3`).
   - Blood Inventory Table with exact quantities and status badges (`Normal`, `Low`, `Critical`) for all 8 blood groups:
     - `A+` (120, Normal, 20 expiring)
     - `A-` (18, Low, 5 expiring)
     - `B+` (75, Normal, 10 expiring)
     - `B-` (8, Critical, 2 expiring)
     - `O+` (150, Normal, 15 expiring)
     - `O-` (12, Low, 4 expiring)
     - `AB+` (30, Normal, 6 expiring)
     - `AB-` (5, Low, 1 expiring)
   - Quick Action buttons: *AI Demand Prediction*, *Manage Inventory*, *Smart Distribution*.
   - Attention warning banner: `3 blood groups need attention (B-, O-, AB-)`.

2. **Blood Inventory:**
   - Detailed batch tracking by facility and component (RBC).
   - **+ Add New Stock Modal:** Register newly collected units with expiry dates.
   - **- Issue / Transfuse Stock Modal:** Deduct units for surgery or trauma resuscitation.
   - Expiry countdown badges (`Safe >15d`, `Moderate 6-15d`, `Critical <=5d`).

3. **AI Demand Prediction:**
   - User inputs: *Hospital* (e.g., Government Hospital), *Blood Group* (e.g., B+), *Period* (7, 14, 30 days).
   - Instant metrics: Current Stock (`75 units`), Predicted Demand (`110 units`), Expected Shortage (`35 units` in red).
   - Interactive line chart comparing Past Demand vs. Predicted Demand (Mon–Sun).
   - AI Recommendation: *"Collect or transfer 35 units of B+ to meet predicted demand."*

4. **Smart Distribution:**
   - Visual Flow: **Hospital A** (`Needs: B+ 35 units`, High Priority) $\longleftrightarrow$ **`[ AI MATCH ]`** $\longrightarrow$ **Blood Bank B** (`Available: B+ 60 units`, Sufficient).
   - One-click **"Approve Distribution"** button.
   - Live state updates: Deducts 35 units from Blood Bank B, replenishes Hospital A, updates inventory, and logs to Alerts.

5. **Alerts:**
   - 🔴 **CRITICAL:** `B- stock is only 8 units.`
   - 🟡 **LOW STOCK:** `O- stock is below required level.`
   - 🟠 **EXPIRY WARNING:** `20 units of A+ may expire soon.`
   - 🟢 **ACTION:** `Transfer B+ from Blood Bank B → Hospital A.`

6. **Reports:**
   - Blood Demand vs. Predicted Demand comparative Bar Chart.
   - Total `540` units Inventory Donut Chart with percentages (`A+ 18.5%`, `B+ 16.7%`, `O+ 27.8%`, etc.).
   - Actionable healthcare logistics insights.

---

## 5. Quick Start Instructions (Two Methods)

### Method A: Standalone Browser Launch (Zero Installation)
Ideal for instant demonstration without setting up Python dependencies:
1. Open the project folder:
   `C:\Users\N. SRI SWATHY\.gemini\antigravity\scratch\blood_demand_optimizer\`
2. Double-click **`prototype.html`** to open it in **Google Chrome** or **Microsoft Edge**.
3. The complete application runs offline with all 6 pages, charts, and interactive workflows.

---

### Method B: Full-Stack Python + Flask Server

#### 1. Requirements Installation
Open Command Prompt or PowerShell in the project directory and run:
```bash
pip install -r requirements.txt
```

#### 2. Initialize Database & Seed Data
```bash
python database.py
```
This creates `bloodchain.db` with all 7 tables:
- `hospitals`
- `blood_banks`
- `blood_inventory`
- `demand_history`
- `predictions`
- `distributions`
- `alerts`

#### 3. Run the Flask Web Server
```bash
python app.py
```
*Or simply double-click `start_prototype.bat`!*

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 6. MySQL Migration Guide

If you wish to switch from SQLite to a live MySQL instance:
1. Install the MySQL Python driver:
   ```bash
   pip install mysql-connector-python
   ```
2. Create the database in MySQL:
   ```sql
   CREATE DATABASE bloodchain_db;
   ```
3. In `database.py`, replace `sqlite3.connect(DB_PATH)` with:
   ```python
   import mysql.connector

   def get_connection():
       return mysql.connector.connect(
           host="localhost",
           user="your_mysql_user",
           password="your_password",
           database="bloodchain_db"
       )
   ```
All SQL statements in `database.py` and `app.py` follow ANSI SQL standard syntax and run identically on MySQL.

---

## 7. Step-by-Step Hackathon Jury Presentation Script

Follow this 2-minute walkthrough to impress the hackathon judges:

1. **Start on Login Screen:**
   - Explain: *"Welcome to BloodChain AI: Predict • Optimize • Save Lives. We manage blood logistics between hospitals and blood banks."*
   - Select User Type: **Hospital (Government Hospital)** $\rightarrow$ click **Login**.

2. **Executive Dashboard:**
   - Point out the 4 KPI cards: **540** Total Units, **12** Hospitals, **5** Blood Banks, **3** Active Alerts.
   - Show the Blood Inventory table: *"Notice that B- is marked Critical (8 units), O- is Low (12 units), and B+ currently has 75 units."*
   - Click the quick-action button **AI Demand Prediction**.

3. **AI Demand Prediction:**
   - Select **Government Hospital** and **B+** $\rightarrow$ click **Predict Demand**.
   - Show the results:
     - Current Stock: **75 units**
     - Predicted Demand: **110 units**
     - Expected Shortage: **35 units** (in red)
   - Highlight the line chart: *"Our Scikit-learn regression model analyzes surgical trends and trauma surges, predicting a demand spike to 110 units by the weekend."*
   - Point out the AI Recommendation: *"Collect or transfer 35 units of B+ to meet predicted demand."*
   - Click **Match Supply $\rightarrow$**.

4. **Smart Distribution:**
   - Show the visual AI Match flow: **Hospital A** (`Needs B+ 35 units`) $\longleftrightarrow$ **`[ AI MATCH ]`** $\longrightarrow$ **Blood Bank B** (`Available B+ 60 units`).
   - Click **"Approve Distribution"**.
   - Observe the confirmation: 35 units are immediately dispatched. Hospital A's requirement drops to 0 (Fulfilled), and Blood Bank B's available stock updates to 25 units.

5. **Alerts & Reports:**
   - Navigate to **Alerts**: Show the newly generated green action alert: *"🟢 ACTION: Transfer 35 units of B+ from Blood Bank B → Hospital A."*
   - Navigate to **Reports**: Show the comparative Bar Chart and the 540-unit Donut Chart with demographic breakdown percentages.
   - Conclude: *"BloodChain AI eliminates manual guesswork, prevents blood wastage, and ensures zero shortage during life-or-death hospital emergencies."*
"# Sri" 
"# Sri" 
"# Sri" 
"# Sri" 
"# sri1" 
