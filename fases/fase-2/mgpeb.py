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
import random


# =============================================================================
# [1] DADOS — Constantes, classe Module e dados da colônia
# =============================================================================

# Faixa de combustível sorteada por módulo (%).
# Limite inferior 15 permite gerar ocasionalmente módulos bloqueados
# pelo limiar de 20% definido em check_landing_authorization.
FUEL_RANGE_MIN = 15.0
FUEL_RANGE_MAX = 95.0

# Probabilidade de cada módulo ter seus sensores de bordo íntegros.
SENSORS_OK_PROBABILITY = 0.95

# Distância orbital de aproximação (km) e velocidade de aproximação (km/h).
# Combinados determinam o ETA: eta_horas = ceil(distance / speed),
# arredondado para horas cheias para que empates ativem o desempate
# multi-critério (priority, fuel_level) na ordenacao da fila de pouso.
DISTANCE_RANGE_MIN = 200.0
DISTANCE_RANGE_MAX = 800.0
SPEED_RANGE_MIN = 100.0
SPEED_RANGE_MAX = 400.0
MISSION_START_HOUR = 6.0   # 06:00 — hora de início da janela de pouso


class Module:
    """
    Representa um módulo da colônia Aurora Siger a ser pousado em Marte.

    Encapsula todos os atributos operacionais do módulo e o comportamento
    de randomização de cenário, que varia a cada execução da missão.

    O ETA é derivado de ceil(distance / speed), não armazenado diretamente:
    usar .eta (int horas) ou .eta_str (HH:00) para exibição e ordenação.
    O arredondamento para horas cheias é deliberado — produz empates que
    ativam os critérios secundários da ordenação multi-critério.
    """

    def __init__(self, id, name, type, priority, fuel_level, mass,
                 cargo_criticality, distance, speed,
                 sensors_ok=True, status="queued"):
        self.id = id
        self.name = name
        self.type = type
        self.priority = priority
        self.fuel_level = fuel_level
        self.mass = mass
        self.cargo_criticality = cargo_criticality
        self.distance = distance     # km — distância orbital de aproximação
        self.speed = speed           # km/h — velocidade de aproximação
        self.sensors_ok = sensors_ok
        self.status = status

    @property
    def eta(self):
        """ETA em horas inteiras a partir do início da missão.

        Arredondado para o próximo inteiro com math.ceil para discretizar
        a fila em horas cheias — empates resultantes são desempatados pelos
        critérios secundários (priority, fuel_level) em sort_multi.
        """
        return math.ceil(self.distance / self.speed)

    @property
    def eta_str(self):
        """ETA formatado como HH:MM, offset de MISSION_START_HOUR."""
        total = MISSION_START_HOUR + self.eta
        h = int(total)
        m = int(round((total - h) * 60))
        if m == 60:
            h += 1
            m = 0
        return f"{h:02d}:{m:02d}"

    def randomize(self):
        """
        Sorteia fuel_level, sensors_ok, distance e speed para simular
        variações operacionais de cada módulo a cada execução da missão.
        """
        self.fuel_level = round(random.uniform(FUEL_RANGE_MIN, FUEL_RANGE_MAX), 1)
        self.sensors_ok = random.random() < SENSORS_OK_PROBABILITY
        self.distance = round(random.uniform(DISTANCE_RANGE_MIN, DISTANCE_RANGE_MAX), 1)
        self.speed = round(random.uniform(SPEED_RANGE_MIN, SPEED_RANGE_MAX), 1)

    def copy(self):
        """Retorna uma cópia independente deste módulo."""
        return Module(
            id=self.id,
            name=self.name,
            type=self.type,
            priority=self.priority,
            fuel_level=self.fuel_level,
            mass=self.mass,
            cargo_criticality=self.cargo_criticality,
            distance=self.distance,
            speed=self.speed,
            sensors_ok=self.sensors_ok,
            status=self.status,
        )

    def __repr__(self):
        return f"Module({self.id}, {self.name!r}, eta={self.eta_str})"


