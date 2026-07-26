---
description: "Capture approved project learnings, revalidate the final HEAD, merge safely, clean up, and summarize delivery"
---

# Ship, Learn, Merge, Cleanup, and Delivery Summary

Run after `/speckit.verify-review-ship.verify` and `/speckit.verify-review-ship.review`.

## User Input

$ARGUMENTS

## Purpose

Complete delivery with one terminal status:

```text
AWAITING_LEARNING_APPROVAL | MERGED | MERGED_WITH_CLEANUP_WARNINGS |
MERGED_WITH_POST_MERGE_WARNINGS | NO-GO | BLOCKED | DRY-RUN READY
```

A passing readiness decision is only a **provisional GO**. Before any Git integration,
this command harvests evidence-backed project learnings, proposes their destinations,
and requires explicit approval. Only after approved changes are applied and the final
HEAD is revalidated does the command merge the work branch.

`--dry-run` produces the readiness, learning proposal, and exact Git operations without
persisting a proposal, editing files, fetching, pruning, merging, pushing, or changing
refs. Optional arguments may set `--base BRANCH` or `--remote REMOTE`.

Approval arguments are explicit and mutually composable:

```text
--approve all
--approve LRN-001,LRN-003
--reject LRN-002
--defer LRN-004
--proposal <proposal-hash>
```

Natural-language approval is acceptable only when it unambiguously identifies the same
candidate IDs. Ambiguity, no approval, a timeout, or an invalid proposal hash returns
`AWAITING_LEARNING_APPROVAL`; it never implies approval.

## Expected Inputs

Consume current Spec Kit artifacts; verify and review reports with ledgers/findings/retries;
Git branch/worktree/remotes; project gates, rollback and monitoring evidence; extension
configuration; and installed `agent-context` configuration. Missing required verify/review
evidence is `BLOCKED`. Never invent results.

## Phase A — Provisional Readiness Decision

Run independent Code Reviewer, Security Auditor, and Test Engineer perspectives in
parallel when subagents are available; otherwise use isolated sequential passes. Validate
requirements/tasks coverage, gates, unresolved review/security findings, and applicable
performance, accessibility, infrastructure, migrations, documentation, monitoring, and
rollback evidence. Record an immutable `source_head` only after provisional GO.

A Critical issue, High security issue, Constitution failure/block, missing rollback plan,
or missing production-bound verification evidence returns `NO-GO` or `BLOCKED`. Neither
status may merge, push, delete a branch, or remove a worktree.

## Phase B — Learning / Policy Gate

This controlled, mutable step happens **before** Git pre-flight and merge.

### B1. Evidence-backed learning ledger

Extract candidates only from `source_head` and concrete verify/review failures, risks,
blockers, accepted fixes, retries, integration gates, rollback/monitoring observations,
analysis decisions, user corrections, and resolved artifact inconsistencies.

Each deterministic `LRN-###` candidate includes: reusable learning; report ledger ID,
file:line, command/result, or approved user decision; scope/confidence; duplicate check;
destination; operation; exact bounded diff; and revalidation risk. Discard feature-local,
transient, subjective, secret-bearing, personally identifying, or unsupported statements.
A candidate without evidence is `BLOCKED` and cannot be applied.

### B2. Deduplicate and route

1. Remove noise, one-off details, and represented candidates.
2. Prefer `AMEND` to an equivalent Constitution principle; create a new principle only for
   recurring, project-wide, non-negotiable, testable governance.
3. Route repository/framework/runtime instructions to `agent-context`.
4. Route architecture decisions, runbooks, and technical knowledge to `adr-docs`.
5. Route valid undelivered improvement to `backlog`.
6. Route only durable, cross-project, non-normative context to `memory`.
7. Use `discard` for remaining noise/duplicates; report but never persist it.

Never duplicate a rule between Constitution, agent context, and memory.

### B3. Validate destinations

- **Constitution:** `.specify/memory/constitution.md` must exist; a candidate is blocked
  if it is missing. Apply official Constitution semantics: SemVer (`MAJOR` incompatible
  redefinition/removal; `MINOR` new/material principle; `PATCH` clarification),
  `LAST_AMENDED_DATE`, Sync Impact Report, and propagation to templates, commands, and
  guidance.
- **Agent context:** read
  `.specify/extensions/agent-context/agent-context-config.yml` first; `context_files`
  precedes `context_file`. Otherwise map `claude` to `CLAUDE.md`, and `codex`, `hermes`,
  or generic to `AGENTS.md`. Present alternatives when ambiguous. Respect managed markers;
  never overwrite managed markers or unrelated content. An absent file is proposed as
  `CREATE`, never created silently.
- **ADR/docs:** validate configured project-relative `adr_directory`; proposal includes
  the exact file path.
- **Backlog:** validate configured project-relative `backlog_path`; absence is a proposed
  `CREATE`, never a fallback.
