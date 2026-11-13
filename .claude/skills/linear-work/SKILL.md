---
name: linear-work
description: Pick up a DSA Linear issue end to end. Moves it to In Progress, creates the branch, hands the code to the dsa-implementer agent, loops it through dsa-reviewer until approved, then commits, runs the gate, pushes and opens the PR. Use when asked to work on, start or pick up DSA-<n>.
---
# Skill: Work on a Linear issue

## When to use
When the user asks to pick up, start, or work on a Linear issue.

## Git safety rules (from git-sync)

These rules are **always active** during the entire workflow:

- **NEVER** force-push, rebase shared history, or skip a hook (`--no-verify`).
- **NEVER** `git add -A`, `git add .`, or `git commit -a`. Stage by explicit path.
- **NEVER** stage secrets: `.env*` (except `.env.example`), `*.pem`, `*.key`,
  `id_rsa*`, or any diff line that holds a credential/token. Stop and warn.
- A failing hook is a **stop**, not a retry with `--no-verify`. Fix the cause.
- A hunk whose intent is unclear during conflict resolution: **stop and ask**.

---

## Steps

### 0. Guard: run only inside a task worktree

Every task gets its own git worktree (`spawn DSA-<n>`, see `docs/herdr-workflow.md`).
The main checkout stays on `main` and is shared by every session opened there,
so a branch switch in it moves all of them. Check **before step 1**, so nothing
changes in Linear or git when the check fails:

```bash
test "$(git rev-parse --path-format=absolute --git-dir)" != \
     "$(git rev-parse --path-format=absolute --git-common-dir)" \
  && echo worktree || echo main-checkout
```

- `worktree`: continue.
- `main-checkout`: **stop.** Change nothing (no Linear state, no branch). Tell
  the user to run `spawn DSA-<n>` in a plain shell pane (not as a message to
  Claude) and to continue in the new workspace's `impl` pane. Continue in the
  main checkout only if the user explicitly says so in this conversation, and
  say that every other session in this checkout will switch branch too.

### 1. Get the issue context

- If the issue was **just created in this conversation** and the full spec
  (title, description, labels, acceptance criteria) is already in context,
  skip the API call and use that data directly.
- Otherwise, use `get_issue` with the issue identifier (e.g., DSA-9). Read
  the description to understand the spec, acceptance criteria, and labels.
- **No `## Acceptance criteria`, or only vague/untestable ones** ("works",
  "handles edge cases", unfilled `<...>` placeholders): **stop**. Don't move
  the issue or branch. Propose concrete criteria to the human and continue
  only after they confirm (and the ticket is updated). Rules:
  `docs/definition-of-done.md`.

### 2. Move to In Progress

Update the issue state to `In Progress` (look up the state ID from `.linear/config.md`)
and assign to `me`.

### 3. Create the branch

Use the naming convention `<type>/DSA-<number>-<kebab-description>`. Derive the
branch type from the issue's **Type** label:

| Type label | Branch type |
|---|---|
| Implementation | `feat` |
| Bug | `fix` |
| Refactor | `refactor` |
| Experiment, Benchmark | `perf` |
| Analysis, Writing, Literature | `docs` |
| Tooling | `chore` |
| Visualization | `feat` |

```bash
git checkout -b <type>/DSA-<number>-<kebab-description>
```

If no Type label is set, default to `feat`.

**Worktree already on the branch** (made by `spawn DSA-<n>` or
`git worktree add -b`): if `git branch --show-current` already shows the
branch, skip the checkout.

### 4. Implement: hand off to `dsa-implementer`

You are the **orchestrator**. In steps 4–5 you never edit `dsa/` or `tests/`
yourself; every code change goes through the implementer. The contract and
file formats are in `docs/agent-handoff.md`.

**Don't use the agents** for Type `Analysis`, `Writing`, `Literature` or
`Tooling`, or for a `needs-human` issue. Do that work directly (or stop and
ask), then skip to step 6.

1. Pick the **mode**:
   - Implementation or Visualization → `feature`
   - Bug → `fix`
   - Refactor → `refactor`
   - Benchmark or Experiment → `benchmark`
   - Component `Tests`, or an issue that only asks for tests → `test`
