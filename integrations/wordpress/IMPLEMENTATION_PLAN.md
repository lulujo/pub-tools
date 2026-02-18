# WordPress Integration — Implementation Plan

**Decision:** Use the official WordPress MCP Adapter as the primary approach, with direct REST API calls as fallback for anything MCP doesn't cover (e.g., WP Media folder taxonomy, Rank Math meta fields).

**Target site:** Blackbird Publishing (blackbirdpublishing.com) on WPEngine

**Tool naming:** All WordPress tools use the `wp_` prefix (e.g., `wp_create_post`, `wp_upload_media`) to avoid collision with Inkwren MCP tools (`inkwren_` prefix). See CLAUDE.md for the full naming convention.

---

## Phase 1: Connect & Discover (Jamie + Claude)

Get Claude Code talking to Blackbird and inventory what's available.

### Jamie does:
1. Install the **WordPress MCP Adapter** plugin on Blackbird
   - Repo: https://github.com/WordPress/mcp-adapter
   - Install via WP Admin → Plugins → Add New (or upload ZIP)
2. Generate an **Application Password** on Blackbird
   - WP Admin → Users → Your Profile → Application Passwords
   - Give it a name like "Claude Code"
   - Copy the password (shown only once)
3. Share the Application Password with Claude

### Claude does:
4. Configure Claude Code to connect to Blackbird via MCP
   - `claude mcp add blackbird <endpoint> --transport http --header "Authorization: Basic <base64>"`
   - This stores the credential in your local Claude Code config (`~/.claude/`), **not** in the repo
   - Each person using this setup generates their own App Password and configures their own local MCP connection — nothing sensitive gets shared
5. **Verify connection and inventory tools:**
   - List all available MCP tools — document exact tool names and parameters
   - Check whether tool names can be prefixed with `wp_` or if the adapter uses fixed names
   - If no prefix support, determine whether we need a wrapper layer or can rely on tool descriptions for disambiguation
6. **Inventory existing site content:**
   - Confirm permalink structure (must be non-Plain for MCP adapter)
   - List existing categories and tags — document exact names and capitalization
   - List existing WP Media folders (via `wpmf-category` taxonomy)
   - Check whether `wpmf-category` taxonomy is REST-enabled: `GET /wp-json/wp/v2/taxonomies/wpmf-category`
7. **Quick REST API sanity check:**
   - Test one direct REST API call (e.g., `GET /wp-json/wp/v2/posts?per_page=1`) to confirm the fallback path works
   - This de-risks Phase 2 — if the MCP Adapter has gaps, we know REST API works

### Done when:
- Claude can list existing posts on Blackbird
- Tool names, categories, tags, media folders, and permalink structure are documented
- We know whether `wp_` prefixes are supported or need a workaround

---

## Phase 2: Draft Posts (Claude)

Create a spotlight or interview post as a WordPress draft.

### Content conversion strategy

WordPress uses Gutenberg blocks. Our `.md` files need to become WordPress content. Options to evaluate:

- **Option A: HTML in a Classic block** — Convert markdown to HTML, wrap in a single Classic block (`<!-- wp:freeform -->..<!-- /wp:freeform -->`). Simplest. Jamie can edit in Classic mode but loses per-section block editing.
- **Option B: Gutenberg blocks** — Convert markdown sections to individual Gutenberg blocks (paragraphs, headings, quotes). More complex but gives Jamie full block editor control.
- **Option C: Raw HTML** — Send HTML content without block markers. WordPress may auto-wrap in a Classic block. Least predictable.

**Decide this before creating the first post.** Test each option with a single post and let Jamie compare the editing experience.

### Steps:
8. Pick one existing spotlight `.md` file as a test case (e.g., `Spotlight_ABetterPlace_JamieFerguson.md`)
9. **Test curly quotes:** Create a draft with known curly quote and em dash content. Verify they survive the transfer to WordPress. If they don't, identify where the mangling happens (MCP adapter? REST API? WordPress itself?) and fix before proceeding.
10. Create a draft post:
    - Title, content (using the chosen conversion approach)
    - Set category ("Story Spotlights") — use exact name from Phase 1 inventory
    - Set tags (author name, anthology name, story title) — match existing tag conventions
    - Status: draft
