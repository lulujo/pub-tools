# WordPress Integration — Implementation Plan

**Decision:** Use **InstaWP/mcp-wp** as the MCP layer — it runs locally (via `npx`), connects to WordPress over the REST API, and requires no plugin install on the server. Direct REST API calls serve as fallback for anything mcp-wp doesn't cover (e.g., WP Media folder taxonomy, Rank Math meta fields).

**Why not WordPress/mcp-adapter?** The official adapter is a Composer package, not a traditional WP plugin. Installing it on WPEngine managed hosting requires SSH/Composer access or manual dependency bundling — too much friction for what it adds. InstaWP/mcp-wp gives us ~35 MCP tools with zero server-side changes.

**Target site:** Blackbird Publishing (blackbirdpublishing.com) on WPEngine

**Tool naming:** All WordPress tools use the `wp_` prefix (e.g., `wp_create_post`, `wp_upload_media`) to avoid collision with Inkwren MCP tools (`inkwren_` prefix). See CLAUDE.md for the full naming convention.

---

## Phase 1: Connect & Discover (Jamie + Claude)

Get Claude Code talking to Blackbird and inventory what's available.

### Jamie does:
1. Create a dedicated **`claude` user** on Blackbird with the **Editor** role
   - WP Admin → Users → Add New User
   - Editor can create/edit/publish posts, manage taxonomy, upload media — no admin access
2. Generate an **Application Password** on the `claude` user's profile
   - Users → edit `claude` → Application Passwords → name it "Claude Code"
   - Copy the password (shown only once)
3. Add the Application Password to `.env` in the pub-tools repo root (copy from `.env.example`)

### Claude does:
3. **Set up InstaWP/mcp-wp locally:**
   - Configure Claude Code to use mcp-wp with credentials from `.env`
   - `.env` is gitignored — credentials never leave the local machine
   - Each person using this setup generates their own App Password and creates their own `.env` — nothing sensitive gets shared
4. **Verify connection and inventory tools:**
   - List all available MCP tools — document exact tool names and parameters
   - Check whether tool names can be prefixed with `wp_` or if mcp-wp uses fixed names
   - If no prefix support, determine whether we need a wrapper layer or can rely on tool descriptions for disambiguation
5. **Inventory existing site content:**
   - Confirm permalink structure
   - List existing categories and tags — document exact names and capitalization
   - List existing WP Media folders (via `wpmf-category` taxonomy)
   - Check whether `wpmf-category` taxonomy is REST-enabled: `GET /wp-json/wp/v2/taxonomies/wpmf-category`
6. **Quick direct REST API sanity check:**
   - Test one direct REST API call (e.g., `GET /wp-json/wp/v2/posts?per_page=1`) to confirm the fallback path works
   - This de-risks Phase 2 — if mcp-wp has gaps, we know direct REST API works

### Done when:
- Claude can list existing posts on Blackbird via mcp-wp
- Tool names, categories, tags, media folders, and permalink structure are documented in `integrations/wordpress/SITE_INVENTORY.md`
- We know whether `wp_` prefixes are supported or need a workaround
- Direct REST API fallback is confirmed working

---

## Phase 2: Draft Posts (Claude)

Create a spotlight or interview post as a WordPress draft.

### Content conversion strategy

WordPress uses Gutenberg blocks. Our `.md` files need to become WordPress content. Options to evaluate:

- **Option A: HTML in a Classic block (recommended)** — Convert markdown to HTML, wrap in a single Classic block (`<!-- wp:freeform -->..<!-- /wp:freeform -->`). Simplest. Matches Jamie's current workflow (markdown → `md2html.py` → paste HTML into WP). Test Kadence theme compatibility — confirm Classic block content doesn't conflict with Kadence pattern styling.
- **Option B: Gutenberg blocks** — Convert markdown sections to individual Gutenberg blocks (paragraphs, headings, quotes). More complex but gives Jamie full block editor control. Only pursue if Option A causes problems.
- **Option C: Raw HTML** — Send HTML content without block markers. WordPress may auto-wrap in a Classic block. Least predictable.

**Confirm Option A works before creating real posts.** Test with a single post and verify Jamie can edit naturally in WP and that Kadence styling is unaffected.

### Steps:
8. Pick one existing spotlight `.md` file as a test case (e.g., `Spotlight_ABetterPlace_JamieFerguson.md`)
9. **Test curly quotes and special characters:** Create a draft with all of these in both the post title and body:
    - Curly double quotes: "like this"
    - Curly single quotes: it's, 'quoted'
    - Em dashes: grief—and loss
    Verify they survive the transfer to WordPress. If they don't, identify where the mangling happens (MCP adapter? REST API? WordPress itself?) and fix before proceeding.
10. Create a draft post:
    - Title, content (using the chosen conversion approach)
    - Set category ("Story Spotlights") — use exact name from Phase 1 inventory
    - Set tags (author name, anthology name, story title) — match existing tag conventions
    - Status: draft
11. Jamie reviews the draft in WP Admin — check:
    - Formatting (curly quotes, em dashes, heading levels)
    - Block editor experience (can she edit sections naturally?)
    - Categories and tags correct
