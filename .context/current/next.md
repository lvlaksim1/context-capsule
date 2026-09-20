# Next actions

1. Keep `main` as the released v1.2 baseline until v1.3 exact-commit verification can run normally.
2. Continue real legacy migration verification with the remaining known repositories, without broadening the adapter framework.
3. After all three known migrations are complete, remove or isolate temporary legacy compatibility before a stable v1.3 release.
4. Re-run unit tests plus central `validate`, `ready`, and `recover` gates when GitHub Actions assigns a runner normally.
