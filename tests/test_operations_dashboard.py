from aurora_siger.operations.dashboard import (
    strip_ansi, padto, hbar, sparkline, miniline, fg, RESET,
)


def test_strip_ansi_removes_escapes():
    colored = fg(255, 0, 0) + "hello" + RESET
    assert strip_ansi(colored) == "hello"


def test_padto_pads_to_visible_width_ignoring_ansi():
    colored = fg(0, 255, 0) + "ab" + RESET
    padded = padto(colored, 5)
    assert strip_ansi(padded) == "ab   "      # 2 visible + 3 spaces
    assert len(strip_ansi(padded)) == 5


def test_hbar_fills_proportionally():
    bar = hbar(5, 10, 10, fg(0, 0, 255))
    plain = strip_ansi(bar)
    assert plain.count("█") == 5
    assert len(plain) == 10


def test_hbar_clamps_overflow():
    bar = hbar(20, 10, 8, fg(0, 0, 255))
    assert strip_ansi(bar).count("█") == 8  # clamped to width


def test_sparkline_shape():
    rows = sparkline([1, 2, 3, 4, 5], w=5, h=3)
    assert len(rows) == 3
    assert all(len(strip_ansi(r)) == 5 for r in rows)


def test_sparkline_empty_is_placeholder():
    rows = sparkline([], w=4, h=2)
    assert len(rows) == 2


def test_miniline_shape():
    rows = miniline([1, 3, 2, 5, 4], w=5, h=3)
    assert len(rows) == 3
    assert all(len(strip_ansi(r)) == 5 for r in rows)
