# Fase 3 — M4: Notebook, Relatório, Ensaio e Entrega Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: este é o marco de **prosa + notebook**, não de código testável. Não há ciclo TDD red-green; cada tarefa entrega um artefato (doc/notebook/config) com um comando de verificação concreto (executabilidade, consistência de versão/links, determinismo). Steps usam checkbox (`- [ ]`).

**Goal:** Fechar a Fase 3 do portfólio: notebook narrativo dos 4 itens, relatório técnico (md→pdf), ensaio reflexivo "reativo→preditivo", atualização do README/roadmap, bump `0.3.0` e nota de consolidação — tudo verificado (pytest verde + notebook executa + CLI smoke + diff determinístico).

**Architecture:** O núcleo `aurora_siger/operations/` (M1–M3) já está pronto e verde (276 testes). O M4 só adiciona **front-ends de apresentação** sobre esse núcleo: o notebook (`run_simulation()` headless + matplotlib inline) e o relatório/ensaio (prosa). Lógica NUNCA inline no notebook — sempre importada de `aurora_siger.operations.*`. O notebook e o CLI `aurora` são dois front-ends do mesmo núcleo determinístico, espelhando notebook + `mgpeb` da Fase 2.

**Tech Stack:** Python 3.12, `aurora_siger.operations` (stdlib-only no núcleo), matplotlib (extra `viz`) para gráficos do notebook, `jupyter nbconvert --execute --inplace`, `pandoc --pdf-engine=xelatex` para o PDF.

---

## File Structure

| Arquivo | Responsabilidade | Ação |
|---|---|---|
| `aurora_siger/__init__.py` | `__version__` | Modificar → `0.3.0` |
| `pyproject.toml` | versão, descrição, keywords | Modificar → `0.3.0` + keywords de energia/simulação |
| `docs/fase-3/reativo-a-preditivo.md` | ensaio reflexivo (spec §6) | Criar |
| `fases/fase-3/notebook.ipynb` | narrativa dos 4 itens + viz, executado in-place | Criar |
| `fases/fase-3/figuras/header.tex` | estilo LaTeX do PDF (cópia adaptada da fase-2) | Criar |
| `fases/fase-3/relatorio.md` | relatório técnico (exigência 2.2) | Criar |
| `fases/fase-3/relatorio.pdf` | PDF gerado do relatório | Gerar |
| `README.md` | roadmap, entregáveis 3.x, badge Colab, quick start, árvore, nota de consolidação | Modificar |

Referências de convenção a seguir: `fases/fase-2/notebook.ipynb` (estrutura de células), `fases/fase-2/relatorio.md` (estrutura de seções), `fases/fase-2/figuras/header.tex` + `gerar_graficos.py` (PDF e plots), spec `docs/superpowers/specs/2026-05-27-fase-3-operations-consolidacao-design.md` (§2, §5, §6, tabela de procedência §6).

---

### Task 1: Bump de versão para 0.3.0

**Files:**
- Modify: `aurora_siger/__init__.py`
- Modify: `pyproject.toml:7`

- [ ] **Step 1: Atualizar `__version__`**

Em `aurora_siger/__init__.py`, trocar `__version__ = "0.2.0"` por `__version__ = "0.3.0"`.

- [ ] **Step 2: Atualizar `pyproject.toml`**

Linha 7: `version = "0.2.0"` → `version = "0.3.0"`.
Linha 8 (descrição): estender para mencionar a operação da colônia, ex.:
`description = "Sistema Inteligente de Gerenciamento de Riscos — telemetria de decolagem, pouso de módulos e operação energética de colônia espacial"`
Adicionar às `keywords` (ordem alfabética preservada): `"energy-management"`, `"ols-regression"`, `"simulation"`.

- [ ] **Step 3: Verificar consistência**

Run: `python -c "import aurora_siger; print(aurora_siger.__version__)"`
Expected: `0.3.0`
Run: `grep -c '0.3.0' pyproject.toml` → ≥ 1.

