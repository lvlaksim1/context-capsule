# DEC-0021 — Durable Finding Gate

Date: 2026-10-03
Status: ACCEPTED FOR V2 DEVELOPMENT
Authority: direct Owner instruction

## Problem
Project Manager v2 already required Reflect → Persist, semantic write-back, and typed durable-memory admission. The contract did not define a sufficiently operational trigger for when a verified lesson becomes mandatory durable state.

A consumer incident demonstrated the gap: a verified reusable publication fallback remained in runtime Mailbox/Trace until the Owner explicitly asked whether it had been preserved. A future Manager could therefore have repeated an already-solved problem despite the existing general persistence rule.

## Decision
Add a normative Durable Finding Gate to Project Manager v2.

After Verify/Reflect, a verified finding is mandatory durable state when it would materially change a reasonable future Manager's next action or prevent repetition of a problem already solved.

Mandatory candidate classes include reusable workarounds/alternate paths, corrected invariants/constraints/classifications, evidence interpretations that change next action, recurring incident resolutions, and durable corrections to beliefs/procedures.

Runtime checkpoints, mailbox/trace/log/chat state remain evidence only and do not satisfy durable admission. Findings are routed by semantics to decisions, procedural memory, beliefs/semantic memory, plans/current views, and/or episodic memory.

Checkpoints remain consolidation points, not the only persistence points. Mere confirmations and transient telemetry do not create write-back churn.

## Product scope
This decision changes v2 development only. Stable v1.3.1 main and existing consumers are unchanged until separately authorized promotion/migration.

## Verification
- Core source and installed templates carry the same Contract/Protocol/ENTRYPOINT invariant.
- generated manifests set `sync_policy.durable_finding_gate_required=true`;
- validation rejects a manifest that disables the invariant;
- deterministic tests assert installed normative surfaces contain the gate.
