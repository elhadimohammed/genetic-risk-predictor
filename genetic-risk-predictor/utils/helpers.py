"""
Utility helpers for the Genetic Risk Predictor.
"""


def classify_risk(probability: float) -> str:
    """
    Convert a raw probability (0–1) to a risk level label.

    Thresholds:
        < 0.35  → Low
        0.35–0.65 → Medium
        > 0.65  → High
    """
    if probability < 0.35:
        return "Low"
    elif probability < 0.65:
        return "Medium"
    else:
        return "High"


def risk_color(level: str) -> str:
    """Return a CSS class name for a given risk level."""
    return {
        "Low":    "risk-low",
        "Medium": "risk-medium",
        "High":   "risk-high",
    }.get(level, "risk-low")


def risk_icon(level: str) -> str:
    """Return an emoji icon for a given risk level."""
    return {
        "Low":    "✅",
        "Medium": "⚠️",
        "High":   "🚨",
    }.get(level, "✅")


def format_percentage(probability: float) -> str:
    """Format probability as a percentage string."""
    return f"{probability * 100:.1f}%"


def format_result(probability: float) -> dict:
    """
    Build a complete result dict used by the result template.
    """
    level = classify_risk(probability)
    return {
        "probability":  probability,
        "percentage":   format_percentage(probability),
        "risk_level":   level,
        "risk_color":   risk_color(level),
        "risk_icon":    risk_icon(level),
        "description":  _risk_description(level),
        "advice":       _risk_advice(level),
    }


def _risk_description(level: str) -> str:
    return {
        "Low": (
            "Your current health profile indicates a low probability of developing "
            "the target disease. Continue maintaining your healthy lifestyle."
        ),
        "Medium": (
            "Your health profile shows a moderate risk level. Several indicators "
            "suggest you should consult a healthcare professional for a comprehensive "
            "evaluation."
        ),
        "High": (
            "Your health profile indicates a high probability of disease risk. "
            "We strongly recommend consulting a specialist as soon as possible for "
            "a thorough medical assessment."
        ),
    }.get(level, "")


def _risk_advice(level: str) -> list[str]:
    base = [
        "Maintain a balanced diet rich in fruits and vegetables.",
        "Exercise regularly — at least 150 minutes of moderate activity per week.",
        "Avoid tobacco products and limit alcohol consumption.",
        "Schedule annual health screenings.",
    ]
    medium = [
        "Monitor your blood pressure and cholesterol every 3–6 months.",
        "Discuss your family history with your doctor.",
        "Consider a personalised nutrition and fitness plan.",
    ]
    high = [
        "Schedule an appointment with a specialist within the next 30 days.",
        "Request a full genetic panel and metabolic blood work.",
        "Track daily vitals (blood pressure, glucose) at home.",
        "Discuss preventive medication options with your physician.",
    ]
    if level == "Low":
        return base
    elif level == "Medium":
        return base[:2] + medium
    else:
        return high + base[:2]
