from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExtensionContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_manifest_and_template_publish_the_same_learning_defaults(self) -> None:
        manifest = self.read("extension.yml")
        template = self.read("config-template.yml")
        for text in (manifest, template):
            self.assertIn("enabled: true", text)
            self.assertIn("require_human_approval: true", text)
            self.assertIn("deduplicate: true", text)
            self.assertIn("auto_commit_versioned_changes: true", text)
            self.assertIn("rerun_analyze_on_constitution_change: true", text)
            self.assertIn("rerun_verify_review: true", text)
            self.assertIn('mode: "propose-only"', text)
            self.assertIn("write_after_verified_merge: true", text)
            self.assertIn('adr_directory: "docs/adr"', text)
            self.assertIn('backlog_path: "BACKLOG.md"', text)
            self.assertIn('context_section_heading: "Project Learnings"', text)
        targets = '["constitution", "agent-context", "adr-docs", "backlog", "memory", "discard"]'
        self.assertIn(targets, manifest)
        self.assertIn(targets, template)

    def test_ship_has_explicit_approval_commit_and_revalidation_gate(self) -> None:
        ship = self.read("commands/ship.md")
        normalized = " ".join(ship.split()).lower()
        self.assertIn("AWAITING_LEARNING_APPROVAL", ship)
        self.assertIn("--approve all", ship)
        self.assertIn("--reject", ship)
        self.assertIn("--defer", ship)
        self.assertIn("proposal hash", normalized)
        self.assertIn("auto_commit_versioned_changes` must be `true`", ship)
        self.assertIn("docs(ship): capture approved project learnings", ship)
        self.assertIn("run `/speckit.analyze`", ship)
        self.assertIn("rerun `verify`, `review`", normalized)
        self.assertLess(ship.index("Phase B — Learning / Policy Gate"), ship.index("Phase C — Git Pre-flight"))

    def test_ship_blocks_unsafe_destinations_without_silent_fallback(self) -> None:
        ship = self.read("commands/ship.md")
        normalized = " ".join(ship.split()).lower()
        self.assertIn("candidate is blocked if it is missing", normalized)
        self.assertIn("never created silently", normalized)
        self.assertIn("no destination fallback is silent", normalized)
        self.assertIn("never overwrite managed markers", normalized)
        self.assertIn("candidate without evidence is `blocked`", normalized)

    def test_ship_keeps_dry_run_read_only_and_memory_non_transactional(self) -> None:
        ship = self.read("commands/ship.md")
        normalized = " ".join(ship.split()).lower()
        self.assertIn("dry-run never writes a proposal", normalized)
        self.assertIn("after remote primary-ref verification", normalized)
        self.assertIn("`host-write` requires a documented", normalized)
        self.assertIn("merged_with_post_merge_warnings", normalized)

    def test_readme_documents_every_router_destination(self) -> None:
        readme = self.read("README.md")
        for target in ("constitution", "agent-context", "adr-docs", "backlog", "memory", "discard"):
            self.assertIn(f"`{target}`", readme)


if __name__ == "__main__":
    unittest.main()
