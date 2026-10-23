# scan-todos

Scan for TODO/FIXME/HACK/XXX comments in the codebase, group them into
actionable tickets, and propose Linear issues for user approval.

## When to use

When the user wants to triage accumulated TODOs into Linear tickets, or to
audit what technical debt markers exist in the codebase.

## Workflow

### 1 - Scan

Grep for `TODO|FIXME|HACK|XXX` across `dsa/` and `tests/`:

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" dsa/ tests/
```

For each hit, read the surrounding context (+/- 3 lines) to understand
the intent.

### 2 - Group

Related TODOs become a single ticket. Group by:
- Same design question or decision (e.g. naming conventions across files)
- Same refactoring pattern (e.g. "extract helper" in multiple places)
- Same file region (adjacent TODOs about one method)

A single TODO that stands alone is its own group.

### 3 - Propose

Present a table to the user with one row per proposed ticket:

| # | Title | TODOs (file:line) | Template | Type label | Agent label |
|---|---|---|---|---|---|

For each ticket, include:
- **Title**: clear, actionable summary
- **TODOs**: the file:line references that this ticket covers
- **Template**: which `.linear/templates/` template to use
- **Type label**: from the Type label group (Implementation, Refactor, Analysis, Tooling, etc.)
- **Agent label**: `agent-ready` if spec is clear, `needs-human` if it requires judgment
- **Suggested additional labels**: Area, Component, Priority, Milestone

### 4 - Wait for approval

Do NOT create any tickets until the user explicitly approves.
The user may:
- Approve all as-is
- Remove groups they don't want ticketed
- Merge or split groups
- Change labels, priority, or template
- Edit titles

### 5 - Create tickets

For each approved group, use `/linear-ticket` to create the issue with:
- The agreed title and description
- All file:line references in the description body
- The chosen template, labels, and priority
- State: Backlog (unless user specifies otherwise)

### 6 - Report

After creation, print a summary table:

| # | Issue ID | Title | Labels |
|---|---|---|---|

## Notes

- This command only scans `dsa/` and `tests/`. To scan other directories,
  the user should specify them explicitly.
- TODOs that are part of the design (e.g. "TODO: implement in phase 2" with a
  ticket already linked) should be noted but not re-ticketed.
- If a TODO already references a DSA-number, skip it — it is already tracked.
