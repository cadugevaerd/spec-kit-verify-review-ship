---
description: "Verify implementation against Spec Kit artifacts and project gates"
---

# Verify Gate

Use after `/speckit.implement` or before `/speckit.verify-review-ship.ship` to produce evidence that the active feature is complete and executable.

## User Input

$ARGUMENTS

## Required Context Discovery

1. Resolve the Spec Kit project root (prefer `.specify/`) and active feature using `SPECIFY_FEATURE_DIRECTORY`, `.specify/feature.json`, `SPECIFY_FEATURE`, matching branch, then `$ARGUMENTS`.
2. Read available `spec.md`, `plan.md`, `tasks.md`, `checklists/*`, `quickstart.md`, `contracts/*`, `data-model.md`, `research.md`, and the extension config/local override.
3. If required artifacts are missing, stop with `VERIFY: BLOCKED` and list every missing path.

## Pre-flight: validation-agent discovery

Before validating, discover whether the current host exposes usable subagents/workers through its documented capability or agent registry. Do not assume a provider-specific API, model, or role.

Record:

```text
Subagents: AVAILABLE | UNAVAILABLE | UNKNOWN
Discovery evidence: <capability / registry result / reason>
Parallel capacity: <number or unknown>
Execution mode: PARALLEL | SEQUENTIAL FALLBACK
```

- When subagents are available, create **one fresh, read-only validation subagent per atomic ledger item**. Dispatch independent items in parallel up to the host capacity; use bounded batches until every item is checked. A batch never combines items: one item always has one agent.
- When unavailable or discovery is inconclusive, the primary agent validates the same ledger sequentially and marks `SEQUENTIAL FALLBACK`. This is not a PASS by default.
- A validator receives only its target paths, applicable artifact excerpt, and expected evidence. It must not edit, stage, commit, deploy, or issue the final verdict.
- The primary agent reconciles results and verifies contradictions against source evidence.

## Verification Procedure

### 1. Build the atomic validation ledger

Enumerate the ledger before dispatch. Include one item each for:

- every present required artifact (`spec.md`, `plan.md`, `tasks.md`, every checklist, and `quickstart.md` when present);
- worktree/diff integrity;
- every discovered project gate (`tests`, `build`, `lint`, `typecheck`, `format`, `security`, and applicable manual gates);
- every requirement and implementation-task traceability entry.

One validator checks exactly one ledger item; never assign it multiple artifacts, gates, requirements, or tasks.

### 2. Artifact, diff, and gate validation

Validate artifacts for task completion, requirement/code evidence, reflected plan decisions, exercised/justified quickstart scenarios, and resolved/accepted `[NEEDS CLARIFICATION]` markers.

For the dedicated diff item, report changed files, feature vs unrelated files, generated artifacts, and accidental secrets/environment-file changes. Never stage or commit.

Discover canonical project commands in this order: CI, task runner, manifests, docs, then framework defaults. Run safe local gates unless forbidden. Record each:

```text
Gate: tests | build | lint | typecheck | format | security | manual
Command: <exact command or "not found">
Result: PASS | FAIL | SKIPPED | BLOCKED
Evidence: <output summary, report path, or reason>
Validator: <subagent id/name or primary fallback>
```

A failed gate prevents `PASS`.

### 3. Spec-to-code traceability

Each requirement and implementation task receives one ledger item and one validator. Aggregate:

```markdown
| Requirement / Task | Evidence | Status | Validator |
|---|---|---|---|
| FR-001 ... | file/test/command | PASS/FAIL/GAP | <id/name> |
```

### 4. Report

Consolidate every result; never infer a pass from another item. If writes are allowed, save `.specify/reports/verify-review-ship/verify.md` and also `<feature-dir>/verify.md` when clear.

```markdown
## Verify Report

**Verdict:** PASS | FAIL | BLOCKED
**Feature:** <feature id/path or unknown>
**Scope:** <changed files / commits / target>

### Validation Execution
- Subagents: AVAILABLE/UNAVAILABLE/UNKNOWN — <evidence>
- Execution mode: PARALLEL/SEQUENTIAL FALLBACK
- Parallel capacity: <number or unknown>
- Ledger: <total>; <passed> PASS, <failed> FAIL, <blocked> BLOCKED, <skipped> SKIPPED

### Artifact Status
| Item | Status | Evidence | Validator |
|---|---|---|---|

### Gate Results
| Gate | Command | Result | Evidence | Validator |
|---|---|---|---|---|

### Traceability
| Requirement / Task | Evidence | Status | Validator |
|---|---|---|---|

### Gaps / Failures
- [Critical/Important] <gap and concrete fix>

### Next Action
- PASS: run `/speckit.verify-review-ship.review`
- FAIL/BLOCKED: fix listed gaps, then rerun verify
```

## Decision Rules

- `PASS` requires required artifacts, completed tasks, evidence for every required ledger item, and passing mandatory gates.
- `FAIL` means implementation/gates have defects; `BLOCKED` means required context, tools, or decisions are missing.
- Never claim a gate/item passed without exact evidence.
- Lack of subagents uses sequential fallback unless project config requires subagents.
