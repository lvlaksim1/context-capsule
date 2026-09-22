# DEC-0013 — Evidence revision semantics

Status: accepted
Date: 2026-09-22

## Context

The second cold-reinstantiation acceptance test found two different situations:

1. a genuinely stale mutable Core SHA embedded inside an active commitment;
2. a newer successful GitHub Actions run that confirmed the same semantic state as an earlier successful verification.

Treating every newer evidence identifier as superseding would create a self-sustaining verification loop: write state → CI verifies → record newer CI → new write → new CI.

Event-sourcing practice treats snapshots and materialized views as derived projections rather than independent truth. Newer events require a projection change only when they change the derived state. Provenance-aware agent-memory work likewise separates recency, provenance, validity, and belief revision.

## Decision

Every new evidence item must be classified relative to the existing proposition:

- **confirm** — supports the same semantic claim; newer evidence may strengthen provenance but does not require a state/view rewrite solely because it is newer;
- **supersede** — authoritative/adjudicated evidence changes the accepted value or truth; preserve the prior record as superseded and update affected active state;
- **conflict** — incompatible evidence cannot yet be adjudicated; preserve both sides explicitly.

Freshness alone never implies supersession. A newer timestamp, commit, CI run ID, or repeated successful verification is confirming evidence when the semantic state is unchanged.

Working views are stale only when their semantic projection becomes false or materially misleading. Evidence pointers do not have to track the numerically latest confirming event.

Mutable provenance values such as the current Core SHA belong in their canonical metadata field and must not be duplicated inside long-lived commitments.

## Consequences

The manifest sync policy requires `freshness_not_supersession: true`. The Manager Protocol and project protocol define confirm/supersede/conflict semantics. Tests enforce the invariant. Acceptance tests must distinguish real belief revision from newer confirming evidence.
