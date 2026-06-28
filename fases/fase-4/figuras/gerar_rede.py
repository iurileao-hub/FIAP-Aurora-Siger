# fases/fase-4/figuras/gerar_rede.py
"""Mapa estilizado da colônia Aurora Siger sobre o terreno marciano.

Lê o grafo canônico (`topology.build_graph`) e desenha um 'mapa de base' marciano,
substituindo o antigo diagrama Graphviz. Escreve rede_colonia.png e rede_colonia.pdf
ao lado deste arquivo.

- terreno: gradiente ferrugem + curvas de nível topográficas + crateras + vinheta
- módulos: domos coloridos por tier de criticidade, tamanho ∝ centralidade (Brandes)
- conexões: dutos com estilo por tipo (energia sólida / dados tracejado / vital pontilhado)
- destaque do achado: ponto de articulação (Logística) e Gerador Eólico isolado (corte)

Layout force-directed (Fruchterman-Reingold) determinístico, iniciado das posições
físicas dos módulos. Sem aleatoriedade variável (RandomState fixo). Depende apenas
de matplotlib + numpy (já usados nas figuras das fases anteriores).
"""
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Circle, Ellipse
from matplotlib.lines import Line2D

from aurora_siger.colony import topology, analysis

OUT = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.RandomState(42)

# ---- paleta marciana --------------------------------------------------------
BG_TOP = np.array([0x24, 0x10, 0x0b]) / 255      # ferrugem escura (topo)
BG_BOT = np.array([0x6b, 0x32, 0x1b]) / 255      # ferrugem clara (base)
CONTOUR = "#854127"
WARMWHITE = "#FBF3E7"
TIER = {                                          # cor por criticidade
    "Vital":    "#FFD166",   # ouro quente
    "Sustento": "#2EC4A6",   # teal
    "Expansão": "#5BB8F0",   # azul céu
}
ETYPE = {                                         # cor + estilo por tipo de conexão
    "energy": ("#FFB02E", "solid"),
    "data":   ("#5BD2F0", (0, (5, 3))),
    "life":   ("#FF6B81", (0, (1, 2))),
}
PT_TIER = {10: "Vital", 7: "Sustento", 4: "Expansão"}
SHORT = {1: "Controle", 2: "Suporte de Vida", 3: "Habitat", 4: "Solar",
         5: "Nuclear", 6: "Comunicações", 7: "Suporte Médico", 8: "Alimentos",
         9: "Logística", 10: "ISRU", 11: "Oficina", 12: "Laboratório",
         13: "Eólico"}


def halo(fg="#1a0a05", lw=3):
    return [pe.withStroke(linewidth=lw, foreground=fg)]


def terrain(ax, xlim, ylim):
    """Gradiente ferrugem + ruído + curvas de nível + vinheta.

    O terreno é rasterizado em baixa resolução (manchas suaves ao ser ampliado
    por interpolação) — comprime muito melhor que ruído por-pixel e fica com
    aspecto de mottling marciano. Domos, dutos e texto são vetoriais e nítidos.
    """
    H, W = 200, 300
    t = np.linspace(0, 1, H)[:, None, None]
    img = BG_TOP[None, None, :] * (1 - t) + BG_BOT[None, None, :] * t
    img = np.repeat(img, W, axis=1)
    img = img + RNG.normal(0, 0.012, img.shape)
    img = np.clip(img, 0, 1)
    ax.imshow(img, extent=[*xlim, *ylim], origin="lower",
              aspect="auto", zorder=0, interpolation="bilinear")

    # curvas de nível: campo suave = soma de gaussianas com centros fixos
    gx = np.linspace(*xlim, 240)
    gy = np.linspace(*ylim, 240)
    GX, GY = np.meshgrid(gx, gy)
    Z = np.zeros_like(GX)
    centers = RNG.uniform([xlim[0], ylim[0]], [xlim[1], ylim[1]], size=(7, 2))
    for cx, cy in centers:
        s = RNG.uniform(1.3, 2.6)
        Z += np.exp(-((GX - cx) ** 2 + (GY - cy) ** 2) / (2 * s ** 2))
    ax.contour(GX, GY, Z, levels=11, colors=CONTOUR, linewidths=0.6,
               alpha=0.30, zorder=1)

    # crateras esparsas
    for _ in range(9):
        cx, cy = RNG.uniform([xlim[0], ylim[0]], [xlim[1], ylim[1]])
        r = RNG.uniform(0.12, 0.4)
        ax.add_patch(Circle((cx, cy), r, fc="none", ec=CONTOUR,
                            lw=0.7, alpha=0.25, zorder=1))

    # vinheta radial (escurece as bordas)
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = W / 2, H / 2
    d = np.sqrt(((xx - cx) / (W / 2)) ** 2 + ((yy - cy) / (H / 2)) ** 2)
    vig = np.zeros((H, W, 4))
    vig[..., 3] = np.clip((d - 0.6) * 0.8, 0, 0.55)
    ax.imshow(vig, extent=[*xlim, *ylim], origin="lower",
              aspect="auto", zorder=1.5, interpolation="bilinear")