- [ ] **Step 4: Commit**

```bash
git add aurora_siger/__init__.py pyproject.toml
git commit -m "chore(fase-3): bump versão 0.3.0 + keywords de operação"
```

---

### Task 2: Ensaio reflexivo `reativo-a-preditivo.md`

**Files:**
- Create: `docs/fase-3/reativo-a-preditivo.md`

Ensaio em PT-BR (spec §6) sobre o objetivo do enunciado: *"evoluir de sistemas reativos para sistemas preditivos"*. Âncora técnica concreta: o **slope OLS** (`prediction.fit_energy_trend`) que antecipa o nível `LOW` antes de a bateria cruzar 40 %, e o `energy_level` rebaixado por slope íngreme (`energy_levels.energy_level`, §3.5). Tom: ensaio reflexivo no nível das fases 1–2 (ver `docs/fase-1/etica.md`, `docs/fase-2/esg.md` para calibrar profundidade), 900–1400 palavras.

- [ ] **Step 1: Escrever o ensaio**

Estrutura mínima (títulos `##`):
1. **Abertura** — a colônia que pousou (Fase 2) agora opera; a pergunta deixa de ser "é seguro pousar?" e passa a ser "vamos ficar sem energia daqui a N horas?".
2. **O reativo e seus limites** — controle por limiar (bateria < X → desliga): age só depois do dano; ilustrar com o load shedding 4 estágios (`allocation.py`) como camada *reativa* legítima mas insuficiente sozinha.
3. **O passo preditivo** — regressão OLS sobre os deltas de energia (`fit_energy_trend`): o slope vira sinal antecipatório; explicar como `energy_level()` usa o slope para rebaixar o rótulo *antes* de o nível de bateria piorar (preempção). Citar a forma fechada `a = Σ(Δx·Δy)/Σ(Δx²)` e por que é exata onde o gradiente precisava de clamp (spec §3.2).
4. **Duas camadas, uma filosofia** — `power_factor` contínuo (preventivo suave) + shedding estrutural (backstop) = defesa em profundidade (§3.3); ligação com a transição reativo→preditivo.
5. **Limites honestos** — OLS linear sobre janela curta extrapola mal sob regime não-estacionário (tempestade/frente fria); previsão é hipótese, não certeza; o humano-no-loop continua necessário (eco da reflexão ética da Fase 1).
6. **Fecho** — preditivo não substitui reativo: o estratifica. O reativo é a rede; o preditivo é não precisar dela com tanta frequência.

Sem código inline pesado; referenciar funções por nome (`fit_energy_trend`, `energy_level`, `power_factor`, `allocate_energy`). Idioma PT-BR.

- [ ] **Step 2: Verificar**

Run: `wc -w docs/fase-3/reativo-a-preditivo.md` → 900–1400 palavras.
Run: `grep -E "fit_energy_trend|energy_level|power_factor|slope" docs/fase-3/reativo-a-preditivo.md` → cita as funções-âncora.

- [ ] **Step 3: Commit**

```bash
git add docs/fase-3/reativo-a-preditivo.md
git commit -m "docs(fase-3): ensaio reflexivo reativo→preditivo (slope OLS)"
```

---

### Task 3: Notebook narrativo dos 4 itens

**Files:**
- Create: `fases/fase-3/notebook.ipynb`

Notebook executável que narra os 4 itens do enunciado (spec §5) importando SEMPRE de `aurora_siger.operations` (nunca lógica inline). Espelha o estilo da Fase 2: markdown explicativo + células de código curtas + gráficos matplotlib. Roda uma simulação determinística (`run_simulation(seed=42)`, horizonte de 168 h = 7 sóis) e analisa o resultado.

**Pré-requisito de execução:** matplotlib disponível no ambiente (extra `viz`). Se ausente: `pip install matplotlib` no venv ativo (ou `pip install -e ".[viz]"`). Verificar antes de executar.

