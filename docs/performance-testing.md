# Performance testing

How to measure, compare, and visualize time/space complexity across backends.

## Architecture: Strategy + Adapter enables backend benchmarking

The data structures in this repo use the **Strategy + Adapter** pattern
(documented in `docs/conventions.md`). Every structure that supports multiple
storage backends exposes a single public class (e.g. `Queue`, `Deque`) that
delegates to a **storage protocol** (`QueueStorage`, `DequeStorage`). Each
concrete backend is an **adapter** that wraps a lower-level data structure
behind that protocol.

This matters for performance testing because:

1. **One test suite, many backends.** The `conftest.py` `BACKENDS` dict maps
   backend names to factory functions. A `make_queue` / `make_deque` fixture
   parametrizes over them. Every performance test automatically runs once per
   backend — no duplication.
2. **Apples-to-apples comparison.** All backends share the exact same API, so
   the benchmark code is identical. The only variable is the storage strategy.
3. **Easy to extend.** Adding a new backend (e.g. `DequeCircularArray`) means
   writing the adapter and adding one entry to `BACKENDS`. All existing tests
   and benchmarks pick it up automatically.

```
Queue (Context)
  ├─ QueueList (Adapter → list)         ← O(n) dequeue
  └─ QueueLinkedList (Adapter → LL)     ← O(1) dequeue

Deque (Context)
  ├─ DequeDoubleLinkedList (Adapter → DLL)  ← O(1) both ends
  └─ DequeCircularArray (Adapter → array)   ← (planned)
```

The benchmark workflow uses this directly: the `BACKENDS` dict feeds both the
perf test assertions (growth-ratio checks) and the data-collection scripts
(CSV output for plotting).

## Goal

Performance tests answer: **does the implementation match the expected
Big-O?** They do this by running the same operation at increasing input sizes,
measuring wall-clock time (and optionally memory), then checking whether the
growth curve matches O(1), O(n), O(n log n), etc.

## How it fits into the repo

```
tests/<topic>/
├── conftest.py              # backend fixture (shared by all test tiers)
├── <topic>_backends.py      # MakeX factory for each backend
├── unit/                    # correctness
├── integration/             # cross-module
└── perf/                    # performance (this guide)
    ├── __init__.py
    └── test_<topic>_perf.py
```

Performance tests reuse the **same `make_<topic>` fixture and backends** as
unit tests. The only additions:

- `pytestmark = pytest.mark.performance` so they are skipped by default
  (`addopts = "-m 'not performance'"` in `pyproject.toml`).
- Run explicitly: `uv run pytest -m performance`.

## Reusing the backend fixture

The `make_queue` / `make_deque` fixture already parametrizes over every
backend in `BACKENDS`. A performance test receives it the same way a unit
test does:

```python
pytestmark = pytest.mark.performance


def test_enqueue_scales_constantly(make_queue: MakeQueue) -> None:
    # runs once per backend (linked_list, list, …)
    ...
```

No extra wiring needed — conftest handles it.

## What to measure

### 1. Time complexity (wall-clock)

Run the operation at several input sizes, record the best-of-N elapsed time,
then check the growth ratio or plot the curve.

```python
import time


def _bench_op(make_queue: MakeQueue, size: int, *, trials: int = 5) -> float:
    """Return best-of-N seconds for draining a queue of *size* items."""
    best = float("inf")
    for _ in range(trials):
        q = make_queue(range(size))
        start = time.perf_counter()
        while not q.is_empty():
            q.dequeue()
        best = min(best, time.perf_counter() - start)
    return best
```

Key points:
- Use `time.perf_counter()`, not `time.time()`.
- **Best-of-N** filters scheduler noise. 3–5 trials is usually enough.
- Warm up once before measuring if the first call has import/allocation overhead.

### 2. Space complexity (peak memory)

`tracemalloc` from the standard library tracks Python-level allocations:

```python
import tracemalloc


def _measure_memory(make_queue: MakeQueue, size: int) -> int:
    """Return peak bytes after building a queue of *size* items."""
    tracemalloc.start()
    q = make_queue(range(size))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak
```

This captures Python object overhead. It does **not** capture C-level
allocations (e.g. numpy internals), but for pure-Python data structures it
is accurate enough.

### 3. Growth-ratio assertions (CI-safe)

Absolute timings are machine-dependent, so assert on **ratios** instead:

```python
_SIZE = 5_000
_GROWTH = 4


def test_dequeue_is_O1(make_queue: MakeQueue) -> None:
    small = _bench_op(make_queue, _SIZE)
    large = _bench_op(make_queue, _SIZE * _GROWTH)
    # O(1) dequeue: 4x items ≈ 4x time.  O(n) dequeue: 4x items ≈ 16x time.
    assert large / small < 8, f"ratio {large / small:.1f}x — expected < 8x"
```

This works on CI shared runners where timings are noisy.

## Collecting data for plotting

For visualization you need a **data-collection script**, not a pytest test.
Put it in `scripts/` so it doesn't run in CI.

