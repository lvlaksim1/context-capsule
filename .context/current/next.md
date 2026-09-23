# Next actions

1. Complete control-plane task `TASK-CC-ACP-REMEDIATION-001` with the verified remediation commit and CI evidence.
2. Execute dependent `TASK-CC-ACP-RETEST-001` as a focused independent read-only Auditor retest of `ACP-CC-001`.
3. Verify the retest checks working-view consistency, the external-gate reconciliation invariant, the absence of a universal lifecycle keyword ontology, and preservation of item-19 interoperability safeguards.
4. If Auditor closes `ACP-CC-001`, treat Master Plan item 19 as independently verified; otherwise remediate only the new evidence.
5. Keep stable v1.3.1, `main`, stable-v2 promotion, and consumer migration unchanged until explicit Owner authorization.