11. Jamie reviews the draft in WP Admin — check:
    - Formatting (curly quotes, em dashes, heading levels)
    - Block editor experience (can she edit sections naturally?)
    - Categories and tags correct
12. Iterate on formatting issues
13. **Clean up:** Delete test posts and note the cleanup process for future testing

### Done when:
- A draft post appears in WP that looks right and has correct taxonomy
- Curly quotes and em dashes are confirmed working
- Content conversion approach is chosen and documented

---

## Phase 3: Featured Images (Claude)

Upload and attach featured images.

**Source:** Featured images for Haunted Waters are in Jamie's Dropbox (location TBD — ask Jamie). Future: Inkwren stores `cover_image_url` for publications, which could be used programmatically.

### Steps:
14. **Ask Jamie** where the featured images for Haunted Waters live
15. Test uploading an image via REST API to `/wp-json/wp/v2/media`
16. **Check Media File Renamer behavior:** After upload, verify the filename wasn't silently renamed by the AI-powered Media File Renamer plugin. The attachment ID should still work, but confirm.
17. Test assigning the image to a WP Media folder via `wpmf-category` taxonomy
    - Use the taxonomy info from Phase 1 discovery
    - If not REST-enabled, ask Jamie to check the WP Media folder plugin settings
18. Attach uploaded image as featured image on the draft post
19. Jamie reviews — does the image appear correctly? Is it in the right media folder?
20. **Clean up:** Delete test media or move to a "test" folder

### Done when:
- Draft posts have featured images, organized in the correct media folder
- Media File Renamer behavior is understood and documented

---

## Phase 4: Scheduling (Claude)

Move from drafts to scheduled posts.

### Steps:
21. Test creating a post with `status: future` and a `date` set to a future datetime
22. Verify the post appears in WP's scheduled queue with the correct date/time
23. Verify the timezone handling — WPEngine/WordPress timezone vs UTC
24. Test the full workflow: `.md` file → upload image → create scheduled post with image, categories, tags

### Done when:
- Claude can create a fully-formed scheduled post in one workflow
- Timezone behavior is documented

---

## Phase 5: SEO — Rank Math (Claude + Jamie)

Layer in SEO metadata.

### Recommended approach: PHP snippet (Option A)

Option A (small PHP snippet in `functions.php`) is simpler and avoids adding a third-party plugin dependency. Option B (Rank Math API Manager plugin) is a fallback if Option A doesn't work on WPEngine.

### Jamie does:
25. Add the PHP snippet to register Rank Math meta fields with `show_in_rest` (we'll provide the exact code)

### Claude does:
26. Test setting Rank Math fields on a post:
    - `rank_math_title` — SEO title
    - `rank_math_description` — meta description
    - `rank_math_focus_keyword` — focus keyword
    - OG fields (title, description, image)
27. Define sensible defaults for each post type:
    - Spotlights: SEO title = "Story Spotlight: [Title] by [Author]", description from hook/premise paragraph
    - Interviews: SEO title = "Interview: [Title] by [Author]", description from opening paragraph
    - Focus keyword from story themes/genre

### Done when:
- Draft/scheduled posts include Rank Math SEO fields with good defaults

---

## Phase 6: Production Workflow

Put it all together for real use.

28. Document the end-to-end workflow for creating a post
29. Test with a batch: create 2-3 posts from existing Haunted Waters `.md` files
30. Jamie reviews, publishes, confirms everything looks right
31. Document any manual steps that remain (CTA pattern, final review)
32. Document cleanup procedures for test content

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

---

## Key Reference Files

- `~/Dropbox/dev/publishing/protocols/BLOG_POST_FORMATS.md` — post structure and formatting rules
- `integrations/wordpress/SETUP.md` — approach comparison, hosting notes, plugin details
- `integrations/wordpress/CONTENT_PLAN.md` — what we're creating, taxonomy plan, media/SEO details
- `~/Dropbox/dev/publishing/sessions/pub_integrations_CLAUDE.md` — session context and log (in publishing Dropbox, not this repo)
