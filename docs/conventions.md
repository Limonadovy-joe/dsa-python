# Conventions

## Solutions

- One data structure or algorithm family per module; `snake_case.py` named after
  the thing, not the problem (`dynamic_array.py`, not `leetcode_1046.py`).
- Export the public names from the topic's `__init__.py` and list them in
  `__all__`. Anything not exported is private to the module.
- Module docstring says what it is; class/function docstring states **complexity**
  (time and space) for the main operations. That line is the point of the repo.
- Prefix helpers with `_`. No module-level mutable state, no printing, no input.
- Fully annotated, `mypy --strict` clean. No bare `Any` in a public signature —
  if a container holds arbitrary elements it is **generic**, using PEP 695
  syntax: `class DynamicArray[T]:`, `def append(self, value: T) -> None`.
- `from __future__ import annotations` at the top, and import typing-only names
  under `if TYPE_CHECKING:` so they cost nothing at runtime.
- A `cast` is allowed only where an invariant the checker can't see makes it
  safe (e.g. buffer slots below `_size` are always populated). Comment the
  invariant. `# type: ignore` needs an error code and a reason.
- Formatting is not a matter of taste: `uv run ruff format .` decides.
- Implement from scratch — the whole exercise is not reaching for `collections`,
  `heapq`, or `bisect` inside a solution. They are fine in tests as an oracle.
- Standard library only for runtime deps.

## Testing

- `tests/` mirrors `dsa/` exactly: `dsa/arrays/dynamic_array.py` →
  `../tests/queue/unit`.
- Tests import the **public** path (`from dsa.arrays import DynamicArray`). If a
  test needs a private path, the export is wrong, not the test.
- Plain `assert`, plain functions, no test classes. `pytest.mark.parametrize` for
  table cases.
- Cover per structure: empty, single element, growth/resize boundary, negative or
  out-of-range index, and the error path (`pytest.raises`).
- Test names describe the behaviour: `test_pop_returns_and_shrinks`.
- New code lands with its test in the same change. `uv run pytest` must be green.
- Tests that cross module boundaries go in an `integration/` folder and set
  `pytestmark = pytest.mark.integration` (like `performance/` does), so the
  pre-push hook and CI run them as their own stage after the unit tests.
- Branch coverage of `dsa/` must stay at or above `fail_under` in
  `pyproject.toml`; CI fails below it.

## Strategy + Adapter pattern for pluggable backends

Data structures that can be backed by different storage (e.g. linked list vs
array) use a two-pattern combo:

1. **Strategy** — A `Protocol` (e.g. `QueueStorage`, `DequeStorage`) defines the
   operations every backend must support. The main class (`Queue`, `Deque`)
   accepts any conforming backend at construction and delegates all calls to it.
2. **Adapter** — Each backend class (e.g. `QueueLinkedList`, `DequeDoubleLinkedList`)
   wraps a lower-level data structure behind the storage protocol, translating
   method names and managing state.

```
QueueStorage (Protocol)          ← strategy interface
├── QueueList (Adapter)          ← wraps Python list
└── QueueLinkedList (Adapter)    ← wraps LinkedList
Queue (Context)                  ← delegates to any QueueStorage
```

**Why:** the same public API runs against every backend, so a single
parametrized test suite (or benchmark) exercises all implementations without
duplication. Performance tests swap the strategy to compare backends
head-to-head (see `docs/performance-testing.md`).

**Rules for new structures:**
- The protocol goes in the same module as the main class.
- Each adapter lives in the same module (unless it grows large enough to split).
- The main class never knows which adapter it holds — only the protocol.
- Test fixtures parametrize over a `BACKENDS` dict that maps name → factory
  (see `tests/<topic>/conftest.py`).

## Branch naming

Branches tie the conventional commit **type** to the Linear issue:

```
<type>/DSA-<number>-<kebab-case-description>
```

- **type** matches the primary conventional commit type (`feat`, `fix`, `test`,
  `refactor`, `docs`, `perf`, `chore`, `ci`, `build`, `style`).
- **DSA-number** is the Linear issue ID.
- **description** is a short kebab-case summary.

Examples: `feat/DSA-11-implement-basic-bst-tests`,
`fix/DSA-15-deque-remove-front-bug`.

For small housekeeping that does not warrant a ticket:

```
chore/<kebab-case-description>
```

No `Refs:` footer needed. Keep these commits small and obvious.

`chore/` no-ticket branches are appropriate for:
- Docs-only changes (`docs/`, `.linear/`, `.claude/`)
- `.gitignore` / config updates
- CI tweaks

NOT for changes to `dsa/` or `tests/` source — those always get a ticket.

## Before a change is done

```bash
uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest
```

All four must pass. The git hooks (`uv run prek install`) enforce the first
three on every commit and the tests on every push. Silencing a rule is a last
resort and needs an inline reason; if a rule is wrong for the whole repo, change
`pyproject.toml` instead of sprinkling `noqa`.
