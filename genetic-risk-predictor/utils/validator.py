"""
Input validation for the Genetic Risk Predictor prediction form.
"""

FIELD_RULES = {
    "patient_name":      {"type": str,   "min": 2,   "max": 100},
    "age":               {"type": int,   "min": 1,   "max": 120},
    "bmi":               {"type": float, "min": 10.0,"max": 70.0},
    "blood_pressure":    {"type": int,   "min": 40,  "max": 300},
    "cholesterol":       {"type": int,   "min": 50,  "max": 500},
    "glucose":           {"type": int,   "min": 40,  "max": 600},
    "physical_activity": {"type": int,   "min": 0,   "max": 168},
}

BINARY_FIELDS = [
    "smoking", "family_history", "alcohol_use",
    "genetic_marker_1", "genetic_marker_2", "genetic_marker_3",
    "genetic_marker_4", "genetic_marker_5",
]


def validate_form(form_data: dict) -> tuple[dict, list[str]]:
    """
    Validate and coerce form data.

    Returns:
        (cleaned_data, errors)  — errors is an empty list on success.
    """
    errors: list[str] = []
    cleaned: dict = {}

    # ── Numeric / text fields ─────────────────────────────────────────────
    for field, rules in FIELD_RULES.items():
        raw = form_data.get(field, "").strip()
        if not raw:
            errors.append(f"'{_label(field)}' is required.")
            continue

        try:
            value = rules["type"](raw)
        except (ValueError, TypeError):
            errors.append(f"'{_label(field)}' must be a valid {rules['type'].__name__}.")
            continue

        if rules["type"] == str:
            if len(value) < rules["min"]:
                errors.append(f"'{_label(field)}' must be at least {rules['min']} characters.")
            elif len(value) > rules["max"]:
                errors.append(f"'{_label(field)}' must be at most {rules['max']} characters.")
            else:
                cleaned[field] = value
        else:
            if value < rules["min"]:
                errors.append(f"'{_label(field)}' must be ≥ {rules['min']}.")
            elif value > rules["max"]:
                errors.append(f"'{_label(field)}' must be ≤ {rules['max']}.")
            else:
                cleaned[field] = value

    # ── Binary / checkbox fields ──────────────────────────────────────────
    for field in BINARY_FIELDS:
        raw = form_data.get(field, "0")
        cleaned[field] = 1 if raw in ("1", "on", "true", "yes") else 0

    return cleaned, errors


def _label(field: str) -> str:
    """Convert snake_case field name to a human-readable label."""
    return field.replace("_", " ").title()
