import pytest
from aurora_siger.operations.prediction import (
    linear_regression, predict, fit_wind_power_model,
    wind_power_forecast, predict_next_wind_power, fit_energy_trend,
)


def test_linear_regression_recovers_exact_line():
    # y = 2x + 1 exactly
    xs = [0, 1, 2, 3, 4]
    ys = [1, 3, 5, 7, 9]
    a, b = linear_regression(xs, ys)
    assert abs(a - 2.0) < 1e-9
    assert abs(b - 1.0) < 1e-9


def test_linear_regression_raises_on_degenerate_input():
    with pytest.raises(ValueError):
        linear_regression([1.0], [2.0])          # < 2 points
    with pytest.raises(ValueError):
        linear_regression([1, 2], [3])           # mismatched lengths
    with pytest.raises(ValueError):
        linear_regression([5, 5, 5], [1, 2, 3])  # constant xs (no variance)


def test_predict_is_affine():
    assert predict(2.0, 1.0, 3) == 7.0


def test_fit_wind_power_model_filters_zero_generation():
    history = {
        "wind_ms": [0.0, 6.0, 8.0, 10.0],
        "wind_generation_kw": [0.0, 10.0, 20.0, 30.0],  # first point below cut-in
    }
    a, b = fit_wind_power_model(history)
    assert a > 0  # power rises with wind over the linear region


def test_wind_power_forecast_clamps_to_zero():
    # a line that would predict negative for low wind must clamp at 0
    assert wind_power_forecast(5.0, -100.0, 1.0) == 0.0


def test_predict_next_wind_power_end_to_end():
    history = {
        "wind_ms": [6.0, 8.0, 10.0],
        "wind_generation_kw": [10.0, 20.0, 30.0],
    }
    assert predict_next_wind_power(history, 12.0) > 30.0


def test_fit_energy_trend_positive_when_rising():
    slope, predicted = fit_energy_trend([1.0, 2.0, 3.0, 4.0])
    assert slope > 0
    assert predicted > 4.0  # extrapolates the next point


def test_fit_energy_trend_negative_when_falling():
    slope, _ = fit_energy_trend([4.0, 3.0, 2.0, 1.0])
    assert slope < 0


def test_fit_energy_trend_flat_series_is_zero_slope():
    slope, predicted = fit_energy_trend([5.0, 5.0, 5.0])
    assert abs(slope) < 1e-9
    assert abs(predicted - 5.0) < 1e-9


def test_fit_energy_trend_degenerate_short_input():
    assert fit_energy_trend([]) == (0.0, 0.0)
    assert fit_energy_trend([7.0]) == (0.0, 7.0)
