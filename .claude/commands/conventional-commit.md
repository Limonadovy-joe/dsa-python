# conventional-commit

Generate and execute a conventional commit message.

## When to use

When the user asks to commit staged or unstaged changes using the Conventional Commits specification.

## Workflow

1. Run `git status` to review changed files.
2. Run `git diff` and `git diff --cached` to inspect both unstaged and staged changes.
3. Stage relevant changes with `git add <file>` (ask the user which files if unclear).
4. Construct the commit message using the structure below.
5. Execute the commit:

```bash
git commit -m "type(scope): description"
```

## Commit message structure

```
<type>(<scope>): <description>

<body>

<footer>
```

- **type** (required): `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`
- **scope** (optional but recommended): the area of the codebase affected
- **description** (required): short, imperative summary ("add", not "added")
- **body** (optional): more detailed explanation of the change
- **footer** (optional): `BREAKING CHANGE: ...` or issue references

## Examples

- `feat(parser): add ability to parse arrays`
- `fix(ui): correct button alignment`
- `docs: update README with usage instructions`
- `refactor: improve performance of data processing`
- `chore: update dependencies`
- `feat!: send email on registration` (BREAKING CHANGE)
- `test(deque): add unit tests for deque backends`

## Branch naming

Branches follow the same **type** as the commit and include the Linear issue ID:

```
<type>/DSA-<number>-<kebab-case-description>
```

Before committing, check you are on the correct branch. If not, create it:

```bash
git checkout -b <type>/DSA-<number>-<kebab-description>
```

**Examples:**
- `feat/DSA-11-implement-basic-bst-tests`
- `fix/DSA-15-deque-remove-front-bug`
- `test/DSA-22-add-heap-unit-tests`
- `refactor/DSA-30-simplify-linked-list`

For housekeeping without a Linear ticket:

```
chore/<kebab-case-description>
```

**Examples:** `chore/add-credentials-doc`, `chore/update-gitignore`

These branches are only for docs, config, CI, and infra changes — never for
changes to `dsa/` or `tests/` source. Omit the `Refs:` footer when there is
no ticket.

## Validation

- **type**: must be one of the allowed types per [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification)
- **scope**: optional, but recommended for clarity
- **description**: required, imperative mood
- **body**: optional, use for additional context
- **footer**: use for breaking changes or issue references

## Instructions

1. Analyze the diff to understand what changed and why.
2. Pick the correct **type** (e.g., `feat` for new functionality, `fix` for a bug fix, `test` for adding tests, `refactor` for restructuring without behaviour change).
3. Pick a **scope** that matches the area (e.g., `deque`, `linked-list`, `ci`, `arrays`).
4. Write a concise **description** in imperative mood.
5. Add a **body** only if the change is non-trivial and needs explanation.
6. Add a **footer** only for breaking changes or issue references.
   **Never** add a `Co-Authored-By` trailer.
7. Use a HEREDOC for multi-line messages:

```bash
git commit -m "$(cat <<'EOF'
type(scope): description

Body text here.

Footer here.

EOF
)"
```
