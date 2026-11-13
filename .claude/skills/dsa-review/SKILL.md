---
name: dsa-review
description: Review dsa code for convention compliance, correctness, and performance of the data structures and algorithms, with concrete optimisation tips. Use when asked to review a branch, a diff, a module or a topic package in this repo, or when the dsa-reviewer agent runs.
argument-hint: "[path | DSA-<n> | branch | --base <ref>]  (default: current branch vs origin/main)"
---

# dsa-review

A read-only review of `dsa/` (and its mirrored `tests/`) against the repo's
rules and against what the code actually costs at runtime. The output is a
findings list plus optimisation tips. **Never edit files.** Fixes are made by
whoever implements the ticket (the `impl` pane).

Arguments: `$ARGUMENTS`

## 1. Scope

| Argument | Review |
|---|---|
| none | `git diff origin/main...HEAD` plus uncommitted changes (`git diff HEAD`); if the branch is `main` with no diff, ask what to review |
| a path (`dsa/queues/`, `dsa/arrays/dynamic_array.py`) | those files in full, plus their mirrored tests |
| `DSA-<n>` or a branch name | that branch's diff vs `origin/main` |
| `--base <ref>` | diff vs that ref |

If `.handoff/DSA-<n>/` exists for the ticket, read `brief.md` and the newest
`impl-<k>.md` (and the previous `review-<k-1>.md` from round 2 on) before the
diff: they say what was asked and what the implementer claims. Verify the
claims; don't trust them. Contract: `docs/agent-handoff.md`.

Read every changed `dsa/` module **in full**, not just the hunks: complexity
depends on the helpers a method calls. Read the mirrored test file and the
topic `__init__.py`.

## 2. Load the rules first

Read before judging, and cite them in findings (`conventions.md: Solutions`):

- `CLAUDE.md` (ground rules)
- `docs/conventions.md` (solution + test rules, Strategy + Adapter pattern)
- `docs/gotchas.md` (Python and DSA pitfalls)
- `docs/performance-testing.md` (what and how to measure)

## 3. Checklist

### A. Conventions (from the docs; flag every miss)
- One structure/algorithm family per module, `snake_case` named after the thing.
- Public names exported from the topic `__init__.py` and listed in `__all__`;
  tests import the public path (`from dsa.queues import Queue`).
