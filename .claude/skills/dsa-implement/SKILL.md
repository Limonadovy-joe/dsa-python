---
name: dsa-implement
description: Implement one DSA ticket round test-first (feature, fix, refactor, test or benchmark), run the full gate, and write the handoff note for dsa-reviewer. Use when the dsa-implementer agent runs, or when asked to implement a brief or address a review-<k>.md in .handoff/.
argument-hint: "DSA-<n> round <k> [mode]"
---

# dsa-implement

The implementer half of the handoff in `docs/agent-handoff.md` (contract, file
formats). Read it first, then `CLAUDE.md`, `docs/architecture.md`,
`docs/conventions.md` and `docs/gotchas.md`.

Arguments: `$ARGUMENTS`

## 1. Input

| Round | Read | Do |
|---|---|---|
| 1 | `.handoff/DSA-<n>/brief.md` | what it asks, in its mode, inside its scope |
| ≥ 2 | `.handoff/DSA-<n>/review-<k-1>.md` | fix every `must-fix`; do `should-fix` unless you have a reason; nothing else |

## 2. Modes

| Mode | Do |
|---|---|
| `feature` | New structure/algorithm or operation. New module: `uv run python scripts/dsa.py create-<type>` scaffolds module + mirrored tests. Generic `class X[T]:`, export in the topic `__init__.py` `__all__`. |
| `fix` | Failing regression test first, then the smallest fix. |
| `refactor` | No behaviour change; tests green before and after, unchanged except imports of a moved public name. Say what got simpler or faster. |
| `test` | Tests only: empty, single, resize boundary, negative/out-of-range index, error path (`pytest.raises`), `parametrize` tables, public imports, `collections`/`heapq`/`bisect` as oracle. Touch `dsa/` only for a bug a test exposed, and say so. |
| `benchmark` | Performance tests per `docs/performance-testing.md`; results to `results/`. |

## 3. Steps

1. Test first, at least one per acceptance criterion in the brief; see it
   fail: `uv run pytest tests/<topic>/<file> -x`. Then make it pass. A
   criterion you can't test as written → `Blocked`, don't reinterpret it.
2. Check each complexity claim against the code; time a doubtful one with
   doubling sizes (`uv run python -c ...`).
3. Full gate until green:
   `uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest`
4. Delete TODOs the ticket resolves; any TODO you leave gets `TODO(DSA-<n>)`.
5. Write `.handoff/DSA-<n>/impl-<k>.md` (format in `docs/agent-handoff.md`,
   including the acceptance criteria → test table;
   from round 2 with the "Review responses" table: fixed, or declined with a
   reason) and return **the same text** as the final message.

## 4. Blocked

Spec unclear, gate red for a reason outside the scope, or a design decision
the brief doesn't settle: stop. Write the note with the `Gate:` line and a
`Blocked` section saying exactly what you need, return it. Don't guess.
