# CLAUDE.md

Instruções para o Claude Code ao trabalhar neste repositório.

## Projeto

Aurora SIGER — atividade integradora da FIAP (Ciência da Computação online, 2026), desenvolvida em **7 fases** ao longo do ano. Para a visão de produto e os entregáveis por fase, ver [`README.md`](README.md). Estado atual: **fases 1 e 2 concluídas** (versão 0.2.0).

## Setup

```bash
pip install -e ".[dev,viz]"   # instala em modo editável
pytest                        # 147 testes (~0.7s)
python3 fases/fase-2/mgpeb.py # CLI da fase 2 (ou `mgpeb` após install)
```

## Arquitetura

```
aurora_siger/                   # Pacote Python — cresce com cada fase
├── data/, eda/, models/, pipeline/   # Fase 1 — telemetria, IF, decisão Go/No-Go
└── landing/                          # Fase 2 — pouso e estabilização (MGPEB)
    ├── module.py        # Module @dataclass + DEFAULT_MODULES
    ├── structures.py    # Vector, Queue, Stack
    ├── authorization.py # evaluate() puro, AuthorizationResult, Alert
    ├── physics.py       # 4 funções físicas
    ├── mission.py       # LandingMission (orquestrador stateful)
    └── cli.py           # menus interativos parametrizados em LandingMission

tests/                  # pytest na raiz, espelha o pacote
fases/fase-N/           # entrypoint: notebook.ipynb (+ extras por fase)
docs/fase-N/            # ensaios textuais
archive/                # gitignored — material original preservado
```

## Convenções

- **Versionamento**: `0.N.0` corresponde à fase N (`0.2.0` = fase 2).
- **Imports**: notebooks importam de `aurora_siger.<modulo>` — nunca lógica inline.
- **Idioma**: nomes/docstrings em inglês no pacote; ensaios e README em português.
- **Type hints**: obrigatórios em parâmetros e retornos públicos.
- **Testes**: `tests/test_<dominio>_<arquivo>.py`; TDD quando possível.
- **Pacote zero-dep no CLI**: `aurora_siger/landing/` usa só `math` + `random`. NumPy fica para módulos da fase 1 e para scripts de plotagem (`figuras/gerar_graficos.py`).

## Decisões de design — fase 1

- `_average_path_length()` é **intencionalmente duplicada** em `IsolationTree` e `MyIsolationForest` para manter cada classe autossuficiente.
- `generate_telemetry_dataset()` usa `np.random.RandomState(seed)` (não `np.random.seed()` global) para isolamento entre chamadas.
- `Validator` aceita `rules` opcional no construtor para override em testes ou fases futuras.
- `launch_decision()` retorna `bool` e imprime o relatório (similar ao `LandingMission.print_report` da fase 2).

## Decisões de design — fase 2

- **Regra de autorização** (`authorization.evaluate`) é **pura**: recebe módulo + condições, devolve `AuthorizationResult(authorized, reasons)`. O empilhamento de `Alert` na `alert_stack` é responsabilidade da `LandingMission`, não da regra. Materializa o argumento "regra inspecionável" do relatório.
- **`LandingMission` encapsula todo o estado** (queue, landed/waiting vectors, alert stack, conditions). Sem globais — duas missões podem rodar em paralelo num notebook.
- **`Vector` → `Queue` → `Stack` por herança** preserva a Figura A.1 do relatório. `Vector` carrega busca/ordenação Module-specific; `Stack` polimórfico aceita `Alert` na `alert_stack` (sem chamar métodos Module-específicos).
- **`Module` é `@dataclass`** com atributos `id`/`type`/`status` deliberadamente sombreando builtins para fidelidade ao relatório (`module.id`, `module.type`).
- **`mgpeb.py` é wrapper de 21 linhas** sobre `aurora_siger.landing.cli:main` — preserva `python3 fases/fase-2/mgpeb.py` enquanto a lógica vive no pacote.
- **`figuras/gerar_graficos.py` importa de `physics.py`** — única fonte de verdade para as 4 fórmulas.

## Como adicionar uma nova fase

1. Criar `aurora_siger/<dominio>/` com submódulos por responsabilidade (ver `landing/` como referência).
2. Criar `fases/fase-N/notebook.ipynb` importando de `aurora_siger.<dominio>` + assets/.
3. Criar `docs/fase-N/` para ensaios.
4. Adicionar testes `tests/test_<dominio>_<arquivo>.py`.
5. Bump `__version__` para `0.N.0` em `aurora_siger/__init__.py` e `pyproject.toml`.
6. Atualizar tabela de roadmap e entregáveis no `README.md`.
7. Executar notebook in-place (`jupyter nbconvert --execute --inplace`) antes do commit para popular outputs.
