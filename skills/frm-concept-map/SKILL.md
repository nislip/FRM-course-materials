---
name: frm-concept-map
description: Explore how FRM topics connect using the FRM Mind Map (the course concept graph). Use when the user asks how FRM concepts relate, what to study before or after a topic, wants a study path or map of a reading, asks what their notes are missing or how complete they are, or wants to open or see the FRM mind map, concept graph, or the term, concept or formula glossary.
---

# FRM Mind Map

Use the concept graph to explain connections between FRM topics, plan study order and show coverage gaps.

## Where the data is

- `${CLAUDE_SKILL_DIR}/../../graph/concept-graph.json` is the graph to query:
  - `summary`: counts, plus the `incomplete` ids (defined but no definition or formula yet) and the `missing` ids (linked to but never defined).
  - `nodes`: keyed by id. Each node has `name`, `kind` (`term`, `concept`, `formula` or `missing`), `part`, `reading`, `file`, `complete`, `definition` or `latex`, and `links`.
  - Each item in `links` has an `id` and a `type`. `related` links are symmetric. Other types (`uses-concept`, `variant`, or custom ones like `is-a`) have a `direction`: `out` means this node points at the other one.
- `${CLAUDE_SKILL_DIR}/../../graph/concept-graph.html` is the FRM Mind Map page for people: an interactive map plus Terms, Concepts and Formulas glossary tabs, with formulas rendered.
- `${CLAUDE_SKILL_DIR}/../../graph/concept-graph.md` is the same graph as a Mermaid diagram.

## What to do

**How does X relate to Y / what connects to X?**
Find the node, then walk its `links` one or two hops. Explain each connection in plain words using the link type, e.g. "Parametric VaR *uses the concept* of Value at Risk". To find a path between two topics, do a breadth-first search over `links` and report the shortest chain.

**What should I study first / study path for a topic?**
Treat outgoing `uses-concept` and `is-a` links as prerequisites: a formula needs its concepts, and a sub-type needs its parent. Order the topics so prerequisites come first, group them by `reading`, and flag any prerequisite that is `incomplete` or `missing`.

**Map of a reading or part:**
Filter nodes by `reading` or `part`. Summarize the clusters, and draw a small Mermaid `flowchart LR` of just that subgraph if the user wants a picture.

**What's missing from my notes / how complete are they?**
Report from `summary`: the counts, the `missing` ids grouped by which nodes link to them, and the `incomplete` ids grouped by `reading`. Suggest filling in the most-linked gaps first, since they unblock the most other topics.

**Show me the mind map / a glossary:**
On macOS, run `open "${CLAUDE_SKILL_DIR}/../../graph/concept-graph.html"`; otherwise give the user the path. Point them to the tab they want, or to a specific entry with an anchor: `#map/<id>` focuses a node, `#terms`, `#concepts` or `#formulas` opens a glossary, and `#formulas/<id>` jumps to one entry. (`open` drops the anchor on file URLs, so tell the user which tab to click.)

## Rules

- For full details of a single entry (variables, examples, sources), use the `frm-lookup` skill or open the node's `file`.
- The `graph/` files are generated. If they look out of date with `semantic-layer/`, tell the user to run `python3 scripts/build_graph.py`; don't hand-edit them.
