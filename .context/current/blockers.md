# Current blockers and open risks

## OPEN

- GitHub Actions verification is currently blocked at runner/job startup: recent runs end as `failure` with zero reported steps, no downloadable job log and no diagnostic artifact. This is not evidence that the test suite itself failed; code-level CI verification must resume when GitHub actually starts the job.
- After Actions execution resumes, run the cleaned GitHub-only suite and fix any real test failures.
- Verify the three production-derived legacy fixtures still migrate correctly.
- Recompute the central continuation checkpoint after verification.
- The recovery-pack hard byte budget remains scheduled for a later change; it must not become an access barrier to needed history.

No desktop/Windows/Python-user compatibility work is required.
