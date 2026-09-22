# Latest handoff

## v2 Project Manager development state

Context Capsule v1.3.1 remains the stable production line on `main`. No existing consumer repository has been migrated to v2.

The v2 Project Manager development line lives on `v2-manager-runtime`.

Authority coordinates:

- manager-state authority: `v2-manager-runtime`;
- product authority: `main`;
- `authoritative_branch` is only a compatibility alias of manager-state authority;
- discovery is a separate bootstrap coordinate.

Evidence semantics remain explicit: `confirm`, `supersede`, `conflict`; freshness alone never implies supersession.

Verification is now automation-first. The permanent suite has 22 tests. Bounded recovery refuses to produce an incomplete manager when the configured budget cannot hold mandatory active state; secondary working views and deeper memory may be omitted and indexed.

Current development Core source: `585d29c2bf3fd371b9509fde48f0c62355540f72`.
Verification evidence: GitHub Actions run `35788332122` — success across permanent tests, compile, self VALID, Project Manager READY, and reinstantiation smoke.

An isolated consumer copy, `lvlaksim1/evrasia-hd-testbed`, exists for occasional black-box behavioral smoke checks only. Routine multi-chat manual acceptance is not the default workflow.

Do not publish stable v2 or migrate existing consumers without explicit owner approval.
