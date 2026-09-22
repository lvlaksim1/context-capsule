# Procedural memory

- For a major Context Capsule change, develop on an isolated branch, keep the stable release line untouched, add explicit migration rather than overloading repair, and verify both local tests and hosted CI.
- Test continuity by creating manager state with an open commitment, rebuilding recovery from repository-only state, and asserting identity plus commitment survive without prior chat history.
- Treat specialist-agent or external-source output as evidence until the Project Manager evaluates provenance and promotes a durable conclusion.
- After a significant architecture/release milestone, consolidate manager state: resolve completed intentions, supersede stale beliefs explicitly, and move reusable lessons into typed memory.
