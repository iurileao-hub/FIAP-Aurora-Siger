from aurora_siger.operations.decision import (
    evaluate_rules, priority_order,
    ACTION_REDUCE, ACTION_ECONOMY, ACTION_CLIMATE, ACTION_EMERGENCY,
)


def test_no_actions_when_healthy():
    snap = {"energy_kw": 200.0, "consumption_kw": 100.0, "storm": "clear"}
    assert evaluate_rules(snap) == []


def test_low_energy_triggers_reduce():
    snap = {"energy_kw": 40.0, "consumption_kw": 30.0, "storm": "clear"}
    assert ACTION_REDUCE in evaluate_rules(snap)


def test_low_energy_and_high_consumption_triggers_economy():
    snap = {"energy_kw": 40.0, "consumption_kw": 80.0, "storm": "clear"}
    actions = evaluate_rules(snap)
    assert ACTION_REDUCE in actions and ACTION_ECONOMY in actions


def test_consumption_above_energy_triggers_emergency():
    snap = {"energy_kw": 100.0, "consumption_kw": 120.0, "storm": "clear"}
    assert ACTION_EMERGENCY in evaluate_rules(snap)


def test_storm_triggers_climate_alert():
    snap = {"energy_kw": 200.0, "consumption_kw": 100.0, "storm": "severe"}
    assert ACTION_CLIMATE in evaluate_rules(snap)


def test_priority_order_matches_criticality_levels():
    assert priority_order() == ["Vital", "Sustenance", "Expansion"]
