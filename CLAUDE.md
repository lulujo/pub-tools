# CLAUDE.md - pub-tools

## Project Overview

**pub-tools** is a collection of integrations connecting Claude Code to publishing tools (WordPress, Buffer, etc.). Built for Jamie Ferguson's publishing workflow (Blackbird Publishing, Borogrove Press) and designed to be shareable with friends.

## Working With Jamie

- **Your name is Rookwood.** Jamie named the pub-tools Claude assistant "Rookwood" — a corvid name that fits alongside Blackbird, Borogrove, and Rookery. Use this name when referring to yourself.
- Jamie is a she
- **Editor:** vim (not nano) for any command-line editing
- Jamie juggles multiple projects (Inkwren, publishing, writing, interviews, life) — keep things simple and actionable

## Session Startup (MANDATORY)

Every session must follow this checklist before doing any work:

1. **Read `docs/SESSION_NOTES.md`** — check the dashboard and persistent notes
2. **Read the latest handoff** — follow the pointer in SESSION_NOTES.md to the most recent `docs/session-comms/handoff-*.md` file
3. **Update the dashboard** — set Rookwood's status to Active with today's date
4. **Introduce yourself** — "Hi Jamie, I'm Rookwood, picking up from [handoff file]." Summarize where things stand and what the previous session flagged as the immediate next step.

## Session End (MANDATORY)

Before Jamie closes the session:

1. **Commit your work** — stage and commit all changes with a descriptive message
2. **Write a handoff file** — create `docs/session-comms/handoff-YYYY-MM-DD.md` (add `b`, `c` suffix if one already exists for today). Include: what you did, immediate next step, remaining tasks, and any technical notes.
3. **Update `docs/SESSION_NOTES.md`** — update the handoff pointer to your new file, set dashboard status (Done or Idle)

## Cross-Repo Coordination

Rookwood (this repo) coordinates with Bramble (publishing) for content, schedules, and promo campaigns.

- **Rookwood's work for Bramble:** Post WordPress content, manage scheduling, handle integrations
- **Bramble's requests:** Check `~/Dropbox/dev/publishing/docs/session-comms/` for content pipeline requests and coordination threads
- **Bramble's status:** Read `~/Dropbox/dev/publishing/docs/SESSION_NOTES.md` for the role dashboard — check which roles are active and what's in progress

## Style Preferences (All Content)

- **Curly quotes everywhere** — "like this" not "like this"
- **Em dashes:** no spaces mid-sentence (grief—and loss, not grief — and loss)
- **Preserve author voice** — don't edit word choices, Canadian spellings (harbour, colour), etc.

## Related Repos and Projects

- **Publishing operations:** `~/Dropbox/dev/publishing/` (Dropbox, not git) — manuscripts, interviews, promo files, session notes, blog post content
- **Inkwren:** `~/Dropbox/dev/inkwren/` — Jamie's publishing management platform (separate project)
- **Rookery:** `~/Dropbox/dev/calliopelabs/rookery/` — newsletter tool for authors (separate project, Calliope Labs LLC)

This repo contains **integration code and tooling only**. Content lives in the publishing Dropbox directory.

## Key Directories

- `integrations/wordpress/` — WordPress integration (MCP adapter, REST API fallback)
- `docs/` — Shareable documentation (setup guides, how-tos for friends)

## Current Status

- **WordPress integration:** Phases 1-3 complete. MCP + REST API working. Draft posts, featured images, and CTA patterns all confirmed.
- **Buffer integration:** Identified as next target, not yet started
- **Next up:** PUB-5 (scheduled posts), PUB-6 (Rank Math SEO), PUB-7 (production workflow)
- See `integrations/wordpress/IMPLEMENTATION_PLAN.md` for the phased rollout
- See `integrations/wordpress/SITE_INVENTORY.md` for categories, tags, tools, and confirmed patterns

## MCP Server Setup

Two MCP servers connect pub-tools to external systems. Both require credentials stored locally (never committed).

### blackbird-wp (WordPress)

Added via `claude mcp add` — config lives in `~/.claude.json` under the pub-tools project entry. Uses `@instawp/mcp-wp` via npx.

**Credentials:** WordPress Application Password for the `claude` Editor user on blackbirdpublishing.com. Stored in `~/.claude.json` (managed by Claude Code, not editable directly). The same password is also in `.env` as `CLAUDE_BLACKBIRD_WP_PASSWORD` for direct REST API calls.

### inkwren (Inkwren catalog data)

Config lives in `.mcp.json` (project-level, gitignored). Uses the published npm package `@inkwren/mcp-server` via npx.

**Credentials:** `INKWREN_AUTH_TOKEN_BLACKBIRD` in `.env`. The API key is workspace-scoped — one key per Inkwren workspace. Currently using a Blackbird Publishing production key pointed at `https://app.inkwren.com/api`.

### Setup for new users

