# MGPEB — Design Spec

**Projeto**: Módulo de Gerenciamento de Pouso e Estabilização de Base (Aurora Siger)
**Disciplina**: Atividade Integradora — FIAP Fase 2
**Equipe**: Gabriel Carmona, Carlos Eugênio, Marcio Francisco, Iúri Leão, Maria Sophia
**Prazo**: 28/04/2026
**Data do design**: 04/04/2026

---

## 1. Visão geral

Sistema em Python (procedural, sem bibliotecas externas) que simula o gerenciamento de pouso de 12 módulos de uma colônia em Marte. Usa dicionários como estrutura de dados central, listas puras para fila/pilha, algoritmos manuais de busca e ordenação, regras de decisão modeladas com expressões booleanas e funções matemáticas para fenômenos físicos do pouso.

**Abordagem escolhida**: Dicionários como "structs" (Abordagem C). Cada módulo é um `dict` com chaves nomeadas. Filas e pilhas são listas de dicts manipuladas por funções. Nomes de código em inglês, comentários/docstrings em português.

**Entrega de código**: Iúri implementa toda a lógica. O esqueleto (boilerplate, assinaturas, TODOs) é gerado como ponto de partida.

---

## 2. Módulos de pouso (12)

| ID | Nome | type | Justificativa |
|----|------|------|---------------|
| 1 | Comando e Controle | `command` | Centro de operações — pousa primeiro |
| 2 | Habitação | `habitat` | Abrigo da tripulação |
| 3 | Energia Solar | `solar` | Painéis e baterias |
| 4 | Energia Nuclear | `nuclear` | Reator de fissão (redundância) |
| 5 | Suporte de Vida (ECLSS) | `life_support` | O₂, reciclagem de água/CO₂ |
| 6 | Suporte Médico | `medical` | Enfermaria, farmácia, emergência |
| 7 | Laboratório Científico | `lab` | Geologia, biologia, atmosfera |
| 8 | Produção de Alimentos | `food` | Estufa hidropônica |
| 9 | Logística e Armazenamento | `logistics` | Peças, suprimentos, ferramentas |
| 10 | Oficina e Manutenção | `workshop` | Fabricação e reparo |
| 11 | Comunicações | `comms` | Antenas deep-space, relay orbital |
| 12 | ISRU | `isru` | Extração de recursos locais (água, propelente) |

### Atributos de cada módulo (dict)

```python
module = {
    "id": int,                    # Identificador único (1-12)
    "name": str,                  # Nome do módulo
    "type": str,                  # Tipo (chave curta para buscas)
    "priority": int,              # Prioridade de pouso (1 = máxima)
    "fuel_level": float,          # Nível de combustível (%)
    "mass": float,                # Massa em kg
    "cargo_criticality": int,     # Criticidade da carga (1-5, 5 = crítica)
    "estimated_arrival": str,     # Horário estimado (HH:MM)
    "status": str                 # "queued" | "landed" | "waiting" | "alert"
}
```

---

## 3. Estruturas lineares

### Estruturas

| Variável | Tipo | Uso |
|----------|------|-----|
| `landing_queue` | Lista (FIFO) | Módulos aguardando autorização de pouso |
| `landed_modules` | Lista | Módulos já pousados |
| `waiting_modules` | Lista | Módulos com pouso adiado |
| `alert_stack` | Lista (LIFO) | Alertas — último empilhado = mais recente |

### Funções de manipulação

| Função | Operação |
|--------|----------|
| `enqueue(queue, module)` | Adiciona ao final da fila |
| `dequeue(queue)` | Remove e retorna o primeiro da fila |
| `push(stack, item)` | Adiciona ao topo da pilha |
| `pop(stack)` | Remove e retorna o topo da pilha |
| `peek(stack)` | Consulta o topo sem remover |
| `is_empty(structure)` | Retorna True se a estrutura está vazia |

---

## 4. Regras de decisão (Portas lógicas)

### Variáveis booleanas

| Variável | Símbolo | Condição para True |
|----------|---------|---------------------|
| Combustível suficiente | F | `fuel_level >= 20.0` |
| Condições atmosféricas OK | A | Flag simulada |
| Área de pouso disponível | L | Nenhum módulo pousando no momento |
| Sensores íntegros | S | Flag simulada |
| Emergência | E | `cargo_criticality == 5` (NOT aplicado) |

### Expressão booleana

```
AUTORIZADO = F AND A AND (L OR E) AND S
```

