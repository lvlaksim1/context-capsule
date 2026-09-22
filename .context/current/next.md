# Next actions

1. Operate Context Capsule Core v1.3.1 from the canonical release commit lineage.
2. Keep every installed capsule's `.context/capsule.json.core_commit` aligned to the exact Core commit whose managed files were applied.
3. Do not reuse an existing version number for behavior-changing Core commits; create a new patch/minor version first.
4. Do not reintroduce repository-specific legacy migration support into the permanent product.
