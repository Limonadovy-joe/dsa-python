# Performance testing workflow

A step-by-step path from "I have structures and unit tests" to "I have data,
statistics and graphs that show whether each implementation matches its Big-O".

This file is **tasks and exercises only** — no implementation. The reference
material (timing snippets, CSV and plotting sketches) lives in
`docs/performance-testing.md`; read it first.

Each phase has:

- **Goal** — what the phase produces.
- **Tasks** — concrete things to build or decide. Tick them off.
- **Exercises** — questions to answer or small experiments to run *before*
  or *while* doing the tasks. Write your answers down (in the ticket or in
  `report/notes.md`); several later phases depend on them.
- **Done when** — the exit check for the phase.

Phases are ordered by dependency. Don't start a phase before the previous
one's "done when" holds.

---

## Phase 0 — Audit what you have

**Goal:** an inventory of every structure, backend and operation you will
measure, and a clean place for performance code to live.

### Tasks

- [ ] List every public structure in `dsa/` and every backend registered in a
      `BACKENDS` dict under `tests/` (today: `Queue` ×2, `Deque` ×1,
      `CircularArray` ×1, plus `DynamicArray`, `LinkedList`,
      `DoublyLinkedList` with no backend dict yet).
- [ ] Fill in the **operation table** below for every structure. Leave
      "Expected" as your own prediction — you will check it against data in
      Phase 5.
- [ ] Unify the performance folder name. `tests/queues/queue/performance/`
      and `tests/queues/deque/perf/` disagree; pick one and update
      `docs/performance-testing.md` to match.
- [ ] Decide whether structures without a `BACKENDS` dict (`DynamicArray`,
      `LinkedList`, `DoublyLinkedList`) get one. A single-entry dict is fine —
      it keeps the benchmark scripts uniform.
- [ ] Decide where outputs go. `CLAUDE.md` names `results/` and `report/`;
      `docs/performance-testing.md` uses `docs/benchmarks/`. Pick one layout,
      write it down, and fix the other doc.
- [ ] Decide what is committed: raw data? only plots? neither? Add the
      matching `.gitignore` entries.

### Operation table (fill in)

| Structure | Backend | Operation | Expected time | Expected space | Notes |
|---|---|---|---|---|---|
| Queue | list | enqueue | ? | ? | |
| Queue | list | dequeue | ? | ? | `list.pop(0)` |
| Queue | linked_list | enqueue | ? | ? | |
| Queue | linked_list | dequeue | ? | ? | |
| Deque | doubly_linked_list | add/remove front/back | ? | ? | |
| CircularArray | circular_array | enqueue / dequeue | ? | ? | crosses capacity? |
| DynamicArray | — | append | ? (amortised) | ? | resize policy |
| DynamicArray | — | insert at 0 / middle | ? | ? | |
| DynamicArray | — | get by index | ? | ? | |
| LinkedList | — | append / prepend | ? | ? | tail pointer? |
| LinkedList | — | find / delete | ? | ? | |
| LinkedList | — | reverse | ? | ? | |
| DoublyLinkedList | — | same as above | ? | ? | |

### Exercises

1. For each row, write the Big-O **and the reason** (which line of code makes
   it that cost). If you can't point to the line, you don't know it yet.
2. Which rows do you expect to *differ between backends*? Those are the
   head-to-head comparisons worth plotting.
3. Which rows have an **amortised** cost that differs from the worst case?
   Those need per-operation timing (Phase 2), not just totals.
4. `test_queue_performance.py` uses a `known_bug` marker. Find where it is
   defined and explain what it does to the `list` backend run.

### Done when

The table is complete, folder names agree, and the output location is written
down in one place.

---

## Phase 1 — Control the environment

**Goal:** know how noisy your machine is before trusting any number it gives.

### Tasks

- [ ] Write down the machine profile you will record with every run:
      CPU model, core count, OS, Python version and implementation, power
      plan, git commit SHA, whether the tree was dirty.
