# Security and integrity

- Target project context never flows back into Core.
- No telemetry or central installation registry.
- Manifest paths interpreted by Core must be relative repository paths and may not escape through `..`, absolute paths, backslash ambiguity, or local symlink traversal.
- Shared bootstrap files are modified only inside explicit managed markers.
- GitHub publication is non-forced from an expected parent.
- Secret values, credentials, cookies, private keys, and unnecessary sensitive personal information are excluded from durable context.