- [ ] **Step 1: Construir o notebook**

Autorar via script `nbformat` (ou montar o JSON), com a sequência de células abaixo. Cada célula de código mostra o conteúdo real a executar.

**Célula 0 (md):** título + contexto.
```markdown
# Aurora SIGER — Fase 3: Operação Energética da Colônia

A colônia que pousou na Fase 2 agora **opera**. Este notebook narra os quatro
itens do enunciado da Fase 3 — organização hierárquica, regras de decisão,
previsão por regressão e análise energética — sobre um núcleo de simulação
**determinístico** (mesma seed ⇒ mesma história). Toda a lógica vive em
`aurora_siger.operations`; aqui só orquestramos e visualizamos.
```

**Célula 1 (md):** `## 0. Setup e simulação determinística`
**Célula 2 (code):**
```python
import matplotlib.pyplot as plt
from aurora_siger.operations.simulator import run_simulation
from aurora_siger.operations.constants import HOURS_PER_SOL, TOTAL_STEPS

climate, battery, history = run_simulation(seed=42)
n = len(history["total_generation_kw"])
print(f"Simulação: {n} horas ({n // HOURS_PER_SOL} sóis), seed=42 (determinística)")
print(f"Bateria final: {battery['current_charge_kwh']:.0f} / {battery['max_capacity_kwh']:.0f} kWh")
```

**Célula 3 (md):** `## Item 1.1 — Organização hierárquica` (texto: árvore funcional + criticidade, Node N-ário, 13 módulos; continuidade da Fase 2).
**Célula 4 (code):**
```python
from aurora_siger.operations.hierarchies import build_criticality_tree
from aurora_siger.operations.modules import MODULES

tree = build_criticality_tree()
print(tree.pretty_print())
print(f"\n{len(MODULES)} módulos; níveis de criticidade: "
      f"{[c.name for c in tree.children]}")
```

**Célula 5 (md):** `## Item 1.2 — Regras de decisão` (texto: `evaluate_rules` puro + níveis CRITICAL→SURPLUS como rótulo de saída, §3.5).
**Célula 6 (code):**
```python
from aurora_siger.operations.decision import evaluate_rules
from collections import Counter

levels = history["energy_level"]
print("Distribuição de níveis de energia ao longo da missão:")
for lvl, c in Counter(levels).most_common():
    print(f"  {lvl:<10} {c:4d} h")
# Alertas de emergência registrados
emergencias = sum(1 for a in history["alerts"] if a)
print(f"\nHoras com alerta de emergência: {emergencias}")
```
*(Ajustar a chamada `evaluate_rules` à assinatura real do módulo — verificar `decision.py` antes; se a função operar sobre um snapshot/dict, montar o snapshot da última hora a partir de `history`/`climate`/`battery`.)*

**Célula 7 (md):** `## Item 1.3 — Previsão por regressão (OLS)` (texto: regressão única, dois usos — vento→eólica e slope preditivo; forma fechada exata, §3.2).
**Célula 8 (code):** treinar OLS vento×eólica e plotar dispersão + reta ajustada.
```python
from aurora_siger.operations.prediction import fit_linear, predict

wind = history["wind_ms"]
wpow = history["wind_generation_kw"]
pts = [(w, p) for w, p in zip(wind, wpow) if p > 0]  # acima do cut-in
xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
a, b = fit_linear(xs, ys)
print(f"Energia eólica ≈ {a:.2f}·vento + {b:.2f}")

fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(xs, ys, s=8, alpha=0.4, label="observado")
line_x = [min(xs), max(xs)]
ax.plot(line_x, [predict(a, b, x) for x in line_x], "r-", label="OLS")
ax.set_xlabel("vento (m/s)"); ax.set_ylabel("geração eólica (kW)")
ax.set_title("Item 1.3 — Previsão OLS: vento → energia eólica"); ax.legend()
plt.tight_layout(); plt.show()
```
*(Verificar nomes reais em `prediction.py`: `fit_linear`/`predict`/`fit_energy_trend`. Usar os que existirem; ajustar a célula à API real.)*

