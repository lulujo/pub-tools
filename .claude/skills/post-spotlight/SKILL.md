---
name: post-spotlight
description: Create a story spotlight draft on Blackbird Publishing. Use when Jamie says to post or draft a spotlight. Pass the author name, story title, or .md file path as the argument.
---

# Post Spotlight

**This is a format conversion task, not a creative writing task.** Do not analyze, interpret, or engage with the story content beyond what's needed for mechanical conversion. The content is already written and approved. Convert format, apply HTML entities, pull bio, check comps against blocklist, create draft. Move quickly.

Create a WordPress draft spotlight post on blackbirdpublishing.com from a markdown source file.

## Usage

`/post-spotlight <author name or file path>`

Examples:
- `/post-spotlight Steve Vernon`
- `/post-spotlight Spotlight_ABetterPlace_JamieFerguson.md`

## Step 1: Find the Source File

Search for the spotlight markdown file:

1. `~/Dropbox/dev/publishing/anthologies/haunted-waters/posts/Spotlight_*<name>*.md`
2. If not found, check other anthology directories under `~/Dropbox/dev/publishing/anthologies/`
3. If still not found, ask Jamie for the file path

Read the file. Identify which anthology it belongs to (determines CTA pattern and tags).

## Step 2: Check for Existing Post

Search Blackbird for an existing post with a matching title to avoid duplicates:

```
mcp__blackbird-wp__list_posts search="<story title>" status="draft"
mcp__blackbird-wp__list_posts search="<story title>" status="publish"
```

If a matching post exists, tell Jamie and ask how to proceed.

## Step 3: Convert to Gutenberg Blocks

Convert the markdown to Gutenberg block markup following these rules:

### Special Characters (CRITICAL)

Use HTML entities for all special characters (see CLAUDE.md table). Unicode curly quotes get flattened to straight quotes by the pipeline.

### Block Structure

Map the markdown sections to Gutenberg blocks in this order:

1. **Hook/Premise** — `<!-- wp:paragraph -->` with `<strong>` wrapper
2. **About the Story** — `<!-- wp:paragraph -->` blocks (no heading, flows from hook)
3. **Excerpt** — `<!-- wp:heading -->` + `<!-- wp:quote -->` block. If placeholder, keep as `<!-- wp:paragraph -->` with the placeholder text.
4. **About the Author** — `<!-- wp:heading -->` + `<!-- wp:paragraph -->` blocks. **Use `/author-info <author name>` to extract the bio from Vellum** instead of leaving a placeholder. If the source markdown already has a bio, prefer the Vellum version (it's the canonical source) but flag any differences to Jamie.
5. **What Lingers After the Last Line** — `<!-- wp:heading -->` + `<!-- wp:paragraph -->` blocks
6. **Read the Story** — `<!-- wp:heading -->` + `<!-- wp:paragraph -->` with anthology name only (no buy link — the CTA pattern provides that)
7. **CTA Pattern** — `<!-- wp:block {"ref":PATTERN_ID} /-->` (see pattern IDs below). The pattern renders a buy link and cover image — do NOT add a separate "Buy the book" paragraph.
8. **If you liked...** — `<!-- wp:heading -->` + `<!-- wp:list -->` block
9. **Closing paragraph** — `<!-- wp:paragraph -->` connecting the recommendations back to the story

### CTA Patterns & Buy Links

See `integrations/wordpress/BUY_LINKS.md` for the current anthology CTA pattern IDs and buy links. Insert the CTA pattern by reference (e.g., `<!-- wp:block {"ref":5400} /-->`).

## Step 4: Set Taxonomy

### Categories

| Post Type | Category ID |
|-----------|------------|
| Story Spotlights | 14 |
| Interviews | 4 |
| New Releases | 16 |

### Tags

| Anthology | Tag ID |
|-----------|--------|
| Haunted Waters | 378 |
| Write Stuff StoryBundle | 387 |
| Escape from 2026 StoryBundle | 393 |

**Always add an author-name tag.** Search existing tags via REST API before creating new ones. Many authors already have tags. If not, create one.

## Step 5: Create the Draft

Use `mcp__blackbird-wp__create_post` with:
- `title`: `Story Spotlight: &ldquo;Story Title&rdquo; by Author Name`
- `content`: Gutenberg block markup from Step 3
- `status`: `draft` (NEVER publish without Jamie's approval)
- `slug`: `spotlight-story-title-by-author-name` (lowercase, hyphens)
- `categories`: `[14]` for spotlights
- `tags`: `[378]` for Haunted Waters (add author tag ID if it exists)
- `author`: `2` (Blackbird Publishing). Posts default to the `claude` user otherwise, which isn't visible in the editor UI but shows on the published post. Always set this.

## Step 6: Set SEO (Rank Math)

Set the post's SEO meta after creation. MCP can't write post meta — use a direct REST PATCH.
Full pattern + rationale: `integrations/wordpress/RANK_MATH_SEO.md`.

- **Focus keyword** = the story title.
- **Description** (≤ 155 chars): `{Author}’s {Story}—a story spotlight from {Anthology}.` (append `, from Blackbird Publishing` only if it still fits). Curly apostrophes / em dashes are fine; no quotes around the title.
- Leave SEO **title** and **canonical** empty — Rank Math's template handles the title.

```bash
source /Users/jamieferguson/Dropbox/dev/pub-tools/.env
WP_PASS=$(echo "$CLAUDE_BLACKBIRD_WP_PASSWORD" | tr -d ' ')
curl -s -X POST "https://blackbirdpublishing.com/wp-json/wp/v2/posts/<POST_ID>" \
  -u "claude:${WP_PASS}" -H 'User-Agent: pub-tools' -H 'Content-Type: application/json' \
  --data '{"meta":{"rank_math_focus_keyword":"...","rank_math_description":"..."}}'
```

Read back (`GET /posts/<id>?context=edit` → `.meta`) to confirm the write stuck.

## Step 7: Featured Image (if available)

Check for a featured image:
1. `~/Dropbox/Jamie/Writing and Publishing/Blackbird Publishing/Publishing/Anthologies/The Haunted Anthology/#3 - Haunted Waters/Promo images/1200x628/Spotlights/`
2. Look for a file matching the author name

If found, upload via REST API (MCP `create_media` can't handle local files):

```bash
source /Users/jamieferguson/Dropbox/dev/pub-tools/.env && WP_PASS=$(echo "$CLAUDE_BLACKBIRD_WP_PASSWORD" | tr -d ' ') && \
curl -s -X POST "https://blackbirdpublishing.com/wp-json/wp/v2/media" \
  -u "claude:${WP_PASS}" \
  -H 'Content-Disposition: attachment; filename="Haunted-Waters-Spotlight-Author-Name.jpg"' \
  -H "Content-Type: image/jpeg" \
  --data-binary "@/path/to/image.jpg"
```

Then set alt text via `mcp__blackbird-wp__edit_media` and attach via `mcp__blackbird-wp__update_post` with `featured_media`.

If no image found, tell Jamie. The post can be created without one.

## Step 8: Report

Tell Jamie:
- Post ID and title
- What's complete vs what has placeholders (excerpt, bio)
- Whether featured image was attached
- Any tag that needs to be created
- Remind her to assign media to the correct WP Media folder (not API-accessible)
