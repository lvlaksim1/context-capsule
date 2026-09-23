# Next actions

1. Run the full current CI suite on the CCPM-R001 remediation snapshot: tests, compile, Core-bound VALID, authoritative READY, recovery, isolated-consumer compatibility/safety smoke, and Service Agent smoke.
2. After successful verification, persist the exact final remediation ref and CI evidence without reintroducing stale lifecycle prose.
3. Provide that pinned snapshot to Supervisor/Owner for a separate focused Auditor retest of CCPM-R001 only.
4. During focused retest, provide evidence without changing Auditor methodology or reopening CCPM-001 through CCPM-004 unless new evidence objectively requires it.
5. Keep stable v1.3.1, `main`, stable-v2 promotion, and consumer migration unchanged until explicit Owner authorization.
