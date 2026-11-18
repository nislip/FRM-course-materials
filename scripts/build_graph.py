"""Build the FRM Mind Map (concept graph) from the semantic layer.

Reads every YAML file under semantic-layer/ and writes:
  graph/concept-graph.json  machine-readable graph the plugin's skills query
  graph/concept-graph.md    Mermaid diagram (renders on GitHub and in VS Code preview)
  graph/concept-graph.html  interactive page (open in a browser)

Output is deterministic: nodes and edges are sorted, there are no timestamps,
and the HTML uses a non-random layout, so the same YAML always produces the
same files and git diffs show only real changes.

Usage: python3 scripts/build_graph.py
"""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LAYER = ROOT / "semantic-layer"
OUT = ROOT / "graph"

# Folder name under semantic-layer/ -> node kind
KINDS = {"terminology": "term", "concepts": "concept", "formulas": "formula"}

# Fields on an entry that point at other entries, and the edge type they imply
LINK_FIELDS = {
    "related": "related",
    "concepts": "uses-concept",
    "variants": "variant",
}


def is_empty(value):
    return value is None or value == "None" or value == "" or value == [] or value == {}


# Fields shown in their own place in the outputs; every other non-empty field
# on an entry goes into the node's "details" (variables, assumptions, examples...)
CORE_FIELDS = {"id", "name", "definition", "latex", "source", "aliases", "acronyms", *LINK_FIELDS}


def details_of(entry):
    """Extra fields as an ordered list, so the glossary shows them in YAML order."""
    return [{"field": k, "value": v} for k, v in entry.items() if k not in CORE_FIELDS and not is_empty(v)]


def as_list(value):
    if is_empty(value):
        return []
    return [str(v) for v in value] if isinstance(value, list) else [str(value)]


def load_entries(path):
    data = yaml.safe_load(path.read_text()) or []
    if not isinstance(data, list):
        sys.exit(f"{path}: expected a list of entries")
    return data


def iter_links(value):
    """Yield (target_id, type_or_None) from a link field.

    Accepts plain ids (`related: [market-risk]`) or typed links
    (`related: [{id: market-risk, type: is-a}]`).
    """
    if is_empty(value):
        return
    for item in value if isinstance(value, list) else [value]:
        if isinstance(item, dict):
            yield str(item["id"]), item.get("type")
        else:
            yield str(item), None


def build():
    nodes = {}
    edges = set()

    for folder, kind in KINDS.items():
        for path in sorted((LAYER / folder).rglob("*.yaml")):
            part = path.parent.name
            reading = path.stem
            for entry in load_entries(path):
                node_id = str(entry["id"])
                if node_id in nodes:
                    sys.exit(f"{path}: duplicate id '{node_id}'")
                text = entry.get("definition") if kind != "formula" else entry.get("latex")
                nodes[node_id] = {
                    "id": node_id,
                    "name": entry.get("name", node_id),
                    "kind": kind,
                    "part": part,
                    "reading": reading,
                    "file": str(path.relative_to(ROOT)),
                    "aliases": as_list(entry.get("aliases")) + as_list(entry.get("acronyms")),
                    "complete": not is_empty(text),
                    "definition": None if is_empty(entry.get("definition")) else " ".join(str(entry["definition"]).split()),
                    "latex": None if is_empty(entry.get("latex")) else str(entry["latex"]).strip(),
                    "source": None if is_empty(entry.get("source")) else entry["source"],
                    "details": details_of(entry),
                }
                for field, default_type in LINK_FIELDS.items():
                    for target, link_type in iter_links(entry.get(field)):
                        edge_type = link_type or default_type
                        if edge_type == "related":
                            # Untyped "related" is symmetric: store each pair once
                            a, b = sorted((node_id, target))
                            edges.add((a, b, edge_type))
                        else:
                            edges.add((node_id, target, edge_type))

    # Anything linked to but not yet defined becomes a placeholder node
    for source, target, _ in edges:
        for node_id in (source, target):
            if node_id not in nodes:
                nodes[node_id] = {
                    "id": node_id,
                    "name": node_id.replace("-", " ").title(),
                    "kind": "missing",
                    "part": None,
                    "reading": None,
                    "file": None,
                    "aliases": [],
                    "complete": False,
                    "definition": None,
                    "latex": None,
                    "source": None,
                    "details": [],
                }

    node_list = [nodes[k] for k in sorted(nodes)]
    edge_list = [{"source": s, "target": t, "type": ty} for s, t, ty in sorted(edges)]
    return node_list, edge_list


