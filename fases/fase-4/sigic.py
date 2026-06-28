# fases/fase-4/sigic.py
"""Fase 4 entrypoint — thin wrapper over aurora_siger.colony.cli:main.

Mirrors fases/fase-2/mgpeb.py and fases/fase-3/aurora_core.py: lets
`python3 fases/fase-4/sigic.py` run the SIGIC terminal app while the logic lives
in the installable package.
"""

from aurora_siger.colony.cli import main

if __name__ == "__main__":
    main()