- [ ] Decide a "benchmark hygiene" checklist: plugged in, high-performance
      power plan, browser/IDE indexing closed, same terminal, no other
      `uv run` in parallel.
- [ ] Run one fixed benchmark (e.g. drain 10 000 items from the linked-list
      queue) 30 times in a row and keep every timing.

### Exercises

1. From those 30 timings compute min, median, mean, max and the
   **coefficient of variation** (stdev / mean). Is CV below 5 %? Below 1 %?
2. Plot the 30 timings in run order. Is there a trend (warm-up, thermal
   throttling) or just scatter?
3. Repeat with the IDE indexing / a video playing. How much does CV move?
   That is your noise floor — any backend difference smaller than it is not
   a finding.
4. Explain in two sentences why `docs/performance-testing.md` recommends
   best-of-N, and name one situation where **median** is the better summary.
5. Why `time.perf_counter()` (or `perf_counter_ns()`) and not `time.time()`?
   What is the resolution of `perf_counter` on Windows? (Hint:
   `time.get_clock_info("perf_counter")`.)

### Done when

You have a number for your machine's noise floor and a written hygiene
checklist.

---

## Phase 2 — Design the measurement harness

**Goal:** one small, reusable harness that every benchmark goes through, so
all data is measured the same way.

### Tasks

- [ ] Decide where the harness lives (e.g. `benchmarks/` or `scripts/`) and
      whether it is type-checked. `[tool.mypy] files` currently covers only
      `dsa` and `tests` — extend it or justify not doing so.
- [ ] Specify the harness's inputs: structure factory, operation, input size
      `n`, number of trials, number of warm-up runs, workload/seed.
- [ ] Specify its outputs: one record **per trial** (not per size) — see the
      schema in Phase 4.
- [ ] Decide how **setup** is excluded from the timed region (building a
      queue of `n` items must not count as `dequeue` time).
- [ ] Decide what happens to the garbage collector during timing
      (`gc.disable()` / `gc.collect()` between trials) and document why.
- [ ] Add a **memory** mode using `tracemalloc` that records peak bytes for
      building a structure of size `n`.
- [ ] Add a **per-operation** mode that records the time of each individual
      call (for amortised analysis) instead of one total.

### Exercises

1. Time a single `enqueue` with `perf_counter`. Then time 1 000 enqueues and
   divide. Why are the two answers different, and which one is meaningful?
2. Compare your harness against the standard library `timeit` module for the
   same operation. Where do they agree? What does `timeit` do by default that
   you had to do by hand?
3. Run the drain benchmark with and without `gc.disable()`. Does the linked
   list (many small objects) change more than the list backend? Why?
4. `tracemalloc` itself slows code down. Why must time and memory be measured
   in **separate** runs?
5. What is the smallest `n` at which the timed region is at least ~1000× the
   timer resolution from Phase 1? Sizes below that are noise.

### Done when

The harness spec (inputs, outputs, setup exclusion, gc policy, modes) is
written down and reviewed, and every later benchmark can be expressed through
it.

---

## Phase 3 — Growth-ratio tests in pytest

**Goal:** fast pass/fail checks that catch a complexity regression, separate
from the data collection used for plots.

### Tasks

- [ ] Extend the existing ratio test pattern to every row of the Phase 0
      table where a regression would matter: deque ends, circular array
      enqueue/dequeue across a capacity boundary, dynamic array append,
      linked list append (does it have a tail pointer?), reverse.
- [ ] Each test: `pytestmark = pytest.mark.performance`, uses the existing
      `make_<topic>` fixture, asserts a **ratio**, never an absolute time.
- [ ] Put every magic number (`_SIZE`, `_GROWTH`, bound) in a named module
      constant with a one-line comment deriving the bound, like the queue test.
- [ ] Mark backends that are *expected* to fail (e.g. `list` dequeue) the same
      way the queue test does, instead of loosening the bound.
- [ ] Run `uv run pytest -m performance` five times. Record any flaky test.

### Exercises

