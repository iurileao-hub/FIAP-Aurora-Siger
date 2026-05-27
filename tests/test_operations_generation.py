from aurora_siger.operations.generation import (
    generate_solar, generate_wind, generate_nuclear,
)

CLEAR_NOON = {"hour": 12, "tau": 0.5, "panel_factor": 1.0, "wind_ms": 10.0}


def test_nuclear_is_constant_capacity():
    mod = {"max_capacity_kw": 80.0}
    assert generate_nuclear(mod, CLEAR_NOON) == 80.0


def test_solar_zero_at_night():
    mod = {"max_capacity_kw": 100.0}
    night = {"hour": 0, "tau": 0.5, "panel_factor": 1.0}
    assert generate_solar(mod, night) == 0.0


def test_solar_positive_at_noon():
    mod = {"max_capacity_kw": 100.0}
    assert generate_solar(mod, CLEAR_NOON) > 0.0


def test_wind_below_cutin_is_zero():
    mod = {"max_capacity_kw": 30.0}
    assert generate_wind(mod, {"wind_ms": 2.0}) == 0.0


def test_wind_saturates_at_capacity():
    mod = {"max_capacity_kw": 30.0}
    assert generate_wind(mod, {"wind_ms": 100.0}) == 30.0
