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

    def test_converge_is_a_required_core_prerequisite_without_extension_hooks(self) -> None:
        manifest = self.read("extension.yml")
        template = self.read("config-template.yml")
        self.assertIn('version: "0.4.2"', manifest)
        self.assertIn('speckit_version: ">=0.11.2"', manifest)
        self.assertIn('"speckit.converge"', manifest)
        self.assertNotIn("\nhooks:\n", manifest)
        for text in (manifest, template):
            self.assertIn("converge:", text)
            self.assertIn("required: true", text)
            self.assertIn('accepted_outcome: "converged"', text)
            self.assertIn("require_current_source: true", text)
            self.assertIn("block_on_tasks_appended: true", text)

    def test_source_fingerprint_excludes_gate_reports_and_drops_head(self) -> None:
        verify = self.read("commands/verify.md")
        review = self.read("commands/review.md")
        ship = self.read("commands/ship.md")
        manifest = self.read("extension.yml")
        template = self.read("config-template.yml")

        # verify owns the canonical definition
        self.assertIn("## Source Fingerprint (Canonical)", verify)
        self.assertIn("reviewed-scope tree hash", verify)
        self.assertIn(":(exclude).specify/reports/verify-review-ship/**", verify)

        # HEAD must not define the fingerprint in any command
        for name, text in (("verify", verify), ("review", review), ("ship", ship)):
            self.assertNotIn(
                "HEAD + current diff hash + tasks.md hash",
                text,
                f"{name} still fingerprints on HEAD, which a committed gate report invalidates",
            )

        # review and ship defer to the canonical definition instead of restating it
        self.assertIn("Source Fingerprint (Canonical)", review)
        self.assertIn("gate reports excluded", ship)

        # the exclusion list is configurable and published identically in both files
        for text in (manifest, template):
            self.assertIn("fingerprint_exclude:", text)
            self.assertIn('- ".specify/reports/verify-review-ship/**"', text)
            self.assertIn('- "specs/**/verify.md"', text)
            self.assertIn('- "specs/**/review.md"', text)

    def test_verify_consumes_converge_handoff_without_repeating_completeness_analysis(self) -> None:
        verify = self.read("commands/verify.md")
        normalized = " ".join(verify.split()).lower()
        self.assertIn("## Converge Handoff (Required)", verify)
        self.assertIn("tasks_appended", verify)
        self.assertIn("source fingerprint", normalized)
        self.assertIn("must not reconstruct the intent inventory", normalized)
        self.assertIn("must not repeat spec-to-code completeness analysis", normalized)
        self.assertNotIn("## Spec-to-code traceability", verify)
        self.assertNotIn("every requirement and implementation task", normalized)

    def test_review_owns_technical_risk_without_reauditing_converge_or_constitution(self) -> None:
        review = self.read("commands/review.md")
        normalized = " ".join(review.split()).lower()
        self.assertIn("## Boundary with Official Converge", review)
        self.assertIn("runtime correctness", normalized)
        self.assertIn("must not repeat requirement, task, or plan completeness", normalized)
        self.assertIn("must not perform a constitution item-by-item audit", normalized)
        self.assertNotIn("every actionable constitution principle", normalized)
        self.assertNotIn("## Constitution Compliance", review)

    def test_ship_consumes_fresh_evidence_and_reconverges_after_governance_changes(self) -> None:
        ship = self.read("commands/ship.md")
        normalized = " ".join(ship.split()).lower()
        self.assertIn("## Phase A — Evidence Freshness", ship)
        self.assertIn("Converge: `CONVERGED`", ship)
        self.assertIn("must not run a new independent code reviewer", normalized)
        self.assertIn("must not run a new independent security auditor", normalized)
        self.assertIn("must not run a new independent test engineer", normalized)
        self.assertIn("`/speckit.analyze` then `/speckit.converge`", ship)
        self.assertIn("tasks_appended", normalized)

    def test_readme_documents_official_converge_loop_and_plugin_boundaries(self) -> None:
        readme = self.read("README.md")
        self.assertIn("implement ⇄ converge", readme)
        self.assertIn("## Responsibility Boundaries", readme)
        self.assertIn("`/speckit.converge`", readme)
        self.assertIn("0 hooks", readme)
        for target in ("constitution", "agent-context", "adr-docs", "backlog", "memory", "discard"):
            self.assertIn(f"`{target}`", readme)

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


if __name__ == "__main__":
    unittest.main()
