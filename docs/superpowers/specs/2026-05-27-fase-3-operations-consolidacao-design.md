# Fase 3 — Consolidação `aurora_siger/operations/` (design)

**Data:** 2026-05-27
**Autor da consolidação:** Iúri Leão de Almeida
**Status:** aprovado (brainstorming) — pronto para plano de implementação

---

## 1. Contexto e objetivo

A Fase 3 da atividade integradora da FIAP foi entregue pela equipe num repositório
separado (`github.com/Gcarmnonapy7/fiap-aurora-siger-fase3`) em **duas branches
arquiteturalmente distintas** do mesmo enunciado:

- **`main`** (majoritariamente Marcio): pacote `colonia_aurora/` — OOP multi-thread,
  dashboard TUI ao vivo, 14 módulos, RNG LCG próprio, regressão por gradiente
  descendente, sistema de crew/eventos. Compartilha com a outra branch apenas o
  commit ancestral do enunciado.
- **`iuri`**: pacote `colony/` — funcional/puro sobre séries temporais (horas),
  clima cientificamente fundamentado (tau, térmico `Q=U·A·ΔT`, degradação de
  painel, tempestades FSM), regressão OLS fechada, árvores hierárquicas, alocação
  de carga em 4 estágios. Já construída via spec.

**Objetivo:** consolidar o que há de mais sofisticado e realista em **cada** branch
numa Fase 3 unificada — *melhor que a soma das duas* — integrada ao portfólio
pessoal `github.com/iurileao-hub/FIAP-Aurora-Siger`, respeitando as convenções já
estabelecidas pelas fases 1 e 2.

A entrega acadêmica já ocorreu; este trabalho é **curadoria de portfólio**, sem
prazo externo.

### Decisões fixadas no brainstorming

| Decisão | Escolha |
|---|---|
| Nível de ambição | Rica + dashboard ao vivo |
| Autoria | Equipe creditada (3 autores) + nota de consolidação |
| Abordagem | **A** — núcleo `iuri` canônico + colheita do `main` |
| Extras de realismo | Falhas de equipamento + auto-reparo; evento de frente fria. **Sem** spawn dinâmico |

---

## 2. Enquadramento no portfólio

A Fase 3 entra como o domínio **`operations/`** no pacote (a colônia *operando* —
fecha o arco narrativo decolagem → pouso → operação, seguindo o padrão de
nome-de-atividade `landing/` da Fase 2). Segue os 7 passos de "Como adicionar uma
nova fase" do `CLAUDE.md` do repositório alvo.

```
aurora_siger/operations/        # Fase 3 — colônia operando (energia + decisão)
├── __init__.py
├── constants.py        # clima/painel/bateria/térmico (iuri) + limiares nível/slope (main)
├── rng.py              # LCG (main), "implementado do zero" — substitui random
├── tree.py             # Node N-ário (iuri)
├── hierarchies.py      # árvores funcional + criticidade (iuri) ............ item 1.1
├── climate.py          # vento, temp, tempestades FSM, tau, painéis, frente fria
├── generation.py       # solar/eólica/nuclear (iuri)
├── consumption.py      # base por modo + térmico Q=U·A·ΔT + power_factor
├── allocation.py       # power_factor (throttle) + load shedding 4 estágios (backstop)
├── energy_levels.py    # NOVO: nível CRITICAL→SURPLUS + slope (main) via OLS (iuri)
├── failures.py         # NOVO: falha estocástica + auto-reparo temporizado (sem crew)
├── state.py            # estado sem singleton (iuri)
├── simulator.py        # run_simulation/step (iuri) + grava nível, slope, falhas
├── decision.py         # evaluate_rules puro (iuri) ........................ item 1.2
├── prediction.py       # regressão OLS (iuri) .............................. item 1.3
├── analysis.py         # balanço, por-sol, breakdown, momentos críticos .... item 1.4
├── dashboard.py        # TUI 6 abas (main) portado via SimSnapshot
└── cli.py              # menu/loop do dashboard ao vivo

fases/fase-3/
├── notebook.ipynb      # narrativa dos 4 itens (badge Colab no README)
├── aurora_core.py      # wrapper fino (~20 linhas) → aurora_siger.operations.cli:main
└── relatorio.md/.pdf   # relatório técnico (exigência 2.2)
docs/fase-3/
└── reativo-a-preditivo.md   # ensaio reflexivo
tests/test_operations_*.py
```

