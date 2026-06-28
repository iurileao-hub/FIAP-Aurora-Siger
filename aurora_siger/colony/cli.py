# aurora_siger/colony/cli.py
"""SIGIC terminal UI — the only I/O layer of the colony domain.

Module names are English in the domain; this layer renders Portuguese labels via
PT_LABELS. Every screen consumes the pure results from colony.{search,paths,
analysis,modeling,topology} and prints them.
"""

import os
import subprocess

from aurora_siger.colony import analysis, paths, search, topology
from aurora_siger.colony.graph import Module, InfrastructureGraph
from aurora_siger.colony.modeling import MathematicalModeling

PT_LABELS: dict[int, str] = {
    1: "Centro de Controle",
    2: "Suporte de Vida (ECLSS)",
    3: "Habitacao",
    4: "Energia Solar",
    5: "Energia Nuclear",
    6: "Comunicacoes",
    7: "Suporte Medico",
    8: "Producao de Alimentos",
    9: "Logistica e Armazenamento",
    10: "ISRU (Recursos Locais)",
    11: "Oficina e Manutencao",
    12: "Laboratorio Cientifico",
    13: "Energia Eolica",
}

TYPE_LABELS_PT = {"energy": "energia", "data": "dados", "life": "suporte a vida"}


def label(module: Module) -> str:
    """Portuguese display name for a module (falls back to its EN name)."""
    return PT_LABELS.get(module.id, module.name)


def _select_module(graph: InfrastructureGraph, prompt: str) -> int | None:
    print("\nModulos disponiveis:")
    for i, module in enumerate(graph.module_list, 1):
        print(f"  {i:2d}. {label(module)}")
    try:
        choice = int(input(f"\n{prompt} (numero): ")) - 1
    except ValueError:
        print("\n[ERRO] Entrada invalida!")
        return None
    if 0 <= choice < len(graph.module_list):
        return graph.module_list[choice].id
    print("\n[ERRO] Opcao invalida!")
    return None


# ==================== STATUS / TYPE HELPERS ====================

def _status_icon(status: str) -> str:
    return {"active": "[A]", "maintenance": "[M]", "alert": "[!]", "inactive": "[X]"}.get(status, "[?]")


def _type_icon(conn_type: str) -> str:
    return {
        "energy": "[E]", "data": "[D]", "communication": "[C]",
        "life": "[L]", "water": "[W]", "air": "[A]",
    }.get(conn_type, "[-]")


# ==================== SCREEN 1: VIEW NETWORK ====================

