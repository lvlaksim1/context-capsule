# Current blockers and open risks

## OPEN

Hosted verification of the exact published branch commit is blocked externally: GitHub Actions runs on `work/core-v1.3` terminate with `runner_id=0`, empty runner name, and `steps=[]`. Retrying produced the same result. This behavior already occurred when the branch contained the unchanged v1.2 baseline, so it is not evidence of a v1.3 test failure.

A 17-test local development prototype passed, but its files are not byte-for-byte identical to the final published implementation. It is supporting evidence only, not a substitute for executing the exact branch commit.

Real migrations of `fgis-fsa-il`, `telegram-receiver`, and `ai-agent-lab` are intentionally outside items 1–9 and have not been performed.
