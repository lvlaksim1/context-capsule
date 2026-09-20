# Security and privacy

## Locality

Context Capsule Core is stateless with respect to installed projects.

Core MUST NOT:

- receive target-project context;
- maintain a central registry of installations;
- collect telemetry or usage statistics;
- copy target context into Core;
- require a network callback for normal installed-capsule operation.

The target repository's access controls govern its own context.

## Repository path boundary

Manifest and lifecycle paths must remain inside the target repository. Absolute paths, parent traversal, `.git` traversal, symlink hops and special files are rejected for capsule paths.

This boundary is enforced before lifecycle writes and by the installed runtime when it follows manifest/index references.

## Managed bootstrap boundary

Core may alter only its explicit managed block inside shared bootstrap Markdown. Unknown surrounding project instructions are preserved.

Known historical Core bootstrap can be recognized using canonical text hashes. Unknown bootstrap is never silently classified as Core-owned and must be explicitly reviewed before a ready checkpoint.

## Integrity

Core-managed installed runtime/schema text is SHA-256 registered in `capsule.json`. Text hashes canonicalize CRLF/CR to LF so the same semantic managed file verifies across Git checkout platforms.

Project-owned semantic files are not treated as Core-owned merely because they are referenced by the manifest.

## Transaction journal

Mutation preimages are stored only in the target repository's Git metadata for rollback/recovery. The journal is validated before recovery and is removed after a committed or successfully rolled-back transaction.

The repository-local lock coordinates Context Capsule writers. Arbitrary noncooperating external writers are handled by snapshot/file conflict detection where possible; the lock is not represented as global filesystem isolation.

## Secrets

Capsules and handoffs must not persist credentials, cookies, private keys, secret values or unnecessary sensitive personal data.
