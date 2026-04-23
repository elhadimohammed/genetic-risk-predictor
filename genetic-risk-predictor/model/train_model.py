"""
Train the Logistic Regression model for Genetic Risk Predictor.
Outputs: logistic_model.pkl, scaler.pkl, feature_columns.pkl
"""
import sys
from pathlib import Path

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DATA_PATH  = ROOT / "data" / "dataset.csv"
MODEL_DIR  = Path(__file__).parent

FEATURE_COLS = [
    "age", "bmi", "blood_pressure", "cholesterol", "glucose",
    "smoking", "family_history", "physical_activity", "alcohol_use",
    "genetic_marker_1", "genetic_marker_2", "genetic_marker_3",
    "genetic_marker_4", "genetic_marker_5",
]
TARGET_COL = "disease_risk"


def train():
    if not DATA_PATH.exists():
        print(f"[ERROR] Dataset not found: {DATA_PATH}")
        print("Run:  python data/generate_dataset.py  first.")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows from {DATA_PATH}")

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = LogisticRegression(
        C=1.0,
        max_iter=500,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train_s, y_train)

    y_pred  = model.predict(X_test_s)
    y_proba = model.predict_proba(X_test_s)[:, 1]

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=["Low Risk", "High Risk"]))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")

    # Save artefacts
    joblib.dump(model,        MODEL_DIR / "logistic_model.pkl")
    joblib.dump(scaler,       MODEL_DIR / "scaler.pkl")
    joblib.dump(FEATURE_COLS, MODEL_DIR / "feature_columns.pkl")

    print(f"\nModel artefacts saved to {MODEL_DIR}")


if __name__ == "__main__":
    train()