**Célula 9 (md):** `### Slope preditivo` (o mesmo estimador antecipando tendência).
**Célula 10 (code):** plotar `slope` e `predicted_delta` ao longo do tempo.
```python
slope = history["slope"]; pred = history["predicted_delta"]
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.plot(slope, label="slope (kW/h)"); ax.plot(pred, label="delta previsto (kW)", alpha=0.7)
ax.axhline(0, color="k", lw=0.5)
ax.set_xlabel("hora"); ax.set_title("Tendência energética antecipada (OLS)"); ax.legend()
plt.tight_layout(); plt.show()
```

**Célula 11 (md):** `## Item 1.4 — Análise energética` (texto: balanço geração×consumo, por-sol, breakdown de fontes, momentos críticos).
**Célula 12 (code):** série temporal geração vs consumo + bateria.
```python
gen = history["total_generation_kw"]; con = history["total_consumption_kw"]
bat = history["battery_charge_kwh"]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax1.plot(gen, label="geração", color="tab:green")
ax1.plot(con, label="consumo", color="tab:red")
ax1.set_ylabel("kW"); ax1.legend(); ax1.set_title("Item 1.4 — Balanço energético")
ax2.plot(bat, color="tab:blue"); ax2.set_ylabel("bateria (kWh)"); ax2.set_xlabel("hora")
plt.tight_layout(); plt.show()
```
**Célula 13 (code):** breakdown por fonte + tabela por-sol via `analysis.py`.
```python
from aurora_siger.operations import analysis
# Usar as funções reais de analysis.py (balanço, por-sol, breakdown, momentos
# críticos). Verificar assinaturas antes; imprimir um resumo por sol.
```
*(Verificar `analysis.py` e usar suas funções reais — não inventar nomes.)*

**Célula 14 (md):** `## Fecho — do reativo ao preditivo` (1 parágrafo ligando ao ensaio `docs/fase-3/reativo-a-preditivo.md` e ao dashboard ao vivo `aurora`).

- [ ] **Step 2: Garantir matplotlib + executar in-place**

Run (no venv ativo): `python -c "import matplotlib" || pip install matplotlib`
Run: `jupyter nbconvert --to notebook --execute --inplace fases/fase-3/notebook.ipynb`
Expected: termina sem erro; outputs (incluindo figuras) populados.

- [ ] **Step 3: Verificar que importa do pacote (lógica não-inline)**

Run: `grep -c "from aurora_siger.operations" fases/fase-3/notebook.ipynb` → ≥ 5.
Inspecionar: nenhuma célula reimplementa OLS/alocação/clima — só importa e chama.

- [ ] **Step 4: Commit**

```bash
git add fases/fase-3/notebook.ipynb
git commit -m "feat(fase-3): notebook narrativo dos 4 itens (executado in-place)"
```

---

### Task 4: Relatório técnico `relatorio.md`

**Files:**
- Create: `fases/fase-3/relatorio.md`

Relatório técnico em PT-BR (exigência 2.2 do enunciado), espelhando a estrutura de `fases/fase-2/relatorio.md`: Resumo, Introdução, seções numeradas cobrindo os 4 itens, contextualização, e **nota de consolidação + tabela de procedência** (spec §6). Cobre obrigatoriamente: organização de dados, regras de decisão, modelo de previsão, ganho energético, e link do repositório.

- [ ] **Step 1: Escrever o relatório**

