# Current blockers and open risks

## OPEN

- Run the cleaned GitHub-only test suite and fix any failures introduced by removing the local-runtime layer.
- Verify the three production-derived legacy fixtures still migrate correctly.
- Verify central self-validation/self-audit on the development branch.
- Recompute the central continuation checkpoint after the cleanup is stable.
- The recovery-pack hard byte budget remains scheduled for a later change; it must not become an access barrier to needed history.

No desktop/Windows/Python-user compatibility work is required.
