# Project rules

1. Context Capsule Core MUST NOT store, aggregate, mirror, index, receive, or collect project context from repositories into which it is installed.
2. No telemetry or central installation statistics.
3. Installed project context is fully repository-local.
4. Installed capsules continue to operate without access to Core.
5. Core is used only for install, validate, explicit upgrade, and repair.
6. Capsule versions are pinned in target repositories; no silent auto-upgrade.
7. Upgrade and repair MUST preserve project-owned context.
8. The canonical bootstrap source is the central repository; out-of-band ZIP files are not the normal installation mechanism.
9. The central repository may carry its own `.context/` because it is itself a project; that context describes only Context Capsule Core.
