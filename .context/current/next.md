# Next actions

1. Provide exact remediation snapshots to the independent Auditor through GitHub durable handoff:
   - ACP: `event-wake-redesign@708a8ab6d4ac97c10d10021e47e7e845051a99bb`;
   - Context Capsule Core: `core_commit 8fc2da36f0a77d0f2a16508a8f7ee97fe1baa754`, verified by CI run `35928337273`.
2. While the Owner remains online, reinstate Auditor immediately in the current live runtime rather than waiting for a Scheduled Task.
3. Retest only PTC-001..PTC-003 and preserve already-closed findings absent new evidence.
4. Keep stable v1.3.1, `main`, stable-v2 promotion, and consumer migration unchanged.
