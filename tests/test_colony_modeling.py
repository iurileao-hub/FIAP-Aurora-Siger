import math
from aurora_siger.colony import topology
from aurora_siger.colony.modeling import MathematicalModeling


def _model():
    return MathematicalModeling(topology.build_graph())


def test_generation_capacity_is_real_210():
    assert _model().generation_capacity == 210.0


def test_initial_consumption_is_805():
    m = _model()
    assert round(m.total_consumption(0), 1) == 80.5


def test_exponential_growth():
    m = _model()
    c0 = m.total_consumption(0)
    assert math.isclose(m.total_consumption(1), c0 * math.exp(0.12), rel_tol=1e-6)


def test_derivative_matches_analytic():
    m = _model()
    # d/dt C0 e^{rt} = r * C(t)
    t = 3.0
    assert math.isclose(m.consumption_derivative(t),
                        0.12 * m.total_consumption(t), rel_tol=1e-3)


def test_energy_loss_grows_with_distance():
    m = _model()
    assert m.energy_loss_by_distance(1) < m.energy_loss_by_distance(5)


def test_critical_point_around_seven_years():
    m = _model()
    crit = m.predict_critical_point(t_max=50)
    assert crit["critical_year"] is not None
    assert 6.0 <= (crit["critical_year"] - 2026) <= 8.0
