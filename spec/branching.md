# Branching

New installations are single-branch: the repository's primary working branch is both discovery and authority.

Lifecycle publication is based on an expected HEAD. The planned commit has that HEAD as its parent and the branch update is non-forced. If the branch advances concurrently, publication is rejected.

The old discovery/authority redirect is retained only for the temporary `ai-agent-lab` migration profile.
