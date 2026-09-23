# DEC-0016 — Authority-bearing recovery integrity

- Status: accepted for development
- Date: 2026-09-23
- Trigger: independent audit `AUD-2026-09-23-CCPM-001`, findings CCPM-001 through CCPM-004, independently reproduced by the Context Capsule Project Manager.

## Decision

1. **Exact Core binding.** Authority-bearing Project Manager validation/recovery must resolve the exact Git commit declared by `.context/capsule.json.core_commit` and compare every Core-managed governing surface to the canonical templates at that commit. SHA syntax alone is never sufficient.
2. **Authority-locus enforcement.** Normal `ready` and `recover` may reinstate the manager only from `authority.manager_state_branch`. An optional expected ref may additionally pin the exact commit. Divergent/detached/exported snapshots require explicit non-authoritative maintenance/audit mode, which must state that it cannot instantiate or resume the Project Manager.
3. **Single mutable Core coordinate.** The mutable installed Core SHA lives only in `.context/capsule.json.core_commit`. Working views and long-lived beliefs reference that field rather than copying its value.
4. **Per-entry provenance.** Every decision-relevant manager belief and every substantive semantic/procedural memory entry must carry its own `source:` and `authority:` provenance before READY/recover.
5. **Git evidence availability.** Hosted CI uses full Git history so an older declared Core commit can be verified as a real Git object rather than trusted as metadata.

## Consequences

- A modified Manager Contract/Protocol with unchanged `core_commit` is rejected by authority-bearing VALID/READY/recover.
- A feature-branch or detached snapshot cannot silently fork the same `manager_id`; explicit non-authoritative mode is inspection-only.
- Legacy v2 memory may remain structurally VALID but is not READY until substantive durable entries satisfy per-entry provenance.
- Stable v1.3.1 and existing stable consumers are unaffected.