- Docstrings are optional: never flag a missing one. Flag a docstring only when
  it is wrong (e.g. claims a complexity the code doesn't have).
- `from __future__ import annotations`; typing-only imports under
  `if TYPE_CHECKING:`; generics with PEP 695 (`class Stack[T]:`), no bare `Any`.
- `cast` only with a commented invariant; `# type: ignore[code]` with a reason.
- No `collections`, `heapq`, `bisect` inside `dsa/` (fine in tests as oracle).
- Helpers `_`-prefixed; no module-level mutable state, no print, no input.
- Pluggable backends: Protocol + adapters in the same module; the main class
  only knows the Protocol; tests parametrise over `BACKENDS`.
- Tests: plain functions, behaviour names, `parametrize` for tables; cover
  empty, single, resize boundary, negative/out-of-range index, error path.
  Cross-module tests in `integration/` with `pytestmark`.

### A2. Acceptance criteria and Definition of done
If a brief exists: every acceptance criterion in it has a test that really
exercises it (not just a test with a matching name) and passes. Missing or
hollow → `must-fix`. Also check the code DoD in `docs/definition-of-done.md`:
resolved TODOs removed, remaining TODOs carry
`TODO(DSA-<n>)`, and a `docs/gotchas.md` entry is needed for surprising
behaviour (the implementer can't edit `docs/`: flag it as `should-fix` for
the orchestrator).

### B. Correctness
Off-by-one at bounds, empty-structure errors (right exception type and
message), aliasing (returning internal buffers), iterator invalidation during
mutation, `is` vs `==`, recursion without a `None` guard at the top,
linked-list pointer updates on head/tail/single-node cases, `__eq__` without
`__hash__` consequences.

### C. Performance — the main point of the repo
For **each public operation**, write down the target complexity (the ticket's
acceptance criteria; without a brief, the textbook bound for the structure)
and the **actual** complexity from the code, then flag any mismatch. Check:

| Trap | Why it costs | Better |
|---|---|---|
| `list.pop(0)`, `list.insert(0, x)`, `del lst[0]` | O(n) shift | head index / circular buffer / linked list |
| `x in some_list`, `.index()`, `.count()` in a loop | O(n) per call → O(n²) | maintain a set/dict or an index |
| slicing (`a[1:]`, `a[:mid]`) in recursion or loops | copies → O(n) per call, O(n log n)/O(n²) total | pass `lo, hi` indices |
| `len()` computed by walking a linked list | O(n) | keep a `_size` counter |
| append to tail without a tail pointer | O(n) | keep `_tail` |
| growth by constant (`+= 10`) | O(n) amortised append | multiply (×2, or ×1.5 for less waste) |
| never shrinking, or shrinking at ½ full | memory waste / thrash at the boundary | shrink to ½ when ¼ full (hysteresis) |
| `str +=` / list concatenation in a loop | O(n²) | collect in a list, `"".join` |
| recursion on user-sized input (DFS, tree walk) | RecursionError past ~1000 | explicit stack |
| visited marked on dequeue in BFS/DFS | duplicates in the frontier | mark when enqueued |
| repeated `isinstance`/Protocol checks or `@property` in a hot loop | attribute lookup overhead | hoist to a local |
| node classes without `__slots__` | ~100+ B extra per node, slower attribute access | `__slots__ = ("value", "next")` |
| `copy`/`list()` of the whole structure in an accessor or `__iter__` | O(n) memory per call | yield lazily |
| exceptions for control flow in the hot path | slow raise/catch | test the condition |
| building temporary lists in `__len__`, `__bool__`, `__contains__` | allocation per call | count / short-circuit |

Also consider: cache locality (array vs linked nodes), worst-case vs amortised
(document both when they differ, e.g. dynamic array append), space overhead per
element, and whether a cheaper Python built-in on a **plain list buffer** would
do the job without breaking the "implement it yourself" rule.

For Strategy + Adapter structures: compare the adapters. State which backend
wins for which operation and whether the Protocol forces a costly operation on
one of them (e.g. `peek_back` on a singly linked list).

### D. Measure when a claim is doubtful (optional, read-only)
If a complexity claim looks wrong, prove it instead of guessing: run a quick
growth check in a throwaway REPL, never by adding files:

```bash
uv run python -c "import timeit; from dsa.queues import Queue; ..."
```

Use doubling sizes (1k, 2k, 4k, 8k) and report the time ratio (≈2 → O(n),
≈4 → O(n²), ≈1 → O(1)). Existing performance tests: `uv run pytest -m performance`.
Don't run long benchmarks; say so if one would be needed.

### E. Gate (optional)
If asked, or if the diff is large: `uv run ruff check . && uv run mypy` and
the relevant `uv run pytest tests/<topic>`. Report failures verbatim.
A diff that adds a bare `# noqa` (no inline reason) is `must-fix`.

## 4. Output

```
## Review: <scope>  (<n> files, base <ref>)

### Previous findings   (round ≥ 2 only)
| # | Finding | Status: resolved / still open / declined-accepted / declined-rejected |

### Findings (most severe first)
1. [must-fix|should-fix][correctness|performance|convention|tests] dsa/x/y.py:42 — one-line defect.
   Why: concrete input/state → wrong result or cost (e.g. "dequeue on 10⁵ items: O(n) shift each → 5·10⁹ ops").
   Fix: the smallest change that solves it.

### Acceptance criteria   (when a brief exists)
| Criterion | Test | Verified? |

### Complexity table
| Operation | Target (AC) | Actual | OK? |

### Optimisation tips (not defects)
- Ranked by impact; each with the expected gain and any trade-off.

### Tests to add
- Missing cases from the conventions checklist, as test names.

VERDICT: approve | changes-requested
```

`must-fix`: correctness, complexity that doesn't match the target, a
convention violation, a required test case missing, an acceptance criterion
without a passing test, a failing gate.
`should-fix`: everything else worth changing. `VERDICT: approve` iff no
must-fix is open. The verdict is the last line, alone, exactly as written.

Severity order: correctness > performance mismatch with the target >
convention > style. Report only verified findings; mark a suspicion as
"unverified" if you couldn't confirm it. Formatting nits that `ruff format`
fixes are not findings.
