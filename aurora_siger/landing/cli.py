"""Interactive command-line interface for the MGPEB prototype.

Drives a single :class:`LandingMission` instance through a menu loop. Each
sub-menu operates on the mission passed as argument — no globals, so a host
notebook can build its own mission and call individual sub-menus instead of
:func:`main` if desired.
"""

from __future__ import annotations

from aurora_siger.landing.mission import LandingMission
from aurora_siger.landing.module import Module
from aurora_siger.landing.physics import (
    descent_altitude,
    fuel_consumption,
    solar_energy,
    surface_temperature,
)
from aurora_siger.landing.structures import Vector


# --- Display helpers ---

def display_module(module: Module) -> None:
    """Print one module as a multi-line block."""
    sens = "OK" if module.sensors_ok else "FALHA"
    print(f"\n[ID:{module.id}] {module.name}"
          f"\n | Prioridade: {module.priority}"
          f"\n | Combustível: {module.fuel_level:.1f}%"
          f"\n | Massa: {module.mass:.0f} kg"
          f"\n | Crítico: {module.cargo_criticality}"
          f"\n | Sensores: {sens}"
          f"\n | Distância: {module.distance:.1f} km  |  Velocidade: {module.speed:.1f} km/h"
          f"\n | ETA: {module.eta_str} ({module.eta}h desde início da missão)")


def display_modules(modules, title: str) -> None:
    """Print every module in an iterable under a heading with a count."""
    n = len(modules) if hasattr(modules, "__len__") else sum(1 for _ in modules)
    print()
    print(f"--- {title} ({n} módulos) ---")
    if n == 0:
        print("  (vazia)")
    else:
        for module in modules:
            display_module(module)
    print()


def display_alerts(mission: LandingMission) -> None:
    """Print the alert stack from top to bottom without consuming it."""
    stack = mission.alert_stack
    print()
    print(f"--- Pilha de Alertas ({stack.size()} alertas) ---")
    if stack.is_empty():
        print("  (nenhum alerta registrado)")
    else:
        for i in range(stack.size() - 1, -1, -1):
            alert = stack[i]
            position = stack.size() - i
            print(f"  [{position}] Módulo: {alert.module_name} (ID:{alert.module_id:02d})")
            print(f"      Motivo: {alert.reason}")
            print(f"      ETA: {alert.timestamp}")
    print()


# --- Sub-menus ---

def menu_sort(mission: LandingMission) -> None:
    """Submenu: sort the landing queue by one of three criteria."""
    print()
    print("--- Ordenar Fila de Pouso ---")
    print("  1. Multi-critério: ETA → prioridade → combustível (Bubble Sort)")
    print("  2. Por combustível (Selection Sort)")
    print("  3. Por prioridade (Bubble Sort)")
    print("  0. Voltar")
    choice = input("Opção: ").strip()

    queue = mission.landing_queue
    match choice:
        case "1":
            queue.sort_multi()
            print("\n  Fila ordenada: ETA → prioridade → combustível.")
            display_modules(queue, "Fila de Pouso")
        case "2":
            queue.sort_by_fuel()
            print("\n  Fila ordenada por nível de combustível.")
            display_modules(queue, "Fila de Pouso")
        case "3":
            queue.sort_by_priority()
            print("\n  Fila ordenada por prioridade.")
            display_modules(queue, "Fila de Pouso")


def _searchable_view(mission: LandingMission) -> tuple[Vector, str]:
    """Return a Vector view to search across, plus a label for the user.

    Searches the queue when modules are still pending; otherwise spans the
    landed and waiting vectors so post-simulation searches still work.
    """
    if not mission.landing_queue.is_empty():
        return mission.landing_queue, "fila de pouso"
    combined = Vector()
    for module in mission.landed_modules:
        combined.append(module)
    for module in mission.waiting_modules:
        combined.append(module)
    return combined, "módulos já processados (pousados + em espera)"


def menu_search(mission: LandingMission) -> None:
    """Submenu: search modules by type, lowest fuel or highest priority."""
    source, source_name = _searchable_view(mission)

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


def menu_math() -> None:
    """Submenu: tabulate one of the four physics functions in ASCII."""
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
                bar_len = max(0, int((temp + 100) / 4))
                bar = " " * bar_len + "#"
                print(f"    t={t:>2d}h  |  T={temp:>6.1f}°C  | {bar}")
            print()


def menu_conditions(mission: LandingMission) -> None:
    """Submenu: toggle environmental flags."""
    while True:
        print()
        print("--- Configurar Condições de Pouso ---")
        atm = "SIM" if mission.conditions["atmosphere_ok"] else "NÃO"
        zone = "SIM" if mission.conditions["landing_zone_free"] else "NÃO"
        print(f"  1. Atmosfera OK:        {atm}")
        print(f"  2. Zona de pouso livre: {zone}")
        print("  0. Voltar")
        choice = input("Alternar condição (0 para voltar): ").strip()

        match choice:
            case "1":
                mission.conditions["atmosphere_ok"] = not mission.conditions["atmosphere_ok"]
            case "2":
                mission.conditions["landing_zone_free"] = not mission.conditions["landing_zone_free"]
            case "0":
                break


