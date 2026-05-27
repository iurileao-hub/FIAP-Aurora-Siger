"""SimSnapshot — read-only adapter over a live simulator state (Fase 3, §4).

Replaces the team `main` branch's DataStorage singleton. The dashboard reads
everything it draws through this thin façade, so the live front-end (cli.py
calling step() in a loop) and the headless notebook share one data-access
layer over the simulator's plain dicts.

`.get(key, default)` returns a single "current" value (live climate/battery
fields, or the latest entry of a recorded history series). `.history(key,
last_n)` returns a recent window of a series. `.modules()` returns the module
table with derived operational status and current consumption. The snapshot
never mutates state.
"""

from aurora_siger.operations.consumption import current_consumption_kw
from aurora_siger.operations.failures import is_operational

# Scalars read live from climate/battery (always present).
_LIVE = {
    "sol": lambda st: st["climate"]["sol"],
    "hour": lambda st: st["climate"]["hour"],
    "temperature_c": lambda st: st["climate"]["temperature_c"],
    "wind_ms": lambda st: st["climate"]["wind_ms"],
    "tau": lambda st: st["climate"]["tau"],
    "storm": lambda st: st["climate"]["storm"],
    "panel_factor": lambda st: st["climate"]["panel_factor"],
    "battery_kwh": lambda st: st["battery"]["current_charge_kwh"],
    "battery_max_kwh": lambda st: st["battery"]["max_capacity_kwh"],
    "battery_pct": lambda st: (
        st["battery"]["current_charge_kwh"] / st["battery"]["max_capacity_kwh"] * 100.0
    ),
    "tick": lambda st: len(st["history"]["total_generation_kw"]),
}

# "Current" scalars taken from the last entry of a recorded history series.
_LATEST = {
    "energy_level": "energy_level",
    "slope": "slope",
    "predicted_delta": "predicted_delta",
    "broken_count": "broken_count",
    "generation_kw": "total_generation_kw",
    "consumption_kw": "total_consumption_kw",
    "solar_kw": "solar_generation_kw",
    "wind_kw": "wind_generation_kw",
    "nuclear_kw": "nuclear_generation_kw",
}


class SimSnapshot:
    """Read-only view over a simulator `state` dict."""

    def __init__(self, state):
        self._state = state

    def get(self, key, default=None):
        st = self._state
        if key in _LIVE:
            return _LIVE[key](st)
        if key in _LATEST:
            series = st["history"][_LATEST[key]]
            return series[-1] if series else default
        return default

    def history(self, series_key, last_n=None):
        """Recent window of a history series (by its HISTORY_KEYS name)."""
        series = self._state["history"].get(series_key, [])
        if last_n is None:
            return list(series)
        return list(series)[-last_n:]

    def modules(self):
        """Module table with derived operational status and live consumption."""
        from aurora_siger.operations.modules import MODULES
        climate = self._state["climate"]
        rows = []
        for m in MODULES:
            active = is_operational(m)
            rows.append({
                "id": m["id"],
                "name": m["name"],
                "type": m["type"],
                "current_mode": m["current_mode"],
                "consumption_kw": current_consumption_kw(m, climate) if active else 0.0,
                "active": active,
                "broken": m.get("broken", False),
            })
        return rows

    def criticality_tree(self):
        """The live criticality tree (Vital → Sustenance → Expansion)."""
        return self._state["criticality_tree"]