def mermaid_id(node_id):
    return node_id.replace("-", "_")


def render_mermaid(nodes, edges):
    lines = ["flowchart LR"]
    by_reading = {}
    for node in nodes:
        by_reading.setdefault(node["reading"] or "not-yet-defined", []).append(node)
    for reading in sorted(by_reading):
        lines.append(f'  subgraph {mermaid_id(reading)}["{reading}"]')
        for node in by_reading[reading]:
            name = node["name"].replace('"', "'")
            lines.append(f'    {mermaid_id(node["id"])}["{name}"]')
        lines.append("  end")
    for edge in edges:
        s, t = mermaid_id(edge["source"]), mermaid_id(edge["target"])
        if edge["type"] == "related":
            lines.append(f"  {s} --- {t}")
        else:
            lines.append(f'  {s} -->|{edge["type"]}| {t}')
    lines += [
        "  classDef term fill:#dbeafe,stroke:#2563eb,color:#1e3a8a",
        "  classDef concept fill:#dcfce7,stroke:#16a34a,color:#14532d",
        "  classDef formula fill:#fef3c7,stroke:#d97706,color:#78350f",
        "  classDef missing fill:#f3f4f6,stroke:#9ca3af,color:#6b7280,stroke-dasharray:4 3",
        "  classDef incomplete stroke-dasharray:4 3",
    ]
    for kind in ("term", "concept", "formula", "missing"):
        ids = [mermaid_id(n["id"]) for n in nodes if n["kind"] == kind]
        if ids:
            lines.append(f"  class {','.join(ids)} {kind}")
    incomplete = [mermaid_id(n["id"]) for n in nodes if not n["complete"] and n["kind"] != "missing"]
    if incomplete:
        lines.append(f"  class {','.join(incomplete)} incomplete")

    done = sum(1 for n in nodes if n["complete"])
    return (
        "# FRM Mind Map\n\n"
        "<!-- Generated by scripts/build_graph.py. Do not edit by hand. -->\n\n"
        f"{len(nodes)} nodes, {len(edges)} links, {done} with a definition or formula.\n\n"
        "Blue = term, green = concept, amber = formula, grey = referenced but not yet defined. "
        "Dashed border = definition still missing.\n\n"
        "```mermaid\n" + "\n".join(lines) + "\n```\n"
    )


def render_html(nodes, edges):
    template = (Path(__file__).parent / "graph_template.html").read_text()
    data = json.dumps({"nodes": nodes, "edges": edges}, indent=1, sort_keys=True, ensure_ascii=False)
    return template.replace("/*GRAPH_DATA*/", data.replace("</", "<\\/"))


def render_json(nodes, edges):
    """Graph keyed by id, with each node's links inline, so an agent can look
    up one node and see all its neighbours without scanning the edge list."""
    by_id = {n["id"]: {**n, "links": []} for n in nodes}
    for e in edges:
        s, t, ty = e["source"], e["target"], e["type"]
        if ty == "related":
            by_id[s]["links"].append({"id": t, "type": ty})
            by_id[t]["links"].append({"id": s, "type": ty})
        else:
            by_id[s]["links"].append({"id": t, "type": ty, "direction": "out"})
            by_id[t]["links"].append({"id": s, "type": ty, "direction": "in"})
    for n in by_id.values():
        n["links"].sort(key=lambda l: (l["type"], l["id"], l.get("direction", "")))
    summary = {
        "nodes": len(nodes),
        "links": len(edges),
        "complete": sum(1 for n in nodes if n["complete"]),
        "incomplete": sorted(n["id"] for n in nodes if not n["complete"] and n["kind"] != "missing"),
        "missing": sorted(n["id"] for n in nodes if n["kind"] == "missing"),
    }
    doc = {
        "_comment": "Generated by scripts/build_graph.py. Do not edit by hand.",
        "summary": summary,
        "nodes": by_id,
    }
    return json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main():
    nodes, edges = build()
    OUT.mkdir(exist_ok=True)
    (OUT / "concept-graph.json").write_text(render_json(nodes, edges))
    (OUT / "concept-graph.md").write_text(render_mermaid(nodes, edges))
    (OUT / "concept-graph.html").write_text(render_html(nodes, edges))
    print(f"graph: {len(nodes)} nodes, {len(edges)} links -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
