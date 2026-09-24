# Manager plans

## Operating mode now active

1. Reinstate `context-capsule-project-manager` from this repository and reconcile live GitHub before substantial work.
2. Receive ordinary Context Capsule development tasks directly from the Owner and execute them within mandate.
3. Maintain Project Manager v2 and Service Agent Base regression baselines.
4. Treat Supervisor as ecosystem coordinator, not replacement project manager.
5. Treat Auditor reports as independent evidence and keep remediation/retest separate.
6. Do not publish stable v2 or migrate consumers without explicit Owner authorization.

## Current verified Core baseline

Current bound Core snapshot:
`ec465bd31a02fdc2602fa4d4808ac8a99ccda480`

Binding:
`9ad957063e16298e3117dd4f99015fbda7f12e3c`

Hosted Core CI:
`35947165325` — SUCCESS.

Verified semantics now include:

- persistent-agent taxonomy;
- task-scoped interactive-first execution;
- crash-safe bounded-delegation return;
- separation of responsibility, authority, and execution ownership;
- explicit handoff as proposed responsibility transfer until verified target acceptance;
- target-home immutable acceptance evidence bound to the exact current execution fence;
- normalized Owner root grant for delegable work;
- first-hop and nested delegation attenuation of allowed effects/scope with prohibitions/constraints preserved;
- historical completed-task compatibility boundary.

Independent acceptance:
- PTC-003 CLOSED / High confidence;
- LRC-001 CLOSED / High confidence;
- TAX-001 CLOSED / High confidence;
- DRA-001 CLOSED / High confidence;
- DRA-002 CLOSED / High confidence.

Executable ACP evidence:
- verified snapshot `5039c15fe7debd779132a06f17edf168bce2b2ea`;
- public exact-snapshot verifier run `35948730227` SUCCESS.

The private-repository hosted-runner quota is no longer part of the verification path for ACP; exact ACP verification is performed by the existing public `repo-factory` workflow without changing ACP runtime semantics.
