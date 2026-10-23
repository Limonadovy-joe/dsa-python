# git-sync skill — Changelog

## Why this skill exists

The original `git-sync` skill was a generic, multi-repo guardrail for agents
doing git operations. It included a Supabase gate, a "super-board writing
standard" commit format, and several features irrelevant to this repo. This
version strips it to the essentials and wires it into the dsa project's
existing conventions.

## Changes from the original

### Removed

| Section | Reason |
|---|---|
| **Supabase gate** (section 3) | This repo has no Supabase. Entire section dropped. |
| **Super-board writing standard** fallback | Not applicable. Replaced with a single commit format. |
| **Host-detection logic** ("if AGENTS.md defines a format...") | Unnecessary indirection — this skill *is* the host config. |
| **Emoji commit prefixes** | The repo uses Conventional Commits, not emoji. |
| **`resolving-merge-conflicts` skill** delegation | Not installed; inline resolution instructions kept. |

### Added

| Addition | Reason |
|---|---|
| **Branch check** (section 1) | Enforces the `<type>/DSA-<number>-<kebab-desc>` convention from `docs/conventions.md` and the `linear-work` skill. Stops on `main`/`master`. |
| **Conventional Commits format** (section 2) | Hardcoded as the only commit format, matching `.claude/commands/conventional-commit.md`. |
| **Gate step** (new section 3) | Runs the full `ruff format + ruff check + mypy + pytest` gate before pushing — the same gate documented in `CLAUDE.md` and enforced by prek hooks. |
| **Pre-commit hook table** | Documents the three prek hooks so the agent knows what to expect on commit. |
| **Linear issue ref in footer** | `Refs: DSA-<number>` convention ties commits to Linear issues. |

### Changed

| Original behaviour | New behaviour |
|---|---|
| Section numbering 1–6 with Supabase at 3 | Renumbered 1–6: Look, Commit, Gate, Pull, Push, Report |
| "Run the host's fast checks" (vague) | Explicit `uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest` |
| Commit format chosen at runtime from multiple sources | Single source: Conventional Commits as defined in this repo |

## How it fits with other skills

```
linear-ticket   — creates the issue in Linear
linear-work     — picks up an issue, creates the branch, does the work
conventional-commit — formats a single commit message
git-sync        — commits, gates, pulls, pushes (calls conventional-commit format)
```

`git-sync` is the last mile: once the work and gate pass, it gets the code
from the working tree to the remote in a safe, auditable way.