# Os 12 módulos da colônia Aurora Siger.
# distance, speed, fuel_level e sensors_ok são sobrescritos por
# randomize_scenario() a cada execução — os valores abaixo são defaults iniciais
# que aproximam as ETAs originais da missão (offset de 06:00).
MODULES_DATA = [
    Module(id=1,  name="Comando e Controle",        type="command",      priority=1,  fuel_level=85.0, mass=12000.0, cargo_criticality=5, distance=200.0, speed=400.0),
    Module(id=2,  name="Suporte de Vida (ECLSS)",   type="life_support", priority=2,  fuel_level=78.0, mass=15000.0, cargo_criticality=5, distance=300.0, speed=400.0),
    Module(id=3,  name="Habitação",                 type="habitat",      priority=3,  fuel_level=72.0, mass=18000.0, cargo_criticality=4, distance=500.0, speed=400.0),
    Module(id=4,  name="Energia Solar",             type="solar",        priority=4,  fuel_level=65.0, mass=8000.0,  cargo_criticality=5, distance=350.0, speed=200.0),
    Module(id=5,  name="Energia Nuclear",           type="nuclear",      priority=5,  fuel_level=58.0, mass=22000.0, cargo_criticality=5, distance=500.0, speed=200.0),
    Module(id=6,  name="Comunicações",              type="comms",        priority=6,  fuel_level=55.0, mass=6000.0,  cargo_criticality=4, distance=400.0, speed=400.0),
    Module(id=7,  name="Suporte Médico",            type="medical",      priority=7,  fuel_level=70.0, mass=10000.0, cargo_criticality=4, distance=400.0, speed=200.0),
    Module(id=8,  name="Produção de Alimentos",     type="food",         priority=8,  fuel_level=60.0, mass=14000.0, cargo_criticality=3, distance=650.0, speed=200.0),
    Module(id=9,  name="Logística e Armazenamento", type="logistics",    priority=9,  fuel_level=45.0, mass=25000.0, cargo_criticality=3, distance=750.0, speed=200.0),
    Module(id=10, name="ISRU (Recursos Locais)",    type="isru",         priority=10, fuel_level=42.0, mass=20000.0, cargo_criticality=2, distance=550.0, speed=100.0),
    Module(id=11, name="Oficina e Manutenção",      type="workshop",     priority=11, fuel_level=50.0, mass=16000.0, cargo_criticality=2, distance=500.0, speed=100.0),
    Module(id=12, name="Laboratório Científico",    type="lab",          priority=12, fuel_level=82.0, mass=12000.0, cargo_criticality=2, distance=400.0, speed=100.0),
]

# Condições de pouso ambientais (configuráveis pelo operador via menu).
# sensors_ok é por módulo — ver Module.sensors_ok.
landing_conditions = {
    "atmosphere_ok": True,          # Condições atmosféricas favoráveis
    "landing_zone_free": True,      # Zona de pouso disponível
}

# Probabilidades de cada condição ambiental estar OK no início da missão.
# Valores inspirados em realismo de missão espacial:
#   - Zona de pouso costuma estar livre com bom planejamento orbital (90%)
#   - Atmosfera marciana é o fator mais volátil — tempestades de poeira (70%)
CONDITION_PROBABILITIES = {
    "atmosphere_ok": 0.70,
    "landing_zone_free": 0.90,
}

# Estruturas lineares globais — instanciadas por load_modules()
landing_queue = None    # Queue (FIFO) — módulos aguardando autorização de pouso
landed_modules = None   # Vector — módulos já pousados com sucesso
waiting_modules = None  # Vector — módulos com pouso adiado
alert_stack = None      # Stack (LIFO) — registros de alertas de bloqueio


