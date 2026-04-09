# MGPEB Implementation Plan

> **Modo de execução:** Tarefa 1 é gerada pelo assistente (esqueleto). Tarefas 2-8 são implementadas pelo Iúri manualmente, usando os TODOs como guia.

**Goal:** Criar o protótipo Python do MGPEB — sistema de gerenciamento de pouso de 12 módulos na colônia Aurora Siger em Marte.

**Architecture:** Arquivo único `mgpeb.py`, paradigma procedural com dicionários como estrutura central. Funções puras organizadas em 8 seções lógicas. Sem bibliotecas externas além de `math`.

**Tech Stack:** Python 3, `math` (apenas `exp`, `sin`, `pi`)

---

### Task 1: Criar esqueleto do mgpeb.py (assistente)

**Files:**
- Create: `mgpeb.py`

O assistente gera o arquivo completo com:
- Todos os 12 módulos em `MODULES_DATA` com valores realistas
- Todas as assinaturas de funções com docstrings em português
- Estruturas de dados inicializadas
- Menu interativo funcional (estrutura do loop)
- Marcadores `# TODO:` em cada ponto onde Iúri implementa lógica

- [ ] **Step 1: Gerar mgpeb.py com esqueleto completo**
- [ ] **Step 2: Executar para verificar que roda sem erros (funções retornam None/pass)**

Run: `python3 mgpeb.py`
Expected: Menu aparece, opções respondem com mensagens placeholder

---

### Task 2: Implementar estruturas lineares

**Files:**
- Modify: `mgpeb.py` — seção [2] ESTRUTURAS LINEARES

Funções a implementar:

- [ ] **Step 1: `enqueue(queue, module)`**

Adiciona `module` ao final da lista `queue`. Uma linha.

```
Exemplo:
>>> fila = []
>>> enqueue(fila, {"name": "Teste"})
>>> fila
[{"name": "Teste"}]
```

- [ ] **Step 2: `dequeue(queue)`**

Remove e retorna o primeiro elemento. Retorna `None` se vazia.

```
Exemplo:
>>> fila = [{"name": "A"}, {"name": "B"}]
>>> dequeue(fila)
{"name": "A"}
>>> fila
[{"name": "B"}]
```

Dica: `list.pop(0)` remove o índice 0.

- [ ] **Step 3: `push(stack, item)`**

Adiciona `item` ao topo (final) da pilha. Uma linha.

- [ ] **Step 4: `pop(stack)`**

Remove e retorna o topo. Retorna `None` se vazia.

Dica: `list.pop()` sem argumento remove o último.

- [ ] **Step 5: `peek(stack)`**

Retorna o topo sem remover. Retorna `None` se vazia.

Dica: `stack[-1]` acessa o último elemento.

- [ ] **Step 6: `is_empty(structure)`**

Retorna `True` se a estrutura tem tamanho 0.

- [ ] **Step 7: Testar manualmente**

```python
# No terminal Python:
fila = []
enqueue(fila, "A")
enqueue(fila, "B")
print(dequeue(fila))  # "A"
print(is_empty(fila))  # False
print(dequeue(fila))  # "B"
print(is_empty(fila))  # True
```

---

### Task 3: Implementar regras lógicas de autorização

**Files:**
- Modify: `mgpeb.py` — seção [3] REGRAS LÓGICAS

- [ ] **Step 1: `check_landing_authorization(module, conditions)`**

`conditions` é um dict:
```python
conditions = {
    "atmosphere_ok": True,
    "landing_zone_free": True,
    "sensors_ok": True
}
```

Lógica booleana a implementar:
```
fuel_ok = module["fuel_level"] >= 20.0
emergency = module["cargo_criticality"] == 5

authorized = fuel_ok AND conditions["atmosphere_ok"] AND (conditions["landing_zone_free"] OR emergency) AND conditions["sensors_ok"]
```

Se `authorized` é `False`, criar um dict de alerta com:
- `"module_id"`: id do módulo
- `"module_name"`: nome do módulo
- `"reason"`: string descrevendo qual condição falhou
- `"timestamp"`: string com horário simulado

Empilhar o alerta na `alert_stack` global e retornar `False`.
Se autorizado, retornar `True`.

- [ ] **Step 2: Testar manualmente**

```python
# Módulo com combustível OK, carga crítica
mod = {"id": 1, "name": "Teste", "fuel_level": 50.0, "cargo_criticality": 5}
cond = {"atmosphere_ok": True, "landing_zone_free": False, "sensors_ok": True}
# Deve retornar True (emergency override)

mod2 = {"id": 2, "name": "Teste2", "fuel_level": 10.0, "cargo_criticality": 1}
cond2 = {"atmosphere_ok": True, "landing_zone_free": True, "sensors_ok": True}
# Deve retornar False (combustível insuficiente)
```

---

### Task 4: Implementar algoritmos de busca

**Files:**
- Modify: `mgpeb.py` — seção [4] BUSCA

- [ ] **Step 1: `search_by_type(modules, module_type)`**

Busca linear: percorrer `modules`, retornar lista com todos que têm `module["type"] == module_type`.

```
Exemplo:
>>> search_by_type(MODULES_DATA, "solar")
[{"id": 3, "name": "Energia Solar", ...}]
```

- [ ] **Step 2: `search_min_fuel(modules)`**

Busca linear pelo menor valor: inicializar com o primeiro, percorrer comparando `fuel_level`.

```
Exemplo:
>>> m = search_min_fuel(MODULES_DATA)
>>> print(m["name"], m["fuel_level"])
"Oficina e Manutenção" 28.0  # (depende dos dados)
```

