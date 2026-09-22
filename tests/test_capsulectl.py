from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from installer.github_atomic import ConcurrentBranchUpdate, HeadState, MutationPlan, publish_single_commit
from installer.model import CapsuleModelError, VERSION, build_recovery_pack, clean_install_changes, discovery_redirect_changes, readiness_snapshot, repair_changes, validate_snapshot
from installer.safety import CapsuleSafetyError, BEGIN_MARKER, END_MARKER, render_managed_block

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


def semantic_overrides():
    return {
        ".context/project/identity.md": "# Identity\n\nThis repository is a durable Context Capsule recovery test project.\n",
        ".context/project/goals.md": "# Goals\n\nAllow a fresh chat with no prior history to resume the project safely.\n",
        ".context/project/architecture.md": "# Architecture\n\nProject semantics live in .context and lifecycle publication is one Git commit.\n",
        ".context/project/constraints.md": "# Constraints\n\nNever upload project context to Core or overwrite project-owned instructions.\n",
        ".context/current/state.md": "# State\n\nClean installation and deterministic recovery are implemented in this fixture.\n",
        ".context/current/blockers.md": "# Blockers\n\nThere are no active blockers in this fixture.\n",
        ".context/current/next.md": "# Next\n\nRun fresh-chat recovery and continue with the next verified integration stage.\n",
        ".context/rules/project-rules.md": "# Rules\n\nPreserve repository-local context and publish target changes as one non-forced Git commit.\n",
        ".context/handoffs/latest.md": "# Handoff\n\nThe fixture is verified; next consume the recovery pack without prior conversation history.\n",
        ".context/decisions/DEC-test.md": "# Decision\n\nKeep fresh-chat working state ahead of deeper durable decision history.\n",
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


class ContextCapsuleV13Tests(unittest.TestCase):
    def test_version_surfaces_stay_in_lockstep(self):
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), VERSION)
        registry = json.loads((ROOT / "migrations" / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["current"], VERSION)
        capsule = json.loads((ROOT / ".context" / "capsule.json").read_text(encoding="utf-8"))
        self.assertEqual(capsule["version"], VERSION)

    def test_atomic_publication_and_concurrent_abort(self):
        plan = MutationPlan("owner/repo", "main", "1" * 40, "install", {"AGENTS.md": "x"})
        ok = FakeBackend()
        self.assertEqual(publish_single_commit(ok, plan), "4" * 40)
        self.assertEqual(ok.moves, ["4" * 40])

        raced = FakeBackend()
        raced.move_after_tree = True
        with self.assertRaises(ConcurrentBranchUpdate):
            publish_single_commit(raced, plan)
        self.assertEqual(raced.moves, [])
        self.assertEqual(raced.head, "9" * 40)

    def test_managed_bootstrap_preserves_user_text(self):
        base = {"AGENTS.md": "# User instructions\n\nKeep deployment policy.\n"}
        final = apply(base, clean_install_changes(base, TEMPLATES, "owner/repo", "main", CORE_SHA))
        self.assertIn("Keep deployment policy.", final["AGENTS.md"])
        self.assertEqual(final["AGENTS.md"].count(BEGIN_MARKER), 1)
        self.assertEqual(final["AGENTS.md"].count(END_MARKER), 1)

        updated = render_managed_block(final["AGENTS.md"], "replacement", default_heading="# Agent Instructions")
        self.assertIn("Keep deployment policy.", updated)
        self.assertIn("replacement", updated)

    def test_malformed_managed_block_is_refused(self):
        with self.assertRaises(CapsuleSafetyError):
            clean_install_changes(
                {"AGENTS.md": f"# User\n\n{BEGIN_MARKER}\nbroken\n"},
                TEMPLATES, "owner/repo", "main", CORE_SHA,
            )

    def test_provenance_validate_ready_and_recovery(self):
        empty = apply({}, clean_install_changes({}, TEMPLATES, "owner/repo", "main", CORE_SHA))
        self.assertEqual(validate_snapshot(empty), [])
        meta = json.loads(empty[".context/capsule.json"])
        self.assertEqual(meta["core_commit"], CORE_SHA)
        self.assertFalse(readiness_snapshot(empty)[0])

        ready = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=semantic_overrides()
        ))
        self.assertTrue(readiness_snapshot(ready)[0])
        pack = build_recovery_pack(ready)
        self.assertIn("fresh chat with no prior history", pack)
        self.assertIn("Never upload project context", pack)
        self.assertIn("Run fresh-chat recovery", pack)
        self.assertLess(pack.index("## LATEST HANDOFF"), pack.index("## DURABLE DECISION"))
        self.assertLess(pack.index("## CURRENT STATE"), pack.index("## DURABLE DECISION"))

    def test_default_semantic_writeback_is_explicit(self):
        installed = apply({}, clean_install_changes({}, TEMPLATES, "owner/repo", "main", CORE_SHA))
        expected_rule = "Do not wait for the user to ask to save context, update the capsule, or for the chat to end."
        self.assertIn(expected_rule, installed[".context/ENTRYPOINT.md"])
        self.assertIn(expected_rule, installed[".context/protocol.md"])
        self.assertIn(expected_rule, installed["AGENTS.md"])

    def test_path_escape_is_rejected(self):
        final = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=semantic_overrides()
        ))
        manifest = json.loads(final[".context/manifest.json"])
        manifest["current"]["next"] = "../outside.md"
        final[".context/manifest.json"] = json.dumps(manifest)
        self.assertTrue(any("unsafe repository path" in x or "escapes repository" in x for x in validate_snapshot(final)))

    def test_repair_preserves_unknown_fields_and_nonstandard_index(self):
        final = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "main", CORE_SHA, semantic_overrides=semantic_overrides()
        ))
        final["docs/custom-decision.md"] = "# Decision\n\nKeep this externally indexed durable project decision.\n"
        manifest = json.loads(final[".context/manifest.json"])
        manifest["custom_extension"] = {"keep": True}
        manifest["runtime"]["custom_flag"] = "keep"
        manifest["decisions"].append("docs/custom-decision.md")
        final[".context/manifest.json"] = json.dumps(manifest)
        repaired = apply(final, repair_changes(
            final, TEMPLATES, repository="owner/repo", branch="main", core_commit=CORE_SHA
        ))
        result = json.loads(repaired[".context/manifest.json"])
        self.assertTrue(result["custom_extension"]["keep"])
        self.assertEqual(result["runtime"]["custom_flag"], "keep")
        self.assertIn("docs/custom-decision.md", result["decisions"])

    def test_clean_install_supports_permanent_redirect_topology(self):
        final = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "context", CORE_SHA,
            semantic_overrides=semantic_overrides(), discovery_branch="main"
        ))
        manifest = json.loads(final[".context/manifest.json"])
        self.assertEqual(manifest["authoritative_branch"], "context")
        self.assertEqual(manifest["discovery_branch"], "main")
        self.assertEqual(manifest["branch_mode"], "redirect")

    def test_discovery_redirect_is_not_a_stale_full_capsule(self):
        full = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "context", CORE_SHA,
            semantic_overrides=semantic_overrides(), discovery_branch="main"
        ))
        discovery = apply(full, discovery_redirect_changes(
            full, TEMPLATES, authoritative_branch="context", discovery_branch="main"
        ))
        self.assertNotIn(".context/manifest.json", discovery)
        self.assertNotIn(".context/capsule.json", discovery)
        self.assertIn("context", discovery[".context/ENTRYPOINT.md"])
        self.assertIn("discovery branch main", discovery["AI_CONTEXT.md"])
        self.assertIn("authoritative durable context is on context", discovery["AGENTS.md"])

    def test_repair_preserves_redirect_topology_and_requires_authoritative_branch(self):
        final = apply({}, clean_install_changes(
            {}, TEMPLATES, "owner/repo", "work", CORE_SHA,
            semantic_overrides=semantic_overrides(), discovery_branch="main"
        ))

        repaired = apply(final, repair_changes(
            final, TEMPLATES, repository="owner/repo", branch="work", core_commit=CORE_SHA
        ))
        result = json.loads(repaired[".context/manifest.json"])
        self.assertEqual(result["authoritative_branch"], "work")
        self.assertEqual(result["discovery_branch"], "main")
        self.assertEqual(result["branch_mode"], "redirect")

        with self.assertRaises(CapsuleModelError):
            repair_changes(
                final, TEMPLATES, repository="owner/repo", branch="main", core_commit=CORE_SHA
            )

    def test_clean_install_refuses_existing_context(self):
        with self.assertRaises(CapsuleModelError):
            clean_install_changes({".context/anything": "x"}, TEMPLATES, "owner/repo", "main", CORE_SHA)

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