- **Memory:** generic Spec Kit has no memory API. `disabled` suppresses it; `propose-only`
  records pending work; `host-write` requires a documented, idempotent adapter and real
  success evidence. Never claim a write that did not occur.

No destination fallback is silent; report unavailable targets and a safe resume action.

### B4. Proposal and approval

For a non-dry run persist the proposal outside the worktree at:

```text
$(git rev-parse --git-common-dir)/verify-review-ship/learning/<source_head>.json
```

Store source head, proposal hash, candidate table, exact patches, decisions, and times.
Dry-run never writes a proposal. Output a table with ID, learning, evidence, destination,
operation, risk, and approval. Stop at `AWAITING_LEARNING_APPROVAL` unless valid approvals
match the proposal hash.

### B5. Apply approved candidates

Require current work HEAD to equal `source_head` and re-check proposal hash. Any change
invalidates approval and regenerates the proposal. Apply only approved versioned changes;
rejected/deferred/blocked/discard candidates never modify the tree. Confirm no unapproved
hunk or path changed. Constitution uses required propagation; context stays outside managed
markers; ADR/docs and backlog use approved project-relative paths only.

`ship.learning_gate.auto_commit_versioned_changes` must be `true`; false or missing is
`BLOCKED`. Create a dedicated work-branch commit:
`docs(ship): capture approved project learnings`. A dirty pre-existing worktree, failed
commit, or unexpected changed path is `BLOCKED`; never stash, discard, or commit user work.

### B6. Revalidate final HEAD

Versioned changes produce immutable `learning_head`; previous reports are stale. If
Constitution changed, run `/speckit.analyze` and validate every actionable Constitution
item. Rerun `verify`, `review`, all affected integration gates, and all configured gates by
default. Require final GO evidence tied to `learning_head`; failed revalidation is `NO-GO`,
missing capability/evidence is `BLOCKED`, and neither permits merge or cleanup.

## Phase C — Git Pre-flight

Discover root/common directory, worktree type/path, work branch/final HEAD, remote/base,
remote refs, strategy, and commands. Require a named clean worktree, no Git operation in
progress, a distinct work/primary branch, and `no-ff` or `ff-only`. Resolve remote/base from
arguments/configuration then symbolic remote HEAD; never guess `main`.

For real runs fetch/prune, reject behind/diverged upstream, record remote work-branch HEAD
for cleanup leasing, require clean cleanup targets, and prove verify/review match final HEAD.
Never stash, `reset --hard`, `git clean`, `branch -D`, force-remove worktrees, or force-push
primary.

## Phase D — Isolated Integration Transaction

Create a detached integration worktree from fetched primary HEAD. Merge final work HEAD
using `--no-ff --no-edit` or configured `--ff-only`; conflicts or failed integrated gates
preserve work and return `BLOCKED`/`NO-GO`. Record `base_before` and `integrated_head`,
require both ancestors, push exactly integrated HEAD without force, and read remote primary
back for exact equality. Concurrent primary change is `BLOCKED`; never force retry.

## Phase E — Memory Finalization and Cleanup

Memory is outside the Git transaction. With default `write_after_verified_merge: true`,
finalize approved memory only **after remote primary-ref verification**. Record adapter and
result. `propose-only`/unavailable memory remains pending. A required post-merge memory
failure returns `MERGED_WITH_POST_MERGE_WARNINGS`; merge remains successful. Pre-merge
memory requires idempotency plus rollback/compensation.

After remote verification, remove temporary integration worktree/ref, then clean only safe
linked worktrees and branches using non-force ancestry, cleanliness, and exact-ref lease
rules. Cleanup failure never rolls back merge and returns `MERGED_WITH_CLEANUP_WARNINGS`
unless there is an earlier post-merge warning.

## Phase F — Report

Classify delivery as `PRODUCT | FEATURE | BUGFIX | SECURITY | REFACTOR | DOCUMENTATION |
CHORE | OTHER`.

```markdown
## Ship Result: <terminal status>

### Learning / Policy Changes
- Source HEAD and proposal hash
- Evidence consumed
- Approved / rejected / deferred / blocked IDs
| ID | Evidence | Destination | Approval | Applied | Revalidation |
|---|---|---|---|---|---|

### Applied Changes
- Versioned learning commit and diff integrity
- Final work HEAD
- Analyze / Verify / Review / integration results

### Pending / Unavailable
- Item, reason, and safe resume action

### Delivered / Quality Evidence / Merge / Cleanup / Delivery Summary
- Type, outcome, scope, rollback, refs, cleanup evidence, and residual action
```

For `AWAITING_LEARNING_APPROVAL`, `NO-GO`, or `BLOCKED`, include the safe resume point.
For a verified merge warning, lead with merged status and list only residual actions.
