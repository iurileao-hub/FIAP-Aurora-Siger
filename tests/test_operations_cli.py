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
