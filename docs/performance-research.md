# Performance research

Every data structure gets one research folder: your predictions, the
exercises, the measurements and the verdicts in one place. The tooling writes
the skeleton and the numbers. You write the Big-O, the reasons and the
verdicts.

## Layout

```
results/<structure>/            # <structure> = module stem: queue, deque, dynamic_array …
├── data/                       # raw measurements, tidy CSV (contract below)
│   ├── <run_id>.csv
│   └── <run_id>.meta.json      # machine profile, git SHA, harness params (Phase 4)
└── report/
    ├── <structure>.md          # the research doc
    └── *.png / *.svg           # figures, next to the text that cites them
```

## The research doc

`results/<structure>/report/<structure>.md` has five sections. Each table sits
between `<!-- perf:table:<key> -->` and `<!-- perf:end -->` markers. Keep the
markers: the script finds the tables by them.

| # | Section | Rows | Script fills | You fill |
|---|---|---|---|---|
| 1 | Operations | backend × public operation, plus rows you add | Structure, Backend, Operation (new rows only) | Expected time, Expected space, Notes |
| 2 | Exercises | — | — (the `perf-exercises` skill writes the questions) | every answer |
| 3 | Time complexity: measured | same as table 1 | Structure, Backend, Operation, Expected time (copied), n, Median time / call, Log-log slope | Measured class, Verdict, Notes |
| 4 | Space complexity: measured | same as table 1 | Structure, Backend, Operation, Expected space (copied), n, Peak memory, Bytes / element, Log-log slope | Measured class, Verdict, Notes |
| 5 | Growth-ratio assertions | same as table 1 | Structure, Backend, Operation, Expected time (copied), Measured ratio, Status | Growth factor (default 4), Bound, Test, Notes |

Rules the script keeps:

- **Table 1 is the master.** Tables 3–5 have exactly its rows, in its order.
  To measure a workload that isn't a method (`drain`, `insert(0, x)`,
  `build`), add a row to table 1 and use the same Operation name in the data.
  Delete a row from table 1 and it disappears from 3–5 on the next run.
- Cells you own are carried over by `(Backend, Operation)` on every run, and
  so are columns you add yourself. Script-owned cells are rewritten.
- Expected time and Expected space are written once, in table 1. Tables 3–5
  copy them.
- Write a literal `|` inside a cell as `\|`.

How a structure is discovered:

- the class is `<Name>` in `dsa/**/<name>.py` (`queue` → `Queue`);
- operations are the public methods and properties the class itself defines,
  plus `__len__`, `__getitem__`, `__setitem__`, `__delitem__`,
  `__contains__` and `__iter__`;
- backends are the keys of `BACKENDS` in `tests/**/<name>_backends.py`. A
  structure without that file gets the single backend `—`.

## Commands

| Task | Command |
|---|---|
| List structures, backends and which have a doc | `uv run python scripts/perf_research.py list` |
| Create `results/<s>/` and the doc | `uv run python scripts/perf_research.py init <s>` |
| Sync rows + refresh measured columns from `data/` | `uv run python scripts/perf_research.py tables <s>` |
| Same, from a specific run | `uv run python scripts/perf_research.py tables <s> --run-id <id>` |
| Full scaffold incl. exercises (agent) | `/perf-research <s>` |
| (Re)write the exercises only (agent) | `/perf-research exercises <s>` |

`/perf-research` runs the `perf-scaffolder` agent
(`.claude/agents/perf-scaffolder.md`). The agent runs the script and writes
the exercises with the `perf-exercises` skill. It asks the questions and never
answers them.

## Data contract

`tables` reads every `*.csv` under `results/<structure>/data/`, one row per
trial in long ("tidy") format, the Phase 4 schema of
`docs/performance-testing-workflow.md`. A file without the required columns is
skipped with a warning.

| Column | Required | Meaning |
|---|---|---|
| `backend` | yes | key of `BACKENDS`; `—`, `-` or empty for a structure without backends |
| `operation` | yes | the Operation cell of table 1 (backticks ignored) |
| `n` | yes | structure size when the operation runs |
| `metric` | yes | `seconds` or `peak_bytes`; other metrics are ignored |
| `value` | yes | `seconds`: wall time of the timed region. `peak_bytes`: `tracemalloc` peak |
| `ops` | no | calls inside the timed region (default 1). `seconds` is divided by it, so the tables always show time **per call** |
| `run_id` | no | `tables` uses only the newest `run_id` (by sort order) unless `--run-id` is given. Runs are never pooled |
| `trial`, `structure`, `workload`, `seed` | no | not read by `tables`; keep them for your own statistics |

What the measured columns are:

- **Median time / call**: median over trials at each n, shown at the
  smallest → largest n.
- **Log-log slope**: least-squares slope of log(median) against log(n). About
  0 means O(1), about 1 means O(n), about 2 means O(n²) per call.
- **Bytes / element**: least-squares slope of median peak bytes against n.
- **Measured ratio**: median per call at the largest n divided by the median
  at n / growth. It is "—" when no pair of sizes is exactly that factor apart,
  so collect geometric sizes.
- **Status**: `pass` if measured ratio < the first number in Bound, else
  `fail`. It stays blank until you set a Bound.

These are deliberately only descriptive numbers. Confidence intervals, model
comparison and the verdict are Phase 5 work: yours.
