# DEC-0007 — Retire temporary legacy adoption

- Status: active
- Date: 2026-09-20

## DECISION

Remove the repository-specific legacy adoption layer from the permanent Context Capsule v1.3 product after completing the three known migrations.

The `adopt` CLI and `installer/legacy.py` are no longer part of Core. The migrated repositories retain their v1.3 capsules and provenance; the old migration implementation remains available in Git history if forensic reconstruction is ever needed.

Future unknown legacy layouts do not automatically expand the permanent compatibility surface. Any such case must be handled deliberately from the repository's actual context and evidence.

## Rationale

The legacy bridge existed only to cross a known transition boundary. Keeping it after the transition would add branches, tests, and project-specific assumptions to every future Core release without serving the normal clean-install/recovery product.
