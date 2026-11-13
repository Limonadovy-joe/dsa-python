# Experiment / Benchmark

## Hypothesis
<!-- What you expect to observe and why -->

## Independent variables
<!-- e.g. n, key distribution, operation mix -->

## Metrics
<!-- e.g. wall-clock time, memory, comparisons, rotations -->

## Baselines
<!-- What to compare against -->

## Setup
- **Hardware:** <!-- CPU, RAM -->
- **Python version:** 3.13
- **Random seeds:** <!-- list seeds -->
- **Repetitions:** <!-- e.g. 10 -->

## Procedure
1. Step 1
2. Step 2

## Expected outcome
<!-- What the hypothesis predicts -->

## Results
<!-- Filled after run -->
| Config | Metric | Value |
|---|---|---|
| | | |

**Plot path:** `results/plots/...`

## Conclusion
<!-- Did results match hypothesis? Why / why not? -->

## Acceptance criteria
<!-- Required. Ticket-specific, observable, testable: input/state → action → expected result.
     Each one becomes at least one test. Do not repeat Definition-of-done items here.
     Rules: docs/definition-of-done.md -->
- [ ] `uv run pytest benchmarks/<file>` runs end-to-end for n = <sizes> with seeds <seeds>
- [ ] Results for every config saved to `results/<path>`
- [ ] <Plot(s)> generated at `results/plots/<name>` (if applicable)
- [ ] Conclusion states whether the hypothesis held, with the numbers

## Definition of done
<!-- Copied from docs/definition-of-done.md (code tickets). Do not edit per ticket. -->
- [ ] Tests for each acceptance criterion, edge cases included
- [ ] CI green: tests, ruff format, ruff check, mypy --strict, pre-commit, coverage gate
- [ ] `docs/gotchas.md` updated if behaviour is surprising; new public names in `__all__`
- [ ] Resolved TODOs removed; any TODO left carries a ticket ID (`TODO(DSA-<n>)`)
- [ ] Conventional commit referencing the ticket (`<type>(<scope>): …` + `Refs: DSA-<n>`)
- [ ] Reviewed (dsa-reviewer approve or human PR approval)
- [ ] Merged to `main`
