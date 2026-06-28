# Fase 4 — SIGIC: Rede de Infraestrutura da Colônia

**A rede que operou na Fase 3 agora é gerenciada como grafo.**

Esta fase apresenta o **SIGIC** (Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia), uma interface terminal (TUI) que expõe os mesmos 13 módulos da Fase 3 como um grafo com pesos e tipos de conexão, permitindo consulta, análise e simulação da rede da colônia Aurora Siger.

## O que demonstra

- **Grafo com atributos reais** — 13 nós derivados diretamente do roster da Fase 3 (nome, tipo, consumo, prioridade) complementados pela topologia da Fase 4 (posições 2D, capacidade de armazenamento, necessidade de comunicação, arestas com peso e tipo).
- **Busca BFS e DFS** — travessias com localização de alvo e caminhos por nível/profundidade, implementadas à mão sobre lista de adjacência.
- **Dijkstra em três variantes** — caminho mínimo simples, caminho com restrição de prioridade mínima e todos os caminhos mínimos a partir de uma origem.
- **Análise de centralidade e pontos críticos** — grau, intermediação (Brandes) e pontos de articulação (Tarjan), com demonstração didática de uma rede-ponte.
- **Modelagem matemática** — projeção de consumo exponencial, perda energética por distância, custo-benefício e simulações de crescimento ancoradas em 210 kW gerados (Fase 3).
- **Diagrama Graphviz** — `figuras/rede_colonia.pdf` gerado por `gerar_rede.py`: cores laranja/azul/vermelho codificam tipos energia/dados/suporte-de-vida; posições fixas refletem o layout da colônia.

A continuidade com a Fase 3 é estrutural: os 13 módulos são os mesmos, a prioridade de cada nó é derivada da árvore de criticidade (Vital ≥ 8, Sustenance = 7, Expansion = 4), e a geração de 210 kW ancora os cálculos de consumo e eficiência.

## Como rodar

```bash
# Após instalar o pacote na raiz do repo:
pip install -e .
sigic                              # entrypoint registrado

# Sem instalar — execução direta:
python3 fases/fase-4/sigic.py
```

Sem dependências externas além da stdlib: o grafo, as buscas e a modelagem são implementações puras; a TUI usa apenas `os` e `subprocess` (para limpar a tela).

## Mapa do menu

| Opção | Tela | Algoritmo / conteúdo |
|-------|------|-----------------------|
| 1 | Visualizar Rede | Lista de adjacência + estatísticas |
| 2 | Consultar Módulo | Detalhes + eficiência de distribuição |
| 3 | Algoritmos de Rede | BFS, DFS, Dijkstra (3 variantes), centralidade, pontos críticos, componentes |
| 4 | Modelagem Matemática | Projeção consumo, perdas, custo-benefício, derivadas, otimização, cenários |
| 5 | Sustentabilidade e Governança | Margem de segurança, recomendações ESG |
| 6 | Simulações Operacionais | Falha de módulo, pico de consumo, expansão, otimização |
| 7 | Análise Completa | Resumo integrado: rede + criticidade + consumo + recomendações |
| 8 | Sobre o Sistema | Versão 0.4.0, disciplinas integradas |
| 9 | Matriz de Adjacência | Visão matricial complementar à lista |
| 0 | Sair | — |

## Diagrama da rede

O arquivo `figuras/rede_colonia.pdf` é gerado por:

```bash
python3 fases/fase-4/figuras/gerar_rede.py
```

Requer o Graphviz instalado (`sudo apt install graphviz`). O script lê o grafo canônico via `topology.build_graph()`, usa os rótulos em português de `cli.PT_LABELS` e grava `rede_colonia.dot` + `rede_colonia.pdf` na mesma pasta.

## Entregáveis desta pasta

| Arquivo | O que é |
|---------|---------|
| `sigic.py` | Entrypoint do SIGIC TUI — *thin wrapper* sobre `aurora_siger.colony.cli` |
| `enunciado.md` | Enunciado oficial da Fase 4 (FIAP) |
| `figuras/gerar_rede.py` | Gerador do diagrama Graphviz (lê o grafo canônico) |
| `figuras/rede_colonia.dot` | Fonte DOT gerada (13 nós, 20 arestas, layout neato) |
| `figuras/rede_colonia.pdf` | Diagrama renderizado — laranja=energia, azul=dados, vermelho=suporte-de-vida |

A lógica de negócio vive inteiramente em `aurora_siger/colony/` (graph, roster, topology, search, paths, analysis, modeling, cli). Esta pasta contém apenas ponto de entrada e artefatos de apresentação.

## Continuidade com as fases anteriores

| Fase | Contribuição para a Fase 4 |
|------|---------------------------|
| Fase 2 (MGPEB) | Padrão de wrapper `python3 fases/N/entrypoint.py` |
| Fase 3 (Operação) | 13 módulos (roster), criticidade, consumos, 210 kW de geração |
| Fase 4 (Rede) | Topologia (posições, arestas, tipos), algoritmos de grafo, modelagem |

## Equipe da entrega FIAP

| Nome | RM | E-mail |
|------|----|--------|
| Gabriel Carmona Bittencourt | RM569239 | gabrielcarmonabittencourtpy@gmail.com |
| Iúri Leão de Almeida | RM570215 | iurileao@gmail.com |
| Márcio Francisco dos Santos Júnior | RM570758 | marciofsantos65@gmail.com |

## Licença

[MIT](../../LICENSE)
