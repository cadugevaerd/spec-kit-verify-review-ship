# Verify Review Ship for Spec Kit

A Spec Kit extension with post-build quality gates and transactional delivery:

- `/speckit.verify-review-ship.verify`
- `/speckit.verify-review-ship.review`
- `/speckit.verify-review-ship.ship`

It completes the normal Spec Kit flow:

```text
constitution → specify → clarify → plan → checklist → tasks → analyze → implement
→ verify → review → ship → merge → cleanup → delivery summary
```

## Parallel validation

`verify` and `review` first discover whether their current agent host exposes subagents/workers. If available, they use bounded parallel batches with **one fresh, read-only validator per atomic item**. If unavailable, they run the identical ledger sequentially and report `SEQUENTIAL FALLBACK`.

`verify` assigns a validator to every artifact, gate, and requirement/task traceability entry. `review` assigns validators to test quality, every enabled review axis, and every actionable item in `.specify/memory/constitution.md`; **one Constitution item equals one validator**.

Reports record discovery evidence, execution mode, capacity, validator identity, and evidence per item.

## Transactional ship

After a `GO` decision, `ship` now:

```text
isolated merge candidate → integration gates → non-force push to primary
→ remote ref verification → safe worktree/branch cleanup → delivery summary
```

The command discovers the remote primary branch, merges in an isolated temporary worktree, reruns configured gates, pushes the primary branch without force, verifies the remote commit, and only then removes the completed linked worktree and local/remote work branches. Remote work-branch deletion uses an exact expected-ref lease so a concurrently advanced branch is preserved. Dirty, diverged, detached, conflicting, stale-evidence, or concurrently changed states fail closed without deleting work.

Use `$ARGUMENTS` with `--dry-run` to preview the decision and exact Git operations through read-only local checks and `ls-remote` queries; dry-run does not fetch, prune, merge, push, or update/delete refs. A successful summary classifies the delivery as product, feature, bugfix, security, refactor, documentation, chore, or other.

> `ship` merges and cleans Git state; it does not deploy the application or infrastructure.

## Configuration

Copy `config-template.yml` to:

```text
.specify/extensions/verify-review-ship/verify-review-ship-config.yml
```

Use it to require subagents, tune parallel capacity, define test/build/lint/typecheck commands, configure review/Constitution validation, and select the remote, base branch, and merge strategy.

## Installation

```bash
specify extension add --dev /path/to/spec-kit-verify-review-ship
specify extension list
```

## License

MIT. See `LICENSE`.
