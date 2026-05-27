# Fase 3 — M3: Dashboard TUI + CLI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar à simulação determinística do M1/M2 um front-end ao vivo: um dashboard TUI de 6 abas (Overview, Energia, Módulos, Sensores, Eventos, Hierarquia) renderizado sobre um adaptador fino `SimSnapshot`, dirigido por um CLI `aurora` que roda a simulação num thread de pacing — espelhando o par notebook+`mgpeb` da Fase 2.

**Architecture:** As **primitivas visuais** (paleta ANSI, `sparkline`, `hbar`, `miniline`, layout, controle de tela) são colhidas intactas da branch `main` da equipe — código puro e reutilizável. As **telas** são escritas do zero, finas, lendo um `SimSnapshot(state)` que expõe `.get(key, default)`/`.history(key, last_n)`/`.modules()`/`.criticality_tree()` sobre o `state`/`history` do simulador (sem o singleton `DataStorage` do `main`). A 6ª aba — onde o `main` tinha Crew (que não portamos) — vira **Hierarquia**: a árvore de criticidade ao vivo (item 1.1 visualizado). O CLI roda `step()` num thread daemon para pacing visual; o conteúdo permanece determinístico dada a seed.

**Tech Stack:** Python 3.11+, stdlib apenas (`sys`, `os`, `termios`, `tty`, `select`, `threading`, `time`, `argparse`, `math`, `re`), pytest. Sem numpy/curses.

**Trabalho corrente:** repo `/home/ubuntu/projects/FIAP-Aurora-Siger`, branch `main`. M1 e M2 já commitados (`5a0939e`..`dfb1c04`): `aurora_siger/operations/` com o núcleo determinístico + controle/decisão/previsão/falhas; suíte de 245 testes verde.

**Procedência (nota de consolidação do M4):** as primitivas visuais e a linguagem de abas vêm do `main` (`colonia_aurora/display/dashboard.py`); o `SimSnapshot`, as telas finas sobre os nossos dados, e a aba **Hierarquia** (que substitui Crew) são consolidação inédita.

---

## File Structure (M3)

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `aurora_siger/operations/simulator.py` | modificar | extrair `init_simulation(seed)` (state builder reusável pelo CLI ao vivo) |
| `aurora_siger/operations/simsnapshot.py` | criar | `SimSnapshot(state)` — `.get/.history/.modules/.criticality_tree` sobre state/history |
| `aurora_siger/operations/dashboard.py` | criar | primitivas (ANSI/sparkline/hbar/layout, colhidas do `main`) + 6 telas + `render_frame()` |
| `aurora_siger/operations/cli.py` | criar | runtime: thread de simulação + loop de input raw + `main(argv)`; entrypoint `aurora` |
| `fases/fase-3/aurora_core.py` | criar | wrapper fino → `aurora_siger.operations.cli:main` |
| `pyproject.toml` | modificar | console script `aurora = "aurora_siger.operations.cli:main"` |
| `tests/test_operations_*.py` | criar | pytest (SimSnapshot a fundo; telas + render via smoke; cli importável) |

---

## Task 1: `init_simulation(seed)` — state builder reusável

O CLI ao vivo precisa do `state` para chamar `step()` num loop e renderizá-lo. Hoje `run_simulation` monta o `state` internamente. Extraímos `init_simulation(seed)` (sem rodar o loop) e fazemos `run_simulation` usá-lo — refactor puro, comportamento idêntico.

**Files:**
- Modify: `aurora_siger/operations/simulator.py`
- Test: `tests/test_operations_simulator.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
# append to tests/test_operations_simulator.py
def test_init_simulation_builds_ready_state():
    from aurora_siger.operations.simulator import init_simulation, step
    state = init_simulation(seed=42)
    assert set(("climate", "battery", "history", "criticality_tree",
                "storm_state", "coldfront_state", "last_wind_24h", "rng")) <= set(state)
    assert state["history"]["total_generation_kw"] == []   # nothing stepped yet
    step(state)
    assert len(state["history"]["total_generation_kw"]) == 1


def test_run_simulation_still_matches_manual_stepping():
    from aurora_siger.operations.simulator import init_simulation, step
    _, _, h_run = run_simulation(seed=42, horizon=24)
    state = init_simulation(seed=42)
    for _ in range(24):
        step(state)
    assert state["history"] == h_run
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_simulator.py -k init_simulation -v`
Expected: FAIL with `ImportError: cannot import name 'init_simulation'`

- [ ] **Step 3: Extract `init_simulation` and have `run_simulation` use it**

In `aurora_siger/operations/simulator.py`, replace the `run_simulation` function with these two functions (note `_reset_modules()` now lives in `init_simulation`):

