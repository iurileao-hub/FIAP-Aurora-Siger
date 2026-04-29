"""MGPEB — Módulo de Gerenciamento de Pouso e Estabilização de Base.

Missão Aurora Siger — Colônia em Marte
Atividade Integradora — FIAP Fase 2
Equipe: Gabriel Carmona, Carlos Eugênio, Marcio Francisco, Iúri Leão, Maria Sophia

Entrypoint do protótipo CLI. Toda a lógica vive em :mod:`aurora_siger.landing`
— este arquivo apenas dispara o menu interativo. Para experimentar a API
programaticamente (cenários, gráficos, comparações), use o notebook em
``fases/fase-2/notebook.ipynb``.

Execução:

    python3 fases/fase-2/mgpeb.py
"""

from aurora_siger.landing.cli import main


if __name__ == "__main__":
    main()