Estrutura (`##`/`###`), espelhando o tom da Fase 2:
- **Cabeçalho** — título, autores (os 3), data, link do repo `github.com/iurileao-hub/FIAP-Aurora-Siger`.
- **Nota de consolidação** (destaque, logo após o cabeçalho): "A Fase 3 foi entregue pela equipe em duas branches arquiteturalmente distintas (`main`, `iuri`) no repo `github.com/Gcarmnonapy7/fiap-aurora-siger-fase3`. Esta versão é uma **consolidação** feita por Iúri Leão sobre as duas, integrada ao portfólio — núcleo científico do `iuri` + colheita do `main`." Incluir a **tabela de procedência** (spec §6: iuri / main / consolidação).
- **## Resumo** — 1 parágrafo.
- **## 1. Introdução** — o arco decolagem→pouso→operação; o salto reativo→preditivo.
- **## 2. Organização dos dados e da colônia** — 13 módulos (continuidade Fase 2), árvores funcional + criticidade (Node N-ário), estado sem singleton, séries temporais horárias. (item 1.1)
- **## 3. Regras de decisão** — `evaluate_rules` puro; máquina de níveis CRITICAL→SURPLUS como rótulo de saída derivado de bateria%+slope (§3.5); fluxo unidirecional física→nível→decisão. (item 1.2)
- **## 4. Modelo de previsão** — OLS de forma fechada, dois usos (vento→eólica e slope preditivo, §3.2); por que OLS e não gradiente. (item 1.3)
- **## 5. Análise e ganho energético** — balanço geração×consumo, controle em duas camadas (`power_factor` + shedding 4 estágios, §3.3, sem dupla-contagem), modelo térmico `Q=U·A·ΔT`, falhas+auto-reparo (§3.6), frente fria (§3.7). Resultado quantitativo da simulação seed=42. (item 1.4)
- **## 6. Arquitetura de consolidação** — duas branches → uma síntese; decisões fixadas (núcleo iuri + colheita main; YAGNI: sem crew/spawn/gradiente/singleton); dois front-ends (notebook headless + CLI `aurora`) sobre um núcleo determinístico.
- **## 7. Conclusão** — eco do ensaio reativo→preditivo.
- **## Referências** (se aplicável).

Números devem bater com a simulação real (rodar `run_simulation(seed=42)` e extrair as métricas citadas — não inventar valores).

- [ ] **Step 2: Verificar**

Run: `grep -E "consolidação|procedência|iurileao-hub" fases/fase-3/relatorio.md` → presente.
Run: `grep -cE "^## " fases/fase-3/relatorio.md` → ≥ 7 seções.
Conferir: cobre os 4 itens + link do repo (exigência 2.2).

- [ ] **Step 3: Commit**

```bash
git add fases/fase-3/relatorio.md
git commit -m "docs(fase-3): relatório técnico + nota de consolidação e procedência"
```

---

### Task 5: Gerar `relatorio.pdf`

**Files:**
- Create: `fases/fase-3/figuras/header.tex`
- Generate: `fases/fase-3/relatorio.pdf`

- [ ] **Step 1: Preparar o header LaTeX**

Copiar `fases/fase-2/figuras/header.tex` para `fases/fase-3/figuras/header.tex` (ajustar título/metadados se o header os contiver). Inspecionar o header da fase-2 antes para replicar o mesmo estilo de PDF.

- [ ] **Step 2: Converter md → pdf**

Run (espelhar o comando que a fase-2 usaria; pandoc + xelatex disponíveis):
```bash
cd fases/fase-3 && pandoc relatorio.md -o relatorio.pdf \
  --pdf-engine=xelatex -H figuras/header.tex \
  -V geometry:margin=2.5cm -V lang=pt-BR --toc
```
Ajustar flags ao que o `header.tex` espera. Se o header da fase-2 usar variáveis específicas, replicá-las.
Expected: `relatorio.pdf` gerado sem erro.

- [ ] **Step 3: Verificar**

Run: `ls -la fases/fase-3/relatorio.pdf` → existe, tamanho > 20 KB.
Run: `pdfinfo fases/fase-3/relatorio.pdf 2>/dev/null | grep Pages` (se `pdfinfo` disponível) → ≥ 3 páginas.

