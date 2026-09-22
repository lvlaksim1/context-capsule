# Lifecycle

## Clean install

A clean install refuses an existing `.context/`, records exact Core provenance, installs the universal Project Manager Protocol, creates a stable manager identity, and seeds manager/memory surfaces. A fresh structural install is normally VALID but not READY until project-specific manager state is captured.

## Upgrade

Major-version migration is explicit. v2 `upgrade` currently accepts installed v1.3.x capsules, preserves project-owned semantic context and manifest extensions, adds manager/memory surfaces, and updates Core-managed bootstrap/protocol files. Upgrade may intentionally leave the capsule NOT READY until the new manager mandate/state is completed.

## Validate

`validate` checks structural coherence, repository confinement, manager identity, manager/memory indexes, and the runtime-checkpoint separation invariant.

## Ready

`ready` means the same Project Manager can be reinstantiated in a fresh runtime. It requires substantive project semantics, mandate, BDI active state, current project state, next work, and provenance-bearing beliefs. Handoff is not required for v2 readiness.

## Recover

`recover` emits a deterministic bounded Project Manager reinstantiation pack. Manager protocol/identity/mandate and active BDI state precede deeper memory and historical decisions.

## Repair

Repair is major-version preserving. It never silently upgrades a v1.3.x capsule into v2. It preserves project-owned manager state and safe manifest extensions while refreshing Core-managed surfaces.

## Permanent redirect topology

Authoritative context may live on a permanent branch with a discovery-only default branch. Runtime/feature branches are execution locations only.