1. For growth factor 4, what ratio do O(1)-per-op, O(log n)-per-op and
   O(n)-per-op give for the **total** time of `n` operations? Choose a bound
   that separates the expected class from the next worse one, and write the
   arithmetic in the comment.
2. Why is a growth factor of 2 a worse choice than 4 or 8 on a noisy machine?
3. Make a test flaky on purpose (tiny `_SIZE`). What is the smallest size at
   which it is stable across 10 runs?
4. Why does CI skip these tests (see `docs/architecture.md`)? Would they
   become CI-safe with a larger bound? What would that cost?

### Done when

Every important operation has a ratio test, `uv run pytest -m performance`
passes five times in a row, and the full gate is still green.

---

## Phase 4 — Collect data into a dataset

**Goal:** raw, tidy, reproducible datasets on disk that every later phase reads
from, without re-running benchmarks.

### Tasks

- [ ] Fix a **schema** — one row per trial, long ("tidy") format. Suggested
      columns (adjust and justify):

      | column | example |
      |---|---|
      | `run_id` | timestamp or UUID of this collection run |
      | `structure` | `Queue` |
      | `backend` | `linked_list` |
      | `operation` | `dequeue` |
      | `workload` | `drain`, `mixed`, `random` |
      | `n` | `10000` |
      | `trial` | `0..k-1` |
      | `metric` | `seconds` or `peak_bytes` |
      | `value` | `0.00412` |
      | `seed` | `42` |

- [ ] Store run metadata (machine profile from Phase 1, git SHA, Python
      version, date, harness parameters) **once per run**, alongside the data
      — not repeated in every row.
- [ ] Pick a file format. Compare CSV, JSON Lines and Parquet on: readable in
      a diff, appendable, typed columns, needs an extra dependency. Write the
      choice and the reason down.
- [ ] Pick a naming scheme so runs never overwrite each other (e.g.
      `results/<structure>/<operation>/<run_id>.csv` + `<run_id>.meta.json`).
- [ ] Choose **sizes**: geometrically spaced (e.g. powers of 2 or a
      1-2-5 sequence) from the Phase 2 minimum up to where the slowest backend
      takes a few seconds per trial.
- [ ] Choose the **order** of execution: interleave backends and sizes
      (shuffled with a fixed seed) instead of running all of backend A then all
      of backend B.
- [ ] Write the collection entry point(s) — one command per structure, plus
      one that runs everything. Add the command to the table in
      `docs/architecture.md`.
- [ ] Collect a full dataset for `Queue` first. Only then the others.

### Exercises

1. Why one row per **trial** rather than one row per size with the best time
   already chosen? Name a statistic from Phase 5 that you could not compute
   otherwise.
2. Why does interleaving the run order matter? Construct a scenario (thermal
   throttling, a background update starting halfway) where sequential order
   makes one backend look slower than it is.
3. Why geometric spacing instead of `range(1_000, 100_001, 1_000)`? Think
   about what the log-log plot in Phase 6 needs.
4. The quadratic `list` dequeue becomes unbearably slow before the others.
   How should the collector cap it — per-backend max `n`, or a time budget per
   cell? What does each choice do to the plots?
5. Re-run the same collection twice. Load both and compare the medians per
   `(backend, n)`. How close are they? This is your reproducibility check.

### Done when

At least one complete `Queue` dataset with metadata exists on disk, a second
run reproduces it within the Phase 1 noise floor, and the schema is written
down.

---

## Phase 5 — Statistics

**Goal:** turn raw trials into numbers that answer "which complexity class?"
and "which backend is faster, by how much, and how sure are we?".

### Libraries — decide first

- [ ] Standard library `statistics` covers mean, median, stdev, quantiles,
      `linear_regression`. Decide whether it is enough.
- [ ] `pandas` is already installed transitively through `seaborn`. Decide
      whether to add it as an explicit dev dependency
      (`uv add --dev pandas`) rather than relying on that.
- [ ] Decide whether you need `numpy` (log fits, arrays) and/or `scipy`
      (`scipy.stats` for bootstrap, Mann–Whitney U, curve fitting).
