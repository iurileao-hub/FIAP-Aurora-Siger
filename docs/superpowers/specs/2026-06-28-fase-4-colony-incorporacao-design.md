# Fase 4 — Incorporação do SIGIC ao monorepo (`colony/`)

**Data:** 2026-06-28
**Autor da consolidação:** Iúri Leão de Almeida
**Origem:** entrega standalone da equipe — repositório `fiap-aurora-siger-fase4`
**Equipe (4):** Gabriel Carmona Bittencourt (RM569239), Márcio Francisco dos Santos Junior (RM570758), Iúri Leão de Almeida (RM570215), Maria Sophia Domingues dos Santos (RM571209)

---

## 1. Contexto e objetivo

A **Fase 4** da Atividade Integradora (FIAP) é o **SIGIC — Sistema Inteligente de Gerenciamento
da Infraestrutura da Colônia**: representa a infraestrutura da Aurora Siger como um **grafo
ponderado** e oferece algoritmos de rede (BFS, DFS, Dijkstra), análise de rede (pontos de
articulação, centralidade, eficiência), modelagem matemática com cálculo diferencial e uma
reflexão de sustentabilidade/governança (ESG). Foi entregue como app de terminal em Python puro
(stdlib), com estrutura própria (`codigo_fonte.py` + `modules/ algorithms/ modeling/ data/ ui/
visualization/`), PDFs obrigatórios e link de vídeo.

**Objetivo desta incorporação:** trazer a Fase 4 para o monorepo `FIAP-Aurora-Siger` como a
**casa canônica**, refatorada para a convenção do pacote `aurora_siger/` — e, diferentemente das
fases anteriores, com **continuidade narrativa real no código**: o grafo da colônia passa a usar
os **13 módulos da Fase 3** (`aurora_siger/operations/modules.py`) como nós. A entrega standalone
permanece **intacta** (é o artefato que a FIAP corrige); o monorepo é a consolidação de engenharia.

### Decisões já tomadas com Iúri (brainstorming 2026-06-28)

1. **Papel:** casa canônica (refator pro pacote), não arquivo fiel.
2. **Profundidade:** abordagem **C** — refator pro padrão do pacote **+ continuidade real no código**.
3. **Continuidade:** a Fase 4 **usa os módulos da Fase 3 como nós do grafo** (fonte única de verdade).
4. **Idioma:** **nomes EN no código** (convenção do pacote), **rótulos PT na CLI** (apresentação).
5. **Notebook:** **não** — só o app CLI (`sigic`), fiel à natureza da Fase 4 (o enunciado exige menu de terminal).

---

## 2. Precedente: consolidação da Fase 3

O README já documenta que a Fase 3 veio de um repo standalone da equipe e foi **consolidada** por
Iúri, com **nota de procedência** e créditos preservados. A Fase 4 segue o mesmo padrão de
atribuição: nota de procedência no README + 4 autores no `pyproject.toml` (a Fase 4 adiciona a 4ª
integrante, Maria Sophia Domingues).

A diferença: a Fase 3 consolidou **duas branches** de uma mesma base. A Fase 4 **reconcilia dois
modelos de domínio diferentes** (o grafo de 10 módulos PT da entrega vs. os 13 módulos EN da
operação), o que é mais invasivo e merece o detalhamento da Seção 4.

---

## 3. Arquitetura — pacote `aurora_siger/colony/`

Novo domínio espelhando `landing/` (Fase 2) e `operations/` (Fase 3). É a **camada de topologia/
rede** sobre a colônia que já opera na Fase 3.

```
aurora_siger/colony/
├── __init__.py       # docstring de fase + (opcional) reexports
├── graph.py          # InfrastructureGraph: lista + matriz de adjacência. Domínio puro.
├── roster.py         # build_nodes(): deriva os nós do grafo de operations.MODULES (continuidade)
├── topology.py       # overlay da Fase 4: posições + arestas ponderadas + tipos sobre os 13 módulos
├── search.py         # BFS, DFS, componentes conexos — retornam dados, sem print
├── paths.py          # Dijkstra (mínimo, restrição de prioridade, todos-destinos) — sem print
├── analysis.py       # eficiência, pontos de articulação (Tarjan), centralidade, clustering
├── modeling.py       # modelagem matemática + cálculo diferencial (lê consumo do roster)
└── cli.py            # menu SIGIC — TODO o I/O (print/input) + PT_LABELS → entrypoint `sigic`
```