```python
def init_simulation(seed=42):
    """Builds a ready-to-step simulation state (does not run any step).

    Resets per-module runtime state so a fresh run never inherits a previous
    run's failures or modes (MODULES is module-level shared state). The live
    CLI dashboard and run_simulation both build their state through here.
    """
    rng = RandomLCG(seed)
    _reset_modules()
    climate, battery, history = initial_state()
    return {
        "climate": climate,
        "battery": battery,
        "history": history,
        "criticality_tree": build_criticality_tree(),
        "storm_state": StormState(),
        "coldfront_state": ColdFrontState(),
        "last_wind_24h": deque(maxlen=24),
        "rng": rng,
    }


def run_simulation(seed=42, horizon=TOTAL_STEPS):
    """Runs `horizon` hourly steps. Returns (climate, battery, history).

    seed=42 (default): deterministic. seed=None: entropy from the clock.
    """
    state = init_simulation(seed)
    for _ in range(horizon):
        step(state)
    return state["climate"], state["battery"], state["history"]
```

Keep `_reset_modules`, `step`, `_detail_generation`, `_energy_trend` unchanged.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_simulator.py -v`
Expected: PASS (the existing M1/M2 simulator tests + 2 new — determinism and bounds unchanged because `run_simulation` is the same sequence).

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/simulator.py tests/test_operations_simulator.py
git commit -m "refactor(fase-3): extrai init_simulation (state builder p/ dashboard ao vivo)"
```

---

## Task 2: `SimSnapshot` — adaptador sobre state/history

`SimSnapshot(state)` é o único ponto de acesso a dados do dashboard: lê valores "atuais" do `climate`/`battery`/última entrada do `history`, séries do `history`, a lista de módulos (com status/consumo derivados) e a árvore de criticidade. Sem o singleton `DataStorage`.

**Files:**
- Create: `aurora_siger/operations/simsnapshot.py`
- Test: `tests/test_operations_simsnapshot.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_simsnapshot.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_simsnapshot.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `aurora_siger/operations/simsnapshot.py`**

```python
"""SimSnapshot — read-only adapter over a live simulator state (Fase 3, §4).

Replaces the team `main` branch's DataStorage singleton. The dashboard reads
everything it draws through this thin façade, so the live front-end (cli.py
calling step() in a loop) and the headless notebook share one data-access
layer over the simulator's plain dicts.

`.get(key, default)` returns a single "current" value (live climate/battery
fields, or the latest entry of a recorded history series). `.history(key,
last_n)` returns a recent window of a series. `.modules()` returns the module
table with derived operational status and current consumption. The snapshot
never mutates state.
"""

from aurora_siger.operations.consumption import current_consumption_kw
from aurora_siger.operations.failures import is_operational

# Scalars read live from climate/battery (always present).
_LIVE = {
    "sol": lambda st: st["climate"]["sol"],
    "hour": lambda st: st["climate"]["hour"],
    "temperature_c": lambda st: st["climate"]["temperature_c"],
    "wind_ms": lambda st: st["climate"]["wind_ms"],
    "tau": lambda st: st["climate"]["tau"],
    "storm": lambda st: st["climate"]["storm"],
    "panel_factor": lambda st: st["climate"]["panel_factor"],
    "battery_kwh": lambda st: st["battery"]["current_charge_kwh"],
    "battery_max_kwh": lambda st: st["battery"]["max_capacity_kwh"],
    "battery_pct": lambda st: (
        st["battery"]["current_charge_kwh"] / st["battery"]["max_capacity_kwh"] * 100.0
    ),
    "tick": lambda st: len(st["history"]["total_generation_kw"]),
}

# "Current" scalars taken from the last entry of a recorded history series.
_LATEST = {
    "energy_level": "energy_level",
    "slope": "slope",
    "predicted_delta": "predicted_delta",
    "broken_count": "broken_count",
    "generation_kw": "total_generation_kw",
    "consumption_kw": "total_consumption_kw",
    "solar_kw": "solar_generation_kw",
    "wind_kw": "wind_generation_kw",
    "nuclear_kw": "nuclear_generation_kw",
}