def dome(ax, x, y, r, color, z=4):
    """Domo: esfera com brilho no topo-esquerdo + sombra no chão."""
    ax.add_patch(Ellipse((x, y - r * 0.55), r * 2.1, r * 0.7, fc="#160803",
                        ec="none", alpha=0.45, zorder=z - 0.5))
    ax.add_patch(Circle((x, y), r, fc=color, ec=WARMWHITE, lw=1.4, zorder=z))
    ax.add_patch(Circle((x, y), r * 0.7, fc="none", ec="white", lw=0.8,
                        alpha=0.28, zorder=z + 0.05))
    ax.add_patch(Circle((x - r * 0.32, y + r * 0.34), r * 0.32, fc="white",
                        ec="none", alpha=0.5, zorder=z + 0.1))
    ax.add_patch(Circle((x, y), r, fc="none", ec="#1a0a05", lw=0.6,
                        alpha=0.4, zorder=z + 0.2))


def fruchterman(nodes, edges, pos0, iters=600, seed=7):
    """Layout force-directed determinístico (FR), iniciado das posições físicas."""
    rng = np.random.RandomState(seed)
    idx = {nid: i for i, nid in enumerate(nodes)}
    pos = np.array([pos0[n] for n in nodes], float)
    pos += rng.normal(0, 0.01, pos.shape)
    n = len(nodes)
    k = np.sqrt(100.0 / n)
    t = 2.5
    cool = t / (iters + 1)
    E = [(idx[a], idx[b]) for a, b in edges]
    for _ in range(iters):
        disp = np.zeros_like(pos)
        for i in range(n):
            delta = pos[i] - pos
            dist = np.linalg.norm(delta, axis=1)
            dist[i] = 1e9
            dist = np.where(dist < 0.01, 0.01, dist)
            disp[i] += ((k * k / dist)[:, None] * (delta / dist[:, None])).sum(0)
        for a, b in E:
            delta = pos[a] - pos[b]
            dist = np.linalg.norm(delta) or 0.01
            f = (dist * dist / k) * (delta / dist)
            disp[a] -= f
            disp[b] += f
        length = np.linalg.norm(disp, axis=1)
        length = np.where(length < 0.01, 0.01, length)
        pos += (disp / length[:, None]) * np.minimum(length, t)[:, None]
        t = max(t - cool, 0.02)
    return {nid: pos[idx[nid]] for nid in nodes}


