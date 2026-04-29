# Fase 2 — MGPEB

**Módulo de Gerenciamento de Pouso e Estabilização de Base**

Esta fase entrega o sistema responsável por organizar o pouso dos doze módulos pré-fabricados que constituem a primeira colônia humana em Marte — a missão **Aurora Siger**. A coordenação manual seria inviável: o atraso de comunicação entre Terra e Marte varia de 4 a 24 minutos por sentido, e a fase de pouso dura poucos minutos. O MGPEB resolve isso com três funções complementares — organizar a fila, decidir caso a caso, registrar cada decisão.

## O que demonstra

- **Estruturas de dados lineares** — `Vector`, `Queue` (FIFO) e `Stack` (LIFO) implementadas do zero, com ordenação Bubble/Selection e busca linear.
- **Lógica booleana inspecionável** — a regra de autorização `F ∧ A ∧ (L ∨ E) ∧ S` combina cinco variáveis (combustível, atmosfera, zona livre, emergência, sensores) e pode ser auditada por tabela-verdade.
- **Funções matemáticas aplicadas** — quatro modelos físicos do pouso: altitude (queda livre), consumo de combustível (exponencial), energia solar (parábola invertida) e temperatura superficial (senoidal).
- **Rastreabilidade** — toda decisão de bloqueio é empilhada com motivo e horário em uma `alert_stack` consultável.

A arquitetura e o argumento por trás dessas escolhas estão no relatório (`relatorio.pdf`) e nos ensaios em [`docs/fase-2/`](../../docs/fase-2/).

## Como rodar

Há duas maneiras de explorar o sistema:

```bash
# 1. Notebook interativo — narrativa + matplotlib + cenários comparados
jupyter notebook fases/fase-2/notebook.ipynb

# 2. Protótipo CLI — menu interativo com todas as operações
python3 fases/fase-2/mgpeb.py
```

O CLI não tem dependências externas (usa só `math` e `random` da stdlib). O notebook usa `matplotlib`, instalado via `pip install -e ".[viz]"` na raiz do repositório.

## Entregáveis desta pasta

| Arquivo | O que é |
|---------|---------|
| `notebook.ipynb` | Narrativa demonstrativa com cenários (atmosfera ruim, frota com pouco combustível, todos críticos) e gráficos das funções físicas |
| `mgpeb.py` | Protótipo CLI executável — *thin wrapper* sobre `aurora_siger.landing` |
| `relatorio.md` / `relatorio.pdf` | Relatório técnico final da entrega FIAP, em fonte Markdown e PDF renderizado |
| `enunciado-atividade-integradora.md` | Enunciado original da atividade |
| `figuras/` | Diagramas (`portas_logicas`, `hierarquia_estruturas`) e gráficos das funções físicas, com o script `gerar_graficos.py` que os reproduz |

Os ensaios fonte das Seções 5 e 6 do relatório (contextualização histórica e ESG) vivem em [`../../docs/fase-2/`](../../docs/fase-2/), seguindo a convenção do projeto: textos em `docs/`, código em `aurora_siger/`, demonstração em `fases/`.

## Reproduzindo o PDF do relatório

Requisitos: [Pandoc](https://pandoc.org/), distribuição LaTeX com `xelatex` (ex.: [BasicTeX](https://tug.org/mactex/morepackages.html)), [matplotlib](https://matplotlib.org/) e [GraphViz](https://graphviz.org/).

```bash
# (opcional) regerar gráficos matplotlib das funções físicas
python3 figuras/gerar_graficos.py

# (opcional) regerar diagramas GraphViz
# obs.: portas_logicas.dot referencia gate_and.svg e gate_or.svg via image=,
# então ambos precisam estar em figuras/ no momento da renderização
dot -Tpng figuras/portas_logicas.dot       -o figuras/portas_logicas.png
dot -Tpng figuras/hierarquia_estruturas.dot -o figuras/hierarquia_estruturas.png

# compilar o PDF
pandoc relatorio.md -o relatorio.pdf \
  --pdf-engine=xelatex \
  -V mainfont=Arial \
  -V fontsize=10pt \
  -V geometry=a4paper,margin=2cm \
  -V linestretch=1.15 \
  --include-in-header=figuras/header.tex
```

## Equipe da entrega FIAP

A atividade integradora foi submetida formalmente como trabalho de equipe pela disciplina:

| Nome | RM | E-mail |
|------|----|--------|
| Gabriel Carmona Bittencourt | RM569239 | gabrielcarmonabittencourtpy@gmail.com |
| Carlos Eugênio Rodrigues de Andrade Filho | RM570285 | carloseugenioprofissional@gmail.com |
| Marcio Francisco dos Santos Junior | RM570758 | marciofsantos65@gmail.com |
| Iúri Leão de Almeida | RM570215 | iurileao@gmail.com |
| Maria Sophia Domingues dos Santos | RM571209 | maria.sophia.domingues@gmail.com |

Os autores que mantêm o software a longo prazo no repositório [Aurora SIGER](../../README.md#autores) são um subconjunto desta lista.

## Licença

[MIT](LICENSE)
