# Canonical GitHub lifecycle protocol

## Clean v2 installation

1. Read the target authoritative branch HEAD and tree.
2. Read existing `AI_CONTEXT.md` / `AGENTS.md` if present and confirm there is no existing `.context/`.
3. Declare authority coordinates before capture: the manager-state authority branch owns durable manager state; the product authority branch is the default product baseline. They may be the same branch.
4. Capture project semantics plus the repository-specific Project Manager mandate and initial BDI state.
5. Build the complete desired snapshot in memory using the pinned Core commit SHA.
6. Run `VALID`; run `READY` only after the manager/project semantics are substantive.
8. Create one Git tree based on the original tree.
7. Create one commit whose parent is the original expected HEAD.
9. Re-read the branch HEAD. If it changed, stop without moving the branch.
10. Update the branch ref non-forced.

The only branch-visible mutation is the final ref update.

## Explicit v1.3.x → v2 upgrade

Major upgrade is never performed by `repair`.

1. Read the authoritative v1.3.x capsule and exact branch HEAD.
2. Preserve project-owned semantic files, project-specific manifest extensions, branch topology, and existing historical context.
3. Refresh Core-managed bootstrap/protocol files and add the v2 Manager Protocol, stable manager identity, manager-state surfaces, and typed-memory surfaces.
4. Upgrade manifest schema to v4 and record the exact v2 Core commit.
5. Validate the complete planned v2 snapshot before publication.
6. Publish through the same expected-parent, one-commit, non-forced branch update.
7. Expect the upgraded capsule to remain NOT READY until manager mandate/beliefs/goals/intentions/plans have been captured substantively with required provenance.

No known consumer repository is upgraded merely because v2 exists.

## Repair / Core refresh

For an installed v2 capsule, repair/refresh must:

- preserve project-owned project/manager/memory semantics and unknown safe manifest extensions;
- update only Core-managed bootstrap/protocol/metadata/index structure;
- preserve stable `manager_id`;
- preserve existing branch topology;
- use expected-parent atomic publication;
- refuse an installed different major version and direct the caller to explicit upgrade.

## Shared bootstrap files

Context Capsule owns only text between:

`<!-- context-capsule:begin -->`

and

`<!-- context-capsule:end -->`

Existing project instructions outside that block are preserved.

## Project Manager continuity boundary

The durable Project Manager includes repository-scoped identity, mandate, BDI-style active state, typed memory, rules, decisions, and verified project state.

Conversation history, pending tool calls, hidden reasoning, leases, heartbeats, and runtime checkpoints are not Project Manager identity. Runtime systems may persist checkpoints separately.

## Manager-state authority, product authority, and discovery

For repositories using disposable feature/runtime branches, keep one permanent manager-state authority branch. The product authority branch may be different, typically `main`. A discovery-only branch may point runtimes to the manager-state branch.

Publish and validate manager-state authority first, then publish any discovery redirect. Feature branches never become durable Project Manager authority or product authority merely because execution occurs there. The compatibility field `authoritative_branch` always aliases manager-state authority in v2.

## Legacy policy

The v1 legacy adoption bridge remains retired. v1.3.x is the only currently defined input for the explicit v2 major upgrade path.

## Service Agent clean installation

Service Agent is a separate v2 profile with its own identity/manifest schema.

1. Start from the agent's **home repository**, not from a target/client project repository.
2. Confirm the home repository does not already contain an unrelated `.context/` installation.
3. Choose a stable `agent_id`, role, specialization, and permanent agent-state branch.
4. Run `service-install` with the exact Core commit SHA.
5. Capture the profile-specific mandate, capabilities, limitations, principal model, durable professional BDI state, and explicit empty-or-active engagement state.
6. Run `service-validate`, then `service-ready`.
7. Run `service-recover` and verify that identity, authority boundaries, active engagements, and professional state survive reinstantiation.
8. Publish the complete installation atomically when operating through GitHub mutation tooling.

A Service Agent home repository is not a client project. Do not install the Service Agent profile into a project merely because the agent will service that project.

### Service Agent repair

`service-repair` refreshes Core-managed Service Agent files while preserving stable identity, professional state, active engagements, and profile-specific semantics. It refuses non-Service-Agent profiles.

Target repository access is never inferred from the Service Agent home repository or its installed tools.
