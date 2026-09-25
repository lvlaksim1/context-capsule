# Latest handoff

## TASK-CC-RUNTIME-IDENTITY-ADOPTION-001

Owner-authorized Context Capsule v2 development task.

Runtime identity is fixed for the lifetime of a persistent-Agent runtime. A different persistent target requires a separate runtime.

Interactive bounded delegation preserves caller responsibility but uses durable `continuation:manual-pull`. Autonomous continuation uses a dependency-bound `runtime:caller-continuation` and a fresh caller runtime. Same-runtime persistent-Agent switching is forbidden.

User-visible persistent-Agent/infrastructure messages require `DD.MM.YYYY · HH:MM MSK · <source_id>` as diagnostic metadata; repository-backed reinstantiation remains identity authority.

IOSPM-001 has been reconciled against canonical Auditor evidence and is CLOSED / Medium / High confidence.

Stable `main`, stable-v2 publication, and consumer migration remain outside scope.
