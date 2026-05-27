#!/usr/bin/env python3
"""Entry point for the Fase 3 live dashboard — thin wrapper over the package.

Preserves `python3 fases/fase-3/aurora_core.py` while the logic lives in
`aurora_siger.operations.cli` (mirrors the Fase 2 `mgpeb.py` wrapper).
"""

import sys

from aurora_siger.operations.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