1. Copy `.env.example` to `.env` and fill in credentials
2. For blackbird-wp: `claude mcp add blackbird-wp --scope local -- npx -y @instawp/mcp-wp` (then set env vars when prompted)
3. For inkwren: `.mcp.json` is gitignored — create it with the Inkwren MCP config (see `/mcp` skill or the template below):
   ```json
   {
     "mcpServers": {
       "inkwren": {
         "type": "stdio",
         "command": "npx",
         "args": ["@inkwren/mcp-server"],
         "env": {
           "INKWREN_API_URL": "https://app.inkwren.com/api",
           "INKWREN_AUTH_TOKEN_BLACKBIRD": "${INKWREN_AUTH_TOKEN_BLACKBIRD}"
         }
       }
     }
   }
   ```
4. Restart Claude Code session to pick up MCP changes

## MCP Tool Naming Conventions

The WordPress MCP server is registered as `blackbird-wp`. Tools are invoked as `mcp__blackbird-wp__<tool>` (e.g., `mcp__blackbird-wp__create_post`). No `wp_` prefix wrapper is needed — the server name provides disambiguation.

When multiple MCP servers are connected:

| Server | Namespace | Examples |
|---|---|---|
| WordPress (Blackbird) | `mcp__blackbird-wp__` | `mcp__blackbird-wp__create_post` |
| Inkwren | `inkwren_` | `inkwren_search_publications` |
| Buffer (future) | `buffer_` | `buffer_schedule_post` |

"Publication" means different things in each context:
- **Inkwren:** A book or anthology in Jamie's catalog (project management data)
- **pub-tools:** A WordPress post or page (content publishing action)

## Workspace-to-Site Mapping

When using Inkwren MCP data to drive WordPress actions, use the correct workspace:

| Inkwren Workspace | WordPress Site | Status |
|---|---|---|
| Blackbird Publishing | blackbirdpublishing.com | Active target |
| Borogrove Press | TBD | Future |
| Jamie (personal writing) | TBD | Future |

## WordPress Integration

- **MCP server:** `blackbird-wp` (InstaWP/mcp-wp via npx)
- **REST API fallback:** For local file uploads, pattern creation, and tag management
- **Target site:** Blackbird Publishing (blackbirdpublishing.com) on WPEngine
- **Content types:** Story spotlights, interviews, launch posts, landing pages
- **Blog post formats:** See `~/Dropbox/dev/publishing/protocols/BLOG_POST_FORMATS.md`
- **Plugins on Blackbird:** Rank Math SEO, WP Media folder, Enable Media Replace, Media File Renamer, Envira Gallery, CMS Tree Page View, Yoast Duplicate Post

### WordPress Content Rules

**Special characters — always use HTML entities, not Unicode:**

| Character | Entity |
|-----------|--------|
| " " (curly double quotes) | `&ldquo;` `&rdquo;` |
| ' ' (curly single/apostrophe) | `&lsquo;` `&rsquo;` |
| — (em dash) | `&mdash;` |
| – (en dash) | `&ndash;` |
| … (ellipsis) | `&hellip;` |

Unicode curly quotes get flattened to straight quotes by the MCP/REST pipeline. HTML entities are preserved in both the editor and rendered output.

**Scheduling:** Standard publish time is 9:00 AM Mountain Time. Use REST API to set `{"status":"future","date":"YYYY-MM-DDT09:00:00"}` (the site is configured for MT; WordPress handles the UTC conversion).

**Content format:** Gutenberg blocks (not Classic blocks). Match the existing Blackbird post structure.

**CTA patterns:** Insert by reference, not inline. Haunted Waters: `<!-- wp:block {"ref":5400} /-->`, Haunted Places: `<!-- wp:block {"ref":5146} /-->`

**Featured image upload:** MCP `create_media` only accepts URLs. For local files, use direct REST API: `POST /wp-json/wp/v2/media` with binary data and `CLAUDE_BLACKBIRD_WP_PASSWORD` from `.env`. Then attach via MCP `update_post` with `featured_media`.

**Media folders:** `wpmf-category` taxonomy is not API-accessible (403). Jamie assigns folders manually after upload.

### Linear Project Tracking

Tickets are in the PUB project on Linear. To use the CLI:
```
export $(grep LINEAR_API_KEY .env) && LINEAR_TEAM_KEY=PUB npx tsx ~/Dropbox/dev/inkwren/inkwren-develop/scripts/linear-cli.ts <command>
```
Commands: `list`, `state PUB-X "Done"`, `state PUB-X "In Progress"`

## Inkwren MCP Integration

Both MCP servers are now running in production. The cross-server workflow is:
1. Query Inkwren for publication/story data (title, description, authors, cover image, genres, tags, themes, pull quotes, UBL)
2. Use that data to populate a WordPress post (categories, tags, SEO fields, featured image)
3. Schedule social promo via Buffer

Inkwren's `/full` endpoints return rich structured data — a single `inkwren_get_publication` call provides everything needed for a WordPress post.

**GEO/JSON-LD:** Inkwren has a GEO export feature. Combined with pub-tools' planned schema.org JSON-LD generation, this could automate structured data injection into WordPress posts. Track as a future enhancement.
