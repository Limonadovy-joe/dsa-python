# Implementation

## Goal
<!-- What this data structure / algorithm does -->

## Public API (signatures)
<!-- List methods with type signatures -->

## Invariants
<!-- Key properties the implementation must maintain -->

## Complexity targets
| Operation | Time (worst) | Time (average) | Time (amortized) | Space |
|---|---|---|---|---|
| | | | | |

## Acceptance criteria
<!-- Required. Ticket-specific, observable, testable: input/state → action → expected result.
     Each one becomes at least one test. Do not repeat Definition-of-done items here.
     Rules: docs/definition-of-done.md -->
- [ ] `<op>(...)` on <state> returns / leaves <expected>
- [ ] Empty: <op> on an empty structure raises `<Error>` (or returns <value>)
- [ ] Single element: <expected behaviour>
- [ ] Boundary / resize: <what happens at capacity, and the complexity>
- [ ] Out-of-range / invalid input: raises `<Error>`
- [ ] Complexity: <op> is <O(..)> time, <O(..)> space, as in the table above
- [ ] Exported as `from dsa.<topic> import <Name>`

## Definition of done
<!-- Copied from docs/definition-of-done.md (code tickets). Do not edit per ticket. -->
- [ ] Tests for each acceptance criterion, edge cases included
- [ ] CI green: tests, ruff format, ruff check, mypy --strict, pre-commit, coverage gate
- [ ] `docs/gotchas.md` updated if behaviour is surprising; new public names in `__all__`
- [ ] Resolved TODOs removed; any TODO left carries a ticket ID (`TODO(DSA-<n>)`)
- [ ] Conventional commit referencing the ticket (`<type>(<scope>): …` + `Refs: DSA-<n>`)
- [ ] Reviewed (dsa-reviewer approve or human PR approval)
- [ ] Merged to `main`

## References
<!-- Papers, textbooks, or links -->