- [ ] **Step 4: Commit**

```bash
git add fases/fase-3/figuras/header.tex fases/fase-3/relatorio.pdf
git commit -m "docs(fase-3): PDF do relatório técnico (pandoc/xelatex)"
```

---

### Task 6: Atualizar README

**Files:**
- Modify: `README.md`

Atualizar o README da raiz para refletir a Fase 3 concluída. Pontos (com números de linha aproximados do estado atual):

- [ ] **Step 1: Badge Colab da Fase 3** (após linha 6)

Adicionar:
```markdown
[![Fase 3 no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/iurileao-hub/FIAP-Aurora-Siger/blob/main/fases/fase-3/notebook.ipynb)
```

- [ ] **Step 2: Parágrafo de visão da Fase 3** (lista de fases, após o bullet da Fase 2, ~linha 17)

Adicionar bullet:
```markdown
- **Fase 3 — Operação (energia):** a colônia que pousou agora opera. Simulação horária determinística de geração (solar/eólica/nuclear), consumo (base + térmico `Q=U·A·ΔT`), bateria e clima (tau, tempestades, frente fria); controle de carga em duas camadas; previsão por regressão OLS; dashboard TUI ao vivo de 6 abas. Resultado: a evolução de decisões **reativas** para **preditivas**.
```

- [ ] **Step 3: Quick start** (~linha 39-44)

Acrescentar, após o bloco da Fase 2:
```markdown
# Notebook da fase 3 — operação energética da colônia
jupyter notebook fases/fase-3/notebook.ipynb

# Dashboard ao vivo da fase 3 (após install, em qualquer diretório)
aurora

# ...ou direto pelo arquivo, sem instalar
python3 fases/fase-3/aurora_core.py
```

- [ ] **Step 4: Árvore de estrutura** (~linha 62-85)

Adicionar o subpacote `operations/` sob `aurora_siger/` e a pasta `fases/fase-3/` + `docs/fase-3/` na árvore, espelhando o nível de detalhe usado para `landing/`.

- [ ] **Step 5: Tabela de Entregáveis da Fase 3** (após a tabela da Fase 2, ~linha 111)

Adicionar seção `## Entregáveis da Fase 3` com linhas 3.1–3.4 mapeando aos módulos (spec §5): 1.1 hierarquias (`hierarchies.py`/`tree.py`/`modules.py`), 1.2 decisão (`decision.py`/`energy_levels.py`), 1.3 previsão (`prediction.py`), 1.4 análise (`analysis.py`), + simulação/dashboard (`simulator.py`/`dashboard.py`/`cli.py`) e relatório (`fases/fase-3/relatorio.pdf`).

- [ ] **Step 6: Roadmap** (~linha 149)

Trocar a linha da Fase 3 de `| **3** | *Em breve* | — |` por:
`| **3** | Operação energética: simulação determinística, OLS, controle 2 camadas, dashboard TUI | Concluída |`

- [ ] **Step 7: Nota de consolidação** (na seção Autores, ~linha 157-163)

Adicionar parágrafo após a lista de autores: a Fase 3 é uma consolidação de Iúri sobre as duas branches da equipe (`main` + `iuri`), com link para `github.com/Gcarmnonapy7/fiap-aurora-siger-fase3`. Os 3 autores permanecem creditados.

- [ ] **Step 8: Verificar**

Run: `grep -c "fase-3" README.md` → ≥ 4 (badge, quick start, estrutura, entregáveis).
Run: `grep "Concluída" README.md | grep -c "3"` → a Fase 3 marcada concluída.

- [ ] **Step 9: Commit**

```bash
git add README.md
git commit -m "docs(fase-3): README — roadmap concluído, entregáveis 3.x, badge, consolidação"
```

---

### Task 7: Verificação final do marco + commit de fechamento

