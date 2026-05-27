from aurora_siger.operations import constants as c


def test_horizon_is_seven_sols():
    assert c.TOTAL_STEPS == 168
    assert c.HOURS_PER_SOL == 24


def test_criticality_levels_order():
    assert c.CRITICALITY_LEVELS == ("Vital", "Sustenance", "Expansion")


def test_coldfront_constants_present():
    assert c.COLDFRONT_DELTA_C < 0          # frente fria esfria
    lo, hi = c.COLDFRONT_DURATION_HOURS
    assert 0 < lo <= hi
    assert 0.0 < c.COLDFRONT_PROB_PER_SOL < 1.0


def test_solar_daytime_curve_peaks_at_noon():
    assert c.solar_daytime_curve(0) == 0.0
    assert c.solar_daytime_curve(12) > c.solar_daytime_curve(8)
    assert c.solar_daytime_curve(12) == 1.0
