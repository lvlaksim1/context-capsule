# Manager intentions and commitments

## Completed

- Implement the first complete v2 Manager Runtime model on branch `v2-manager-runtime`.
- Resolve the ambiguity between product authority and Project Manager state authority.
- Establish explicit confirm/supersede/conflict evidence semantics.
- Establish automation-first verification and bounded recovery that cannot silently omit mandatory active manager state.
- Complete Master Plan item 1 by defining the normative Project Manager v2 Contract, closing the identified owner/commitment/memory/reconciliation/self-modification/expertise gaps, protecting deterministic clauses with permanent tests, and passing an isolated consumer compatibility smoke.

## Active commitments

- Keep stable `main` and all v1.3.1 consumers untouched until the owner explicitly approves v2 promotion or migration.
- Preserve exact Core provenance through the canonical `.context/capsule.json.core_commit` field. Do not duplicate mutable Core SHA values inside long-lived commitments.
- Treat stable v2 release and consumer migration as separate owner-authorized lifecycle operations.
- Preserve the Project Manager Contract and its self-modification/audit boundaries while preparing for the next owner-directed Master Plan stage.
