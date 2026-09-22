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
