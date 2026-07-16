---
description: "Run a five-axis and Constitution-aware code review for the current Spec Kit feature or change"
---

# Review Gate

Run after `/speckit.verify-review-ship.verify` or before `/speckit.verify-review-ship.ship`.

## User Input

$ARGUMENTS

## Purpose

Review the current change for Correctness, Readability, Architecture, Security, and Performance, then validate **every actionable item** in the active Spec Kit Constitution.

## Required Context Discovery

1. Resolve the active feature as specified by `/speckit.verify-review-ship.verify`.
2. Read `.specify/memory/constitution.md`, `spec.md`, `plan.md`, `tasks.md`, and any `verify.md` report.
3. Inspect the diff/staged changes/recent commits, or the explicit PR, branch, commit, file, or feature directory in `$ARGUMENTS`.
4. Review tests first.

If `.specify/memory/constitution.md` is missing, report `Constitution: BLOCKED`; do not claim full approval. If it has no actionable items, report that with evidence rather than inventing items.

## Pre-flight: review-agent discovery

Before fan-out, discover usable subagents/workers through the current host's documented capability or agent registry. Do not assume a provider-specific API, model, or role.

```text
Subagents: AVAILABLE | UNAVAILABLE | UNKNOWN
Discovery evidence: <capability / registry result / reason>
Parallel capacity: <number or unknown>
Execution mode: PARALLEL | SEQUENTIAL FALLBACK
```

- When available, create **one fresh, read-only reviewer per atomic review item**; dispatch independent items in bounded parallel batches. A batch never combines items: each item has one agent.
- When unavailable or unknown, the primary agent reviews the same items sequentially and marks `SEQUENTIAL FALLBACK`.
- Each reviewer receives only its item, scope, and relevant artifact excerpt. It returns exact `file:line`, test/gate, or artifact evidence, severity, and a concrete fix for Critical/Important findings. It must not edit, stage, commit, deploy, or issue the final verdict.
- The primary agent reconciles conflicts against source evidence and owns the verdict.

## Build the atomic review ledger

Before dispatch, enumerate and assign exactly one reviewer to each:

- test quality and coverage;
- every enabled review axis: Correctness, Readability, Architecture, Security, Performance;
- **every actionable Constitution principle, policy, and non-negotiable rule** parsed from `.specify/memory/constitution.md` — **one Constitution item equals one subagent**; never combine items;
- an explicitly requested PR, commit, file, or directory item not already covered.

Preserve item IDs in the report. Do not assign multiple axes or Constitution items to one reviewer.

## Review Procedure

### 1. Context and tests

State the change goal, implemented Spec Kit requirements/tasks, and verification already run. The test reviewer checks behavior-focused tests for changed behavior, happy/edge/error/regression paths, and specification-like names.

### 2. Five-axis review

Each dedicated reviewer evaluates only its axis:

- **Correctness:** spec/tasks match, boundaries/errors/concurrency, state transitions, safe migrations/data changes.
- **Readability:** names, control flow, simplicity, no dead/debug/vague TODO code.
- **Architecture:** existing patterns, dependency direction, ownership boundaries, canonical helpers, complexity reduction.
- **Security:** untrusted inputs, boundary validation/output encoding, secrets, auth/authz, injection; AI output is untrusted and tool permissions are scoped.
- **Performance:** N+1/unbounded work, pagination, hot-path sync work, caches/indexes, unnecessary UI renders.

### 3. Constitution compliance review

Parse the Constitution into individually identifiable actionable items. For **each item**, dispatch one dedicated reviewer. It returns only:

```text
Constitution item: <stable heading/id and exact text>
Status: PASS | FAIL | RISK | BLOCKED
Evidence: <file:line, test/gate output, or artifact reference>
Finding: <non-compliance or "none">
Fix: <required for FAIL/RISK>
Validator: <subagent id/name or primary fallback>
```

A non-negotiable-rule `FAIL` is at least `Important`; it is `Critical` for a security vulnerability, data-loss risk, or broken core behavior. Missing Constitution evidence is `BLOCKED`, not PASS.

### 4. Findings and report

Severity: `Critical` blocks merge/ship; `Important` should be fixed before merge/ship; `Suggestion`, `Nit`, and `FYI` are non-blocking. Every Critical/Important finding includes a concrete fix.

Keep all missing, failed, conflicting, skipped, and blocked items visible. If writes are allowed, save `.specify/reports/verify-review-ship/review.md` and `<feature-dir>/review.md` when clear.

```markdown
## Review Report

**Verdict:** APPROVE | REQUEST CHANGES | BLOCKED
**Feature:** <feature id/path or unknown>
**Reviewed scope:** <diff/branch/commit/files>

### Review Execution
- Subagents: AVAILABLE/UNAVAILABLE/UNKNOWN — <evidence>
- Execution mode: PARALLEL/SEQUENTIAL FALLBACK
- Parallel capacity: <number or unknown>
- Ledger: <total>; <passed> PASS, <failed> FAIL, <risks> RISK, <blocked> BLOCKED

### Critical Issues
- [file:line] <issue> — Fix: <specific fix>

### Important Issues
- [file:line] <issue> — Fix: <specific fix>

### Five-Axis Checklist
| Axis | Status | Notes | Validator |
|---|---|---|---|

### Constitution Compliance
| Constitution item | Status | Evidence | Finding / Fix | Validator |
|---|---|---|---|---|

### Test & Verification Review
- Tests reviewed: yes/no + observations + validator
- Build verified: yes/no + evidence
- Verify report consumed: yes/no

### Final Recommendation
- APPROVE: run `/speckit.verify-review-ship.ship`
- REQUEST CHANGES: fix Critical/Important issues, rerun verify and review
- BLOCKED: supply missing Constitution/context/evidence, then rerun review
```

## Decision Rules

- Never approve with a Critical issue, Constitution `FAIL`, or Constitution `BLOCKED` result.
- Default to `REQUEST CHANGES` when meaningful behavior changes lack tests without a documented reason.
- Use `BLOCKED` when Constitution, required context, or required evidence is unavailable.
- Do not rubber-stamp or block on personal style preferences.
