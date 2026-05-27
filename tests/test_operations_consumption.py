from aurora_siger.operations.consumption import (
    heating_consumption_kw, current_consumption_kw,
)

# The habitat has ~4 kW of internal gain (people + equipment), which passively
# covers the envelope loss down to ≈ -87 °C. The electric heating term only
# becomes positive below that — so a "cold" test needs deep cold (e.g. a night
# under a cold front), not merely -60 °C.
COLD = {"temperature_c": -100.0}
WARM = {"temperature_c": 25.0}


def test_thermal_zero_when_factor_zero():
    assert heating_consumption_kw(-100.0, thermal_factor=0.0) == 0.0


def test_thermal_zero_when_warmer_than_target():
    # target internal 20°C; nothing to heat when it's 25°C outside
    assert heating_consumption_kw(25.0, thermal_factor=1.0) == 0.0


def test_thermal_zero_when_internal_gain_covers_loss():
    # at -60 °C the ~4 kW internal gain still exceeds the envelope loss → 0 kW
    assert heating_consumption_kw(-60.0, thermal_factor=1.0) == 0.0


def test_thermal_positive_in_deep_cold():
    assert heating_consumption_kw(-100.0, thermal_factor=1.0) > 0.0


def test_current_consumption_adds_base_and_thermal():
    mod = {
        "consumption_by_mode": {"off": 0, "minimum": 4, "adequate": 12, "surplus": 12},
        "current_mode": "adequate",
        "thermal_factor": 0.4,
    }
    base = 12
    expected = base + heating_consumption_kw(COLD["temperature_c"], 0.4)
    assert current_consumption_kw(mod, COLD) == expected


def test_power_factor_scales_base_not_thermal():
    mod = {
        "consumption_by_mode": {"off": 0, "minimum": 4, "adequate": 12, "surplus": 12},
        "current_mode": "adequate",
        "thermal_factor": 1.0,
    }
    deep_cold = {"temperature_c": -100.0}
    thermal = heating_consumption_kw(-100.0, 1.0)
    full = current_consumption_kw(mod, deep_cold, power_factor=1.0)
    half = current_consumption_kw(mod, deep_cold, power_factor=0.5)
    # base (12) halves; thermal term is unchanged
    assert abs(full - (12 + thermal)) < 1e-9
    assert abs(half - (6 + thermal)) < 1e-9


def test_power_factor_defaults_to_one():
    mod = {
        "consumption_by_mode": {"off": 0, "minimum": 4, "adequate": 12, "surplus": 12},
        "current_mode": "adequate",
        "thermal_factor": 0.0,
    }
    warm = {"temperature_c": 25.0}
    assert current_consumption_kw(mod, warm) == 12  # default power_factor=1.0
