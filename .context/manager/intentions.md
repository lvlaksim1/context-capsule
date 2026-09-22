# Manager intentions and commitments

## Completed

- Resolve the ambiguity between product authority and Project Manager state authority discovered by the first cold-reinstantiation acceptance test.

- Implement the first complete v2 Manager Runtime model on branch `v2-manager-runtime`.
- Verify the model with local permanent tests and GitHub-hosted CI before claiming the implementation works.
- Persist the research-derived architecture and its rationale into the project's own Context Capsule.

## Active commitments

- Keep stable `main` and all v1.3.1 consumers untouched until the owner explicitly approves v2 promotion or migration.
- Preserve exact Core provenance through the canonical `.context/capsule.json.core_commit` field. Do not duplicate the mutable SHA inside long-lived commitments.
- Treat stable v2 release and consumer migration as separate owner-authorized lifecycle operations, not an automatic consequence of successful development CI.
