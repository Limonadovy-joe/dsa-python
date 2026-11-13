# Skill: Create a Linear ticket

## When to use
When the user asks to create an issue/ticket in Linear for the DSA project.

## Steps

1. Determine the **Type** label from the request (Implementation, Experiment, Benchmark, Analysis, Writing, Literature, Bug, Refactor, Tooling, Visualization).
2. Pick the matching template from `.linear/templates/`:
   - Implementation → `implementation.md`
   - Experiment or Benchmark → `experiment.md`
   - Analysis → `analysis.md`
   - Writing → `writing.md`
   - Literature → `literature.md`
   - Bug → `bug.md`
   - Refactor, Tooling → `implementation.md` (adapt headings)
   - Visualization → `experiment.md` (adapt headings)
   - Unclear → `spike.md`
3. Read the template, fill it in with details from the user's request.
   - **`## Acceptance criteria` is mandatory.** Replace every placeholder with
     ticket-specific criteria: observable, testable (input/state → action →
     expected result), naming the edge cases and the exceptions raised. Delete
     placeholders that don't apply; never leave `<...>` in the ticket. Don't
     repeat Definition-of-done items as criteria. Rules: `docs/definition-of-done.md`.
   - Keep the template's `## Definition of done` checklist **as is**.
   - Refactor/Tooling/Visualization adapting another template: keep its
     Acceptance criteria and Definition of done sections.
4. Choose labels:
   - **Type:** exactly one (from step 1)
   - **Area:** one if applicable (Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Heaps, Hashing, Sorting/Searching, Dynamic Programming, Greedy, Backtracking)
   - **Component:** one (Core, Tests, Benchmarks, Notebooks, Report, Infra)
   - **Agent:** `agent-ready` if spec is complete and mechanical **and** every acceptance criterion is testable; `needs-human` if it requires judgment or you could not write testable criteria (say which are missing)
   - **Flag:** only if needed (Blocked, Needs-supervisor, Reproducibility)
5. Assign to the correct **milestone** based on the work phase.
6. Create the issue with `save_issue`:
   - `team`: `DSA`
   - `project`: `DSA Research`
   - `milestone`: the chosen milestone name
   - `labels`: array of label names
   - `state`: `Backlog` (default) or `Todo` if urgent
   - `priority`: 0–4 (0=None, 1=Urgent, 2=High, 3=Medium, 4=Low)
7. Report the issue ID and URL to the user, with its acceptance criteria.