```python
# scripts/bench_queue.py
"""Collect timing data for queue backends and save to CSV."""

from __future__ import annotations

import csv
import time
from pathlib import Path

# reuse the same backends as the test suite
from tests.queues.queue.queue_backends import BACKENDS

SIZES = [100, 500, 1_000, 2_500, 5_000, 10_000, 25_000, 50_000]
TRIALS = 5
OUT = Path("docs/benchmarks/queue_dequeue.csv")


def bench_drain(name: str, make_queue, size: int) -> dict:  # noqa: ANN001
    best = float("inf")
    for _ in range(TRIALS):
        q = make_queue(range(size))
        start = time.perf_counter()
        while not q.is_empty():
            q.dequeue()
        best = min(best, time.perf_counter() - start)
    return {"backend": name, "n": size, "seconds": best}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for name, factory in BACKENDS.items():
        for size in SIZES:
            rows.append(bench_drain(name, factory, size))
            print(f"{name:>15}  n={size:>6}  {rows[-1]['seconds']:.6f}s")

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["backend", "n", "seconds"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved → {OUT}")


if __name__ == "__main__":
    main()
```

Run with: `uv run python scripts/bench_queue.py`

## Visualizing with seaborn / matplotlib

```python
# scripts/plot_queue.py
"""Plot queue benchmark results from CSV."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

CSV = Path("docs/benchmarks/queue_dequeue.csv")
OUT_DIR = Path("docs/benchmarks")


def main() -> None:
    df = pd.read_csv(CSV)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 5))

    sns.lineplot(data=df, x="n", y="seconds", hue="backend", marker="o", ax=ax)

    ax.set_title("Queue.dequeue() — time vs input size")
    ax.set_xlabel("n (number of items)")
    ax.set_ylabel("Time (seconds)")

    out = OUT_DIR / "queue_dequeue.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.show()


if __name__ == "__main__":
    main()
```

Run with: `uv run python scripts/plot_queue.py`

### Plotting memory

Same idea — collect peak bytes at each size, save to CSV, plot:

```python
sns.lineplot(data=df, x="n", y="peak_bytes", hue="backend", marker="o")
ax.set_ylabel("Peak memory (bytes)")
```

### Log-scale plots for spotting Big-O

A log-log plot turns power-law curves into straight lines. The **slope**
reveals the exponent: slope 1 = O(n), slope 2 = O(n²), slope 0 = O(1).

```python
ax.set_xscale("log")
ax.set_yscale("log")
```

## Other aspects to benchmark

Beyond raw time and memory, several factors affect real-world performance:

### Cache locality

**What:** CPUs load memory in cache lines (64 bytes). Contiguous storage
(arrays/lists) keeps elements close → fewer cache misses. Pointer-chasing
structures (linked lists, trees) scatter nodes across the heap → more misses.

**How to test:** Compare wall-clock time for a sequential scan over the same
number of elements stored in a list-backed vs linked-list-backed structure.
The list backend will be faster even if both are O(n), because of cache hits.

```python
def test_sequential_scan_cache_effect(make_queue: MakeQueue) -> None:
    """List-backed queue should scan faster due to cache locality."""
    q = make_queue(range(50_000))
    start = time.perf_counter()
    while not q.is_empty():
        q.dequeue()
    elapsed = time.perf_counter() - start
    # Don't assert — just record; the ratio between backends shows the effect.
```

### Amortized cost vs worst-case

**What:** Dynamic arrays double on resize — most appends are O(1), but one
in N is O(n). The **amortized** cost is O(1), but the worst single operation
is expensive.

**How to test:** Record per-operation time (not just total) and check the
distribution — most should be fast, with rare spikes:

```python
times: list[float] = []
q = make_queue(())
for i in range(10_000):
    start = time.perf_counter()
    q.enqueue(i)
    times.append(time.perf_counter() - start)
# Plot as a scatter or histogram to see the spike pattern.
```

### Memory overhead per element

**What:** A Python `list` stores one pointer (8 bytes) per element. A linked
list node stores value + next pointer + Python object header (~56+ bytes).

**How to test:** Use `tracemalloc` at increasing sizes, then compute
`(peak_at_2n - peak_at_n) / n` to estimate bytes per element.

### Throughput under mixed workloads

**What:** Real usage interleaves enqueue and dequeue. Some backends degrade
under mixed patterns (e.g. list-based queue with frequent `pop(0)`).

**How to test:** Alternate enqueue/dequeue in a loop and measure throughput
(ops/sec) at increasing queue depths.

### Resize / growth policy

**What:** Doubling gives amortized O(1) append; growing by a fixed constant
gives O(n). Ring buffers avoid shifting entirely.

**How to test:** Measure append time at sizes that cross resize boundaries
(powers of 2) and check that the average stays flat.

## Summary: the workflow

1. **Write the perf test** in `tests/<topic>/perf/` using the existing
   `make_<topic>` fixture. Assert on growth ratios, not absolute times.
2. **Collect data** with a script in `scripts/` that imports `BACKENDS`
   and writes CSV.
3. **Plot** with a companion script using seaborn/matplotlib.
4. Keep plots in `docs/benchmarks/` for reference.