- [ ] All of these are **dev-only**. Confirm `dsa/` still has zero runtime
      dependencies.

### Tasks

- [ ] **Descriptive summary** per `(structure, backend, operation, n)`:
      count, min, median, mean, stdev, IQR, CV.
- [ ] **Outlier policy**: decide (and document) whether you drop anything,
      e.g. trials above Q3 + 1.5·IQR. Report how many were dropped.
- [ ] **Confidence intervals** for the median via bootstrap resampling.
- [ ] **Empirical Big-O via log-log regression**: fit
      `log(time) = a + b·log(n)` per backend; the slope `b` estimates the
      exponent. Report `b` with its CI.
- [ ] **Model comparison**: for each backend, fit `time ≈ c·f(n)` for
      candidate `f` ∈ {1, log n, n, n log n, n²} and rank by residual error
      (or R²). Report the winner.
- [ ] **Normalised cost**: compute `time / n` (cost per operation) per size.
      For an O(1)-per-op operation it should be flat.
- [ ] **Backend comparison**: speed-up ratio of backend A over B per `n`, with
      a CI; optionally a Mann–Whitney U test for "is the difference real".
- [ ] **Amortised analysis** (dynamic array, circular array): from
      per-operation timings, compute the share of "slow" operations and check
      their indices against your resize policy.
- [ ] **Memory**: bytes per element = slope of `peak_bytes` vs `n`.
- [ ] Write every summary to a derived file next to the raw data (never
      overwrite raw data).

### Exercises

1. Fit the log-log slope for queue `dequeue` (drain total time). Predict the
   slope for each backend **before** fitting, then compare. If `list` comes
   out at 1.7 instead of 2.0, explain why (hint: small-`n` constant costs,
   `memmove` being very fast C code).
2. Fit only the largest half of the sizes. Does the slope move toward the
   theoretical value? What does that tell you about where asymptotics kick in?
3. Why does the model comparison need **all trials** (or at least the
   spread), and not just one number per `n`, to say "n² beats n log n"
   honestly?
4. Compute bytes-per-element for the list and linked-list queue backends.
   Compare with `sys.getsizeof` of a node object plus its value. Explain the
   gap.
5. For the dynamic array, predict at which indices `append` is slow, then
   check the data. Do the spikes appear exactly at powers of two? If not,
   why?
6. Your two backends differ by 3 % at `n = 1 000`. Is that a finding? Use the
   Phase 1 noise floor and the CI to answer.

### Done when

Every operation in the Phase 0 table has a fitted slope, a winning model and
a CI, and you have written a one-line verdict per row: **"matches expected"**
or **"does not match, because …"**.

---

## Phase 6 — Graphs

**Goal:** a small, consistent set of figures that make each verdict from
Phase 5 obvious at a glance.

### Libraries

`matplotlib` and `seaborn` are already dev dependencies. Use seaborn for
statistical plots over the tidy data and matplotlib for fine control (axes,
reference lines, saving).

### Tasks

- [ ] Agree on a **plot style** once: theme, figure size, font size, one
      fixed colour per backend (same colour in every figure), DPI, file format
      (PNG for docs, SVG/PDF for the report).
- [ ] Build these figure types, each reading only from the datasets of
      Phase 4/5:
  - [ ] **Time vs n** (linear axes), one line per backend, median with a CI
        band.
  - [ ] **Log-log time vs n**, with dashed reference lines for O(1), O(n),
        O(n log n), O(n²) anchored at the smallest `n`. Annotate the fitted
        slope in the legend.
  - [ ] **Normalised cost** `time / n` vs `n` (log x-axis). Flat = constant
        per op.
  - [ ] **Trial distribution** per `(backend, n)` as a box or violin plot —
        shows noise and outliers.
  - [ ] **Per-operation scatter** for amortised structures: x = operation
        index, y = time; mark resize points.
  - [ ] **Memory** bytes vs `n` per backend, plus a bar chart of
        bytes-per-element.
  - [ ] **Speed-up ratio** backend A / backend B vs `n`, with a horizontal
        line at 1.
