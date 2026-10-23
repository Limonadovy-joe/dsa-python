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

## Linear

Configuration (workspace, team, project, state IDs, milestone IDs) is in
`.linear/config.md` — **gitignored**, not committed. Agents must read that
file for IDs.

### Label groups

| Group | Children |
|---|---|
| **Type** (single) | Implementation, Experiment, Benchmark, Analysis, Writing, Literature, Bug, Refactor, Tooling, Visualization |
| **Area** (single) | Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Heaps, Hashing, Sorting/Searching, Dynamic Programming, Greedy, Backtracking |
| **Component** (single) | Core, Tests, Benchmarks, Notebooks, Report, Infra |
| **Agent** (single) | agent-ready, needs-human |
| **Flag** (single) | Blocked, Needs-supervisor, Reproducibility |

### Workflow rules

- Agents **never** set an issue to Done — only the human does.
- `agent-ready` means the spec is clear enough for an agent to implement.
- `needs-human` means the issue requires human judgment (proofs, design, writing voice).
- When an agent finishes work, it moves the issue to In Progress (no In Review state yet).
- Issue templates live in `.linear/templates/` — agents use them when creating issues.

### Project commands

| Task | Command |
|---|---|
| Full gate | `uv run ruff format . && uv run ruff check . && uv run mypy && uv run pytest` |
| Run benchmarks | `uv run pytest benchmarks/` (once harness is set up) |
| Results directory | `results/` |
| Report directory | `report/` |