**Princípio diretor (igual a `landing/`/`operations/`):** o domínio é **puro e sem I/O**. Funções
recebem dados e devolvem dados (listas, dicts, tuplas); `cli.py` é a única camada que imprime e lê
do usuário. Isso torna todo o domínio testável por igualdade de valores.

### Entregáveis e metadados

- `pyproject.toml`: adicionar `sigic = "aurora_siger.colony.cli:main"` em `[project.scripts]`;
  bump de versão `0.3.0 → 0.4.0`; adicionar a 4ª autora à lista de `authors`.
- `aurora_siger/__init__.py`: `__version__ = "0.4.0"`.
- `fases/fase-4/`:
  - `sigic.py` — wrapper ≈20 linhas sobre `aurora_siger.colony.cli:main` (espelha `mgpeb.py`/`aurora_core.py`).
  - `relatorio.md` + `relatorio.pdf` — relatório técnico (regenerado para os 13 nós; ver §8).
  - `figuras/gerar_rede.py` — gerador Graphviz do diagrama (porte de `arquivos_auxiliares/gerar_rede_pdf.py`).
  - `figuras/rede_colonia.pdf` + `.dot` — diagrama dos **13 nós** (regenerado).
  - `enunciado.md` — cópia do enunciado oficial.
  - `README.md` — visão da fase + como rodar.
- `docs/fase-4/` — ensaio textual: "Da operação à topologia — a colônia como rede".
- `tests/test_colony_*.py` — suíte completa (§7).

---

## 4. Reconciliação dos módulos (coração da continuidade)

`operations.MODULES` (13, EN, dicts) vira a **fonte única de verdade** dos nós. O pacote `colony/`
**lê** a Fase 3 e **nunca a modifica** (protege os 276 testes existentes). `roster.build_nodes()`
deriva cada nó do grafo assim:

| Atributo do nó (grafo) | Origem |
|---|---|
| `id` (int 1–13), `name` (EN), `type` | direto de `operations.MODULES` |
| `consumption` (kW) | `consumption_by_mode["adequate"]` |
| `priority` (1–10) | **derivado da árvore de criticidade** (`operations.hierarchies.build_criticality_tree`): Vital → 9–10, Sustenance → 6–8, Expansion → 4–5 (valores exatos por módulo definidos no plano) |
| `position` (x, y) | overlay novo em `topology.py` |
| arestas + pesos + tipo | overlay novo em `topology.py` |
| `communication_need` | overlay novo em `topology.py` (atributo de rede, inexistente na Fase 3) |

### 4.1 Prioridade a partir da criticidade

A Fase 3 não tem prioridade numérica, mas tem **tiers de criticidade** (`Vital`, `Sustenance`,
`Expansion`) — semanticamente a prioridade que o grafo precisa. Mapa proposto:

- **Vital** (Command and Control, Life Support/ECLSS, Medical Support, Habitat) → prioridade **9–10**.
- **Sustenance** (Solar/Nuclear/Wind Power, Food Production, Communications, ISRU) → prioridade **6–8**.
- **Expansion** (Logistics and Storage, Workshop and Maintenance, Science Lab) → prioridade **4–5**.

A função lê o tier de cada módulo a partir do `build_criticality_tree()` (fonte única), evitando
uma segunda tabela de prioridade que poderia divergir.

### 4.2 Topologia (arestas) reprojetada sobre os 13 nós

A topologia antiga (arestas entre HAB-01, CTR-01…) **não casa 1:1** com os 13 módulos. `topology.py`
define um conjunto **novo e explícito** de arestas ponderadas sobre os ids 1–13, reaproveitando a
intenção das conexões da entrega onde há correspondência e adicionando as conexões dos módulos novos
(geradores, ISRU). Critério das conexões (a justificar no relatório, exigência do enunciado §1.2):

