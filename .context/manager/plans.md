# Manager plans

## Operating mode now active

1. Reinstate `context-capsule-project-manager` from this repository and reconcile live GitHub before substantial work.
2. Receive ordinary Context Capsule development tasks directly from the Owner and execute them within mandate.
3. Maintain Project Manager v2 and Service Agent Base regression baselines.
4. Treat Supervisor as ecosystem coordinator, not replacement project manager.
5. Treat Auditor reports as independent evidence and keep remediation/retest separate.
6. Do not publish stable v2 or migrate consumers without explicit Owner authorization.

## Current focused milestone

The PTC-003 Core remediation is implemented.

Normative Project Manager and Service Agent Contracts, Protocols, ENTRYPOINTs, interoperability specifications, manifest invariants/validators, and regression tests now make the live carrier mandatory whenever interactive work has a control-plane or otherwise scheduler-visible projection. Direct Owner work with no scheduler-visible projection remains valid without creating control-plane state.

Canonical Core implementation snapshot:
`8fc2da36f0a77d0f2a16508a8f7ee97fe1baa754`

Binding commit:
`b1e5ef97235400f8f3f98aae109a687b2643be30`

Hosted verification:
GitHub Actions run `35928337273` on head `7d3c21770e439e7957185fda263d1636ec77e653` passed permanent tests, compile, self VALID, Project Manager READY, reinstantiation smoke, isolated consumer compatibility smoke, and Service Agent CLI smoke.

Remaining gate: focused independent PTC-001..PTC-003 retest.

## Prior audit continuity

CCPM-001..CCPM-004, CCPM-R001, ACP-CC-001, and EW-001..EW-003 remain CLOSED for their verified mechanisms.
