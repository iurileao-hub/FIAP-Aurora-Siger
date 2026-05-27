# Fase 3 — M2: Controle, Decisão e Previsão — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Estender o núcleo determinístico do M1 com as camadas de consolidação da Fase 3 — controle de carga em duas camadas (`power_factor` contínuo + load shedding 4 estágios), nível de energia como rótulo de saída (`CRITICAL→SURPLUS`), regressão OLS com dois usos (vento→energia e slope preditivo), regras de decisão, análise de balanço energético, e falhas de equipamento com auto-reparo — cobrindo os itens 1.2, 1.3 e 1.4 do enunciado.

**Architecture:** Funções puras sobre dicts (continuação do M1), três ports quase-verbatim do `iuri` (`prediction`/`decision`/`analysis`) e três peças de consolidação re-vestidas no estilo funcional a partir do `main` (`power_factor`, níveis de energia, falhas+reparo). A fusão central é o controle em duas camadas: `power_factor(battery%)` escala a **base** de consumo (térmico nunca), e o alocador 4-estágios dimensiona os **modos** sobre essa base já escalada — sem dupla-contagem, porque o consumo real (`base[modo]·power_factor + térmico`) é exatamente o que o alocador compara contra a oferta. Toda aleatoriedade nova (falhas) passa pelo `RandomLCG` único do M1; `run_simulation` reseta o estado de runtime dos módulos para preservar o determinismo por seed.

**Tech Stack:** Python 3.11+, stdlib apenas (`math`, `collections`, `os`, `datetime`), pytest. Sem numpy no pacote `operations`.

**Trabalho corrente:** repo `/home/ubuntu/projects/FIAP-Aurora-Siger`, branch `main`. O M1 já está commitado (`5a0939e`..`9b8038b`): `aurora_siger/operations/` com rng, constants, tree, modules, hierarchies, climate, generation, consumption, allocation, state, simulator; suíte de 196 testes verde.

**Pré-requisito — branches da equipe via remote `team`:** os ports usam `git show team/iuri:colony/<arquivo>.py`. Se `git show team/iuri:colony/prediction.py` falhar num clone novo, recrie o remote:

```bash
git remote add team /home/ubuntu/projects/fiap-aurora-siger-fase3
git fetch team 'refs/remotes/origin/iuri:refs/remotes/team/iuri' \
                'refs/remotes/origin/marcio:refs/remotes/team/marcio' \
                'refs/heads/main:refs/remotes/team/main'
```

**Procedência (para a nota de consolidação do M4):** `prediction.py`, `decision.py`, `analysis.py` vêm do `iuri` (núcleo científico). `power_factor`, níveis `CRITICAL→SURPLUS` e falhas+reparo vêm do `main` (`colonia_aurora/energy/energy_manager.py`, `modules/module.py`), re-vestidos no estilo funcional puro — **sem** `DataStorage` singleton, **sem** gradiente descendente (usa a OLS do `iuri`), **sem** crew (reparo é processo de fundo automático). A regressão única com dois usos, o controle em duas camadas e o reset de estado para determinismo são inéditos nas duas branches.

---

## File Structure (M2)

| Arquivo | Ação | Responsabilidade | Origem |
|---|---|---|---|
| `aurora_siger/operations/constants.py` | modificar | + níveis/slope, breakpoints power_factor, janela de tendência, prob/duração de falha, novas `HISTORY_KEYS` | novo |
| `aurora_siger/operations/prediction.py` | criar (port + append) | OLS fechada (item 1.3) + `fit_energy_trend` (slope preditivo) | port `iuri` + novo |
| `aurora_siger/operations/decision.py` | criar (port sed) | `evaluate_rules` puro (item 1.2) | port `iuri` |
| `aurora_siger/operations/analysis.py` | criar (port sed) | balanço/por-sol/breakdown/momentos críticos/log (item 1.4) | port `iuri` |
| `aurora_siger/operations/energy_levels.py` | criar | `energy_level(battery%, slope, predicted_delta)` — rótulo de saída | re-vestido do `main` |
| `aurora_siger/operations/consumption.py` | modificar | `current_consumption_kw(module, climate, power_factor=1.0)` | M1 + power_factor |
| `aurora_siger/operations/allocation.py` | modificar | `power_factor(battery%)` (throttle) + threading nos 4 estágios | M1 + re-vestido do `main` |
| `aurora_siger/operations/failures.py` | criar | falha estocástica via LCG + auto-reparo temporizado (sem crew) | re-vestido do `main` |
| `aurora_siger/operations/simulator.py` | modificar | integra power_factor, falhas, tendência OLS, nível; reseta módulos por run | M1 + consolidação |
| `tests/conftest.py` | criar | fixture autouse reseta runtime dos `MODULES` (suíte hermética) | novo |
| `tests/test_operations_*.py` | criar/modificar | suíte pytest | novo |

---

## Task 1: Constantes do M2

**Files:**
- Modify: `aurora_siger/operations/constants.py`
- Test: `tests/test_operations_constants_m2.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_constants_m2.py
from aurora_siger.operations import constants as c


def test_energy_levels_ordered_low_to_high():
    assert c.ENERGY_LEVELS == ("CRITICAL", "LOW", "NOMINAL", "HIGH", "SURPLUS")


def test_battery_level_thresholds_are_ascending_percentages():
    assert 0 < c.LEVEL_CRITICAL_PCT < c.LEVEL_LOW_PCT < c.LEVEL_SURPLUS_PCT < 100


def test_slope_thresholds_are_negative_and_ordered():
    assert c.SLOPE_CRITICAL < c.SLOPE_LOW < 0


def test_trend_window_positive():
    assert c.TREND_WINDOW > 1


def test_failure_constants_present():
    assert 0.0 < c.FAILURE_PROB_PER_HOUR < 1.0
    lo, hi = c.REPAIR_DURATION_HOURS
    assert 0 < lo <= hi


def test_history_keys_extended_with_m2_outputs():
    for key in ("energy_level", "slope", "predicted_delta", "broken_count"):
        assert key in c.HISTORY_KEYS
    # no duplicates introduced
    assert len(c.HISTORY_KEYS) == len(set(c.HISTORY_KEYS))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_constants_m2.py -v`
