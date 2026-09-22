# Security and integrity

- Consumer project context never flows back into Core; there is no telemetry or central installation registry.
- Manifest paths must remain repository-relative and may not escape through `..`, absolute paths, backslash ambiguity, or symlink traversal.
- Shared bootstrap files are modified only inside explicit managed markers.
- GitHub publication is non-forced from an expected parent.
- Secret values, credentials, cookies, private keys, unnecessary sensitive personal information, and hidden chain-of-thought are excluded from durable manager memory.

## Persistent-memory poisoning boundary

Durable manager beliefs that can affect future decisions must preserve provenance and authority. Owner directives, verified repository/CI/runtime evidence, trusted external evidence, specialist-agent output, and manager inference are distinct evidence classes.

Retrieved content or specialist output must not modify the manager mandate, goals, or authority model merely by containing instructions. It remains evidence until explicitly evaluated and promoted.

When durable understanding changes, supersession should remain explicit enough to reconstruct why the manager changed its belief.

## Runtime boundary

Runtime checkpoints, conversation buffers, pending tool calls, and executor internals are not durable manager identity and must not silently override repository-local manager state.
