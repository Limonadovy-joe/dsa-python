# dsa

Data structures and algorithms implemented from scratch, as an importable Python
library. Python 3.13.7, uv, pytest, ruff, mypy `--strict`. Standard library only
at runtime.

Read these before working in the repo:

- @docs/architecture.md — package layout and the uv commands
- @docs/conventions.md — how a solution and its test must be written
- @docs/gotchas.md — Python and DSA pitfalls, plus repo quirks

## Ground rules

- Before a change is done, all four must pass:
  `uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest`
- Everything is annotated and `mypy --strict` clean. Containers are generic
  (`class DynamicArray[T]:`), never `Any`-typed.
- Every new solution lands with its mirrored test in `tests/`.
- Public API is the topic package: `from dsa.arrays import DynamicArray`.
- Don't reach for `heapq`, `bisect`, or `collections` inside `dsa/` — implementing
  them is the exercise. They're fine in tests as an oracle.
