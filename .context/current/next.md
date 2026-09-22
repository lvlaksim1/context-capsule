# Next actions

1. Review the verified v2 Project Manager architecture with the owner and collect any changes to the manager model before declaring the v2 design frozen.
2. Strengthen the v2 test matrix around memory poisoning/provenance, supersession of beliefs, commitment lifecycle, and bounded context recovery before stable promotion.
3. Keep v1.3.1 production and all existing consumers unchanged until the owner explicitly authorizes a v2 release and migration plan.
4. If stable promotion is approved, create a canonical immutable v2 Core commit, release/tag it, then migrate consumers explicitly rather than through `repair`.
