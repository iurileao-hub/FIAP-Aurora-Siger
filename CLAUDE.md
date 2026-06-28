# CLAUDE.md

Instruções para o Claude Code ao trabalhar neste repositório.

## Projeto

Aurora SIGER — atividade integradora da FIAP (Ciência da Computação online, 2026), desenvolvida em **7 fases** ao longo do ano. Para a visão de produto e os entregáveis por fase, ver [`README.md`](README.md). Estado atual: **fases 1, 2, 3 e 4 concluídas** (versão 0.4.0).

## Setup

```bash
pip install -e ".[dev,viz]"   # instala em modo editável
pytest                        # 314 testes (~1.2s)
python3 fases/fase-2/mgpeb.py        # CLI da fase 2 (ou `mgpeb` após install)
python3 fases/fase-3/aurora_core.py  # dashboard da fase 3 (ou `aurora` após install)
python3 fases/fase-4/sigic.py        # TUI SIGIC da fase 4 (ou `sigic` após install)
```

## Arquitetura

```
aurora_siger/                   # Pacote Python — cresce com cada fase
├── data/, eda/, models/, pipeline/   # Fase 1 — telemetria, IF, decisão Go/No-Go
├── landing/                          # Fase 2 — pouso e estabilização (MGPEB)
│   ├── module.py        # Module @dataclass + DEFAULT_MODULES
│   ├── structures.py    # Vector, Queue, Stack
│   ├── authorization.py # evaluate() puro, AuthorizationResult, Alert
│   ├── physics.py       # 4 funções físicas
│   ├── mission.py       # LandingMission (orquestrador stateful)
│   └── cli.py           # menus interativos parametrizados em LandingMission
├── operations/                       # Fase 3 — operação energética da colônia
│   ├── constants.py / modules.py          # 13 módulos (dicts) + parâmetros físicos
│   ├── tree.py / hierarchies.py           # Node N-ário; árvores funcional + criticidade
│   ├── climate.py / generation.py         # clima (tau, térmico, FSM); 3 fontes de energia
│   ├── consumption.py / energy_levels.py  # consumo térmico; rótulo CRITICAL→SURPLUS
│   ├── prediction.py / decision.py        # OLS à mão; evaluate_rules() puro
│   ├── allocation.py / failures.py        # load shedding 4 estágios; falhas + auto-reparo
│   ├── simulator.py / state.py / rng.py   # run_simulation; estado sem singleton; LCG
│   ├── simsnapshot.py / dashboard.py / cli.py  # adaptador; TUI 6 abas; entrypoint aurora
│   └── analysis.py                        # agrega o history em métricas de balanço
└── colony/                           # Fase 4 — topologia/rede da colônia (grafo + algoritmos)
    ├── graph.py                       # Module @dataclass + InfrastructureGraph (adj + pesos)
    ├── roster.py                      # 13 nós derivados de operations.MODULES (fonte única)
    ├── topology.py                    # EDGES declarativas + build_graph() canônico
    ├── search.py                      # BFS por níveis, DFS iterativo, connected_components
    ├── paths.py                       # Dijkstra, variante com restrição de prioridade, all_shortest
    ├── analysis.py                    # Tarjan (pontos de articulação), Brandes (betweenness), clustering
    ├── modeling.py                    # C(t)=C0·e^{rt}, derivadas, perda por distância, cenários
    └── cli.py                         # menus TUI SIGIC + PT_LABELS (rótulos em português)

tests/                  # pytest na raiz, espelha o pacote
fases/fase-N/           # entrypoint: notebook.ipynb (+ extras por fase)
docs/fase-N/            # ensaios textuais
archive/                # gitignored — material original preservado
```

## Convenções

- **Versionamento**: `0.N.0` corresponde à fase N (`0.2.0` = fase 2).
- **Imports**: notebooks importam de `aurora_siger.<modulo>` — nunca lógica inline.
- **Idioma**: nomes/docstrings em inglês no pacote; ensaios e README em português.
- **Type hints**: obrigatórios em parâmetros e retornos públicos.
- **Testes**: `tests/test_<dominio>_<arquivo>.py`; TDD quando possível.
- **Pacotes zero-dep no CLI**: `aurora_siger/landing/` (fase 2) e `aurora_siger/operations/` (fase 3) usam só stdlib (`math`, `random`/LCG próprio) — a regressão OLS da fase 3 é escrita à mão, sem numpy/sklearn. NumPy fica para módulos da fase 1 e para scripts de plotagem (`figuras/gerar_graficos.py`).

