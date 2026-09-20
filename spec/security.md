# Security and privacy

## Locality

Target-project context remains in the target repository. Core does not keep a central copy, registry or telemetry stream.

## GitHub-only execution

All Context Capsule executable logic remains in the central Core repository and runs inside GitHub automation.

Target repositories must not receive a Context Capsule executable runtime or bundled schema/tool copies. The user's computer is outside the product execution boundary.

## Repository path boundary

Context paths must remain inside the target repository. Absolute paths, parent traversal, `.git` traversal, symlink hops and special files are rejected by central service validation.

## Managed bootstrap boundary

Core may update only its explicit managed block inside shared bootstrap Markdown. Unknown surrounding project instructions are preserved and require review rather than silent replacement.

## Integrity

Managed integrity covers Core-owned bootstrap blocks. Project-owned semantic content is not reclassified as Core-owned merely because the manifest references it.

## Concurrency

The service verifies branch/HEAD before publication and relies on normal Git/GitHub atomic commit/reference update semantics to prevent stale overwrite.

## Secrets

Capsules and handoffs must not persist credentials, cookies, private keys, secret values or unnecessary sensitive personal data.
