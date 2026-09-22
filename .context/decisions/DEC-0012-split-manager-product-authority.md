# DEC-0012 — Separate Project Manager state authority from product authority

Status: accepted
Date: 2026-09-22

## Context

The first real cold-reinstantiation test recovered the v2 Project Manager from branch `v2-manager-runtime`, but the inherited manifest still contained `authoritative_branch: main`. The runtime correctly recognized that `main` was the stable production line, while durable v2 manager state physically lived on the development branch. One coordinate was therefore representing two different concepts.

External agent practice reinforces the separation: persistent agent identity/state can outlive and move independently of a particular execution workspace, while logical agent identity must remain stable across rehydrated runtimes.

## Decision

Context Capsule v2 has two explicit authority coordinates:

- `authority.manager_state_branch` owns durable Project Manager identity, mandate, BDI state, typed memory, and working views.
- `authority.product_branch` is the default product/repository baseline against which live product facts are reconciled.

The legacy-compatible `authoritative_branch` field remains but is defined strictly as an alias for `authority.manager_state_branch`. `discovery_branch` remains only a bootstrap/discovery coordinate.

Execution on a feature or runtime branch never promotes that branch to either authority automatically.

For Context Capsule v2 development:

- manager-state authority: `v2-manager-runtime`;
- product authority: `main`.

## Consequences

Recovery reports both authority coordinates explicitly. Validation rejects a mismatch between `authoritative_branch` and `authority.manager_state_branch`. Install/upgrade can set product authority independently. Existing redirect topology remains valid: a permanent `context` manager-state branch may use `main` as both discovery and product baseline.