Mudanças de projeto:
- `pyproject.toml`: novo console script `aurora = "aurora_siger.operations.cli:main"`;
  bump de versão para **`0.3.0`**.
- `README.md`: atualizar tabela de roadmap (Fase 3 → Concluída), tabela de
  entregáveis 3.x e badge Colab da Fase 3.
- `aurora_siger/__init__.py`: `__version__ = "0.3.0"`.

---

## 3. Núcleo consolidado — decisões técnicas

### 3.1 Fundações canônicas

| Dimensão | Canônico | Descartado |
|---|---|---|
| Unidade de tempo | **horas** (iuri); 1 passo = 1 hora, sol = 24 h | ticks wall-clock (main) |
| Execução do núcleo | batch determinístico sem thread (iuri) | thread real-time como *motor* (main) |
| Estado | dicts locais, **sem singleton** (iuri) | `DataStorage` singleton (main) |
| Bateria | 500 kWh + reserva de emergência 20 % (iuri) | 1000 kWh (main) |
| RNG | **LCG** `operations/rng.py` (main), seed-aware | `random` (iuri), gradiente (main) |
| Regressão | **OLS fechada** (iuri) | gradiente descendente (main) |
| Taxonomia de módulos | **13 módulos do iuri** (continuidade da colônia da Fase 2) | 14 classes OOP (main) |
| Clima | iuri (tau, térmico, painel, FSM) | random-walk de sensores (main) |

**Continuidade da Fase 2:** os módulos 1–12 do iuri preservam exatamente os
nomes/prioridades dos módulos que pousaram na Fase 2; o 13º (eólico) foi adicionado
na Fase 3. A colônia que pousou é literalmente a que opera agora — não se introduz
uma taxonomia paralela.

### 3.2 Uma única regressão, dois usos

A OLS fechada de `prediction.py` (`a = Σ(Δx·Δy)/Σ(Δx²)`, `b = ȳ − a·x̄`) é usada para:
1. **Item 1.3** — prever energia eólica a partir do vento (treina sobre
   `wind_ms` × `wind_generation_kw`, filtrando pontos abaixo do cut-in).
2. **Slope preditivo** — regressão sobre os últimos N deltas de energia para
   antecipar tendência (era o uso do gradiente descendente no `main`).

Uma implementação, dois propósitos: menos código, e a forma fechada é exata onde o
gradiente precisava de clamp anti-divergência.

### 3.3 Controle de carga em duas camadas (fusão central)

As duas branches têm filosofias opostas de controle; a síntese combina ambas:

1. **Camada decentralizada (rápida) — `power_factor` (do main):** cada módulo
   degrada suavemente o alvo `adequate` conforme a % de bateria (escala contínua,
   sem saltos binários).
2. **Camada centralizada (estrutural) — load shedding 4 estágios (do iuri):** o
   alocador percorre a árvore de criticidade (Vital → Sustento → Expansão) e,
   quando a oferta ainda não cobre a demanda já atenuada, rebaixa modos
   bottom-up; Vital nunca desliga.

**Risco de integração a tratar no plano:** evitar dupla-contagem entre as duas
camadas. Composição proposta: `power_factor` escala o **alvo** `adequate`/`surplus`;
a alocação então decide os **modos** (`off`/`minimum`/`adequate`/`surplus`) contra
a oferta disponível usando esses alvos já escalados. A ordem é: (a) computar
`power_factor` da bateria; (b) escalar alvos; (c) rodar alocação 4 estágios.

### 3.4 Consumo