- [ ] **Step 3: `search_highest_priority(modules)`**

Busca linear pelo menor número de `priority` (1 = máxima).

- [ ] **Step 4: Testar via menu (opção 3)**

---

### Task 5: Implementar algoritmos de ordenação

**Files:**
- Modify: `mgpeb.py` — seção [5] ORDENAÇÃO

- [ ] **Step 1: `sort_by_priority(modules)`**

Bubble Sort: dois loops aninhados. Loop externo `i` de 0 a n-1. Loop interno `j` de 0 a n-i-2. Se `modules[j]["priority"] > modules[j+1]["priority"]`, trocar (swap).

Otimização opcional: flag `swapped` — se nenhuma troca no loop interno, lista já está ordenada, pode parar.

```python
# Swap em Python:
modules[j], modules[j+1] = modules[j+1], modules[j]
```

Retorna a lista ordenada (in-place, mas retorna também para conveniência).

- [ ] **Step 2: `sort_by_fuel(modules)`**

Selection Sort: loop externo `i` de 0 a n-1. Encontrar o índice do menor `fuel_level` de `i` até o final. Trocar `modules[i]` com `modules[min_idx]`.

```python
# Estrutura:
for i in range(n):
    min_idx = i
    for j in range(i + 1, n):
        if modules[j]["fuel_level"] < modules[min_idx]["fuel_level"]:
            min_idx = j
    modules[i], modules[min_idx] = modules[min_idx], modules[i]
```

- [ ] **Step 3: Testar via menu (opção 2)**

Verificar que a fila é reordenada corretamente após cada ordenação.

---

### Task 6: Implementar funções matemáticas

**Files:**
- Modify: `mgpeb.py` — seção [6] FUNÇÕES MATEMÁTICAS

Cada função recebe parâmetros e retorna um `float`. Usar `import math` no topo do arquivo.

- [ ] **Step 1: `descent_altitude(t, h0, v0, a)`**

```
h(t) = h0 - v0 * t - 0.5 * a * t**2
```

Uma linha de retorno.

- [ ] **Step 2: `fuel_consumption(v, c0, k)`**

```
C(v) = c0 * math.exp(k * v)
```

Uma linha de retorno.

- [ ] **Step 3: `solar_energy(t, a_coeff, t_mid, e_max)`**

```
E(t) = -a_coeff * (t - t_mid)**2 + e_max
```

Uma linha de retorno.

- [ ] **Step 4: `surface_temperature(t, t_avg, amplitude, period, phase)`**

```
T(t) = t_avg + amplitude * math.sin(2 * math.pi * t / period - phase)
```

Uma linha de retorno.

- [ ] **Step 5: Testar manualmente**

```python
# Descida: altitude deve diminuir com o tempo
for t in range(0, 60, 10):
    print(f"t={t}s → h={descent_altitude(t, 120000, 500, 3.7):.0f}m")

# Energia solar: pico no meio do dia, zero nas bordas
for t in range(0, 25):
    print(f"t={t}h → E={solar_energy(t, 15, 12, 2200):.0f}W")
```

---

### Task 7: Implementar simulação de pouso

**Files:**
- Modify: `mgpeb.py` — seção [7] SIMULAÇÃO

- [ ] **Step 1: `run_landing_simulation()`**

Lógica:
1. Copiar `MODULES_DATA` para `landing_queue` (usar `list()` ou list comprehension com `.copy()` de cada dict)
2. Chamar `sort_by_priority(landing_queue)`
3. Definir `conditions` simuladas (atmosfera, zona, sensores)
4. Loop `while not is_empty(landing_queue)`:
   a. `module = dequeue(landing_queue)`
   b. `authorized = check_landing_authorization(module, conditions)`
   c. Se autorizado: `module["status"] = "landed"`, adicionar a `landed_modules`
   d. Se não: `module["status"] = "waiting"`, adicionar a `waiting_modules`
   e. Imprimir resultado de cada módulo
5. Exibir resumo final: total pousados, em espera, alertas

Dica importante: copiar os dicts com `.copy()` para não alterar `MODULES_DATA` original.

- [ ] **Step 2: Testar via menu (opção 4)**

Simular com condições variadas:
- Todas as condições OK → todos pousam
- Zona de pouso ocupada → apenas emergências passam
- Sensores com falha → nenhum pousa

---

### Task 8: Completar menu interativo

**Files:**
- Modify: `mgpeb.py` — seção [8] MAIN

- [ ] **Step 1: Implementar cada opção do menu**

O esqueleto já tem a estrutura do loop e os `input()`. Conectar cada opção à função correspondente:

| Opção | Ação |
|-------|------|
| 1 | Exibir `landing_queue` formatada |
| 2 | Submenu: ordenar por prioridade ou combustível |
| 3 | Pedir tipo via `input()`, chamar `search_by_type()` |
| 4 | Chamar `run_landing_simulation()` |
| 5 | Exibir `alert_stack` (do topo pra base) |
| 6 | Submenu: calcular cada função matemática com valores de input |
| 0 | Sair |

- [ ] **Step 2: `display_module(module)`**

Função auxiliar para exibir um módulo formatado:
```
[ID: 01] Comando e Controle | Prioridade: 1 | Combustível: 85.0% | Massa: 12000kg | Status: queued
```

- [ ] **Step 3: `display_queue(queue, title)`**

Loop que chama `display_module()` para cada item, com cabeçalho `title`.

- [ ] **Step 4: Teste final end-to-end**

Executar `python3 mgpeb.py`, testar todas as opções do menu em sequência.