### Portas lógicas (diagrama)

```
F ──────────────────┐
                    ├── AND ──┐
A ──────────────────┘         │
                              ├── AND ── AUTORIZADO
L ──────────┐                 │
            ├── OR ───────────┘
E (NOT) ────┘         │
                      │
S ────────────────────┘
```

*(Diagrama formal com portas AND/OR/NOT será produzido para o relatório PDF)*

Quando `AUTORIZADO = False`, a função `check_landing_authorization()` empilha um alerta na `alert_stack` com o motivo específico do bloqueio.

---

## 5. Algoritmos de busca e ordenação

### Busca (linear)

| Função | Critério | Retorno |
|--------|----------|---------|
| `search_by_type(modules, type)` | Tipo do módulo | Lista de módulos do tipo |
| `search_min_fuel(modules)` | Menor combustível | Módulo com menor `fuel_level` |
| `search_highest_priority(modules)` | Maior prioridade | Módulo com menor `priority` (1 = máx) |

### Ordenação (manual)

| Função | Algoritmo | Critério |
|--------|-----------|----------|
| `sort_by_priority(modules)` | Bubble Sort | `priority` ascendente |
| `sort_by_fuel(modules)` | Selection Sort | `fuel_level` ascendente |

Dois algoritmos diferentes para demonstrar conhecimento e permitir comparação no relatório.

---

## 6. Funções matemáticas

### 6a) Altura na descida — Quadrática

```
h(t) = h₀ - v₀·t - ½·a·t²
```

- h₀ = altitude inicial (ex: 120 km)
- v₀ = velocidade inicial de descida
- a = aceleração de frenagem (retrofoguetes)
- Aplicação: determinar momento de acionar retrofoguetes

Função: `descent_altitude(t, h0, v0, a)`

### 6b) Consumo de combustível vs velocidade — Exponencial

```
C(v) = C₀ · e^(k·v)
```

- C₀ = consumo base
- k = coeficiente de crescimento
- Aplicação: justificar desaceleração gradual vs. frenagem brusca

Função: `fuel_consumption(v, c0, k)` (usa `math.exp`)

### 6c) Geração de energia solar — Quadrática (parábola invertida)

```
E(t) = -a·(t - t_meio)² + E_max
```

- t_meio = meio do dia marciano
- E_max = geração máxima
- Aplicação: determinar janelas de pouso com energia suficiente

Função: `solar_energy(t, a, t_mid, e_max)`

### 6d) Temperatura externa — Senoidal

```
T(t) = T_media + A · sin(2π·t / P - φ)
```

- T_media ≈ -60°C, A ≈ 40°C, P ≈ 24.62h (sol marciano)
- Aplicação: restringir pousos a faixas de temperatura aceitáveis

Função: `surface_temperature(t, t_avg, amplitude, period, phase)` (usa `math.sin`, `math.pi`)

---

## 7. Estrutura do arquivo Python

```
mgpeb.py
├── [1] DADOS — MODULES_DATA (12 dicts) + condições simuladas
├── [2] ESTRUTURAS LINEARES — enqueue, dequeue, push, pop, peek, is_empty
├── [3] REGRAS LÓGICAS — check_landing_authorization
├── [4] BUSCA — search_by_type, search_min_fuel, search_highest_priority
├── [5] ORDENAÇÃO — sort_by_priority, sort_by_fuel
├── [6] FUNÇÕES MATEMÁTICAS — descent_altitude, fuel_consumption, solar_energy, surface_temperature
├── [7] SIMULAÇÃO — run_landing_simulation (loop principal)
└── [8] MAIN — menu interativo
```

### Fluxo da simulação (seção 7)

1. Carrega os 12 módulos na `landing_queue`
2. Ordena por prioridade
3. Para cada módulo no front da fila:
   - Verifica autorização (`check_landing_authorization`)
   - Se autorizado → `dequeue` + adiciona em `landed_modules`
   - Se bloqueado → move para `waiting_modules` + empilha alerta
4. Exibe resumo: pousados, em espera, alertas

### Menu (seção 8)

```
1. Ver fila de pouso
2. Ordenar por prioridade / combustível
3. Buscar módulo por tipo
4. Executar simulação de pouso
5. Ver pilha de alertas
0. Sair
```

---

## 8. Contextualização histórica — Roteiro de conteúdo

