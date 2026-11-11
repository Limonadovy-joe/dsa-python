# Gotchas

## Repo quirks

- `dsa/` is a real installed package. After adding a **new topic folder**, it needs
  an `__init__.py` or imports silently resolve as a namespace package and editors
  stop autocompleting.
- Run tests with `uv run pytest`, never bare `pytest` — bare `pytest` may hit a
  global interpreter where `dsa` is not installed.
- If `import dsa` fails after a fresh clone: `uv sync`. The editable install is
  what puts the package on the path.
- Windows: paths in tests should come from `pathlib`, never string-joined.

## Python

- Mutable default arguments (`def f(acc=[])`) are shared across calls. Use `None`.
- `[[0] * n] * m` makes `m` references to **one** row. Use
  `[[0] * n for _ in range(m)]` — bites hardest in DP grids.
- Slicing copies: `arr[1:]` inside a recursion turns O(n) into O(n²). Pass
  indices instead.
- Default recursion limit is 1000. Deep trees/DFS need an explicit stack, not
  `setrecursionlimit`.
- `list.pop(0)` is O(n). For a queue, use two stacks or a linked list — and in
  tests, `collections.deque`.
- Integer division: `//` floors toward negative infinity, so `-7 // 2 == -4`.
  Midpoints in binary search want `low + (high - low) // 2`.
- `is` vs `==`: small ints and short strings are interned, so `is` accidentally
  "works" in tests and then fails on real data.
- Dicts preserve insertion order; sets do **not**. Never assert on set iteration
  order.
- `sorted(..., key=...)` is stable — rely on it for multi-key sorts instead of
  sorting twice with a comparator.

## DSA

- Binary search: pick a loop invariant (`[low, high]` vs `[low, high)`) and keep
  it. Most off-by-ones are a mid-loop switch between the two.
- Resize policy matters: doubling gives amortised O(1) append, growing by a
  constant gives O(n).
- Recursive tree code must handle `None` at the top, not at each call site.
- Graph DFS/BFS needs `visited` marked when **enqueued**, not when dequeued, or
  nodes get processed twice.
- DP: write the recurrence and base case in a comment before the loop. The loop
  order has to follow the dependency direction.

## Comparator (`utils/comparator`)

`Comparator.default_compare` is what `LinkedList`, `DoublyLinkedList` and
`Deque` use for `find`/`delete` when no `compare_fun` is passed.

- NaN is equal to NaN and greater than every other `int`/`float`/`bool`,
  including `+inf`. So `find(float("nan"))` finds a NaN node, unlike plain `==`.
- `bool` is a number: `(True, 1)` → `0`, `(False, 0.5)` → `-1`, but
  `(True, "1")` raises.
- Primitives from different families (numbers / `str` / `bytes` / `None`) raise
  `TypeError` naming both types, even where plain `==` would just say `False`:
  `(None, 0)`, `("a", b"a")`, `("1", 1)`. A list holding mixed `str` and `int`
  raises on `find`/`delete` with the default comparator.
- Anything else (lists, tuples, sets, custom objects, and numeric types outside
  `int`/`float`/`bool` such as `Fraction` or `Decimal`) goes through `==`, then
  `<`, then `>`. An unequal pair Python refuses to order (two `object()`s, a
  list and a tuple) raises `TypeError`.
- Partial orders: unequal values where neither `<` nor `>` holds (disjoint
  sets, `[nan]` vs another `[nan]`, `nan` vs `Fraction(1, 2)`) get an arbitrary
  but antisymmetric nonzero order by `id`. `equal` is correctly `False`, but
  never sort by `compare` on such values: the order is meaningless and only
  stable while both objects are alive.
