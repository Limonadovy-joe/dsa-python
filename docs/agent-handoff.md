# Agent handoff: implementer ⇄ reviewer

How code changes move between the `dsa-implementer` and `dsa-reviewer` agents
during `/linear-work`. This file is the contract; the agent definitions in
`.claude/agents/` and the `linear-work` skill follow it.

## Roles

| Role | Who | Can edit | Owns |
|---|---|---|---|
| **Orchestrator** | the main Claude session running `/linear-work` (herdr `impl` pane) | `.handoff/` only | Linear, branch, brief, spawning both agents, the loop, commit, push, PR |
| **Implementer** | `dsa-implementer` subagent (workflow: `dsa-implement` skill) | `dsa/`, `tests/`, `results/`, `.handoff/<id>/impl-*.md` | code + tests for one mode: `feature`, `fix`, `refactor`, `test`, `benchmark` |
| **Reviewer** | `dsa-reviewer` subagent (workflow: `dsa-review` skill; or the herdr `review` pane run as that agent) | nothing (Write/Edit disallowed) | findings + verdict |

Subagents cannot spawn other subagents, so the two agents never talk to each
other directly. The orchestrator carries every message, and every message is
also a file on disk.

## The channel: `.handoff/<DSA-id>/` (gitignored)

Created in the worktree root, next to `dsa/`. Never committed.

| File | Written by | Read by | Content |
|---|---|---|---|
| `brief.md` | orchestrator | implementer | ticket spec, mode, acceptance criteria, files in scope, out of scope |
| `impl-<k>.md` | implementer | reviewer, orchestrator | what changed in round `k` (format below) |
| `review-<k>.md` | orchestrator (verbatim copy of the reviewer's final message) | implementer, orchestrator | findings + `VERDICT:` line |

Why files and not just the agents' final messages:

- The reviewer starts with a **fresh context**. It sees only its prompt, so the
  note tells it what changed, why, and which complexity claims to check.
- The implementer can be **resumed** with its context intact (SendMessage to
  its agent id); if it can't (new session, agent gone), a fresh implementer is
  spawned with `brief.md` + the latest `review-<k>.md` and loses nothing.
- The herdr `review` pane and you can read the same files at any time.

The code itself is not copied: both agents work in the **same worktree**, and
the reviewer reads `git diff origin/main...HEAD` plus `git diff HEAD`
(uncommitted). Nothing is committed during the loop.

## Sequence

```
orchestrator                    implementer                    reviewer
    │ write brief.md                 │                             │
    ├─ Agent(dsa-implementer) ──────▶│ TDD, gate                   │
    │                                │ write impl-1.md             │
    │◀──────── final msg = impl-1 ───┤                             │
    ├─ Agent(dsa-reviewer, "round 1, note impl-1.md") ────────────▶│ read note + diff
    │◀───────────────────────────────── final msg = report+VERDICT ┤
    │ save review-1.md                                             │
    │ VERDICT: changes-requested                                   │
    ├─ SendMessage(implementer, "round 2: fix review-1.md") ▶│     │
    │                                │ fix, gate, impl-2.md        │
    │◀──────── final msg = impl-2 ───┤                             │
    ├─ Agent(dsa-reviewer, "round 2, note impl-2.md, prev review-1.md") ▶│
    │◀───────────────────────────────── VERDICT: approve ──────────┤
    │ save review-2.md → commit, gate, push, PR                    │
```

- **Max 3 review rounds.** Still `changes-requested` after round 3: stop and
  show the human the open must-fix findings. Don't commit.
- A fresh reviewer is spawned every round (unbiased by its earlier report); it
  gets the previous `review-<k-1>.md` only to check each finding was resolved.
- The orchestrator **never edits `dsa/` or `tests/` itself**, not even a
  one-liner; it sends the change back to the implementer. That keeps the note
  in sync with the diff.
- The implementer may **decline** a finding with a reason. The reviewer
  either accepts it or keeps it as must-fix; a disagreement still open after
  round 3 goes to the human.

## Formats

### `brief.md` (orchestrator → implementer)

```markdown
# Brief: DSA-<n> — <title>
Mode: feature | fix | refactor | test | benchmark
Branch: <type>/DSA-<n>-<desc>
Labels: <Type | Area | Component | Agent>

## Spec
<issue description, verbatim>

## Acceptance criteria
- <verbatim from the ticket; each one needs a test>

## In scope
- dsa/<topic>/<module>.py, tests/<topic>/test_<module>.py, ...

## Out of scope
- anything the ticket doesn't ask for (no drive-by refactors)
```

Mode from the issue: Type `Implementation`/`Visualization` → `feature`,
`Bug` → `fix`, `Refactor` → `refactor`, `Benchmark`/`Experiment` →
`benchmark`; Component `Tests` (or a ticket that only asks for tests) →
`test`. `Analysis`/`Writing`/`Literature`/`Tooling` tickets don't use the
agents.

### `impl-<k>.md` (implementer → reviewer)

```markdown
# Handoff: DSA-<n> round <k> — implementer → reviewer
Mode: <mode>

## Summary
<2-4 lines: what the change does and why>

## Changed files
- dsa/x/y.py — <what / why>
- tests/x/test_y.py — <cases added>

## Complexity claims
| Operation | Time | Space | Note (amortised / worst case) |

## Acceptance criteria
| Criterion (verbatim from brief) | Test(s) | Status |
| Deque.pop_front() on empty raises IndexError | test_pop_front_empty_raises | pass |

## Tests
- test_<name> — <behaviour>

## Gate
ruff format: pass | ruff check: pass | mypy: pass | pytest: <N passed>

## Review responses   (round ≥ 2 only)
| # | Finding | Action |
| 1 | dsa/x/y.py:42 O(n) pop | fixed: head index |
| 3 | __slots__ on Node | declined: <reason> |

## For the reviewer
- risks, places the implementer is unsure about, anything not done and why
```

A note with a failing gate is not a handoff: the implementer fixes it first,
or says `Gate: FAIL` with the output and stops (the orchestrator then asks the
human).

### `review-<k>.md` (reviewer → implementer)

The `dsa-review` skill's output, where each finding carries a blocking tag,
and the **last line** is the verdict:

```markdown
1. [must-fix][performance] dsa/queues/queue.py:42 — dequeue is O(n).
   Why: ... Fix: ...
2. [should-fix][tests] tests/queues/test_queue.py — no empty-queue error test.
...
VERDICT: changes-requested
```

- `must-fix`: correctness bugs, complexity that doesn't match the AC target,
  convention violations from `CLAUDE.md` / `docs/conventions.md`, missing
  required test cases, an acceptance criterion with no passing test, a failing gate.
- `should-fix`: worth doing, not blocking. The implementer does them in the
  next round if there is one, otherwise they go in the PR body.
- Optimisation tips are never blocking.
- `VERDICT: approve` iff there are no open `must-fix` findings.
