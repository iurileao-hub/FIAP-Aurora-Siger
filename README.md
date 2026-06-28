# Aurora SIGER

**Sistema Inteligente de Gerenciamento de Riscos**

[![Fase 1 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/iurileao-hub/FIAP-Aurora-Siger/blob/main/fases/fase-1/notebook.ipynb)
[![Fase 2 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/iurileao-hub/FIAP-Aurora-Siger/blob/main/fases/fase-2/notebook.ipynb)
[![Fase 3 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/iurileao-hub/FIAP-Aurora-Siger/blob/main/fases/fase-3/notebook.ipynb)

> Projeto desenvolvido como atividade integradora do primeiro ano do curso de **Ciência da Computação (online)** na **FIAP — 2026**. O repositório acompanha todas as **7 fases** do projeto ao longo do ano letivo, cada fase adicionando novas capacidades ao sistema.

## O que é o Aurora SIGER?

Imagine que você faz parte da equipe de controle de missão de uma colônia espacial. A cada operação crítica — uma decolagem na Terra, um pouso em outro planeta — dezenas de sensores transmitem dados em tempo real e dezenas de regras precisam ser verificadas em segundos. **Como decidir se é seguro prosseguir?**

O Aurora SIGER responde a essa pergunta com um pipeline de decisão **Go/No-Go** que evolui ao longo das fases:

- **Fase 1 — Decolagem (telemetria):** validação determinística de 7 sensores, detecção de anomalias com Isolation Forest implementado do zero e análise energética orbital. Resultado: **"PRONTO PARA DECOLAR"** ou aborto justificado.
- **Fase 2 — Pouso (MGPEB):** organização da fila de pouso de 12 módulos da colônia Aurora Siger em Marte, autorização por expressão booleana inspecionável `F ∧ A ∧ (L ∨ E) ∧ S` e registro auditável de cada bloqueio. Resultado: **"AUTORIZADO PARA POUSO"** ou bloqueio rastreável.
- **Fase 3 — Operação (energia):** a colônia que pousou agora opera. Simulação horária **determinística** de geração (solar/eólica/nuclear), consumo (carga base + térmico `Q = U·A·ΔT`), bateria e clima (opacidade `tau`, tempestades, frente fria); controle de carga em duas camadas; previsão por regressão OLS feita à mão; dashboard TUI ao vivo de 6 abas. Resultado: a evolução de decisões **reativas** para **preditivas**.
- **Fase 4 — Topologia (rede):** a colônia que opera agora se mapeia como grafo ponderado; BFS/DFS/Dijkstra, pontos de articulação, centralidade (Brandes) e modelagem de consumo ancorada na geração real (210 kW).

Em todas as fases, a ênfase é a mesma: decisões automatizadas em sistemas críticos precisam ser **inspecionáveis** — tabela-verdade aberta, faixas seguras documentadas, histórico empilhado.

---

## Quick start

```bash
# Clone o repositório
git clone https://github.com/iurileao-hub/FIAP-Aurora-Siger.git
cd FIAP-Aurora-Siger

# Instale o pacote (com dependências de desenvolvimento e visualização)
pip install -e ".[dev,viz]"

# Notebook da fase 1 — telemetria de decolagem
jupyter notebook fases/fase-1/notebook.ipynb

# Notebook da fase 2 — pouso e estabilização
jupyter notebook fases/fase-2/notebook.ipynb

# Protótipo CLI da fase 2 (após install, em qualquer diretório)
mgpeb

# ...ou direto pelo arquivo, sem instalar
python3 fases/fase-2/mgpeb.py

# Notebook da fase 3 — operação energética da colônia
jupyter notebook fases/fase-3/notebook.ipynb

# Dashboard TUI ao vivo da fase 3 (após install, em qualquer diretório)
aurora

# ...ou direto pelo arquivo, sem instalar
python3 fases/fase-3/aurora_core.py

# TUI SIGIC da fase 4 (após install, em qualquer diretório)
sigic

# ...ou direto pelo arquivo, sem instalar
python3 fases/fase-4/sigic.py
```

---

## Estrutura do projeto

```
FIAP-Aurora-Siger/
├── pyproject.toml
├── README.md
├── LICENSE
├── aurora_siger/                 # Pacote Python principal — cresce a cada fase
│   ├── data/generation.py        # Fase 1 — geração de telemetria sintética
│   ├── eda/plots.py              # Fase 1 — visualização exploratória
│   ├── models/isolation_forest.py# Fase 1 — Isolation Forest do zero
│   ├── pipeline/                 # Fase 1 — validação e decisão Go/No-Go
│   │   ├── validator.py
│   │   └── launch.py
│   ├── landing/                  # Fase 2 — pouso e estabilização (MGPEB)
│   │   ├── module.py
│   │   ├── structures.py
│   │   ├── authorization.py
│   │   ├── physics.py
│   │   ├── mission.py
│   │   └── cli.py
│   ├── operations/               # Fase 3 — colônia operando (energia + decisão)
│   │   ├── rng.py                # LCG seed-aware (determinismo)
│   │   ├── tree.py / hierarchies.py   # árvores N-árias (item 1.1)
│   │   ├── climate.py            # vento, temp, tau, tempestades, frente fria
│   │   ├── generation.py / consumption.py / allocation.py
│   │   ├── decision.py / energy_levels.py   # regras + nível (item 1.2)
│   │   ├── prediction.py         # OLS à mão (item 1.3)
│   │   ├── analysis.py           # balanço energético (item 1.4)
│   │   ├── failures.py / simulator.py / state.py
│   │   └── simsnapshot.py / dashboard.py / cli.py   # dashboard TUI ao vivo
│   └── colony/                   # Fase 4 — topologia/rede da colônia (grafo + algoritmos)
├── tests/                        # pytest acompanha o pacote
├── fases/
│   ├── fase-1/
│   │   ├── notebook.ipynb
│   │   └── assets/
│   ├── fase-2/
│   │   ├── notebook.ipynb
│   │   ├── mgpeb.py              # entrypoint CLI fino sobre aurora_siger.landing
│   │   ├── relatorio.md / .pdf   # relatório técnico da entrega FIAP
│   │   └── figuras/
│   ├── fase-3/
│   │   ├── notebook.ipynb        # narrativa dos 4 itens (run_simulation headless)
│   │   ├── aurora_core.py        # entrypoint fino sobre aurora_siger.operations
│   │   ├── relatorio.md / .pdf   # relatório técnico da entrega FIAP
│   │   └── figuras/
│   └── fase-4/
│       ├── sigic.py              # entrypoint fino sobre aurora_siger.colony
│       ├── enunciado.md          # enunciado oficial FIAP
│       ├── relatorio.md / .pdf   # relatório técnico da entrega FIAP
│       └── figuras/              # rede_colonia.png/.pdf (matplotlib)
└── docs/
    ├── fase-1/
    │   ├── pseudocodigo.md / fluxograma.md / energia.md / etica.md
    ├── fase-2/
    │   ├── contextualizacao-historica.md
    │   └── esg.md
    ├── fase-3/
    │   └── reativo-a-preditivo.md   # ensaio reflexivo
    └── fase-4/
        └── operacao-a-topologia.md  # ensaio reflexivo
```

---

## Entregáveis da Fase 1

| Entregável | Descrição | Arquivo |
|------------|-----------|---------|
| **1.1** Organização da telemetria | Geração de 100k amostras sintéticas (97k normais + 3k anomalias) com 7 sensores | `aurora_siger/data/generation.py` |
| **1.2** Algoritmo de verificação | Pseudocódigo e fluxograma do pipeline de 3 etapas | `docs/fase-1/pseudocodigo.md`, `docs/fase-1/fluxograma.md` |
| **1.3** Script em Python | Classe `Validator`, funções `ai_anomaly_check()`, `calculate_autonomy()` e `launch_decision()` | `aurora_siger/pipeline/validator.py`, `aurora_siger/pipeline/launch.py` |
| **1.4** Análise energética | Cálculo de autonomia orbital (18 kWh, perdas 14%, consumo orbital 1.2 kW) | `docs/fase-1/energia.md` |
| **1.5** Análise assistida por IA | Isolation Forest do zero + comparação com Scikit-learn | `aurora_siger/models/isolation_forest.py` |
| **1.6** Reflexão crítica | Ensaio sobre ética, automação e limites da IA na tomada de decisão | `docs/fase-1/etica.md` |

## Entregáveis da Fase 2

| Entregável | Descrição | Arquivo |
|------------|-----------|---------|
| **2.1** Modelagem dos módulos | Classe `Module` com 12 instâncias representando a colônia; ETA derivado de `distance/speed` | `aurora_siger/landing/module.py` |
| **2.2** Estruturas lineares | `Vector`, `Queue` (FIFO) e `Stack` (LIFO) com busca linear e ordenações Bubble/Selection | `aurora_siger/landing/structures.py` |
| **2.3** Regra de autorização | Expressão booleana `F ∧ A ∧ (L ∨ E) ∧ S` com tabela-verdade e diagrama de portas lógicas | `aurora_siger/landing/authorization.py` |
| **2.4** Funções matemáticas | Altitude de descida, consumo exponencial de combustível, energia solar e temperatura senoidal | `aurora_siger/landing/physics.py` |
| **2.5** Simulação e CLI | `LandingMission` orquestra a fila, decisões e alertas; protótipo CLI executável | `aurora_siger/landing/mission.py`, `fases/fase-2/mgpeb.py` |
| **2.6** Contextualização histórica | Ensaio sobre a evolução do hardware embarcado e a hierarquia de propriedades não-funcionais | `docs/fase-2/contextualizacao-historica.md` |
| **2.7** Reflexão ESG | Ensaio sobre sustentabilidade, governança e cultura na colônia Aurora Siger | `docs/fase-2/esg.md` |
| **2.8** Relatório técnico | Documento integrador da fase 2 com seções 1–6 e Anexo A | `fases/fase-2/relatorio.pdf` |

## Entregáveis da Fase 3

| Entregável | Descrição | Arquivo |
|------------|-----------|---------|
| **3.1** Organização hierárquica | Árvores N-árias funcional + criticidade (`Node`) sobre os 13 módulos da colônia (continuidade da Fase 2) | `aurora_siger/operations/hierarchies.py`, `tree.py`, `modules.py` |
| **3.2** Regras de decisão | `evaluate_rules()` puro + nível de energia `CRITICAL→SURPLUS` como rótulo de saída | `aurora_siger/operations/decision.py`, `energy_levels.py` |
| **3.3** Previsão por regressão | OLS de forma fechada implementada à mão; dois usos (vento→eólica e slope preditivo) | `aurora_siger/operations/prediction.py` |
| **3.4** Análise energética | Balanço geração×consumo, agregação por sol, breakdown por fonte, momentos críticos | `aurora_siger/operations/analysis.py` |
| **3.5** Simulação e dashboard | Simulação horária determinística (LCG); dashboard TUI ao vivo de 6 abas; CLI `aurora` | `aurora_siger/operations/simulator.py`, `dashboard.py`, `cli.py` |
| **3.6** Reflexão crítica | Ensaio sobre a evolução de sistemas reativos para preditivos, ancorado no slope OLS | `docs/fase-3/reativo-a-preditivo.md` |
| **3.7** Relatório técnico | Documento integrador da fase 3 com nota de consolidação e tabela de procedência | `fases/fase-3/relatorio.pdf` |

## Entregáveis da Fase 4

| Entregável | Descrição | Arquivo |
|------------|-----------|---------|
| **4.1** Código | Pacote `aurora_siger/colony/` (graph/roster/topology/search/paths/analysis/modeling/cli) + entrypoint `fases/fase-4/sigic.py` | `aurora_siger/colony/`, `fases/fase-4/sigic.py` |
| **4.2** Diagrama | Mapa marciano da rede (matplotlib): 13 nós, 20 arestas, domos por tier e dimensionados por centralidade, dutos por tipo, ponto de articulação destacado | `fases/fase-4/figuras/rede_colonia.png` / `.pdf` |
| **4.3** Relatório técnico | Documento integrador da fase 4 com nota de procedência, algoritmos e modelagem | `fases/fase-4/relatorio.pdf` |
| **4.4** Enunciado | Enunciado oficial FIAP da fase 4 | `fases/fase-4/enunciado.md` |

---

## Faixas seguras de telemetria (Fase 1)

| Sensor | Faixa segura | Condição de aborto |
|--------|-------------|--------------------|
| `internal_temp` | 18 -- 26 °C | Fora da faixa |
| `external_temp` | -65 -- 125 °C | Fora da faixa |
| `structural_integrity` | 1 (íntegro) | != 1 |
| `energy` | 60 -- 100 % | < 60 % |
| `vibration` | 0.1 -- 0.5 g | Fora da faixa |
| `tank_pressure` | 270 -- 340 atm | Fora da faixa |
| `critical_modules` | 1 (ativo) | != 1 |

## Variáveis booleanas da autorização de pouso (Fase 2)

| Símbolo | Variável | Origem | Significado |
|:----:|:------------|:------------------------------------------------|:----------------------------|
| **F** | `fuel_ok` | `module.fuel_level >= 20` | Combustível suficiente para descida controlada |
| **A** | `atmosphere_ok` | condição ambiental | Atmosfera favorável (vento, visibilidade, sem tempestade) |
| **L** | `zone_free` | condição ambiental | Zona de pouso disponível |
| **E** | `emergency` | `module.cargo_criticality == 5` | Carga de criticidade máxima — *bypass* de zona ocupada |
| **S** | `sensors_ok` | `module.sensors_ok` | Sensores de bordo íntegros |

Regra: `AUTORIZADO = F ∧ A ∧ (L ∨ E) ∧ S`.

---

## Roadmap

O Aurora SIGER é desenvolvido ao longo de **7 fases** durante o ano letivo de 2026. Cada fase adiciona novas capacidades ao sistema, e o pacote `aurora_siger` cresce de forma incremental.

| Fase | Tema | Status |
|------|------|--------|
| **1** | Telemetria, Isolation Forest, pipeline Go/No-Go | Concluída |
| **2** | Pouso de módulos, estruturas lineares, lógica booleana, modelagem física | Concluída |
| **3** | Operação energética: simulação determinística, OLS, controle em 2 camadas, dashboard TUI | Concluída |
| **4** | Topologia: grafo ponderado da colônia, BFS/DFS/Dijkstra, pontos de articulação, centralidade (Brandes), modelagem de consumo | Concluída |
| **5** | *Em breve* | — |
| **6** | *Em breve* | — |
| **7** | *Em breve* | — |

---

## Autores

Projeto desenvolvido por alunos do 1.º ano de Ciência da Computação (online) — FIAP, 2026:

- **Gabriel Carmona Bittencourt** — [GitHub](https://github.com/Gcarmnonapy7) · gabrielcarmonabittencourtpy@gmail.com
- **Iúri Leão de Almeida** — [GitHub](https://github.com/iurileao-hub) · iurileao@gmail.com
- **Márcio Francisco dos Santos Júnior** — [GitHub](https://github.com/Marcio-VOT) · marciofsantos65@gmail.com
- **Maria Sophia Domingues dos Santos** — RM571209 · maria.sophia.domingues@gmail.com (autora da Fase 4)

> **Nota de consolidação (Fase 3):** a Fase 3 foi entregue pela equipe em [repositório próprio](https://github.com/Gcarmnonapy7/fiap-aurora-siger-fase3), em duas branches arquiteturalmente distintas (`main` e `iuri`). A versão aqui presente é uma **consolidação** feita por Iúri Leão sobre as duas — núcleo científico da branch `iuri` + colheita da branch `main` —, integrada a este portfólio. Os três autores permanecem creditados; detalhes na tabela de procedência de `fases/fase-3/relatorio.pdf`.

> **Nota de procedência (Fase 4):** a Fase 4 foi entregue pela equipe como repositório autônomo. A versão aqui presente é uma **consolidação** feita por Iúri Leão que integra o SIGIC a este portfólio, reutilizando os 13 módulos da Fase 3 como nós canônicos do grafo (`aurora_siger.operations.MODULES`, fonte única de verdade), derivando as prioridades diretamente da árvore de criticidade (Vital → 10, Sustenance → 7, Expansion → 4) e ancorando a modelagem de consumo nos 210 kW reais de geração instalada (Solar + Nuclear + Eólico). Nesta fase não há notebook — a entrega é o executável `sigic` e o relatório técnico. Os quatro autores (Gabriel, Iúri, Márcio e Maria Sophia) permanecem creditados; detalhes em `fases/fase-4/relatorio.pdf`.

---

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
