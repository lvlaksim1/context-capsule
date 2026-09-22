# Context Capsule Core

**Stable release: v1.3.1. Development line: v2 Project Manager on `v2-manager-runtime`.**

Context Capsule v1.3.1 is the stable repository-local durable project-memory product. v2 evolves the same foundation into a portable Project Manager that can be reinstantiated across replaceable chats, models, processes, or agent runtimes.

## v2 Project Manager model

The Project Manager is not the runtime. A runtime is a temporary carrier of one stable repository-scoped manager identity.

v2 adds:

- a universal Core-managed Project Manager Protocol;
- stable `manager_id` independent of chat/model/process identity;
- repository-local project-specific mandate and authority boundaries;
- separate authority coordinates for durable manager state and the product baseline;
- BDI-inspired active state: beliefs, goals, intentions/commitments, plans;
- provenance-bearing manager beliefs with explicit confirm / supersede / conflict evidence semantics;
- typed semantic, episodic, and procedural memory;
- explicit separation of runtime checkpoints from durable manager state;
- manager-aware `READY` and deterministic reinstantiation `recover`;
- explicit v1.3.x → v2 major upgrade; `repair` never silently performs that upgrade.

The universal manager loop is:

`Reinstate → Reconcile → Plan → Execute → Verify → Reflect → Persist`

During Reconcile, newer evidence is not automatically treated as a state change. Freshness alone does not imply supersession: evidence may confirm the existing state, supersede it, or remain in unresolved conflict.

## Preserved invariants

v2 keeps the strongest v1.3 properties:

- all consumer project context remains inside that consumer repository;
- no central registry, telemetry, or context collection;
- exact Core provenance through `core_commit`;
- repository-confined paths and managed bootstrap blocks;
- project-owned manifest extensions are preserved;
- canonical GitHub mutation remains expected-parent atomic publication;
- permanent manager-state authority branches and discovery redirects remain supported;
- versions are explicit and there is no silent auto-upgrade.

## CLI development surface

```bash
python installer/capsulectl.py install --target /repo --repository owner/name --branch main --product-branch main --core-commit <sha>
python installer/capsulectl.py install --target /repo-context --repository owner/name --branch context --discovery-branch main --product-branch main --core-commit <sha>
python installer/capsulectl.py upgrade --target /repo --repository owner/name --branch main --product-branch main --core-commit <sha>
python installer/capsulectl.py repair --target /repo --repository owner/name --branch main --core-commit <sha>
python installer/capsulectl.py validate --target .
python installer/capsulectl.py ready --target .
python installer/capsulectl.py recover --target .
```

In v2, `authoritative_branch` is a compatibility alias for `authority.manager_state_branch`; it does not mean product authority. `authority.product_branch` identifies the default product baseline independently.

Stable consumer repositories must remain on v1.3.1 until v2 is explicitly promoted and migration is explicitly requested.
