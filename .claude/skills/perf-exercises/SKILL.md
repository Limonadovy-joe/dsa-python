---
name: perf-exercises
description: >-
  Write the "Exercises" section of a performance research doc
  (results/<structure>/report/<structure>.md): four blocks (operations,
  backend differences, amortised vs worst case, structure-specific), at most
  four questions each, tailored to the structure. Questions only, never
  answers. Use when the
  perf-scaffolder agent runs, for /perf-research exercises <structure>, or when
  asked to (re)write performance exercises for a data structure.
---

# Performance exercises

The research doc is a learning exercise. The human predicts each cost, points
at the line of code that causes it, and only then measures. Your job is to ask
good questions. **You never answer them.**

## Inputs

1. The doc `results/<structure>/report/<structure>.md`. If it is missing, run
   `uv run python scripts/perf_research.py init <structure>` first.
2. The rows of table 1 (between `<!-- perf:table:operations -->` and
   `<!-- perf:end -->`), including rows the human added by hand (`drain`,
   `insert(0, x)`, `build` …). They are the pool you pick questions from.
3. The code, read in full before writing:
   - the class module (the `Class` line of the doc's header table),
   - every backend adapter it delegates to, and the lower-level structure
     each adapter wraps (e.g. `QueueLinkedList` → `LinkedList`),
   - the backends file (`tests/**/<structure>_backends.py`), if any,
   - any perf test under `tests/**/perf*/` for this structure.

   Follow each operation's call path to the bottom (public method → adapter
   method → wrapped structure method). You need the real cost of every row to
   ask a question that lands on it. Write that cost nowhere.

## Where to write

Replace only the text between `<!-- perf:exercises -->` and its
`<!-- perf:end -->`. Touch nothing else in the doc: not the tables, not the
Expected columns, not the human's notes.

- If the section holds only the placeholder (`_Not written yet …_`), or
  questions whose blanks (`- Time:`, `- Line:`, `- Answer:` …) are all still
  empty, write it in full (replacing any old questions).
- If any blank has an answer, the human has started. Change nothing; report
  that the section is in use and stop. Only an explicit request from the human
  to rewrite it overrides this.

## Shape of the section

Exactly four blocks, in this order, each with **at most four questions**
(fewer if the structure doesn't give four good ones; never pad). That is 16
questions at most. Number questions continuously (Q1…Q16) so they can be
referenced. Use exactly this skeleton. Headings are `###` because the section
itself is `##`.

```markdown
Every row of table 1 still gets its Big-O there (Expected time / Expected
space). These questions are the rows worth reasoning through in writing. Cite
lines as `path:line`. If you can't point to the line, you don't know it yet.

### A. Operations: Big-O and the reason

**Q1. `list` · `dequeue`.** <tailored question>
- Time:
- Space:
- Line:
- Reason:

**Q2. …** (≤ 4 in this block)

### B. Which rows differ between backends?

**Q5. …** <tailored question>
- Answer:

### C. Amortised vs worst case

**Q9. …** <tailored question>
- Answer:

### D. <Structure>-specific

**Q13. …** <tailored question>
- Answer:
```

Numbering continues across blocks: if A has three questions, B starts at Q4.

## Writing the questions

### A: operations (≤ 4)

Pick the rows with the most to learn, not the trivial ones. Prefer, in order:
rows whose cost hides behind delegation (public method → adapter → wrapped
structure), rows where the same operation runs on different mechanisms per
backend, rows with a cost that isn't obvious from the method name (a count
recomputed, a result built), and hand-added workload rows. One question may
cover a row on two backends ("`dequeue` on `list` and on `linked_list`") when
the contrast is the point. Each question asks for the Big-O and the reason
(the line) and points the reader at the **mechanism** to inspect. It must not
reveal the cost.

- Name the call path, so the reader knows where to look:
  "`Queue.dequeue` hands off to `QueueList.remove_from_front`. What does the
  `list` method it calls do to the elements that stay?"
- Ask about the thing that decides the cost: what moves, what is walked, what
  is allocated, what happens when capacity runs out, whether a count is stored
  or recomputed.
- Space means **auxiliary** space of the call. Where a call builds a result
  (`to_string`, `to_array`, a copy), ask what it allocates.

**Forbidden in any question or hint** (this is the whole point):
- the complexity class, or any wording that implies it: "constant", "linear",
  "quadratic", "cheap", "expensive", "slow", "fast", "O(…)";
- the answer-bearing verb, when it *is* the answer: "shifts every element",
  "walks to the tail", "copies the buffer". Ask "what happens to …" instead;
- line numbers, or quoting the costly line;
- filling any Time/Space/Line/Reason blank, or any table cell.

Pointing at a method or file is fine. Pointing at the line is the human's job.

### B: backends (≤ 4)

- Don't repeat a contrast already asked in A; go wider (plots, factors, what
  the benchmark will and won't show).
- **Two or more backends**: frame it around the rows where the backends use
  different mechanisms for the same operation. Ask the human to predict which
  backend wins and roughly by what factor at n = 10⁴, and which rows will look
  identical on a plot even though the code differs (constant factors, cache
  locality). Don't say which rows differ. Ask them to find out.
- **One backend** (`—`): there is no head-to-head, so compare the structure
  against something meaningful. Use the Python built-in that does the same job
  (`list` for `DynamicArray`, `collections.deque` for a deque). It's fine as a
  benchmark oracle, never inside `dsa/`. Or compare two operations of the same
  structure that look symmetric but may not be (`append` vs `prepend`,
  `delete_head` vs `delete_tail`, `insert` at 0 vs at the end).

### C: amortised vs worst case (≤ 4)

- **Structures that resize** (dynamic arrays, circular buffers with growth):
  ask when the expensive call happens, how often, what the growth policy is,
  and what per-operation timing would look like across a resize boundary.
- **Structures that never resize** (linked structures, fixed-capacity
  buffers): say so as a question ("is there any call whose cost depends on the
  history of earlier calls?"). Then move to **state-dependent** cost: best vs
  worst case driven by the *position* of the item (`search`, `find`,
  `delete(value)`), by fullness (`is_full` before `enqueue`), or by a value
  that is recomputed rather than stored. Ask which rows have a best case that
  differs from the worst, and what input produces each.

### D: structure-specific (≤ 4)

Built from what you actually saw in the code. Good sources:
- an operation used *inside* a benchmark loop whose own cost changes the
  benchmark's total (e.g. a loop condition calling `is_empty()`). Ask for the
  total cost of the loop *using their answers from A*;
- a perf test and its markers or bounds (e.g. a `known_bug` marker: where it
  is defined, and what it does to that backend's run);
- memory per element: node object vs a buffer slot, and how to estimate it
  with `tracemalloc` at two sizes;
- behaviour at the edges (empty, full, wrap-around, capacity boundary) that
  the timing harness must cover or exclude.

Never invent behaviour. Every question must be answerable from code that
exists today. If the module has a TODO or a known bug that affects a cost, you
may ask the human to find its effect, without stating it.

## Final message

Report: the doc path, how many questions were written per block (A/B/C/D, each ≤ 4),
which table-1 rows A covers, and anything in the code that blocked a question
(e.g. a method that can't be followed). No answers, not even in the report.
