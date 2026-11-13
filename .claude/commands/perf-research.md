# perf-research

Scaffold or refresh the performance research of one data structure under
`results/<structure>/` (`data/` for measurements, `report/<structure>.md` for
the text and graphs). Contract: `docs/performance-research.md`.

## Usage

```
/perf-research <structure>             # scaffold: folders + doc + tables + exercises
/perf-research exercises <structure>   # (re)write the Exercises section only
/perf-research tables <structure>      # sync rows, refresh measured columns from data/
/perf-research list                    # structures, classes, backends, doc yes/no
```

`<structure>` is the module stem: `queue`, `deque`, `circular_array`,
`dynamic_array`, `linked_list`, `doubly_linked_list`.

## Instructions

Arguments: `$ARGUMENTS`

1. **`list`**: run `uv run python scripts/perf_research.py list` and show the
   output.
2. **`tables <structure>`**: run
   `uv run python scripts/perf_research.py tables <structure>` (pass
   `--run-id <id>` through if given) and show the output. No agent is needed:
   the script is deterministic.
3. **`<structure>`** or **`exercises <structure>`**: spawn the
   `perf-scaffolder` agent with the prompt
   `mode: scaffold, structure: <structure>` (or `mode: exercises`). Then relay
   its final message: the doc path, what changed, and the exercise counts.
4. Never fill the human-owned columns (Expected time/space, Measured class,
   Verdict, Bound, Test, Notes) and never answer the exercises. That work is
   the user's.
