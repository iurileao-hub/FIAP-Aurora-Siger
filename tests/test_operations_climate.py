from aurora_siger.operations.rng import RandomLCG
from aurora_siger.operations.climate import (
    compute_tau, solar_transmission, sample_wind, sample_temperature,
    update_panel_factor, StormState, ColdFrontState,
)


def test_tau_increases_with_storm_severity():
    assert compute_tau("clear", 0) < compute_tau("moderate", 0) < compute_tau("severe", 0)


def test_solar_transmission_decreases_with_tau():
    assert solar_transmission(0.5) > solar_transmission(3.0)


def test_sample_wind_is_deterministic_per_seed():
    a, b = RandomLCG(5), RandomLCG(5)
    assert [round(sample_wind(h, a), 6) for h in range(24)] == \
           [round(sample_wind(h, b), 6) for h in range(24)]


def test_sample_wind_non_negative():
    r = RandomLCG(3)
    assert all(sample_wind(h, r) >= 0.0 for h in range(24))


def test_panel_factor_degrades_without_cleaning():
    r = RandomLCG(1)
    assert update_panel_factor(1.0, cleaning_drawn=False, rng=r) < 1.0


def test_storm_persists_then_clears():
    r = RandomLCG(1)
    s = StormState()
    s.state = "moderate"
    s.hours_remaining = 2
    s.advance(0.0, 0, 0, r)
    assert s.state == "moderate"  # still 1 hour left
    s.advance(0.0, 0, 1, r)
    assert s.state == "clear"


def test_coldfront_offset_only_when_active():
    cf = ColdFrontState()
    assert cf.temperature_offset() == 0.0
    cf.active = True
    assert cf.temperature_offset() < 0.0


def test_coldfront_clears_after_duration():
    r = RandomLCG(1)
    cf = ColdFrontState()
    cf.active = True
    cf.hours_remaining = 1
    cf.advance(0, 0, r)
    assert cf.active is False
