"""
MGPEB — Módulo de Gerenciamento de Pouso e Estabilização de Base
Missão Aurora Siger — Colônia em Marte

Atividade Integradora — FIAP Fase 2
Equipe: Gabriel Carmona, Carlos Eugênio, Marcio Francisco, Iúri Leão, Maria Sophia

Este módulo simula o sistema responsável por organizar pousos de módulos
da colônia, gerenciar informações da operação e aplicar regras de decisão
baseadas em lógica booleana, utilizando estruturas de dados lineares,
algoritmos clássicos de busca e ordenação, e funções matemáticas aplicadas.
"""

import math


# =============================================================================
# [1] DADOS — Módulos da colônia e condições simuladas
# =============================================================================

# Dados dos 12 módulos da colônia Aurora Siger.
# Cada módulo é um dicionário com atributos relevantes para o pouso.
MODULES_DATA = [
    {
        "id": 1,
        "name": "Comando e Controle",
        "type": "command",
        "priority": 1,
        "fuel_level": 85.0,
        "mass": 12000.0,
        "cargo_criticality": 5,
        "estimated_arrival": "06:30",
        "status": "queued",
    },
    {
        "id": 2,
        "name": "Suporte de Vida (ECLSS)",
        "type": "life_support",
        "priority": 2,
        "fuel_level": 78.0,
        "mass": 15000.0,
        "cargo_criticality": 5,
        "estimated_arrival": "06:45",
        "status": "queued",
    },
    {
        "id": 3,
        "name": "Habitação",
        "type": "habitat",
        "priority": 3,
        "fuel_level": 72.0,
        "mass": 18000.0,
        "cargo_criticality": 4,
        "estimated_arrival": "07:15",
        "status": "queued",
    },
    {
        "id": 4,
        "name": "Energia Solar",
        "type": "solar",
        "priority": 4,
        "fuel_level": 65.0,
        "mass": 8000.0,
        "cargo_criticality": 5,
        "estimated_arrival": "07:45",
        "status": "queued",
    },
    {
        "id": 5,
        "name": "Energia Nuclear",
        "type": "nuclear",
        "priority": 5,
        "fuel_level": 58.0,
        "mass": 22000.0,
        "cargo_criticality": 5,
        "estimated_arrival": "08:30",
        "status": "queued",
    },
    {
        "id": 6,
        "name": "Comunicações",
        "type": "comms",
        "priority": 6,
        "fuel_level": 55.0,
        "mass": 6000.0,
        "cargo_criticality": 4,
        "estimated_arrival": "07:00",
        "status": "queued",
    },
    {
        "id": 7,
        "name": "Suporte Médico",
        "type": "medical",
        "priority": 7,
        "fuel_level": 70.0,
        "mass": 10000.0,
        "cargo_criticality": 4,
        "estimated_arrival": "08:00",
        "status": "queued",
    },
    {
        "id": 8,
        "name": "Produção de Alimentos",
        "type": "food",
        "priority": 8,
        "fuel_level": 60.0,
        "mass": 14000.0,
        "cargo_criticality": 3,
        "estimated_arrival": "09:15",
        "status": "queued",
    },
    {
        "id": 9,
        "name": "Logística e Armazenamento",
        "type": "logistics",
        "priority": 9,
        "fuel_level": 45.0,
        "mass": 25000.0,
        "cargo_criticality": 3,
        "estimated_arrival": "09:45",
        "status": "queued",
    },
    {
        "id": 10,
        "name": "ISRU (Recursos Locais)",
        "type": "isru",
        "priority": 10,
        "fuel_level": 42.0,
        "mass": 20000.0,
        "cargo_criticality": 2,
        "estimated_arrival": "11:30",
        "status": "queued",
    },
    {
        "id": 11,
        "name": "Oficina e Manutenção",
        "type": "workshop",
        "priority": 11,
        "fuel_level": 15.0,       # Abaixo do limiar de 20% — será bloqueado
        "mass": 16000.0,
        "cargo_criticality": 2,
        "estimated_arrival": "11:00",
        "status": "queued",
    },
    {
        "id": 12,
        "name": "Laboratório Científico",
        "type": "lab",
        "priority": 12,
        "fuel_level": 82.0,
        "mass": 12000.0,
        "cargo_criticality": 2,
        "estimated_arrival": "10:00",
        "status": "queued",
    },
]

