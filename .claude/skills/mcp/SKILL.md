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

If inkwren is missing, re-add it. `~/.claude.json` does NOT expand `${VAR}`, so inline the **literal** token (pull it from `.env` into a shell var first, and redact when echoing). The env var the server reads is `INKWREN_AUTH_TOKEN`:
```bash
TOK=$(grep '^INKWREN_AUTH_TOKEN_BLACKBIRD=' .env | cut -d= -f2- | tr -d '" ')
claude mcp add-json inkwren --scope local "{\"type\":\"stdio\",\"command\":\"npx\",\"args\":[\"@inkwren/mcp-server\"],\"env\":{\"INKWREN_API_URL\":\"https://app.inkwren.com/api\",\"INKWREN_AUTH_TOKEN\":\"$TOK\"}}"
```
Because the token is stored literally, **no shell export is needed** for inkwren — it does not depend on `${VAR}` reaching the Claude Code process.

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

## Setting Up Inkwren MCP for Another Project (Bramble, etc.)

Other Claude assistants can get the same Inkwren read access. **Bramble** (the publishing repo, `~/Dropbox/dev/publishing/`) was set up this way on 2026-06-19.

Method (mirrors the pub-tools setup — literal token, no `.mcp.json`, no shell export):

1. Confirm the target project already has the Blackbird key in its `.env` as `INKWREN_AUTH_TOKEN_BLACKBIRD` (publishing already did). If not, copy it from pub-tools `.env`.
2. Register the server under that project's entry in `~/.claude.json` via `claude mcp add-json`, run **from the target project directory** (`--scope local` keys off the cwd). Inline the literal token; redact on echo:
   ```bash
   cd /Users/jamieferguson/Dropbox/dev/publishing
   TOK=$(grep '^INKWREN_AUTH_TOKEN_BLACKBIRD=' .env | cut -d= -f2- | tr -d '" ')
   claude mcp add-json inkwren --scope local "{\"type\":\"stdio\",\"command\":\"npx\",\"args\":[\"@inkwren/mcp-server\"],\"env\":{\"INKWREN_API_URL\":\"https://app.inkwren.com/api\",\"INKWREN_AUTH_TOKEN\":\"$TOK\"}}" 2>&1 | sed "s/$TOK/<redacted>/g"
   ```
3. Verify it landed (redact secrets):
   ```bash
   python3 -c "import json,os,copy; d=json.load(open(os.path.expanduser('~/.claude.json'))); ms=copy.deepcopy(d['projects']['/Users/jamieferguson/Dropbox/dev/publishing'].get('mcpServers',{})); [s['env'].__setitem__(k,'<redacted>') for s in ms.values() for k in s.get('env',{}) if 'TOKEN' in k]; print(json.dumps(ms,indent=2))"
   ```
4. **A fresh session** in that project picks it up. Confirm with `inkwren_list_workspaces` (returns Blackbird Publishing).
5. Document the capability in that project's `CLAUDE.md` so its sessions know they have it (done for Bramble).

**Why `.mcp.json` won't work here:** the publishing project already has an entry in `~/.claude.json`, so Claude Code ignores a project-root `.mcp.json` — same gotcha as pub-tools. Use `claude mcp add-json`.

**Workspace scope:** the key is workspace-scoped (one key = one workspace), and only **Blackbird Publishing** currently exists. To give a coordinator access to other workspaces (Borogrove, personal writing), create those workspaces + keys in Inkwren first, then add each as its own env/server.

## Adding a New MCP Server

When connecting a new MCP server to pub-tools:

1. Add via `claude mcp add-json <name> --scope local '<json>'` (NOT by editing `.mcp.json`)
2. Export any required env vars in `~/.zshenv`
3. Add env var names to `.env.example` for documentation
4. Update the MCP Tool Naming Conventions table in `CLAUDE.md`
5. Update the Workspace-to-Site Mapping table if the server maps to a WordPress site
6. Fully quit and relaunch Claude Code (not just `/restart`)
