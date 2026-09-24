from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PersistentAgentTaxonomyTests(unittest.TestCase):
    def test_normative_taxonomy_defines_distinct_concepts(self):
        text = (ROOT / "spec" / "agent-taxonomy-v1.md").read_text(encoding="utf-8")
        for marker in (
            "Agent ≠ Runtime ≠ Skill ≠ Workflow",
            "An **Agent** is a persistent accountable actor",
            "A **Runtime** is a disposable execution carrier",
            "A **Skill** is a reusable bounded capability",
            "A **Workflow** is an explicit sequence, graph, or state machine",
            "tool capability ≠ authority",
            "Conversation history can be useful continuity evidence",
        ):
            self.assertIn(marker, text)

    def test_taxonomy_denies_implicit_authority_to_execution_layers(self):
        text = (ROOT / "spec" / "agent-taxonomy-v1.md").read_text(encoding="utf-8")
        for marker in (
            "Runtime ownership does not grant authority",
            "Skill availability does not grant authority",
            "Workflow routing does not grant authority",
            "Tool access does not grant authority",
            "Registry or Catalog presence does not grant authority",
        ):
            self.assertIn(marker, text)

    def test_project_manager_contract_carries_taxonomy_boundary(self):
        contract = (ROOT / "templates" / ".context" / "manager" / "CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("## 14. Agent / Runtime / Skill / Workflow boundary", contract)
        self.assertIn("The Project Manager is the persistent Agent", contract)
        self.assertIn("A Runtime is only a disposable execution carrier", contract)
        self.assertIn("A Skill cannot own the manager's commitment", contract)
        self.assertIn("A Workflow may coordinate execution", contract)
        self.assertIn("Conversation history is not authoritative proof", contract)

    def test_service_agent_contract_carries_taxonomy_boundary(self):
        contract = (ROOT / "service-agent-templates" / ".context" / "service-agent" / "CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("## Concept taxonomy boundary", contract)
        self.assertIn("The Service Agent is the persistent **Agent**", contract)
        self.assertIn("A Runtime is only a disposable execution carrier", contract)
        self.assertIn("A Skill has no independent mandate", contract)
        self.assertIn("A Workflow may coordinate execution", contract)
        self.assertIn("Conversation history is not authoritative proof", contract)

    def test_architecture_points_to_normative_taxonomy(self):
        architecture = (ROOT / "spec" / "architecture.md").read_text(encoding="utf-8")
        self.assertIn("spec/agent-taxonomy-v1.md", architecture)
        self.assertIn("Agent ≠ Runtime ≠ Skill ≠ Workflow", architecture)


if __name__ == "__main__":
    unittest.main()
