# DEC-0006 — Clean installation and temporary legacy support

- Status: active
- Source: explicit user instructions in the current development conversation.

## Requirements

The permanent installation scenario is clean installation into a repository without a capsule. Existing project memory must never be overwritten by a clean install.

Legacy adoption, merging and version migration are TEMPORARY mechanisms. Keep them available and safe until the old capsules in `fgis-fsa-il`, `telegram-receiver`, and `ai-agent-lab` have actually been updated and verified. Do not remove these mechanisms now. Their later removal is a separate, evidence-gated change; do not invest in a general long-term migration framework.

The primary product outcome is reliable continuation in a fresh chat with no prior conversation. The target repository must supply goals, binding rules, accepted and rejected decisions, verified implementation state, blockers and the next concrete action. Significant semantic changes must be recorded during work, not only at an explicit handoff request.

All target context remains local to the target repository. No reverse synchronization, telemetry or central installation statistics.

## Work reporting

After every significant stage, give the user a concise report with completed changes, actual verification, saved commit and the next step. Keep a precise repository handoff so a different model can continue without redoing the investigation.

## Supersession

DEC-0004's legacy support is retained for the one-time transition, not as a permanent product capability. Earlier statements suggesting immediate deletion of migration mechanisms were incorrect and are superseded by this decision.
