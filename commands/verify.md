---
description: "Verify implementation against Spec Kit artifacts and project gates"
---

# Verify Gate

Use this after `/speckit.implement` or before `/speckit.verify-review-ship.ship` when you need evidence that the feature is complete and executable.

## User Input

$ARGUMENTS

## Purpose

Verify that the current implementation:

1. Satisfies the active Spec Kit feature artifacts.
2. Has a credible project-specific verification story.
3. Does not hide incomplete work behind passing superficial checks.
4. Produces a concise report that `/speckit.verify-review-ship.review` and `/speckit.verify-review-ship.ship` can consume.

## Required Context Discovery

1. Resolve the Spec Kit project root. Prefer the directory containing `.specify/`.
2. Resolve the active feature using, in order:
   - `SPECIFY_FEATURE_DIRECTORY`
   - `.specify/feature.json`
   - `SPECIFY_FEATURE`
   - current branch name if it matches a Spec Kit feature directory
   - explicit path/name from `$ARGUMENTS`
3. Read available feature artifacts:
   - `spec.md`
   - `plan.md`
   - `tasks.md`
   - `checklists/*`
   - `quickstart.md`
   - `contracts/*`
   - `data-model.md`
   - `research.md`
4. Read extension config if present:
   - `.specify/extensions/verify-review-ship/verify-review-ship-config.yml`
   - local override `.specify/extensions/verify-review-ship/verify-review-ship-config.local.yml`

If required Spec Kit artifacts are missing, stop with `VERIFY: BLOCKED` and list exactly what is missing.

## Verification Procedure

### 1. Artifact completeness

Check:

- `tasks.md` exists and has no unchecked implementation tasks unless explicitly out of scope.
- `spec.md` requirements have corresponding implementation evidence.
- `plan.md` technical decisions are reflected in the codebase.
- `quickstart.md` validation scenarios were exercised or have a stated reason not to run.
- Any `[NEEDS CLARIFICATION]` markers are resolved or explicitly accepted as risk.

### 2. Worktree and diff inspection

Inspect current changes/recent commits using the project’s available VCS tooling.

Report:

- changed files
- likely feature files vs unrelated files
- generated/build artifacts accidentally included
- secrets or environment files accidentally modified

Do not blindly stage or commit anything.

### 3. Project gate discovery

Discover canonical commands from the project, preferring this order:

1. CI workflow definitions
2. `Makefile` / `justfile` / task runner config
3. package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.)
4. README/contribution docs
5. obvious framework defaults only if no project command exists

Identify commands for:

- tests
- build/compile
- lint
- typecheck/static analysis
- formatting check
- security/dependency audit when available

### 4. Execute or request evidence

Run safe local gates when the agent has terminal/tool access and the user did not forbid execution.

For each gate, record:

```text
Gate: tests | build | lint | typecheck | security | manual
Command: <exact command or "not found">
Result: PASS | FAIL | SKIPPED | BLOCKED
Evidence: <short output summary, file/report path, or reason>
```

If a gate fails, do not continue to a GO result. Summarize failure and recommended next fix.

### 5. Spec-to-code traceability

Create a compact traceability table:

```markdown
| Requirement / Task | Evidence | Status |
|---|---|---|
| FR-001 ... | file/test/command | PASS/FAIL/GAP |
```

### 6. Save report when possible

If file writes are allowed, save a report at:

```text
.specify/reports/verify-review-ship/verify.md
```

If an active feature directory is clear, also prefer:

```text
<feature-dir>/verify.md
```

## Output Format

```markdown
## Verify Report

**Verdict:** PASS | FAIL | BLOCKED
**Feature:** <feature id/path or unknown>
**Scope:** <changed files / recent commits / user-specified target>

### Artifact Status
- Spec: PASS/FAIL/BLOCKED
- Plan: PASS/FAIL/BLOCKED
- Tasks: PASS/FAIL/BLOCKED
- Clarifications/checklists: PASS/FAIL/BLOCKED

### Gate Results
| Gate | Command | Result | Evidence |
|---|---|---|---|

### Traceability
| Requirement / Task | Evidence | Status |
|---|---|---|

### Gaps / Failures
- [Critical/Important] <specific gap and fix recommendation>

### Verification Story
- Tests run: <commands>
- Build run: <commands>
- Manual checks: <what was checked>
- Not run / skipped: <why>

### Next Action
- If PASS: run `/speckit.verify-review-ship.review`
- If FAIL/BLOCKED: fix listed gaps, then rerun verify
```

## Decision Rules

- `PASS` only when required artifacts exist, required tasks are complete, and all discovered mandatory gates pass.
- `FAIL` when artifacts exist but implementation/gates have defects.
- `BLOCKED` when required context, tools, or decisions are missing.
- Never claim a gate passed without exact evidence.
