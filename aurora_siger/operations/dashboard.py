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
