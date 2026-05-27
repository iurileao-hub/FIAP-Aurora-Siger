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
