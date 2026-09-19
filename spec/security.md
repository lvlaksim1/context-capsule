# Security and privacy

Context Capsule Core is stateless with respect to installed projects.

It MUST NOT:

- receive target project context;
- maintain a registry of installed repositories;
- collect telemetry or usage statistics;
- copy target context into Core;
- require a network callback during normal capsule operation.

A target repository's access controls govern its own `.context/` content. Private repository context stays private to that repository and its authorized tooling.