A seção deve traçar um arco narrativo: da computação primitiva até os sistemas embarcados que sustentariam o MGPEB em Marte.

### 8a) Dos computadores de propósito geral aos sistemas embarcados espaciais

- **ENIAC (1946)**: 30 toneladas, 18.000 válvulas, programado por fiação física. Calculava trajetórias balísticas — o ancestral direto do cálculo de trajetórias orbitais. Um MGPEB nessa era seria um salão inteiro de válvulas.
- **Transistor e miniaturização (anos 1950-60)**: A transição válvula → transistor → circuito integrado possibilitou que computadores saíssem de salas e entrassem em foguetes.
- **Apollo Guidance Computer (1966)**: 32 kg, 74 KB de ROM, 4 KB de RAM, clock de 2 MHz. Navegou humanos à Lua com menos poder computacional que uma calculadora moderna. Usava listas encadeadas em memória fixa — uma decisão de estrutura de dados ditada pela escassez de hardware, exatamente o tipo de trade-off que o MGPEB enfrentaria.
- **Voyager 1 e 2 (1977)**: Ainda operacionais em 2026, com 69 KB de memória e processador de 250 kHz. Demonstram que software confiável compensa hardware limitado — princípio central de sistemas espaciais.
- **Mars rovers (Sojourner → Curiosity → Perseverance)**: RAD750 com 256 MB de RAM e 200 MHz, radiation-hardened. O Perseverance roda VxWorks (RTOS) e prioriza determinismo sobre velocidade. Cada instrução conta.

### 8b) Limitações de hardware em Marte e impacto no MGPEB

| Limitação | Realidade em Marte | Impacto nas escolhas do MGPEB |
|-----------|-------------------|-------------------------------|
| **Radiação cósmica** | Sem magnetosfera, partículas de alta energia causam bit-flips em memória | Processadores rad-hard são ~10x mais lentos que comerciais; algoritmos devem ser simples e verificáveis |
| **Comunicação** | Delay de 4-24 min com a Terra; janelas de comunicação limitadas | O MGPEB precisa ser autônomo — não pode esperar comando terrestre para autorizar pousos |
| **Energia** | Painéis solares geram ~600 W (Curiosity: RTG ~110 W); tempestades de poeira reduzem drasticamente | Cada ciclo de CPU custa energia; algoritmos O(n²) com n=12 são aceitáveis, mas O(n!) seria proibitivo |
| **Memória** | 256 MB típico em sistemas rad-hard | Dicionários em Python são luxo terrestre; em Marte, structs compactas em C. Nosso protótipo simula a lógica, não o hardware real |
| **Temperatura** | -120°C a +20°C; eletrônica precisa de aquecimento ativo | Ciclos de processamento geram calor — computação pesada pode servir dupla função em ambientes gelados |
| **Redundância** | Falhas não podem ser reparadas rapidamente | Sistemas votam entre si (redundância tripla no Apollo); nosso `alert_stack` é uma versão simplificada de log de falhas |

### 8c) Conexão com as escolhas de algoritmos do projeto

- **Bubble Sort e Selection Sort** são O(n²), mas com n=12 módulos isso significa no máximo 144 comparações — trivial até para um processador de 200 MHz. Em hardware limitado, a previsibilidade (sem alocação dinâmica, sem recursão profunda) vale mais que a velocidade assintótica.
- **Busca linear** evita estruturas auxiliares (árvores, hash tables) que consumiriam memória preciosa.
- **Expressões booleanas** são determinísticas e executam em tempo constante — exatamente o que se quer para decisões críticas de segurança onde o resultado deve ser previsível a cada ciclo.
- **Fila e pilha com listas** têm comportamento O(1) no append/pop do final; o `pop(0)` da fila é O(n), mas com n=12 é irrelevante. Em um sistema real, seria implementado como buffer circular em memória fixa.

---

## 9. Reflexão ESG — Roteiro de conteúdo

A seção deve ir além de platitudes e ancorar cada princípio em decisões concretas do MGPEB e da colônia.

### 9a) Ambiental — Proteção planetária e sustentabilidade

**Escolha da área de pouso:**
- O Protocolo de Proteção Planetária (COSPAR) classifica missões em categorias I-V. Uma colônia em Marte seria Categoria V (retorno de amostras) ou além — o mais restritivo. O MGPEB deve considerar:
  - Evitar Regiões Especiais (RSRs): áreas com possível água líquida sazonal (recurring slope lineae), onde vida microbiana é mais provável
  - Distância mínima de sítios de interesse científico (para não contaminar antes de estudar)
  - Terreno estável (planícies de baixa inclinação, sem dunas ativas)
