"""Telemetry validation against safe operating ranges."""

from typing import Any


# Safe operating ranges for pre-launch telemetry validation.
# "range" rules check min <= value <= max; "binary" rules check value == expected.
# Units: temp in °C, energy in %, vibration in g, pressure in atm.
RULES: dict[str, dict[str, Any]] = {
    "internal_temp":        {"type": "range",  "min": 18,   "max": 26},
    "external_temp":        {"type": "range",  "min": -65,  "max": 125},
    "structural_integrity": {"type": "binary", "expected": 1},
    "energy":               {"type": "range",  "min": 60,   "max": 100},
    "vibration":            {"type": "range",  "min": 0.1,  "max": 0.5},
    "tank_pressure":        {"type": "range",  "min": 270,  "max": 340},
    "critical_modules":     {"type": "binary", "expected": 1},
}


class Validator:
    """Validates a telemetry reading against predefined safe ranges.

    Args:
        rules: Override the default RULES dictionary if needed.
    """

    def __init__(self, rules: dict[str, dict[str, Any]] | None = None):
        self.rules = rules or RULES

    def validate_item(self, item: dict[str, float | int]) -> bool:
        """Return True if all telemetry values are within safe ranges."""
        for col, rule in self.rules.items():
            value = item[col]
            if rule["type"] == "binary":
                if value != rule["expected"]:
                    return False
            else:
                mn, mx = rule.get("min"), rule.get("max")
                if mn is not None and value < mn:
                    return False
                if mx is not None and value > mx:
                    return False
        return True

    def validate_item_detail(self, item: dict[str, float | int]) -> dict[str, str]:
        """Return per-column validation results (OK or FAILED with reason)."""
        result: dict[str, str] = {}
        for col, rule in self.rules.items():
            value = item[col]
            if rule["type"] == "binary":
                result[col] = "OK" if value == rule["expected"] else "FAILED"
            else:
                mn, mx = rule.get("min"), rule.get("max")
                if mn is not None and value < mn:
                    result[col] = f"FAILED ({value} < {mn})"
                elif mx is not None and value > mx:
                    result[col] = f"FAILED ({value} > {mx})"
                else:
                    result[col] = "OK"
        return result
