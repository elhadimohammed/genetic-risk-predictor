"""
Generate a synthetic dataset for the Genetic Risk Predictor.
Run this script once to create data/dataset.csv before training.
"""
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)
N = 1200

age              = np.random.randint(20, 80, N)
bmi              = np.round(np.random.uniform(16.0, 45.0, N), 1)
blood_pressure   = np.random.randint(60, 180, N)
cholesterol      = np.random.randint(120, 320, N)
glucose          = np.random.randint(60, 250, N)
smoking          = np.random.randint(0, 2, N)
family_history   = np.random.randint(0, 2, N)
physical_activity= np.random.randint(0, 8, N)   # hours/week
alcohol_use      = np.random.randint(0, 2, N)
genetic_marker_1 = np.random.randint(0, 2, N)
genetic_marker_2 = np.random.randint(0, 2, N)
genetic_marker_3 = np.random.randint(0, 2, N)
genetic_marker_4 = np.random.randint(0, 2, N)
genetic_marker_5 = np.random.randint(0, 2, N)

# Risk score formula (weighted)
risk_score = (
    0.03 * age
    + 0.05 * bmi
    + 0.02 * blood_pressure
    + 0.01 * cholesterol
    + 0.03 * glucose
    + 1.5  * smoking
    + 2.0  * family_history
    - 0.3  * physical_activity
    + 1.0  * alcohol_use
    + 1.2  * genetic_marker_1
    + 0.8  * genetic_marker_2
    + 1.0  * genetic_marker_3
    + 0.6  * genetic_marker_4
    + 0.9  * genetic_marker_5
    + np.random.normal(0, 1.5, N)
)

# Normalise to [0,1] then threshold at 0.5
risk_prob = 1 / (1 + np.exp(-0.15 * (risk_score - risk_score.mean())))
disease_risk = (risk_prob >= 0.5).astype(int)

df = pd.DataFrame({
    "age": age,
    "bmi": bmi,
    "blood_pressure": blood_pressure,
    "cholesterol": cholesterol,
    "glucose": glucose,
    "smoking": smoking,
    "family_history": family_history,
    "physical_activity": physical_activity,
    "alcohol_use": alcohol_use,
    "genetic_marker_1": genetic_marker_1,
    "genetic_marker_2": genetic_marker_2,
    "genetic_marker_3": genetic_marker_3,
    "genetic_marker_4": genetic_marker_4,
    "genetic_marker_5": genetic_marker_5,
    "disease_risk": disease_risk,
})

out = Path(__file__).parent / "dataset.csv"
df.to_csv(out, index=False)
print(f"Dataset saved to {out}  ({len(df)} rows, {disease_risk.sum()} positive cases)")
