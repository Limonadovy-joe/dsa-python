# Architecture

A plain Python library. No app, no CLI, no I/O — everything is importable and testable.

## Layout

```
dsa/                    # the package (installed editable into .venv)
├── __init__.py         # version only; no re-exports of topics
├── arrays/
├── linked_lists/
├── stacks/
├── queues/
├── trees/
├── graphs/
├── heaps/
├── hashing/
├── sorting_searching/
├── dynamic_programming/
├── greedy/
└── backtracking/
tests/                  # mirrors dsa/, one test file per solution module
docs/                   # these files
```

Each topic package is a real package with an `__init__.py` that re-exports its
public names, so users import from the topic, not the module:

```python
from dsa.arrays import DynamicArray  # yes
from dsa.arrays.dynamic_array import DynamicArray  # works, but not the public path
```

## Commands (uv)

| Task | Command |
| --- | --- |
| Sync env + install `dsa` editable | `uv sync` |
| Run the tests | `uv run pytest` |
| Format | `uv run ruff format .` |
| Lint | `uv run ruff check .` |
| Lint + autofix | `uv run ruff check --fix .` |
| Type-check | `uv run mypy` |
| One test file | `uv run pytest tests/arrays/test_dynamic_array.py` |
| One test | `uv run pytest -k test_grows_by_doubling` |
| Add a runtime dep | `uv add <pkg>` |
| Add a dev-only dep | `uv add --dev <pkg>` |
| Throwaway REPL against the package | `uv run python` |
| Install the git hooks (once per clone) | `uv run prek install` |
| Run the pre-commit hooks by hand | `uv run prek run --all-files` |
| Run the pre-push hooks by hand | `uv run prek run --all-files --stage pre-push` |
| Retest (failed → new → rest) | `uv run python scripts/retest.py` |
| Tests with the coverage gate | `uv run coverage run -m pytest && uv run coverage report` |

The full gate before calling a change done:

```bash
uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest
```

## Tooling

- **ruff 0.16** is both the formatter (a black-compatible 88-column style) and
  the linter (pycodestyle, pyflakes, isort, bugbear, pyupgrade, pydocstyle,
  pylint, annotation and pathlib rules). Configured in `[tool.ruff]`.
- **mypy 2.3** in `strict` mode over `dsa/` and `tests/`, pinned to
  `python_version = "3.13"`. Configured in `[tool.mypy]`.
- **prek 0.5** (a drop-in for pre-commit) runs `.pre-commit-config.yaml`:
  ruff check, ruff format and mypy on **pre-commit**; unit then integration
  tests on **pre-push**. Every hook is `uv run --locked`, so it uses the
  versions in `uv.lock`.
- **coverage 7** measures branch coverage of `dsa/`; `[tool.coverage.report]`
  `fail_under` is the gate.
- All four are dev-group dependencies, so `uv sync` gets everyone the same versions.

## CI

`.github/workflows/ci.yml` runs on pushes to `main`, on PRs, and by hand:

1. **checks**: `prek run --all-files`, the same hooks as pre-commit.
2. **tests**, after checks pass, on {Ubuntu, Windows, macOS} × Python {3.13, 3.14}:
   unit tests, then integration tests, then the coverage gate.

Each job builds a fresh `.venv` from `uv.lock` on a uv-managed interpreter.
`UV_LOCKED=1` fails the job if the lock is stale. The uv cache is keyed on
`uv.lock`. Performance tests are not run in CI: shared runners make timings
noisy.

`uv sync` installs the project itself (hatchling backend, `packages = ["dsa"]`),
which is what makes `import dsa` resolve from anywhere in the venv.
