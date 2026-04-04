# Session Coordination Notes

---

## SESSION DASHBOARD

| Role | Status | Last Active | Notes |
|------|--------|-------------|-------|
| Rookwood | Idle | 2026-04-04 | MCP npm setup complete, verify connection in fresh session |

**Status Icons:** -- Idle | Active | Blocked | Done

---

## LATEST HANDOFF

Read this file to pick up where the last session left off:

> docs/session-comms/handoff-2026-04-04.md

---

## COORDINATION PROTOCOL

**What Goes Where:**

**SESSION_NOTES.md** (this file) — Persistent state and session pointer:
- Dashboard status (one line)
- Latest handoff pointer (updated every session end)
- Persistent technical notes (gotchas that would otherwise repeat in every handoff)

**Handoff files** (`docs/session-comms/handoff-*.md`) — Work log:
- What this session accomplished
- Immediate next steps
- Remaining tasks carried forward
- Technical notes specific to current work

**Linear tickets** — Ticket progress:
- Use the Linear CLI to update ticket states
- Log implementation details in ticket comments

**session-comms threads** (`docs/session-comms/`) — Bramble coordination:
- Non-handoff files are coordination threads with Bramble
- Content pipeline requests, cross-repo task handoffs

**Rule of thumb:** Handoff files are *your work log*. This file is *persistent state* that every session reads on startup.

---

## CROSS-REPO COORDINATION

**Rookwood** (this repo) and **Bramble** (publishing) coordinate through:

- `docs/session-comms/` in **this repo** — Rookwood writes handoff files and technical status here
- `docs/session-comms/` in **publishing repo** — Bramble writes requests and content plans there

**To check Bramble's status:**
1. Read `~/Dropbox/dev/publishing/docs/SESSION_NOTES.md` — check the dashboard
2. Read the relevant role session file in `~/Dropbox/dev/publishing/sessions/` for details

**To leave a message for Bramble:**
- Write or update a file in `~/Dropbox/dev/publishing/docs/session-comms/` describing what you need

---

## HANDOFF NAMING CONVENTION

Handoff files follow this pattern:

```
handoff-YYYY-MM-DD.md     (first session of the day)
handoff-YYYY-MM-DDb.md    (second session, same day)
handoff-YYYY-MM-DDc.md    (third session, same day)
```

No hyphen before the letter suffix. Examples:
- `handoff-2026-02-23.md` (correct)
- `handoff-2026-02-23b.md` (correct)
- `handoff-2026-02-22-b.md` (old format, avoid going forward)

---

## PERSISTENT NOTES

Technical gotchas that apply across sessions. Update these as things change.

### REST API Auth
The WordPress Application Password in `.env` has spaces (e.g., `abcd efgh ijkl mnop`). When using curl directly, **remove the spaces** — the spaced format causes auth failures. MCP tools handle this automatically.

### Linear CLI
```
export $(grep LINEAR_API_KEY .env) && LINEAR_TEAM_KEY=PUB npx tsx ~/Dropbox/dev/inkwren/inkwren-develop/scripts/linear-cli.ts <command>
```
Commands: `list`, `state PUB-X "Done"`, `state PUB-X "In Progress"`, `next-task`

### Inkwren MCP
- **Published:** `@inkwren/mcp-server@0.1.0` on npm (2026-03-29)
- Config in `.mcp.json` uses `npx @inkwren/mcp-server` (no more local source path)
- API URL: `https://app.inkwren.com/api` (production)
- API key is workspace-scoped (one key = one workspace)
- `inkwren_` prefix applied by MCP server in `register-tools.ts`
- **Env vars must be exported before starting Claude Code.** The `.env` file stores tokens but MCP servers inherit from the shell environment, not `.env` directly. Run `set -a && source .env && set +a` in the pub-tools directory before launching `claude`. Without this, Inkwren MCP tools won't appear.
- For diagnostics, use the `/mcp` skill

---

## ACTIVE SESSIONS

### Rookwood — 2026-04-04
**What happened:** Reviewed and approved `@inkwren/mcp-server@0.1.0` npm publish. Set up production MCP connection. Debugged three config issues (`.mcp.json` ignored, `${VAR}` not expanded, `.zshrc` not inherited). Created `/mcp` skill. Updated CLAUDE.md and SESSION_NOTES.md.
**Next:** Verify Inkwren MCP connection in fresh session (tools loaded but disconnected during `--resume`). Then resume interview pipeline and PUB-6.