def menu_edit_module(mission: LandingMission) -> None:
    """Submenu: locate a module by id and edit a few fields."""
    try:
        module_id = int(input("\n  ID do módulo (1-12): ").strip())
    except ValueError:
        print("  ID inválido.")
        return

    module: Module | None = None
    for structure in (mission.landing_queue, mission.waiting_modules, mission.landed_modules):
        module = structure.find_by_id(module_id)
        if module:
            break

    if not module:
        print(f"\n  Módulo ID {module_id} não encontrado nas estruturas ativas.")
        return

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
                    val = float(input("  Novo combustível (0–100): ").strip())
                    module.fuel_level = round(max(0.0, min(100.0, val)), 1)
                    print(f"  Combustível atualizado: {module.fuel_level:.1f}%")
                except ValueError:
                    print("  Valor inválido.")
            case "2":
                module.sensors_ok = not module.sensors_ok
                print(f"  Sensores: {'OK' if module.sensors_ok else 'FALHA'}")
            case "3":
                try:
                    val = float(input("  Nova distância (km, > 0): ").strip())
                    if val > 0:
                        module.distance = round(val, 1)
                        print(f"  Distância: {module.distance:.1f} km  →  ETA: {module.eta_str}")
                    else:
                        print("  Distância deve ser maior que zero.")
                except ValueError:
                    print("  Valor inválido.")
            case "4":
                try:
                    val = float(input("  Nova velocidade (km/h, > 0): ").strip())
                    if val > 0:
                        module.speed = round(val, 1)
                        print(f"  Velocidade: {module.speed:.1f} km/h  →  ETA: {module.eta_str}")
                    else:
                        print("  Velocidade deve ser maior que zero.")
                except ValueError:
                    print("  Valor inválido.")
            case "5":
                try:
                    val = int(input("  Nova prioridade (1–12): ").strip())
                    module.priority = max(1, min(12, val))
                    print(f"  Prioridade: {module.priority}")
                except ValueError:
                    print("  Valor inválido.")
            case "6":
                try:
                    val = int(input("  Nova criticidade (1–5): ").strip())
                    module.cargo_criticality = max(1, min(5, val))
                    print(f"  Criticidade: {module.cargo_criticality}")
                except ValueError:
                    print("  Valor inválido.")
            case "0":
                break
            case _:
                print("  Opção inválida.")


# --- Top-level ---

def announce_scenario(mission: LandingMission) -> None:
    """Print a brief banner describing the current environmental flags."""
    print()
    print("  >> CENÁRIO ALEATÓRIO GERADO <<")
    atm = "OK" if mission.conditions["atmosphere_ok"] else "DESFAVORÁVEL"
    zone = "LIVRE" if mission.conditions["landing_zone_free"] else "OCUPADA"
    print(f"     Atmosfera={atm} | Zona={zone}")
    print("     Combustível, sensores, distância e velocidade: randomizados por módulo")


def run_landing_simulation(mission: LandingMission) -> None:
    """Wrapper around :meth:`LandingMission.simulate` that re-fills the queue
    when it is empty, matching the original CLI behaviour."""
    if mission.landing_queue.is_empty():
        mission.reload()
        print("  (Fila recarregada a partir dos dados originais)")
    report = mission.simulate()
    mission.print_report(report)


def main() -> None:
    """Entry point for the MGPEB CLI prototype."""
    mission = LandingMission.from_defaults()
    mission.randomize_scenario()
    announce_scenario(mission)

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
                display_modules(mission.landing_queue, "Fila de Pouso")
                if not mission.landed_modules.is_empty():
                    display_modules(mission.landed_modules, "Módulos Pousados")
                if not mission.waiting_modules.is_empty():
                    display_modules(mission.waiting_modules, "Módulos em Espera")
            case "2":
                if mission.landing_queue.is_empty():
                    print("\n  Fila vazia. Execute a simulação (opção 4) para recarregar.")
                else:
                    menu_sort(mission)
            case "3":
                menu_search(mission)
            case "4":
                run_landing_simulation(mission)
            case "5":
                display_alerts(mission)
            case "6":
                menu_math()
            case "7":
                menu_conditions(mission)
            case "8":
                menu_edit_module(mission)
            case "0":
                print()
                print("  Encerrando MGPEB. Missão Aurora Siger — fim da sessão.")
                print()
                break
            case _:
                print("  Opção inválida. Tente novamente.")
