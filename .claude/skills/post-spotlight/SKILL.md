---
name: post-spotlight
description: Create a story spotlight draft on Blackbird Publishing. Use when Jamie says to post or draft a spotlight. Pass the author name, story title, or .md file path as the argument.
---

# Post Spotlight

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

**Always use HTML entities, never Unicode characters:**

| Character | Entity |
|-----------|--------|
| " " (curly double quotes) | `&ldquo;` `&rdquo;` |
| ' ' (curly single/apostrophe) | `&lsquo;` `&rsquo;` |
| — (em dash) | `&mdash;` |
| – (en dash) | `&ndash;` |
| … (ellipsis) | `&hellip;` |

Unicode curly quotes get flattened to straight quotes by the pipeline. HTML entities survive in both the editor and rendered output.

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

### CTA Pattern IDs

| Anthology | Pattern ID | Reference |
|-----------|-----------|-----------|
| Haunted Waters | 5400 | `<!-- wp:block {"ref":5400} /-->` |
| Haunted Places | 5146 | `<!-- wp:block {"ref":5146} /-->` |

### Buy Links

| Anthology | URL |
|-----------|-----|
| Haunted Waters | `https://books2read.com/h3-haunted-waters` |

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

For author-name tags: search existing tags via REST API before creating new ones. Many authors already have tags.

## Step 5: Create the Draft

Use `mcp__blackbird-wp__create_post` with:
- `title`: `Story Spotlight: &ldquo;Story Title&rdquo; by Author Name`
- `content`: Gutenberg block markup from Step 3
- `status`: `draft` (NEVER publish without Jamie's approval)
- `slug`: `story-spotlight-story-title-by-author-name` (lowercase, hyphens)
- `categories`: `[14]` for spotlights
- `tags`: `[378]` for Haunted Waters (add author tag ID if it exists)

## Step 6: Featured Image (if available)

Check for a featured image:
1. `~/Dropbox/Jamie/Writing and Publishing/Blackbird Publishing/Publishing/Anthologies/The Haunted Anthology/#3 - Haunted Waters/Promo images/1200x628/Spotlights/`
2. Look for a file matching the author name

If found, upload via REST API (MCP `create_media` can't handle local files):

```bash
WP_PASS=$(grep CLAUDE_BLACKBIRD_WP_PASSWORD .env | cut -d= -f2) && \
curl -s -X POST "https://blackbirdpublishing.com/wp-json/wp/v2/media" \
  -u "claude:${WP_PASS}" \
  -H 'Content-Disposition: attachment; filename="Haunted-Waters-Spotlight-Author-Name.jpg"' \
  -H "Content-Type: image/jpeg" \
  --data-binary "@/path/to/image.jpg"
```

Then set alt text via `mcp__blackbird-wp__edit_media` and attach via `mcp__blackbird-wp__update_post` with `featured_media`.

If no image found, tell Jamie. The post can be created without one.

## Step 7: Report

Tell Jamie:
- Post ID and title
- What's complete vs what has placeholders (excerpt, bio)
- Whether featured image was attached
- Any tag that needs to be created
- Remind her to assign media to the correct WP Media folder (not API-accessible)