Expected: FAIL with `AttributeError: module ... has no attribute 'ENERGY_LEVELS'`

- [ ] **Step 3: Extend `HISTORY_KEYS` and append the M2 block**

Edit `HISTORY_KEYS` in `aurora_siger/operations/constants.py` to add four output series. Replace the existing tuple:

```python
HISTORY_KEYS = (
    "wind_ms", "temperature_c", "storm", "tau",
    "solar_generation_kw", "wind_generation_kw", "nuclear_generation_kw",
    "total_generation_kw", "total_consumption_kw",
    "battery_charge_kwh", "modes_summary", "alerts",
)
```

with:

```python
HISTORY_KEYS = (
    "wind_ms", "temperature_c", "storm", "tau",
    "solar_generation_kw", "wind_generation_kw", "nuclear_generation_kw",
    "total_generation_kw", "total_consumption_kw",
    "battery_charge_kwh", "modes_summary", "alerts",
    # --- M2 output labels (Fase 3 consolidation) ---
    "energy_level", "slope", "predicted_delta", "broken_count",
)
```

Then append this block to the END of `aurora_siger/operations/constants.py`:

```python


# --- Energy level (output label) + OLS trend (Fase 3, harvested from `main`) ---
# The CRITICAL→SURPLUS machine no longer *controls* modules; it is the read-only
# summary computed from battery % and the OLS trend. Thresholds from the team's
# `main` branch (colonia_aurora/energy/energy_manager.py).
ENERGY_LEVELS = ("CRITICAL", "LOW", "NOMINAL", "HIGH", "SURPLUS")
LEVEL_CRITICAL_PCT = 20.0      # battery % below which the level is CRITICAL
LEVEL_LOW_PCT = 40.0           # below this (and >= critical) → LOW
LEVEL_SURPLUS_PCT = 90.0       # above this → SURPLUS
SLOPE_CRITICAL = -2.0          # kW/h trend that forces a one-step downgrade
SLOPE_LOW = -0.5               # milder negative trend → softer downgrade
TREND_WINDOW = 48              # hours of recent deltas the OLS trend fits over

# --- Equipment failure + timed auto-repair (Fase 3 event, no crew) ---
# Each operational module rolls a failure each hour via the injected LCG; on
# failure it leaves generation/consumption until an automatically sampled
# repair window elapses.
FAILURE_PROB_PER_HOUR = 0.005          # ~0.5%/h per operational module
REPAIR_DURATION_HOURS = (6, 24)        # inclusive window, sampled on failure
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_constants_m2.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Confirm the existing state shape test still holds**

Run: `python3 -m pytest tests/test_operations_state.py -v`
Expected: PASS — `initial_state()` builds `history` from `HISTORY_KEYS`, so the four new keys appear automatically as empty lists.

- [ ] **Step 6: Commit**

```bash
git add aurora_siger/operations/constants.py tests/test_operations_constants_m2.py
git commit -m "feat(fase-3): constantes M2 (níveis, slope, power_factor, falhas)"
```

---

## Task 2: `prediction.py` — OLS (item 1.3), port verbatim

`prediction.py` no `iuri` é stdlib-puro (sem `from colony.`), então porta com `git show` direto, sem sed.

**Files:**
- Create: `aurora_siger/operations/prediction.py`
- Test: `tests/test_operations_prediction.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_prediction.py
import pytest
from aurora_siger.operations.prediction import (
    linear_regression, predict, fit_wind_power_model,
    wind_power_forecast, predict_next_wind_power,
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_prediction.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port the file (verbatim — no internal imports)**

```bash
git show team/iuri:colony/prediction.py \
  > aurora_siger/operations/prediction.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_prediction.py -v`
Expected: PASS (6 passed)

If a test fails because the ported API differs (function names/signatures), STOP and report NEEDS_CONTEXT — do not edit the ported logic.

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/prediction.py tests/test_operations_prediction.py
git commit -m "feat(fase-3): regressão OLS vento→energia (item 1.3, port iuri)"
```

---

## Task 3: `prediction.py` — `fit_energy_trend` (slope preditivo, 2º uso da OLS)

A mesma `linear_regression` ganha um segundo uso (§3.2): ajustar uma reta sobre os últimos deltas de energia (`geração − consumo`) e devolver `(slope, predicted_next)`. É o que o nível de energia lê (Task 6) e substitui o gradiente descendente do `main`.

**Files:**
- Modify: `aurora_siger/operations/prediction.py`
- Test: `tests/test_operations_prediction.py` (append)

- [ ] **Step 1: Write the failing test (append to the file)**

```python
# append to tests/test_operations_prediction.py
from aurora_siger.operations.prediction import fit_energy_trend


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_prediction.py -k fit_energy_trend -v`
Expected: FAIL with `ImportError: cannot import name 'fit_energy_trend'`

- [ ] **Step 3: Append `fit_energy_trend` to `aurora_siger/operations/prediction.py`**

Add at the end of the file:

```python


def fit_energy_trend(deltas):
    """Second use of the single OLS estimator (§3.2): fits the recent
    generation-minus-consumption deltas to a line and returns
    (slope, predicted_next_delta).

    `slope` is the OLS coefficient `a` (kW per step); `predicted_next_delta`
    is the line evaluated one step past the data. This replaces the team
    `main` branch's gradient-descent trend with the closed-form fit.

    Degenerate input (fewer than 2 points, or a constant series with zero
    x-variance never occurs here since xs = 0..n-1) returns a zero slope and
    the last observed value as the prediction, so callers never see a raise.
    """
    n = len(deltas)
    if n < 2:
        return 0.0, (deltas[-1] if deltas else 0.0)
    xs = list(range(n))
    a, b = linear_regression(xs, deltas)
    return a, predict(a, b, n)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_prediction.py -v`
Expected: PASS (10 passed — the 6 from Task 2 plus 4 new)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/prediction.py tests/test_operations_prediction.py
git commit -m "feat(fase-3): slope preditivo via OLS (2º uso, §3.2)"
```

---

## Task 4: `decision.py` — regras (item 1.2), port com reescrita de import

**Files:**
- Create: `aurora_siger/operations/decision.py`
- Test: `tests/test_operations_decision.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_decision.py
from aurora_siger.operations.decision import (
    evaluate_rules, priority_order,
    ACTION_REDUCE, ACTION_ECONOMY, ACTION_CLIMATE, ACTION_EMERGENCY,
)


def test_no_actions_when_healthy():
    snap = {"energy_kw": 200.0, "consumption_kw": 100.0, "storm": "clear"}
    assert evaluate_rules(snap) == []


def test_low_energy_triggers_reduce():
    snap = {"energy_kw": 40.0, "consumption_kw": 30.0, "storm": "clear"}
    assert ACTION_REDUCE in evaluate_rules(snap)


def test_low_energy_and_high_consumption_triggers_economy():
    snap = {"energy_kw": 40.0, "consumption_kw": 80.0, "storm": "clear"}
    actions = evaluate_rules(snap)
    assert ACTION_REDUCE in actions and ACTION_ECONOMY in actions


def test_consumption_above_energy_triggers_emergency():
    snap = {"energy_kw": 100.0, "consumption_kw": 120.0, "storm": "clear"}
    assert ACTION_EMERGENCY in evaluate_rules(snap)


def test_storm_triggers_climate_alert():
    snap = {"energy_kw": 200.0, "consumption_kw": 100.0, "storm": "severe"}
    assert ACTION_CLIMATE in evaluate_rules(snap)


def test_priority_order_matches_criticality_levels():
    assert priority_order() == ["Vital", "Sustenance", "Expansion"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_decision.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port with import rewrite**

```bash
git show team/iuri:colony/decision.py \
  | sed 's/from colony\./from aurora_siger.operations./g' \
  > aurora_siger/operations/decision.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_decision.py -v`
Expected: PASS (6 passed)

After porting, run `grep -n "colony" aurora_siger/operations/decision.py` — there must be no `from/import colony` lines. If the ported API differs, STOP and report NEEDS_CONTEXT.

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/decision.py tests/test_operations_decision.py
git commit -m "feat(fase-3): regras de decisão evaluate_rules (item 1.2, port iuri)"
```

---

## Task 5: `analysis.py` — análise de energia (item 1.4), port com reescrita de import

**Files:**
- Create: `aurora_siger/operations/analysis.py`
- Test: `tests/test_operations_analysis.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_analysis.py
from aurora_siger.operations.analysis import (
    analyze_balance, summarize_history, aggregate_by_sol,
    status_distribution, generation_breakdown, critical_moments, write_log,
)

# A tiny 3-hour history covering one risk hour, one surplus hour, one balanced.
HISTORY = {
    "total_generation_kw":   [50.0, 200.0, 105.0],
    "total_consumption_kw":  [100.0, 100.0, 100.0],
    "solar_generation_kw":   [10.0, 120.0, 60.0],
    "wind_generation_kw":    [20.0, 50.0, 30.0],
    "nuclear_generation_kw": [20.0, 30.0, 15.0],
    "storm":                 ["clear", "moderate", "clear"],
    "battery_charge_kwh":    [300.0, 350.0, 340.0],
    "alerts":                [["x"], [], []],
}


def test_analyze_balance_classifies_three_regimes():
    assert analyze_balance(50.0, 100.0)["status"] == "risk"
    assert analyze_balance(200.0, 100.0)["status"] == "surplus"
    assert analyze_balance(105.0, 100.0)["status"] == "balanced"


def test_summarize_history_counts_storm_and_alert_hours():
    s = summarize_history(HISTORY)
    assert s["total_steps"] == 3
    assert s["storm_hours"] == 1
    assert s["alert_hours"] == 1
    assert s["max_generation_kw"] == 200.0


def test_aggregate_by_sol_single_partial_sol():
    rows = aggregate_by_sol(HISTORY)
    assert len(rows) == 1
    assert rows[0]["sol"] == 0 and rows[0]["hours"] == 3


def test_status_distribution_sums_to_total():
    counts = status_distribution(HISTORY)
    assert counts["risk"] == 1 and counts["surplus"] == 1 and counts["balanced"] == 1


def test_generation_breakdown_shares_sum_to_one():
    bd = generation_breakdown(HISTORY)
    total_share = bd["solar"]["share"] + bd["wind"]["share"] + bd["nuclear"]["share"]
    assert abs(total_share - 1.0) < 1e-9


def test_critical_moments_finds_worst_and_best():
    cm = critical_moments(HISTORY)
    assert cm["worst_deficit"]["delta_kw"] == -50.0   # hour 0
    assert cm["biggest_surplus"]["delta_kw"] == 100.0  # hour 1


def test_write_log_creates_file(tmp_path):
    path = tmp_path / "logs" / "run.txt"
    write_log(HISTORY, str(path), seed=42)
    content = path.read_text(encoding="utf-8")
    assert "Aurora Siger" in content and "seed=42" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_analysis.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Port with import rewrite**

```bash
git show team/iuri:colony/analysis.py \
  | sed 's/from colony\./from aurora_siger.operations./g' \
  > aurora_siger/operations/analysis.py
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_analysis.py -v`
Expected: PASS (7 passed)

Run `grep -n "colony" aurora_siger/operations/analysis.py` — no `from/import colony` lines. If the ported API differs from the test's expectations, STOP and report NEEDS_CONTEXT.

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/analysis.py tests/test_operations_analysis.py
git commit -m "feat(fase-3): análise de balanço energético (item 1.4, port iuri)"
```

---

## Task 6: `energy_levels.py` — nível de energia como rótulo de saída (§3.5)

Re-veste o `_determine_level` do `main` numa função pura. O nível deixa de **controlar** módulos e passa a ser **saída** computada de `bateria% + slope OLS + delta previsto`.

**Files:**
- Create: `aurora_siger/operations/energy_levels.py`
- Test: `tests/test_operations_energy_levels.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_energy_levels.py
from aurora_siger.operations.energy_levels import energy_level


# slope=0, predicted_delta chosen so the base branch is exercised cleanly.
def test_base_levels_from_battery_pct():
    assert energy_level(10.0, slope=0.0, predicted_delta=0.0) == "CRITICAL"
    assert energy_level(30.0, slope=0.0, predicted_delta=0.0) == "LOW"
    assert energy_level(95.0, slope=0.0, predicted_delta=0.0) == "SURPLUS"
    assert energy_level(60.0, slope=0.0, predicted_delta=5.0) == "HIGH"      # rising
    assert energy_level(60.0, slope=0.0, predicted_delta=-5.0) == "NOMINAL"  # falling


def test_steep_negative_slope_downgrades_one_step():
    # NOMINAL/HIGH/SURPLUS collapse to LOW under a steep drop
    assert energy_level(60.0, slope=-3.0, predicted_delta=5.0) == "LOW"
    # LOW collapses to CRITICAL
    assert energy_level(30.0, slope=-3.0, predicted_delta=0.0) == "CRITICAL"


def test_mild_negative_slope_softer_downgrade():
    # HIGH/SURPLUS → NOMINAL
    assert energy_level(95.0, slope=-1.0, predicted_delta=0.0) == "NOMINAL"
    # NOMINAL → LOW
    assert energy_level(60.0, slope=-1.0, predicted_delta=-5.0) == "LOW"


def test_critical_battery_unaffected_by_slope():
    # already CRITICAL; slope cannot make it worse
    assert energy_level(5.0, slope=-10.0, predicted_delta=-5.0) == "CRITICAL"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_energy_levels.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `aurora_siger/operations/energy_levels.py`**

```python
"""Energy level as an output label (Fase 3 consolidation, §3.5).

Re-casts the team `main` branch's CRITICAL→SURPLUS state machine
(colonia_aurora/energy/energy_manager.py::_determine_level). Instead of
*controlling* modules, the level is now a read-only summary computed from
battery % and the OLS trend (slope + predicted next delta). The flow is
one-way: physics → level → presentation/decision.
"""

from aurora_siger.operations.constants import (
    LEVEL_CRITICAL_PCT, LEVEL_LOW_PCT, LEVEL_SURPLUS_PCT,
    SLOPE_CRITICAL, SLOPE_LOW,
)


def energy_level(battery_pct, slope, predicted_delta):
    """Returns one of CRITICAL/LOW/NOMINAL/HIGH/SURPLUS.

    Base level comes from battery %; a positive predicted delta lifts the
    mid-range to HIGH. A steeply negative OLS slope then forces a one-step
    downgrade (anticipating a drop before the battery actually falls), and a
    mildly negative slope a softer one. CRITICAL and LOW are never upgraded
    by the slope rules.
    """
    if battery_pct < LEVEL_CRITICAL_PCT:
        base = "CRITICAL"
    elif battery_pct < LEVEL_LOW_PCT:
        base = "LOW"
    elif battery_pct > LEVEL_SURPLUS_PCT:
        base = "SURPLUS"
    elif predicted_delta > 0:
        base = "HIGH"
    else:
        base = "NOMINAL"

    if slope <= SLOPE_CRITICAL:
        if base in ("NOMINAL", "HIGH", "SURPLUS"):
            return "LOW"
        if base == "LOW":
            return "CRITICAL"
    elif slope <= SLOPE_LOW:
        if base in ("HIGH", "SURPLUS"):
            return "NOMINAL"
        if base == "NOMINAL":
            return "LOW"

    return base
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_energy_levels.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/energy_levels.py tests/test_operations_energy_levels.py
git commit -m "feat(fase-3): nível de energia CRITICAL→SURPLUS como saída (§3.5)"
```

---

## Task 7: `consumption.py` — parâmetro `power_factor` (§3.4)

Adiciona a 1ª camada de controle ao consumo: a **base** por modo escala por `power_factor`; o termo térmico **nunca** escala (habitats pressurizados não podem congelar). O default `1.0` preserva o comportamento e os testes do M1.

**Files:**
- Modify: `aurora_siger/operations/consumption.py`
- Test: `tests/test_operations_consumption.py` (append)

- [ ] **Step 1: Write the failing test (append to the file)**

```python
# append to tests/test_operations_consumption.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_consumption.py -k power_factor -v`
Expected: FAIL with `TypeError: current_consumption_kw() got an unexpected keyword argument 'power_factor'`

- [ ] **Step 3: Add the `power_factor` parameter**

Replace `current_consumption_kw` in `aurora_siger/operations/consumption.py`:

```python
def current_consumption_kw(module, climate, power_factor=1.0):
    """Total consumption of the module right now (kW).

    `power_factor` (the first control layer, §3.4) throttles the per-mode base
    consumption smoothly with battery level; the thermal term is never scaled
    because pressurized habitats cannot be allowed to freeze. Defaults to 1.0
    so callers that don't throttle (and the M1 tests) are unaffected.
    """
    base = module["consumption_by_mode"][module["current_mode"]] * power_factor
    thermal = heating_consumption_kw(climate["temperature_c"], module["thermal_factor"])
    return base + thermal
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_consumption.py -v`
Expected: PASS (7 passed — the 5 from M1 plus 2 new)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/consumption.py tests/test_operations_consumption.py
git commit -m "feat(fase-3): power_factor escala base de consumo (§3.4, camada 1)"
```

---

## Task 8: `allocation.py` — `power_factor(battery%)` + threading nos 4 estágios (§3.3)

Adiciona a função `power_factor(battery_pct)` (re-vestida do `main`) e passa o `power_factor` por todos os cálculos de custo do alocador, de modo que os 4 estágios dimensionem os modos sobre os alvos **já escalados**. Composição sem dupla-contagem: o custo que o alocador compara é exatamente `base[modo]·power_factor + térmico`, idêntico ao consumo real.

**Files:**
- Modify: `aurora_siger/operations/allocation.py`
- Test: `tests/test_operations_allocation.py` (append)

- [ ] **Step 1: Write the failing test (append to the file)**

```python
# append to tests/test_operations_allocation.py
from aurora_siger.operations.allocation import power_factor


def test_power_factor_is_piecewise_and_monotonic():
    assert power_factor(80.0) == 1.0
    assert power_factor(50.0) == 1.0
    assert power_factor(5.0) == 0.2
    # monotonic non-decreasing in battery %
    pts = [power_factor(p) for p in range(0, 101, 5)]
    assert all(b >= a for a, b in zip(pts, pts[1:]))
    assert all(0.2 <= v <= 1.0 for v in pts)


def test_low_power_factor_lets_more_fit_under_same_supply():
    # With the throttle on (pf<1), the same scarce supply keeps more modules
    # out of 'off' than at full power, because each module's target is smaller.
    from aurora_siger.operations.modules import find_module, MODULES
    from aurora_siger.operations.consumption import current_consumption_kw

    def off_count(pf):
        for mid in range(1, 14):
            find_module(mid)["current_mode"] = "adequate"
        tree = build_criticality_tree()
        allocate_energy(tree, supply_kw=40.0, climate=WARM, power_factor=pf)
        return sum(1 for m in MODULES if m["current_mode"] == "off")

    assert off_count(0.4) <= off_count(1.0)


def test_allocation_default_power_factor_matches_m1():
    # default power_factor=1.0 reproduces the M1 behavior exactly
    for mid in range(1, 14):
        find_module(mid)["current_mode"] = "adequate"
    tree = build_criticality_tree()
    allocate_energy(tree, supply_kw=20.0, climate=WARM)  # no power_factor arg
    assert find_module(12)["current_mode"] == "off"
    assert find_module(1)["current_mode"] != "off"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_allocation.py -k power_factor -v`
Expected: FAIL with `ImportError: cannot import name 'power_factor'`

- [ ] **Step 3: Add `power_factor` and thread it through the allocator**

In `aurora_siger/operations/allocation.py`, add this function near the top (after the imports):

```python
def power_factor(battery_pct):
    """First control layer (§3.3): a smooth throttle on the consumption target
    as the battery drains. Piecewise-linear, harvested from the team `main`
    branch (colonia_aurora/energy/energy_manager.py::_compute_power_factor):
    full power at/above 50%, degrading to a 0.2 floor below 10%.
    """
    if battery_pct >= 50.0:
        return 1.0
    if battery_pct >= 30.0:
        return 0.7 + (battery_pct - 30.0) / 20.0 * 0.3
    if battery_pct >= 10.0:
        return 0.4 + (battery_pct - 10.0) / 20.0 * 0.3
    return 0.2
```

Replace `_consumption_at_mode` so it accepts `power_factor` (base scaled, thermal not):

```python
def _consumption_at_mode(module, mode, climate, power_factor=1.0):
    """Consumption of the module IF it were in `mode` (does not mutate).

    Mirrors consumption.current_consumption_kw: the per-mode base scales by
    power_factor, the thermal term does not.
    """
    base = module["consumption_by_mode"][mode] * power_factor
    extra = heating_consumption_kw(climate["temperature_c"], module["thermal_factor"])
    return base + extra
```

Change the `allocate_energy` signature and every `_consumption_at_mode(...)` call inside it to pass `power_factor`. Replace the whole function:

```python
def allocate_energy(criticality_tree, supply_kw, climate, power_factor=1.0):
    """Applies the 4-stage policy. Mutates module['current_mode'] in place.

    `power_factor` (the first control layer, §3.3) scales the per-mode target
    cost before the 4-stage shedding (the second layer) decides modes against
    supply. The cost compared here is exactly the real draw computed by
    consumption.current_consumption_kw with the same power_factor — so the two
    layers compose without double-counting.

    Generators are not downgraded by the policy (mode fixed at 'adequate'),
    but their own consumption IS included in the cost.
    """
    levels, generators = _leaves_by_level(criticality_tree)
    everyone = [m for level in CRITICALITY_LEVELS for m in levels[level]]

    # Stage 1: everyone at 'adequate'
    for m in everyone:
        m["current_mode"] = "adequate"
    consumer_cost = sum(_consumption_at_mode(m, "adequate", climate, power_factor) for m in everyone)
    generator_fixed_cost = sum(_consumption_at_mode(m, "adequate", climate, power_factor) for m in generators)
    cost = consumer_cost + generator_fixed_cost

    if cost <= supply_kw:
        remaining = supply_kw - cost
        for m in sorted([x for x in everyone if x["scales_with_surplus"]], key=lambda x: x["id"]):
            delta = (_consumption_at_mode(m, "surplus", climate, power_factor)
                     - _consumption_at_mode(m, "adequate", climate, power_factor))
            if remaining >= delta:
                m["current_mode"] = "surplus"
                remaining -= delta
        return

    # Stage 2: downgrade bottom-up across every level (Vital included as last resort).
    for level_name in reversed(CRITICALITY_LEVELS):
        for m in reversed(levels[level_name]):
            if cost <= supply_kw:
                return
            before = _consumption_at_mode(m, m["current_mode"], climate, power_factor)
            m["current_mode"] = "minimum"
            after = _consumption_at_mode(m, "minimum", climate, power_factor)
            cost -= (before - after)

    if cost <= supply_kw:
        return

    # Stage 3: shut off bottom-up across every level except Vital.
    for level_name in reversed(CRITICALITY_LEVELS[1:]):
        for m in reversed(levels[level_name]):
            if cost <= supply_kw:
                return
            before = _consumption_at_mode(m, m["current_mode"], climate, power_factor)
            m["current_mode"] = "off"
            after = _consumption_at_mode(m, "off", climate, power_factor)
            cost -= (before - after)

    # Stage 4: emergency — Vital stays in 'minimum'. Alert emitted by the simulator.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_allocation.py -v`
Expected: PASS (6 passed — the 3 from M1 plus 3 new). The M1 tests still pass because `power_factor` defaults to 1.0.

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/allocation.py tests/test_operations_allocation.py
git commit -m "feat(fase-3): controle em duas camadas (power_factor + 4 estágios, §3.3)"
```

---

## Task 9: `failures.py` — falha estocástica + auto-reparo (§3.6)

Módulo NOVO. Cada módulo operacional sorteia falha por hora via o LCG injetado; ao falhar, sai de geração/consumo; o reparo é automático e temporizado (sem crew). Funções puras sobre o dict do módulo — os testes usam dicts locais, nunca o `MODULES` global.

**Files:**
- Create: `aurora_siger/operations/failures.py`
- Test: `tests/test_operations_failures.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_operations_failures.py
from aurora_siger.operations.rng import RandomLCG
from aurora_siger.operations.failures import (
    is_operational, maybe_fail, advance_repair,
)


def _fresh_module():
    return {"id": 1, "name": "Test", "broken": False, "repair_hours_remaining": 0}


def test_fresh_module_is_operational():
    assert is_operational(_fresh_module()) is True


def test_maybe_fail_is_deterministic_per_seed():
    a, b = RandomLCG(42), RandomLCG(42)
    ma, mb = _fresh_module(), _fresh_module()
    rolls_a = [maybe_fail(_fresh_module(), a) for _ in range(50)]
    rolls_b = [maybe_fail(_fresh_module(), b) for _ in range(50)]
    assert rolls_a == rolls_b


def test_failure_sets_broken_and_schedules_repair():
    # find a seed/sequence that fails: drive rng until a failure is observed
    rng = RandomLCG(7)
    mod = _fresh_module()
    for _ in range(100000):
        if maybe_fail(mod, rng):
            break
    assert mod["broken"] is True
    assert is_operational(mod) is False
    assert mod["repair_hours_remaining"] >= 1


def test_advance_repair_restores_after_countdown():
    mod = {"id": 1, "broken": True, "repair_hours_remaining": 2}
    assert advance_repair(mod) is False  # 2 -> 1, still broken
    assert mod["broken"] is True
    assert advance_repair(mod) is True   # 1 -> 0, repaired
    assert mod["broken"] is False
    assert is_operational(mod) is True


def test_advance_repair_noop_on_operational_module():
    mod = _fresh_module()
    assert advance_repair(mod) is False
    assert is_operational(mod) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_failures.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create `aurora_siger/operations/failures.py`**

```python
"""Stochastic equipment failure + timed auto-repair (Fase 3 event, §3.6).

Harvested from the team `main` branch's broken/active flags
(colonia_aurora/modules/module.py), but WITHOUT the crew system: repair is an
automatic background process whose duration is sampled when the failure
happens. All randomness flows through the injected RandomLCG, so failures are
deterministic per seed like everything else in the simulation.

Pure functions over a module dict. A module carries two runtime fields:
  * "broken" (bool) — out of generation/consumption while True;
  * "repair_hours_remaining" (int) — ticks down to 0, then the module is back.
Both default to absent → operational, so callers need not pre-initialize them
(run_simulation resets them explicitly to keep runs independent).
"""

from aurora_siger.operations.constants import (
    FAILURE_PROB_PER_HOUR, REPAIR_DURATION_HOURS,
)


def is_operational(module):
    """A module is operational unless it is currently broken."""
    return not module.get("broken", False)


def maybe_fail(module, rng):
    """Rolls a failure for one operational module (one hour).

    On failure: marks it broken and samples a repair countdown. Returns True
    iff it just failed. A module already broken is left untouched (returns
    False) — repair is handled by advance_repair.
    """
    if module.get("broken", False):
        return False
    if rng.random() < FAILURE_PROB_PER_HOUR:
        module["broken"] = True
        lo, hi = REPAIR_DURATION_HOURS
        module["repair_hours_remaining"] = rng.randint(lo, hi)
        return True
    return False


def advance_repair(module):
    """Ticks a broken module's repair timer by one hour; restores it when the
    countdown reaches 0. Returns True iff it just came back online. A no-op on
    operational modules (returns False).
    """
    if not module.get("broken", False):
        return False
    module["repair_hours_remaining"] -= 1
    if module["repair_hours_remaining"] <= 0:
        module["broken"] = False
        module["repair_hours_remaining"] = 0
        return True
    return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_operations_failures.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add aurora_siger/operations/failures.py tests/test_operations_failures.py
git commit -m "feat(fase-3): falha estocástica + auto-reparo via LCG (§3.6)"
```

---

## Task 10: `simulator.py` — integração + `conftest.py` hermético

Integra tudo no passo: `power_factor` da bateria, falhas+reparo, tendência OLS e nível de energia, gravando os novos rótulos no `history`. `run_simulation` reseta o estado de runtime dos módulos para preservar o determinismo entre runs. Um `tests/conftest.py` com fixture autouse torna a suíte inteira hermética quanto ao `MODULES` global.

**Files:**
- Modify: `aurora_siger/operations/simulator.py`
- Create: `tests/conftest.py`
- Test: `tests/test_operations_simulator.py` (append)

- [ ] **Step 1: Write the failing tests (append to the simulator test file)**

```python
# append to tests/test_operations_simulator.py
from aurora_siger.operations.constants import ENERGY_LEVELS


def test_m2_history_keys_populated():
    _, _, h = run_simulation(seed=42, horizon=TOTAL_STEPS)
    for key in ("energy_level", "slope", "predicted_delta", "broken_count"):
        assert len(h[key]) == TOTAL_STEPS


def test_energy_levels_are_valid_labels():
    _, _, h = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert set(h["energy_level"]) <= set(ENERGY_LEVELS)


def test_determinism_holds_with_failures_and_control():
    # The decisive M2 regression: failures mutate the shared MODULES dicts, so
    # run_simulation MUST reset them — otherwise the second run inherits the
    # first run's broken modules and h1 != h2.
    _, _, h1 = run_simulation(seed=42, horizon=TOTAL_STEPS)
    _, _, h2 = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert h1 == h2


def test_broken_count_within_module_count():
    _, _, h = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert all(0 <= b <= 13 for b in h["broken_count"])


def test_battery_still_within_bounds_under_m2():
    _, battery, h = run_simulation(seed=42, horizon=TOTAL_STEPS)
    assert all(0.0 <= c <= battery["max_capacity_kwh"] for c in h["battery_charge_kwh"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_operations_simulator.py -k "m2 or determinism_holds_with" -v`
Expected: FAIL with `KeyError: 'energy_level'` (step() doesn't record the new keys yet).

- [ ] **Step 3: Create `tests/conftest.py` (hermetic shared state)**

```python
"""Test fixtures shared across the suite.

MODULES (aurora_siger.operations.modules) is module-level shared state that
allocation and failures mutate in place. Resetting each module's runtime
fields before every test makes the suite order-independent: no test inherits
another's modes or failures. (run_simulation does the same reset internally;
this fixture protects tests that drive step()/allocate_energy directly.)
"""

import pytest

from aurora_siger.operations.modules import MODULES


@pytest.fixture(autouse=True)
def _reset_module_runtime_state():
    for m in MODULES:
        m["broken"] = False
        m["repair_hours_remaining"] = 0
        m["current_mode"] = "adequate"
    yield
```

- [ ] **Step 4: Rewrite `aurora_siger/operations/simulator.py`**

Replace the entire file with:

```python
"""Simulator orchestrator: 1 step + complete horizon (Fase 3, M2).

Builds on M1's deterministic core. M2 adds the consolidation layers:
  * a battery-driven power_factor that throttles consumption targets, composed
    with the 4-stage load shedding (two-layer control, §3.3);
  * stochastic equipment failure with timed auto-repair (§3.6);
  * an OLS energy trend (slope + predicted next delta) and the CRITICAL→SURPLUS
    energy level it feeds (§3.5), recorded each step as output labels.

Determinism per seed is preserved: all randomness still flows through the
single injected RandomLCG, and run_simulation() resets per-module runtime
state so a fresh seeded run never inherits a previous run's failures or modes.
"""

from collections import deque

from aurora_siger.operations.allocation import allocate_energy, power_factor
from aurora_siger.operations.climate import (
    sample_wind, sample_temperature, compute_tau,
    update_panel_factor, StormState, ColdFrontState,
)
from aurora_siger.operations.consumption import current_consumption_kw
from aurora_siger.operations.constants import (
    HOURS_PER_SOL, TOTAL_STEPS, CLEANING_PROB_PER_SOL, FORCE_DIDACTIC_EVENT,
    TREND_WINDOW,
)
from aurora_siger.operations.energy_levels import energy_level
from aurora_siger.operations.failures import maybe_fail, advance_repair, is_operational
from aurora_siger.operations.prediction import fit_energy_trend
from aurora_siger.operations.state import initial_state
from aurora_siger.operations.generation import (
    generate_solar, generate_wind, generate_nuclear,
)
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import MODULES
from aurora_siger.operations.rng import RandomLCG


def _detail_generation(climate):
    """Returns {kind: kW}. Skips broken modules (a failed unit produces nothing)."""
    detail = {"solar": 0.0, "wind": 0.0, "nuclear": 0.0}
    for m in MODULES:
        if not is_operational(m):
            continue
        if m["type"] == "solar_generator":
            detail["solar"] += generate_solar(m, climate)
        elif m["type"] == "wind_generator":
            detail["wind"] += generate_wind(m, climate)
        elif m["type"] == "nuclear_generator":
            detail["nuclear"] += generate_nuclear(m, climate)
    return detail


def _energy_trend(history):
    """(slope, predicted_next_delta) over the recent generation-minus-consumption
    deltas, via the single OLS estimator (§3.2). Short history → (0.0, 0.0)."""
    gen = history["total_generation_kw"]
    con = history["total_consumption_kw"]
    deltas = [g - c for g, c in zip(gen, con)][-TREND_WINDOW:]
    return fit_energy_trend(deltas)


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

    # 1. Climate sampling — wind then temperature MUST stay the first rng draws
    #    (the cold-front wiring test probes the rng in exactly this order).
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

    # 2. Equipment failures + auto-repair (after climate draws; fixed iteration
    #    order over MODULES keeps the rng sequence deterministic).
    for m in MODULES:
        if is_operational(m):
            maybe_fail(m, rng)
        else:
            advance_repair(m)
    broken_count = sum(1 for m in MODULES if not is_operational(m))

    # 3. First control layer: battery-driven power_factor (uses the charge at
    #    the start of the hour, before this step's balance is applied).
    battery_pct = battery["current_charge_kwh"] / battery["max_capacity_kwh"] * 100.0
    pf = power_factor(battery_pct)

    # 4. Generation (broken modules excluded)
    detail = _detail_generation(climate)
    total_generation = detail["solar"] + detail["wind"] + detail["nuclear"]

    # 5. Supply = generation + battery available above the emergency reserve
    battery_available = max(0, battery["current_charge_kwh"] - battery["emergency_reserve_kwh"])
    supply = total_generation + battery_available

    # 6. Second control layer: 4-stage load shedding over the scaled targets
    allocate_energy(criticality, supply_kw=supply, climate=climate, power_factor=pf)

    # 7. Total consumption after allocation (operational modules, scaled draw)
    total_consumption = sum(
        current_consumption_kw(m, climate, power_factor=pf)
        for m in MODULES if is_operational(m)
    )

    # 8. Battery balance, clamped to [0, max]
    balance = total_generation - total_consumption
    battery["current_charge_kwh"] = max(0, min(
        battery["max_capacity_kwh"],
        battery["current_charge_kwh"] + balance,
    ))

    # 9. OLS energy trend → energy level (output labels) + emergency alert
    slope, predicted_delta = _energy_trend(history)
    level = energy_level(battery_pct, slope, predicted_delta)

    alerts = []
    if total_consumption > total_generation + battery_available:
        alerts.append(f"EMERGÊNCIA sol {sol} hora {hour}: oferta insuficiente")

    # 10. Record history
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
    history["energy_level"].append(level)
    history["slope"].append(slope)
    history["predicted_delta"].append(predicted_delta)
    history["broken_count"].append(broken_count)

    # 11. Advance clock
    climate["hour"] += 1
    if climate["hour"] >= HOURS_PER_SOL:
        climate["hour"] = 0
        climate["sol"] += 1


def _reset_modules():
    """Clears per-module runtime state so a fresh run never inherits a previous
    run's failures or modes. MODULES is module-level shared state: allocation
    overwrites current_mode every step, but the failure flags would otherwise
    persist across run_simulation calls and break determinism."""
    for m in MODULES:
        m["broken"] = False
        m["repair_hours_remaining"] = 0
        m["current_mode"] = "adequate"


def run_simulation(seed=42, horizon=TOTAL_STEPS):
    """Runs `horizon` hourly steps. Returns (climate, battery, history).

    seed=42 (default): deterministic. seed=None: entropy from the clock.
    """
    rng = RandomLCG(seed)
    _reset_modules()
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

- [ ] **Step 5: Run the simulator tests**

Run: `python3 -m pytest tests/test_operations_simulator.py -v`
Expected: PASS (11 passed — the 6 from M1 plus 5 new). The M1 cold-front test still passes because failures roll *after* the wind/temperature draws, leaving the probed temperature unchanged.

- [ ] **Step 6: Commit**

```bash
git add aurora_siger/operations/simulator.py tests/conftest.py tests/test_operations_simulator.py
git commit -m "feat(fase-3): integra controle 2 camadas + falhas + nível/slope no simulador"
```

---

## Task 11: Verificação do marco M2

- [ ] **Step 1: Run the full operations suite**

Run: `python3 -m pytest tests/test_operations_*.py -v`
Expected: all green. M1 (~49) + M2 (constants 6, prediction 10, decision 6, analysis 7, energy_levels 4, consumption +2, allocation +3, failures 5, simulator +5) ≈ 97 tests.

- [ ] **Step 2: Smoke-run a headless simulation with the M2 outputs**

Run:
```bash
python3 -c "
from aurora_siger.operations.simulator import run_simulation
from collections import Counter
c, b, h = run_simulation(seed=42)
print('horas:', len(h['total_generation_kw']))
print('bateria final kWh:', round(b['current_charge_kwh'], 1))
print('níveis:', dict(Counter(h['energy_level'])))
print('horas com módulo quebrado:', sum(1 for x in h['broken_count'] if x > 0))
print('slope final:', round(h['slope'][-1], 3), '| delta previsto:', round(h['predicted_delta'][-1], 2))
"
```
Expected: 168 horas; bateria em [0, 500]; distribuição de níveis cobrindo ao menos NOMINAL/HIGH/LOW; algumas horas com módulo quebrado (falhas dispararam); slope/predicted_delta numéricos.

- [ ] **Step 3: Confirm two seeded runs produce identical logs (determinism)**

Run:
```bash
python3 -c "
from aurora_siger.operations.simulator import run_simulation
_,_,h1 = run_simulation(seed=42); _,_,h2 = run_simulation(seed=42)
print('determinismo (h1 == h2):', h1 == h2)
_,_,h3 = run_simulation(seed=7)
print('seeds divergem:', h1['energy_level'] != h3['energy_level'] or h1['total_generation_kw'] != h3['total_generation_kw'])
"
```
Expected: `determinismo (h1 == h2): True` e `seeds divergem: True`.

- [ ] **Step 4: Confirm the whole repo suite still passes**

Run: `python3 -m pytest`
Expected: the pre-existing 147 fase-1/2 tests + all operations tests, all green.

> Nota de ambiente: rode `pytest` num shell onde o venv do projeto (com numpy/pandas) esteja ativo — os testes das fases 1–2 dependem deles. Os testes de `operations/` são stdlib-puro e passam em qualquer ambiente.

---

## Self-Review (preenchido pelo autor do plano)

**Cobertura do spec (M2 scope):**
- §3.2 OLS dois usos → Task 2 (vento→energia) + Task 3 (slope) ✓
- §3.3 controle em duas camadas → Task 7 (consumo) + Task 8 (power_factor + threading) + Task 10 (composição no step) ✓
- §3.4 consumo com power_factor → Task 7 ✓
- §3.5 nível de energia como saída → Task 6 + Task 10 (gravação) ✓
- §3.6 falhas + auto-reparo → Task 9 + Task 10 (integração, exclusão de gen/consumo) ✓
- item 1.2 decisão → Task 4 ✓ | item 1.3 previsão → Task 2 ✓ | item 1.4 análise → Task 5 ✓
- **Fora do M2 (vai para M3/M4):** dashboard 6 abas + SimSnapshot + cli (M3); notebook/relatório/ensaio/README/bump 0.3.0 (M4). Rastreado.

**Riscos do spec (§9) tratados:**
- Dupla-contagem (§9.1): Task 8 compõe power_factor (escala base) + 4 estágios (decide modos) de forma que o custo comparado é idêntico ao draw real; teste de fronteira em Task 8 (`test_low_power_factor_lets_more_fit`).
- Determinismo com LCG (§9.3): falhas passam pelo LCG único; `_reset_modules()` em `run_simulation` evita vazamento de `broken` entre runs; `test_determinism_holds_with_failures_and_control` (Task 10) é o guard. Falhas rolam **depois** de wind/temp para não quebrar o teste de frente fria do M1.
- Escopo/monólito (§9.4): cada módulo tem responsabilidade única; `conftest.py` autouse torna a suíte hermética quanto ao `MODULES` global (resolve a fragilidade que o M1 anotou).

**Placeholder scan:** sem TBD/TODO; todo passo que altera código mostra o código completo (ports verbatim via `git show`; consolidação escrita por extenso). ✓

**Consistência de tipos/assinaturas:** `current_consumption_kw(module, climate, power_factor=1.0)` (consumption) e `_consumption_at_mode(module, mode, climate, power_factor=1.0)` (allocation) escalam a base de forma idêntica. `allocate_energy(tree, supply_kw, climate, power_factor=1.0)`. `power_factor(battery_pct)` em allocation, importada pelo simulator. `energy_level(battery_pct, slope, predicted_delta)` (energy_levels) recebe o par devolvido por `fit_energy_trend(deltas) -> (slope, predicted_next)` (prediction). `is_operational/maybe_fail/advance_repair(module[, rng])` (failures) consistentes entre failures.py e simulator.py. Novas `HISTORY_KEYS` (`energy_level`, `slope`, `predicted_delta`, `broken_count`) gravadas no step() e pré-criadas por `initial_state()` via `HISTORY_KEYS`. ✓
