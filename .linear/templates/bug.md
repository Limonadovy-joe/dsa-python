# Bug

## Expected vs. actual
- **Expected:**
- **Actual:**

## Minimal reproduction
```python
# Steps to reproduce
```

## Environment
- Python version:
- OS:
- Relevant dependencies:

## Suspected cause
<!-- Your hypothesis about what's wrong -->

## Acceptance criteria
<!-- Required. Ticket-specific, observable, testable: input/state → action → expected result.
     Each one becomes at least one test. Do not repeat Definition-of-done items here.
     Rules: docs/definition-of-done.md -->
- [ ] The reproduction above gives the expected result (regression test fails before the fix, passes after)
- [ ] <Neighbouring cases that must also hold, e.g. empty / single / boundary>
- [ ] <Behaviour that must NOT change>

## Definition of done
<!-- Copied from docs/definition-of-done.md (code tickets). Do not edit per ticket. -->
- [ ] Tests for each acceptance criterion, edge cases included
- [ ] CI green: tests, ruff format, ruff check, mypy --strict, pre-commit, coverage gate
- [ ] `docs/gotchas.md` updated if behaviour is surprising; new public names in `__all__`
- [ ] Resolved TODOs removed; any TODO left carries a ticket ID (`TODO(DSA-<n>)`)
- [ ] Conventional commit referencing the ticket (`<type>(<scope>): …` + `Refs: DSA-<n>`)
- [ ] Reviewed (dsa-reviewer approve or human PR approval)
- [ ] Merged to `main`
