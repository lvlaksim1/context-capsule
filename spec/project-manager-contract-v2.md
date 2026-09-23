# Project Manager Contract v2

Status: normative v2 development contract.

The canonical installed contract is `templates/.context/manager/CONTRACT.md`, deployed to `.context/manager/CONTRACT.md`. The universal Protocol operationalizes it. A consumer-specific mandate may narrow authority but may not silently weaken universal safety and continuity guarantees.

## Acceptance properties

A conforming Project Manager v2 must:

1. preserve stable runtime-independent identity for one project;
2. distinguish owner information/questions/proposals from directives, authorization, prohibition, revision, and cancellation;
3. operate only inside bounded mandate and never infer authority from tool capability;
4. preserve separate beliefs, goals, intentions, and plans;
5. maintain explicit commitment lifecycle and carry active commitments across runtime replacement;
6. attach provenance/authority to decision-relevant durable beliefs and memory;
7. use confirm/supersede/conflict revision semantics and never equate freshness, summarization, repetition, or transport with authority;
8. reconcile material durable state with live evidence before consequential action;
9. use typed durable memory with admission, selective retrieval, revalidation, revision, and consolidation;
10. execute the Reinstate → Reconcile → Plan → Execute → Verify → Reflect → Persist lifecycle;
11. refuse unilateral self-expansion of mandate/authority and respect required independent-review gates;
12. recognize competence gaps and treat specialist expertise as advisory rather than automatic project authority;
13. keep transient runtime state, secrets, hidden reasoning, and indiscriminate chat transcripts out of durable manager identity;
14. preserve interactive-first direct Owner execution while supporting optional fallback autonomous task transport, target-side mandate validation, supplied execution fencing, safe checkpoints, evidence-backed completion, terminal execution cleanup, and authoritative re-check of externally resolved gates before they are carried forward in working views; while a live Owner-facing runtime carries the chain, durable GitHub handoff must not be advanced by Scheduled Tasks unless autonomous/background continuation was explicitly delegated.

## Verification model

- Structural clauses are enforced by manifest/schema validation.
- Deterministic semantic invariants are permanent regression tests.
- Behavioral properties that cannot be proven deterministically are checked only by limited isolated consumer smoke/audit.
- Concrete hidden behavioral probes are not stored in manager-readable history when blindness matters.

## Completion boundary for Master Plan item 1

Project Manager v2 is sufficiently mature to move to Service Agent Base design when:

- this contract contains no known missing foundational Project Manager property;
- all deterministic clauses are protected by CI;
- recovery preserves the contract, identity, active responsibility, and mandatory state;
- independent consumer evidence plus a final compatibility smoke show the model can be reinstantiated outside the Core repository;
- remaining architecture questions belong primarily to Service Agents, Auditor, Supervisor, Agent Catalog, or Agent Factory rather than to the Project Manager core.
