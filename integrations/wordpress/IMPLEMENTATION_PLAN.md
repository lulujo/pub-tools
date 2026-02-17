# WordPress Integration — Implementation Plan

**Decision:** Use the official WordPress MCP Adapter as the primary approach, with direct REST API calls as fallback for anything MCP doesn't cover (e.g., WP Media folder taxonomy, Rank Math meta fields).

**Target site:** Blackbird Publishing (blackbirdpublishing.com) on WPEngine

---

## Phase 1: Connect (Jamie + Claude)

Get Claude Code talking to Blackbird.

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
5. Verify connection — list available tools, confirm we can read posts

### Done when:
- Claude can list existing posts on Blackbird

---

## Phase 2: Draft Posts (Claude)

Create a spotlight or interview post as a WordPress draft.

7. Pick one existing spotlight `.md` file as a test case
8. Create a draft post via MCP:
   - Title, content (converted from markdown to WP blocks or HTML)
   - Set category ("Story Spotlights")
   - Set tags (author name, anthology name, story title)
   - Status: draft
9. Jamie reviews the draft in WP Admin — check formatting, categories, tags
10. Iterate on any formatting issues (curly quotes, em dashes, heading levels, etc.)

### Done when:
- A draft post appears in WP that looks right and has correct taxonomy

---

## Phase 3: Featured Images (Claude)

Upload and attach featured images.

11. Test uploading an image via REST API to `/wp-json/wp/v2/media`
12. Test assigning the image to a WP Media folder via `wpmf-category` taxonomy
    - First check: hit `/wp-json/wp/v2/taxonomies/wpmf-category` to verify it's REST-enabled
    - If not REST-enabled, we'll assign the folder via a direct `wp_set_object_terms` approach or ask Jamie to check a plugin setting
13. Attach uploaded image as featured image on the draft post
14. Jamie reviews — does the image appear correctly? Is it in the right media folder?

### Done when:
- Draft posts have featured images, organized in the correct media folder

---

## Phase 4: Scheduling (Claude)

Move from drafts to scheduled posts.

15. Test creating a post with `status: future` and a `date` set to a future datetime
16. Verify the post appears in WP's scheduled queue with the correct date/time
17. Test the full workflow: `.md` file → upload image → create scheduled post with image, categories, tags

### Done when:
- Claude can create a fully-formed scheduled post in one workflow

---

## Phase 5: SEO — Rank Math (Claude + Jamie)

Layer in SEO metadata.

18. Enable Rank Math fields in REST API (one of):
    - **Option A:** Jamie adds a small PHP snippet to `functions.php` to register meta fields with `show_in_rest`
    - **Option B:** Install the Rank Math API Manager plugin
19. Test setting Rank Math fields on a post:
    - `rank_math_title` — SEO title
    - `rank_math_description` — meta description
    - `rank_math_focus_keyword` — focus keyword
    - OG fields (title, description, image)
20. Define sensible defaults for each post type:
    - Spotlights: SEO title = "Story Spotlight: [Title] by [Author]", description from hook/premise paragraph
    - Interviews: SEO title = "Interview: [Title] by [Author]", description from opening paragraph
    - Focus keyword from story themes/genre

### Done when:
- Draft/scheduled posts include Rank Math SEO fields with good defaults

---

## Phase 6: Production Workflow

Put it all together for real use.

21. Document the end-to-end workflow for creating a post
22. Test with a batch: create 2-3 posts from existing Haunted Waters `.md` files
23. Jamie reviews, publishes, confirms everything looks right
24. Document any manual steps that remain (CTA pattern, final review)

### Done when:
- Jamie can say "post this spotlight" and get a fully-formed draft/scheduled post on Blackbird with image, taxonomy, and SEO

---

## Future Phases (not yet planned in detail)

- **Batch scheduling** — schedule an entire anthology's post calendar at once
- **GEO / Schema.org JSON-LD** — integrate Inkwren-generated structured data
- **Cross-promotion automation** — auto-add "Also Featured in..." links
- **Additional sites** — extend to Jamie's author site
- **Buffer integration** — schedule social media promo posts to coincide with WP posts

---

## Key Reference Files

- `protocols/BLOG_POST_FORMATS.md` — post structure and formatting rules
- `integrations/wordpress/SETUP.md` — approach comparison, hosting notes, plugin details
- `integrations/wordpress/CONTENT_PLAN.md` — what we're creating, taxonomy plan, media/SEO details
- `sessions/pub_integrations_CLAUDE.md` — session context and log
