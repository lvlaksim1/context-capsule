# Next actions

1. Execute PM-004 Origin-bound memory authority from `spec/v2-acceptance.md`.
2. Test four poisoning/laundering variants: direct untrusted text, manager summarization, trusted-tool echo, and manufactured/repeated corroboration.
3. Require authority non-amplification: derived memory must retain the lowest relevant originating authority unless an explicit authorized elevation event exists.
4. Then execute PM-005 explicit belief supersession and PM-006 unresolved conflict.
5. Keep v1.3.1 production and all existing consumers unchanged until the owner explicitly authorizes a v2 release and migration plan.