## Decisões de design — fase 1

- `_average_path_length()` é **intencionalmente duplicada** em `IsolationTree` e `MyIsolationForest` para manter cada classe autossuficiente.
- `generate_telemetry_dataset()` usa `np.random.RandomState(seed)` (não `np.random.seed()` global) para isolamento entre chamadas.
- `Validator` aceita `rules` opcional no construtor para override em testes ou fases futuras.
- `launch_decision()` retorna `bool` e imprime o relatório (similar ao `LandingMission.print_report` da fase 2).

## Decisões de design — fase 2

- **Regra de autorização** (`authorization.evaluate`) é **pura**: recebe módulo + condições, devolve `AuthorizationResult(authorized, reasons)`. O empilhamento de `Alert` na `alert_stack` é responsabilidade da `LandingMission`, não da regra. Materializa o argumento "regra inspecionável" do relatório.
- **`LandingMission` encapsula todo o estado** (queue, landed/waiting vectors, alert stack, conditions). Sem globais — duas missões podem rodar em paralelo num notebook.
- **`Vector` → `Queue` → `Stack` por herança** preserva a Figura A.1 do relatório. `Vector` carrega busca/ordenação Module-specific; `Stack` polimórfico aceita `Alert` na `alert_stack` (sem chamar métodos Module-específicos).
- **`Module` é `@dataclass`** com atributos `id`/`type`/`status` deliberadamente sombreando builtins para fidelidade ao relatório (`module.id`, `module.type`).
- **`mgpeb.py` é wrapper de 21 linhas** sobre `aurora_siger.landing.cli:main` — preserva `python3 fases/fase-2/mgpeb.py` enquanto a lógica vive no pacote.
- **`figuras/gerar_graficos.py` importa de `physics.py`** — única fonte de verdade para as 4 fórmulas.

## Decisões de design — fase 3

> Fonte de verdade dos *porquês*: `fases/fase-3/relatorio.md` (§6 Arquitetura de consolidação) e a spec em `docs/superpowers/specs/2026-05-27-fase-3-operations-consolidacao-design.md`. Esta seção resume o que o código não conta sozinho.

- **Consolidação de duas branches da equipe**: o núcleo científico da branch `iuri` (funcional/puro) é **canônico**; colhe-se da branch `main` (OO/multi-thread) o dashboard, níveis de energia, LCG, falhas+auto-reparo e frente fria. Rejeitados de propósito (YAGNI/convenções): sistema de crew, spawn dinâmico de módulos, gradiente descendente, singleton `DataStorage`, tick de relógio de parede. **Não reintroduzir** esses sem motivo.
- **Continuidade da fase 2**: os 13 módulos preservam nomes/prioridades dos que pousaram na fase 2 (1–12) + gerador eólico (13). Sem taxonomia paralela — é decisão narrativa.
- **Estado sem singleton**: `init_simulation(seed)` devolve um `dict` local (clima, bateria, árvores, FSMs, RNG). Sem global — duas simulações coexistem (espelha o "sem globais" da `LandingMission`).
- **Duas árvores N-árias sobre os mesmos dicts**: `hierarchies.py` constrói árvore funcional + de criticidade referenciando os **mesmos** módulos — alterar `module["current_mode"]` é visível por ambas, sem cópia. A de criticidade guia o load shedding; **Vital nunca desliga**.
- **Duas camadas de decisão**: `decision.evaluate_rules(snapshot)` é puro e inspecionável (a camada didática do enunciado, formato exato pedido); `allocation.py` faz o load shedding estrutural em 4 estágios. Separadas de propósito.
- **Nível de energia é rótulo de saída, não controle**: `CRITICAL→…→SURPLUS` computado de `bateria% + slope OLS`. Fluxo unidirecional física → nível → apresentação. Slope negativo rebaixa o nível *antes* de a bateria cair — é o ponto preditivo da fase.
- **Uma regressão, dois usos**: `prediction.linear_regression()` (OLS forma fechada, à mão) serve previsão eólica **e** slope da tendência. OLS escolhida sobre gradiente descendente: exata, sem learning rate, sem clamp anti-explosão, auditável.
- **Controle de carga em duas camadas sem dupla-contagem**: `power_factor` (preventivo, contínuo 1.0→0.2, da `main`) escala os *alvos* de consumo; o load shedding (rede de segurança, da `iuri`) decide os *modos* contra a oferta já atenuada. A ordem de operação evita contar a economia duas vezes.
- **Consumo térmico físico**: `current_consumption_kw()` é puro — `base_por_modo × power_factor + termo_térmico (Q=U·A·ΔT)`. O termo é somado **mesmo com o módulo "off"** (habitats pressurizados não congelam) e zera com `thermal_factor == 0`.
- **`aurora_core.py` é wrapper** sobre `aurora_siger.operations.cli:main` — espelha o `mgpeb.py` da fase 2. Dashboard TUI de 6 abas lê os dados via adaptador fino `SimSnapshot` (`.get()`/`.history()`/`.modules()`); a thread só faz *pacing* visual.
- **Determinismo bit-a-bit**: toda aleatoriedade (clima, falhas) passa pelo **mesmo** LCG em `state["rng"]`; mesma seed ⇒ histórico idêntico (verificado por diff de dois runs headless). Execução canônica: `run_simulation(seed=42)`.

