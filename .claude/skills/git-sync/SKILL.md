# Skill: git-sync

Sync the current branch in one pass — commit the working tree, run the gate,
pull, push. Use when the user runs `/git-sync` or says "git-sync", "sync",
"commit and push", "pull and push", or "sync my branch".

## Hard rules

- **NEVER** force-push, rebase shared history, or skip a hook (`--no-verify`).
- **NEVER** `git add -A`, `git add .`, or `git commit -a`. Stage by explicit path.
- **NEVER** stage secrets: `.env*` (except `.env.example`), `*.pem`, `*.key`,
  `id_rsa*`, or any diff line that holds a credential/token. Stop and warn.
- A failing hook is a **stop**, not a retry with `--no-verify`. Fix the cause.
- A hunk whose intent is unclear during conflict resolution: **stop and ask**.

---

## 1 - Look

1. Run `git status`, `git branch --show-current`, and
   `git rev-parse --abbrev-ref @{upstream}` (may fail on new branches).
2. Run `git fetch` then `git rev-list --left-right --count HEAD...@{upstream}`
   for ahead/behind.
3. **Stop** on a detached HEAD.
4. **Stop** when an in-progress merge, rebase, cherry-pick, or revert exists
   that this run did not start (`.git/MERGE_HEAD`, `.git/rebase-merge`,
   `.git/rebase-apply`, `.git/CHERRY_PICK_HEAD`).
5. Nothing to commit and nothing ahead or behind: say "in sync" and stop.

### Branch check

Verify the current branch follows one of the accepted branch patterns:

```
<type>/DSA-<number>-<kebab-case-description>   (ticket work)
chore/<kebab-case-description>                  (housekeeping — no ticket needed)
```

`chore/` no-ticket branches are only for docs, config, CI, and infra changes —
never for changes to `dsa/` or `tests/` source (those always get a ticket).

If on `master` or `main`, **stop** — work should happen on a feature branch.
If the branch name does not match either convention, warn the user but continue.

---

## 2 - Commit

1. Read the diff (`git diff`, `git diff --staged`, untracked files) and group
   changes into **logical commits**. One change, one commit.
2. Stage each group by explicit path (`git add -- <path>...`).
3. Files that look like someone else's work in progress (another task's
   half-edit, a file you cannot explain from this conversation): **leave
   unstaged** and list in the report.
4. Changes already staged by the user are one group; commit them as-is.

### Commit format

Follow the **Conventional Commits** spec as documented in
`.claude/commands/conventional-commit.md`:

```
<type>(<scope>): <description>

<body>

<footer>
```

- **type** (required): `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`
- **scope** (recommended): the topic area (`arrays`, `linked-list`, `deque`, `ci`, etc.)
- **description** (required): imperative mood, lowercase start
- **body** (optional): why, not what — only when non-trivial
- **footer** (optional): `BREAKING CHANGE:` or issue refs (e.g. `Refs: DSA-11`).
  Omit the `Refs:` footer on `chore/` branches that have no ticket.

Use a HEREDOC for multi-line messages:

```bash
git commit -m "$(cat <<'EOF'
type(scope): description

Body text here.

Refs: DSA-<number>
EOF
)"
```

### Pre-commit hooks

The repo uses **prek** (`.pre-commit-config.yaml`). On every commit the hooks
run automatically:

| Hook | What it does |
|---|---|
| `ruff-check` | Lint + autofix |
| `ruff-format` | Format |
| `mypy` | Strict type-check of `dsa/` and `tests/` |

If a hook fails:
1. Read the error output.
2. Fix the issue in the relevant file(s).
3. Re-stage the fix and create a **new** commit (never `--amend` after a hook
   failure — the original commit did not land).

---

## 3 - Gate

Before pushing, run the full project gate:

```bash
uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest
```

- All four must pass.
- If any step fails, fix the issue, commit the fix, and re-run the gate.
- Do **not** push with a failing gate.

---

## 4 - Pull

1. Run `git pull --no-rebase`. Merge, never rebase.
2. No conflict: go to Push.
3. Conflict: resolve hunk by hunk, keeping both sides' intent.
   - **NEVER** use `-X ours`, `-X theirs`, `git checkout --ours/--theirs` on a
     whole file, or delete a side to make the conflict disappear.
   - A hunk whose intent is unclear: **stop and ask** the user, showing both sides.
4. After resolving, run the full gate again before concluding the merge.
5. Gate fails: fix the merge, not the checks. Still failing: **stop and report**.
6. Conclude with `git commit --no-edit`.

---

## 5 - Push

1. Branch has an upstream: `git push`.
2. New branch (no upstream): `git push -u origin <branch>`.
3. **NEVER** `--force` or `--force-with-lease`.
4. Branch is `main` or `master`: **stop** — ask the user for confirmation
   before pushing. Offer creating a PR instead.
5. Push rejected as non-fast-forward: go back to Pull **once**. Rejected again:
   **stop**.

---

## 6 - Report

Keep it short:

```
Committed  <sha> <subject>
           <sha> <subject>
Gate       passed
Pulled     <N> commits (<conflicts resolved: N files | no conflicts>)
Pushed     <N> commits to <remote>/<branch>
Left out   <path> — <why>
```

Drop lines that do not apply.
