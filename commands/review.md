---
description: "Run a five-axis code review for the current Spec Kit feature or change"
---

# Review Gate

Adapted from Addy Osmani's `agent-skills` review workflow and integrated with Spec Kit artifacts.

## User Input

$ARGUMENTS

## Purpose

Conduct a structured code review across five axes:

1. **Correctness** — matches spec, handles edge/error cases, tests prove behavior.
2. **Readability** — names, control flow, organization, simplicity.
3. **Architecture** — follows project patterns, clean boundaries, justified abstractions.
4. **Security** — validates inputs, protects secrets, enforces auth/authz, avoids injection.
5. **Performance** — avoids N+1, unbounded work, sync hot paths, missing pagination, large bundles.

Use this after `/speckit.verify-review-ship.verify` or before `/speckit.verify-review-ship.ship`.

## Required Context Discovery

1. Identify the active Spec Kit feature using the same resolution approach as `/speckit.verify-review-ship.verify`.
2. Read `spec.md`, `plan.md`, `tasks.md`, and any existing `verify.md` report.
3. Inspect current diff, staged changes, or recent commits. If `$ARGUMENTS` names a PR, branch, commit, file, or feature directory, review that target.
4. Review tests first — tests reveal intended behavior and coverage.

## Review Procedure

### 1. Context

Answer briefly:

- What is this change trying to accomplish?
- Which Spec Kit requirements/tasks does it implement?
- What verification has already run?

### 2. Tests first

Check:

- Tests exist for changed behavior.
- Tests are behavior-focused, not implementation snapshots only.
- Happy path, edge cases, error paths, and regression cases are covered.
- Test names read like specifications.

### 3. Five-axis review

For each changed area, evaluate:

#### Correctness

- Does implementation match `spec.md` and `tasks.md`?
- Are edge cases covered: null, empty, boundaries, errors, concurrency?
- Are state transitions consistent?
- Are migrations/data changes safe?

#### Readability & Simplicity

- Clear names and straightforward control flow.
- No unnecessary abstractions or clever tricks.
- No dead code, no debug leftovers, no vague TODOs.
- File size and concept count remain reviewable.

#### Architecture

- Follows existing patterns unless a new one is justified.
- Dependencies flow in the right direction.
- Feature-specific logic stays in the owning layer.
- No near-duplicate helper when canonical helper exists.
- Refactor reduces complexity rather than relocating it.

#### Security

- Treat external data as untrusted.
- Validate at boundaries and encode outputs.
- No secrets in code, logs, fixtures, or committed env files.
- Auth/authz checked where needed.
- SQL/shell/path/HTML/template injection avoided.
- For AI/LLM features: model output is untrusted; prompts are not security boundaries; tool permissions are scoped.

#### Performance

- No N+1 or unbounded queries.
- Pagination/limits on list operations.
- No expensive sync work in hot paths.
- Caches and indexes considered where relevant.
- UI changes avoid unnecessary re-renders and obvious Core Web Vitals regressions.

### 4. Finding severity

Use these labels:

- **Critical** — blocks merge/ship: security vulnerability, data loss, broken core behavior.
- **Important** — should fix before merge/ship: missing tests, weak error handling, poor abstraction, relevant perf risk.
- **Suggestion** — optional improvement.
- **Nit** — minor style issue; optional.
- **FYI** — informational only.

Every Critical and Important finding must include a concrete fix recommendation.

### 5. Save report when possible

If file writes are allowed, save:

```text
.specify/reports/verify-review-ship/review.md
```

If active feature directory is clear, also prefer:

```text
<feature-dir>/review.md
```

## Output Format

```markdown
## Review Report

**Verdict:** APPROVE | REQUEST CHANGES
**Feature:** <feature id/path or unknown>
**Reviewed scope:** <diff/branch/commit/files>

### Overview
<1-2 sentences>

### Critical Issues
- [file:line] <issue> — Fix: <specific fix>

### Important Issues
- [file:line] <issue> — Fix: <specific fix>

### Suggestions
- [file:line] <suggestion>

### What's Done Well
- <specific positive observation>

### Five-Axis Checklist
| Axis | Status | Notes |
|---|---|---|
| Correctness | PASS/FAIL/RISK | ... |
| Readability | PASS/FAIL/RISK | ... |
| Architecture | PASS/FAIL/RISK | ... |
| Security | PASS/FAIL/RISK | ... |
| Performance | PASS/FAIL/RISK | ... |

### Test & Verification Review
- Tests reviewed: yes/no + observations
- Build verified: yes/no + source of evidence
- Verify report consumed: yes/no

### Final Recommendation
- If APPROVE: run `/speckit.verify-review-ship.ship` before production-bound release.
- If REQUEST CHANGES: fix Critical/Important issues, rerun verify and review.
```

## Decision Rules

- Do not approve with any Critical issue.
- Default to `REQUEST CHANGES` if tests are absent for meaningful behavior changes unless there is a documented reason.
- Avoid rubber-stamping. If evidence is missing, say what evidence is missing.
- Do not block on personal style preferences if the code improves the codebase and follows conventions.
