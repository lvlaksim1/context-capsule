# Current state

## FACT

Released baseline remains Core v1.2.0 on `main` at `2965c17`. Development is isolated on `work/seamless-context-v1.3`; draft PR #1 remains unmerged.

The v1.3 branch has been corrected back to the intended product boundary: Context Capsule is GitHub-only. Target repositories contain context data and managed discovery text, not an executable runtime.

The earlier target-installed `.context/tools/**`, Windows compatibility work, OS locking/journaling and cross-platform desktop CI have been removed. Lifecycle logic remains central and runs against GitHub-hosted repository checkouts.

Still retained:
- schema v3;
- managed bootstrap blocks that preserve project text;
- valid-vs-ready semantics;
- semantic index;
- resume/checkpoint;
- path/branch/HEAD validation;
- temporary migration support for the three real legacy capsules.

Final verification of the cleaned GitHub-only branch is still pending.
