# Session Coordination Notes

---

## SESSION DASHBOARD

| Role | Status | Last Active | Notes |
|------|--------|-------------|-------|
| Rookwood | Done | 2026-06-13 | Escape from 2026: created drafts 5715/5716/5717 (Jason, Annie, Kari) |

**Status Icons:** -- Idle | Active | Blocked | Done

---

## LATEST HANDOFF

Read this file to pick up where the last session left off:

> docs/session-comms/handoff-2026-06-13.md

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

### Gutenberg Image Blocks (resized)

For a resized image block to validate, **all three** of these must be in sync:

1. `"width":"300px"` in the block JSON attributes
2. `is-resized` class on `<figure>` (auto-derived from the `width` attribute, **not** something you put in `"className"`)
3. `style="width:300px"` on the `<img>` only (not the `<figure>`)

If any of these are missing or contradict each other, the editor shows "Block contains unexpected or invalid content" and "Attempt recovery" silently drops the resize, rendering the image full-width.

**Correct:**
```html
<!-- wp:image {"id":123,"width":"300px","sizeSlug":"full","linkDestination":"none","align":"center"} -->
<figure class="wp-block-image aligncenter size-full is-resized"><img src="..." class="wp-image-123" style="width:300px"/></figure>
<!-- /wp:image -->
```

**Wrong (recovery strips the resize, image renders huge):**
```html
<!-- wp:image {"id":123,"sizeSlug":"full","className":"is-resized"} -->
<figure class="wp-block-image size-full is-resized"><img src="..." style="width:300px"/></figure>
<!-- /wp:image -->
```
The `width` attribute is missing from the JSON, so Gutenberg can't reconcile the inline `style` against the block spec.

### WordPress Post Titles
WordPress does not support HTML in post titles. `<em>` tags get escaped to literal text. Book titles cannot be italicized in titles — use plain text instead.

### WordPress Filename Normalization
WordPress lowercases and hyphenates filenames on upload. A local file named `Cover FInal.jpg` (with a typo'd capital "I") becomes `cover-final.jpg` in the URL. So a sloppy local filename never makes it to the public URL — no need to rename locally and re-upload for cosmetic fixes. Use the existing media ID's `source_url` (look it up via `GET /wp-json/wp/v2/media/<id>`) rather than constructing URLs from the source filename.

### Multi-Post Series Workflow
For 3+ posts in a series (e.g., bundle interviews, anthology spotlights), extract the shared scaffolding into a single helpers module and `import` from per-post scripts. Cuts most of the per-post code and prevents drift across posts.

Shared bits to factor out:
- Block builders: `p()`, `h2()`, `sep()`, `q()` (bold question), `cover_block(media_id, url, alt)`, `find_list(links)`, `bundle_montage()`
- Bundle constants: bundle banner media ID + URL, bundle banner alt text, bundle CTA text, bundle URL
- HTML entity shortcuts: `LDQUO`, `RDQUO`, `RSQUO`, `MDASH`, `HELLIP`
- The `post_to_wp(post_dict)` REST API caller (with the User-Agent header — WPEngine 1010s without it)
- An `assemble(cover, intros, qa, bio, find_heading, find_html, book_title_html)` function that builds the full content from per-post inputs

The per-post script then becomes ~80% data (intros, Q&A pairs, bio, find links, post metadata) and ~20% wiring. See `/tmp/escape_helpers.py` from the Escape from 2026 series for a working example pattern (the file itself is ephemeral; rebuild it at the start of a new series).

### Markdown&rarr;Gutenberg Entity Conversion (smart quotes / dashes)

Bramble&rsquo;s `interview_post.md` source files use **straight quotes and Unicode em dashes only** (no curly quotes, no entities). When auto-converting to HTML entities, two edge cases will silently corrupt output if the converter is naive (both hit during the 2026-06-13 Escape batch):

1. **Nested bold + italic.** A `**bold question**` containing an `*italic*` (e.g. Annie&rsquo;s *Gray Lady* / *What-Ifs&hellip;*) breaks a `\*\*([^*]+)\*\*` bold regex (the inner `*` blocks the character class). Use a **non-greedy** match: `\*\*(.+?)\*\*`, then convert single-`*` italics afterward.

2. **Opening quote after `*` or em dash.** A `"` whose preceding char is `**` (e.g. `**"Comstock"`) or an em dash (e.g. `justice—"something"`) gets mis-rendered as a *closing* `&rdquo;` because the &ldquo;opening&rdquo; rule only looked for whitespace/brackets. Fix: run **smart-quotes before em-dash conversion** and include `*` and `—` in the opening-quote lookbehind set: `(^|[\s\(\[\{\*—])"` (and the same for single quotes).

**Always verify the generated content** before/after creating the post: assert zero stray `*` in the tag-stripped text, and grep for `(?:<p>|<strong>|<em>|&mdash;)&rdquo;` (an opening quote mis-rendered as closing) &mdash; both should be zero.

---

## ACTIVE SESSIONS

### Rookwood — 2026-04-04
**What happened:** Reviewed and approved `@inkwren/mcp-server@0.1.0` npm publish. Set up production MCP connection. Debugged three config issues (`.mcp.json` ignored, `${VAR}` not expanded, `.zshrc` not inherited). Created `/mcp` skill. Updated CLAUDE.md and SESSION_NOTES.md.
**Next:** Verify Inkwren MCP connection in fresh session (tools loaded but disconnected during `--resume`). Then resume interview pipeline and PUB-6.
