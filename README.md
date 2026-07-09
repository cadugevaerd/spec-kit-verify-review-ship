# Verify Review Ship for Spec Kit

A Spec Kit extension that adds post-build quality gates inspired by [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills):

- `/speckit.verify-review-ship.verify`
- `/speckit.verify-review-ship.review`
- `/speckit.verify-review-ship.ship`

## Upstream Project

This extension is built for the original [GitHub Spec Kit](https://github.com/github/spec-kit) project and its official extension system. It is not a fork or replacement for Spec Kit; it adds final quality gates to the existing Spec-Driven Development workflow.

It integrates those gates with the Spec Kit artifact flow:

```text
/speckit.constitution
→ /speckit.specify
→ /speckit.clarify
→ /speckit.plan
→ /speckit.checklist
→ /speckit.tasks
→ /speckit.analyze
→ /speckit.implement
→ /speckit.verify-review-ship.verify
→ /speckit.verify-review-ship.review
→ /speckit.verify-review-ship.ship
```

## Commands

### `/speckit.verify-review-ship.verify`

Verifies implementation completeness against the active Spec Kit feature artifacts and project gates.

Checks include:

- artifact completeness: `spec.md`, `plan.md`, `tasks.md`, checklists, quickstart
- task completion and traceability
- current diff/recent commits
- project test/build/lint/typecheck discovery
- gate results with exact evidence

### `/speckit.verify-review-ship.review`

Runs a five-axis review adapted from `agent-skills`:

1. Correctness
2. Readability
3. Architecture
4. Security
5. Performance

Outputs Critical, Important, Suggestion, Nit, and FYI findings.

### `/speckit.verify-review-ship.ship`

Aggregates verification and review evidence into a production readiness decision:

```text
GO | NO-GO
```

It includes:

- blocker list
- recommended fixes
- acknowledged risks
- launch checklist
- rollback plan
- specialist summaries for code review, security, and test coverage

This command does **not** deploy. It produces a decision and launch evidence.

## Installation

### Local development

From any initialized Spec Kit project:

```bash
specify extension add --dev /path/to/spec-kit-verify-review-ship
specify extension list
```

### From release archive

```bash
specify extension add verify-review-ship \
  --from https://github.com/cadugevaerd/spec-kit-verify-review-ship/archive/refs/tags/v0.1.0.zip
```

## Hooks

This extension registers one optional hook:

- `after_implement` → prompt to run `/speckit.verify-review-ship.verify`

`review` and `ship` remain manual because they are heavier analytical/release gates.

## Configuration

Optional config file:

```text
.specify/extensions/verify-review-ship/verify-review-ship-config.yml
```

Template: `config-template.yml`.

Use it to set explicit commands for tests/build/lint/typecheck or tune gate behavior.

## Design Notes

This extension intentionally uses the original GitHub Spec Kit extension architecture instead of Claude/Codex-specific plugin formats:

- `extension.yml` manifest
- namespaced commands: `speckit.verify-review-ship.*`
- Markdown command files
- lifecycle hooks
- optional project config

The content is adapted from concepts in `addyosmani/agent-skills`, especially:

- `commands/review.toml`
- `commands/ship.toml`
- `skills/code-review-and-quality`
- `skills/shipping-and-launch`
- `agents/code-reviewer.md`
- `agents/security-auditor.md`
- `agents/test-engineer.md`

## License

MIT. See `LICENSE`.
