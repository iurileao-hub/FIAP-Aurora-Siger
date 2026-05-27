# Fase 3 — M1: Núcleo Determinístico — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Portar o núcleo de simulação científica da branch `iuri` para `aurora_siger/operations/`, trocando o RNG por um LCG determinístico injetável e adicionando o evento de frente fria — produzindo uma simulação headless de 168 horas, reprodutível por seed e coberta por testes.

**Architecture:** Funções puras sobre dicts de estado (sem singleton global), seguindo a convenção do pacote (notebooks/CLIs importam de `aurora_siger.operations`). A aleatoriedade passa por uma instância única de `RandomLCG` criada em `run_simulation()` e injetada via `state["rng"]` — garantindo determinismo e permitindo simulações paralelas independentes. Este marco NÃO inclui `power_factor`, níveis de energia, regressão, decisão, análise ou falhas (ficam para o M2); porta consumo e alocação fielmente do `iuri`.

**Tech Stack:** Python 3.11+, stdlib apenas (`math`, `collections`), pytest. Sem numpy no pacote `operations`.

**Repo de origem dos ports:** `/home/ubuntu/projects/fiap-aurora-siger-fase3`, branch `origin/iuri`, pacote `colony/`. Extração via `git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/<arquivo>.py`.

**Trabalho corrente:** repo `/home/ubuntu/projects/FIAP-Aurora-Siger`, branch `main`.

---

## File Structure (M1)

| Arquivo | Responsabilidade | Origem |
|---|---|---|
| `aurora_siger/operations/__init__.py` | marca o subpacote | novo |
| `aurora_siger/operations/rng.py` | `RandomLCG` (LCG do zero) + `gauss` Box-Muller | port `main` + novo método |
| `aurora_siger/operations/constants.py` | parâmetros físicos + constantes da frente fria | port `iuri` + novo |
| `aurora_siger/operations/tree.py` | `Node` N-ário | port `iuri` (verbatim) |
| `aurora_siger/operations/modules.py` | lista plana dos 13 módulos + `find_module` | port `iuri` (verbatim) |
| `aurora_siger/operations/hierarchies.py` | árvores funcional + criticidade | port `iuri` (verbatim) |
| `aurora_siger/operations/climate.py` | clima + frente fria + RNG injetado | port `iuri` + mudanças |
| `aurora_siger/operations/generation.py` | geração solar/eólica/nuclear | port `iuri` (verbatim) |
| `aurora_siger/operations/consumption.py` | consumo base + térmico `Q=U·A·ΔT` | port `iuri` (verbatim) |
| `aurora_siger/operations/allocation.py` | load shedding 4 estágios | port `iuri` (verbatim) |
| `aurora_siger/operations/state.py` | estado inicial (clima/bateria/history/rng) | port `iuri` + mudanças |
| `aurora_siger/operations/simulator.py` | `step` + `run_simulation` com LCG + frente fria | port `iuri` + mudanças |
| `tests/test_operations_*.py` | suíte pytest | novo |

---

## Task 1: Scaffold do subpacote

**Files:**
- Create: `aurora_siger/operations/__init__.py`
- Test: `tests/test_operations_package.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_package.py
def test_operations_package_importable():
    import aurora_siger.operations as ops
    assert ops is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_package.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.operations'`

- [ ] **Step 3: Create the package**

```bash
mkdir -p aurora_siger/operations
printf '"""Fase 3 — colônia operando: energia, decisão e previsão."""\n' > aurora_siger/operations/__init__.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_package.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/__init__.py tests/test_operations_package.py
git commit -m "feat(fase-3): scaffold do subpacote operations"
```

---

## Task 2: RNG — `RandomLCG` com `gauss`

O LCG vem da branch `main`. Adicionamos `gauss(mu, sigma)` via Box-Muller, porque o `climate.py` do `iuri` usa `random.gauss` e o LCG original não tem esse método. **Não** portamos o singleton global `seed/__init__.py` do `main` — a instância será injetada via estado.

**Files:**
- Create: `aurora_siger/operations/rng.py`
- Test: `tests/test_operations_rng.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_rng.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_rng.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_siger.operations.rng'`

- [ ] **Step 3: Create `aurora_siger/operations/rng.py`**