class SimSnapshot:
    """Read-only view over a simulator `state` dict."""

    def __init__(self, state):
        self._state = state

    def get(self, key, default=None):
        st = self._state
        if key in _LIVE:
            return _LIVE[key](st)
        if key in _LATEST:
            series = st["history"][_LATEST[key]]
            return series[-1] if series else default
        return default

    def history(self, series_key, last_n=None):
        """Recent window of a history series (by its HISTORY_KEYS name)."""
        series = self._state["history"].get(series_key, [])
        if last_n is None:
            return list(series)
        return list(series)[-last_n:]

    def modules(self):
        """Module table with derived operational status and live consumption."""
        from aurora_siger.operations.modules import MODULES
        climate = self._state["climate"]
        rows = []
        for m in MODULES:
            active = is_operational(m)
            rows.append({
                "id": m["id"],
                "name": m["name"],
                "type": m["type"],
                "current_mode": m["current_mode"],
                "consumption_kw": current_consumption_kw(m, climate) if active else 0.0,
                "active": active,
                "broken": m.get("broken", False),
            })
        return rows

    def criticality_tree(self):
        """The live criticality tree (Vital → Sustenance → Expansion)."""
        return self._state["criticality_tree"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_simsnapshot.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/simsnapshot.py tests/test_operations_simsnapshot.py
git commit -m "feat(fase-3): SimSnapshot — adaptador de dados sobre o state (§4)"
```

---

## Task 3: `dashboard.py` — primitivas visuais (colhidas do `main`)

As primitivas são copiadas da branch `main` (`colonia_aurora/display/dashboard.py`, helpers puros) — a "colheita" da linguagem visual. Funções puras de formatação: testáveis sem terminal.

**Files:**
- Create: `aurora_siger/operations/dashboard.py`
- Test: `tests/test_operations_dashboard.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_dashboard.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_dashboard.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `aurora_siger/operations/dashboard.py` with the primitives**

```python
"""Live TUI dashboard for the Aurora Siger colony (Fase 3, §4).

The visual primitives (ANSI palette, sparkline, hbar, miniline, layout, screen
control) are harvested intact from the team `main` branch
(colonia_aurora/display/dashboard.py). The six screen renderers and the frame
composer (added in later tasks) are written fresh over a SimSnapshot, so they
read our simulator's data instead of the team's DataStorage singleton.
"""

import re
import sys

# --- ANSI palette / control (harvested from `main`) ---
ESC = "\033"
RESET = f"{ESC}[0m"
BOLD = f"{ESC}[1m"
DIM = f"{ESC}[2m"


def fg(r, g, b):
    return f"{ESC}[38;2;{r};{g};{b}m"


def bg(r, g, b):
    return f"{ESC}[48;2;{r};{g};{b}m"


AMBER = fg(245, 158, 11)
TEAL = fg(20, 184, 166)
RED = fg(239, 68, 68)
GREEN = fg(34, 197, 94)
BLUE = fg(96, 165, 250)
PURPLE = fg(167, 139, 250)
GRAY = fg(107, 128, 168)
DIM_C = fg(40, 55, 85)
WHITE = fg(210, 220, 255)
ORANGE = fg(249, 115, 22)
YELLOW = fg(234, 179, 8)

LEVEL_CLR = {
    "CRITICAL": RED, "LOW": ORANGE, "NOMINAL": YELLOW,
    "HIGH": GREEN, "SURPLUS": TEAL,
}

HLINE = "─"
BAR_F = "█"
BAR_E = "░"

# --- layout ---
TOTAL_W = 100
TOTAL_H = 30
CONTENT_H = TOTAL_H - 6
CONTENT_W = TOTAL_W - 2


def goto(r, c):
    return f"{ESC}[{r};{c}H"


def clr():
    return f"{ESC}[2J{ESC}[H"


def hide_cur():
    sys.stdout.write(f"{ESC}[?25l")
    sys.stdout.flush()


def show_cur():
    sys.stdout.write(f"{ESC}[?25h")
    sys.stdout.flush()


def alt_screen():
    sys.stdout.write(f"{ESC}[?1049h")
    sys.stdout.flush()


def norm_screen():
    sys.stdout.write(f"{ESC}[?1049l")
    sys.stdout.flush()


def at(r, c, txt):
    return goto(r, c) + txt


def strip_ansi(text):
    return re.sub(r"\033\[[^m]*m", "", text)


def padto(text, width):
    plain_len = len(strip_ansi(text))
    diff = width - plain_len
    return text + " " * diff if diff > 0 else text


def hbar(val, mx, w, color):
    filled = int((val / mx) * w) if mx > 0 else 0
    filled = max(0, min(w, filled))
    return color + BAR_F * filled + DIM_C + BAR_E * (w - filled) + RESET


def sparkline(vals, w, h, vmin=None, vmax=None):
    if not vals:
        return [DIM_C + "·" * w + RESET] * h
    if vmin is None:
        vmin = min(vals)
    if vmax is None:
        vmax = max(vals)
    vr = (vmax - vmin) or 1
    data = [int(((v - vmin) / vr) * (h - 1)) for v in vals][-w:]
    while len(data) < w:
        data.insert(0, 0)
    rows = []
    for ri in range(h - 1, -1, -1):
        row = ""
        for v in data:
            ratio = ri / (h - 1) if h > 1 else 0
            if v >= ri:
                c = GREEN if ratio > 0.65 else (YELLOW if ratio > 0.35 else RED)
                row += c + BAR_F + RESET
            else:
                row += DIM_C + "·" + RESET
        rows.append(row)
    return rows


def miniline(vals, w, h):
    if not vals:
        return [" " * w] * h
    vmin = min(vals)
    vmax = max(vals)
    vr = (vmax - vmin) or 1
    data = [int(((v - vmin) / vr) * (h - 1)) for v in vals][-w:]
    while len(data) < w:
        data.insert(0, 0)
    rows = []
    for ri in range(h - 1, -1, -1):
        row = ""
        for i, v in enumerate(data):
            prev = data[i - 1] if i > 0 else v
            if v == ri:
                row += TEAL + "─" + RESET
            elif v > ri > prev or prev > ri > v:
                row += TEAL + "│" + RESET
            else:
                row += DIM_C + " " + RESET
        rows.append(row)
    return rows
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_dashboard.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/dashboard.py tests/test_operations_dashboard.py
git commit -m "feat(fase-3): primitivas visuais do dashboard (colhidas do main)"
```

---

## Task 4: Telas 1–3 — Overview, Energia, Sensores

Telas finas que recebem `(snapshot, w, h)` e devolvem uma lista de linhas (strings com ANSI). Puras e testáveis. Leem só do `SimSnapshot`.

**Files:**
- Modify: `aurora_siger/operations/dashboard.py` (append)
- Test: `tests/test_operations_dashboard.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
# append to tests/test_operations_dashboard.py
from aurora_siger.operations.dashboard import (
    screen_overview, screen_energia, screen_sensores,
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
```

Note: `CONTENT_W`/`CONTENT_H` are already imported transitively via `from aurora_siger.operations.dashboard import *`? No — import them explicitly. Add to the test file's imports: `from aurora_siger.operations.dashboard import CONTENT_W, CONTENT_H`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_dashboard.py -k "overview or energia or sensores or fresh_state" -v`
Expected: FAIL with `ImportError: cannot import name 'screen_overview'`

- [ ] **Step 3: Append the three screens to `aurora_siger/operations/dashboard.py`**

```python


def _bar_line(label, value, unit, val, mx, color, w):
    """A labelled horizontal bar: 'Label  ███░░░  value unit'."""
    bar = hbar(val, mx, max(10, w - 30), color)
    return f"  {GRAY}{label:<14}{RESET}{bar} {color}{value}{unit}{RESET}"


def screen_overview(snap, w, h):
    level = snap.get("energy_level", "NOMINAL")
    lc = LEVEL_CLR.get(level, WHITE)
    pct = snap.get("battery_pct", 0.0)
    gen = snap.get("generation_kw", 0.0)
    con = snap.get("consumption_kw", 0.0)
    pred = snap.get("predicted_delta", 0.0)
    lines = []
    lines.append(f"  {AMBER}Visão Geral{RESET}   {GRAY}Nível de energia:{RESET} {lc}{BOLD}{level}{RESET}")
    lines.append(DIM_C + HLINE * w + RESET)
    lines.append(_bar_line("Bateria", f"{pct:.0f}", "%", pct, 100.0, lc, w))
    spark = sparkline(snap.history("battery_charge_kwh", 48), w=48, h=4)
    for row in spark:
        lines.append("    " + row)
    lines.append("")
    lines.append(f"  {GRAY}Geração:{GREEN}{gen:7.1f} kW{RESET}   "
                 f"{GRAY}Consumo:{RED}{con:7.1f} kW{RESET}   "
                 f"{GRAY}Saldo:{lc}{gen - con:+7.1f} kW{RESET}")
    lines.append(f"  {GRAY}Delta previsto (OLS):{RESET} {lc}{pred:+.2f} kW{RESET}")
    return lines


def screen_energia(snap, w, h):
    gen = snap.get("generation_kw", 0.0)
    solar = snap.get("solar_kw", 0.0)
    wind = snap.get("wind_kw", 0.0)
    nuclear = snap.get("nuclear_kw", 0.0)
    con = snap.get("consumption_kw", 0.0)
    slope = snap.get("slope", 0.0)
    mx = max(gen, con, 1.0)
    lines = []
    lines.append(f"  {AMBER}Energia{RESET}")
    lines.append(DIM_C + HLINE * w + RESET)
    lines.append(_bar_line("Solar", f"{solar:.1f}", " kW", solar, mx, YELLOW, w))
    lines.append(_bar_line("Eólica", f"{wind:.1f}", " kW", wind, mx, TEAL, w))
    lines.append(_bar_line("Nuclear", f"{nuclear:.1f}", " kW", nuclear, mx, PURPLE, w))
    lines.append(_bar_line("Consumo", f"{con:.1f}", " kW", con, mx, RED, w))
    lines.append("")
    lines.append(f"  {GRAY}Geração total:{GREEN} {gen:.1f} kW{RESET}   "
                 f"{GRAY}Tendência (slope OLS):{RESET} {slope:+.3f} kW/h")
    spark = sparkline(snap.history("total_generation_kw", 48), w=48, h=4)
    for row in spark:
        lines.append("    " + row)
    return lines


def screen_sensores(snap, w, h):
    temp = snap.get("temperature_c", 0.0)
    wind = snap.get("wind_ms", 0.0)
    tau = snap.get("tau", 0.0)
    storm = snap.get("storm", "clear")
    panel = snap.get("panel_factor", 1.0)
    lines = []
    lines.append(f"  {AMBER}Sensores e Clima{RESET}   {GRAY}tempestade:{RESET} {storm}")
    lines.append(DIM_C + HLINE * w + RESET)
    lines.append(f"  {GRAY}Temperatura:{RESET} {BLUE}{temp:7.1f} °C{RESET}")
    lines.append(f"  {GRAY}Vento:{RESET}       {TEAL}{wind:7.1f} m/s{RESET}")
    lines.append(f"  {GRAY}tau (opacidade):{RESET} {WHITE}{tau:5.2f}{RESET}")
    lines.append(f"  {GRAY}Fator de painel:{RESET} {hbar(panel, 1.0, 30, AMBER)} {panel:.2f}")
    lines.append("")
    lines.append(f"  {GRAY}Vento (24 h){RESET}")
    for row in miniline(snap.history("wind_ms", 48), w=48, h=4):
        lines.append("    " + row)
    return lines
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_dashboard.py -v`
Expected: PASS (11 passed — 7 primitives + 4 new)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/dashboard.py tests/test_operations_dashboard.py
git commit -m "feat(fase-3): telas Overview/Energia/Sensores do dashboard"
```

---

## Task 5: Telas 4–6 — Módulos, Eventos, Hierarquia (item 1.1 ao vivo)

A aba Hierarquia substitui a Crew do `main`: percorre a árvore de criticidade e renderiza Vital → Sustento → Expansão com os módulos e seus modos — o item 1.1 visualizado ao vivo.

**Files:**
- Modify: `aurora_siger/operations/dashboard.py` (append)
- Test: `tests/test_operations_dashboard.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
# append to tests/test_operations_dashboard.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_dashboard.py -k "modulos or eventos or hierarquia or part2" -v`
Expected: FAIL with `ImportError: cannot import name 'screen_modulos'`

- [ ] **Step 3: Append the three screens to `aurora_siger/operations/dashboard.py`**

```python


_MODE_CLR = {"surplus": TEAL, "adequate": GREEN, "minimum": YELLOW, "off": DIM_C}


def screen_modulos(snap, w, h):
    mods = snap.modules()
    active = sum(1 for m in mods if m["active"])
    lines = []
    lines.append(f"  {AMBER}Módulos — {active} ativos / {len(mods)} total{RESET}")
    lines.append(DIM_C + HLINE * w + RESET)
    lines.append(f"  {GRAY}{'ID':<4}{'Nome':<22}{'Tipo':<18}{'Modo':<10}{'Consumo':<10}{'Status':<10}{RESET}")
    lines.append(DIM_C + HLINE * w + RESET)
    for m in mods:
        if m["broken"]:
            sc, dot, st = RED, "✕", "quebrado"
        elif not m["active"]:
            sc, dot, st = DIM_C, "○", "offline"
        else:
            sc, dot, st = GREEN, "●", "online"
        mc = _MODE_CLR.get(m["current_mode"], WHITE)
        lines.append(
            f"  {AMBER}{m['id']:<4}{RESET}{sc}{dot} {m['name']:<20}{RESET}"
            f"{GRAY}{m['type']:<18}{RESET}"
            f"{mc}{m['current_mode']:<10}{RESET}"
            f"{sc}{m['consumption_kw']:<10.1f}{RESET}"
            f"{sc}{st:<10}{RESET}"
        )
        if len(lines) >= h - 1:
            break
    return lines


def screen_eventos(snap, w, h):
    storm = snap.get("storm", "clear")
    temp = snap.get("temperature_c", 0.0)
    broken = snap.get("broken_count", 0)
    lines = []
    lines.append(f"  {AMBER}Eventos{RESET}")
    lines.append(DIM_C + HLINE * w + RESET)
    storm_clr = RED if storm in ("moderate", "severe") else (YELLOW if storm == "light" else GREEN)
    lines.append(f"  {GRAY}Tempestade de poeira:{RESET} {storm_clr}{storm}{RESET}")
    cold = temp < -86.0  # cold-front-level deep cold (thermal heating kicks in)
    lines.append(f"  {GRAY}Frente fria:{RESET} "
                 f"{(BLUE + 'ATIVA' + RESET) if cold else (DIM_C + 'inativa' + RESET)}"
                 f"   {GRAY}(temp {temp:.0f} °C){RESET}")
    bc = RED if broken else GREEN
    lines.append(f"  {GRAY}Falhas de equipamento:{RESET} {bc}{broken} módulo(s) em reparo{RESET}")
    lines.append("")
    lines.append(f"  {GRAY}Módulos quebrados (48 h){RESET}")
    for row in sparkline([float(x) for x in snap.history("broken_count", 48)], w=48, h=3):
        lines.append("    " + row)
    return lines


def screen_hierarquia(snap, w, h):
    """Tab 6: the criticality tree live — item 1.1 visualized (replaces Crew)."""
    root = snap.criticality_tree()
    lines = []
    lines.append(f"  {AMBER}Hierarquia de Criticidade{RESET}   {GRAY}(item 1.1 ao vivo){RESET}")
    lines.append(DIM_C + HLINE * w + RESET)
    for level in root.children:
        leaves = level.leaves()
        on = sum(1 for m in leaves if m["current_mode"] != "off"
                 and not m.get("broken", False))
        lines.append(f"  {TEAL}{BOLD}{level.name}{RESET} {GRAY}({on}/{len(leaves)} operando){RESET}")
        for m in sorted(leaves, key=lambda x: x["id"]):
            mode = m["current_mode"]
            if m.get("broken", False):
                mc, tag = RED, "✕ quebrado"
            else:
                mc, tag = _MODE_CLR.get(mode, WHITE), mode
            lines.append(f"      {mc}•{RESET} {WHITE}{m['name']:<22}{RESET}{mc}{tag}{RESET}")
            if len(lines) >= h - 1:
                return lines
    return lines
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_dashboard.py -v`
Expected: PASS (15 passed — 11 + 4 new)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/dashboard.py tests/test_operations_dashboard.py
git commit -m "feat(fase-3): telas Módulos/Eventos/Hierarquia (item 1.1 ao vivo)"
```

---

## Task 6: `render_frame()` — composição do quadro + abas

Compõe um quadro completo (header + barra de abas + tela ativa + rodapé) numa única string posicionada com ANSI. Puro: recebe `(snapshot, tab_idx)` e devolve a string do buffer. É o "1 smoke render" do spec §7.

**Files:**
- Modify: `aurora_siger/operations/dashboard.py` (append)
- Test: `tests/test_operations_dashboard.py` (append)

- [ ] **Step 1: Write the failing test (append)**

```python
# append to tests/test_operations_dashboard.py
from aurora_siger.operations.dashboard import render_frame, TABS


def test_tabs_are_six_with_hierarquia():
    names = [name for name, _ in TABS]
    assert len(TABS) == 6
    assert "Hierarquia" in names and "Crew" not in names


def test_render_frame_returns_string_with_active_tab_content():
    snap = _snap()
    frame = render_frame(snap, tab_idx=0)        # Overview
    assert isinstance(frame, str) and frame
    assert "Bateria" in strip_ansi(frame)
    # all tab names appear in the tab bar
    for name, _ in TABS:
        assert name in strip_ansi(frame)


def test_render_frame_each_tab_smoke():
    snap = _snap()
    for idx in range(len(TABS)):
        frame = render_frame(snap, tab_idx=idx)
        assert isinstance(frame, str) and len(frame) > 0


def test_render_frame_clamps_tab_index():
    snap = _snap()
    # out-of-range index must not raise (defensive)
    assert isinstance(render_frame(snap, tab_idx=99), str)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_dashboard.py -k "render_frame or tabs_are_six" -v`
Expected: FAIL with `ImportError: cannot import name 'render_frame'`

- [ ] **Step 3: Append the frame composer to `aurora_siger/operations/dashboard.py`**

```python


TABS = [
    ("Overview", "1", screen_overview),
    ("Energia", "2", screen_energia),
    ("Módulos", "3", screen_modulos),
    ("Sensores", "4", screen_sensores),
    ("Eventos", "5", screen_eventos),
    ("Hierarquia", "6", screen_hierarquia),
]


def _tab_bar(active_idx):
    cells = []
    for i, (name, key, _) in enumerate(TABS):
        if i == active_idx:
            cells.append(f"{BOLD}{AMBER}[{key}:{name}]{RESET}")
        else:
            cells.append(f"{GRAY}{key}:{name}{RESET}")
    return "  ".join(cells)


def render_frame(snap, tab_idx):
    """Builds the full dashboard frame as one positioned ANSI string.

    Pure: given a SimSnapshot and the active tab index, returns the buffer the
    runtime would write. Out-of-range tab indices are clamped defensively.
    """
    tab_idx = tab_idx % len(TABS) if TABS else 0
    name, _, screen = TABS[tab_idx]
    level = snap.get("energy_level", "NOMINAL")
    lc = LEVEL_CLR.get(level, WHITE)
    sol = snap.get("sol", 0)
    hour = snap.get("hour", 0)
    tick = snap.get("tick", 0)

    buf = []
    buf.append(clr())
    buf.append(at(ROW := 1, 2,
                  f"{BOLD}{AMBER}AURORA SIGER{RESET}  {GRAY}colônia operando{RESET}   "
                  f"{GRAY}sol {sol}  {hour:02d}:00   passo {tick}{RESET}   "
                  f"{GRAY}energia:{RESET} {lc}{level}{RESET}"))
    buf.append(at(2, 2, _tab_bar(tab_idx)))
    buf.append(at(3, 2, DIM_C + HLINE * CONTENT_W + RESET))

    body = screen(snap, CONTENT_W, CONTENT_H)
    for i, line in enumerate(body[:CONTENT_H]):
        buf.append(at(5 + i, 1, line))

    footer_row = 5 + CONTENT_H + 1
    buf.append(at(footer_row, 2,
                  f"{GRAY}←/→ ou 1–6: abas   p: pausa   q: sair{RESET}"))
    return "".join(buf)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_dashboard.py -v`
Expected: PASS (19 passed — 15 + 4 new)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/dashboard.py tests/test_operations_dashboard.py
git commit -m "feat(fase-3): composição do quadro + navegação de 6 abas"
```

---

## Task 7: `cli.py` — runtime ao vivo + entrypoint `aurora`

O runtime: monta o `state`, roda `step()` num thread daemon (pacing), e renderiza `render_frame` no thread principal lendo teclas em modo raw. Inclui um modo headless `--frames N` (sem terminal raw) para fumaça/automação. Registra o console script `aurora` e o wrapper de fase.

**Files:**
- Create: `aurora_siger/operations/cli.py`
- Create: `fases/fase-3/aurora_core.py`
- Modify: `pyproject.toml`
- Test: `tests/test_operations_cli.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_cli.py
import subprocess
import sys

from aurora_siger.operations import cli


def test_cli_module_exposes_main():
    assert hasattr(cli, "main") and callable(cli.main)


def test_headless_frames_mode_runs_without_a_terminal():
    # --frames N steps the sim N times and prints the final frame to stdout,
    # never touching raw-terminal mode — safe under pytest / CI.
    out = subprocess.run(
        [sys.executable, "-m", "aurora_siger.operations.cli",
         "--seed", "42", "--frames", "10"],
        capture_output=True, text=True, timeout=30,
    )
    assert out.returncode == 0
    assert "AURORA SIGER" in out.stdout


def test_headless_is_deterministic_per_seed():
    def run(seed):
        return subprocess.run(
            [sys.executable, "-m", "aurora_siger.operations.cli",
             "--seed", str(seed), "--frames", "20", "--plain"],
            capture_output=True, text=True, timeout=30,
        ).stdout
    assert run(42) == run(42)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.operations.cli'`

- [ ] **Step 3: Create `aurora_siger/operations/cli.py`**

```python
"""`aurora` — live TUI front-end for the colony simulation (Fase 3).

Mirrors the Fase 2 `mgpeb` pattern: a thin runtime over the package logic. The
simulation runs in a daemon thread (visual pacing only — content stays
deterministic per seed); the main thread renders the dashboard frame and reads
keys in raw mode. A headless `--frames N` mode steps the sim and prints one
frame without touching the terminal, for smoke tests and CI.
"""

import argparse
import sys
import threading
import time

from aurora_siger.operations.dashboard import (
    render_frame, strip_ansi, TABS, hide_cur, show_cur, alt_screen, norm_screen,
)
from aurora_siger.operations.simulator import init_simulation, step, TOTAL_STEPS
from aurora_siger.operations.simsnapshot import SimSnapshot


def _run_headless(seed, frames, plain):
    """Steps `frames` times and prints the final Overview frame. No raw TTY."""
    state = init_simulation(seed)
    for _ in range(min(frames, TOTAL_STEPS)):
        step(state)
    frame = render_frame(SimSnapshot(state), tab_idx=0)
    sys.stdout.write(strip_ansi(frame) + "\n" if plain else frame + "\n")
    return 0


def _run_live(seed, tick_seconds):
    """Live loop: sim in a daemon thread, raw-mode keyboard nav in the main
    thread. Falls back to headless if stdin is not a TTY."""
    import select
    import termios
    import tty

    if not sys.stdin.isatty():
        return _run_headless(seed, TOTAL_STEPS, plain=False)

    state = init_simulation(seed)
    snap = SimSnapshot(state)
    stop = threading.Event()
    pause = threading.Event()

    def sim_loop():
        steps = 0
        while not stop.is_set() and steps < TOTAL_STEPS:
            if not pause.is_set():
                step(state)
                steps += 1
            stop.wait(tick_seconds)

    worker = threading.Thread(target=sim_loop, daemon=True)
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tab_idx = 0
    try:
        alt_screen()
        hide_cur()
        tty.setraw(fd)
        worker.start()
        while not stop.is_set():
            sys.stdout.write(render_frame(snap, tab_idx))
            sys.stdout.flush()
            if select.select([fd], [], [], 0.1)[0]:
                ch = sys.stdin.read(1)
                if ch in ("q", "\x03"):       # q / Ctrl-C
                    stop.set()
                elif ch == "p":
                    (pause.clear if pause.is_set() else pause.set)()
                elif ch in "123456":
                    tab_idx = int(ch) - 1
                elif ch == "\x1b":            # arrow keys: ESC [ C / D
                    seq = sys.stdin.read(2)
                    if seq == "[C":
                        tab_idx = (tab_idx + 1) % len(TABS)
                    elif seq == "[D":
                        tab_idx = (tab_idx - 1) % len(TABS)
    finally:
        stop.set()
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        show_cur()
        norm_screen()
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="aurora", description="Aurora Siger live dashboard")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (deterministic)")
    parser.add_argument("--tick", type=float, default=0.4, help="seconds per simulated hour (live)")
    parser.add_argument("--frames", type=int, default=None,
                        help="headless: step N times, print one frame, exit")
    parser.add_argument("--plain", action="store_true", help="headless: strip ANSI (for diffing)")
    args = parser.parse_args(argv)
    if args.frames is not None:
        return _run_headless(args.seed, args.frames, args.plain)
    return _run_live(args.seed, args.tick)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Create `fases/fase-3/aurora_core.py` (thin wrapper)**

```python
#!/usr/bin/env python3
"""Entry point for the Fase 3 live dashboard — thin wrapper over the package.

Preserves `python3 fases/fase-3/aurora_core.py` while the logic lives in
`aurora_siger.operations.cli` (mirrors the Fase 2 `mgpeb.py` wrapper).
"""

import sys

from aurora_siger.operations.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 5: Register the console script in `pyproject.toml`**

Find the `[project.scripts]` table (it already has `mgpeb = "aurora_siger.landing.cli:main"`). Add the `aurora` line:

```toml
[project.scripts]
mgpeb = "aurora_siger.landing.cli:main"
aurora = "aurora_siger.operations.cli:main"
```

(If there is no `[project.scripts]` table, add it. Do not change other tables.)

- [ ] **Step 6: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_cli.py -v`
Expected: PASS (3 passed)

- [ ] **Step 7: Commit**

```bash
git add aurora_siger/operations/cli.py fases/fase-3/aurora_core.py pyproject.toml tests/test_operations_cli.py
git commit -m "feat(fase-3): CLI aurora — dashboard ao vivo + modo headless"
```

---

## Task 8: Verificação do marco M3

- [ ] **Step 1: Run the full operations suite**

Run: `python3 -m pytest tests/test_operations_*.py -v`
Expected: all green. M1+M2 (~98) + M3 (simulator +2, simsnapshot 7, dashboard 19, cli 3) ≈ 129 tests.

- [ ] **Step 2: Smoke the headless CLI**

Run:
```bash
python3 -m aurora_siger.operations.cli --seed 42 --frames 30
```
Expected: prints a full ANSI frame whose header reads "AURORA SIGER" and tab bar shows the six tabs including Hierarquia.

- [ ] **Step 3: Confirm determinism of the headless render**

Run:
```bash
diff <(python3 -m aurora_siger.operations.cli --seed 42 --frames 30 --plain) \
     <(python3 -m aurora_siger.operations.cli --seed 42 --frames 30 --plain) && echo IDENTICAL
```
Expected: `IDENTICAL`.

- [ ] **Step 4: Confirm the whole repo suite still passes**

Run: `python3 -m pytest`
Expected: the 147 fase-1/2 tests + all operations tests, all green.

> Nota: o modo ao vivo (`aurora` sem `--frames`) precisa de um terminal interativo (raw mode); sob pytest/CI ele detecta `stdin` não-tty e cai no headless. A verificação manual do modo ao vivo é opcional e feita pelo usuário no terminal.

---

## Self-Review (preenchido pelo autor do plano)

**Cobertura do spec (M3 scope, §4):**
- SimSnapshot `.get/.history` sobre state/history (sem singleton) → Task 2 ✓
- Primitivas ANSI/sparkline/layout colhidas do `main` → Task 3 ✓
- 6 abas: Overview/Energia (main), Sensores/Clima (iuri), Módulos (iuri+falhas), Eventos (tempestade+frente fria+falhas), Hierarquia (item 1.1, substitui Crew) → Tasks 4–6 ✓
- Notebook headless e dashboard ao vivo como dois front-ends sobre o mesmo núcleo; thread só no front-end para pacing → Tasks 1 (init_simulation compartilhado) + 7 (thread daemon) ✓
- console script `aurora` + wrapper de fase → Task 7 ✓
- **Fora do M3 (vai para M4):** notebook.ipynb, relatorio.md/pdf, ensaio reativo-a-preditivo, README/badge, bump 0.3.0. Rastreado.

**Riscos tratados:**
- Port do dashboard (§9.2): em vez de emular as chaves do `main`, o SimSnapshot expõe as NOSSAS chaves e as telas são escritas finas sobre ele — sem campos faltantes; os que o `main` tinha e não temos (crew) viram a aba Hierarquia.
- Determinismo: o thread só faz pacing; `--frames`/`--plain` permite diffar dois runs seeded (Task 8 step 3). `init_simulation` reseta os módulos.
- Testabilidade (§7): SimSnapshot testado a fundo; telas via "retorna linhas + contém rótulos"; render via smoke de string; runtime raw NÃO é unit-testado (cai em headless sob não-tty).

**Placeholder scan:** sem TBD/TODO; todo passo que altera código mostra o código completo. ✓

**Consistência de tipos/assinaturas:** telas `screen_*(snap, w, h) -> list[str]`; `render_frame(snap, tab_idx) -> str`; `TABS` é lista de `(name, key, screen_fn)`; `SimSnapshot(state)` com `.get(key, default)`, `.history(series_key, last_n)`, `.modules() -> list[dict]`, `.criticality_tree() -> Node`. `init_simulation(seed) -> state`; `step(state)`; `cli.main(argv) -> int`. As telas usam só chaves que o SimSnapshot expõe (battery_pct, energy_level, generation_kw, solar_kw/wind_kw/nuclear_kw, consumption_kw, slope, predicted_delta, temperature_c, wind_ms, tau, storm, panel_factor, broken_count, sol, hour, tick) e séries do history (battery_charge_kwh, total_generation_kw, wind_ms, broken_count). ✓
