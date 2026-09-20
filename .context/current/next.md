# Next actions

1. Do not add new legacy compatibility cases to the permanent product.
2. When GitHub Actions assigns a runner normally, execute the exact v1.3 test suite plus compile, self-VALID, self-READY, and recovery smoke gates.
3. If those exact gates pass, review the final diff against released v1.2 and prepare promotion of v1.3 to `main`.
4. Only after a verified stable commit exists, create an immutable v1.3 release/tag and use that commit as the canonical installation source.
