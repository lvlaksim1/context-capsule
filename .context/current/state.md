# Current state

## Production / development topology

- stable production: Context Capsule v1.3.1 on `main`;
- v2 development and durable manager state: `v2-manager-runtime`;
- canonical installed Core provenance is read only from `.context/capsule.json.core_commit`;
- no consumer migration or stable-v2 promotion is authorized.

## Task-scoped interactive-first baseline

PTC-003 is CLOSED / High confidence. The Core preserves task-scoped live-carrier execution, direct Owner invocation, and unrelated autonomous scheduler availability.

## Active pre-scaling Core work

Owner-directed live delegation return semantics are being added:

- bounded delegation preserves active commitment/responsibility/authority with the caller;
- live bounded delegation identifies that caller as return target;
- verified terminal child completion reinstantiates the caller immediately in the same live runtime and continues from the durable result without another Owner message;
- explicit handoff is a distinct authorized responsibility transfer and implies no automatic return;
- nested bounded delegations unwind one caller at a time;
- Supervisor is not a mandatory return hop.

Implementation is under verification and is not yet a closed Core baseline.