- No código, isso poderia ser uma variável adicional de condição de pouso (não implementada, mas mencionada no relatório)

**Gestão de recursos e resíduos:**
- **Ciclo fechado de água**: o módulo ECLSS recicla ~93% da água (ISS real: 93.5%). Cada litro perdido custa propelente para repor da Terra
- **Atmosfera**: CO₂ marciano (95%) → MOXIE (Mars Oxygen ISRU Experiment) → O₂. O módulo ISRU é a chave
- **Resíduos sólidos**: sem aterro em Marte. Incineração controlada (recupera energia) ou reciclagem molecular. Lixo orgânico vira composto para estufa hidropônica
- **Propelente**: Sabatier reaction (CO₂ + H₂ → CH₄ + H₂O) produz metano para retorno e operações — o módulo ISRU fecha esse ciclo

### 9b) Social — Governança participativa e bem-estar

**Critérios de prioridade:**
- A fila de pouso prioriza módulos de suporte de vida sobre laboratório — é uma decisão ética (sobrevivência > ciência). O grupo deve argumentar por que essa hierarquia é justa e como seria revisada
- Em emergência médica, o módulo médico sobe na fila — o sistema codifica o valor de que saúde é prioridade, uma decisão social embutida em algoritmo

**Transparência algorítmica:**
- O `alert_stack` funciona como log auditável — qualquer colono pode consultar por que um pouso foi adiado
- Decisões automatizadas (expressões booleanas) devem ser documentadas e compreensíveis por não-engenheiros
- Analogia com a Lei Geral de Proteção de Dados (LGPD, Art. 20): direito a explicação sobre decisões automatizadas

**Bem-estar e participação:**
- Isolamento extremo (meses de viagem, delay de comunicação) exige estruturas de apoio psicossocial
- Governança por consenso vs. hierarquia: em emergências, o MGPEB decide automaticamente (hierarquia); em operações normais, colegiado humano pode reordenar a fila (participação)
- Representatividade: critérios de seleção da tripulação devem considerar diversidade de competências e perspectivas

### 9c) Governança corporativa — Ética e responsabilidade

**Propriedade e uso de recursos:**
- Tratado do Espaço Exterior (1967, Art. II): nenhuma nação pode reivindicar soberania sobre Marte. Mas e uma colônia privada? O MGPEB gerencia recursos que beneficiam quem?
- Proposta: recursos extraídos pelo ISRU são commons (bem comum da colônia), geridos por comitê eleito, com relatórios periódicos de consumo acessíveis a todos

**Responsabilidade algorítmica:**
- Se o MGPEB adia um pouso e o módulo perde combustível irrecuperavelmente, quem é responsável? O algoritmo? O engenheiro que definiu os limiares? O comitê de governança?
- Argumento: o sistema deve ter override humano documentado — a máquina recomenda, o humano autoriza (human-in-the-loop), exceto em emergências onde o delay humano é inaceitável

**Sustentabilidade de longo prazo:**
- A colônia deve planejar para gerações, não apenas para a missão inicial
- Modularidade do MGPEB permite expansão: novos módulos futuros entram na mesma fila com os mesmos critérios — o sistema escala sem mudar a lógica
- Documentação técnica como patrimônio: o código e as regras devem ser compreensíveis por quem chegar depois, não apenas pelos desenvolvedores originais

---

## 10. Seções do relatório (PDF, 5-10 páginas)

1. Descrição do cenário e dos 12 módulos
2. Diagramas de portas lógicas (AND, OR, NOT)
3. Modelagem das 4 funções matemáticas (fórmulas, parâmetros, gráficos, análise)
4. Contextualização histórica (seção 8 deste spec)
5. Reflexão ESG (seção 9 deste spec)
6. Anexo: estruturas de dados (como listas, filas e pilhas foram usadas, com exemplos)

---

## 11. Decisões de implementação

- **Linguagem**: Python 3, sem bibliotecas além de `math` (para `exp`, `sin`, `pi`)
- **Paradigma**: Procedural — funções puras + dicionários
- **Nomenclatura**: Código em inglês, comentários/docstrings em português
- **Arquivo único**: `mgpeb.py`
- **Implementação**: Iúri escreve toda a lógica; esqueleto gerado com assinaturas + TODOs