def randomize_scenario():
    """
    Sorteia um novo cenário de pouso: chama Module.randomize() em cada módulo
    (fuel_level, sensors_ok, distance, speed) e alterna as flags de landing_conditions.

    Deve ser chamada uma vez no início de main(), antes de load_modules(),
    para que cada execução do simulador apresente condições diferentes.

    Efeitos colaterais:
        - Modifica MODULES_DATA in-place via Module.randomize()
          (propagado para landing_queue via load_modules)
        - Modifica landing_conditions in-place
    """
    for module in MODULES_DATA:
        module.randomize()

    for condition in landing_conditions:
        landing_conditions[condition] = random.random() < CONDITION_PROBABILITIES[condition]

    print()
    print("  >> CENÁRIO ALEATÓRIO GERADO <<")
    atm = "OK" if landing_conditions["atmosphere_ok"] else "DESFAVORÁVEL"
    zone = "LIVRE" if landing_conditions["landing_zone_free"] else "OCUPADA"
    print(f"     Atmosfera={atm} | Zona={zone}")
    print(f"     Combustível, sensores, distância e velocidade: randomizados por módulo")


# =============================================================================
# [2] ESTRUTURAS LINEARES — Classes Vector, Queue e Stack
# =============================================================================

class Vector:
    """
    Lista ordenada com interface de vetor: acesso por índice, iteração,
    inserção e remoção em qualquer posição.

    Também centraliza os algoritmos de busca e ordenação sobre módulos,
    para que Queue e Stack os herdem sem duplicação.
    """

    def __init__(self):
        self._data = []

    # --- Interface de vetor ---

    def append(self, item):
        """Adiciona um item ao final."""
        self._data.append(item)

    def insert(self, index, item):
        """Insere um item em uma posição específica."""
        self._data.insert(index, item)

    def remove_at(self, index):
        """Remove e retorna o item na posição dada. Levanta IndexError se fora do intervalo."""
        if index < 0 or index >= len(self._data):
            raise IndexError("Índice fora do intervalo.")
        return self._data.pop(index)

    def get(self, index):
        """Retorna o item na posição dada sem removê-lo."""
        return self._data[index]

    def size(self):
        """Retorna o número de itens."""
        return len(self._data)

    def is_empty(self):
        """Retorna True se não houver itens."""
        return len(self._data) == 0

    def to_list(self):
        """Retorna uma cópia da lista interna."""
        return list(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"
    
    # --- Busca ---

    def search_by_type(self, module_type):
        """
        Busca linear por tipo: retorna lista com todos os módulos cujo
        atributo 'type' corresponde ao valor buscado.
        Complexidade: O(n).
        """
        results = []
        for item in self._data:
            if item.type == module_type:
                results.append(item)
        return results

    def search_min_fuel(self):
        """
        Busca linear pelo módulo com menor nível de combustível.
        Retorna None se vazio.
        Complexidade: O(n).
        """
        if self.is_empty():
            return None
        minimum = self._data[0]
        for i in range(1, len(self._data)):
            if self._data[i].fuel_level < minimum.fuel_level:
                minimum = self._data[i]
        return minimum

    def search_highest_priority(self):
        """
        Busca linear pelo módulo com maior prioridade (menor valor numérico).
        Retorna None se vazio.
        Complexidade: O(n).
        """
        if self.is_empty():
            return None
        best = self._data[0]
        for i in range(1, len(self._data)):
            if self._data[i].priority < best.priority:
                best = self._data[i]
        return best

    def find_by_id(self, module_id):
        """
        Busca linear pelo módulo com o id fornecido.
        Retorna o módulo encontrado ou None se não existir.
        Complexidade: O(n).
        """
        for item in self._data:
            if item.id == module_id:
                return item
        return None

    # --- Ordenação ---

    def sort_multi(self):
        """
        Bubble Sort multi-critério: ETA → prioridade → combustível.

        Ordem de desempate:
            1. eta (ascendente) — módulo que chega primeiro pousa primeiro
            2. priority (ascendente) — critério de missão como segundo critério
            3. fuel_level (ascendente) — quem está no limite pousa com prioridade

        Complexidade: O(n²) pior caso, O(n) melhor caso.
        """
        n = len(self._data)
        for i in range(n):
            swapped = False
            for j in range(n - i - 1):
                a = self._data[j]
                b = self._data[j + 1]
                if (a.eta, a.priority, a.fuel_level) > (b.eta, b.priority, b.fuel_level):
                    self._data[j], self._data[j + 1] = self._data[j + 1], self._data[j]
                    swapped = True
            if not swapped:
                break

    def sort_by_priority(self):
        """
        Bubble Sort por prioridade (ascendente).
        Ordena self._data in-place.
        Complexidade: O(n²) pior caso, O(n) melhor caso.
        """
        n = len(self._data)
        for i in range(n):
            swapped = False
            for j in range(n - i - 1):
                if self._data[j].priority > self._data[j + 1].priority:
                    self._data[j], self._data[j + 1] = self._data[j + 1], self._data[j]
                    swapped = True
            if not swapped:
                break

    def sort_by_fuel(self):
        """
        Selection Sort por combustível (ascendente).
        Ordena self._data in-place.
        Complexidade: O(n²) em todos os casos.
        """
        n = len(self._data)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if self._data[j].fuel_level < self._data[min_idx].fuel_level:
                    min_idx = j
            if min_idx != i:
                self._data[i], self._data[min_idx] = self._data[min_idx], self._data[i]


class Queue(Vector):
    """
    Fila FIFO construída sobre Vector.

    Restringe acesso ao início (dequeue) e ao fim (enqueue).
    Herda search_by_type, search_min_fuel, search_highest_priority,
    sort_multi, sort_by_priority e sort_by_fuel de Vector.
    """

    def enqueue(self, item):
        """Adiciona um item ao final da fila (operação FIFO)."""
        self.append(item)

    def dequeue(self):
        """
        Remove e retorna o primeiro item da fila (operação FIFO).
        Retorna None se vazia.
        """
        if self.is_empty():
            return None
        return self.remove_at(0)

    def peek(self):
        """Consulta o primeiro item sem removê-lo. Retorna None se vazia."""
        if self.is_empty():
            return None
        return self.get(0)


class Stack(Vector):
    """
    Pilha LIFO construída sobre Vector.

    Restringe acesso ao topo (push/pop).
    Herda search_by_type, search_min_fuel, search_highest_priority,
    sort_multi, sort_by_priority e sort_by_fuel de Vector.
    """

    def push(self, item):
        """Adiciona um item ao topo da pilha (operação LIFO)."""
        self.append(item)

    def pop(self):
        """
        Remove e retorna o item do topo da pilha (operação LIFO).
        Retorna None se vazia.
        """
        if self.is_empty():
            return None
        return self.remove_at(len(self._data) - 1)

    def peek(self):
        """Consulta o topo sem remover. Retorna None se vazia."""
        if self.is_empty():
            return None
        return self.get(-1)


# =============================================================================
# [3] REGRAS LÓGICAS — Autorização de pouso com expressões booleanas
# =============================================================================

def check_landing_authorization(module, conditions):
    """
    Verifica se um módulo está autorizado a pousar com base em regras booleanas.

    Expressão lógica implementada:
        AUTORIZADO = F AND A AND (L OR E) AND S

    Variáveis:
        F = combustível suficiente (module.fuel_level >= 20%)
        A = condições atmosféricas favoráveis
        L = zona de pouso livre
        S = sensores de bordo íntegros (module.sensors_ok)
        E = emergência (module.cargo_criticality == 5) — bypass da zona de pouso

    Quando o pouso é negado, um alerta é empilhado na alert_stack
    contendo o motivo do bloqueio.

    Retorna: True se autorizado, False caso contrário.
    """
    fuel_ok = module.fuel_level >= 20
    atmosphere_ok = conditions["atmosphere_ok"]
    zone_free = conditions["landing_zone_free"]
    sensors_ok = module.sensors_ok
    emergency = module.cargo_criticality == 5

    authorized = fuel_ok and atmosphere_ok and (zone_free or emergency) and sensors_ok

    if not authorized:
        reasons = []
        if not fuel_ok:
            reasons.append(f"Combustível insuficiente ({module.fuel_level:.1f}%)")
        if not atmosphere_ok:
            reasons.append("Condições atmosféricas desfavoráveis")
        if not zone_free and not emergency:
            reasons.append("Zona de pouso ocupada")
        if not sensors_ok:
            reasons.append("Falha nos sensores")

        alert = {
            "module_id": module.id,
            "module_name": module.name,
            "reason": "; ".join(reasons),
            "timestamp": module.eta_str,
        }
        alert_stack.push(alert)

    return authorized


# =============================================================================
# [4] FUNÇÕES MATEMÁTICAS — Modelagem de fenômenos do pouso
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

    Retorna: altitude em metros (mínimo 0)
    """
    return max(0.0, h0 - v0 * t - 0.5 * a * t ** 2)


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
    return c0 * math.exp(k * v)


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
    return max(0.0, (-a_coeff * (t - t_mid) ** 2 + e_max))


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
    return t_avg + amplitude * math.sin(2 * math.pi * t / period - phase)


# =============================================================================
# [5] SIMULAÇÃO — Execução do pouso sequencial
# =============================================================================

def load_modules():
    """
    Instancia as estruturas lineares e carrega os módulos na fila de pouso.
    Reinicia todas as estruturas para uma nova simulação.
    Usa Module.copy() para preservar MODULES_DATA intacto.
    """
    global landing_queue, landed_modules, waiting_modules, alert_stack
    landing_queue = Queue()
    landed_modules = Vector()
    waiting_modules = Vector()
    alert_stack = Stack()

    for module in MODULES_DATA:
        landing_queue.enqueue(module.copy())


def run_landing_simulation():
    """
    Executa a simulação completa de pouso dos módulos da colônia.

    Fluxo:
        1. Recarrega todos os módulos na fila de pouso
        2. Ordena a fila multi-critério: ETA → prioridade → combustível
        3. Processa cada módulo: verifica autorização via regras booleanas
        4. Módulos autorizados vão para landed_modules (Vector)
        5. Módulos bloqueados vão para waiting_modules (Vector) + alerta na Stack
        6. Exibe resumo completo da operação
    """
    # Só recarrega se a fila estiver vazia (simulação anterior já a drenou).
    # Se houver módulos na fila (inclusive editados), usa o estado atual.
    if landing_queue.is_empty():
        load_modules()
        print("  (Fila recarregada a partir dos dados originais)")

    landing_queue.sort_multi()

    print()
    print("=" * 60)
    print("     SIMULAÇÃO DE POUSO — Colônia Aurora Siger")
    print("=" * 60)
    print()
    atm = "OK" if landing_conditions["atmosphere_ok"] else "DESFAVORÁVEL"
    zone = "LIVRE" if landing_conditions["landing_zone_free"] else "OCUPADA"
    print(f"  Condições: Atmosfera={atm} | Zona={zone} | Sensores=por módulo")
    print(f"  Ordem de pouso: ETA → prioridade → combustível")
    print()
    print(f"  Processando fila de pouso ({landing_queue.size()} módulos)...")
    print("-" * 60)

    while not landing_queue.is_empty():
        module = landing_queue.dequeue()
        authorized = check_landing_authorization(module, landing_conditions)

        if authorized:
            module.status = "landed"
            landed_modules.append(module)
            print(f"  [AUTORIZADO] {module.name:<30} ETA {module.eta_str}")
        else:
            module.status = "waiting"
            waiting_modules.append(module)
            last_alert = alert_stack.peek()
            reason = last_alert["reason"] if last_alert else "Desconhecido"
            print(f"  [BLOQUEADO]  {module.name:<30} ETA {module.eta_str}")
            print(f"               Motivo: {reason}")

    print()
    print("-" * 60)
    print("     RESUMO DA SIMULAÇÃO")
    print("-" * 60)
    print(f"  Módulos pousados com sucesso:  {landed_modules.size()}")
    print(f"  Módulos em espera (bloqueados): {waiting_modules.size()}")
    print(f"  Alertas gerados:               {alert_stack.size()}")
    print()


# =============================================================================
# [6] EXIBIÇÃO E MENU — Interface com o operador
# =============================================================================

def display_module(module):
    """Exibe os dados de um módulo em formato de linha única formatada."""
    sens = "OK" if module.sensors_ok else "FALHA"
    print(f"\n[ID:{module.id}] {module.name}"
          f"\n | Prioridade: {module.priority}"
          f"\n | Combustível: {module.fuel_level:.1f}%"
          f"\n | Massa: {module.mass:.0f} kg"
          f"\n | Crítico: {module.cargo_criticality}"
          f"\n | Sensores: {sens}"
          f"\n | Distância: {module.distance:.1f} km  |  Velocidade: {module.speed:.1f} km/h"
          f"\n | ETA: {module.eta_str} ({module.eta}h desde início da missão)")


def display_modules(modules, title):
    """Exibe uma estrutura linear de módulos com título e contagem."""
    print()
    print(f"--- {title} ({len(modules)} módulos) ---")
    if len(modules) == 0:
        print("  (vazia)")
    else:
        for module in modules:
            display_module(module)
    print()


def display_alerts():
    """Exibe a pilha de alertas do topo para a base (sem remover)."""
    print()
    print(f"--- Pilha de Alertas ({alert_stack.size()} alertas) ---")
    if alert_stack.is_empty():
        print("  (nenhum alerta registrado)")
    else:
        for i in range(alert_stack.size() - 1, -1, -1):
            alert = alert_stack[i]
            position = alert_stack.size() - i
            print(f"  [{position}] Módulo: {alert['module_name']} (ID:{alert['module_id']:02d})")
            print(f"      Motivo: {alert['reason']}")
            print(f"      ETA: {alert['timestamp']}")
    print()


def menu_sort():
    """Submenu de ordenação da fila de pouso."""
    print()
    print("--- Ordenar Fila de Pouso ---")
    print("  1. Multi-critério: ETA → prioridade → combustível (Bubble Sort)")
    print("  2. Por combustível (Selection Sort)")
    print("  3. Por prioridade (Bubble Sort)")
    print("  0. Voltar")
    choice = input("Opção: ").strip()

    match choice:
        case "1":
            landing_queue.sort_multi()
            print("\n  Fila ordenada: ETA → prioridade → combustível.")
            display_modules(landing_queue, "Fila de Pouso")
        case "2":
            landing_queue.sort_by_fuel()
            print("\n  Fila ordenada por nível de combustível.")
            display_modules(landing_queue, "Fila de Pouso")
        case "3":
            landing_queue.sort_by_priority()
            print("\n  Fila ordenada por prioridade.")
            display_modules(landing_queue, "Fila de Pouso")


def menu_search():
    """Submenu de busca de módulos na fila ou nos dados originais."""
    if not landing_queue.is_empty():
        source = landing_queue
        source_name = "fila de pouso"
    else:
        source = Vector()
        for m in MODULES_DATA:
            source.append(m)
        source_name = "dados originais"

    print()
    print(f"--- Buscar Módulo (buscando em: {source_name}) ---")
    print("  1. Por tipo")
    print("  2. Menor combustível")
    print("  3. Maior prioridade")
    print("  0. Voltar")
    choice = input("Opção: ").strip()

    match choice:
        case "1":
            print()
            print("  Tipos disponíveis:")
            print("    command, life_support, habitat, solar, nuclear, comms,")
            print("    medical, food, logistics, isru, workshop, lab")
            module_type = input("  Digite o tipo: ").strip().lower()
            results = source.search_by_type(module_type)
            if not results:
                print(f"\n  Nenhum módulo do tipo '{module_type}' encontrado.")
            else:
                display_modules(results, f"Módulos do tipo '{module_type}'")
        case "2":
            result = source.search_min_fuel()
            if result:
                print("\n  Módulo com menor combustível:")
                display_module(result)
                print()
        case "3":
            result = source.search_highest_priority()
            if result:
                print("\n  Módulo com maior prioridade:")
                display_module(result)
                print()


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

    match choice:
        case "1":
            print()
            print("  Altitude de descida: h(t) = h0 - v0*t - 0.5*a*t^2")
            print("  Parâmetros: h0=2000m, v0=80m/s, a=3.7m/s^2")
            print()
            for t in range(0, 20):
                h = descent_altitude(t)
                if h == 0.0 and t > 0:
                    print(f"    t={t:>2d}s  |  IMPACTO (h = 0)")
                    break
                bar = "#" * max(0, int(h / 50))
                print(f"    t={t:>2d}s  |  h={h:>7.1f}m  | {bar}")
            print()
        case "2":
            print()
            print("  Consumo de combustível: C(v) = C0 * e^(k*v)")
            print("  Parâmetros: C0=10.0 kg/s, k=0.02")
            print()
            for v in range(0, 201, 20):
                c = fuel_consumption(v)
                bar = "#" * min(50, int(c / 5))
                print(f"    v={v:>3d} m/s  |  C={c:>8.2f} kg/s  | {bar}")
            print()
        case "3":
            print()
            print("  Energia solar: E(t) = -a*(t - t_mid)^2 + E_max")
            print("  Parâmetros: a=15.0, t_mid=12.3h, E_max=2200W")
            print()
            for t in range(0, 25):
                e = solar_energy(t)
                bar = "#" * int(e / 100)
                print(f"    t={t:>2d}h  |  E={e:>7.1f}W  | {bar}")
            print()
        case "4":
            print()
            print("  Temperatura superficial: T(t) = T_avg + A*sin(2*pi*t/P - phi)")
            print("  Parâmetros: T_avg=-60°C, A=40°C, P=24.62h")
            print()
            for t in range(0, 25):
                temp = surface_temperature(t)
                # Escala visual: mapear -100°C...-20°C para 0...20 caracteres
                bar_len = max(0, int((temp + 100) / 4))
                bar = " " * bar_len + "#"
                print(f"    t={t:>2d}h  |  T={temp:>6.1f}°C  | {bar}")
            print()


def menu_conditions():
    """Submenu para configurar condições de pouso (alternar True/False)."""
    while True:
        print()
        print("--- Configurar Condições de Pouso ---")
        atm = "SIM" if landing_conditions["atmosphere_ok"] else "NÃO"
        zone = "SIM" if landing_conditions["landing_zone_free"] else "NÃO"
        print(f"  1. Atmosfera OK:        {atm}")
        print(f"  2. Zona de pouso livre: {zone}")
        print("  0. Voltar")
        choice = input("Alternar condição (0 para voltar): ").strip()

        match choice:
            case "1":
                landing_conditions["atmosphere_ok"] = not landing_conditions["atmosphere_ok"]
            case "2":
                landing_conditions["landing_zone_free"] = not landing_conditions["landing_zone_free"]
            case "0":
                break


def menu_edit_module():
    """Busca um módulo por ID e permite editar seus campos limitadores."""
    try:
        module_id = int(input("\n  ID do módulo (1-12): ").strip())
    except ValueError:
        print("  ID inválido.")
        return

    # Procura em todas as estruturas ativas
    module = None
    for structure in (landing_queue, waiting_modules, landed_modules):
        module = structure.find_by_id(module_id)
        if module:
            break

    if not module:
        print(f"\n  Módulo ID {module_id} não encontrado nas estruturas ativas.")
        return

    # Referência ao original em MODULES_DATA para persistir edições nos reloads
    source = next((m for m in MODULES_DATA if m.id == module_id), None)

    while True:
        print()
        display_module(module)
        print()
        print("  --- Editar campos ---")
        print(f"  1. Combustível       ({module.fuel_level:.1f}%)")
        print(f"  2. Sensores OK       ({'SIM' if module.sensors_ok else 'NÃO'})")
        print(f"  3. Distância         ({module.distance:.1f} km)")
        print(f"  4. Velocidade        ({module.speed:.1f} km/h)")
        print(f"  5. Prioridade        ({module.priority})")
        print(f"  6. Criticidade carga ({module.cargo_criticality})")
        print("  0. Voltar")
        field_choice = input("  Campo: ").strip()

        match field_choice:
            case "1":
                try:
                    val = float(input(f"  Novo combustível (0–100): ").strip())
                    module.fuel_level = round(max(0.0, min(100.0, val)), 1)
                    if source:
                        source.fuel_level = module.fuel_level
                    print(f"  Combustível atualizado: {module.fuel_level:.1f}%")
                except ValueError:
                    print("  Valor inválido.")
            case "2":
                module.sensors_ok = not module.sensors_ok
                if source:
                    source.sensors_ok = module.sensors_ok
                print(f"  Sensores: {'OK' if module.sensors_ok else 'FALHA'}")
            case "3":
                try:
                    val = float(input(f"  Nova distância (km, > 0): ").strip())
                    if val > 0:
                        module.distance = round(val, 1)
                        if source:
                            source.distance = module.distance
                        print(f"  Distância: {module.distance:.1f} km  →  ETA: {module.eta_str}")
                    else:
                        print("  Distância deve ser maior que zero.")
                except ValueError:
                    print("  Valor inválido.")
            case "4":
                try:
                    val = float(input(f"  Nova velocidade (km/h, > 0): ").strip())
                    if val > 0:
                        module.speed = round(val, 1)
                        if source:
                            source.speed = module.speed
                        print(f"  Velocidade: {module.speed:.1f} km/h  →  ETA: {module.eta_str}")
                    else:
                        print("  Velocidade deve ser maior que zero.")
                except ValueError:
                    print("  Valor inválido.")
            case "5":
                try:
                    val = int(input(f"  Nova prioridade (1–12): ").strip())
                    module.priority = max(1, min(12, val))
                    if source:
                        source.priority = module.priority
                    print(f"  Prioridade: {module.priority}")
                except ValueError:
                    print("  Valor inválido.")
            case "6":
                try:
                    val = int(input(f"  Nova criticidade (1–5): ").strip())
                    module.cargo_criticality = max(1, min(5, val))
                    if source:
                        source.cargo_criticality = module.cargo_criticality
                    print(f"  Criticidade: {module.cargo_criticality}")
                except ValueError:
                    print("  Valor inválido.")
            case "0":
                break
            case _:
                print("  Opção inválida.")


def main():
    """
    Loop principal do MGPEB.
    Apresenta menu interativo e despacha para as funções correspondentes.
    """
    # Randomizar cenário (combustíveis, sensores, distância e velocidade por módulo,
    # mais condições ambientais) antes de carregar a fila.
    randomize_scenario()

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
        print("  8. Editar módulo por ID")
        print("  0. Sair")
        print("-" * 45)
        choice = input("Opção: ").strip()

        match choice:
            case "1":
                display_modules(landing_queue, "Fila de Pouso")
                if not landed_modules.is_empty():
                    display_modules(landed_modules, "Módulos Pousados")
                if not waiting_modules.is_empty():
                    display_modules(waiting_modules, "Módulos em Espera")
            case "2":
                if landing_queue.is_empty():
                    print("\n  Fila vazia. Execute a simulação (opção 4) para recarregar.")
                else:
                    menu_sort()
            case "3":
                menu_search()
            case "4":
                run_landing_simulation()
            case "5":
                display_alerts()
            case "6":
                menu_math()
            case "7":
                menu_conditions()
            case "8":
                menu_edit_module()
            case "0":
                print()
                print("  Encerrando MGPEB. Missão Aurora Siger — fim da sessão.")
                print()
                break
            case _:
                print("  Opção inválida. Tente novamente.")


# =============================================================================
# Ponto de entrada
# =============================================================================

if __name__ == "__main__":
    main()