def _screen_view_network(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("VISUALIZACAO DA REDE")
    print("=" * 70)

    print("\nESTRUTURA DA REDE:")
    print("-" * 70)

    print("\nMODULOS:")
    for module in graph.module_list:
        icon = _status_icon(module.status)
        priority_bar = "█" * (module.priority // 2) + "░" * (5 - module.priority // 2)
        print(f"  {icon} {label(module)} (ID: {module.id})")
        print(f"     Consumo: {module.consumption} kWh  |  Prioridade: [{priority_bar}] {module.priority}/10")
        print(f"     Capacidade: {module.capacity} kWh  |  Comunicacao: {module.communication_need}/10")

    print("\nCONEXOES:")
    seen: set[tuple[int, int]] = set()
    for id1, neighbors in graph.adjacency_list.items():
        for id2 in neighbors:
            key = (min(id1, id2), max(id1, id2))
            if key not in seen:
                seen.add(key)
                weight = graph.get_weight(id1, id2)
                conn_type = graph.connection_types.get(graph._get_edge_key(id1, id2), "energy")
                icon = _type_icon(conn_type)
                print(f"  {icon} {label(graph.modules[id1])} <-> {label(graph.modules[id2])}")
                print(f"     Distancia: {weight:.1f} unidades  |  Tipo: {TYPE_LABELS_PT.get(conn_type, conn_type)}")

    n = graph.get_module_count()
    edges = graph.get_connection_count()
    avg_deg = (2 * edges) / n if n else 0.0
    print("\n" + "-" * 70)
    print(f"Estatisticas: {n} modulos | {edges} conexoes | Grau medio: {avg_deg:.2f}")
    print("\n" + "=" * 70)
    input("\nPressione ENTER para voltar ao menu...")


# ==================== SCREEN 2: QUERY MODULE ====================

def _display_module_details(graph: InfrastructureGraph, module_id: int) -> None:
    module = graph.get_module(module_id)
    if not module:
        print("\n[ERRO] Modulo nao encontrado!")
        return

    modeling = MathematicalModeling(graph)

    print("\n" + "=" * 70)
    print(f"DETALHES DO MODULO: {label(module)}")
    print("=" * 70)

    print("\nINFORMACOES GERAIS:")
    print("-" * 40)
    print(f"  ID: {module.id}")
    print(f"  Status: {module.status.upper()} {_status_icon(module.status)}")

    print("\nINDICADORES OPERACIONAIS:")
    print("-" * 40)
    print(f"  Consumo energetico: {module.consumption} kWh")
    print(f"  Capacidade: {module.capacity} kWh")
    print(f"  Comunicacao: {module.communication_need}/10")
    print(f"  Prioridade: {module.priority}/10")
    priority_bar = "█" * module.priority + "░" * (10 - module.priority)
    print(f"     [{priority_bar}]")

    print("\nCONEXOES:")
    print("-" * 40)
    neighbors = graph.get_neighbors(module_id)
    if neighbors:
        for neighbor_id in neighbors:
            neighbor = graph.get_module(neighbor_id)
            if neighbor:
                weight = graph.get_weight(module_id, neighbor_id)
                edge_key = graph._get_edge_key(module_id, neighbor_id)
                conn_type = graph.connection_types.get(edge_key, "energy")
                icon = _type_icon(conn_type)
                print(f"  {icon} {label(neighbor)} (Distancia: {weight:.1f}, Tipo: {TYPE_LABELS_PT.get(conn_type, conn_type)})")
    else:
        print("  Nenhuma conexao encontrada.")

    print("\nANALISE DE EFICIENCIA:")
    print("-" * 40)
    eff = modeling.distribution_efficiency(module_id)
    print(f"  Eficiencia de distribuicao: {eff['efficiency']*100:.1f}%")
    print(f"  Capacidade total disponivel: {eff['total_capacity']:.2f} kWh")
    print(f"  Distancia media: {eff['average_distance']:.2f}")
    print(f"  Status: {eff['status'].upper()}")

    print("\nRECOMENDACOES:")
    print("-" * 40)
    if eff["efficiency"] < 0.6:
        print("  Eficiencia baixa. Considere:")
        print("     * Aumentar a capacidade de armazenamento")
        print("     * Otimizar rotas de distribuicao")
        print("     * Verificar conexoes criticas")
    elif eff["efficiency"] < 0.8:
        print("  Eficiencia media. Sugestoes:")
        print("     * Monitorar consumo regularmente")
        print("     * Planejar expansao gradual")
    else:
        print("  Modulo operando com alta eficiencia!")
        print("     * Manter praticas atuais")
        print("     * Servir como referencia para outros modulos")

    print("\n" + "=" * 70)


def _screen_query_module(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("CONSULTA DE MODULO")
    print("=" * 70)

    print("\nModulos disponiveis:")
    print("-" * 40)
    for i, module in enumerate(graph.module_list, 1):
        icon = _status_icon(module.status)
        print(f"  {i:2d}. {icon} {label(module)} (Prioridade: {module.priority})")

    print("\n" + "-" * 40)
    option = input("Selecione o numero do modulo (0 para voltar): ").strip()
    if option == "0":
        return

    try:
        idx = int(option) - 1
        if 0 <= idx < len(graph.module_list):
            module = graph.module_list[idx]
            _display_module_details(graph, module.id)
        else:
            print("\n[ERRO] Opcao invalida!")
    except ValueError:
        print("\n[ERRO] Entrada invalida! Digite um numero.")

    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: BFS ====================

def _screen_bfs(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("BFS - BUSCA EM LARGURA")
    print("=" * 70)

    start = _select_module(graph, "Modulo de inicio")
    if start is None:
        return

    search_answer = input("\nBuscar um alvo especifico? (s/n): ").strip().lower()
    target = None
    if search_answer == "s":
        target = _select_module(graph, "Modulo alvo")

    result = search.bfs(graph, start, target)

    print(f"\nOrigem: {label(graph.modules[start])} (nivel 0)")
    print("\nPercurso por nivel:")
    for lvl_nodes in result.order_by_level:
        level = result.levels[lvl_nodes[0]]
        names = ", ".join(label(graph.modules[n]) for n in lvl_nodes)
        print(f"  Nivel {level}: {names}")

    if target is not None:
        if result.target_found_at is not None:
            print(f"\nAlvo encontrado no nivel {result.target_found_at}!")
            path = result.paths.get(target, [])
            if path:
                print(f"Caminho: {' -> '.join(label(graph.modules[n]) for n in path)}")
        else:
            print("\nAlvo nao encontrado.")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: DFS ====================

def _screen_dfs(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("DFS - BUSCA EM PROFUNDIDADE")
    print("=" * 70)

    start = _select_module(graph, "Modulo de inicio")
    if start is None:
        return

    search_answer = input("\nBuscar um alvo especifico? (s/n): ").strip().lower()
    target = None
    if search_answer == "s":
        target = _select_module(graph, "Modulo alvo")

    result = search.dfs(graph, start, target)

    print("\nOrdem de visita:")
    print(f"   {' -> '.join(label(graph.modules[n]) for n in result.order)}")

    if target is not None:
        if result.path:
            print("\nCaminho encontrado:")
            print(f"   {' -> '.join(label(graph.modules[n]) for n in result.path)}")
        else:
            print("\nNenhum caminho encontrado.")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: DIJKSTRA ====================

def _screen_dijkstra(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("DIJKSTRA - CAMINHO MINIMO")
    print("=" * 70)

    origin = _select_module(graph, "Modulo de origem")
    if origin is None:
        return

    destination = _select_module(graph, "Modulo de destino")
    if destination is None:
        return

    result = paths.shortest_path(graph, origin, destination)

    if result.steps:
        print("\nTrace passo a passo:")
        for node_id, dist in result.steps:
            print(f"  * {label(graph.modules[node_id])} (distancia: {dist:.2f})")

    if result.path:
        print("\nRota mais eficiente:")
        print(f"   {' -> '.join(label(graph.modules[n]) for n in result.path)}")
        print(f"   Distancia total: {result.distance:.2f}")
    else:
        print("\nNao foi possivel encontrar um caminho.")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: DIJKSTRA WITH CONSTRAINTS ====================

def _screen_dijkstra_constraints(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("DIJKSTRA - CAMINHO COM RESTRICOES")
    print("=" * 70)

    origin = _select_module(graph, "Modulo de origem")
    if origin is None:
        return

    destination = _select_module(graph, "Modulo de destino")
    if destination is None:
        return

    try:
        min_priority = int(input("\nPrioridade minima requerida (0-10): "))
        if min_priority < 0 or min_priority > 10:
            print("\n[ERRO] Prioridade deve estar entre 0 e 10!")
            return

        result = paths.shortest_path_with_priority(graph, origin, destination, min_priority)

        if result.skipped:
            print(f"\nModulos ignorados (prioridade < {min_priority}):")
            for nid in result.skipped:
                m = graph.get_module(nid)
                if m:
                    print(f"  * {label(m)}")

        if result.path:
            print("\nRota encontrada com restricoes:")
            print(f"   {' -> '.join(label(graph.modules[n]) for n in result.path)}")
            print(f"   Distancia total: {result.distance:.2f}")
        else:
            print("\nNao foi possivel encontrar um caminho com as restricoes.")

    except ValueError:
        print("\n[ERRO] Entrada invalida!")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: DIJKSTRA ALL PATHS ====================

def _screen_dijkstra_all(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("DIJKSTRA - CAMINHOS MINIMOS PARA TODOS OS DESTINOS")
    print("=" * 70)

    origin = _select_module(graph, "Modulo de origem")
    if origin is None:
        return

    results = paths.all_shortest_paths(graph, origin)

    print(f"\nOrigem: {label(graph.modules[origin])}")
    print("-" * 70)

    if not results:
        print("\nNenhum destino alcancavel a partir deste modulo.")
    else:
        ordered = sorted(results.items(), key=lambda item: item[1].distance)
        print(f"\n{'Destino':30} | {'Dist.':>5} | Rota")
        print("-" * 70)
        for dest_id, res in ordered:
            route = " -> ".join(label(graph.modules[n]) for n in res.path)
            print(f"{label(graph.modules[dest_id]):30} | {res.distance:5.1f} | {route}")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: EFFICIENCY ====================

def _screen_efficiency(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("ANALISE DE EFICIENCIA OPERACIONAL")
    print("=" * 70)

    eff = analysis.analyze_efficiency(graph)

    print("\nMETRICAS GERAIS:")
    print("-" * 40)
    print(f"  Total de modulos: {eff['total_modules']}")
    print(f"  Total de conexoes: {eff['total_connections']}")
    print(f"  Grau medio: {eff['average_degree']:.2f}")
    print(f"  Coeficiente de cluster: {eff['clustering_coefficient']:.3f}")

    print("\nEFICIENCIA:")
    print("-" * 40)
    print(f"  Comunicacao: {eff['communication_efficiency']*100:.1f}%")
    print(f"  Energetica: {eff['energy_efficiency']*100:.1f}%")
    print(f"  Status geral: {eff['overall_status'].upper()}")

    print("\nPESOS DAS ARESTAS:")
    print("-" * 40)
    print(f"  Media: {eff['avg_edge_weight']:.2f}")
    print(f"  Maximo: {eff['max_edge_weight']}")
    print(f"  Minimo: {eff['min_edge_weight']}")

    name_to_module = {m.name: m for m in graph.module_list}

    if eff["critical_modules"]:
        print("\nMODULOS CRITICOS:")
        print("-" * 40)
        for mod_name in eff["critical_modules"]:
            m = name_to_module.get(mod_name)
            print(f"  * {label(m) if m else mod_name}")

    if eff["articulation_points"]:
        print("\nPONTOS DE ARTICULACAO (vertices criticos):")
        print("-" * 40)
        for pt_name in eff["articulation_points"]:
            m = name_to_module.get(pt_name)
            print(f"  * {label(m) if m else pt_name}")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: CRITICAL POINTS ====================

def _build_demo_bridge_graph() -> InfrastructureGraph:
    """Builds a small didactic graph that contains articulation points.

    Two triangles (sectors A and B) joined by a single bridge edge 103-201,
    so 103 and 201 are critical: removing either disconnects the network.
    Adapted from the standalone _build_demo_bridge_graph to the new Module
    dataclass: Module(id:int, name:str, type:str, consumption:float,
    priority:int, capacity:float, communication_need:int, position, status).
    """
    demo = InfrastructureGraph()
    specs = [
        (101, "Setor-A No 1", "data"),
        (102, "Setor-A No 2", "data"),
        (103, "Setor-A No 3 (ponte)", "data"),
        (201, "Setor-B No 1 (ponte)", "data"),
        (202, "Setor-B No 2", "data"),
        (203, "Setor-B No 3", "data"),
    ]
    for mod_id, name, mtype in specs:
        demo.add_module(Module(mod_id, name, mtype, 10.0, 5, 10.0, 5, None, "active"))
    connections = [
        (101, 102), (102, 103), (103, 101),  # triangulo A
        (201, 202), (202, 203), (203, 201),  # triangulo B
        (103, 201),                           # unica ponte
    ]
    for id1, id2 in connections:
        demo.add_connection(id1, id2, 1.0)
    return demo


def _screen_critical_points(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("DETECCAO DE PONTOS CRITICOS")
    print("=" * 70)

    points = analysis.articulation_points(graph)

    if points:
        print(f"\nPontos criticos encontrados ({len(points)}):")
        print("-" * 40)
        for p in points:
            module = graph.get_module(p)
            if module:
                print(f"  * {label(module)} (ID: {p})")
                print(f"    Prioridade: {module.priority}")
                print(f"    Conexoes: {len(graph.get_neighbors(p))}")
                print(f"    Status: {module.status}")
                print()
    else:
        print("\nNenhum ponto critico detectado!")
        print("   A rede esta robusta e interconectada.")

    print("\nIMPLICACOES:")
    print("-" * 40)
    if points:
        print("  A remocao de qualquer um desses modulos pode desconectar a rede.")
        print("  Recomendacoes:")
        print("  * Criar conexoes redundantes para estes pontos")
        print("  * Manter monitoramento constante")
        print("  * Ter planos de contingencia")
    else:
        print("  A rede e resiliente a falhas individuais.")
        print("  Estrutura bem projetada para suportar contingencias.")

    # Didactic demonstration: a small network that DOES have articulation
    # points, so the algorithm shows a positive case even when a real
    # network is robust. Two sectors (triangles) linked by a single bridge.
    print("\n" + "-" * 70)
    print("DEMONSTRACAO DIDATICA - cenario com conexao critica:")
    print("-" * 70)
    print("  Dois setores (triangulos A e B) ligados por uma unica ponte A3-B1.")
    demo_graph = _build_demo_bridge_graph()
    demo_points = analysis.articulation_points(demo_graph)
    if demo_points:
        print(f"\n  Pontos de articulacao detectados ({len(demo_points)}):")
        for p in demo_points:
            module = demo_graph.get_module(p)
            if module:
                print(f"    * {module.name} (ID: {p})")
        print("\n  Remover qualquer um deles desconecta a rede de exemplo,")
        print("  comprovando que o algoritmo identifica conexoes criticas reais.")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: CENTRALITY ====================

def _screen_centrality(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("ANALISE DE CENTRALIDADE")
    print("=" * 70)

    centrality = analysis.analyze_centrality(graph)

    print("\nCENTRALIDADE DOS MODULOS:")
    print("-" * 40)

    sorted_modules = sorted(
        centrality.items(),
        key=lambda x: x[1]["degree"],
        reverse=True,
    )

    for mod_id, data in sorted_modules:
        module = graph.get_module(mod_id)
        pt_name = label(module) if module else data["name"]
        bar = "█" * min(data["degree"], 10) + "░" * (10 - min(data["degree"], 10))
        print(f"  {pt_name:30} | Grau: {data['degree']:2d} {bar}")
        print(f"  {'':30} | Intermediacao: {data['betweenness']:.3f}")
        print(f"  {'':30} | Prioridade: {data['priority']}/10")
        print()

    print("INTERPRETACAO:")
    print("-" * 40)
    print("  * Grau: Numero de conexoes diretas")
    print("  * Intermediacao: Importancia como ponte entre modulos")
    print("  * Modulos com alto grau sao hubs da rede")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SCREEN: CONNECTED COMPONENTS ====================

def _screen_components(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("COMPONENTES CONEXOS")
    print("=" * 70)

    components = search.connected_components(graph)

    print(f"\nTotal de componentes: {len(components)}")
    print("-" * 40)

    for i, component in enumerate(components, 1):
        print(f"\nComponente {i}:")
        for mod_id in component:
            module = graph.get_module(mod_id)
            if module:
                print(f"  * {label(module)}")

    if len(components) > 1:
        print("\nATENCAO:")
        print("  A rede possui mais de um componente conexo.")
        print("  Isso significa que ha modulos isolados.")
        print("  Recomendacao: Criar conexoes adicionais.")
    else:
        print("\nA rede e totalmente conexa.")
        print("  Todos os modulos estao interligados.")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== ALGORITHMS SUBMENU ====================

def _menu_algorithms(graph: InfrastructureGraph) -> None:
    while True:
        print("\n" + "=" * 70)
        print("ALGORITMOS DE REDE")
        print("=" * 70)
        print("\n 1. BFS - Busca em Largura")
        print(" 2. DFS - Busca em Profundidade")
        print(" 3. Dijkstra - Caminho Minimo")
        print(" 4. Dijkstra - Caminho com Restricoes de Prioridade")
        print(" 5. Dijkstra - Caminhos Minimos para Todos os Destinos")
        print(" 6. Analise de Eficiencia da Rede")
        print(" 7. Detectar Pontos Criticos")
        print(" 8. Analise de Centralidade")
        print(" 9. Componentes Conexos")
        print(" 0. Voltar")
        print("=" * 70)

        try:
            option = input("\nEscolha uma opcao: ").strip()
            if option == "0":
                break
            elif option == "1":
                _screen_bfs(graph)
            elif option == "2":
                _screen_dfs(graph)
            elif option == "3":
                _screen_dijkstra(graph)
            elif option == "4":
                _screen_dijkstra_constraints(graph)
            elif option == "5":
                _screen_dijkstra_all(graph)
            elif option == "6":
                _screen_efficiency(graph)
            elif option == "7":
                _screen_critical_points(graph)
            elif option == "8":
                _screen_centrality(graph)
            elif option == "9":
                _screen_components(graph)
            else:
                print("\n[ERRO] Opcao invalida!")
        except ValueError:
            print("\n[ERRO] Entrada invalida!")
        except KeyboardInterrupt:
            break


# ==================== MODELING SCREENS ====================

def _screen_project_consumption(graph: InfrastructureGraph, modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("PROJECAO DE CONSUMO ENERGETICO")
    print("=" * 70)

    try:
        years = int(input("\nNumero de anos para projecao: "))
        if years <= 0:
            print("\n[ERRO] Deve ser um numero positivo!")
            return

        result = modeling.temporal_consumption_analysis(years=years, points=years * 10)
        initial_consumption = sum(module.consumption for module in graph.module_list)

        print(f"\nConsumo inicial: {initial_consumption:.2f} kWh")
        print(f"Projecao para {years} anos:")
        print("-" * 50)
        print("\nAno | Consumo Total | Media por Modulo | Crescimento")
        print("-" * 50)
        for t in range(years):
            if t % 2 == 0 or t == years - 1:
                idx = t * 10
                data = result["data"]
                if idx < len(data["consumption"]):
                    consumption = data["consumption"][idx]
                    avg_consumption = consumption / graph.get_module_count()
                    growth = data["growth_rate"][idx] if idx < len(data["growth_rate"]) else 0
                    print(f"{t:3d}  | {consumption:12.2f} | {avg_consumption:16.2f} | {growth:6.1f}%")

        total_growth = result["total_growth"]
        print(f"\nANALISE:")
        print("-" * 40)
        print(f"  Crescimento total: {total_growth:.1f}%")

        if total_growth > 100:
            print("  Crescimento exponencial - infraestrutura precisa de expansao")
            print("  Recomendacao: Investir em fontes alternativas de energia")
        elif total_growth > 50:
            print("  Crescimento significativo - planejar expansao gradual")
            print("  Recomendacao: Otimizar eficiencia dos modulos existentes")
        else:
            print("  Crescimento controlado - infraestrutura suficiente")
            print("  Recomendacao: Manter praticas atuais e monitorar")

    except ValueError:
        print("\n[ERRO] Entrada invalida!")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


def _screen_energy_loss(graph: InfrastructureGraph, modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("PERDA ENERGETICA POR DISTANCIA")
    print("=" * 70)

    print("\nANALISE DE PERDAS:")
    print("-" * 40)

    distances = set(graph.edge_weights.values())
    print("\nDistancia | Perda | Eficiencia")
    print("-" * 40)
    for d in sorted(distances):
        loss = modeling.energy_loss_by_distance(float(d))
        eff = 1.0 - loss
        bar = "█" * int(eff * 10) + "░" * (10 - int(eff * 10))
        print(f"  {d:5.1f}    | {loss*100:5.1f}%  | {bar} {eff*100:.1f}%")

    print("\nANALISE:")
    print("-" * 40)
    print("  * A perda segue uma curva exponencial")
    print("  * Distancias menores reduzem significativamente as perdas")
    print("  * Conexoes com perda > 30% sao consideradas ineficientes")

    high_loss = [d for d in sorted(distances) if modeling.energy_loss_by_distance(float(d)) > 0.3]
    if high_loss:
        print("\nConexoes com perda > 30%:")
        for d in high_loss:
            print(f"  * Distancia {d:.1f} - Considere otimizar")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


def _screen_predict_growth(modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("PREVISAO DE CRESCIMENTO DA INFRAESTRUTURA")
    print("=" * 70)

    try:
        years = int(input("\nNumero de anos para previsao: "))
        if years <= 0:
            print("\n[ERRO] Deve ser um numero positivo!")
            return

        prediction = modeling.growth_prediction(years)

        print(f"\nPREVISAO PARA {years} ANOS:")
        print("-" * 50)
        print(f"  Modulos atuais: {prediction['current_modules']}")
        print(f"  Ano base: {prediction['current_year']}")
        print(f"  Modulos necessarios em {years} anos: {prediction['modules_needed'][-1]}")
        print(f"  Expansao necessaria: {prediction['expansion_needed']} modulos")

        print("\nProjecao detalhada:")
        print("Ano | Modulos | Consumo Total")
        print("-" * 40)
        for t in range(years):
            if t % 2 == 0 or t == years - 1:
                print(
                    f"{prediction['current_year'] + t:4d} | "
                    f"{prediction['modules_needed'][t]:8d} | "
                    f"{prediction['projected_consumption'][t]:12.2f} kWh"
                )

    except ValueError:
        print("\n[ERRO] Entrada invalida!")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


def _screen_cost_benefit(modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("ANALISE DE CUSTO-BENEFICIO")
    print("=" * 70)

    results = modeling.cost_benefit_analysis()

    print("\nMODULOS ORDENADOS POR EFICIENCIA:")
    print("-" * 40)

    sorted_modules = sorted(
        results.items(),
        key=lambda x: x[1]["priority_per_consumption"],
        reverse=True,
    )

    for mod_id, data in sorted_modules:
        m = modeling.graph.get_module(mod_id)
        pt_name = label(m) if m else data["name"]
        print(f"  {pt_name:30}")
        print(f"    Prioridade/Consumo: {data['priority_per_consumption']:.3f}")
        print(f"    Eficiencia: {data['distribution_efficiency']*100:.1f}%")
        print(f"    Status: {data['distribution_status'].upper()}")
        print(f"    Custo: {data['operational_cost']:.2f}")
        print(f"    Valor estrategico: {data['strategic_value']:.2f}")
        print()

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


def _screen_temporal_analysis(modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("ANALISE TEMPORAL (DERIVADAS)")
    print("=" * 70)

    try:
        years = int(input("\nNumero de anos para analise: "))
        if years <= 0:
            print("\n[ERRO] Deve ser um numero positivo!")
            return

        result = modeling.temporal_consumption_analysis(years=years, points=50)

        print(f"\nANALISE PARA {years} ANOS:")
        print("-" * 40)
        print(f"Consumo inicial: {result['initial_consumption']:.2f} kWh")
        print(f"Consumo final: {result['final_consumption']:.2f} kWh")
        print(f"Crescimento total: {result['total_growth']:.1f}%")
        print(f"Taxa de crescimento anual: {result['avg_growth_rate']:.2f}%")

        if result["inflection_points"]:
            print(f"Pontos de inflexao detectados: {result['inflection_points']}")

        print(result["qualitative_analysis"])

    except ValueError:
        print("\n[ERRO] Entrada invalida!")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


def _screen_optimize_distribution(modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("OTIMIZACAO DE DISTRIBUICAO DE ENERGIA")
    print("=" * 70)

    results = modeling.optimize_energy_distribution()

    print("\nOTIMIZACAO POR MODULO:")
    print("-" * 40)

    for mod_id, data in results.items():
        m = modeling.graph.get_module(mod_id)
        pt_name = label(m) if m else data["name"]
        print(f"\n  {pt_name}:")
        print(f"    Consumo atual: {data['current_consumption']:.2f} kWh")
        print(f"    Consumo otimo: {data['optimal_consumption']:.2f} kWh")
        print(f"    Eficiencia atual: {data['current_efficiency']*100:.1f}%")
        print(f"    Eficiencia otima: {data['optimal_efficiency']*100:.1f}%")
        if data["improvement"] > 0:
            print(f"    Melhoria potencial: +{data['improvement']:.1f}%")
        else:
            print("    Ja otimizado")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


def _screen_simulate_scenarios(modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("SIMULACAO DE CENARIOS")
    print("=" * 70)

    scenarios = modeling.simulate_scenarios()

    print("\nCENARIOS DE CRESCIMENTO (10 ANOS):")
    print("-" * 40)

    for name, data in scenarios.items():
        print(f"\n  {name.upper()}:")
        print(f"    Taxa anual: {data['avg_annual_rate']:.1f}%")
        print(f"    Consumo final: {data['final_consumption']:.2f} kWh")
        print(f"    Crescimento: {data['growth_percentage']:.1f}%")
        print(f"    {data['analysis']}")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


def _screen_complete_calculus(modeling: MathematicalModeling) -> None:
    """Complete calculus analysis: rates at t=0/5/10 plus optimization.

    The standalone delegated to modeling.complete_analysis() (which no longer
    exists in the pure colony module). This screen composes the available
    colony modeling methods to produce the same educational output.
    """
    print("\n" + "=" * 70)
    print("ANALISE COMPLETA COM CALCULO")
    print("=" * 70)

    for t in (0, 5, 10):
        rate = modeling.consumption_rate_analysis(t)
        print(f"\nt = {t} anos:")
        print(f"  Consumo: {rate['consumption']:.2f} kWh")
        print(f"  Taxa (1a derivada): {rate['first_derivative']:.2f} kWh/ano")
        print(f"  Aceleracao (2a derivada): {rate['second_derivative']:.2f}")
        print(f"  Taxa relativa: {rate['relative_rate']:.2f}%/ano")
        print(f"  Interpretacao: {rate['interpretation']}")

    opt = modeling.optimal_consumption_point()
    print("\nOTIMIZACAO:")
    print("-" * 40)
    if opt.get("minimum"):
        print(
            f"  Consumo minimo: {opt['minimum']['consumption']:.2f} kWh "
            f"em t={opt['minimum']['t']:.2f} anos"
        )
    if opt.get("maximum"):
        print(
            f"  Consumo maximo: {opt['maximum']['consumption']:.2f} kWh "
            f"em t={opt['maximum']['t']:.2f} anos"
        )
    print(opt.get("analysis", ""))

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


def _menu_modeling(graph: InfrastructureGraph) -> None:
    modeling = MathematicalModeling(graph)
    while True:
        print("\n" + "=" * 70)
        print("MODELAGEM MATEMATICA")
        print("=" * 70)
        print("\n 1. Projecao de Consumo Energetico")
        print(" 2. Perda Energetica por Distancia")
        print(" 3. Previsao de Crescimento")
        print(" 4. Analise de Custo-Beneficio")
        print(" 5. Analise Temporal (Derivadas)")
        print(" 6. Otimizacao de Distribuicao")
        print(" 7. Simulacao de Cenarios")
        print(" 8. Analise Completa com Calculo")
        print(" 0. Voltar")
        print("=" * 70)

        try:
            option = input("\nEscolha uma opcao: ").strip()
            if option == "0":
                break
            elif option == "1":
                _screen_project_consumption(graph, modeling)
            elif option == "2":
                _screen_energy_loss(graph, modeling)
            elif option == "3":
                _screen_predict_growth(modeling)
            elif option == "4":
                _screen_cost_benefit(modeling)
            elif option == "5":
                _screen_temporal_analysis(modeling)
            elif option == "6":
                _screen_optimize_distribution(modeling)
            elif option == "7":
                _screen_simulate_scenarios(modeling)
            elif option == "8":
                _screen_complete_calculus(modeling)
            else:
                print("\n[ERRO] Opcao invalida!")
        except ValueError:
            print("\n[ERRO] Entrada invalida!")


# ==================== SCREEN: SUSTAINABILITY ====================

def _screen_sustainability(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("SUSTENTABILIDADE E GOVERNANCA")
    print("=" * 70)

    print("\nANALISE DE SUSTENTABILIDADE:")
    print("-" * 40)

    total_consumption = sum(m.consumption for m in graph.module_list)
    total_capacity = sum(m.capacity for m in graph.module_list)
    critical_count = len([m for m in graph.module_list if m.priority >= 8])

    print(f"  Consumo total: {total_consumption} kWh")
    print(f"  Capacidade total: {total_capacity} kWh")
    safety_margin = (
        (total_capacity - total_consumption) / total_capacity * 100
        if total_capacity > 0 else 0.0
    )
    print(f"  Margem de seguranca: {safety_margin:.1f}%")
    print(f"  Modulos criticos: {critical_count}")

    print("\nRECOMENDACOES ESG:")
    print("-" * 40)
    print("  * Ambiental:")
    print("    - Otimizar consumo energetico")
    print("    - Implementar fontes renovaveis")
    print("    - Reduzir perdas nas conexoes")
    print("  * Social:")
    print("    - Garantir prioridade aos modulos de suporte a vida")
    print("    - Manter comunicacao constante com a tripulacao")
    print("  * Governanca:")
    print("    - Estabelecer protocolos de decisao")
    print("    - Monitorar metricas continuamente")
    print("    - Planejar expansao sustentavel")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== SIMULATIONS ====================

def _screen_simulate_failure(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("SIMULACAO DE FALHA DE MODULO")
    print("=" * 70)

    module_id = _select_module(graph, "Modulo para simular falha")
    if module_id is None:
        return

    print(f"\nSimulando falha no modulo: {label(graph.modules[module_id])}")
    print("-" * 40)

    neighbors = graph.get_neighbors(module_id)
    print(f"  Conexoes afetadas: {len(neighbors)}")

    critical = analysis.articulation_points(graph)
    if module_id in critical:
        print("  IMPACTO: Ponto critico - rede pode ser desconectada!")
        print("  Recomendacao: Implementar redundancia imediatamente")
    else:
        print("  IMPACTO: A rede continua operacional")
        print("  Recomendacao: Monitorar e planejar substituto")

    if len(neighbors) > 1:
        print("\n  Rotas alternativas disponiveis:")
        for i, neighbor_id in enumerate(neighbors[:3], 1):
            n_mod = graph.get_module(neighbor_id)
            if n_mod:
                print(f"    {i}. Via {label(n_mod)}")


def _screen_consumption_peak(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("SIMULACAO DE PICO DE CONSUMO")
    print("=" * 70)

    try:
        peak = int(input("\nPercentual de aumento no consumo (%): "))
        if peak <= 0:
            print("\n[ERRO] Deve ser um numero positivo!")
            return

        print(f"\nSimulando pico de {peak}% no consumo:")
        print("-" * 40)

        total_current = sum(m.consumption for m in graph.module_list)
        total_capacity = sum(m.capacity for m in graph.module_list)
        total_peak = total_current * (1 + peak / 100)

        print(f"  Consumo atual: {total_current:.2f} kWh")
        print(f"  Consumo no pico: {total_peak:.2f} kWh")
        print(f"  Capacidade total: {total_capacity:.2f} kWh")
        print(f"  Margem: {total_capacity - total_peak:.2f} kWh")

        if total_peak > total_capacity:
            print("  ALERTA: Demanda excede capacidade!")
            print("  Recomendacao: Reduzir consumo em modulos nao criticos")
        else:
            print("  OK: Capacidade suficiente para o pico")
            print("  Recomendacao: Monitorar e planejar expansao futura")

        print("\n  Modulos que excederiam sua capacidade:")
        for m in graph.module_list:
            consumption_peak_val = m.consumption * (1 + peak / 100)
            if consumption_peak_val > m.capacity:
                print(f"    * {label(m)}: {consumption_peak_val:.2f} kWh > {m.capacity:.2f} kWh")

    except ValueError:
        print("\n[ERRO] Entrada invalida!")


def _screen_simulate_expansion(modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("SIMULACAO DE EXPANSAO")
    print("=" * 70)

    try:
        years = int(input("\nNumero de anos para expansao: "))
        if years <= 0:
            print("\n[ERRO] Deve ser um numero positivo!")
            return

        prediction = modeling.growth_prediction(years)

        print(f"\nSIMULACAO DE EXPANSAO PARA {years} ANOS:")
        print("-" * 40)
        print(f"  Modulos atuais: {prediction['current_modules']}")
        print(f"  Modulos necessarios: {prediction['modules_needed'][-1]}")
        print(f"  Expansao necessaria: {prediction['expansion_needed']} modulos")

        print("\n  Cronograma sugerido:")
        for t in range(0, years + 1, 2):
            modules = (
                prediction["modules_needed"][t]
                if t < len(prediction["modules_needed"])
                else prediction["modules_needed"][-1]
            )
            print(f"    Ano {prediction['current_year'] + t}: {modules} modulos")

    except ValueError:
        print("\n[ERRO] Entrada invalida!")


def _screen_simulate_optimization(modeling: MathematicalModeling) -> None:
    print("\n" + "=" * 70)
    print("SIMULACAO DE OTIMIZACAO")
    print("=" * 70)

    print("\nOtimizando distribuicao de energia:")
    print("-" * 40)

    results = modeling.optimize_energy_distribution()

    total_savings = sum(
        data["current_consumption"] * (data["improvement"] / 100)
        for data in results.values()
        if data["improvement"] > 0
    )
    print(f"  Economia total potencial: {total_savings:.2f} kWh")

    print("\n  Modulos com maior potencial de melhoria:")
    sorted_modules = sorted(results.items(), key=lambda x: x[1]["improvement"], reverse=True)[:3]
    for mod_id, data in sorted_modules:
        if data["improvement"] > 0:
            m = modeling.graph.get_module(mod_id)
            pt_name = label(m) if m else data["name"]
            print(f"    * {pt_name}: {data['improvement']:.1f}%")


def _menu_simulations(graph: InfrastructureGraph) -> None:
    modeling = MathematicalModeling(graph)
    print("\n" + "=" * 70)
    print("SIMULACOES OPERACIONAIS")
    print("=" * 70)
    print("\n 1. Simular Falha de Modulo")
    print(" 2. Simular Pico de Consumo")
    print(" 3. Simular Expansao")
    print(" 4. Simular Otimizacao")
    print(" 0. Voltar")
    print("=" * 70)

    try:
        option = input("\nEscolha uma opcao: ").strip()
        if option == "0":
            return
        elif option == "1":
            _screen_simulate_failure(graph)
        elif option == "2":
            _screen_consumption_peak(graph)
        elif option == "3":
            _screen_simulate_expansion(modeling)
        elif option == "4":
            _screen_simulate_optimization(modeling)
        else:
            print("\n[ERRO] Opcao invalida!")
    except ValueError:
        print("\n[ERRO] Entrada invalida!")

    input("\nPressione ENTER para continuar...")


# ==================== COMPLETE ANALYSIS ====================

def _screen_complete_analysis(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("ANALISE COMPLETA DO SISTEMA")
    print("=" * 70)

    eff = analysis.analyze_efficiency(graph)

    print("\n1. ANALISE DA REDE:")
    print("-" * 40)
    print(f"  Modulos: {eff['total_modules']}")
    print(f"  Conexoes: {eff['total_connections']}")
    print(f"  Eficiencia global: {eff['overall_status'].upper()}")

    critical = analysis.articulation_points(graph)
    print("\n2. PONTOS CRITICOS:")
    print("-" * 40)
    if critical:
        print(f"  Encontrados: {len(critical)}")
        for c in critical[:5]:
            m = graph.get_module(c)
            if m:
                print(f"    * {label(m)}")
    else:
        print("  Nenhum ponto critico detectado")

    total_consumption = sum(m.consumption for m in graph.module_list)
    total_capacity = sum(m.capacity for m in graph.module_list)
    print("\n3. CONSUMO E CAPACIDADE:")
    print("-" * 40)
    print(f"  Consumo total: {total_consumption:.2f} kWh")
    print(f"  Capacidade total: {total_capacity:.2f} kWh")
    utilization = total_consumption / total_capacity * 100 if total_capacity > 0 else 0.0
    print(f"  Utilizacao: {utilization:.1f}%")

    print("\n4. RECOMENDACOES:")
    print("-" * 40)
    if eff["overall_status"] == "critico":
        print("  * Implementar melhorias urgentes na rede")
    elif eff["overall_status"] == "bom":
        print("  * Otimizar areas com baixa eficiencia")
    else:
        print("  * Manter monitoramento continuo")

    if critical:
        print("  * Criar redundancia para pontos criticos")
    if total_consumption / total_capacity > 0.8:
        print("  * Planejar expansao de capacidade")

    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== ABOUT ====================

def _screen_about() -> None:
    print("\n" + "=" * 70)
    print("SOBRE O SISTEMA")
    print("=" * 70)
    print("\nSIGIC - Sistema Inteligente de Gerenciamento")
    print("Infraestrutura da Colonia Aurora Siger")
    print("\nVersao: 0.4.0")
    print("\nDisciplinas Integradas:")
    print("  * Algoritmos e Estruturas de Dados")
    print("  * Grafos e Algoritmos de Redes")
    print("  * Modelagem Matematica")
    print("  * Calculo Diferencial")
    print("  * Sustentabilidade e Governanca ESG")
    print("\nFuncionalidades:")
    print("  * Visualizacao da rede")
    print("  * Consulta de modulos")
    print("  * Algoritmos de caminho minimo")
    print("  * Modelagem matematica")
    print("  * Simulacoes operacionais")
    print("  * Analise de eficiencia")
    print("\n" + "=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== ADJACENCY MATRIX ====================

def _screen_adjacency_matrix(graph: InfrastructureGraph) -> None:
    print("\n" + "=" * 70)
    print("MATRIZ DE ADJACENCIA")
    print("=" * 70)
    print()

    matrix = graph.get_adjacency_matrix()
    modules = graph.module_list
    n = len(modules)

    # Header row: short PT labels
    header = f"{'':22}"
    for m in modules:
        short = label(m)[:6]
        header += f"{short:>8}"
    print(header)

    # Data rows
    for i, row_mod in enumerate(modules):
        row = f"{label(row_mod):22}"
        for j in range(n):
            val = matrix[i][j]
            row += "       0" if val == 0 else f"{val:>8.1f}"
        print(row)

    print("\n" + "=" * 70)
    print("A matriz complementa a lista de adjacencia: permite consultar em")
    print("tempo O(1) o peso da conexao entre quaisquer dois modulos.")
    print("=" * 70)
    input("\nPressione ENTER para continuar...")


# ==================== HEADER / MENU ====================

def _display_header(graph: InfrastructureGraph) -> None:
    print("=" * 70)
    print("SIGIC - SISTEMA INTELIGENTE DE GERENCIAMENTO")
    print("INFRAESTRUTURA DA COLONIA AURORA SIGER")
    print("=" * 70)
    print(f"Status: {graph.get_module_count()} modulos ativos")
    print(f"Conexoes: {graph.get_connection_count()}")
    print("-" * 70)


def _display_main_menu() -> None:
    print("\nMENU PRINCIPAL")
    print("=" * 70)
    print(" 1. Visualizar Rede da Colonia")
    print(" 2. Consultar Modulo")
    print(" 3. Algoritmos de Rede")
    print(" 4. Modelagem Matematica")
    print(" 5. Sustentabilidade e Governanca")
    print(" 6. Simulacoes Operacionais")
    print(" 7. Analise Completa")
    print(" 8. Sobre o Sistema")
    print(" 9. Matriz de Adjacencia")
    print(" 0. Sair")
    print("=" * 70)


# ==================== MAIN ====================

def main() -> None:
    """Entry point for the `sigic` console script."""
    graph = topology.build_graph()
    while True:
        # Hardcoded command list — no user input, no injection risk.
        subprocess.run(["cmd", "/c", "cls"] if os.name == "nt" else ["clear"],
                       check=False)
        _display_header(graph)
        _display_main_menu()

        try:
            option = input("\nEscolha uma opcao: ").strip()
            if option == "0":
                print("\nSaindo do SIGIC...")
                print("Obrigado por utilizar o sistema!")
                break
            elif option == "1":
                _screen_view_network(graph)
            elif option == "2":
                _screen_query_module(graph)
            elif option == "3":
                _menu_algorithms(graph)
            elif option == "4":
                _menu_modeling(graph)
            elif option == "5":
                _screen_sustainability(graph)
            elif option == "6":
                _menu_simulations(graph)
            elif option == "7":
                _screen_complete_analysis(graph)
            elif option == "8":
                _screen_about()
            elif option == "9":
                _screen_adjacency_matrix(graph)
            else:
                print("\n[ERRO] Opcao invalida! Tente novamente.")
        except KeyboardInterrupt:
            print("\n\nSaindo do sistema...")
            break
        except Exception as e:
            print(f"\n[ERRO] Erro inesperado: {e}")
            input("\nPressione ENTER para continuar...")