2. Write `.handoff/DSA-<n>/brief.md` in the format from
   `docs/agent-handoff.md`: the issue spec verbatim, acceptance criteria,
   mode, files in scope, and what is out of scope. Check that `.handoff/` is
   gitignored (`git check-ignore -q .handoff`).
3. Spawn the implementer with the Agent tool, `subagent_type: dsa-implementer`:

   ```
   DSA-<n> round 1. Mode: <mode>. Brief: .handoff/DSA-<n>/brief.md.
   Work in this worktree; write .handoff/DSA-<n>/impl-1.md and return it.
   ```

   Keep its agent id: rounds 2+ resume the **same** agent.
4. Wait for its completion notification. Don't predict its result, and don't
   touch `dsa/` or `tests/` while it runs.
5. Check its note: `.handoff/DSA-<n>/impl-1.md` must exist with a passing
   `Gate:` line. If the note has a `Blocked` section or says `Gate: FAIL`,
   stop and show the human.

### 5. Review loop: `dsa-reviewer` ⇄ `dsa-implementer`

Repeat for rounds `k = 1, 2, 3`:

1. Spawn a **fresh** reviewer with the Agent tool,
   `subagent_type: dsa-reviewer`:

   ```
   Review DSA-<n> round <k>. Brief: .handoff/DSA-<n>/brief.md.
   Handoff note: .handoff/DSA-<n>/impl-<k>.md.
   Previous review: .handoff/DSA-<n>/review-<k-1>.md   (round ≥ 2 only)
   Scope: git diff origin/main...HEAD plus uncommitted changes.
   ```

2. Save its final message **verbatim** to `.handoff/DSA-<n>/review-<k>.md`.
3. Read the last line of the review:
   - `VERDICT: approve` → go to step 6.
   - `VERDICT: changes-requested` with `k < 3` → resume the implementer with
     SendMessage to its agent id:

     ```
     DSA-<n> round <k+1>. Review: .handoff/DSA-<n>/review-<k>.md.
     Fix every must-fix, answer every finding in "Review responses",
     rerun the gate, write .handoff/DSA-<n>/impl-<k+1>.md and return it.
     ```

     If the implementer can't be resumed, spawn a new `dsa-implementer` with
     the same text plus `Brief: .handoff/DSA-<n>/brief.md`. Wait for it, check
     its note as in step 4.5, then start the next round.
   - No `VERDICT:` line → spawn the reviewer once more for this round. If it
     still gives no verdict, stop and ask.
4. Stop if the review still says `changes-requested` after round 3, or if the
   implementer and reviewer still disagree about a declined finding. Show the
   human the open must-fix findings and both positions. Don't commit.

Keep any `should-fix` findings still open after approval for the PR body.

### 6. Commit (git-sync rules)

1. Never stage `.handoff/`. It is gitignored; if `git status` lists it, stop
   and fix `.gitignore`.
2. Read the diff (`git diff`, `git diff --staged`, untracked files) and group
   changes into **logical commits**. One change, one commit.
3. Stage each group by explicit path (`git add -- <path>...`).
4. Files that look like someone else's work in progress (another task's
   half-edit, a file you cannot explain): **leave unstaged** and list in the report.

#### Commit format

Follow the **Conventional Commits** spec:

```
<type>(<scope>): <description>

<body>

Refs: DSA-<number>
```

- **type** (required): `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`
- **scope** (recommended): the topic area (`arrays`, `linked-list`, `deque`, `ci`, etc.)
- **description** (required): imperative mood, lowercase start
- **body** (optional): why, not what — only when non-trivial
- **footer**: always include `Refs: DSA-<number>` linking back to the issue.
  **Never** add a `Co-Authored-By` trailer.

Use a HEREDOC for multi-line messages:

```bash
git commit -m "$(cat <<'EOF'
type(scope): description

Body text here.

Refs: DSA-<number>
EOF
)"
```

#### Pre-commit hooks

The repo uses **prek** (`.pre-commit-config.yaml`). On every commit the hooks
run automatically (`ruff-check`, `ruff-format`, `mypy`).