## Decisões de design — fase 4

> Fonte de verdade dos *porquês*: `fases/fase-4/relatorio.md` (§6 Nota de procedência) e as specs em `docs/superpowers/specs/`. Esta seção resume o que o código não conta sozinho.

- **Continuidade via `operations.MODULES`**: os 13 módulos da Fase 3 são a **fonte única de verdade** para nome, tipo e consumo de cada nó do grafo. `colony/roster.py` importa `aurora_siger.operations.MODULES` em modo somente-leitura e não duplica tabelas. Qualquer mudança no roster da Fase 3 propagará automaticamente para a Fase 4.
- **Prioridade derivada da árvore de criticidade**: `roster.py` mapeia o tier de criticidade da Fase 3 diretamente em inteiro de prioridade (`Vital → 10, Sustenance → 7, Expansion → 4`). Essa derivação garante coerência com o load-shedding da Fase 3 (Vital nunca desliga) e com o roteamento prioritário do Dijkstra na Fase 4.
- **Idioma EN-código / PT-CLI**: os módulos, funções e campos internos seguem inglês (convenção do pacote); a apresentação ao usuário usa `cli.PT_LABELS` (dicionário de rótulos em português). Separação intencional — testes cobrem código EN; a tradução fica isolada e não afeta a lógica.
- **Betweenness Brandes substitui enumeração de caminhos simples**: a implementação de Brandes em `analysis.betweenness()` opera em $O(V \cdot E)$ — polinomial e determinístico. A abordagem anterior (enumeração exaustiva de todos os caminhos simples) é exponencial e impraticável em grafos maiores. Brandes foi adotado sem perda de exatidão.
- **`GENERATION_CAPACITY` derivado dos geradores reais**: `modeling.GENERATION_CAPACITY = 210` (kW) é a soma Solar (100) + Nuclear (80) + Eólico (30) lida diretamente dos dados da Fase 3. Toda a modelagem de consumo (`C(t) = C₀·e^{rt}`) e os limiares de alerta (90 % de 210 kW = 189 kW em ~7,1 anos) são ancorados nesse valor — não é uma constante inventada.
- **Wind (#13) é folha → Logistics (#9) é ponto de articulação real**: o Gerador Eólico tem grau 1 (conectado exclusivamente ao Armazenamento e Logística). Isso faz do módulo #9 (tier Expansão, prioridade 4) o único ponto de corte da rede — contradizendo a intuição baseada só em criticidade operacional. O algoritmo de Tarjan (`analysis.articulation_points`) identifica esse risco automaticamente. **Não adicionar arestas ao Eólico sem rever esse achado.**

## Como adicionar uma nova fase

1. Criar `aurora_siger/<dominio>/` com submódulos por responsabilidade (ver `landing/` como referência).
2. Criar `fases/fase-N/notebook.ipynb` importando de `aurora_siger.<dominio>` + assets/.
3. Criar `docs/fase-N/` para ensaios.
4. Adicionar testes `tests/test_<dominio>_<arquivo>.py`.
5. Bump `__version__` para `0.N.0` em `aurora_siger/__init__.py` e `pyproject.toml`.
6. Atualizar tabela de roadmap e entregáveis no `README.md`.
7. Atualizar **este `CLAUDE.md`**: estado/versão (linha do "Projeto"), bloco Setup (contagem de testes, novo entrypoint), árvore de Arquitetura e nova seção "Decisões de design — fase N".
8. Executar notebook in-place (`jupyter nbconvert --execute --inplace`) antes do commit para popular outputs.
