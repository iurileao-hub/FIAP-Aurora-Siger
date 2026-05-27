"""Live TUI dashboard for the Aurora Siger colony (Fase 3, §4).

The visual primitives (ANSI palette, sparkline, hbar, miniline, layout, screen
control) are harvested intact from the team `main` branch
(colonia_aurora/display/dashboard.py). The six screen renderers and the frame
composer (added in later tasks) are written fresh over a SimSnapshot, so they
read our simulator's data instead of the team's DataStorage singleton.
"""

import re
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid coupling this presentation module to the data adapter
    from aurora_siger.operations.simsnapshot import SimSnapshot

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


def _bar_line(label, value, unit, val, mx, color, w):
    """A labelled horizontal bar: 'Label  ███░░░  value unit'."""
    bar = hbar(val, mx, max(10, w - 30), color)
    return f"  {GRAY}{label:<14}{RESET}{bar} {color}{value}{unit}{RESET}"


def screen_overview(snap: "SimSnapshot", w: int, h: int) -> list[str]:
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


def screen_energy(snap: "SimSnapshot", w: int, h: int) -> list[str]:
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


def screen_sensors(snap: "SimSnapshot", w: int, h: int) -> list[str]:
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


_MODE_CLR = {"surplus": TEAL, "adequate": GREEN, "minimum": YELLOW, "off": DIM_C}


def screen_modules(snap: "SimSnapshot", w: int, h: int) -> list[str]:
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


def screen_events(snap: "SimSnapshot", w: int, h: int) -> list[str]:
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


def screen_hierarchy(snap: "SimSnapshot", w: int, h: int) -> list[str]:
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


# Display labels stay in Portuguese (product UI); function identifiers are
# English per the package naming convention.
TABS = [
    ("Overview", "1", screen_overview),
    ("Energia", "2", screen_energy),
    ("Módulos", "3", screen_modules),
    ("Sensores", "4", screen_sensors),
    ("Eventos", "5", screen_events),
    ("Hierarquia", "6", screen_hierarchy),
]


def _tab_bar(active_idx):
    cells = []
    for i, (name, key, _) in enumerate(TABS):
        if i == active_idx:
            cells.append(f"{BOLD}{AMBER}[{key}:{name}]{RESET}")
        else:
            cells.append(f"{GRAY}{key}:{name}{RESET}")
    return "  ".join(cells)


def render_frame(snap: "SimSnapshot", tab_idx: int) -> str:
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
    buf.append(at(1, 2,
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