`current_consumption_kw(module, climate, power_factor)` — função pura:
`base_por_modo × power_factor + termo_térmico`, onde o termo térmico é o modelo
físico `Q = U·A·ΔT` por `thermal_factor` (do iuri). O termo térmico é somado mesmo
com o módulo "off" (habitats pressurizados não podem congelar) e zera naturalmente
quando `thermal_factor == 0`.

### 3.5 Nível de energia como estado-resumo (saída)

A máquina `CRITICAL → LOW → NOMINAL → HIGH → SURPLUS` + escalonamento por slope
(do main) deixa de **controlar** os módulos e passa a ser o **rótulo de saída**
computado de `bateria% + slope OLS`. É lido pelo dashboard e pelas regras de
decisão. Fluxo unidirecional: física → nível → apresentação/decisão.

### 3.6 Falhas de equipamento + auto-reparo (`failures.py`)

- Cada módulo ativo tem probabilidade ~0,5 %/hora de falhar (via LCG).
- Ao falhar: `broken = True`, `active = False`; sai da geração/consumo.
- Reparo **automático e temporizado** (sorteio de duração em horas); ao concluir,
  volta a `active`. **Sem sistema de crew** — reparo é processo de fundo.
- Registrado no `history` para o log de eventos do dashboard.

### 3.7 Evento de frente fria (em `climate.py`)

Além das tempestades FSM do iuri, adiciona-se **frente fria**: queda brusca de
temperatura (ex.: −30 °C por janela de horas) que dispara pico de consumo térmico
via `Q=U·A·ΔT`. Exercita o modelo térmico de forma dramática e dá material visual
ao dashboard.

---

## 4. Port do dashboard (6 abas)

O dashboard do `main` lê de `storage.get(chave, default)` + dict `hist`. Em vez do
singleton, um **adaptador fino `SimSnapshot`** expõe a mesma interface
`.get()`/`.history()` sobre o `state`/`history` do simulador. As funções de
renderização (ANSI, sparklines, layout, navegação por abas) reusam intactas.

| Aba | Conteúdo | Origem |
|---|---|---|
| 1 Visão Geral | nível, bateria, delta, alerta, evento ativo | main + nível |
| 2 Energia | geração solar/eólica/nuclear, consumo, sparklines | main |
| 3 Clima | temp, vento, irradiância, **tau**, poeira, tempestade, fator de painel | iuri |
| 4 Módulos | 13 módulos: modo, consumo, criticidade, **status quebrado/reparo** | iuri + falhas |
| 5 Eventos | tempestades, **frentes frias**, **falhas/reparos** | iuri + main |
| 6 **Hierarquia** | árvore de criticidade ao vivo — **item 1.1 visualizado** | iuri (repurposa crew) |

Notebook (headless, `run_simulation()`) e dashboard (ao vivo, `cli.py` chamando
`step()` num loop) são **dois front-ends sobre o mesmo núcleo** — espelhando
notebook + `mgpeb` da Fase 2. A thread só existe no front-end do dashboard, para
pacing visual; o conteúdo da simulação permanece determinístico dada a seed.

---

## 5. Mapeamento aos 4 itens do enunciado

| Item | Entregável | Módulo | Síntese |
|---|---|---|---|
| **1.1** Organização hierárquica | árvores funcional + criticidade (Node N-ário) + lista plana dos 13 módulos | `hierarchies.py`, `tree.py`, `modules.py` | iuri |
| **1.2** Regras de decisão | `evaluate_rules(snapshot)` puro + alertas dos níveis | `decision.py`, `energy_levels.py` | iuri + main |
| **1.3** Previsão por regressão | OLS fechada vento → energia eólica | `prediction.py` | iuri |
| **1.4** Análise de energia | balanço geração×consumo, por-sol, breakdown, momentos críticos | `analysis.py` | iuri |

---

## 6. Notebook, relatório, docs e autoria

- **`fases/fase-3/notebook.ipynb`:** narrativa dos 4 itens importando de
  `aurora_siger.operations` (lógica nunca inline). Executado in-place
  (`nbconvert --execute --inplace`) antes do commit.
