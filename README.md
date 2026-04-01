# Aurora SIGER

**Sistema Inteligente de Gerenciamento de Riscos**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/iurileao-hub/FIAP-Aurora-Siger/blob/main/fases/fase-1/notebook.ipynb)

> Projeto desenvolvido como atividade integradora do primeiro ano do curso de **Ciência da Computação (online)** na **FIAP — 2026**. O repositório acompanhará todas as **7 fases** do projeto ao longo do ano letivo, cada fase adicionando novas capacidades ao sistema.

## O que é o Aurora SIGER?

Imagine que você faz parte da equipe de controle de missão de um foguete. Segundos antes da decolagem, dezenas de sensores transmitem dados em tempo real: temperatura da cabine, pressão dos tanques, vibração dos motores, carga das baterias... **Como saber se é seguro decolar?**

O Aurora SIGER responde a essa pergunta simulando um pipeline completo de decisão **Go/No-Go** em três etapas:

1. **Validação de telemetria** — cada sensor é comparado com sua faixa segura por regras determinísticas.
2. **Verificação por IA** — um modelo Isolation Forest (implementado do zero) analisa combinações de valores para detectar anomalias sutis que passariam despercebidas sensor a sensor.
3. **Análise energética** — calcula se a carga das baterias é suficiente para cobrir o lançamento e manter a nave em órbita.

Somente se as três etapas forem aprovadas, o sistema emite: **"PRONTO PARA DECOLAR"**.

---

## Quick start

```bash
# Clone o repositório
git clone https://github.com/iurileao-hub/FIAP-Aurora-Siger.git
cd FIAP-Aurora-Siger

# Instale o pacote (com dependências de desenvolvimento e visualização)
pip install -e ".[dev,viz]"

# Execute o notebook
jupyter notebook fases/fase-1/notebook.ipynb
```

---

## Estrutura do projeto

```
FIAP-Aurora-Siger/
├── pyproject.toml
├── README.md
├── LICENSE
├── aurora_siger/           # Pacote Python principal
│   ├── data/generation.py
│   ├── eda/plots.py
│   ├── models/isolation_forest.py
│   └── pipeline/
│       ├── validator.py
│       └── launch.py
├── tests/
│   ├── test_generation.py
│   ├── test_isolation_forest.py
│   └── test_validator.py
├── fases/
│   └── fase-1/
│       ├── notebook.ipynb
│       └── assets/
└── docs/
    └── fase-1/
        ├── pseudocodigo.md
        ├── fluxograma.md
        ├── energia.md
        └── etica.md
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

---

## Faixas seguras de telemetria

| Sensor | Faixa segura | Condição de aborto |
|--------|-------------|--------------------|
| `internal_temp` | 18 -- 26 °C | Fora da faixa |
| `external_temp` | -65 -- 125 °C | Fora da faixa |
| `structural_integrity` | 1 (íntegro) | != 1 |
| `energy` | 60 -- 100 % | < 60 % |
| `vibration` | 0.1 -- 0.5 g | Fora da faixa |
| `tank_pressure` | 270 -- 340 atm | Fora da faixa |
| `critical_modules` | 1 (ativo) | != 1 |

---

## Roadmap

O Aurora SIGER será desenvolvido ao longo de **7 fases** durante o ano letivo de 2026. Cada fase adiciona novas capacidades ao sistema, e o pacote `aurora_siger` cresce de forma incremental.

| Fase | Tema | Status |
|------|------|--------|
| **1** | Telemetria, Isolation Forest, pipeline Go/No-Go | Concluída |
| **2** | *Em breve* | — |
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
