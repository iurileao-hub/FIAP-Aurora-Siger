# MGPEB — Módulo de Gerenciamento de Pouso e Estabilização de Base

Protótipo em Python e relatório técnico do sistema de gerenciamento de pouso de 12 módulos da colônia **Aurora Siger** em Marte.

Atividade Integradora da Fase 2 — Ciência da Computação, FIAP (2026).

## Entregáveis

| Arquivo | Descrição |
|---------|-----------|
| `relatorio.pdf` | Relatório técnico final em PDF |
| `mgpeb.py` | Protótipo do MGPEB em Python |
| `relatorio.md` | Fonte Markdown do relatório (renderizado em `relatorio.pdf`) |

## Estrutura do repositório

```
.
├── README.md
├── LICENSE
├── enunciado-atividade-integradora.md   # enunciado original da atividade
├── mgpeb.py                             # protótipo executável do MGPEB
├── relatorio.md                         # fonte Markdown do relatório
├── relatorio.pdf                        # PDF final renderizado
├── contextualizacao-historica.md        # texto-fonte da Seção 5 do relatório
├── esg.md                               # texto-fonte da Seção 6 do relatório
└── figuras/
    ├── portas_logicas.dot/.png          # Figura 1 — diagrama de portas lógicas
    ├── gate_and.svg, gate_or.svg        # símbolos ANSI/IEEE referenciados pelo .dot
    ├── func_altitude.png                # Figura 2a — altitude de descida
    ├── func_combustivel.png             # Figura 2b — consumo de combustível
    ├── func_solar.png                   # Figura 3a — energia solar
    ├── func_temperatura.png             # Figura 3b — temperatura superficial
    ├── hierarquia_estruturas.dot/.png   # Figura A.1 — herança UML
    ├── gerar_graficos.py                # script reproduzível dos gráficos matplotlib
    └── header.tex                       # header LaTeX para o pacote subcaption
```

## Como executar o protótipo

```bash
python3 mgpeb.py
```

Sem dependências externas — usa apenas `math` e `random` da biblioteca padrão.

## Como regerar o PDF do relatório

Requisitos: [Pandoc](https://pandoc.org/), uma distribuição LaTeX com `xelatex` (ex. [BasicTeX](https://tug.org/mactex/morepackages.html)), [matplotlib](https://matplotlib.org/) e [GraphViz](https://graphviz.org/).

```bash
# (opcional) regerar gráficos matplotlib
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

## Equipe

| Nome | RM | E-mail |
|------|----|--------|
| Gabriel Carmona Bittencourt | RM569239 | gabrielcarmabittencourtpy@gmail.com |
| Carlos Eugênio Rodrigues de Andrade Filho | RM570285 | carloseugenioprofissional@gmail.com |
| Marcio Francisco dos Santos Junior | RM570758 | marciofsantos65@gmail.com |
| Iúri Leão de Almeida | RM570215 | iurileao@gmail.com |
| Maria Sophia Domingues dos Santos | RM571209 | maria.sophia.domingues@gmail.com |

## Licença

[MIT](LICENSE)