# Estruturas lineares globais
landing_queue = []          # Fila (FIFO) — módulos aguardando autorização de pouso
landed_modules = []         # Lista — módulos já pousados com sucesso
waiting_modules = []        # Lista — módulos com pouso adiado
alert_stack = []            # Pilha (LIFO) — registros de alertas de bloqueio

# Condições de pouso (configuráveis pelo operador via menu)
landing_conditions = {
    "atmosphere_ok": True,          # Condições atmosféricas favoráveis
    "landing_zone_free": True,      # Zona de pouso disponível
    "sensors_ok": True,             # Integridade dos sensores
}


# =============================================================================
# [2] ESTRUTURAS LINEARES — Operações de fila, pilha e verificação
# =============================================================================

def enqueue(queue, module):
    """Adiciona um módulo ao final da fila (operação FIFO)."""
    queue.append(module)


def dequeue(queue):
    """
    Remove e retorna o primeiro módulo da fila (operação FIFO).
    Retorna None se a fila estiver vazia.
    """
    if len(queue) == 0:
        return None
    return queue.pop(0)


def push(stack, item):
    """Adiciona um item ao topo da pilha (operação LIFO)."""
    stack.append(item)


def pop(stack):
    """
    Remove e retorna o item do topo da pilha (operação LIFO).
    Retorna None se a pilha estiver vazia.
    """
    if len(stack) == 0:
        return None
    return stack.pop()


def peek(stack):
    """
    Consulta o item do topo da pilha sem removê-lo.
    Retorna None se a pilha estiver vazia.
    """
    if len(stack) == 0:
        return None
    return stack[-1]


def is_empty(structure):
    """Verifica se uma estrutura (fila, pilha ou lista) está vazia."""
    return len(structure) == 0


# =============================================================================
# [3] REGRAS LÓGICAS — Autorização de pouso com expressões booleanas
# =============================================================================

def check_landing_authorization(module, conditions):
    """
    Verifica se um módulo está autorizado a pousar com base em regras booleanas.

    Expressão lógica implementada:
        AUTORIZADO = F AND A AND (L OR E) AND S

    Variáveis:
        F = combustível suficiente (fuel_level >= 20%)
        A = condições atmosféricas favoráveis
        L = zona de pouso livre
        S = sensores íntegros
        E = emergência (cargo_criticality == 5) — porta NOT sobre normalidade
        

    Quando o pouso é negado, um alerta é empilhado na alert_stack
    contendo o motivo do bloqueio.

    Retorna: True se autorizado, False caso contrário.
    """

    fuel_ok = module["fuel_level"] >= 20
    atmosphere_ok = conditions["atmosphere_ok"]
    zone_free = conditions["landing_zone_free"]
    sensors_ok = conditions["sensors_ok"]
    emergency = module["cargo_criticality"] == 5

    authorized = fuel_ok and atmosphere_ok and (zone_free or emergency) and sensors_ok

    if not authorized:
        reasons = []
        if not fuel_ok:
            reasons.append(f"Combustível insuficiente ({module['fuel_level']:.1f}%)")
        if not atmosphere_ok:
            reasons.append("Condições atmosféricas desfavoráveis")
        if not zone_free and not emergency:
            reasons.append("Zona de pouso ocupada")
        if not sensors_ok:
            reasons.append("Falha nos sensores")

        alert = {
            "id": module["id"],
            "name": module["name"],
            "reason": "; ".join(reasons),
            "timestamp": module["estimated_arrival"],
        }
        push(alert_stack, alert)

    return authorized


# =============================================================================
# [4] BUSCA — Algoritmos de busca linear
# =============================================================================

def search_by_type(modules, module_type):
    """
    Busca linear por tipo: percorre a lista e retorna todos os módulos
    cujo campo 'type' corresponde ao tipo buscado.

    Complexidade: O(n) — percorre todos os elementos uma vez.
    """
    # TODO: criar lista vazia results
    # TODO: percorrer modules, adicionando a results os que têm type == module_type
    # TODO: retornar results
    pass


def search_min_fuel(modules):
    """
    Busca linear pelo menor valor: retorna o módulo com menor
    nível de combustível na lista.

    Inicializa com o primeiro elemento e compara com cada subsequente.
    Complexidade: O(n).
    """
    # TODO: verificar se modules está vazia (retornar None)
    # TODO: inicializar min_module com modules[0]
    # TODO: percorrer de 1 a len(modules), comparando fuel_level
    # TODO: retornar min_module
    pass


