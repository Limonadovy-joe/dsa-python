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

### 1. Get the issue context

- If the issue was **just created in this conversation** and the full spec
  (title, description, labels, acceptance criteria) is already in context,
  skip the API call and use that data directly.
- Otherwise, use `get_issue` with the issue identifier (e.g., DSA-9). Read
  the description to understand the spec, acceptance criteria, and labels.

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

### 4. Do the work

Follow the spec:
- For Implementation: create the module in `dsa/<topic>/`, export from `__init__.py`, create mirrored tests in `tests/<topic>/`.
- For Benchmark/Experiment: write benchmark code, run it, save results to `results/`.
- For Bug: reproduce, fix, add regression test.
- For all: follow repo conventions in `docs/conventions.md`.

### 5. Commit (git-sync rules)

1. Read the diff (`git diff`, `git diff --staged`, untracked files) and group
   changes into **logical commits**. One change, one commit.
2. Stage each group by explicit path (`git add -- <path>...`).
3. Files that look like someone else's work in progress (another task's
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

### 6. Gate

Run the full project gate:

```bash
uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest
```

- All four must pass.
- If any step fails, fix the issue, commit the fix, and re-run the gate.
- Do **not** push with a failing gate.

### 7. Pull

1. Run `git pull --no-rebase`. Merge, never rebase.
2. No conflict: go to Push.
3. Conflict: resolve hunk by hunk, keeping both sides' intent.
   - **NEVER** use `-X ours`, `-X theirs`, `git checkout --ours/--theirs` on a
     whole file, or delete a side to make the conflict disappear.
   - A hunk whose intent is unclear: **stop and ask** the user, showing both sides.
4. After resolving, run the full gate again before concluding the merge.
5. Conclude with `git commit --no-edit`.

### 8. Push

1. Branch has an upstream: `git push`.
2. New branch (no upstream): `git push -u origin <branch>`.
3. **NEVER** `--force` or `--force-with-lease`.
4. Push rejected as non-fast-forward: go back to Pull **once**. Rejected again: **stop**.

### 9. Wrap up

- **Never move to Done** — leave in In Progress. Only the human moves issues to Done.
- Post a short report:

```
Issue      DSA-<number> — <title>
Branch     <type>/DSA-<number>-<description>
Committed  <sha> <subject>
           <sha> <subject>
Gate       passed
Pulled     <N> commits (<conflicts resolved: N files | no conflicts>)
Pushed     <N> commits to <remote>/<branch>
Left out   <path> — <why>
```

Drop lines that do not apply.

## Key references
- Linear IDs (team, project, states, milestones): see `.linear/config.md`
