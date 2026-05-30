# Fase 3 — Operação Energética da Colônia

**A colônia que pousou na Fase 2 agora opera.**

Esta fase simula a **operação energética** da colônia Aurora Siger ao longo de 7 sóis marcianos (168 horas), passo a passo de uma hora. O sistema gera energia (solar, eólica, nuclear), consome-a (carga base por modo de operação somada a um termo térmico físico), armazena o saldo em bateria e **decide** continuamente como distribuir potência escassa. A contribuição conceitual da fase é a transição de um controle puramente **reativo** (cortar carga depois que falta energia) para um controle **preditivo** (antecipar a queda via regressão e agir antes), preservando o reativo como rede de segurança.

## O que demonstra

- **Organização hierárquica** — duas árvores N-árias (`Node` genérico) sobre os mesmos 13 módulos: uma **funcional** (Energy, Life Support, Command, Operations) e uma de **criticidade** (Vital → Sustenance → Expansion). A de criticidade guia o corte de carga, e **Vital nunca desliga** *(item 1.1)*.
- **Regras de decisão inspecionáveis** — `evaluate_rules()` é uma função pura que devolve ações legíveis ("ATIVAR MODO ECONOMIA", "EMERGÊNCIA ENERGÉTICA"); o nível de energia `CRITICAL → SURPLUS` é o rótulo de saída, computado de `bateria% + slope OLS` *(item 1.2)*.
- **Previsão por regressão** — mínimos quadrados de **forma fechada implementados à mão** (sem numpy/sklearn), com dois usos: prever a geração eólica a partir do vento e estimar o *slope* da tendência energética para antecipar quedas *(item 1.3)*.
- **Análise energética** — balanço geração × consumo, agregação por sol, *breakdown* por fonte e identificação dos momentos críticos da missão *(item 1.4)*.
- **Determinismo de projeto** — toda a aleatoriedade (clima e falhas) passa por um único gerador congruencial linear (LCG) *seed-aware*: a mesma seed reproduz a história hora a hora, bit-a-bit.
- **Controle de carga em duas camadas** — `power_factor` contínuo (preventivo, suave) compõe com *load shedding* em 4 estágios (estrutural, rede de segurança), sem dupla-contagem.

A arquitetura e o argumento por trás dessas escolhas — incluindo a **consolidação de duas branches** da equipe — estão no relatório (`relatorio.pdf`) e no ensaio em [`docs/fase-3/`](../../docs/fase-3/).

## Como rodar

Há duas maneiras de explorar o sistema:

```bash
# 1. Notebook interativo — narrativa dos 4 itens + matplotlib (run_simulation headless)
jupyter notebook fases/fase-3/notebook.ipynb

# 2. Dashboard TUI ao vivo — 6 abas (Visão Geral, Energia, Sensores, Módulos, Eventos, Hierarquia)
aurora                              # após `pip install -e .` na raiz do repo
python3 fases/fase-3/aurora_core.py # alternativa sem instalar o pacote
```

O CLI não tem dependências externas (usa só `math` e `random`/LCG da stdlib — a regressão OLS é escrita à mão). O notebook usa `matplotlib`, instalado via `pip install -e ".[viz]"` na raiz do repositório.

## Entregáveis desta pasta

| Arquivo | O que é |
|---------|---------|
| `notebook.ipynb` | Narrativa demonstrativa dos quatro itens do enunciado a partir de `run_simulation(seed=42)`, com gráficos do balanço energético |
| `aurora_core.py` | Entrypoint do dashboard TUI — *thin wrapper* sobre `aurora_siger.operations.cli` |
| `relatorio.md` / `relatorio.pdf` | Relatório técnico final da entrega FIAP, em fonte Markdown e PDF renderizado |
| `figuras/header.tex` | Cabeçalho LaTeX (XeLaTeX) usado na compilação do PDF |

Diferente da Fase 2, as figuras do relatório são geradas **dentro do notebook** — não há script `gerar_graficos.py` nem diagramas GraphViz nesta pasta. O ensaio reflexivo (Seção 7 do relatório) vive em [`../../docs/fase-3/`](../../docs/fase-3/), seguindo a convenção do projeto: textos em `docs/`, código em `aurora_siger/`, demonstração em `fases/`.

## Reproduzindo o PDF do relatório

Requisitos: [Pandoc](https://pandoc.org/) e uma distribuição LaTeX com `xelatex` (ex.: [BasicTeX](https://tug.org/mactex/morepackages.html)).

```bash
pandoc relatorio.md -o relatorio.pdf \
  --pdf-engine=xelatex \
  -V mainfont=Arial \
  -V fontsize=10pt \
  -V geometry=a4paper,margin=2cm \
  -V linestretch=1.15 \
  --include-in-header=figuras/header.tex
```

## Equipe da entrega FIAP

A Fase 3 foi desenvolvida pela equipe em [repositório próprio](https://github.com/Gcarmnonapy7/fiap-aurora-siger-fase3), em duas branches arquiteturalmente distintas (`main` e `iuri`). Esta versão é uma **consolidação** feita por Iúri Leão sobre as duas — núcleo científico da branch `iuri` + colheita da branch `main`. Os três autores permanecem creditados (procedência detalhada no `relatorio.pdf`):

| Nome | RM | E-mail |
|------|----|--------|
| Gabriel Carmona Bittencourt | RM569239 | gabrielcarmonabittencourtpy@gmail.com |
| Iúri Leão de Almeida | RM570215 | iurileao@gmail.com |
| Márcio Francisco dos Santos Júnior | RM570758 | marciofsantos65@gmail.com |

## Licença

[MIT](../../LICENSE)
