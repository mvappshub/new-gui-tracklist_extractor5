# PM Ticket: Plan for fluent_gui.py Removal

- Context: fluent_gui.py served as the compatibility layer around the new UI package. All production entry points now use `app.py` and modular imports.
- Decision: Removal executed as part of change `refactor-architecture-modularity`.
- Steps:
  1) Inventory imports (completed 2025-10-26).
  2) Update entry points, scripts, and tests to reference authoritative modules (completed).
  3) Delete `fluent_gui.py`, retire characterization tests, and document migration path (completed).
- Owner: maintainers
- Status: completed
- Notes: External consumers should import symbols directly from `ui/`, `services/`, `core/`, or `adapters/`. Legacy exports are no longer available.
- Related change: openspec/changes/refactor-architecture-modularity
