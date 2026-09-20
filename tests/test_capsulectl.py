from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from installer.github_atomic import ConcurrentBranchUpdate, HeadState, MutationPlan, publish_single_commit
from installer.legacy import adopt_known_legacy_changes, detect_known_profile
from installer.model import CapsuleModelError, build_recovery_pack, clean_install_changes, readiness_snapshot, repair_changes, validate_snapshot
from installer.safety import CapsuleSafetyError, BEGIN_MARKER, END_MARKER, render_managed_block

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
CORE_SHA = "a" * 40


def apply(base, changes):
    result = dict(base)
    result.update(changes)
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

    def test_clean_install_refuses_existing_context(self):
        with self.assertRaises(CapsuleModelError):
            clean_install_changes({".context/anything": "x"}, TEMPLATES, "owner/repo", "main", CORE_SHA)

    def test_known_legacy_scope_is_closed(self):
        self.assertEqual(detect_known_profile("lvlaksim1/fgis-fsa-il"), "fgis-fsa-il")
        self.assertEqual(detect_known_profile("lvlaksim1/telegram-receiver"), "telegram-receiver")
        self.assertEqual(detect_known_profile("lvlaksim1/ai-agent-lab"), "ai-agent-lab")
        with self.assertRaises(CapsuleModelError):
            detect_known_profile("owner/random-old-repo")

    def test_fgis_legacy_profile_preserves_rich_paths(self):
        files = {
            "AI_CONTEXT.md": "legacy", "AGENTS.md": "legacy",
            ".context/ENTRYPOINT.md": "legacy entry", ".context/protocol.md": "legacy protocol",
            ".context/project/identity.md": "# Identity\n\nFGIS project repository responsibility and identity are known.\n",
            ".context/project/goals.md": "# Goals\n\nMaintain verified accreditation automation while preserving project rules.\n",
            ".context/project/architecture.md": "# Architecture\n\nTwo Excel VBA books use repository baselines and controlled release specifications.\n",
            ".context/project/constraints.md": "# Constraints\n\nPreserve mandatory VBA standards and confirmed workbook baselines.\n",
            ".context/current/state.md": "# State\n\nCurrent implementation is verified by simulation and controlled Excel testing.\n",
            ".context/current/blockers.md": "# Blockers\n\nNo active blocker exists in this fixture.\n",
            ".context/current/next.md": "# Next\n\nContinue the verified indicator-ID workflow from the accepted state.\n",
            ".context/rules/user-rules.md": "# Rules\n\nUse mandatory VBA methodology and preserve the confirmed XLSM baseline.\n",
            ".context/handoffs/latest.md": "# Handoff\n\nResume from the accepted verification stage and preserve both test layers.\n",
        }
        files[".context/manifest.json"] = json.dumps({
            "repository": "lvlaksim1/fgis-fsa-il", "default_branch": "main",
            "active_handoff": ".context/handoffs/latest.md",
            "authoritative": {
                "identity": ".context/project/identity.md", "goals": ".context/project/goals.md",
                "architecture": ".context/project/architecture.md", "constraints": ".context/project/constraints.md",
                "current_state": ".context/current/state.md", "blockers": ".context/current/blockers.md",
                "next": ".context/current/next.md", "user_rules": ".context/rules/user-rules.md"
            },
            "custom_legacy_field": {"keep": True}
        })
        adopted = apply(files, adopt_known_legacy_changes(
            files, TEMPLATES, "lvlaksim1/fgis-fsa-il", "main", CORE_SHA
        ))
        manifest = json.loads(adopted[".context/manifest.json"])
        self.assertTrue(manifest["custom_legacy_field"]["keep"])
        self.assertEqual(manifest["context_version"], "1.3.0")
        self.assertEqual(manifest["legacy_context_version"], "1.0")
        self.assertEqual(manifest["capsule_installer_version"], "1.3.0")
        self.assertEqual(manifest["installation_status"], "adopted-v1.3")
        self.assertIn(".context/rules/user-rules.md", manifest["rules"])
        self.assertIn(".context/history/legacy-entrypoint-before-v1.3.md", adopted)
        self.assertNotIn(".context/rules/project-rules.md", adopted)
        self.assertNotIn(".context/decisions/README.md", adopted)

    def test_telegram_legacy_profile(self):
        files = {
            "AI_CONTEXT.md": "legacy", "AGENTS.md": "legacy",
            ".context/ENTRYPOINT.md": "legacy entry", ".context/protocol.md": "legacy protocol",
            ".context/current/state.md": "# State\n\nDirect FIFO receiver is the accepted and verified architecture.\n",
            ".context/rules/project.md": "# Rules\n\nProcess updates sequentially and keep credentials out of the consumer.\n",
            ".context/handoffs/latest.md": "# Handoff\n\nReceiver is operational; next verify one immediate ordinary response.\n",
            ".context/decisions/direct-fifo.md": "# Decision\n\nUse direct FIFO getUpdates to consumer to sendMessage processing.\n",
        }
        files[".context/manifest.json"] = json.dumps({
            "repository": "lvlaksim1/telegram-receiver", "authoritative_branch": "main",
            "current_state": ".context/current/state.md", "latest_handoff": ".context/handoffs/latest.md",
            "protocol": ".context/protocol.md", "rules": [".context/rules/project.md"],
            "decisions": [".context/decisions/direct-fifo.md"]
        })
        overrides = {
            ".context/project/identity.md": "# Identity\n\nTelegram receiver provides ordered two-way bot message processing.\n",
            ".context/project/goals.md": "# Goals\n\nDeliver accepted Telegram updates promptly and in strict FIFO order.\n",
            ".context/project/architecture.md": "# Architecture\n\ngetUpdates flows through one receiver, isolated consumer, then sendMessage.\n",
            ".context/project/constraints.md": "# Constraints\n\nDo not restore per-message Actions or repository writes to the hot path.\n",
            ".context/current/blockers.md": "# Blockers\n\nDuplicate reply window remains a documented non-blocking limitation.\n",
            ".context/current/next.md": "# Next\n\nVerify one ordinary message receives an immediate correctly bound reply.\n",
        }
        adopted = apply(files, adopt_known_legacy_changes(
            files, TEMPLATES, "lvlaksim1/telegram-receiver", "main", CORE_SHA, semantic_overrides=overrides
        ))
        self.assertEqual(validate_snapshot(adopted), [])

    def test_ai_agent_legacy_profile_preserves_redirect_and_runtime(self):
        files = {
            "AI_CONTEXT.md": "legacy", "AGENTS.md": "legacy",
            ".context/ENTRYPOINT.md": "legacy entry", ".context/protocol.md": "legacy protocol",
            ".context/current/state.md": "# State\n\nWorkshop control plane and worker state machine are active.\n",
            ".context/rules/ai-rules.md": "# Rules\n\nKeep durable semantics separate from volatile runtime state.\n",
            ".context/handoffs/latest.md": "# Handoff\n\nContinue control-plane hardening from the accepted management decision.\n",
            ".agent/runtime.json": "{}",
            ".agent/management/interactive-bootstrap.md": "# Manager\\n\\nMaterialize persistent manager identity before management work.\\n"
        }
        files[".context/manifest.json"] = json.dumps({
            "repository": "lvlaksim1/ai-agent-lab", "default_branch": "main",
            "authoritative_context_branch": "work-webhook-test",
            "current_state": ".context/current/state.md", "active_handoff": ".context/handoffs/latest.md",
            "rules": [".context/rules/ai-rules.md"], "authoritative_files": {"live_runtime": ".agent/"}
        })
        overrides = {
            ".context/project/identity.md": "# Identity\n\nAI Agent Lab is the autonomous GitHub workshop and control-plane experiment.\n",
            ".context/project/goals.md": "# Goals\n\nProvide durable autonomous work with controlled handoff, stopping, commands, and reports.\n",
            ".context/project/architecture.md": "# Architecture\n\nDurable meaning lives in .context; queues, leases, and heartbeat live in .agent.\n",
            ".context/project/constraints.md": "# Constraints\n\nDo not weaken control-plane invariants or copy routine .agent churn into semantic context.\n",
            ".context/current/blockers.md": "# Blockers\n\nNo fixture blocker prevents recovery.\n",
            ".context/current/next.md": "# Next\n\nResume the latest control-plane hardening task from the verified handoff.\n",
        }
        adopted = apply(files, adopt_known_legacy_changes(
            files, TEMPLATES, "lvlaksim1/ai-agent-lab", "work-webhook-test", CORE_SHA,
            semantic_overrides=overrides
        ))
        manifest = json.loads(adopted[".context/manifest.json"])
        self.assertEqual(manifest["authoritative_branch"], "work-webhook-test")
        self.assertEqual(manifest["discovery_branch"], "main")
        self.assertEqual(manifest["branch_mode"], "redirect")
        self.assertEqual(manifest["context_version"], "1.3.0")
        self.assertEqual(manifest["legacy_context_version"], "1.0")
        self.assertEqual(manifest["installation_status"], "adopted-v1.3")
        self.assertIn(".agent/", manifest["runtime"]["authoritative_paths"])
        self.assertNotIn(".context/rules/project-rules.md", adopted)
        self.assertNotIn(".context/dialogues/README.md", adopted)
        self.assertIn(".context/history/legacy-AI_CONTEXT-before-v1.3.md", adopted)
        self.assertIn(".context/history/legacy-AGENTS-before-v1.3.md", adopted)
        self.assertIn("Начальник участка", adopted[".context/ENTRYPOINT.md"])
        self.assertIn(".agent/management/interactive-bootstrap.md", adopted[".context/ENTRYPOINT.md"])
        self.assertNotIn("Project Context Capsule v1.0", adopted["AI_CONTEXT.md"])
        with self.assertRaises(CapsuleModelError):
            adopt_known_legacy_changes(files, TEMPLATES, "lvlaksim1/ai-agent-lab", "main", CORE_SHA)

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