- **`fases/fase-3/aurora_core.py`:** wrapper fino → `aurora_siger.operations.cli:main`.
- **`fases/fase-3/relatorio.md` → `.pdf`:** relatório técnico cobrindo organização
  de dados, regras de decisão, modelo de previsão, ganho energético e link do repo
  (exigência 2.2). Espelha o formato do relatório da Fase 2.
- **`docs/fase-3/reativo-a-preditivo.md`:** ensaio reflexivo sobre o objetivo final
  do enunciado (§5: "evoluir de sistemas reativos para sistemas preditivos"),
  ancorado no slope OLS que antecipa `LOW` antes de a bateria cair abaixo de 40 %.
- **Autoria:** `README.md`, `pyproject.toml` e relatório mantêm os 3 autores (como
  hoje) + **nota de consolidação** explícita: "Fase 3 é uma consolidação de Iúri
  sobre as duas branches da equipe", com link para
  `Gcarmnonapy7/fiap-aurora-siger-fase3`.

### Tabela de procedência (para a nota de consolidação)

| Componente | Vem de | Observação |
|---|---|---|
| Clima, térmico, painel, tempestades, OLS, hierarquias, alocação, 13 módulos | `iuri` | núcleo científico |
| Dashboard TUI, níveis de energia, `power_factor`, LCG, falhas+reparo, frente fria | `main` | colheita / re-vestida no estilo funcional |
| Controle em duas camadas, regressão única com dois usos, aba Hierarquia, `SimSnapshot` | consolidação | inédito nas duas branches |

---

## 7. Testes e verificação

Suíte `tests/test_operations_*.py`, espelhando o rigor das fases 1–2 (147 testes):

- **Determinismo (chave):** mesma seed ⇒ `history` idêntico passo-a-passo (espelha o
  isolamento de RNG da Fase 1).
- **OLS:** recupera coeficientes exatos de dados lineares sintéticos; erra
  graciosamente (ValueError) em entrada degenerada.
- **Alocação:** os 4 estágios disparam nas fronteiras corretas de oferta; Vital
  nunca desliga; geradores não são rebaixados mas seu consumo entra no custo.
- **Térmico:** `Q=U·A·ΔT` zera com `thermal_factor=0`; sobe sob frente fria.
- **Níveis:** transições corretas por bateria% e por slope.
- **Falhas:** módulo falha → fica fora de geração/consumo → reparado após N horas.
- **LCG:** período e uniformidade básica; reprodutibilidade por seed.
- **Dashboard:** testa o adaptador `SimSnapshot` (não o ANSI) + 1 smoke render para
  buffer de string.

Verificação final: `pytest` verde + `nbconvert --execute` sem erro + smoke manual
do CLI (`aurora`) + diff de dois runs seeded confirmando logs idênticos.

---

## 8. Fora de escopo (YAGNI)

Explicitamente **não** portados do `main`:
- Sistema de crew (saúde/reparo manual) — substituído por reparo automático.
- Spawn dinâmico de módulos — quebra a continuidade dos 13 módulos da Fase 2.
- Regressão por gradiente descendente — substituída pela OLS.
- `DataStorage` singleton global — conflita com a convenção "sem globais".
- Tick wall-clock como unidade do núcleo — substituído por horas.
- Bateria de 1000 kWh / taxonomia de 14 módulos paralela.
- `aurora_dashboard.py` legado da raiz do repo de equipe (código morto) — não migra.

---

## 9. Riscos e pontos de atenção

1. **Dupla-contagem no controle em duas camadas** (§3.3) — exige composição
   cuidadosa e testes de fronteira.
2. **Port do dashboard** — mapeamento completo das chaves esperadas pelo
   `SimSnapshot`; identificar campos que o `history` do iuri ainda não grava
   (nível, slope, status de falha) e garantir que o simulador os publique.
3. **Determinismo com LCG** — todas as fontes de aleatoriedade (clima, falhas)
   devem passar pelo LCG único, senão o determinismo por seed quebra.
4. **Escopo** — a Fase 3 é ambiciosa; manter cada módulo de responsabilidade única
   e bem-testado para não virar um monólito difícil de revisar.
