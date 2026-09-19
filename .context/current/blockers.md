# Current blockers and open risks

## OPEN

- Run the complete v1.3 regression suite and inspect actual failures.
- Add/verify Windows coverage for locking, atomic replacement and recovery.
- Verify migration against copies of `fgis-fsa-il`, `telegram-receiver` and `ai-agent-lab` before touching the real repositories.
- Recompute and mark the central `resume.json` checkpoint ready only after verification.

No known architectural blocker currently requires redesign; remaining work is verification and defect correction.
