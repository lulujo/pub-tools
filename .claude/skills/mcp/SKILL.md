---
name: mcp
description: Diagnose, configure, or verify MCP server connections (Inkwren, WordPress). Use when MCP tools are missing, connections fail, or setup needs updating.
---

# MCP Server Management

Diagnose and fix MCP connection issues, or help set up MCP servers for new users.

## MCP Servers in This Project

### blackbird-wp (WordPress)

- **Config:** `~/.claude.json` (added via `claude mcp add`, managed by Claude Code)
- **Package:** `@instawp/mcp-wp` via npx
- **Credentials:** WordPress Application Password for the `claude` Editor user on blackbirdpublishing.com
- **Env var:** `CLAUDE_BLACKBIRD_WP_PASSWORD` in `.env` (for REST API fallback)
- **Tool prefix:** `mcp__blackbird-wp__` (e.g., `mcp__blackbird-wp__create_post`)

### inkwren (Inkwren catalog data)

- **Config:** `~/.claude.json` (added via `claude mcp add-json`, managed by Claude Code)
- **Package:** `@inkwren/mcp-server` via npx (published on npm)
- **Credentials:** Literal API key in `~/.claude.json` env config (rotate via `claude mcp add-json`)
- **API URL:** `https://app.inkwren.com/api` (production)
- **Tool prefix:** `inkwren_` (e.g., `inkwren_search_publications`)

## Where MCP Config Lives

**IMPORTANT:** Both MCP servers are configured in `~/.claude.json` under the pub-tools project entry (added via `claude mcp add` / `claude mcp add-json`). There is also a `.mcp.json` at the project root, but Claude Code does NOT reliably read it when a project entry already exists in `~/.claude.json`. Always use `claude mcp add-json` to register servers.

**ENV VAR GOTCHA:** `~/.claude.json` does NOT expand `${VAR}` references in env values. Use **literal values** when adding via `claude mcp add-json`. The `${VAR}` syntax works in `.mcp.json` but not in `~/.claude.json`.

To inspect the current config:
```bash
python3 -c "
import json
with open('$HOME/.claude.json') as f:
    d = json.load(f)
mcp = d['projects']['/Users/jamieferguson/Dropbox/dev/pub-tools']['mcpServers']
print(json.dumps(mcp, indent=2))
"
```

## Diagnosing Connection Issues

When MCP tools are missing or not working, check these in order:

### Step 1: Verify server is registered in ~/.claude.json

Run the inspect command above. Both `blackbird-wp` and `inkwren` should appear with correct env vars.

If inkwren is missing, re-add it:
```bash
claude mcp add-json inkwren --scope local '{"type":"stdio","command":"npx","args":["@inkwren/mcp-server"],"env":{"INKWREN_API_URL":"https://app.inkwren.com/api","INKWREN_AUTH_TOKEN":"${INKWREN_AUTH_TOKEN_BLACKBIRD}"}}'
```

### Step 2: Verify env vars are exported

MCP env vars using `${VAR}` syntax expand from the **shell environment that launched Claude Code**, not from `.env` files. `INKWREN_AUTH_TOKEN_BLACKBIRD` must be exported in `~/.zshenv` (not just `.zshrc`) so it's available in all contexts.

```bash
# Verify the var is set in the Claude Code process
echo $INKWREN_AUTH_TOKEN_BLACKBIRD | head -c 10
```

If empty, the var isn't reaching Claude Code. Check `~/.zshenv` and restart.

### Step 3: Verify the API key works

```bash
source .env
curl -s -H "Authorization: Bearer $INKWREN_AUTH_TOKEN_BLACKBIRD" \
  "https://app.inkwren.com/api/ai/tools" | head -c 200
```

If this returns a JSON array of tool definitions, the key is valid. If it returns 401, the key is wrong or expired.

### Step 5: Verify npm package is accessible

```bash
npm view @inkwren/mcp-server version
```

## Common Fixes

| Symptom | Fix |
|---------|-----|
| Inkwren tools not appearing | Check `~/.claude.json` for inkwren entry, verify env var, restart |
| Env var empty in Claude Code | Export in `~/.zshenv` (not just `.zshrc`), fully quit and relaunch |
| Server starts but no catalog tools | API key invalid or API unreachable — test with curl |
| Wrong API URL (localhost) | Re-add with `claude mcp add-json` using production URL |
| WordPress tools not appearing | Run `claude mcp add blackbird-wp --scope local -- npx -y @instawp/mcp-wp` |
| Stale npm package | Run `npx @inkwren/mcp-server@latest` or clear npx cache |
| `.mcp.json` not picked up | Claude Code ignores `.mcp.json` when project exists in `~/.claude.json` — use `claude mcp add-json` instead |

## Adding a New MCP Server

When connecting a new MCP server to pub-tools:

1. Add via `claude mcp add-json <name> --scope local '<json>'` (NOT by editing `.mcp.json`)
2. Export any required env vars in `~/.zshenv`
3. Add env var names to `.env.example` for documentation
4. Update the MCP Tool Naming Conventions table in `CLAUDE.md`
5. Update the Workspace-to-Site Mapping table if the server maps to a WordPress site
6. Fully quit and relaunch Claude Code (not just `/restart`)
