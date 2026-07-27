"""Behavioural tests for the canonical source fingerprint.

These execute scripts/source-fingerprint.sh against throwaway git repositories.
A prose assertion cannot catch a fingerprint that silently starts tracking HEAD
again, or one that ignores untracked files; running it can.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "source-fingerprint.sh"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SourceFingerprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        git(self.tmp, "init", "-b", "main")
        git(self.tmp, "config", "user.email", "t@example.com")
        git(self.tmp, "config", "user.name", "t")
        (self.tmp / "specs" / "001-feature").mkdir(parents=True)
        (self.tmp / ".specify" / "reports" / "verify-review-ship").mkdir(parents=True)
        (self.tmp / "specs" / "001-feature" / "tasks.md").write_text("- [X] T001\n")
        (self.tmp / "src.py").write_text("value = 1\n")
        git(self.tmp, "add", "-A")
        git(self.tmp, "commit", "-m", "init")

    def fingerprint(self, config: str | None = None) -> str:
        cmd = ["bash", str(SCRIPT), "specs/001-feature"]
        if config:
            cmd.append(config)
        out = subprocess.run(cmd, cwd=self.tmp, check=True,
                             capture_output=True, text=True).stdout
        return out

    def value(self, out: str, key: str) -> str:
        for line in out.splitlines():
            if line.startswith(key + " "):
                return line.split(" ", 1)[1]
        raise AssertionError(f"{key} missing from output:\n{out}")

    def test_committing_a_gate_report_does_not_change_the_fingerprint(self) -> None:
        before = self.fingerprint()
        (self.tmp / "specs" / "001-feature" / "verify.md").write_text("PASS\n")
        (self.tmp / ".specify" / "reports" / "verify-review-ship" / "verify.md").write_text("PASS\n")
        git(self.tmp, "add", "-A")
        git(self.tmp, "commit", "-m", "docs: verify report")
        after = self.fingerprint()
        self.assertEqual(self.value(before, "fingerprint"), self.value(after, "fingerprint"))

    def test_a_real_content_change_does_change_the_fingerprint(self) -> None:
        before = self.fingerprint()
        (self.tmp / "src.py").write_text("value = 2\n")
        git(self.tmp, "add", "-A")
        git(self.tmp, "commit", "-m", "feat: change")
        after = self.fingerprint()
        self.assertNotEqual(self.value(before, "tree"), self.value(after, "tree"))

    def test_untracked_files_are_part_of_the_fingerprint(self) -> None:
        before = self.fingerprint()
        (self.tmp / "new_module.py").write_text("def added(): ...\n")
        after = self.fingerprint()
        self.assertNotEqual(
            self.value(before, "work"), self.value(after, "work"),
            "an untracked implementation file must not be invisible to the fingerprint",
        )

    def test_tasks_md_is_pinned_separately(self) -> None:
        before = self.fingerprint()
        (self.tmp / "specs" / "001-feature" / "tasks.md").write_text("- [X] T001\n- [ ] T002\n")
        after = self.fingerprint()
        self.assertNotEqual(self.value(before, "plan"), self.value(after, "plan"))

    def test_non_executable_packaged_script_runs_via_bash(self) -> None:
        """Source archives may extract shell scripts without their executable mode bit."""
        packaged_script = self.tmp / "source-fingerprint.sh"
        shutil.copyfile(SCRIPT, packaged_script)
        packaged_script.chmod(0o644)

        result = subprocess.run(
            ["bash", str(packaged_script), "specs/001-feature"],
            cwd=self.tmp,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("fingerprint ", result.stdout)

    def test_configured_exclusions_are_honoured(self) -> None:
        cfg = self.tmp / "custom.yml"
        cfg.write_text(
            "converge:\n"
            "  fingerprint_exclude:\n"
            '    - "reports/**"\n'
        )
        # Commit the config first: leaving it untracked would move `work`, and
        # tracking it later would move `tree`, so the setup itself would explain
        # a difference this test attributes to the exclusion list.
        git(self.tmp, "add", "-A")
        git(self.tmp, "commit", "-m", "chore: custom fingerprint config")
        before = self.fingerprint("custom.yml")
        (self.tmp / "reports").mkdir()
        (self.tmp / "reports" / "gate.md").write_text("PASS\n")
        git(self.tmp, "add", "-A")
        git(self.tmp, "commit", "-m", "docs: custom report location")
        after = self.fingerprint("custom.yml")
        self.assertEqual(
            self.value(before, "fingerprint"), self.value(after, "fingerprint"),
            "the published fingerprint_exclude list must drive the algorithm",
        )

    def test_three_components_are_reported_separately(self) -> None:
        out = self.fingerprint()
        for key in ("tree", "work", "plan", "fingerprint"):
            self.assertIn(f"{key} ", out)


if __name__ == "__main__":
    unittest.main()
