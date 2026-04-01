# Aurora SIGER

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/iurileao-hub/FIAP-Aurora-Siger/blob/main/fases/fase-1/notebook.ipynb)

Sistema Inteligente de Gerenciamento de Riscos para telemetria pré-decolagem de espaçonaves. O Aurora SIGER simula um pipeline completo de decisão Go/No-Go, combinando validação de sensores por regras, detecção de anomalias com Isolation Forest (implementado do zero) e análise energética — tudo integrado em um único fluxo de três etapas que determina se é seguro decolar.

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

## Arquitetura

O pipeline de decisão de lançamento opera em três estágios sequenciais. Se qualquer estágio falhar, o lançamento é abortado imediatamente:

1. **Validação de telemetria** -- cada leitura dos 7 sensores é comparada com sua faixa segura via regras determinísticas (`Validator`).
2. **Verificação por IA** -- um modelo Isolation Forest analisa o conjunto de leituras e calcula um anomaly score. Se o score ultrapassar o limiar, a anomalia é detectada mesmo que cada sensor individualmente esteja dentro da faixa.
3. **Análise energética** -- calcula a autonomia restante das baterias considerando capacidade, perdas e consumo orbital. A carga deve ser >= 95% para aprovação Go/No-Go.

---

## Roadmap

O projeto Aurora SIGER será desenvolvido ao longo de **7 fases** durante o ano letivo de 2026, cada fase adicionando novas capacidades ao sistema. Esta entrega corresponde à **Fase 1**.

---

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
