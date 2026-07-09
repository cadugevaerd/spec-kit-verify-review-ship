---
description: "Synthesize verify and review evidence into a ship go/no-go decision"
---

# Ship Gate

Adapted from Addy Osmani's `agent-skills` `/ship` workflow and integrated with Spec Kit artifacts.

## User Input

$ARGUMENTS

## Purpose

Produce a single production-readiness decision:

```text
GO | NO-GO
```

This command does **not** deploy by itself. It aggregates evidence, identifies blockers, and creates a rollback/monitoring plan before a human or deployment automation proceeds.

## Expected Inputs

Prefer consuming, in order:

1. Active Spec Kit feature artifacts:
   - `spec.md`
   - `plan.md`
   - `tasks.md`
   - `quickstart.md`
   - contracts/data model/checklists if present
2. `/speckit.verify-review-ship.verify` report.
3. `/speckit.verify-review-ship.review` report.
4. Current diff/staged changes/recent commits.
5. Project release/deploy docs and CI status if available.

If verify/review reports are missing, run or ask for:

```text
/speckit.verify-review-ship.verify
/speckit.verify-review-ship.review
```

## Ship Procedure

### Phase A — Independent specialist passes

Run three independent perspectives. If the current AI environment supports subagents/tools, execute them in parallel. If not, simulate the three perspectives in isolated sections and do not let one perspective depend on another.

#### 1. Code Reviewer perspective

Evaluate:

- correctness
- readability
- architecture
- security notes already visible in code review
- performance notes already visible in code review

Use the Review Gate five-axis standard.

#### 2. Security Auditor perspective

Evaluate:

- OWASP Top 10 style issues
- secrets and credentials
- auth/authz
- input validation and output encoding
- dependency/supply-chain risk
- infrastructure/config risk
- AI/LLM-specific risks when applicable: prompt injection, excessive agency, unsafe tool calls, context leakage, untrusted model output

Promote any Critical/High security issue to ship blocker.

#### 3. Test Engineer perspective

Evaluate:

- test coverage for spec requirements
- happy path, edge cases, error paths
- integration/e2e needs
- migration/data rollback coverage
- manual smoke test requirements

### Phase B — Launch readiness checklist

Check and summarize:

#### Code Quality

- all mandatory tests pass
- build/lint/typecheck pass or have documented exception
- review Critical/Important findings resolved or explicitly accepted

#### Security

- no Critical/High vulnerabilities
- no secrets in code or logs
- auth/authz and data boundaries covered

#### Performance

- no obvious N+1/unbounded operations
- latency/bundle/database risks identified
- Core Web Vitals considered for UI/web changes

#### Accessibility, if UI change

- keyboard navigation
- screen reader semantics
- focus management
- contrast
- error messages

#### Infrastructure

- environment variables documented and present
- migrations planned and reversible where possible
- feature flags/kill switch considered
- health checks/logging/error reporting in place
- monitoring dashboards/alerts identified

#### Documentation

- README/setup docs updated
- API docs/contracts current
- ADR/changelog/user docs updated where needed

### Phase C — Decision and rollback

Create a rollback plan before any GO decision.

Rollback plan must include:

- trigger conditions
- rollback steps
- database/data considerations
- feature flag/kill switch steps, if applicable
- verification after rollback
- estimated recovery time objective

## Output Format

```markdown
## Ship Decision: GO | NO-GO

**Feature:** <feature id/path or unknown>
**Scope:** <diff/branch/release target>
**Decision basis:** <verify/review reports + direct checks>

### Blockers (must fix before ship)
- [Source: verify/review/security/test/infra] <finding + file:line/evidence>

### Recommended Fixes (should fix before ship)
- [Source] <finding + recommendation>

### Acknowledged Risks
- <risk> — Mitigation: <mitigation> — Owner: <owner if known>

### Launch Checklist
| Area | Status | Evidence / Notes |
|---|---|---|
| Code quality | PASS/FAIL/RISK | ... |
| Security | PASS/FAIL/RISK | ... |
| Performance | PASS/FAIL/RISK | ... |
| Accessibility | PASS/FAIL/N/A/RISK | ... |
| Infrastructure | PASS/FAIL/RISK | ... |
| Documentation | PASS/FAIL/RISK | ... |

### Rollback Plan
- Trigger conditions: <signals>
- Rollback procedure: <exact steps>
- Data/migration handling: <notes>
- Verification after rollback: <checks>
- Recovery time objective: <target>

### Specialist Reports

#### Code Reviewer
<summary>

#### Security Auditor
<summary>

#### Test Engineer
<summary>

### Final Instruction
- If GO: deployment may proceed only after human confirmation.
- If NO-GO: fix blockers, rerun verify/review/ship.
```

## Decision Rules

1. Any unresolved Critical issue => default `NO-GO`.
2. Any High security issue => default `NO-GO`.
3. Missing rollback plan => `NO-GO`.
4. Missing verification evidence for production-bound change => `NO-GO`.
5. `GO` requires explicit evidence and still does not authorize deployment unless the user/deployment process confirms.
6. Do not invent CI/deploy/monitoring results. If unavailable, mark as `RISK` or `BLOCKED`.
