"""
Genetic Risk Predictor — Flask Application
==========================================
Routes:
  GET  /            → Landing page
  GET  /predict     → Prediction form
  POST /predict     → Run model & save result
  GET  /result/<id> → Show a single result
  GET  /history     → Paginated prediction history
  GET  /api/history → JSON history API
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import joblib
import numpy as np
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from database.db import get_prediction_by_id, get_history, get_total_count, save_prediction
from utils.helpers import format_result
from utils.validator import validate_form

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "grp-secret-key-change-in-production"

# ── Load ML artefacts ────────────────────────────────────────────────────────
MODEL_DIR = ROOT / "model"

try:
    model        = joblib.load(MODEL_DIR / "logistic_model.pkl")
    scaler       = joblib.load(MODEL_DIR / "scaler.pkl")
    feature_cols = joblib.load(MODEL_DIR / "feature_columns.pkl")
    MODEL_READY  = True
except FileNotFoundError:
    MODEL_READY  = False
    model = scaler = feature_cols = None
    print("[WARNING] Model artefacts not found. Run:  python model/train_model.py")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    stats = {
        "total_predictions": get_total_count(),
        "model_ready":       MODEL_READY,
    }
    return render_template("index.html", stats=stats)


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return render_template("predict.html", errors=[], form_data={})

    # POST — validate → predict → store → redirect
    form_data = request.form.to_dict()
    cleaned, errors = validate_form(form_data)

    if errors:
        return render_template("predict.html", errors=errors, form_data=form_data)

    if not MODEL_READY:
        flash("Model not trained yet. Please run model/train_model.py first.", "error")
        return render_template("predict.html", errors=[], form_data=form_data)

    # Build feature vector
    features = np.array([[cleaned[col] for col in feature_cols]])
    features_scaled = scaler.transform(features)

    probability = float(model.predict_proba(features_scaled)[0][1])
    result      = format_result(probability)

    # Persist
    record = {**cleaned, **{
        "risk_probability": probability,
        "risk_level":       result["risk_level"],
    }}
    new_id = save_prediction(record)

    return redirect(url_for("result", prediction_id=new_id))


@app.route("/result/<int:prediction_id>")
def result(prediction_id: int):
    record = get_prediction_by_id(prediction_id)
    if not record:
        flash("Prediction not found.", "error")
        return redirect(url_for("index"))

    result_data = format_result(record["risk_probability"])
    return render_template("result.html", record=record, result=result_data)


@app.route("/history")
def history():
    page     = max(1, request.args.get("page", 1, type=int))
    per_page = 10
    offset   = (page - 1) * per_page
    total    = get_total_count()
    records  = get_history(limit=per_page, offset=offset)
    total_pages = max(1, -(-total // per_page))  # ceiling division

    # Annotate each record with formatted result
    for r in records:
        r["result"] = format_result(r["risk_probability"])

    return render_template(
        "history.html",
        records=records,
        page=page,
        total_pages=total_pages,
        total=total,
        per_page=per_page,
    )


@app.route("/api/history")
def api_history():
    limit  = min(request.args.get("limit", 20, type=int), 100)
    offset = request.args.get("offset", 0, type=int)
    return jsonify({
        "total":   get_total_count(),
        "records": get_history(limit=limit, offset=offset),
    })


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