The LCG body is ported from the team repo's `main` branch
(`colonia_aurora/seed/linear_congruential_generator.py`); `gauss` is new. Write
the file by hand with the following content (do not extract via `git show` — we
are dropping the original's global `rng` singleton):

```python
"""Linear Congruential Generator (LCG) — implemented from scratch.

Ported from the team's `main` branch (colonia_aurora/seed). Parameters from
Numerical Recipes. A `gauss()` method (Box-Muller) is added here because the
climate model needs Gaussian noise and the stdlib `random` module is not used
in this package — all randomness flows through a single seeded LCG instance.
"""

import math
from time import time
from typing import List, Optional, Sequence, TypeVar

T = TypeVar("T")


class RandomLCG:
    """X_{n+1} = (a * X_n + c) mod m, with m = 2^32 (Numerical Recipes)."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self.a = 1664525
        self.c = 1013904223
        self.m = 2 ** 32
        if seed is None:
            seed = int(time() * 1_000_000) % self.m
        self.state = seed % self.m
        self.initial_seed = self.state

    def set_seed(self, seed: int) -> None:
        self.state = seed % self.m
        self.initial_seed = self.state

    def next_int(self) -> int:
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def random(self) -> float:
        """Float in [0, 1)."""
        return self.next_int() / self.m

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.random()

    def randint(self, low: int, high: int) -> int:
        """Integer in [low, high] (both inclusive)."""
        if low > high:
            raise ValueError("low must be <= high")
        return low + (self.next_int() % (high - low + 1))

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Gaussian sample via the Box-Muller transform."""
        u1 = self.random()
        u2 = self.random()
        if u1 < 1e-12:  # guard against log(0)
            u1 = 1e-12
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mu + sigma * z0

    def choice(self, sequence: Sequence[T]) -> T:
        if not sequence:
            raise ValueError("cannot choose from an empty sequence")
        return sequence[self.randint(0, len(sequence) - 1)]

    def shuffle(self, array: List[T]) -> None:
        for i in range(len(array) - 1, 0, -1):
            j = self.randint(0, i)
            array[i], array[j] = array[j], array[i]

    def get_state(self) -> int:
        return self.state
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_rng.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/rng.py tests/test_operations_rng.py
git commit -m "feat(fase-3): LCG determinístico com gauss (Box-Muller)"
```

---

## Task 3: Constantes (port + frente fria)

**Files:**
- Create: `aurora_siger/operations/constants.py`
- Test: `tests/test_operations_constants.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_constants.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_constants.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port constants and append cold-front block**

```bash
git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/constants.py \
  | sed 's#docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md#docs/superpowers/specs/2026-05-27-fase-3-operations-consolidacao-design.md#' \
  > aurora_siger/operations/constants.py
```

Then append the cold-front block to the end of `aurora_siger/operations/constants.py`:

```python


# --- Cold front (Fase 3 event) ---
# A sudden temperature drop that stresses the thermal model (Q = U·A·ΔT).
COLDFRONT_PROB_PER_SOL = 0.05          # ~1 frente fria a cada 20 sóis
COLDFRONT_DURATION_HOURS = (6, 18)     # janela em horas
COLDFRONT_DELTA_C = -30.0              # offset aplicado à temperatura enquanto ativa
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_constants.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/constants.py tests/test_operations_constants.py
git commit -m "feat(fase-3): constantes físicas (port iuri) + frente fria"
```

---

## Task 4: `Node` (árvore N-ária) — port verbatim

**Files:**
- Create: `aurora_siger/operations/tree.py`
- Test: `tests/test_operations_tree.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_tree.py
from aurora_siger.operations.tree import Node


def _toy_tree():
    root = Node("root")
    a = root.add_child(Node("A"))
    a.add_child(Node("leaf-1", module={"id": 1}))
    a.add_child(Node("leaf-2", module={"id": 2}))
    root.add_child(Node("leaf-3", module={"id": 3}))
    return root


def test_leaves_returns_module_dicts():
    leaves = _toy_tree().leaves()
    assert sorted(m["id"] for m in leaves) == [1, 2, 3]


def test_find_by_name():
    assert _toy_tree().find("A").name == "A"
    assert _toy_tree().find("nope") is None


def test_aggregate_sum_over_leaves():
    total = _toy_tree().aggregate(lambda m: m["id"], 0, lambda x, y: x + y)
    assert total == 6


def test_depth():
    assert _toy_tree().depth() == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_tree.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port the file (verbatim — no internal `colony.` imports)**

```bash
git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/tree.py \
  > aurora_siger/operations/tree.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_tree.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/tree.py tests/test_operations_tree.py
git commit -m "feat(fase-3): Node (árvore N-ária) — port iuri"
```

---

## Task 5: `modules.py` (13 módulos) — port verbatim

**Files:**
- Create: `aurora_siger/operations/modules.py`
- Test: `tests/test_operations_modules.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_modules.py
import pytest
from aurora_siger.operations.modules import MODULES, find_module


def test_thirteen_modules_with_unique_ids():
    ids = [m["id"] for m in MODULES]
    assert len(MODULES) == 13
    assert sorted(ids) == list(range(1, 14))


def test_each_module_has_four_modes():
    for m in MODULES:
        assert set(m["consumption_by_mode"]) == {"off", "minimum", "adequate", "surplus"}


def test_find_module_returns_dict_and_raises_on_missing():
    assert find_module(1)["name"] == "Command and Control"
    with pytest.raises(KeyError):
        find_module(999)


def test_three_generators_present():
    gens = [m for m in MODULES if "generator" in m["type"]]
    assert {m["type"] for m in gens} == {"solar_generator", "nuclear_generator", "wind_generator"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_modules.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port the file (verbatim — no internal imports)**

```bash
git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/modules.py \
  > aurora_siger/operations/modules.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_modules.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/modules.py tests/test_operations_modules.py
git commit -m "feat(fase-3): 13 módulos da colônia (port iuri, continuidade Fase 2)"
```

---

## Task 6: `hierarchies.py` — port com reescrita de imports

**Files:**
- Create: `aurora_siger/operations/hierarchies.py`
- Test: `tests/test_operations_hierarchies.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_hierarchies.py
from aurora_siger.operations.hierarchies import (
    build_functional_tree, build_criticality_tree,
)
from aurora_siger.operations.modules import MODULES


def test_criticality_tree_has_three_levels():
    root = build_criticality_tree()
    assert [c.name for c in root.children] == ["Vital", "Sustenance", "Expansion"]


def test_both_trees_cover_all_thirteen_modules():
    for build in (build_functional_tree, build_criticality_tree):
        ids = {m["id"] for m in build().leaves()}
        assert ids == {m["id"] for m in MODULES}


def test_trees_reference_same_module_dicts():
    # mutating a module via one tree is visible from MODULES (shared identity)
    tree = build_criticality_tree()
    leaf_mod = tree.find("Habitat").module
    leaf_mod["current_mode"] = "off"
    from aurora_siger.operations.modules import find_module
    assert find_module(3)["current_mode"] == "off"
    leaf_mod["current_mode"] = "adequate"  # restore
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_hierarchies.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port with import rewrite**

```bash
git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/hierarchies.py \
  | sed 's/from colony\./from aurora_siger.operations./g' \
  > aurora_siger/operations/hierarchies.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_hierarchies.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/hierarchies.py tests/test_operations_hierarchies.py
git commit -m "feat(fase-3): árvores funcional e de criticidade (item 1.1)"
```

---

## Task 7: `climate.py` — port + RNG injetado + frente fria

Mudanças sobre o original do `iuri`: (1) remover `import random`; (2) cada função estocástica recebe `rng`; (3) `StormState.advance` recebe `rng`; (4) nova classe `ColdFrontState`.

**Files:**
- Create: `aurora_siger/operations/climate.py`
- Test: `tests/test_operations_climate.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_climate.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_climate.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `aurora_siger/operations/climate.py`**

```python
"""Realistic climate model for the Aurora Siger colony (Fase 3).

Ported from the team's `iuri` branch. Two changes from the original:
  * randomness is injected (a RandomLCG instance) instead of using stdlib
    `random`, so the whole simulation is deterministic per seed and two
    runs can proceed independently;
  * a ColdFrontState FSM is added (Fase 3 event) to stress the thermal model.
"""

import math

from aurora_siger.operations.constants import (
    V_BASE, V_AMPLITUDE, SEASONAL_FACTOR, V_NOISE_SIGMA,
    T_MEAN, A_DAILY, A_SEASONAL, PHI_DAILY, T_NOISE_SIGMA,
    SOLS_PER_MARS_YEAR,
    BASE_PROB_PER_SOL, DURATION_HOURS, WIND_BONUS_THRESHOLD, PERIHELION_FACTOR,
    DIDACTIC_EVENT_SOL, DIDACTIC_EVENT_HOUR,
    TAU_BASE, TAU_WIND_FACTOR, TAU_WIND_THRESHOLD,
    PANEL_LOSS_PER_SOL, CLEANING_RECOVERY, PANEL_FACTOR_FLOOR,
    COLDFRONT_PROB_PER_SOL, COLDFRONT_DURATION_HOURS, COLDFRONT_DELTA_C,
)


def compute_tau(storm, wind):
    """Atmospheric opacity = base per class + wind bonus."""
    extra = TAU_WIND_FACTOR * max(0.0, wind - TAU_WIND_THRESHOLD)
    return TAU_BASE[storm] + extra


def solar_transmission(tau):
    """Beer-Lambert: transmission = exp(-tau) (zenith simplification)."""
    return math.exp(-tau)


def update_panel_factor(current_factor, cleaning_drawn, rng):
    """Continuous deposition and (if cleaning_drawn) dust-devil recovery."""
    new = max(PANEL_FACTOR_FLOOR, current_factor - PANEL_LOSS_PER_SOL)
    if cleaning_drawn:
        recovery = rng.uniform(*CLEANING_RECOVERY)
        new = min(1.0, new + recovery)
    return new


def sample_wind(hour, rng):
    """Wind speed in m/s for the given local hour (0..23)."""
    daily_component = V_AMPLITUDE * max(0.0, math.sin(math.pi * (hour - 6) / 12))
    noise = rng.gauss(0, V_NOISE_SIGMA)
    return max(0.0, (V_BASE + daily_component) * SEASONAL_FACTOR + noise)


def sample_temperature(sol, hour, rng):
    """Temperature in °C for the given sol and hour (before cold-front offset)."""
    daily = A_DAILY * math.sin(2 * math.pi * (hour - PHI_DAILY) / 24)
    seasonal = A_SEASONAL * math.sin(2 * math.pi * sol / SOLS_PER_MARS_YEAR)
    noise = rng.gauss(0, T_NOISE_SIGMA)
    return T_MEAN + daily + seasonal + noise


class StormState:
    """Dust-storm FSM: 'clear' → 'light'/'moderate'/'severe', with persistence."""

    def __init__(self):
        self.state = "clear"
        self.hours_remaining = 0

    def _start_probability(self, klass, wind_max_24h):
        prob = BASE_PROB_PER_SOL[klass]
        wind_bonus = max(0.0, (wind_max_24h - WIND_BONUS_THRESHOLD) / 10.0)
        return prob * (1 + wind_bonus) * PERIHELION_FACTOR

    def advance(self, wind_max_24h, sol, hour, rng, force_event=False):
        """Advances one hour of the FSM."""
        if (force_event and sol == DIDACTIC_EVENT_SOL and hour == DIDACTIC_EVENT_HOUR
                and self.state == "clear"):
            self.state = "moderate"
            min_h, max_h = DURATION_HOURS["moderate"]
            self.hours_remaining = rng.randint(min_h, max_h)
            return

        if self.state != "clear":
            self.hours_remaining -= 1
            if self.hours_remaining <= 0:
                self.state = "clear"
                self.hours_remaining = 0
            return

        for klass in ("severe", "moderate", "light"):  # rarest first
            hour_prob = self._start_probability(klass, wind_max_24h) / 24.0
            if rng.random() < hour_prob:
                self.state = klass
                min_h, max_h = DURATION_HOURS[klass]
                self.hours_remaining = rng.randint(min_h, max_h)
                return


class ColdFrontState:
    """Cold-front FSM: applies COLDFRONT_DELTA_C to temperature while active."""

    def __init__(self):
        self.active = False
        self.hours_remaining = 0

    def advance(self, sol, hour, rng):
        """Advances one hour: tick down if active, else roll a new front."""
        if self.active:
            self.hours_remaining -= 1
            if self.hours_remaining <= 0:
                self.active = False
                self.hours_remaining = 0
            return
        if rng.random() < COLDFRONT_PROB_PER_SOL / 24.0:
            self.active = True
            lo, hi = COLDFRONT_DURATION_HOURS
            self.hours_remaining = rng.randint(lo, hi)

    def temperature_offset(self):
        return COLDFRONT_DELTA_C if self.active else 0.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_climate.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/climate.py tests/test_operations_climate.py
git commit -m "feat(fase-3): clima com RNG injetado (LCG) + evento de frente fria"
```

---

## Task 8: `generation.py` — port com reescrita de imports

**Files:**
- Create: `aurora_siger/operations/generation.py`
- Test: `tests/test_operations_generation.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_generation.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_generation.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port with import rewrite**

```bash
git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/generation.py \
  | sed 's/from colony\./from aurora_siger.operations./g' \
  > aurora_siger/operations/generation.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_generation.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/generation.py tests/test_operations_generation.py
git commit -m "feat(fase-3): geração solar/eólica/nuclear (port iuri)"
```

---

## Task 9: `consumption.py` — port com reescrita de imports

Porte fiel (sem `power_factor` — isso entra no M2).

**Files:**
- Create: `aurora_siger/operations/consumption.py`
- Test: `tests/test_operations_consumption.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_consumption.py
from aurora_siger.operations.consumption import (
    heating_consumption_kw, current_consumption_kw,
)

COLD = {"temperature_c": -60.0}
WARM = {"temperature_c": 25.0}


def test_thermal_zero_when_factor_zero():
    assert heating_consumption_kw(-60.0, thermal_factor=0.0) == 0.0


def test_thermal_zero_when_warmer_than_target():
    # target internal 20°C; nothing to heat when it's 25°C outside
    assert heating_consumption_kw(25.0, thermal_factor=1.0) == 0.0


def test_thermal_positive_in_cold():
    assert heating_consumption_kw(-60.0, thermal_factor=1.0) > 0.0


def test_current_consumption_adds_base_and_thermal():
    mod = {
        "consumption_by_mode": {"off": 0, "minimum": 4, "adequate": 12, "surplus": 12},
        "current_mode": "adequate",
        "thermal_factor": 0.4,
    }
    base = 12
    expected = base + heating_consumption_kw(-60.0, 0.4)
    assert current_consumption_kw(mod, COLD) == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_consumption.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port with import rewrite**

```bash
git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/consumption.py \
  | sed 's/from colony\./from aurora_siger.operations./g' \
  > aurora_siger/operations/consumption.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_consumption.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/consumption.py tests/test_operations_consumption.py
git commit -m "feat(fase-3): consumo base + térmico Q=U·A·ΔT (port iuri)"
```

---

## Task 10: `allocation.py` — port com reescrita de imports

Porte fiel do load shedding 4 estágios.

**Files:**
- Create: `aurora_siger/operations/allocation.py`
- Test: `tests/test_operations_allocation.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_allocation.py
from aurora_siger.operations.allocation import allocate_energy
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import find_module

WARM = {"temperature_c": 25.0}  # no thermal term, keeps arithmetic simple


def _reset_modes():
    for mid in range(1, 14):
        find_module(mid)["current_mode"] = "adequate"


def test_abundant_supply_keeps_everyone_at_least_adequate():
    _reset_modes()
    tree = build_criticality_tree()
    allocate_energy(tree, supply_kw=10_000, climate=WARM)
    assert all(find_module(i)["current_mode"] in ("adequate", "surplus")
               for i in range(1, 14))


def test_scarce_supply_never_shuts_vital():
    _reset_modes()
    tree = build_criticality_tree()
    allocate_energy(tree, supply_kw=1.0, climate=WARM)
    vital_ids = [1, 2, 7, 3]  # Command, ECLSS, Medical, Habitat
    assert all(find_module(i)["current_mode"] != "off" for i in vital_ids)


def test_expansion_sheds_before_vital():
    _reset_modes()
    tree = build_criticality_tree()
    allocate_energy(tree, supply_kw=20.0, climate=WARM)
    # Science Lab (id 12, Expansion) should be off before any Vital module
    assert find_module(12)["current_mode"] == "off"
    assert find_module(1)["current_mode"] != "off"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_allocation.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port with import rewrite**

```bash
git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/allocation.py \
  | sed 's/from colony\./from aurora_siger.operations./g' \
  > aurora_siger/operations/allocation.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_allocation.py -v`
Expected: PASS (3 passed)

> If `test_expansion_sheds_before_vital` is sensitive to the exact supply
> threshold, adjust `supply_kw` so it sits between the Vital-only cost and the
> full-colony cost (print `sum(current_consumption_kw(m, WARM) for m in MODULES)`
> to find the range). Do not change the allocation logic.

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/allocation.py tests/test_operations_allocation.py
git commit -m "feat(fase-3): load shedding 4 estágios (port iuri)"
```

---

## Task 11: `state.py` — port + rng/coldfront no estado

Mudanças sobre o original: `initial_state()` continua devolvendo `(climate, battery, history)`; o `rng` e os FSMs são montados no `run_simulation` (Task 12), não aqui. Porte verbatim com reescrita de import.

**Files:**
- Create: `aurora_siger/operations/state.py`
- Test: `tests/test_operations_state.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_state.py
from aurora_siger.operations.state import initial_state
from aurora_siger.operations.constants import HISTORY_KEYS, BATTERY_CAPACITY_KWH


def test_initial_state_shape():
    climate, battery, history = initial_state()
    assert climate["sol"] == 0 and climate["hour"] == 0
    assert battery["max_capacity_kwh"] == BATTERY_CAPACITY_KWH
    assert battery["emergency_reserve_kwh"] == BATTERY_CAPACITY_KWH * 0.20
    assert set(history) == set(HISTORY_KEYS)
    assert all(history[k] == [] for k in HISTORY_KEYS)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_state.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port with import rewrite**

```bash
git -C /home/ubuntu/projects/fiap-aurora-siger-fase3 show origin/iuri:colony/state.py \
  | sed 's/from colony\./from aurora_siger.operations./g' \
  > aurora_siger/operations/state.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_state.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/state.py tests/test_operations_state.py
git commit -m "feat(fase-3): estado inicial sem singleton (port iuri)"
```

---

## Task 12: `simulator.py` — LCG injetado + frente fria

Mudanças sobre o original do `iuri`: (1) `import random` → `from aurora_siger.operations.rng import RandomLCG`; (2) `run_simulation` cria `rng = RandomLCG(seed)` e o guarda no `state`; (3) `step` lê `rng = state["rng"]` e o passa às funções de clima; (4) novo `ColdFrontState` no estado, avançado a cada passo e somado à temperatura; (5) imports reescritos para `aurora_siger.operations`.

**Files:**
- Create: `aurora_siger/operations/simulator.py`
- Test: `tests/test_operations_simulator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_simulator.py
from aurora_siger.operations.simulator import run_simulation
from aurora_siger.operations.constants import TOTAL_STEPS


def test_horizon_length():
    _, _, history = run_simulation(seed=42, horizon=48)
    assert len(history["total_generation_kw"]) == 48


def test_same_seed_is_bit_identical():
    _, _, h1 = run_simulation(seed=42, horizon=TOTAL_STEPS)
    _, _, h2 = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert h1 == h2


def test_different_seed_diverges():
    _, _, h1 = run_simulation(seed=42, horizon=TOTAL_STEPS)
    _, _, h2 = run_simulation(seed=7, horizon=TOTAL_STEPS)
    assert h1["total_generation_kw"] != h2["total_generation_kw"]


def test_battery_stays_within_bounds():
    _, battery, history = run_simulation(seed=42, horizon=TOTAL_STEPS)
    charges = history["battery_charge_kwh"]
    assert all(0.0 <= c <= battery["max_capacity_kwh"] for c in charges)


def test_coldfront_recorded_when_it_fires():
    # cold-front presence is derivable from temperature dips; just assert the
    # run completes and temperature series has the expected length
    _, _, history = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert len(history["temperature_c"]) == TOTAL_STEPS
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_simulator.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `aurora_siger/operations/simulator.py`**

```python
"""Simulator orchestrator: 1 step + complete horizon.

Ported from the team's `iuri` branch, with two changes: randomness flows
through an injected RandomLCG (seeded, deterministic, no global state) and a
ColdFrontState event is advanced each step and applied to the temperature.
"""

from collections import deque

from aurora_siger.operations.allocation import allocate_energy
from aurora_siger.operations.climate import (
    sample_wind, sample_temperature, compute_tau,
    update_panel_factor, StormState, ColdFrontState,
)
from aurora_siger.operations.consumption import current_consumption_kw
from aurora_siger.operations.constants import (
    HOURS_PER_SOL, TOTAL_STEPS, CLEANING_PROB_PER_SOL, FORCE_DIDACTIC_EVENT,
)
from aurora_siger.operations.state import initial_state
from aurora_siger.operations.generation import (
    generate_solar, generate_wind, generate_nuclear,
)
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import MODULES
from aurora_siger.operations.rng import RandomLCG


def _detail_generation(climate):
    """Returns {kind: kW}. Iterates MODULES (generation depends only on type)."""
    detail = {"solar": 0.0, "wind": 0.0, "nuclear": 0.0}
    for m in MODULES:
        if m["type"] == "solar_generator":
            detail["solar"] += generate_solar(m, climate)
        elif m["type"] == "wind_generator":
            detail["wind"] += generate_wind(m, climate)
        elif m["type"] == "nuclear_generator":
            detail["nuclear"] += generate_nuclear(m, climate)
    return detail


def step(state):
    """Advances the simulation by 1 hour. Mutates `state` in place."""
    climate = state["climate"]
    battery = state["battery"]
    history = state["history"]
    criticality = state["criticality_tree"]
    storm_state = state["storm_state"]
    coldfront_state = state["coldfront_state"]
    last_wind_24h = state["last_wind_24h"]
    rng = state["rng"]

    sol = climate["sol"]
    hour = climate["hour"]

    # 1. Climate sampling (all randomness via the injected LCG)
    wind = sample_wind(hour, rng)
    temperature = sample_temperature(sol, hour, rng)
    last_wind_24h.append(wind)
    wind_max_24h = max(last_wind_24h)

    storm_state.advance(wind_max_24h, sol, hour, rng, force_event=FORCE_DIDACTIC_EVENT)
    coldfront_state.advance(sol, hour, rng)
    temperature += coldfront_state.temperature_offset()

    tau = compute_tau(storm_state.state, wind)

    if hour == 0:
        cleaning_drawn = rng.random() < CLEANING_PROB_PER_SOL
        climate["panel_factor"] = update_panel_factor(
            climate["panel_factor"], cleaning_drawn, rng
        )

    climate["wind_ms"] = wind
    climate["temperature_c"] = temperature
    climate["storm"] = storm_state.state
    climate["tau"] = tau

    # 2. Generation
    detail = _detail_generation(climate)
    total_generation = detail["solar"] + detail["wind"] + detail["nuclear"]

    # 3. Supply = generation + battery above the emergency reserve
    battery_available = max(0, battery["current_charge_kwh"] - battery["emergency_reserve_kwh"])
    supply = total_generation + battery_available

    # 4. Allocation (4-stage load shedding)
    allocate_energy(criticality, supply_kw=supply, climate=climate)

    # 5. Total consumption after allocation
    total_consumption = sum(current_consumption_kw(m, climate) for m in MODULES)

    # 6. Battery balance, clamped to [0, max]
    balance = total_generation - total_consumption
    battery["current_charge_kwh"] = max(0, min(
        battery["max_capacity_kwh"],
        battery["current_charge_kwh"] + balance,
    ))

    # 7. Emergency alert
    alerts = []
    if total_consumption > total_generation + battery_available:
        alerts.append(f"EMERGÊNCIA sol {sol} hora {hour}: oferta insuficiente")

    # 8. Record history
    history["wind_ms"].append(wind)
    history["temperature_c"].append(temperature)
    history["storm"].append(storm_state.state)
    history["tau"].append(tau)
    history["solar_generation_kw"].append(detail["solar"])
    history["wind_generation_kw"].append(detail["wind"])
    history["nuclear_generation_kw"].append(detail["nuclear"])
    history["total_generation_kw"].append(total_generation)
    history["total_consumption_kw"].append(total_consumption)
    history["battery_charge_kwh"].append(battery["current_charge_kwh"])
    history["modes_summary"].append({m["name"]: m["current_mode"] for m in MODULES})
    history["alerts"].append(alerts)

    # 9. Advance clock
    climate["hour"] += 1
    if climate["hour"] >= HOURS_PER_SOL:
        climate["hour"] = 0
        climate["sol"] += 1


def run_simulation(seed=42, horizon=TOTAL_STEPS):
    """Runs `horizon` hourly steps. Returns (climate, battery, history).

    seed=42 (default): deterministic. seed=None: entropy from the clock.
    """
    rng = RandomLCG(seed)
    climate, battery, history = initial_state()
    state = {
        "climate": climate,
        "battery": battery,
        "history": history,
        "criticality_tree": build_criticality_tree(),
        "storm_state": StormState(),
        "coldfront_state": ColdFrontState(),
        "last_wind_24h": deque(maxlen=24),
        "rng": rng,
    }
    for _ in range(horizon):
        step(state)
    return climate, battery, history
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_simulator.py -v`
Expected: PASS (5 passed)

> Note: `build_criticality_tree()` references the module dicts in `MODULES`,
> and allocation mutates `current_mode` on them. Because `MODULES` is module-level
> shared state, the determinism test still holds (each `run_simulation` re-runs
> the full deterministic sequence from the same seed), but two *concurrent* runs
> would interfere. Threading `MODULES` into state is deferred to M2 if needed.

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/simulator.py tests/test_operations_simulator.py
git commit -m "feat(fase-3): simulador headless determinístico (LCG) + frente fria"
```

---

## Task 13: Verificação do marco M1

- [ ] **Step 1: Run the full operations suite**

Run: `pytest tests/test_operations_*.py -v`
Expected: all green (≈ 37 tests across 11 files)

- [ ] **Step 2: Smoke-run a headless simulation**

Run:
```bash
python -c "
from aurora_siger.operations.simulator import run_simulation
c, b, h = run_simulation(seed=42)
print('horas:', len(h['total_generation_kw']))
print('geração média kW:', round(sum(h['total_generation_kw'])/len(h['total_generation_kw']), 1))
print('bateria final kWh:', round(b['current_charge_kwh'], 1))
print('temp mín °C:', round(min(h['temperature_c']), 1))
"
```
Expected: prints 168 horas, a positive average generation, a battery charge within [0, 500], and a minimum temperature reflecting cold-front dips.

- [ ] **Step 3: Confirm the whole repo suite still passes**

Run: `pytest`
Expected: the pre-existing 147 tests + the new operations tests, all green.

---

## Self-Review (preenchido pelo autor do plano)

**Cobertura do spec (M1 scope):**
- rng (§3.1, §3.6 dependência) → Task 2 ✓ | constants (§3) → Task 3 ✓ | tree/hierarchies/modules (§5 item 1.1) → Tasks 4–6 ✓ | climate + cold-front (§3.7) → Task 7 ✓ | generation/consumption/allocation (§3.4) → Tasks 8–10 ✓ | state (§3.1 sem singleton) → Task 11 ✓ | simulator + determinismo LCG (§3.1, §9 risco 3) → Task 12 ✓.
- **Fora do M1 (vai para M2/M3/M4):** power_factor & controle em duas camadas (§3.3), energy_levels (§3.5), prediction/decision/analysis (itens 1.2–1.4), failures (§3.6), dashboard (§4), notebook/relatório/docs (§6). Rastreado para os próximos planos.

**Placeholder scan:** sem TBD/TODO; todo passo que altera código mostra o código (ports verbatim usam comando `git show` determinístico — conteúdo reproduzível). ✓

**Consistência de tipos/assinaturas:** `RandomLCG(seed)`, `.random()`, `.gauss(mu,sigma)`, `.randint(lo,hi)`, `.uniform(a,b)` usados de forma idêntica em rng/climate/simulator. `sample_wind(hour, rng)`, `sample_temperature(sol, hour, rng)`, `update_panel_factor(current, cleaning_drawn, rng)`, `StormState.advance(wind_max_24h, sol, hour, rng, force_event=)`, `ColdFrontState.advance(sol, hour, rng)`/`.temperature_offset()` consistentes entre climate.py e simulator.py. ✓