- **Energia:** geradores (Solar #4, Nuclear #5, Wind #13) → consumidores críticos (Command #1,
  ECLSS #2, Habitat #3, Medical #7); peso ∝ "distância"/perda.
- **Dados/comunicação:** Command and Control #1 como hub de dados → Communications #6, Science Lab #12.
- **Suporte à vida:** ECLSS #2 ↔ Habitat #3 ↔ Medical #7.
- **Operações:** Logistics #9, Workshop #11, ISRU #10 ligados a Food #8 e aos geradores.

> O conjunto exato de arestas (pares + pesos + tipo) será proposto como **tabela revisável** no
> plano de implementação, antes de virar código. Meta: grafo **conexo**, com pelo menos um **ponto
> de articulação real** para a detecção (Seção 5) ter caso positivo na rede principal — ou, se a
> rede ficar robusta de propósito, manter a demo didática da ponte (`_build_demo_bridge_graph`).

### 4.3 Idioma: EN no código, PT na apresentação

`roster`/`graph`/algoritmos usam os nomes EN canônicos (`"Command and Control"`). O `cli.py`
mantém um dict de apresentação `PT_LABELS: dict[int, str]` (id → nome PT, ex.: `1: "Centro de
Controle"`) usado **só na renderização**. O domínio nunca vê português. Os tipos de aresta também
têm rótulos PT só na CLI.

---

## 5. Algoritmos — refator para domínio puro

Comportamento preservado; I/O removido. Mudanças por arquivo:

- **`paths.py` (Dijkstra)** — remove `verbose`/`print`. `find_path(origin, dest) -> (path, distance)`.
  O trace passo-a-passo vira **dado**: `find_path(..., trace=True) -> (path, distance, steps)` onde
  `steps` é uma lista de tuplas (módulo, distância) que a CLI renderiza. `find_path_with_constraints`
  retorna `(path, distance, skipped)` (lista dos ignorados por prioridade). `find_all_paths` retorna
  o dict atual.
- **`search.py`** — `bfs(start, target=None) -> {"levels": {id: nível}, "paths": {id: [ids]},
  "order_by_level": [[ids]]}`. `dfs(start, target=None) -> {"order": [...], "path": [...]}`.
  `connected_components() -> [[ids]]`. Sem print.
- **`analysis.py`** — já retorna dicts; só tipagem + EN. **Melhoria:** trocar a betweenness baseada
  em `_find_simple_paths` (enumeração de **todos** os caminhos simples — risco de explosão
  combinatória num grafo de 13 nós mais denso) por **betweenness sobre caminhos mínimos**
  (acumulação tipo Brandes via Dijkstra). Mais correto e sem risco de custo exponencial. Tarjan de
  pontos de articulação e clustering ficam como estão (corretos).
- A **demo didática** `_build_demo_bridge_graph` migra para o `cli.py` (é apresentação) e continua
  provando o caso positivo de articulação.

---

## 6. Modelagem matemática — refator

`modeling.py` puro, lendo consumo do roster. Constantes ancoradas na Fase 3:

- `C0` = soma do consumo `adequate` dos 13 módulos = **80,5 kW** (substitui a soma dos 10 módulos PT).
- `GENERATION_CAPACITY` = **geração real instalada da Fase 3** = Solar 100 + Nuclear 80 + Wind 30 =
  **210 kW** (substitui o valor inventado `2000`). Derivado de `operations.MODULES` (`max_capacity_kw`
  dos geradores), não hard-coded, para não divergir.

Preserva-se todo o cálculo: `C(t)=C0·e^{rt}`, derivadas numéricas (diferença central), 2ª derivada,
otimização por ponto crítico/extremos, perda energética `1−e^{−d(1−η)}`, eficiência de distribuição,
cenários (otimista/moderado/pessimista), previsão de crescimento, custo-benefício. Os `print` de
`complete_analysis()` vão para a CLI.

**Consequência numérica (verificada):** a 12%/ano, o consumo (80,5 kW) atinge 90% da geração
(189 kW) em **~7,1 anos** — narrativa coerente e ancorada em dados reais, melhor que a projeção
atual contra 2000 kW (que nunca satura num horizonte plausível). Os números exatos das telas serão
reconferidos na implementação.

---

## 7. Testes (`tests/test_colony_*.py`)

Domínio puro ⇒ testes por igualdade de valores. Cobertura mínima:

- `test_colony_roster.py` — 13 nós derivados; prioridade correta por tier de criticidade
  (Vital→9/10, etc.); consumo = modo `adequate`; capacidade de geração derivada = 210 kW.
- `test_colony_topology.py` — grafo conexo; simetria das arestas (não-direcionado); pesos positivos;
  matriz de adjacência coerente com a lista.
- `test_colony_graph.py` — add/get módulos e conexões; matriz vs. lista; `get_weight` simétrico.
- `test_colony_paths.py` — Dijkstra correto em topologia conhecida; caminho com restrição de
  prioridade ignora nós abaixo do limiar; todos-destinos ordenado.
- `test_colony_search.py` — níveis de BFS; ordem de DFS; componentes conexos.
- `test_colony_analysis.py` — pontos de articulação no grafo-ponte (caso positivo); betweenness
  Brandes ≥ 0 e coerente; clustering em [0,1].
- `test_colony_modeling.py` — `C(t)` exponencial; derivada ≈ `r·C(t)`; perda cresce com distância;
  ponto crítico ~7 anos; determinismo (mesma entrada → mesma saída).
- `test_colony_cli.py` — smoke: o menu instancia e o `PT_LABELS` cobre os 13 ids.
- **`test_colony_parity.py`** — *fixture* reproduzindo a topologia original de **10 nós PT** da
  entrega; prova que os algoritmos refatorados batem os exemplos do README entregue
  (ARM→MED = 4.0; níveis de BFS a partir do Centro de Controle). Garante que o **refator preservou
  a semântica** enquanto os **dados evoluíram** para os 13 nós.

Meta: manter `pytest` verde (276 testes da Fase 3 intactos + novos da Fase 4).

---

## 8. Documentação, README e procedência

- **`README.md`** (raiz):
  - Nova subseção da arquitetura: `colony/` (Fase 4 — topologia/rede da colônia).
  - Seção "Entregáveis da Fase 4" (tabela 4.x apontando para `fases/fase-4/...`).
  - Atualizar o **Roadmap** (Fase 4 concluída).
  - **Nota de procedência da Fase 4** (espelha a da Fase 3): entrega standalone da equipe →
    consolidação por Iúri, 4 autores creditados, **com continuidade explícita** declarada (o grafo
    usa os 13 módulos da Fase 3).
  - Sem badge de Colab (não há notebook nesta fase).
- **`CLAUDE.md`** — seguir o próprio checklist "Como adicionar uma nova fase":
  estado/versão (`0.4.0`, fases 1–4 concluídas); Setup (contagem de testes + `python3 fases/fase-4/sigic.py`
  e `sigic`); árvore de Arquitetura (+`colony/`); nova seção **"Decisões de design — fase 4"**
  documentando: continuidade via `operations.MODULES`, prioridade derivada da criticidade, idioma
  EN-código/PT-CLI, betweenness Brandes, `GENERATION_CAPACITY` derivado dos geradores reais.
- **`docs/fase-4/`** — ensaio textual da fase.
- **PDFs** (`relatorio.pdf`, `rede_colonia.pdf`) — **regenerados** para os 13 nós (pandoc/xelatex e
  Graphviz). Marcado como tarefa explícita: o PDF antigo (10 nós PT) **não** é reaproveitado.

---

## 9. Não-objetivos (YAGNI / fora de escopo)

- **Não modificar** `aurora_siger/operations/` nem a representação dos módulos da Fase 3 (a Fase 4
  só lê).
- **Não criar notebook** para a Fase 4.
- **Não tocar** na entrega standalone (`fiap-aurora-siger-fase4`) — é o artefato avaliado.
- **Não introduzir dependências** — domínio em stdlib pura (`math`, `heapq`, `collections`), como
  `landing/` e `operations/`.
- **Não reescrever** os algoritmos corretos (Tarjan, Dijkstra, clustering); só remover I/O e trocar
  a betweenness exponencial.

---

## 10. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Refator quebrar a semântica dos algoritmos | `test_colony_parity.py` valida contra os exemplos do README entregue |
| Acoplar com `operations/` quebrar os 276 testes | `colony/` só **lê** a Fase 3; CI roda a suíte inteira |
| Topologia nova ficar desconexa ou sem ponto de articulação | revisar a tabela de arestas no plano; manter demo da ponte |
| Números da modelagem ficarem incoerentes com a narrativa | sanity já feito (~7,1 anos); reconferir telas na implementação |
| Mistura de ids int (Fase 3) com chaves de aresta string | `graph._get_edge_key` usa `min/max` — funciona com int; cobrir em teste |

---

## 11. Sequência de implementação (resumo; detalhe no plano)

1. `colony/graph.py` + `colony/roster.py` + `colony/topology.py` (domínio de dados) + testes.
2. `colony/search.py` + `colony/paths.py` (algoritmos puros) + testes (incl. paridade).
3. `colony/analysis.py` (com betweenness Brandes) + testes.
4. `colony/modeling.py` (ancorado em 210 kW) + testes.
5. `colony/cli.py` (menu + PT_LABELS + demo da ponte) + smoke; `pyproject` script `sigic`.
6. `fases/fase-4/` (wrapper, enunciado, figuras/gerador, README); regenerar diagrama.
7. Relatório `fases/fase-4/relatorio.md` → PDF; ensaio `docs/fase-4/`.
8. README (entregáveis + roadmap + procedência) + CLAUDE.md (checklist de nova fase) + bump 0.4.0 + 4ª autora.
9. `pytest` verde ponta-a-ponta; revisão final.
