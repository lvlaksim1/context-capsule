# Current state

## FACT — Current semantic state

Context Capsule Core v1.2.0 is prepared for release.

Compared with v1.1.0 it adds stable project semantics (`project/identity`, `goals`, `architecture`, `constraints`), split compact current working set (`state`, `blockers`, `next`), stronger evidence precedence, semantic-only synchronization for projects with volatile runtime stores, branch-aware discovery metadata, CAS-aware lifecycle mutations, audit/compactness warnings, and chained migrations.

The design incorporates lessons from real legacy capsules in `fgis-fsa-il`, `telegram-receiver`, and `ai-agent-lab` without storing their project context in Core.
