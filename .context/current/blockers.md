# Current blockers and open risks

## RELEASE BLOCKERS

None.

## Infrastructure note

GitHub-hosted Actions for this private repository currently terminate before runner assignment (`runner_id=0`, `steps=[]`). The exact implementation has therefore been independently verified byte-for-byte instead of treating the unavailable hosted runner as a product blocker.

The CI workflow remains enabled for stable `main` and pull requests so normal hosted verification resumes automatically when GitHub assigns runners again.
