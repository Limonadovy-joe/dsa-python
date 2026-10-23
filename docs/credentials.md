# Credentials and API keys

Secrets used by this project. None are committed — they live in environment
variables or gitignored config files.

## Active

| Service | Key / token | Where it lives | Used by |
|---|---|---|---|
| Linear | Personal API token | `LINEAR_API_KEY` env var (set in shell profile or `.env`) | `.mcp.json` Linear MCP server |

## Gitignored paths that may hold secrets

| Path | Contents |
|---|---|
| `.env` / `.env.*` | Environment variables (API keys, tokens) |
| `secrets/` | Any local secret files |
| `.linear/config.md` | Linear workspace/team/project UUIDs |
| `.mcp.json` | MCP server URLs (local ports, may embed tokens) |
| `.claude/settings.local.json` | User-local Claude Code permissions |

## Claude Code deny rules

`settings.local.json` blocks Claude from reading sensitive paths:

- `**/.env`, `**/.env.*` — environment files
- `**/secrets/**` — secret directories
- `~/.ssh/**` — SSH keys
- `~/.aws/**` — AWS credentials
