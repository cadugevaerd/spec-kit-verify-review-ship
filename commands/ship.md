---
description: "Decide readiness, merge a GO change into the primary branch, clean its worktree/branch, and summarize delivery"
---

# Ship, Merge, Cleanup, and Delivery Summary

Run after `/speckit.verify-review-ship.verify` and `/speckit.verify-review-ship.review`.

## User Input

$ARGUMENTS

## Purpose

Complete the delivery transaction with one terminal status:

```text
MERGED | MERGED_WITH_CLEANUP_WARNINGS | NO-GO | BLOCKED | DRY-RUN READY
```

A successful `GO` authorizes this command to merge the current work branch into the repository's primary branch, push the primary branch, safely clean the completed worktree/branch, and return a concise delivery summary. It does **not** deploy an application or infrastructure.

Use `--dry-run` in `$ARGUMENTS` to produce the decision and exact intended operations without changing local or remote Git state. Optional arguments may explicitly name `--base BRANCH` or `--remote REMOTE`; otherwise use extension configuration and then the remote default branch.

## Expected Inputs

Consume, in order:

1. Active Spec Kit artifacts: `spec.md`, `plan.md`, `tasks.md`, `quickstart.md`, contracts, data model, and checklists when present.
2. `/speckit.verify-review-ship.verify` report.
3. `/speckit.verify-review-ship.review` report.
4. Current Git repository, worktree, branch, diff, commits, remotes, and primary branch.
5. Project test/build/lint/typecheck, release, CI, rollback, and monitoring evidence.

If required verify/review evidence is missing, run those commands when possible; otherwise return `BLOCKED`. Never invent results.

## Phase A — Readiness Decision

Run independent Code Reviewer, Security Auditor, and Test Engineer perspectives in parallel when subagents are available, otherwise as isolated sequential passes.

Validate at least:

- requirements/tasks and changed behavior are covered;
- mandatory tests, build, lint, and typecheck pass;
- no unresolved Critical/Important review finding;
- no Critical/High security issue or exposed secret;
- performance, accessibility, infrastructure, migrations, documentation, monitoring, and rollback are addressed when applicable.

Create the rollback plan before `GO`, including trigger, exact rollback steps, data/migration handling, post-rollback verification, and recovery objective.

Decision rules:

1. Unresolved Critical issue, High security issue, Constitution failure/block, missing rollback plan, or missing production-bound verification evidence => `NO-GO` or `BLOCKED`.
2. `NO-GO` and `BLOCKED` perform **no merge, push, branch deletion, or worktree removal**.
3. `GO` continues automatically to the Git integration transaction unless `--dry-run` is present.

## Phase B — Git Pre-flight (fail closed)

Before changing Git state, discover and record:

```text
repository root and Git common directory
current worktree path and whether it is primary or linked
work branch and immutable work HEAD
target remote and primary branch
remote primary HEAD and remote work-branch HEAD
merge strategy and configured verification commands
```

Apply every guard below:

1. Require a Git repository, a named current branch, and no merge/rebase/cherry-pick/revert/bisect in progress. Detached HEAD => `BLOCKED`.
2. Resolve the remote from `--remote`, then `ship.remote`; resolve the primary branch from `--base`, then `ship.base_branch`, then the remote symbolic `HEAD`. Never guess `main` when discovery is available.
3. Require the work branch to differ from the primary branch and reject protected/reserved branches such as the primary branch itself.
4. Require the worktree to be completely clean, including staged, unstaged, untracked, conflicted, and modified-submodule state. Do not stash, discard, commit, or delete user changes automatically.
5. For `--dry-run`, perform remote discovery only with read-only queries such as `git ls-remote --symref <remote> HEAD` and `git ls-remote <remote> <refs>`. Do **not** fetch, prune, create/remove worktrees, checkout, merge, push, or update/delete any ref. After all local and remote read-only guards pass, return `DRY-RUN READY` with the exact planned operations and stop.
6. For a real transaction, fetch the identified remote with pruning and require the remote primary branch to exist.
7. If the work branch has an upstream, reject a behind or diverged branch. If a same-named remote work branch exists, record its exact HEAD for an atomic cleanup lease.
8. Require every existing worktree that will be touched during cleanup to be clean. Do not use `git clean`, `reset --hard` on a user worktree, `branch -D`, `worktree remove --force`, or forced primary-branch pushes. The only permitted `--force-with-lease` is the exact-ref lease used for conditional deletion of the completed remote work branch in Phase D.
9. Reconfirm that verify/review evidence corresponds to the recorded work HEAD. Stale evidence => `BLOCKED`.
10. Allow only the configured merge strategies `no-ff` and `ff-only`; any other value => `BLOCKED`.

## Phase C — Isolated Integration Transaction

Do not merge directly inside a potentially shared primary worktree. Use a temporary detached integration worktree based on the fetched remote primary HEAD:

