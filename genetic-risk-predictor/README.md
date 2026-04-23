# Genetic Risk Predictor

An educational web application that predicts disease risk probability using a Logistic Regression model trained on synthetic health and genetic indicator data.

> ⚠️ **Educational use only** — not for clinical diagnosis.

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | HTML5, CSS3, Vanilla JS, Chart.js |
| Backend    | Python 3.11+ · Flask 3.x          |
| ML Engine  | scikit-learn · Logistic Regression|
| Database   | SQLite (default) · SQL Server     |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate training data
```bash
python data/generate_dataset.py
```

### 3. Train the model
```bash
python model/train_model.py
```

### 4. Run the app
```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## SQL Server Configuration

By default the app uses **SQLite** (`database/predictions.db`) — no setup needed.

To switch to SQL Server:

1. Create the database and run `database/schema.sql`
2. Set environment variables before starting the app:

```powershell
$env:USE_SQLSERVER = "true"
$env:DB_SERVER     = "YOUR_SERVER"
$env:DB_NAME       = "GeneticRiskPredictor"
$env:DB_DRIVER     = "ODBC Driver 17 for SQL Server"
$env:DB_TRUSTED    = "yes"          # Windows Auth
# --- OR for SQL Auth ---
$env:DB_TRUSTED    = "no"
$env:DB_USER       = "sa"
$env:DB_PASSWORD   = "YourPassword"
```

---

## Features

- 📋 **Prediction Form** — 14-feature health input (clinical + lifestyle + genetic)
- 🔬 **ML Prediction** — Logistic Regression probability score
- 📊 **Risk Dashboard** — Animated gauge chart, risk level badge, personalised advice
- 🗂️ **History Table** — Paginated, clickable rows, animated probability bars
- 🔗 **REST API** — `GET /api/history?limit=20&offset=0`

---

## Folder Structure

```
genetic-risk-predictor/
├── app.py                  # Flask routes
├── requirements.txt
├── model/
│   ├── train_model.py      # Training script
│   ├── logistic_model.pkl  # Saved model
│   ├── scaler.pkl
│   └── feature_columns.pkl
├── database/
│   ├── db.py               # DB helper (SQLite / SQL Server)
│   ├── schema.sql          # SQL Server DDL
│   └── predictions.db      # SQLite file (auto-created)
├── data/
│   ├── generate_dataset.py
│   └── dataset.csv
├── templates/
│   ├── index.html
│   ├── predict.html
│   ├── result.html
│   └── history.html
├── static/
│   ├── css/style.css
│   └── js/script.js
└── utils/
    ├── helpers.py
    └── validator.py
```
