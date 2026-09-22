from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from installer.github_atomic import ConcurrentBranchUpdate, HeadState, MutationPlan, publish_single_commit
from installer.model import (
    CapsuleModelError,
    VERSION,
    build_recovery_pack,
    clean_install_changes,
    discovery_redirect_changes,
    readiness_snapshot,
    repair_changes,
    upgrade_changes,
    validate_snapshot,
)
from installer.safety import BEGIN_MARKER, END_MARKER, CapsuleSafetyError, render_managed_block

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
CORE_SHA = "a" * 40


def apply(base, changes):
    result = dict(base)
    for path, content in changes.items():
        if content is None:
            result.pop(path, None)
        else:
            result[path] = content
    return result


def ready_overrides():
    return {
        ".context/project/identity.md": "# Identity\n\nThis repository is a durable Project Manager recovery test project.\n",
        ".context/project/goals.md": "# Goals\n\nAllow the same project manager to survive replacement of the chat runtime.\n",
        ".context/project/architecture.md": "# Architecture\n\nDurable manager state lives in .context while runtime checkpoints remain separate.\n",
        ".context/project/constraints.md": "# Constraints\n\nNever upload project context to Core and never equate runtime state with manager identity.\n",
        ".context/current/state.md": "# State\n\nThe manager model is implemented and deterministic recovery is under verification.\n",
        ".context/current/blockers.md": "# Blockers\n\nNo active blockers are currently verified for this fixture.\n",
        ".context/current/next.md": "# Next\n\nReinstantiate the manager in a fresh runtime and verify commitment continuity.\n",
        ".context/rules/project-rules.md": "# Rules\n\nPreserve manager identity and require evidence before claiming work complete.\n",
        ".context/manager/mandate.md": "# Mandate\n\nThe manager may implement and test non-destructive changes; owner approval is required for stable release.\n",
        ".context/manager/beliefs.md": "# Beliefs\n\n- The v2 manager model is active. source: repository tests; authority: verified-repository.\n",
        ".context/manager/goals.md": "# Manager goals\n\nMaintain continuous project responsibility across runtime replacement and preserve project invariants.\n",
        ".context/manager/intentions.md": "# Intentions\n\n- Verify fresh-runtime continuity before declaring the v2 manager implementation complete.\n",
        ".context/manager/plans.md": "# Plans\n\nRun structural tests, recovery tests, and then evaluate repository CI evidence before completion.\n",
        ".context/memory/semantic.md": "# Semantic memory\n\nRuntime identity is replaceable; durable manager identity is repository-local. source: architecture decision; authority: verified-repository.\n",
        ".context/memory/procedural.md": "# Procedural memory\n\nFor major upgrades, use explicit upgrade and verify VALID before attempting READY.\n",
        ".context/handoffs/latest.md": "# Handoff\n\nOptional emergency summary only; manager continuity does not depend on this file.\n",
        ".context/decisions/DEC-test.md": "# Decision\n\nKeep runtime checkpoints separate from durable Project Manager state.\n",
    }


class FakeBackend:
    def __init__(self):
        self.head = "1" * 40
        self.tree = "2" * 40
        self.moves = []
        self.move_after_tree = False
        self.parent = None

    def get_head(self, repository, branch):
        return HeadState(self.head, self.tree)

    def create_tree(self, repository, base_tree_sha, changes):
        if self.move_after_tree:
            self.head = "9" * 40
        return "3" * 40

    def create_commit(self, repository, message, tree_sha, parent_sha):
        self.parent = parent_sha
        return "4" * 40

    def update_ref_fast_forward(self, repository, branch, new_commit_sha):
        if self.head != self.parent:
            return False
        self.head = new_commit_sha
        self.moves.append(new_commit_sha)
        return True


