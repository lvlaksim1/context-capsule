# Project architecture

## DECISION — v2 architecture

Core provides schemas, lifecycle tooling, templates, tests, and the universal Manager Protocol.

Each installed repository owns five durable layers:

1. project semantics (`project/`);
2. Project Manager identity/mandate and active beliefs-goals-intentions-plans (`manager/`);
3. typed semantic/episodic/procedural memory (`memory/`);
4. durable rules/decisions/history;
5. compact current objective project state (`current/`).

A chat/model/agent process is only a temporary runtime carrier. Runtime checkpoint state is explicitly outside the manager-identity boundary.

## Authority coordinates

Project Manager persistence and product truth are separate coordinates.

- Manager-state authority for the v2 development manager is `v2-manager-runtime`. Its identity, mandate, BDI state, memory, and working views persist there.
- Product authority remains `main`, which continues to represent the stable v1.3.1 production line.
- Discovery is a separate bootstrap concern and currently stays on `v2-manager-runtime` for this isolated development manager.

The compatibility field `authoritative_branch` aliases manager-state authority only. A feature/runtime checkout never becomes an authority merely because work executes there.

