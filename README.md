# Verify Review Ship for Spec Kit

A Spec Kit extension with post-build quality gates, learning capture, and transactional delivery:

- `/speckit.verify-review-ship.verify`
- `/speckit.verify-review-ship.review`
- `/speckit.verify-review-ship.ship`

It completes the normal Spec Kit flow:

```text
constitution → specify → clarify → plan → checklist → tasks → analyze → implement
→ verify → review → ship: learn → approve → revalidate → merge → cleanup → summary
```

## Parallel validation

`verify` and `review` first discover whether their current agent host exposes subagents/workers. If available, they use bounded parallel batches with **one fresh, read-only validator per atomic item**. If unavailable, they run the identical ledger sequentially and report `SEQUENTIAL FALLBACK`.

`verify` assigns a validator to every artifact, gate, and requirement/task traceability entry. `review` assigns validators to test quality, every enabled review axis, and every actionable item in `.specify/memory/constitution.md`; **one Constitution item equals one validator**.

Reports record discovery evidence, execution mode, capacity, validator identity, and evidence per item.

## Learning and policy gate

Before the merge transaction, `ship` extracts only **evidence-backed** learnings from current Spec Kit artifacts, `verify`/`review` findings, retries, decisions, and gate results. It removes transient or feature-only noise, checks duplicates, then creates a stable proposal ledger.

```text
GO (provisional)
  → collect evidence
  → classify + deduplicate
  → show exact diffs and destinations
  → AWAITING_LEARNING_APPROVAL
  → apply approved changes on work branch
  → revalidate the new HEAD
  → transactional merge
```

Each candidate has a stable ID and can be approved, rejected, or deferred individually. No candidate is written without explicit approval. If the current HEAD or proposal hash changes, approval is invalidated and the proposal is regenerated.

### Router

| Destination | Use for |
|---|---|
| `constitution` | Durable, project-wide, non-negotiable and testable governance. An amendment must use Constitution SemVer and dependent-artifact propagation. |
| `agent-context` | Repository/runtime operating instructions. Target paths come from the opt-in Spec Kit `agent-context` configuration when present; otherwise from the active integration. Managed blocks are never overwritten. |
| `adr-docs` | Architecture decisions, technical procedures, and durable project documentation. |
| `backlog` | Valid improvement or follow-up that is not part of this delivery. |
| `memory` | Stable, cross-project, non-normative context only. Generic Spec Kit has no memory API, so this is `propose-only` unless the host exposes a documented adapter. |
| `discard` | Noise, duplicates, transient observations, or feature-local details. It is reported but not persisted. |

The proposal accepts `--approve all`, `--approve LRN-001,LRN-003`, `--reject LRN-002`, and `--defer LRN-004`. Ambiguous or absent approval returns `AWAITING_LEARNING_APPROVAL` without mutating Git state.

Approved versioned changes receive a dedicated work-branch commit. They invalidate stale reports: Constitution changes require `analyze`; all relevant changes require `verify`, `review`, and affected integration gates before a final GO. If revalidation fails, no merge or cleanup occurs.

External memory is intentionally finalized **after** remote primary-ref verification unless the adapter supports rollback. This prevents non-versioned memory from claiming a delivery that failed to merge.

## Transactional ship

After learning approval and final `GO`, `ship` runs:

```text
isolated merge candidate → integration gates → non-force push to primary
→ remote ref verification → memory finalization → safe cleanup → delivery summary
```

The command discovers the remote primary branch, merges in an isolated temporary worktree, reruns configured gates, pushes the primary branch without force, verifies the remote commit, and only then removes the completed linked worktree and local/remote work branches. Remote work-branch deletion uses an exact expected-ref lease so a concurrently advanced branch is preserved. Dirty, diverged, detached, conflicting, stale-evidence, or concurrently changed states fail closed without deleting work.

Use `$ARGUMENTS` with `--dry-run` to preview the readiness, learning proposal, and exact Git operations through read-only checks. Dry-run does not persist a proposal, edit files, fetch, prune, merge, push, or update/delete refs.

> `ship` merges and cleans Git state; it does not deploy the application or infrastructure.

## Configuration

Copy `config-template.yml` to:

```text
.specify/extensions/verify-review-ship/verify-review-ship-config.yml
```

Use it to require subagents, tune parallel capacity, define test/build/lint/typecheck commands, configure review/Constitution validation, configure learning destinations, and select the remote, base branch, and merge strategy.

## Installation

```bash
specify extension add --dev /path/to/spec-kit-verify-review-ship
specify extension list
```

## License

MIT. See `LICENSE`.
