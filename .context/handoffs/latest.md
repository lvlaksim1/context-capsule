# Latest handoff

## Master Plan item 1 complete

Context Capsule v1.3.1 remains the stable production line on `main`. Existing consumers have not been migrated.

The v2 development line lives on `v2-manager-runtime`.

Project Manager v2 now has a normative Core-managed Contract at `.context/manager/CONTRACT.md`. It defines owner-message semantics, bounded authority, BDI state, commitment lifecycle, evidence revision, reconciliation, durable-memory lifecycle, work lifecycle, self-modification, external expertise, and persistence/privacy.

Current Core provenance: `8b91e41737615f3c54ff87b193d8df6a6a886644`.

Verification evidence: GitHub Actions run `35797459058` — success across 26 permanent tests, compile, self VALID, Project Manager READY, self reinstantiation smoke, and isolated `evrasia-hd-testbed` compatibility smoke.

The testbed itself was not modified; CI tested a temporary clone.

Master Plan item 1 is therefore complete enough to proceed. The next owner-directed stage is item 2: design the Minimal Service Agent Base that will later underpin Supervisor, Auditor, Specialist Agents, and Agent Factory.

Do not publish stable v2 or migrate existing consumers without explicit owner approval.
