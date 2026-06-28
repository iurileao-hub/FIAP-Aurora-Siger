# fases/fase-4/figuras/gerar_rede.py
"""Regenerates the colony network diagram (13 nodes) from the canonical graph.

Requires Graphviz (`dot`). Writes rede_colonia.dot and rede_colonia.pdf next to
this file. Node labels are Portuguese (PT_LABELS); edge colour encodes the type.
"""

import os
import subprocess

from aurora_siger.colony import topology
from aurora_siger.colony.cli import PT_LABELS

HERE = os.path.dirname(os.path.abspath(__file__))
EDGE_COLOR = {"energy": "orange", "data": "blue", "life": "red"}


def build_dot() -> str:
    g = topology.build_graph()
    lines = ["graph ColoniaAuroraSiger {", '  layout=neato; overlap=false;',
             '  node [shape=box, style=rounded, fontname="Helvetica"];']
    for m in g.module_list:
        x, y = m.position
        lines.append(f'  {m.id} [label="{PT_LABELS[m.id]}\\n(p{m.priority})", pos="{x},{y}!"];')
    seen = set()
    for id1, neigh in g.adjacency_list.items():
        for id2 in neigh:
            key = (min(id1, id2), max(id1, id2))
            if key in seen:
                continue
            seen.add(key)
            ctype = g.connection_types.get(g._get_edge_key(id1, id2), "energy")
            w = g.get_weight(id1, id2)
            lines.append(f'  {id1} -- {id2} [label="{w:g}", color={EDGE_COLOR.get(ctype,"black")}];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    dot = build_dot()
    dot_path = os.path.join(HERE, "rede_colonia.dot")
    pdf_path = os.path.join(HERE, "rede_colonia.pdf")
    with open(dot_path, "w") as f:
        f.write(dot)
    subprocess.run(["dot", "-Tpdf", dot_path, "-o", pdf_path], check=True)
    print(f"Diagrama gerado: {pdf_path}")


if __name__ == "__main__":
    main()