**Files:** nenhum novo — verificação holística.

- [ ] **Step 1: Suíte de testes**

Run: `pytest -q`
Expected: 276 passed (M4 não adiciona testes; nada deve quebrar).

- [ ] **Step 2: Notebook executa sem erro**

Run: `jupyter nbconvert --to notebook --execute --inplace fases/fase-3/notebook.ipynb`
Expected: sem exceção; reexecutável (idempotente).

- [ ] **Step 3: Smoke do CLI + determinismo**

Run:
```bash
A=$(python -m aurora_siger.operations.cli --frames 168 --plain)
B=$(python -m aurora_siger.operations.cli --frames 168 --plain)
[ "$A" = "$B" ] && echo "DETERMINÍSTICO" || echo "DIVERGIU"
```
Expected: `DETERMINÍSTICO`.

- [ ] **Step 4: Versão consistente em todos os lugares**

Run: `python -c "import aurora_siger; assert aurora_siger.__version__=='0.3.0'"` e `grep '0.3.0' pyproject.toml`.

- [ ] **Step 5: Re-sincronizar a memória do projeto**

Atualizar `memory/fase3-consolidacao.md` e `MEMORY.md`: Fase 3 **concluída** (M1–M4), versão 0.3.0, 276 testes. Registrar quaisquer dívidas remanescentes (ex.: kW/kWh em `simulator.step()`; type hints de M1/climate/simulator ainda pendentes).

- [ ] **Step 6: Notebook executado no commit final**

Garantir que o `notebook.ipynb` commitado contém os outputs populados (executado in-place). Se a verificação do Step 2 alterou o arquivo, commitar a versão executada.

```bash
git add -A && git commit -m "chore(fase-3): verificação final do marco M4 — Fase 3 concluída (0.3.0)"
```

---

## Self-Review

**Cobertura do spec (§2, §5, §6, §7):**
- §2 (mudanças de projeto): bump 0.3.0 (T1), console script `aurora` já feito no M3, README roadmap/entregáveis/badge (T6). ✓
- §5 (4 itens): notebook narra os 4 (T3) + relatório cobre os 4 (T4). ✓
- §6 (notebook/relatório/ensaio/autoria): T2 (ensaio), T3 (notebook), T4+T5 (relatório md+pdf), nota de consolidação + procedência em T4 e T6. ✓
- §7 (verificação final): pytest + nbconvert + CLI smoke + diff determinístico em T7. ✓

**Placeholders:** as tarefas de prosa (T2, T4) dão *estrutura de seções + pontos de conteúdo* em vez de texto literal — apropriado para prosa (não se "TDDa" um ensaio); não são placeholders vazios. As células do notebook (T3) trazem código real, com a ressalva explícita de **verificar as assinaturas reais** de `decision.py`/`prediction.py`/`analysis.py` antes de chamar (evita inventar nomes de função). Idem T5: inspecionar o `header.tex` da fase-2 antes de copiar.

**Consistência:** versão `0.3.0` referenciada igual em T1/T7; `run_simulation(seed=42)` é a fonte única de métricas para notebook (T3) e relatório (T4); CLI invocado como `python -m aurora_siger.operations.cli` (forma que funciona sem install editável, como verificado no M3).

**Risco conhecido:** matplotlib não está no `~/.venv` — T3 Step 2 instala se ausente. O wrapper `fases/fase-3/aurora_core.py` depende de install editável (igual ao `mgpeb` da Fase 2); por isso a verificação usa `python -m`.

---

## Execução

Marco de **prosa + notebook**: a execução é **inline nesta sessão pelo controlador** (não subagent-driven). Justificativa: ensaio e relatório exigem o contexto completo de todas as decisões de consolidação (M1–M3) que vivem nesta sessão — um subagente fresco perderia a nuance; o notebook precisa casar com a API real do pacote, já em contexto. Verificação por executabilidade + consistência, não por revisão de código dupla.