- [ ] Every figure: title says *what* and *which operation*; axis labels have
      **units**; no chart without a caption sentence stating the takeaway.
- [ ] Save figures deterministically (same input → same file name) into the
      output folder decided in Phase 0.

### Exercises

1. Plot queue `dequeue` on linear axes and on log-log axes. Which one makes
   "the list backend is quadratic" obvious? Which one hides it?
2. Why should reference lines be anchored at the smallest `n` rather than
   the largest? Try both.
3. Draw the normalised-cost plot for the dynamic array `append`. Explain
   every bump.
4. Show the box plot to someone without context. Can they tell which backend
   is noisier? If not, what would you change?
5. Change the backend colour mapping between two figures and see how much
   harder comparing becomes. Then fix it centrally.

### Done when

Each verdict from Phase 5 has at least one figure that supports it, and all
figures share one style.

---

## Phase 7 — Report

**Goal:** a written result someone else can read, check and reproduce.

### Tasks

- [ ] One section per structure in `report/` (or the location from Phase 0):
      the operation table with **expected vs measured**, the key figures, the
      fitted slopes with CIs, and the verdict.
- [ ] A "Method" section: harness design, hygiene checklist, sizes, trials,
      outlier policy, statistics used — linking to this file rather than
      repeating it.
- [ ] A "Threats to validity" section: interpreter overhead, noise floor,
      single machine, `tracemalloc` scope, small-`n` effects.
- [ ] A "Reproduce" section: the exact commands, and the `run_id` of the
      dataset each figure came from.

### Exercises

1. For every claim in the report, point to the figure or number that backs
   it. Delete claims you can't back.
2. Hand the reproduce section to a fresh clone (or a teammate). Does it work
   without asking you anything?
3. Which result surprised you most? Write one paragraph on why, connecting it
   to the code.

### Done when

The report is written, every claim is backed by data, and the reproduce
steps work from a clean checkout.

---

## Phase 8 — Automate and keep it alive

**Goal:** performance work keeps working as new structures land.

### Tasks

- [ ] One command runs the pipeline end to end: collect → summarise → plot.
      Each stage can also run alone (re-plot without re-measuring).
- [ ] Adding a backend to a `BACKENDS` dict automatically includes it in
      collection, statistics and plots — verify by adding a dummy backend.
- [ ] Add a "performance" step to the new-structure checklist (scaffold skill,
      `docs/conventions.md`): ratio test + dataset + figure + report section.
- [ ] Decide how to detect regressions over time: compare a new run's fitted
      slopes against the last committed run and flag changes beyond the CI.

### Exercises

1. Implement `CircularArray` as a `Deque` backend (once it is ready) and run
   the whole pipeline without touching any benchmark code. What broke?
2. Introduce a deliberate regression (e.g. make `LinkedList.append` walk to
   the tail). Which stage catches it first — the ratio test, the slope fit,
   or the plot?

### Done when

A new backend appears in tests, data, statistics and figures by editing only
its `BACKENDS` dict.

---

## Suggested Linear breakdown

One ticket per phase (or per phase × structure for Phases 4–6), using the
labels from `CLAUDE.md`:

| Phase | Type | Component | Agent |
|---|---|---|---|
| 0 Audit | Analysis | Tests | needs-human |
| 1 Environment | Experiment | Benchmarks | needs-human |
| 2 Harness | Tooling | Benchmarks | agent-ready (after spec) |
| 3 Ratio tests | Benchmark | Tests | agent-ready |
| 4 Datasets | Benchmark | Benchmarks | agent-ready |
| 5 Statistics | Analysis | Notebooks | needs-human |
| 6 Graphs | Visualization | Notebooks | agent-ready (after style) |
| 7 Report | Writing | Report | needs-human |
| 8 Automation | Tooling | Infra | agent-ready |

Add the `Reproducibility` flag to Phases 1, 4 and 7.
