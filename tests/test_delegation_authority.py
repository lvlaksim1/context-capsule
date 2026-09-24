from __future__ import annotations

import json
import unittest
from pathlib import Path

from installer.model import clean_install_changes
from installer.service_agent import service_clean_install_changes


ROOT = Path(__file__).resolve().parents[1]


class DelegationAuthoritySemanticsTests(unittest.TestCase):
    def test_normative_spec_separates_responsibility_authority_and_execution(self):
        text = (ROOT / "spec" / "delegation-responsibility-authority-v1.md").read_text(encoding="utf-8")
        for marker in (
            "responsibility ≠ authority ≠ execution ownership",
            "intersection",
            "proposed responsibility transfer",
            "explicitly accepts the handoff in its own durable state",
            "allowed_effects",
            "forbidden_effects",
            "It may never widen it",
            "Historical version-1 responsibility artifacts may remain readable",
        ):
            self.assertIn(marker, text)

    def test_hardened_task_schema_preserves_legacy_and_adds_v2(self):
        schema = json.loads((ROOT / "schemas" / "agent-task-envelope.schema.json").read_text(encoding="utf-8"))
        branches = schema["properties"]["responsibility"]["oneOf"]
        legacy = [b for b in branches if b.get("type") == "object" and "semantics_version" not in b.get("properties", {})]
        hardened = [b for b in branches if b.get("properties", {}).get("semantics_version", {}).get("const") == 2]
        self.assertEqual(len(legacy), 1)
        self.assertEqual(len(hardened), 1)
        required = set(hardened[0]["required"])
        self.assertTrue({
            "caller_agent_id",
            "commitment_owner_agent_id",
            "proposed_commitment_owner_agent_id",
            "transfer_requires_target_acceptance",
            "authority_chain",
        }.issubset(required))
        chain = hardened[0]["properties"]["authority_chain"]
        self.assertTrue({
            "root",
            "immediate_grantor_agent_id",
            "grant_reference",
            "delegation_depth",
            "allowed_effects",
            "forbidden_effects",
            "subdelegation",
        }.issubset(set(chain["required"])))

    def test_installed_contracts_carry_hardening_invariants(self):
        manager = clean_install_changes({}, ROOT / "templates", "owner/project", "main", "a" * 40)
        service = service_clean_install_changes(
            {}, ROOT / "service-agent-templates", "owner/service", "main", "b" * 40,
            "example-service-agent", "Service Agent", "Delegation semantics test"
        )
        for contract in (
            manager[".context/manager/CONTRACT.md"],
            service[".context/service-agent/CONTRACT.md"],
        ):
            self.assertIn("Responsibility / authority hardening", contract)
            self.assertIn("explicit handoff names the target only as the **proposed** next commitment owner", contract)
            self.assertIn("effective authority is the intersection", contract)
            self.assertIn("allowed effects form a subset", contract)
            self.assertIn("Historical completed tasks may retain the older responsibility shape", contract)

    def test_sync_policies_make_hardening_non_optional(self):
        manager = clean_install_changes({}, ROOT / "templates", "owner/project", "main", "a" * 40)
        service = service_clean_install_changes(
            {}, ROOT / "service-agent-templates", "owner/service", "main", "b" * 40,
            "example-service-agent", "Service Agent", "Delegation semantics test"
        )
        manager_policy = json.loads(manager[".context/manifest.json"])["sync_policy"]
        service_policy = json.loads(service[".context/manifest.json"])["sync_policy"]
        for key in (
            "responsibility_authority_orthogonal",
            "handoff_requires_target_acceptance",
            "delegated_authority_attenuation_required",
            "authority_root_provenance_required",
            "subdelegation_inherits_constraints",
        ):
            self.assertIs(manager_policy[key], True)
            self.assertIs(service_policy[key], True)


if __name__ == "__main__":
    unittest.main()
