import math
from aurora_siger.operations.rng import RandomLCG


def test_same_seed_is_deterministic():
    a = RandomLCG(42)
    b = RandomLCG(42)
    assert [a.next_int() for _ in range(5)] == [b.next_int() for _ in range(5)]


def test_random_in_unit_interval():
    r = RandomLCG(7)
    for _ in range(1000):
        x = r.random()
        assert 0.0 <= x < 1.0


def test_randint_inclusive_range():
    r = RandomLCG(1)
    seen = {r.randint(1, 6) for _ in range(2000)}
    assert seen == {1, 2, 3, 4, 5, 6}


def test_gauss_mean_and_spread():
    r = RandomLCG(123)
    n = 20000
    xs = [r.gauss(10.0, 2.0) for _ in range(n)]
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / n
    assert abs(mean - 10.0) < 0.1
    assert abs(math.sqrt(var) - 2.0) < 0.1


def test_gauss_is_deterministic():
    a = RandomLCG(99)
    b = RandomLCG(99)
    assert [round(a.gauss(), 9) for _ in range(5)] == [round(b.gauss(), 9) for _ in range(5)]
