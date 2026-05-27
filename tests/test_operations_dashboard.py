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


# Task 4: Three screen renderers
from aurora_siger.operations.dashboard import (
    screen_overview, screen_energia, screen_sensores, CONTENT_W, CONTENT_H,
)
from aurora_siger.operations.simulator import init_simulation, step
from aurora_siger.operations.simsnapshot import SimSnapshot


def _snap(n=30):
    state = init_simulation(seed=42)
    for _ in range(n):
        step(state)
    return SimSnapshot(state)


def test_overview_renders_lines_with_battery_label():
    lines = screen_overview(_snap(), CONTENT_W, CONTENT_H)
    assert isinstance(lines, list) and lines
    blob = strip_ansi("".join(lines))
    assert "Bateria" in blob and "Nível" in blob


def test_energia_shows_generation_sources():
    blob = strip_ansi("".join(screen_energia(_snap(), CONTENT_W, CONTENT_H)))
    assert "Solar" in blob and "Eólica" in blob and "Nuclear" in blob


def test_sensores_shows_climate_fields():
    blob = strip_ansi("".join(screen_sensores(_snap(), CONTENT_W, CONTENT_H)))
    assert "Temperatura" in blob and "Vento" in blob and "tau" in blob.lower()


def test_screens_handle_fresh_state_without_crashing():
    fresh = SimSnapshot(init_simulation(seed=1))  # nothing stepped
    for screen in (screen_overview, screen_energia, screen_sensores):
        assert isinstance(screen(fresh, CONTENT_W, CONTENT_H), list)


# Task 5: Three more screen renderers (Módulos, Eventos, Hierarquia)
from aurora_siger.operations.dashboard import (
    screen_modulos, screen_eventos, screen_hierarquia,
)


def test_modulos_lists_all_thirteen():
    blob = strip_ansi("".join(screen_modulos(_snap(), CONTENT_W, CONTENT_H)))
    assert "13 total" in blob or "/ 13" in blob


def test_eventos_mentions_storm_and_failures():
    blob = strip_ansi("".join(screen_eventos(_snap(), CONTENT_W, CONTENT_H)))
    assert "Tempestade" in blob or "Frente fria" in blob or "Falha" in blob


def test_hierarquia_renders_three_criticality_levels():
    blob = strip_ansi("".join(screen_hierarquia(_snap(), CONTENT_W, CONTENT_H)))
    assert "Vital" in blob and "Sustenance" in blob and "Expansion" in blob


def test_part2_screens_handle_fresh_state():
    fresh = SimSnapshot(init_simulation(seed=1))
    for screen in (screen_modulos, screen_eventos, screen_hierarquia):
        assert isinstance(screen(fresh, CONTENT_W, CONTENT_H), list)