1. Create a unique temporary integration worktree from `<remote>/<primary>` and record `base_before`.
2. Merge the immutable work HEAD using the validated strategy: `--no-ff --no-edit` by default, or `--ff-only` when configured.
3. On conflict, abort the merge, remove only the clean temporary integration worktree, preserve the work branch/worktree, and return `BLOCKED` with conflicted paths.
4. In the integrated tree, rerun all mandatory configured test/build/lint/typecheck gates. A failed gate means `NO-GO`; remove the temporary integration worktree and preserve the work branch/worktree.
5. Record `integrated_head`, verify `base_before` and the recorded work HEAD are its ancestors, and push exactly `integrated_head` to `refs/heads/<primary>` **without force**.
6. A non-fast-forward/rejected push means the primary branch changed concurrently. Preserve the work branch/worktree, remove only the temporary integration worktree, fetch again, and return `BLOCKED`; never retry by force.
7. Read the remote primary ref back and require it to equal `integrated_head`. Only this verified remote equality marks the merge complete.

If the merge is verified remotely, cleanup failures must never roll back or hide the successful merge. Continue with warnings and finish as `MERGED_WITH_CLEANUP_WARNINGS` when necessary.

## Phase D — Safe Cleanup

Cleanup starts only after the remote primary ref is verified at `integrated_head`.

1. Remove the temporary integration worktree and temporary integration ref.
2. For a **linked worktree** that still has the exact recorded work HEAD and is clean:
   - change to a safe directory outside it;
   - remove it with ordinary `git worktree remove` (never `--force`);
   - prune only stale worktree metadata.
3. For the **primary worktree**, never delete its directory. If possible, switch it to the updated primary branch and fast-forward it. If that branch is already checked out elsewhere, park the clean primary worktree at the verified integrated commit in detached mode and report this explicitly.
4. Delete the local work branch only when it is no longer checked out anywhere and `git merge-base --is-ancestor <recorded-work-head> <integrated-head>` succeeds. Use `git branch -d`, never `-D`.
5. Delete the same-named remote work branch only when it existed at pre-flight, its recorded commit is an ancestor of `integrated_head`, and a fresh `git ls-remote` still returns the exact recorded remote work HEAD. Perform an atomic compare-and-delete with:

   ```bash
   git push --force-with-lease=refs/heads/<work-branch>:<recorded-remote-work-head> \
     <remote> --delete <work-branch>
   ```

   This exact-ref lease is the only permitted force option. If the ref advanced or the lease is rejected, preserve the branch and report `WARNING`; never retry with a broader lease or force. Re-read the remote ref after the operation and require it to be absent before reporting `DONE`.
6. Re-read worktree registrations, local branches, the remote work branch, and remote primary HEAD. Report each cleanup action as `DONE`, `SKIPPED`, or `WARNING` with evidence.

Never delete the primary branch, the repository's primary worktree, an unmerged branch, a dirty worktree, or a branch/ref that changed after pre-flight.

## Phase E — Delivery Classification and Summary

Classify the delivered work from Spec Kit artifacts, branch/commit conventions, and changed scope. Use one primary type:

```text
PRODUCT | FEATURE | BUGFIX | SECURITY | REFACTOR | DOCUMENTATION | CHORE | OTHER
```

If evidence is ambiguous, use `OTHER`; do not invent a product or feature label. Summarize what was delivered in business language, then the technical proof.

## Required Output

```markdown
## Ship Result: MERGED | MERGED_WITH_CLEANUP_WARNINGS | NO-GO | BLOCKED | DRY-RUN READY

### Delivered
- Type: PRODUCT | FEATURE | BUGFIX | SECURITY | REFACTOR | DOCUMENTATION | CHORE | OTHER
- Name: <feature/spec/title or concise inferred title>
- Outcome: <what changed and why it matters>
- Scope: <requirements/tasks/components delivered>

### Quality Evidence
- Verify: PASS/FAIL/BLOCKED — <report/ref>
- Review: APPROVE/REQUEST CHANGES/BLOCKED — <report/ref>
- Integration gates: <commands and real results>
- Risks/rollback: <remaining risks and rollback summary>

### Merge
- Work branch: <branch>@<recorded work HEAD>
- Primary branch: <remote>/<branch>
- Strategy: <strategy>
- Before: <base_before>
- Integrated: <integrated_head or not created>
- Remote verification: PASS/FAIL/NOT RUN — <observed ref>

### Cleanup
| Item | Status | Evidence / note |
|---|---|---|
| Temporary integration worktree/ref | DONE/SKIPPED/WARNING | ... |
| Work worktree | DONE/SKIPPED/WARNING | ... |
| Local work branch | DONE/SKIPPED/WARNING | ... |
| Remote work branch | DONE/SKIPPED/WARNING | ... |

### Delivery Summary
<3-7 concise bullets covering user/business outcome, important technical changes, verification, merge, cleanup, and any residual action>
```

For `NO-GO` or `BLOCKED`, include blockers and the exact safe resume point. For a verified merge with cleanup warnings, lead with the fact that delivery is already merged and list only the residual cleanup actions; never describe it as unmerged.
