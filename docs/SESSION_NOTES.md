# Session Coordination Notes

---

## SESSION DASHBOARD

| Role | Status | Last Active | Notes |
|------|--------|-------------|-------|
| Rookwood | Active | 2026-06-28 | PUB-6 (Rank Math SEO) Done &mdash; snippet live in new Kadence child theme; 27 Haunted Waters posts backfilled; skills now set SEO. Open: PUB-9, PUB-10. |

**Status Icons:** -- Idle | Active | Blocked | Done

---

## LATEST HANDOFF

Read this file to pick up where the last session left off:

> docs/session-comms/handoff-2026-06-27.md

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

### Bundle Interview Posts &mdash; use the `/post-bundle-interview` skill
StoryBundle author interviews (Escape from 2026, Write Stuff, future bundles) are now handled by a committed, tested engine &mdash; **do not rebuild a converter in /tmp**:
- Skill: `.claude/skills/post-bundle-interview/SKILL.md` (full workflow + config format)
- Engine: `integrations/wordpress/md_to_gutenberg.py` (markdown&rarr;Gutenberg conversion, retry-wrapped REST, idempotent media reuse, `verify()` self-checks)
- Tests: `integrations/wordpress/test_md_to_gutenberg.py` &mdash; run after any engine change. Each case is a real bug we hit (nested bold/italic, opening-quote-after-`*`/em-dash, en dash, `E=mc²`, ampersands, italic-inside-link). The converter rationale lives in the engine docstring.

### StoryBundle scraper &mdash; use `integrations/storybundle/`
Pulling a StoryBundle's contents (books, authors, covers, tiers, detail links) is handled by a committed, tested tool (PUB-11) &mdash; **do not rebuild a scraper in /tmp**:
- Tool: `integrations/storybundle/storybundle.py` (stdlib-only; `python3 storybundle.py <slug>` &rarr; JSON; `--details` adds per-book `author_bio` + best-effort `synopsis`). Full usage in its `README.md`.
- Tests: `integrations/storybundle/test_storybundle.py` &mdash; run after any change (pre-commit hook runs it when staged).
- **Must run while the bundle is LIVE.** Expired bundle pages are JS shells with zero book links &mdash; the data can't be recovered after the promo window. A `count: 0` result means expired-or-wrong-slug, not "no books."
- Consumers: the listing layer feeds Inkwren catalog cross-ref + spotlight/interview target lists; the publishing repo's StoryBundle role session exercises `--details`. Field-design rationale: `docs/session-comms/storybundle-scraper-details-field.md`.

### WPEngine/Cloudflare 5xx during bulk REST
Bulk REST runs occasionally hit transient **522/525** from Cloudflare/WPEngine, and WPEngine 1010s any request without a `User-Agent` header. The engine above already wraps calls in retry-on-5xx and reuses already-uploaded media (a 522 between the image POST and the alt-text POST otherwise leaves an orphan upload). For any *other* REST work, do the same: set a UA, retry 5xx, and `GET /media?search=<filename>` before re-uploading to avoid duplicates.

### Blackbird active theme = Kadence (custom PHP goes in the child theme)
Blackbird's active theme is **Kadence** (a third-party theme that auto-updates). Custom PHP snippets (e.g. the Rank Math REST registration) live in the **Kadence child theme**: `wp-content/themes/kadence-child/functions.php`. Do **not** edit the Kadence *parent* (wiped on update) or `blackbirdtwentyseventeen` (dormant, not active). The child theme was created 2026-06-28; its `functions.php` has an `after_switch_theme` hook that one-time-copies the parent's theme_mods (Customizer/menus/Additional CSS) on activation. Theme files aren't REST-editable &mdash; Jamie deploys child-theme changes via SFTP/WPEngine.

### Rank Math SEO &mdash; use the skills / `seo_backfill.py`
SEO meta fields are REST-writable now (PUB-6 Done). MCP **cannot** write post meta &mdash; PATCH `/posts/<id>` with `{"meta":{"rank_math_focus_keyword":...,"rank_math_description":...}}` (UA + 5xx retry + read-back). The posting skills do this automatically. To backfill old posts: `python3 integrations/wordpress/seo_backfill.py --tag <id> --anthology "Name: Subtitle"` (dry run; add `--apply`). Curly apostrophes/em dashes round-trip fine in meta. Full reference: `integrations/wordpress/RANK_MATH_SEO.md`.

---

## ACTIVE SESSIONS

### Rookwood — 2026-04-04
**What happened:** Reviewed and approved `@inkwren/mcp-server@0.1.0` npm publish. Set up production MCP connection. Debugged three config issues (`.mcp.json` ignored, `${VAR}` not expanded, `.zshrc` not inherited). Created `/mcp` skill. Updated CLAUDE.md and SESSION_NOTES.md.
**Next:** Verify Inkwren MCP connection in fresh session (tools loaded but disconnected during `--resume`). Then resume interview pipeline and PUB-6.
