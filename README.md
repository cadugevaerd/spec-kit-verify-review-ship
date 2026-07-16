# Verify Review Ship for Spec Kit

A Spec Kit extension with post-build quality gates:

- `/speckit.verify-review-ship.verify`
- `/speckit.verify-review-ship.review`
- `/speckit.verify-review-ship.ship`

It complements the normal Spec Kit flow:

```text
constitution → specify → clarify → plan → checklist → tasks → analyze → implement → verify → review → ship
```

## Parallel validation

`verify` and `review` first discover whether their current agent host exposes subagents/workers. If available, they use bounded parallel batches with **one fresh, read-only validator per atomic item**. If unavailable, they run the identical ledger sequentially and report `SEQUENTIAL FALLBACK`.

`verify` assigns a validator to every artifact, gate, and requirement/task traceability entry. `review` assigns validators to test quality, every enabled review axis, and every actionable item in `.specify/memory/constitution.md`; **one Constitution item equals one validator**.

Reports record discovery evidence, execution mode, capacity, validator identity, and evidence per item.

## Configuration

Copy `config-template.yml` to:

```text
.specify/extensions/verify-review-ship/verify-review-ship-config.yml
```

Use it to require subagents, tune parallel capacity, set explicit test/build/lint/typecheck commands, and configure review/Constitution validation.

## Installation

```bash
specify extension add --dev /path/to/spec-kit-verify-review-ship
specify extension list
```

## License

MIT. See `LICENSE`.
