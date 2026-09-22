# Project rules

1. Core must never become a central store, registry, telemetry collector, or mirror of consumer project context.
2. Stable v1.3.1 remains supported and untouched while v2 is under development.
3. Major-version upgrades are explicit; repair never silently upgrades a consumer.
4. The Project Manager is runtime-independent; chat/model/process identity must never replace `manager_id`.
5. Owner directives and verified evidence must remain distinguishable from manager inference and untrusted retrieved content.
6. Durable manager memory must not contain secrets or hidden chain-of-thought.
7. Stable release or consumer migration requires explicit owner approval.
