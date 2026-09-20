# Current blockers and open risks

## OPEN

The GitHub Actions service is currently not executing jobs for `work/core-v1.3`: both the initial run and a retry end with `runner_id=0` and `steps=[]`. The same behavior occurred when the branch contained the unchanged v1.2 baseline, so no test failure from our code has been observed in hosted CI.

Real migrations of `fgis-fsa-il`, `telegram-receiver`, and `ai-agent-lab` are intentionally outside items 1–9 and have not been performed.
