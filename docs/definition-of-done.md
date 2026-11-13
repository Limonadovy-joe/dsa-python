# Acceptance criteria and Definition of Done

Every Linear ticket answers two questions:

| | Acceptance criteria (AC) | Definition of Done (DoD) |
|---|---|---|
| Answers | *What* must this ticket achieve? | *How well* must any ticket be finished? |
| Scope | Specific to one ticket | The same for every ticket of a kind |
| Written by | Whoever creates the ticket | This file. Tickets copy the checklist |
| Checked by | Tests (code) or the human (docs) | Gate, CI, reviewer, human |

A ticket is **done** when every AC is met **and** every DoD item is ticked.
Only the human moves it to Done (see `CLAUDE.md`, Workflow rules).

## Acceptance criteria: required on every ticket

- Every ticket has a `## Acceptance criteria` section with at least one item,
  every template included (spikes too: the criterion is the question answered).
- Each criterion is **observable and testable**: an input/state, an action and
  an expected result. For code tickets each one maps to at least one test.
  - Good: `Deque.pop_front()` on an empty deque raises `IndexError`.
  - Good: `DynamicArray.append` is amortised O(1); capacity doubles at `size == capacity`.
  - Bad: "deque works", "handle edge cases", "clean code". These are
    either untestable or already covered by the DoD.
- Name the edge cases explicitly: empty, single element, resize/boundary,
  negative or out-of-range index, invalid input, and the exception raised.
- Complexity targets are criteria: state time and space per operation.
- Don't repeat DoD items (gate, exports) as criteria.
- Can't write testable criteria? The spec isn't ready: label the ticket
  `needs-human`, never `agent-ready`.

## Definition of Done: code tickets

Applies to Implementation, Bug, Refactor, Tooling, Experiment, Benchmark and
Visualization tickets.

- [ ] **Tests per AC**: each acceptance criterion has a test, edge cases
      included (empty, single, boundary, out-of-range, error path with
      `pytest.raises`). Bugs: a regression test that failed before the fix.
- [ ] **CI green**: tests (unit + integration), `ruff format`, `ruff check`,
      `mypy --strict`, pre-commit hooks and the coverage gate, on every OS ×
      Python in `.github/workflows/ci.yml`.
- [ ] **Docs**: `docs/gotchas.md` updated if the behaviour is surprising; new
      public names exported in the topic `__all__`. Docstrings are not
      required (`docs/conventions.md`).
- [ ] **TODOs**: TODOs this ticket resolves are deleted; any TODO it leaves or
      adds carries a ticket ID (`# TODO(DSA-<n>): …`, see
      `.claude/skills/todo-format/SKILL.md`).
- [ ] **Conventional commit referencing the ticket**: `fix(deque): …` with the
      footer `Refs: DSA-<n>`, on a branch `<type>/DSA-<n>-<desc>`, with no
      `Co-Authored-By` trailer.
- [ ] **Reviewed**: `dsa-reviewer` gave `VERDICT: approve` (agent flow) or a
      human approved the PR.
- [ ] **Merged to `main`** through a PR. A human does the merge.

## Definition of Done: docs tickets

Applies to Analysis, Writing and Literature tickets. These do not go through
the implementer/reviewer agents.

- [ ] Every acceptance criterion met; the human has checked the content.
- [ ] Sources cited (BibTeX key added if it's new).
- [ ] Proofread; consistent with the rest of `report/` and `docs/`.
- [ ] Conventional commit referencing the ticket (`docs(report): …`,
      `Refs: DSA-<n>`), merged to `main` through a PR.

## Who checks what

| Step | Checks |
|---|---|
| `linear-ticket` skill / `linear-ticket-creator` | The ticket has testable AC and the DoD checklist |
| `/linear-work` step 1 | Stops if the ticket has no AC |
| `dsa-implementer` | Writes a test per AC; the handoff note maps AC → test |
| `dsa-reviewer` | An AC with no test, or failing, is `must-fix` |
| PR body | AC and DoD checklists, ticked |
| Human | Merges, then moves the ticket to Done |