def search_highest_priority(modules):
    """
    Busca linear pela maior prioridade: retorna o módulo com menor
    valor numérico de prioridade (1 = máxima, 12 = mínima).

    Complexidade: O(n).
    """
    # TODO: verificar se modules está vazia (retornar None)
    # TODO: inicializar best com modules[0]
    # TODO: percorrer de 1 a len(modules), comparando priority (menor = melhor)
    # TODO: retornar best
    pass


# =============================================================================
# [5] ORDENAÇÃO — Bubble Sort e Selection Sort
# =============================================================================

def sort_by_priority(modules):
    """
    Bubble Sort: ordena a lista de módulos por prioridade (ascendente).

    Percorre a lista repetidamente, comparando pares adjacentes e
    trocando-os se estiverem fora de ordem. A flag 'swapped' permite
    encerrar antecipadamente se a lista já estiver ordenada.

    Complexidade: O(n²) no pior caso, O(n) no melhor caso (já ordenada).
    """
    n = len(modules)
    # TODO: loop externo i de 0 a n
    #   TODO: inicializar swapped = False
    #   TODO: loop interno j de 0 a n - i - 1
    #     TODO: se modules[j]["priority"] > modules[j+1]["priority"], trocar
    #       Swap: modules[j], modules[j+1] = modules[j+1], modules[j]
    #       swapped = True
    #   TODO: se not swapped, break (lista já está ordenada)
    return modules


def sort_by_fuel(modules):
    """
    Selection Sort: ordena a lista de módulos por combustível (ascendente).

    Para cada posição, encontra o menor elemento na parte não ordenada
    e o coloca na posição correta. Faz no máximo n trocas.

    Complexidade: O(n²) em todos os casos, mas eficiente em trocas.
    """
    n = len(modules)
    # TODO: loop externo i de 0 a n
    #   TODO: inicializar min_idx = i
    #   TODO: loop interno j de i+1 a n
    #     TODO: se modules[j]["fuel_level"] < modules[min_idx]["fuel_level"]
    #       min_idx = j
    #   TODO: se min_idx != i, trocar modules[i] com modules[min_idx]
    return modules


# =============================================================================
# [6] FUNÇÕES MATEMÁTICAS — Modelagem de fenômenos do pouso
# =============================================================================

def descent_altitude(t, h0=2000.0, v0=80.0, a=3.7):
    """
    Calcula a altitude durante a descida de um módulo em Marte.

    Fórmula: h(t) = h₀ - v₀·t - ½·a·t²
    Modelo: queda livre sob gravidade marciana (fase antes dos retrofoguetes).

    Parâmetros:
        t: tempo em segundos desde o início da descida
        h0: altitude inicial em metros (padrão: 2000m — fase final)
        v0: velocidade inicial de descida em m/s (padrão: 80 m/s)
        a: aceleração gravitacional em m/s² (padrão: 3.7 — Marte)

    Retorna: altitude em metros
    """
    # TODO: retornar h0 - v0 * t - 0.5 * a * t ** 2
    pass


def fuel_consumption(v, c0=10.0, k=0.02):
    """
    Calcula o consumo de combustível em função da velocidade de frenagem.

    Fórmula: C(v) = C₀ · e^(k·v)
    Modelo: relação exponencial — frenagem brusca consome exponencialmente
    mais combustível do que frenagem gradual.

    Parâmetros:
        v: velocidade de frenagem em m/s
        c0: consumo base em kg/s (padrão: 10.0)
        k: coeficiente de crescimento exponencial (padrão: 0.02)

    Retorna: consumo de combustível em kg/s
    """
    # TODO: retornar c0 * math.exp(k * v)
    pass


def solar_energy(t, a_coeff=15.0, t_mid=12.3, e_max=2200.0):
    """
    Calcula a geração de energia solar ao longo do dia marciano.

    Fórmula: E(t) = -a·(t - t_meio)² + E_max
    Modelo: parábola invertida com geração máxima ao meio-dia marciano
    e zero ao nascer/pôr do sol.

    Parâmetros:
        t: hora do dia marciano (0 a ~24.6h, duração de um 'sol')
        a_coeff: coeficiente de abertura da parábola (padrão: 15.0)
        t_mid: hora do pico solar (padrão: 12.3h)
        e_max: geração máxima em watts (padrão: 2200.0)

    Retorna: energia gerada em watts (mínimo 0)
    """
    # TODO: calcular energy = -a_coeff * (t - t_mid) ** 2 + e_max
    # TODO: se energy < 0, retornar 0.0
    # TODO: retornar energy
    pass


