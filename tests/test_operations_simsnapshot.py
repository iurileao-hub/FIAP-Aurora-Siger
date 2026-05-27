from aurora_siger.operations.simulator import init_simulation, step
from aurora_siger.operations.simsnapshot import SimSnapshot


def _stepped(n=10, seed=42):
    state = init_simulation(seed)
    for _ in range(n):
        step(state)
    return state


def test_get_live_values_before_any_step():
    snap = SimSnapshot(init_simulation(seed=42))
    assert snap.get("tick") == 0
    assert snap.get("sol") == 0 and snap.get("hour") == 0
    assert 0.0 <= snap.get("battery_pct") <= 100.0
    # latest-history scalars fall back to the default when nothing stepped yet
    assert snap.get("energy_level", "NOMINAL") == "NOMINAL"
    assert snap.get("generation_kw", 0.0) == 0.0


def test_get_reflects_latest_step():
    state = _stepped(5)
    snap = SimSnapshot(state)
    assert snap.get("tick") == 5
    assert snap.get("generation_kw") == state["history"]["total_generation_kw"][-1]
    assert snap.get("energy_level") == state["history"]["energy_level"][-1]
    assert snap.get("temperature_c") == state["climate"]["temperature_c"]


def test_get_unknown_key_returns_default():
    snap = SimSnapshot(init_simulation(seed=1))
    assert snap.get("nope", "fallback") == "fallback"


def test_history_returns_recent_window():
    state = _stepped(60)
    snap = SimSnapshot(state)
    last48 = snap.history("total_generation_kw", 48)
    assert len(last48) == 48
    assert last48 == state["history"]["total_generation_kw"][-48:]
    assert snap.history("total_generation_kw") == state["history"]["total_generation_kw"]


def test_modules_carry_status_and_consumption():
    snap = SimSnapshot(_stepped(3))
    mods = snap.modules()
    assert len(mods) == 13
    m = mods[0]
    assert {"id", "name", "type", "current_mode", "consumption_kw", "active", "broken"} <= set(m)
    assert isinstance(m["active"], bool)
    assert m["consumption_kw"] >= 0.0


def test_criticality_tree_exposed():
    snap = SimSnapshot(_stepped(1))
    root = snap.criticality_tree()
    assert [c.name for c in root.children] == ["Vital", "Sustenance", "Expansion"]


def test_battery_pct_matches_charge_over_capacity():
    state = _stepped(20)
    snap = SimSnapshot(state)
    expected = state["battery"]["current_charge_kwh"] / state["battery"]["max_capacity_kwh"] * 100.0
    assert abs(snap.get("battery_pct") - expected) < 1e-9
