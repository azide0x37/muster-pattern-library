# Muster Pattern Library

Muster is a catalog of reusable operational shapes for small Linux appliances, especially systemd-based edge machines.

The repository is organized around pattern contracts rather than loose unit-file snippets. Each pattern has a stable ID, manifest, README, example artifacts, and validation rules.

## Repository Shape

```text
schemas/      JSON Schema for pattern manifests
templates/    Copyable pattern authoring templates
patterns/     Tech I, II, and III pattern folders
examples/     Concrete appliance sketches
tools/        Validation and documentation renderers
docs/         Taxonomy, authoring guide, generated index, graph
tests/        Repository-level validation tests
```

## Fast Checks

Use UV for Python commands:

```sh
uv run python tools/validate_patterns.py
uv run python tools/check_composition_rules.py
uv run python tools/render_index.py --check
uv run python tools/render_graph.py --check
uv run python -m unittest discover tests
```

## Current Scope

The first milestone is a complete, machine-checkable scaffold for the planned Muster pattern catalog:

- Tech I Common, Rare, and Mythic patterns
- Tech II Common and Rare patterns
- Tech III Common, Rare, and Mythic patterns
- Example appliance sketches for edge bundles, Bluetooth audio, DVD ripping, and G-code spooling

`docs/index.md` and `docs/pattern-graph.md` are generated from manifests. Do not hand-edit them.
`docs/completion.md` is also generated and reports maturity from manifest status fields.
