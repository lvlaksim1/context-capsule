# Latest handoff

## Completed

The temporary Context Capsule legacy migration layer has been fully retired after migrating the three known legacy repositories.

Permanent cleanup implementation commit: `f7b947b0974bc697cf61f553d7f48294413d39d5`.

Removed from the normal product:

- `installer/legacy.py`;
- `capsulectl adopt`;
- repository-specific legacy migration tests;
- temporary legacy profile registry entries;
- active documentation that presented legacy adoption as an available lifecycle operation.

Historical migration code remains recoverable from Git history only.

## Permanent v1.3 surface

- clean install;
- non-destructive repair;
- VALID;
- READY;
- bounded fresh-chat recover;
- managed bootstrap blocks;
- safe repository paths;
- exact Core SHA provenance;
- atomic GitHub branch publication.

## Verification boundary

Static repository inspection confirms no executable/import references to the removed legacy adapter remain and the permanent test suite contains eight focused tests.

GitHub Actions still fails before runner assignment (`runner_id=0`, `steps=[]`), so exact hosted execution of the cleanup commit remains pending.

## Next

Once Actions runs normally, execute the exact permanent suite and, if green, promote v1.3 to the stable branch and create immutable release provenance.