class ContextCapsuleV2Tests(unittest.TestCase):
    def test_version_surfaces_stay_in_lockstep(self):
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), VERSION)
        registry = json.loads((ROOT / "migrations" / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["current"], VERSION)

    def test_atomic_publication_and_concurrent_abort(self):
        plan = MutationPlan("owner/repo", "main", "1" * 40, "install", {"AGENTS.md": "x"})
        ok = FakeBackend()
        self.assertEqual(publish_single_commit(ok, plan), "4" * 40)
        raced = FakeBackend()
        raced.move_after_tree = True
        with self.assertRaises(ConcurrentBranchUpdate):
            publish_single_commit(raced, plan)
        self.assertEqual(raced.moves, [])

    def test_clean_install_is_valid_but_not_ready_until_manager_is_captured(self):
        installed = apply({}, clean_install_changes({}, TEMPLATES, "owner/repo", "main", CORE_SHA))
        self.assertEqual(validate_snapshot(installed), [])
        ready, reasons = readiness_snapshot(installed)
        self.assertFalse(ready)
        self.assertTrue(any("manager.mandate" in x for x in reasons))
        identity = json.loads(installed[".context/manager/identity.json"])
        self.assertEqual(identity["manager_id"], "project-manager")
        self.assertEqual(identity["continuity"], "runtime-independent")
        manifest = json.loads(installed[".context/manifest.json"])
        self.assertEqual(manifest["authority"]["manager_state_branch"], "main")
        self.assertEqual(manifest["authority"]["product_branch"], "main")

    def test_manager_reinstantiation_pack_preserves_identity_and_commitment(self):
        installed = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=ready_overrides()
        ))
        self.assertTrue(readiness_snapshot(installed)[0])
        pack = build_recovery_pack(installed)
        self.assertIn("new runtime instance of the existing Project Manager", pack)
        self.assertIn("Manager ID: project-manager", pack)
        self.assertIn("Manager state authority branch: main", pack)
        self.assertIn("Product authority branch: main", pack)
        self.assertIn("Verify fresh-runtime continuity", pack)
        self.assertLess(pack.index("## MANAGER PROTOCOL"), pack.index("## WORKING VIEW — CURRENT STATE (NON-AUTHORITATIVE)"))
        self.assertLess(pack.index("## MANAGER INTENTIONS"), pack.index("## DURABLE DECISION"))

    def test_product_and_manager_state_authority_are_distinct(self):
        installed = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "v2-manager-runtime", CORE_SHA,
            semantic_overrides=ready_overrides(), product_branch="main"
        ))
        manifest = json.loads(installed[".context/manifest.json"])
        self.assertEqual(manifest["authoritative_branch"], "v2-manager-runtime")
        self.assertEqual(manifest["authority"]["manager_state_branch"], "v2-manager-runtime")
        self.assertEqual(manifest["authority"]["product_branch"], "main")
        pack = build_recovery_pack(installed)
        self.assertIn("Manager state authority branch: v2-manager-runtime", pack)
        self.assertIn("Product authority branch: main", pack)

        manifest["authority"]["manager_state_branch"] = "main"
        installed[".context/manifest.json"] = json.dumps(manifest)
        self.assertTrue(any(
            "authoritative_branch must alias authority.manager_state_branch" in error
            for error in validate_snapshot(installed)
        ))

    def test_handoff_is_not_required_for_v2_ready(self):
        overrides = ready_overrides()
        overrides[".context/handoffs/latest.md"] = "# Handoff\n"
        installed = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=overrides
        ))
        self.assertTrue(readiness_snapshot(installed)[0])

    def test_beliefs_require_provenance(self):
        overrides = ready_overrides()
        overrides[".context/manager/beliefs.md"] = "# Beliefs\n\nThe implementation is correct because the manager believes so.\n"
        installed = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=overrides
        ))
        ready, reasons = readiness_snapshot(installed)
        self.assertFalse(ready)
        self.assertTrue(any("source:" in x and "authority:" in x for x in reasons))

    def test_working_views_are_non_authoritative_and_recovery_marks_them(self):
        installed = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=ready_overrides()
        ))
        manifest = json.loads(installed[".context/manifest.json"])
        self.assertTrue(manifest["sync_policy"]["working_views_non_authoritative"])
        pack = build_recovery_pack(installed)
        self.assertIn("WORKING VIEW — CURRENT STATE (NON-AUTHORITATIVE)", pack)
        self.assertIn("If they conflict with manager BDI state or newer live evidence", pack)

        manifest["sync_policy"]["working_views_non_authoritative"] = False
        installed[".context/manifest.json"] = json.dumps(manifest)
        self.assertTrue(any(
            "working views must be non-authoritative" in error
            for error in validate_snapshot(installed)
        ))

    def test_runtime_checkpoint_is_explicitly_not_capsule_state(self):
        installed = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=ready_overrides()
        ))
        manifest = json.loads(installed[".context/manifest.json"])
        self.assertFalse(manifest["runtime"]["checkpoint_is_capsule_state"])
        installed[".context/runtime-checkpoint.json"] = '{"pending_tool":"x"}'
        pack = build_recovery_pack(installed)
        self.assertNotIn("pending_tool", pack)

    def test_managed_bootstrap_preserves_project_owned_text(self):
        base = {"AGENTS.md": "# User instructions\n\nKeep deployment policy.\n"}
        final = apply(base, clean_install_changes(base, TEMPLATES, "owner/repo", "main", CORE_SHA))
        self.assertIn("Keep deployment policy.", final["AGENTS.md"])
        self.assertEqual(final["AGENTS.md"].count(BEGIN_MARKER), 1)
        updated = render_managed_block(final["AGENTS.md"], "replacement", default_heading="# Agent Instructions")
        self.assertIn("Keep deployment policy.", updated)
        self.assertIn("replacement", updated)

    def test_malformed_managed_block_is_refused(self):
        with self.assertRaises(CapsuleSafetyError):
            clean_install_changes(
                {"AGENTS.md": f"# User\n\n{BEGIN_MARKER}\nbroken\n"},
                TEMPLATES, "owner/repo", "main", CORE_SHA,
            )

    def test_explicit_v13_upgrade_preserves_semantics_and_extensions(self):
        v13 = {
            "AI_CONTEXT.md": "# AI Context\n",
            "AGENTS.md": "# Agent Instructions\n",
            ".context/capsule.json": json.dumps({
                "schema": "context-capsule", "version": "1.3.1", "source": "lvlaksim1/context-capsule",
                "core_commit": "b" * 40, "installed_at": "2026-09-20", "repository": "owner/repo",
                "update_policy": "manual", "custom_meta": "keep"
            }),
            ".context/manifest.json": json.dumps({
                "schema": "context-capsule-manifest", "schema_version": 3, "repository": "owner/repo",
                "authoritative_branch": "main", "discovery_branch": "main", "branch_mode": "single",
                "entrypoint": ".context/ENTRYPOINT.md", "capsule_metadata": ".context/capsule.json",
                "protocol": ".context/protocol.md", "latest_handoff": ".context/handoffs/latest.md",
                "project": {"identity": ".context/project/identity.md", "goals": ".context/project/goals.md",
                            "architecture": ".context/project/architecture.md", "constraints": ".context/project/constraints.md"},
                "current": {"state": ".context/current/state.md", "blockers": ".context/current/blockers.md", "next": ".context/current/next.md"},
                "rules": [".context/rules/project-rules.md"], "decisions": [], "dialogues": [], "history": [],
                "runtime": {"authoritative_paths": [], "volatile": false if False else False},
                "sync_policy": {"semantic_only": True, "volatile_runtime_excluded": True, "atomic_git_publication": True},
                "custom_extension": {"keep": True}
            }),
            ".context/ENTRYPOINT.md": "old entrypoint",
            ".context/protocol.md": "old protocol",
            ".context/project/identity.md": "# Identity\n\nExisting project identity must survive major upgrade unchanged.\n",
            ".context/project/goals.md": "# Goals\n\nExisting project goal must survive major upgrade unchanged.\n",
            ".context/project/architecture.md": "# Architecture\n\nExisting project architecture must survive major upgrade unchanged.\n",
            ".context/project/constraints.md": "# Constraints\n\nExisting project constraints must survive major upgrade unchanged.\n",
            ".context/current/state.md": "# State\n\nExisting state survives explicit upgrade.\n",
            ".context/current/blockers.md": "# Blockers\n\nNo blocker.\n",
            ".context/current/next.md": "# Next\n\nCapture new v2 manager state.\n",
            ".context/rules/project-rules.md": "# Rules\n\nExisting durable project rule survives upgrade.\n",
            ".context/handoffs/latest.md": "# Handoff\n\nExisting handoff remains available.\n",
        }
        upgraded = apply(v13, upgrade_changes(
            v13, TEMPLATES, repository="owner/repo", branch="main", core_commit=CORE_SHA
        ))
        self.assertEqual(validate_snapshot(upgraded), [])
        self.assertIn("Existing project identity", upgraded[".context/project/identity.md"])
        meta = json.loads(upgraded[".context/capsule.json"])
        manifest = json.loads(upgraded[".context/manifest.json"])
        self.assertEqual(meta["version"], VERSION)
        self.assertEqual(meta["custom_meta"], "keep")
        self.assertTrue(manifest["custom_extension"]["keep"])
        self.assertEqual(manifest["schema_version"], 4)
        self.assertIn("manager", manifest)
        self.assertFalse(readiness_snapshot(upgraded)[0])

    def test_repair_refuses_major_upgrade_and_preserves_manager_id(self):
        v13 = {".context/capsule.json": json.dumps({"version": "1.3.1"}), ".context/manifest.json": "{}"}
        with self.assertRaises(CapsuleModelError):
            repair_changes(v13, TEMPLATES, repository="owner/repo", branch="main", core_commit=CORE_SHA)

        installed = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=ready_overrides()
        ))
        identity = json.loads(installed[".context/manager/identity.json"])
        identity["manager_id"] = "durable-manager-42"
        installed[".context/manager/identity.json"] = json.dumps(identity)
        repaired = apply(installed, repair_changes(
            installed, TEMPLATES, repository="owner/repo", branch="main", core_commit=CORE_SHA
        ))
        self.assertEqual(json.loads(repaired[".context/manager/identity.json"])["manager_id"], "durable-manager-42")

    def test_redirect_topology_remains_supported(self):
        full = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "context", CORE_SHA,
            semantic_overrides=ready_overrides(), discovery_branch="main"
        ))
        manifest = json.loads(full[".context/manifest.json"])
        self.assertEqual(manifest["branch_mode"], "redirect")
        self.assertEqual(manifest["authority"]["manager_state_branch"], "context")
        self.assertEqual(manifest["authority"]["product_branch"], "main")
        discovery = apply(full, discovery_redirect_changes(
            full, TEMPLATES, authoritative_branch="context", discovery_branch="main"
        ))
        self.assertNotIn(".context/manifest.json", discovery)
        self.assertIn("authoritative Project Manager branch", discovery["AI_CONTEXT.md"])

    def test_path_escape_is_rejected(self):
        final = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=ready_overrides()
        ))
        manifest = json.loads(final[".context/manifest.json"])
        manifest["manager"]["plans"] = "../outside.md"
        final[".context/manifest.json"] = json.dumps(manifest)
        self.assertTrue(any("unsafe repository path" in x or "escapes repository" in x for x in validate_snapshot(final)))

    def test_local_symlink_escape_is_rejected(self):
        from installer.capsulectl import load_snapshot
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            repo = Path(td)
            (repo / ".context").mkdir()
            external = Path(outside) / "secret.md"
            external.write_text("outside", encoding="utf-8")
            (repo / ".context" / "escape.md").symlink_to(external)
            with self.assertRaises(CapsuleSafetyError):
                load_snapshot(repo)


if __name__ == "__main__":
    unittest.main()
