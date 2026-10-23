# dsa

Data structures and algorithms implemented from scratch in Python — no `heapq`,
no `bisect`, no `collections` shortcuts. Packaged as a normal library so every
implementation is importable and covered by tests.

## Setup

```bash
uv sync                  # creates .venv and installs dsa in editable mode
uv run prek install      # git hooks: lint/format/types on commit, tests on push
uv run pytest            # run the suite
uv run ruff format .     # format
uv run ruff check .      # lint
uv run mypy              # type-check (strict)
```

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). Everything is fully
annotated with PEP 695 generics and checked by `mypy --strict`.

## Usage

```python
from dsa.arrays import DynamicArray

array = DynamicArray([1, 2, 3])  # DynamicArray[int]
array.append(4)
array.insert(0, 0)
array.pop()  # -> 4
list(array)  # [0, 1, 2, 3]
len(array)  # 4
array.capacity  # allocated slots, grows by doubling
```

## Layout

```
dsa/       one package per topic: arrays, linked_lists, stacks, queues, trees,
           graphs, heaps, hashing, sorting_searching, dynamic_programming,
           greedy, backtracking
tests/     mirrors dsa/, one test file per module
docs/      architecture, conventions, gotchas
```

Import from the topic package, not the module: `from dsa.arrays import DynamicArray`.

## Contributing to your own repo

Each implementation documents the time and space complexity of its main
operations, and ships with tests covering the empty case, the growth boundary,
and the error paths. See [docs/conventions.md](docs/conventions.md).
