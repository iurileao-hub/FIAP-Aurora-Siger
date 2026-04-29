# Aurora SIGER

**Sistema Inteligente de Gerenciamento de Riscos**

[![Fase 1 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/iurileao-hub/FIAP-Aurora-Siger/blob/main/fases/fase-1/notebook.ipynb)
[![Fase 2 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/iurileao-hub/FIAP-Aurora-Siger/blob/main/fases/fase-2/notebook.ipynb)

> Projeto desenvolvido como atividade integradora do primeiro ano do curso de **Ciência da Computação (online)** na **FIAP — 2026**. O repositório acompanha todas as **7 fases** do projeto ao longo do ano letivo, cada fase adicionando novas capacidades ao sistema.

## O que é o Aurora SIGER?

Imagine que você faz parte da equipe de controle de missão de uma colônia espacial. A cada operação crítica — uma decolagem na Terra, um pouso em outro planeta — dezenas de sensores transmitem dados em tempo real e dezenas de regras precisam ser verificadas em segundos. **Como decidir se é seguro prosseguir?**

O Aurora SIGER responde a essa pergunta com um pipeline de decisão **Go/No-Go** que evolui ao longo das fases:

- **Fase 1 — Decolagem (telemetria):** validação determinística de 7 sensores, detecção de anomalias com Isolation Forest implementado do zero e análise energética orbital. Resultado: **"PRONTO PARA DECOLAR"** ou aborto justificado.
- **Fase 2 — Pouso (MGPEB):** organização da fila de pouso de 12 módulos da colônia Aurora Siger em Marte, autorização por expressão booleana inspecionável `F ∧ A ∧ (L ∨ E) ∧ S` e registro auditável de cada bloqueio. Resultado: **"AUTORIZADO PARA POUSO"** ou bloqueio rastreável.

Em ambas as fases, a ênfase é a mesma: decisões automatizadas em sistemas críticos precisam ser **inspecionáveis** — tabela-verdade aberta, faixas seguras documentadas, histórico empilhado.

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
│   └── landing/                  # Fase 2 — pouso e estabilização (MGPEB)
│       ├── module.py
│       ├── structures.py
│       ├── authorization.py
│       ├── physics.py
│       ├── mission.py
│       └── cli.py
├── tests/                        # pytest acompanha o pacote
├── fases/
│   ├── fase-1/
│   │   ├── notebook.ipynb
│   │   └── assets/
│   └── fase-2/
│       ├── notebook.ipynb
│       ├── mgpeb.py              # entrypoint CLI fino sobre aurora_siger.landing
│       ├── relatorio.md / .pdf   # relatório técnico da entrega FIAP
│       └── figuras/
└── docs/
    ├── fase-1/
    │   ├── pseudocodigo.md / fluxograma.md / energia.md / etica.md
    └── fase-2/
        ├── contextualizacao-historica.md
        └── esg.md
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
| **3** | *Em breve* | — |
| **4** | *Em breve* | — |
| **5** | *Em breve* | — |
| **6** | *Em breve* | — |
| **7** | *Em breve* | — |

---

## Autores

Projeto desenvolvido por alunos do 1.º ano de Ciência da Computação (online) — FIAP, 2026:

- **Gabriel Carmona Bittencourt** — [GitHub](https://github.com/Gcarmnonapy7) · gabrielcarmonabittencourtpy@gmail.com
- **Iúri Leão de Almeida** — [GitHub](https://github.com/iurileao-hub) · iurileao@gmail.com
- **Márcio Francisco dos Santos Júnior** — [GitHub](https://github.com/Marcio-VOT) · marciofsantos65@gmail.com

---

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
