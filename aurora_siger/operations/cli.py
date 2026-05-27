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
