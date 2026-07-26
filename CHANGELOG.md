# Changelog

## 0.4.0 - 2026-07-26

### Added

- `ship` now has an evidence-backed learning and policy gate before the Git integration transaction.
- Candidates are deduplicated and routed to Constitution, agent context, ADR/docs, backlog, external memory, or discard.
- The user can approve all, approve/reject/defer individual stable IDs, and resume only when the recorded work HEAD and proposal hash still match.
- Approved versioned changes are committed on the work branch, then `analyze` (for Constitution changes), `verify`, `review`, and affected integration gates are rerun before merge.
- Ship reports now include learning evidence, proposals, approvals, applied changes, revalidation, and pending/unavailable persistence.

### Changed

- Context-file targeting follows the optional Spec Kit `agent-context` configuration when present; managed blocks are never overwritten.
- External memory defaults to `propose-only`; host writes require a documented adapter and are finalized after the remote primary ref is verified unless rollback is supported.

## 0.3.0 - 2026-07-24

### Changed

- `ship` now treats a successful GO decision as authorization to integrate the recorded work HEAD into the discovered primary branch.
- Integration runs in an isolated temporary worktree, reruns mandatory gates, pushes without force, and verifies the remote primary ref before cleanup.
- Completed linked worktrees and local/remote work branches are removed only after ancestry, cleanliness, and immutable-ref checks pass.
- Final output classifies the delivery (product, feature, bugfix, security, refactor, documentation, chore, or other) and summarizes business outcome, evidence, merge, and cleanup.
- Extension effect changed from `read-only` to `read-write`; `--dry-run` previews the transaction without mutation.

## 0.2.0 - 2026-07-16

### Added

- Subagent/worker pre-flight discovery with explicit sequential fallback for `verify` and `review`.
- Atomic validation ledgers: one fresh, read-only validator per artifact, gate, requirement/task traceability item, and review axis.
- Constitution compliance review: each actionable `.specify/memory/constitution.md` item receives one dedicated validator.
- Validator identity, execution mode, capacity, and evidence in reports.
- Orchestration configuration for discovery, required availability, and bounded parallelism.

## 0.1.0 - 2026-07-09

### Added

- Initial Spec Kit extension manifest, verify/review/ship commands, hook, and configuration template.
