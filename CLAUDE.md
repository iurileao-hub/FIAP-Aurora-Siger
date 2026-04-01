# CLAUDE.md

Instruções para o Claude Code ao trabalhar neste repositório.

## Projeto

Aurora SIGER (Sistema Inteligente de Gerenciamento de Riscos) é um projeto acadêmico da FIAP (Ciência da Computação, 2026) que simula um sistema de gerenciamento de riscos para telemetria pré-decolagem de foguetes. O projeto se estende por **7 fases** ao longo do primeiro ano de graduação — atualmente na **Fase 1**.

- **Público técnico** → código e notebooks neste repo
- **Público leigo** → apresentação via MDX no portfólio (iurileao.dev, repo separado)

## Setup

```bash
# Instalar pacote em modo editável (inclui dependências de visualização e dev)
pip install -e ".[dev,viz]"

# Rodar testes
pytest

# Abrir notebook da fase 1
jupyter notebook fases/fase-1/notebook.ipynb
```

## Arquitetura

O projeto é um **pacote Python instalável** (`aurora_siger/`) com notebooks por fase:

```
aurora_siger/                 # Pacote principal — cresce com cada fase
├── data/generation.py        # Geração de dataset sintético de telemetria
├── eda/plots.py              # Funções de visualização (heatmap, pairplot, boxplot, 3D)
├── models/isolation_forest.py # IsolationTreeNode, IsolationTree, MyIsolationForest
└── pipeline/
    ├── validator.py           # Validator + RULES (faixas seguras)
    └── launch.py              # ai_anomaly_check, calculate_autonomy, launch_decision

fases/fase-N/                 # Cada fase tem seu próprio diretório
├── notebook.ipynb            # Notebook técnico (importa de aurora_siger)
└── assets/                   # Imagens e artefatos gerados

docs/fase-N/                  # Documentação textual por fase
tests/                        # Testes pytest (na raiz, acompanham o pacote)
archive/                      # Notebook original preservado como referência
```

### Convenções

- **Versionamento**: `0.N.0` corresponde à fase N (ex: `0.1.0` = Fase 1)
- **Imports**: sempre usar `from aurora_siger.modulo import ...` — nunca lógica inline no notebook
- **Testes**: pytest, TDD quando possível. Arquivo `test_<modulo>.py` para cada módulo
- **Idioma do código**: nomes de variáveis/funções em inglês, docstrings em inglês, documentação/ensaios em português
- **Type hints**: obrigatórios em todos os parâmetros e retornos de funções públicas

## Como adicionar uma nova fase

1. Criar `fases/fase-N/notebook.ipynb` importando de `aurora_siger`
2. Criar `fases/fase-N/assets/` para imagens geradas
3. Criar `docs/fase-N/` para ensaios e documentação textual
4. Adicionar novos módulos em `aurora_siger/` conforme necessário (ex: `aurora_siger/models/random_forest.py`)
5. Adicionar testes em `tests/`
6. Atualizar `__version__` em `aurora_siger/__init__.py` e `pyproject.toml`
7. Atualizar a tabela de entregáveis no `README.md`

## Decisões de design

- `_average_path_length()` (média de caminho BST via constante de Euler-Mascheroni) é **intencionalmente duplicada** em `IsolationTree` e `MyIsolationForest` para manter cada classe autossuficiente
- `generate_telemetry_dataset()` usa `np.random.RandomState(seed)` (não `np.random.seed()` global) para isolamento entre chamadas
- `structural_integrity` e `critical_modules` são correlacionados com `tank_pressure` via função logística (probabilidade de falha sobe quando pressão excede 340/300 atm para dados normais/anômalos)
- `Validator` aceita um `rules` dict opcional no construtor para permitir override em testes ou fases futuras
- `launch_decision()` retorna `bool` (True=GO, False=NO-GO) e imprime o relatório

## Referência rápida — faixas seguras de telemetria

| Coluna | Faixa segura | Condição de aborto |
|---|---|---|
| `internal_temp` | 18–26 °C | fora da faixa |
| `external_temp` | -65–125 °C | fora da faixa |
| `structural_integrity` | 1 = intacto | != 1 |
| `energy` | 60–100 % | < 60 |
| `vibration` | 0.1–0.5 g | fora da faixa |
| `tank_pressure` | 270–340 atm | fora da faixa |
| `critical_modules` | 1 = ativo | != 1 |
