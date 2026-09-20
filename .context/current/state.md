# Current state

## FACT — Current semantic state

Released baseline remains Core v1.2.0 on `main` at `2965c17e5545e641ed7c0b4038a44885e3726a05`.

v1.3 hardening is being implemented independently on `work/core-v1.3` from that exact baseline. No commits or code from the external-model checkpoint are being used.

The v1.3 scope is fixed by DEC-0006: atomic GitHub publication, safe path handling, preservation of project-owned context, managed bootstrap blocks, exact Core provenance, VALID vs READY, fresh-chat recovery, focused negative tests, and temporary adapters for the three known legacy repositories.