def surface_temperature(t, t_avg=-60.0, amplitude=40.0, period=24.62, phase=0.0):
    """
    Calcula a temperatura na superfície marciana ao longo do dia.

    Fórmula: T(t) = T_média + A · sin(2π·t / P - φ)
    Modelo: variação senoidal com ciclo de um sol marciano (~24h37min).
    Temperatura média de -60°C com amplitude de 40°C.

    Parâmetros:
        t: hora do dia marciano (0 a ~24.6h)
        t_avg: temperatura média em °C (padrão: -60.0)
        amplitude: amplitude da variação em °C (padrão: 40.0)
        period: duração do sol marciano em horas (padrão: 24.62)
        phase: deslocamento de fase em radianos (padrão: 0.0)

    Retorna: temperatura em °C
    """
    # TODO: retornar t_avg + amplitude * math.sin(2 * math.pi * t / period - phase)
    pass


# =============================================================================
# [7] SIMULAÇÃO — Execução do pouso sequencial
# =============================================================================

def load_modules():
    """
    Carrega os módulos na fila de pouso a partir dos dados originais.
    Reinicia todas as estruturas para uma nova simulação.
    Cria cópias independentes (dict()) para preservar MODULES_DATA.
    """
    global landing_queue, landed_modules, waiting_modules, alert_stack
    # TODO: reiniciar as 4 estruturas como listas vazias
    # TODO: percorrer MODULES_DATA e enqueue(landing_queue, dict(module))
    #   Nota: dict(module) cria uma cópia para não alterar os dados originais
    pass


def run_landing_simulation():
    """
    Executa a simulação completa de pouso dos módulos da colônia.

    Fluxo:
        1. Recarrega todos os módulos na fila de pouso
        2. Ordena a fila por prioridade (Bubble Sort)
        3. Processa cada módulo: verifica autorização via regras booleanas
        4. Módulos autorizados vão para landed_modules
        5. Módulos bloqueados vão para waiting_modules + alerta na pilha
        6. Exibe resumo completo da operação
    """
    # TODO: chamar load_modules() e sort_by_priority(landing_queue)

    # TODO: imprimir cabeçalho da simulação com condições atuais
    #   Dica: landing_conditions["atmosphere_ok"] → "OK" ou "DESFAVORÁVEL"

    # TODO: loop while not is_empty(landing_queue):
    #   module = dequeue(landing_queue)
    #   authorized = check_landing_authorization(module, landing_conditions)
    #   Se autorizado:
    #     module["status"] = "landed"
    #     adicionar a landed_modules
    #     imprimir "[AUTORIZADO] nome"
    #   Se bloqueado:
    #     module["status"] = "waiting"
    #     adicionar a waiting_modules
    #     imprimir "[BLOQUEADO] nome" + motivo (peek na alert_stack)

    # TODO: imprimir resumo — total pousados, em espera, alertas
    pass


# =============================================================================
# [8] EXIBIÇÃO E MENU — Interface com o operador
# =============================================================================

def display_module(module):
    """Exibe os dados de um módulo em formato de linha única formatada."""
    # TODO: imprimir linha formatada com id, name, priority, fuel_level, mass,
    #   cargo_criticality e status
    #   Dica: f"  [ID:{module['id']:02d}] {module['name']:<28s} | ..."
    pass


def display_modules(modules, title):
    """Exibe uma lista de módulos com título e contagem."""
    # TODO: imprimir título com contagem
    # TODO: se vazia, imprimir "(vazia)"
    # TODO: senão, percorrer e chamar display_module() para cada um
    pass


def display_alerts():
    """Exibe a pilha de alertas do topo para a base (sem remover)."""
    # TODO: imprimir título com contagem de alertas
    # TODO: se vazia, imprimir "(nenhum alerta registrado)"
    # TODO: senão, percorrer de trás para frente (topo → base)
    #   e imprimir module_name, reason, timestamp de cada alerta
    pass


def menu_sort():
    """Submenu de ordenação da fila de pouso."""
    print()
    print("--- Ordenar Fila de Pouso ---")
    print("  1. Por prioridade (Bubble Sort)")
    print("  2. Por combustível (Selection Sort)")
    print("  0. Voltar")
    choice = input("Opção: ").strip()

    # TODO: se choice == "1", chamar sort_by_priority e exibir fila
    # TODO: se choice == "2", chamar sort_by_fuel e exibir fila
    pass