def main():
    g = topology.build_graph()
    bw = analysis.betweenness(g)
    artic = set(analysis.articulation_points(g))
    bw_max = max(bw.values()) or 1.0

    nodes = [m.id for m in g.module_list]
    edges = list({(min(a, b), max(a, b))
                  for a, nb in g.adjacency_list.items() for b in nb})
    pos0 = {m.id: np.array(m.position, float) * np.array([1.0, 1.1])
            for m in g.module_list}
    pos = fruchterman(nodes, edges, pos0)

    # normaliza p/ largura ~12 e reposiciona na origem
    P = np.array([pos[n] for n in nodes])
    P -= P.min(0)
    span = P.max(0)
    P *= 12.0 / max(span[0], 1e-6)
    pos = {n: P[i] for i, n in enumerate(nodes)}

    radius = {n: 0.30 + 0.34 * np.sqrt(bw[n] / bw_max) for n in nodes}

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    padx, pady = 1.7, 1.5
    xlim = (min(xs) - padx, max(xs) + padx)
    ylim = (min(ys) - pady, max(ys) + pady + 0.7)  # espaço p/ título

    ratio = (xlim[1] - xlim[0]) / (ylim[1] - ylim[0])
    fig, ax = plt.subplots(figsize=(13, 13 / ratio), dpi=150)
    ax.axis("off")
    terrain(ax, xlim, ylim)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect("equal")

    # ---- arestas (dutos), ancoradas na borda dos domos ----
    for (id1, id2) in sorted(edges):
        ctype = g.connection_types.get(g._get_edge_key(id1, id2), "energy")
        w = g.get_weight(id1, id2)
        color, style = ETYPE.get(ctype, ETYPE["energy"])
        p1, p2 = pos[id1], pos[id2]
        u = p2 - p1
        d = np.linalg.norm(u) or 1e-6
        u = u / d
        s1 = p1 + u * (radius[id1] + 0.05)
        s2 = p2 - u * (radius[id2] + 0.05)
        is_cut = (id1, id2) == (9, 13)
        ax.plot([s1[0], s2[0]], [s1[1], s2[1]],
                color="#FF4D4D" if is_cut else color,
                lw=6.5 if is_cut else 5.0, alpha=0.14, zorder=2,
                solid_capstyle="round")
        ax.plot([s1[0], s2[0]], [s1[1], s2[1]],
                color="#FF4D4D" if is_cut else color, lw=2.2,
                ls="--" if is_cut else style, alpha=0.95, zorder=2.1,
                solid_capstyle="round")
        perp = np.array([-u[1], u[0]])
        mid = (s1 + s2) / 2 + perp * 0.18
        ax.text(*mid, f"{w:g}", fontsize=8, color=WARMWHITE, ha="center",
                va="center", zorder=2.5, alpha=0.92, path_effects=halo(lw=2.2))
        if is_cut:                      # marca de corte no duto frágil
            c = (s1 + s2) / 2
            for off in (-0.12, 0.12):
                a0 = c + perp * 0.16 + u * off
                a1 = c - perp * 0.16 + u * off
                ax.plot([a0[0], a1[0]], [a0[1], a1[1]], color="#FFE0E0",
                        lw=2.2, zorder=2.6, solid_capstyle="round")

    # ---- nós (domos) ----
    for m in g.module_list:
        x, y = pos[m.id]
        r = radius[m.id]
        if m.id in artic:               # anel de alerta do ponto de corte
            ax.add_patch(Circle((x, y), r + 0.22, fc="none", ec="#FF4D4D",
                                lw=2.2, ls=(0, (4, 3)), zorder=3.5, alpha=0.9))
        dome(ax, x, y, r, TIER[PT_TIER[m.priority]])
        ax.text(x, y - r - 0.30, SHORT[m.id], fontsize=10.5, color=WARMWHITE,
                ha="center", va="top", zorder=6, fontweight="bold",
                path_effects=halo())

    # ---- anotações do achado ----
    x9, y9 = pos[9]
    ax.annotate("Único ponto de articulação\nremovê-lo isola o Eólico",
                xy=(x9, y9 + radius[9] + 0.25), xytext=(x9 - 0.3, y9 + 3.1),
                fontsize=11, color="#FFE2E2", ha="center", va="center",
                zorder=7, fontweight="bold", path_effects=halo(),
                bbox=dict(boxstyle="round,pad=0.5", fc="#3a0f0f", ec="#FF6B6B",
                          lw=1.3, alpha=0.85),
                arrowprops=dict(arrowstyle="-|>", color="#FF6B6B", lw=1.8,
                                connectionstyle="arc3,rad=0.15"))
    x13, y13 = pos[13]
    ax.add_patch(Ellipse((x13, y13), radius[13] * 4.2, radius[13] * 3.6,
                        fc="#FF4D4D", ec="#FF6B6B", ls=(0, (3, 3)), lw=1.4,
                        alpha=0.10, zorder=2.6))
    ax.text(x13, y13 + radius[13] + 0.95, "fragmento isolado", fontsize=8.5,
            color="#FFB3B3", ha="center", va="center", style="italic",
            zorder=7, path_effects=halo(lw=2.2))

    # ---- título ----
    ax.text(xlim[0] + 0.3, ylim[1] - 0.35,
            "Colônia Aurora Siger — a rede sobre o terreno marciano",
            fontsize=17, color=WARMWHITE, ha="left", va="top",
            fontweight="bold", zorder=8, path_effects=halo(lw=4))
    ax.text(xlim[0] + 0.3, ylim[1] - 0.92,
            "13 módulos · 20 conexões · tamanho do domo ∝ centralidade",
            fontsize=10.5, color="#E9C9A7", ha="left", va="top",
            zorder=8, path_effects=halo(lw=2.5))

    # ---- legenda ----
    handles = [
        Line2D([], [], marker="o", ls="", mfc=TIER["Vital"], mec=WARMWHITE,
               ms=12, label="Vital"),
        Line2D([], [], marker="o", ls="", mfc=TIER["Sustento"], mec=WARMWHITE,
               ms=12, label="Sustento"),
        Line2D([], [], marker="o", ls="", mfc=TIER["Expansão"], mec=WARMWHITE,
               ms=12, label="Expansão"),
        Line2D([], [], color=ETYPE["energy"][0], lw=2.4, label="energia"),
        Line2D([], [], color=ETYPE["data"][0], lw=2.4, ls="--", label="dados"),
        Line2D([], [], color=ETYPE["life"][0], lw=2.4, ls=":", label="suporte vital"),
    ]
    leg = ax.legend(handles=handles, loc="lower right", ncol=2, fontsize=10,
                    facecolor="#1c0d07", edgecolor="#854127", framealpha=0.85,
                    labelcolor=WARMWHITE, borderpad=0.9, columnspacing=1.4)
    leg.set_zorder(9)

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(os.path.join(OUT, "rede_colonia.png"), dpi=150, facecolor=BG_TOP)
    fig.savefig(os.path.join(OUT, "rede_colonia.pdf"), facecolor=BG_TOP)
    print("ok:", os.path.join(OUT, "rede_colonia.png"))


if __name__ == "__main__":
    main()
