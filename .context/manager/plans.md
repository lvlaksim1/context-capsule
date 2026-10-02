# Manager plans

## Current verified baseline

Durable Finding Gate is implemented and verified on `v2-manager-runtime`.

Implementation: `e6dbfb6df38f270e298e210852bf243b895524e6`.
Self-provenance binding: `fbcb36757882a7d89af96335e3fb707830d8ac27`.
CI: `37072482225` SUCCESS.

The v2 Project Manager now:
- evaluates verified reusable findings after Verify/Reflect;
- requires prompt durable admission when the finding can change future action or prevent repetition of a solved problem;
- treats runtime checkpoint/mailbox/trace/log/chat state as evidence rather than durable memory;
- routes findings to decision/procedural/belief-plan/episodic surfaces by meaning;
- preserves checkpoint consolidation without making checkpoints the only persistence point;
- enforces `sync_policy.durable_finding_gate_required=true` through manifest generation and validation.

Stable `main` / v1.3.1 and existing consumers remain unchanged. Stable promotion requires separate Owner authorization and the applicable independent-audit gate.