def menu_search():
    """Submenu de busca de módulos na fila ou nos dados originais."""
    # Se a fila estiver vazia (pós-simulação), buscar nos dados originais
    source = landing_queue if not is_empty(landing_queue) else MODULES_DATA

    print()
    print("--- Buscar Módulo ---")
    print("  1. Por tipo")
    print("  2. Menor combustível")
    print("  3. Maior prioridade")
    print("  0. Voltar")
    choice = input("Opção: ").strip()

    # TODO: se choice == "1":
    #   pedir tipo via input(), chamar search_by_type(), exibir resultados
    # TODO: se choice == "2":
    #   chamar search_min_fuel(), exibir resultado
    # TODO: se choice == "3":
    #   chamar search_highest_priority(), exibir resultado
    pass


def menu_math():
    """Submenu de funções matemáticas com visualização em texto."""
    print()
    print("--- Funções Matemáticas ---")
    print("  1. Altitude de descida       h(t) — quadrática")
    print("  2. Consumo de combustível    C(v) — exponencial")
    print("  3. Energia solar             E(t) — parábola invertida")
    print("  4. Temperatura superficial   T(t) — senoidal")
    print("  0. Voltar")
    choice = input("Opção: ").strip()

    # TODO: para cada opção, imprimir a fórmula e parâmetros, depois
    #   usar um loop for/range para calcular e imprimir valores tabelados.
    #   Exemplo para altitude:
    #     for t in range(0, 20):
    #         h = descent_altitude(t)
    #         if h < 0:
    #             print("IMPACTO"); break
    #         print(f"  t={t}s | h={h:.1f}m")
    pass


def menu_conditions():
    """Submenu para configurar condições de pouso (alternar True/False)."""
    global landing_conditions

    while True:
        print()
        print("--- Configurar Condições de Pouso ---")
        atm = "SIM" if landing_conditions["atmosphere_ok"] else "NÃO"
        zone = "SIM" if landing_conditions["landing_zone_free"] else "NÃO"
        sens = "SIM" if landing_conditions["sensors_ok"] else "NÃO"
        print(f"  1. Atmosfera OK:        {atm}")
        print(f"  2. Zona de pouso livre: {zone}")
        print(f"  3. Sensores OK:         {sens}")
        print("  0. Voltar")
        choice = input("Alternar condição (0 para voltar): ").strip()

        # TODO: se choice == "1", inverter landing_conditions["atmosphere_ok"]
        # TODO: se choice == "2", inverter landing_conditions["landing_zone_free"]
        # TODO: se choice == "3", inverter landing_conditions["sensors_ok"]
        # TODO: se choice == "0", break
        if choice == "0":
            break


def main():
    """
    Loop principal do MGPEB.
    Apresenta menu interativo e despacha para as funções correspondentes.
    """
    # Carregar módulos na fila ao iniciar o sistema
    load_modules()

    print()
    print("=" * 60)
    print("     MGPEB — Gerenciamento de Pouso e Estabilização")
    print("     Missão Aurora Siger — Colônia em Marte")
    print("=" * 60)

    while True:
        print()
        print("-" * 45)
        print("  1. Ver fila de pouso")
        print("  2. Ordenar fila de pouso")
        print("  3. Buscar módulo")
        print("  4. Executar simulação de pouso")
        print("  5. Ver pilha de alertas")
        print("  6. Funções matemáticas")
        print("  7. Configurar condições de pouso")
        print("  0. Sair")
        print("-" * 45)
        choice = input("Opção: ").strip()

        # TODO: conectar cada opção à função correspondente
        #   "1" → display_modules(landing_queue, "Fila de Pouso")
        #          + exibir landed_modules e waiting_modules se não vazias
        #   "2" → menu_sort() (verificar se fila não está vazia antes)
        #   "3" → menu_search()
        #   "4" → run_landing_simulation()
        #   "5" → display_alerts()
        #   "6" → menu_math()
        #   "7" → menu_conditions()
        #   "0" → imprimir despedida e break

        if choice == "0":
            print()
            print("  Encerrando MGPEB. Missão Aurora Siger — fim da sessão.")
            print()
            break
        else:
            print("  Opção ainda não implementada.")


# =============================================================================
# Ponto de entrada
# =============================================================================

if __name__ == "__main__":
    main()