12. **Set a clean post slug** — don't rely on WordPress auto-generated slugs. Convention: `[story-title]-[author-last-name]` for spotlights, `interview-[author-name]` for interviews (confirm with Jamie).
13. Iterate on formatting issues
14. **Clean up:** Delete test posts and note the cleanup process for future testing

### Done when:
- A draft post appears in WP that looks right and has correct taxonomy
- Curly quotes and em dashes are confirmed working
- Content conversion approach is chosen and documented

---

## Phase 3: Featured Images (Claude)

Upload and attach featured images.

**Source:** Featured images live in Jamie's Dropbox, but the location varies by project (e.g., `anthologies/[name]/promo/` for anthology promo images, separate folders for covers). Image path is provided per-post or discovered from the project's directory structure. Future: Inkwren stores `cover_image_url` for publications, which could be used programmatically.

### Steps:
15. **Confirm image path** for the test post (Jamie provides the path, or we locate it in the project's Dropbox directory)
16. Test uploading an image via REST API to `/wp-json/wp/v2/media`
17. **Check Media File Renamer behavior:** After upload, verify the filename wasn't silently renamed by the AI-powered Media File Renamer plugin. The attachment ID should still work, but confirm.
18. Test assigning the image to a WP Media folder via `wpmf-category` taxonomy
    - Use the taxonomy info from Phase 1 discovery
    - If not REST-enabled, ask Jamie to check the WP Media folder plugin settings
19. Attach uploaded image as featured image on the draft post
20. Jamie reviews — does the image appear correctly? Is it in the right media folder?
21. **Clean up:** Delete test media or move to a "test" folder

### Done when:
- Draft posts have featured images, organized in the correct media folder
- Media File Renamer behavior is understood and documented

---

## Phase 4: Scheduling (Claude)

Move from drafts to scheduled posts.

### Steps:
22. Test creating a post with `status: future` and a `date` set to a future datetime
23. Verify the post appears in WP's scheduled queue with the correct date/time
24. Verify the timezone handling — WPEngine/WordPress timezone vs UTC
25. Test the full workflow: `.md` file → upload image → create scheduled post with image, categories, tags
26. **Coordinate with POST_SCHEDULE.md** — once scheduling works, pull dates from the Haunted Waters post schedule (managed by Publisher Claude) rather than entering manually

### Done when:
- Claude can create a fully-formed scheduled post in one workflow
- Timezone behavior is documented

---

## Phase 5: SEO — Rank Math (Claude + Jamie)

Layer in SEO metadata.

### Recommended approach: PHP snippet (Option A)

Option A (small PHP snippet in `functions.php`) is simpler and avoids adding a third-party plugin dependency. Option B (Rank Math API Manager plugin) is a fallback if Option A doesn't work on WPEngine.

### Jamie does:
27. Add the PHP snippet to register Rank Math meta fields with `show_in_rest` (we'll provide the exact code)

### Claude does:
28. Test setting Rank Math fields on a post:
    - `rank_math_title` — SEO title
    - `rank_math_description` — meta description
    - `rank_math_focus_keyword` — focus keyword
    - OG fields (title, description, image)
29. Define sensible defaults for each post type:
    - Spotlights: SEO title = "Story Spotlight: [Title] by [Author]", description from hook/premise paragraph
    - Interviews: SEO title = "Interview: [Title] by [Author]", description from opening paragraph
    - Focus keyword from story themes/genre

### Done when:
- Draft/scheduled posts include Rank Math SEO fields with good defaults

---

## Phase 6: Production Workflow

Put it all together for real use.

30. Document the end-to-end workflow for creating a post
31. Test with a batch: create 2-3 posts from existing Haunted Waters `.md` files
32. Jamie reviews, publishes, confirms everything looks right
33. Document any manual steps that remain (CTA pattern, final review)
34. Document cleanup procedures for test content

### Done when:
- Jamie can say "post this spotlight" and get a fully-formed draft/scheduled post on Blackbird with image, taxonomy, and SEO

---

## Future Phases (not yet planned in detail)

- **Inkwren cross-server workflow** — pull publication data from Inkwren MCP → populate WordPress posts automatically
- **Batch scheduling** — schedule an entire anthology's post calendar at once
- **GEO / Schema.org JSON-LD** — integrate Inkwren GEO export data into WordPress posts
- **Cross-promotion automation** — auto-add "Also Featured in..." links
- **Additional sites** — extend to Jamie's author site
- **Buffer integration** — schedule social media promo posts to coincide with WP posts
- **CTA pattern automation** — template the Kadence CTA block so it can be inserted programmatically (same pattern, different buy links)

---

## Key Reference Files

- `~/Dropbox/dev/publishing/protocols/BLOG_POST_FORMATS.md` — post structure and formatting rules
- `integrations/wordpress/SETUP.md` — approach comparison, hosting notes, plugin details
- `integrations/wordpress/CONTENT_PLAN.md` — what we're creating, taxonomy plan, media/SEO details
- `~/Dropbox/dev/publishing/sessions/pub_integrations_CLAUDE.md` — session context and log (in publishing Dropbox, not this repo)
