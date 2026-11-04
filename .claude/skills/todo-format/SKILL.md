---
name: todo-format
description: >-
  Format and triage rules for TODO/FIXME comments in the DSA repo: Linear
  ticket ID plus a [Type | Area | Component | Agent] labels line, and how to
  turn TODOs (all of them, a file, or one section) into ticket proposals. Use
  when writing, rewriting, parsing or ticketing TODO comments.
---

# TODO comments

A TODO names its Linear ticket and carries that ticket's labels, so it can be
traced and triaged without opening Linear:

```python
# TODO(DSA-27): comparator should be a Protocol/ABC, not the concrete class?
#   [Analysis | Linked Lists | Core | needs-human]
#   further notes, same indent
```

## Format rules

- Line 1: `TODO(DSA-<n>):` plus a one-line summary. No ticket yet: plain `TODO:`.
- Line 2: labels in the order Type | Area | Component | Agent (Flag last, if any).
  Without a ticket, list the labels it would get.
- Inside a docstring, write the same lines without `#`.
- Keep the comment's original indentation, and keep lines at 88 characters or fewer.
- Note lines go under the labels line with the same indent. Never drop the
  author's notes.
- If one TODO block mixes concerns from different tickets, split it into
  separate blocks, with a bare `#` line between them.
- Labels come from the ticket's labels in Linear. For a TODO without a ticket,
  choose labels using `.claude/skills/linear-ticket/SKILL.md`.
- When a ticket's labels change in Linear, update the TODO. When the ticket is
  done, delete the TODO.

## Valid label values

- Type: Implementation, Experiment, Benchmark, Analysis, Writing, Literature,
  Bug, Refactor, Tooling, Visualization
- Area: Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Heaps, Hashing,
  Sorting/Searching, Dynamic Programming, Greedy, Backtracking
- Component: Core, Tests, Benchmarks, Notebooks, Report, Infra
- Agent: agent-ready, needs-human
- Flag: Blocked, Needs-supervisor, Reproducibility

## States

| Comment | State | Action |
|---|---|---|
| `TODO(DSA-<n>):` + labels line | tracked | skip; flag if labels differ from Linear |
| `TODO:` + labels line | proposal | propose a ticket with those labels |
| `TODO:` without a labels line | legacy | propose a ticket, pick labels, mark for rewrite |
| any TODO an open issue already covers | tracked, untagged | skip; report the `DSA-<n>` to tag it with |

## Triage

**Scope.** Exactly what the caller gives: a whole tree (default `dsa/` and
`tests/`), a file, a `file:line`, a line range, or a named method or class.
For `file:line`, take the whole TODO block that contains the line (from the
`TODO` line to the last note line). Don't widen the scope on your own.

**Steps.**
1. Grep `TODO|FIXME|HACK|XXX` in scope and read a few lines around each hit.
2. Classify each block by the States table. For untagged blocks, check open
   issues with `list_issues` (team `DSA`, keywords from the summary).
3. Group related blocks into one ticket: same design question, same
   refactoring pattern, or same method. A block that stands alone is its own ticket.
4. Labels: reuse the labels line if there is one, else choose by the
   `linear-ticket` rules. `needs-human` for design or naming questions,
   `agent-ready` only for mechanical changes.

**Output.**
1. Table: `#`, title, file:line refs, template, Type, Area, Component, Agent,
   priority, milestone.
2. One self-contained spec per row: intent (what done looks like) and the
   verbatim TODO blocks. This is what goes to `linear-ticket-creator`.
3. Lists: already tracked (with IDs), label mismatches, unclear TODOs.

## Write-back

Once a ticket exists, rewrite each of its TODO blocks to
`TODO(DSA-<n>):` with the ticket's final labels line, following the format
rules. Only comment lines change.