If a hook fails:
1. Read the error output.
2. Fix the issue in the relevant file(s).
3. Re-stage the fix and create a **new** commit (never `--amend` after a hook
   failure — the original commit did not land).

### 6b. Definition of done check

Before the gate, walk the code DoD in `docs/definition-of-done.md`:

- Every acceptance criterion maps to a test (the `Acceptance criteria` table
  in the latest `impl-<k>.md`, confirmed by the reviewer).
- `docs/gotchas.md` updated if the behaviour is
  surprising (the implementer can't edit `docs/`; you do it, in its own
  `docs(...)` commit).
- `git grep -n "TODO" -- dsa tests`: TODOs this ticket resolves are gone; any
  remaining one in touched files has `TODO(DSA-<n>)`.
- Every commit has the `Refs: DSA-<number>` footer.

### 7. Gate

Run the full project gate:

```bash
uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest
```

- All four must pass.
- If a step fails in `dsa/` or `tests/`, resume the implementer with the
  failure (it updates its note), commit its fix, and re-run the gate.
- Do **not** push with a failing gate.

### 8. Pull

1. Run `git pull --no-rebase`. Merge, never rebase.
2. No conflict: go to step 9 (Push).
3. Conflict: resolve hunk by hunk, keeping both sides' intent.
   - **NEVER** use `-X ours`, `-X theirs`, `git checkout --ours/--theirs` on a
     whole file, or delete a side to make the conflict disappear.
   - A hunk whose intent is unclear: **stop and ask** the user, showing both sides.
4. After resolving, run the full gate again before concluding the merge.
5. Conclude with `git commit --no-edit`.

### 9. Push

1. Branch has an upstream: `git push`.
2. New branch (no upstream): `git push -u origin <branch>`.
3. **NEVER** `--force` or `--force-with-lease`.
4. Push rejected as non-fast-forward: go back to step 8 (Pull) **once**. Rejected again: **stop**.

### 10. Pull Request

After pushing, create a PR targeting `main`:

```bash
gh pr create --title "<type>(<scope>): <description>" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points explaining the change>

Refs: DSA-<number>

## Acceptance criteria
- [x] <criterion, verbatim from the ticket> — `test_<name>`

## Definition of done
- [x] Tests for each acceptance criterion, edge cases included
- [x] CI green: tests, ruff format, ruff check, mypy --strict, pre-commit, coverage gate
- [x] gotchas.md updated if surprising; new public names in `__all__`
- [x] Resolved TODOs removed; remaining TODOs carry a ticket ID
- [x] Conventional commits with `Refs: DSA-<number>`
- [x] Reviewed: dsa-reviewer approved in round <k>
- [ ] Merged to `main` (human)

## Review
- Open should-fix: <list, or "none">
EOF
)"
```

- **Title**: follows the same conventional-commit format as the primary commit.
- **Body**: brief summary, issue reference, the ticket's acceptance criteria
  each with its test, and the Definition of done checklist. Tick only what is
  true; an unticked item is named in the wrap-up report. Leave "Merged" for
  the human.
- If a PR already exists for this branch, skip this step.

### 11. Wrap up

- **Never move to Done** — leave in In Progress. Only the human moves issues to Done.
- Post a short report:

```
Issue      DSA-<number> — <title>
Branch     <type>/DSA-<number>-<description>
Review     approved in round <k> (<N> must-fix fixed, <N> should-fix open)
Committed  <sha> <subject>
           <sha> <subject>
Gate       passed
Pulled     <N> commits (<conflicts resolved: N files | no conflicts>)
Pushed     <N> commits to <remote>/<branch>
PR         <url>
Left out   <path> — <why>
```

Drop lines that do not apply.

## Key references
- Linear IDs (team, project, states, milestones): see `.linear/config.md`
- Implementer ⇄ reviewer contract and file formats: `docs/agent-handoff.md`
- Agents: `.claude/agents/dsa-implementer.md` (skill `dsa-implement`),
  `.claude/agents/dsa-reviewer.md` (skill `dsa-review`)
