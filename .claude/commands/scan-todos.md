# scan-todos

Turn TODO/FIXME/HACK/XXX comments into Linear tickets: the whole codebase, a
file, or one TODO section.

## When to use

- `/scan-todos` — triage every TODO in `dsa/` and `tests/`.
- `/scan-todos <path | file:line | file:start-end>` — triage one file or section.
- Plain requests too: "create a ticket from the TODO at linked_list.py:61",
  "ticket the TODOs in doubly_linked_list.py".

## Workflow

```
todo-scanner agent  →  main session: approval  →  linear-ticket-creator agent  →  main session: write-back
 (triage the scope)      (user edits the table)      (dedupe, create, report)      (TODO → TODO(DSA-n))
```

Agents live in `.claude/agents/`. Format and triage rules live in the
`todo-format` skill; label, template and milestone rules in `linear-ticket`.

### 1 - Triage (agent)

Launch `todo-scanner` (Agent tool, `subagent_type: todo-scanner`) with the
scope: the paths, `file:line` or range the user gave, else `dsa/` and `tests/`.
For "this TODO" without a location, resolve it from the conversation (the file
the user has open or just mentioned) before launching; if you can't, ask.

### 2 - Approval

- **Full or multi-ticket scan:** show the proposal table plus the
  already-tracked, mismatch and unclear lists. Wait for explicit approval. The
  user may drop, merge or split rows, or change labels, priority, milestone,
  template or title; apply the edits to the specs yourself.
- **Targeted request that yields one ticket** ("create a ticket from this
  TODO"): the request is the approval. Show the one-line proposal and go on,
  unless the TODO is already tracked or unclear — then report that and stop.

### 3 - Create (agent)

Launch `linear-ticket-creator` **once** with all approved specs. State Backlog
unless the user said otherwise.

### 4 - Write-back

For each created issue, rewrite its TODO blocks to `TODO(DSA-<n>):` plus the
ticket's labels line (Write-back in `todo-format`). Comment lines only. Do the
same for TODOs the scanner reported as covered by an existing open issue. These
are `dsa/`/`tests/` edits: leave them unstaged for the user's ticket branch.

### 5 - Report

| # | Result | Issue | Title | Labels | TODOs rewritten |
|---|---|---|---|---|---|

Include skipped duplicates, defaults the creator chose, and errors.

## Notes

- Neither agent can ask the user anything; all questions happen in the main session.
- TODOs in `scripts/` or `utils/` are only scanned when the user names them.
