# Next actions

1. Finish the systemic `ACP-CC-001` remediation: reconcile all primary working views and enforce external-gate result re-check during Reconcile/Persist.
2. Run the full current hosted CI suite on the provenance-bound remediation snapshot.
3. Complete control-plane task `TASK-CC-ACP-REMEDIATION-001` with commit + CI evidence.
4. Let dependent task `TASK-CC-ACP-RETEST-001` invoke the independent Auditor for a focused read-only retest of `ACP-CC-001`.
5. If the retest closes `ACP-CC-001`, treat Master Plan item 19 as independently verified; otherwise remediate the new evidence separately.
6. Keep stable v1.3.1, `main`, stable-v2 promotion, and consumer migration unchanged until explicit Owner authorization.
