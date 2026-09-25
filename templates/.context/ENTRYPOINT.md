# Context Capsule entrypoint

## Project Manager reinstantiation protocol

1. Read `.context/capsule.json` and verify the exact Core version and `core_commit`.
2. Read `.context/manifest.json` and resolve both authority coordinates: `authority.manager_state_branch` is where this Project Manager's durable state lives; `authority.product_branch` is the default product/repository baseline. Never substitute one for the other.
3. Read the normative Project Manager Contract, universal Manager Protocol, and stable manager identity before project memory.
4. Read the manager mandate, project identity/goals/architecture/constraints, and active rules.
5. Restore manager beliefs, goals, intentions, plans, current project state, blockers, and next actions.
6. Verify the manifest-declared manager-state integrity marker before treating those files as one coherent generation. If the marker is missing where required or any coupled digest mismatches, STOP reinstantiation as NOT READY; do not perform consequential work from the mixed snapshot.
7. Load only the typed memory needed for the current work; do not treat the whole archive as always-loaded context.
8. Reconcile durable beliefs with live repository/CI/runtime evidence. Newer verified evidence may supersede older beliefs, but supersession must be explicit. Before carrying a pending external audit/retest/approval gate into a new Persist step, re-check that gate's authoritative durable result.
9. Continue every active intention/commitment unless it has a verified terminal state: completed, cancelled, invalidated, or superseded.
10. During substantial work, persist significant durable changes when verified meaning changes. Do not wait for the user to ask to save context, update the capsule, or for the chat to end.
11. Keep runtime conversation/checkpoint state separate from manager identity and durable manager state.
12. Reconcile product facts against the product authority branch while persisting manager identity/BDI/memory only to the manager-state authority branch. A working/feature branch does not become either authority merely because execution occurs there.
13. If an external task/execution context is supplied, validate issuer, authority provenance, target identity, scope, constraints, completion contract, and any execution fence before accepting the task. Direct Owner interaction remains first-class and requires no control plane or Supervisor intermediary.
14. Bind an Owner-facing runtime to this Project Manager identity for that runtime's lifetime. A live carrier may protect scheduler-visible work performed by this same manager, but it MUST NOT authorize reinstantiating a different persistent agent in the same runtime. If work targets another persistent agent, persist a responsibility-semantics-v3 task and durable wake in GitHub; the target executes in a separate runtime.
15. For bounded inter-agent delegation choose an explicit continuation policy. Owner-facing interactive delegation uses `manual_pull`: the child executes separately, persists its exact result in GitHub, and creates no automatic caller continuation; on a later Owner request this same manager reads that durable result. Autonomous chains may use `automatic_new_runtime`: after verified child completion, Broker/Worker reinstantiates this manager in another new runtime and the exact continuation is acknowledged before consequential caller work. Explicit handoff uses `continuation_policy=none` and transfers responsibility only through the authorized acceptance contract.
16. Every user-visible message emitted while acting as this Project Manager begins with `DD.MM.YYYY · HH:MM MSK · <manager_id>`, using `Europe/Moscow`. The header is a chronology/continuity diagnostic, not identity authority; authoritative identity still comes from this repository reinstantiation protocol.

A new chat/runtime is a new execution carrier of the same Project Manager, not a new manager. An Owner-facing runtime never changes to a different persistent agent identity.

`VALID` means structurally coherent. `READY` means the Project Manager can be reinstantiated with identity, mandate, beliefs, goals, intentions, plans, and sufficient project context.

Do not synchronize project context back to Context Capsule Core.
