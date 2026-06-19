---
name: post-interview
description: Create an interview draft on Blackbird Publishing. Use when Jamie says to post or draft an interview. Pass the author name, story title, or .md file path as the argument.
---

# Post Interview

**This is a format conversion task, not a creative writing task.** Do not analyze, interpret, or engage with the story content beyond what's needed for mechanical conversion. The content is already written and approved. Convert format, apply HTML entities, pull bio, check comps against blocklist, create draft. Move quickly.

Create a WordPress draft interview post on blackbirdpublishing.com from a markdown source file.

## Usage

`/post-interview <author name or file path>`

## Step 1: Find the Source File

Search for the interview markdown file:

1. `~/Dropbox/dev/publishing/anthologies/haunted-waters/posts/Interview_*<name>*.md`
2. If not found, check other anthology directories under `~/Dropbox/dev/publishing/anthologies/`
3. If still not found, ask Jamie for the file path

Read the file. Identify which anthology it belongs to.

## Step 2: Check for Existing Post

Search Blackbird for a duplicate before creating:

```
mcp__blackbird-wp__list_posts search="<story title>" status="draft"
mcp__blackbird-wp__list_posts search="<story title>" status="publish"
```

## Step 3: Convert to Gutenberg Blocks

### Special Characters (CRITICAL)

Use HTML entities for all special characters (see CLAUDE.md table). Unicode curly quotes get flattened to straight quotes by the pipeline.

### Block Structure

1. **Opening Description** — `<!-- wp:paragraph -->` (narrative hook, not a summary)
2. **Interview Questions heading** — `<!-- wp:heading -->`
3. **Q&A pairs** — Questions as `<!-- wp:paragraph -->` with `<strong>` wrapper, answers as `<!-- wp:paragraph -->` blocks
4. **About the Author** — `<!-- wp:heading -->` + bio paragraphs + website link. **Use `/author-info <author name>` to extract the bio from Vellum** instead of leaving a placeholder. If the interview markdown already has a bio, prefer the Vellum version (canonical source) but flag any differences to Jamie.
5. **Read the Story** — `<!-- wp:heading -->` + paragraph with anthology name only (no buy link — the CTA pattern provides that)
6. **CTA Pattern** — Look up the pattern ID in `integrations/wordpress/BUY_LINKS.md` and insert by reference (e.g., `<!-- wp:block {"ref":5400} /-->`). The pattern renders a buy link and cover image — do NOT add a separate "Buy the book" paragraph.

### Author Voice Rules

- **DO NOT edit content** — only formatting (bold questions, spacing, block structure)
- **Leave author spellings alone** (Canadian: harbour, colour, etc.)
- **Leave author word choices exactly as written**
- **Jamie reviews and decides on any content changes**

## Step 4: Create the Draft

Use `mcp__blackbird-wp__create_post` with:
- `title`: `Interview: &ldquo;Story Title&rdquo; by Author Name`
- `content`: Gutenberg block markup
- `status`: `draft` (NEVER publish)
- `slug`: `interview-story-title-by-author-name`
- `categories`: `[4]` for interviews
- `tags`: anthology/project tag (e.g., `[378]` for Haunted Waters, `[387]` for Write Stuff StoryBundle, `[393]` for Escape from 2026 StoryBundle) + author tag. **Always create or find an author-name tag** — search existing tags first, create via REST API if needed.
- `author`: `2` (Blackbird Publishing). Posts default to the `claude` user otherwise, which isn't visible in the editor UI but shows on the published post. Always set this.

## Step 5: Featured Image

Same process as post-spotlight — check the Promo images directory for an interview-specific image:
`~/Dropbox/Jamie/Writing and Publishing/Blackbird Publishing/Publishing/Anthologies/The Haunted Anthology/#3 - Haunted Waters/Promo images/1200x628/Interviews/`

Upload via REST API if found. See `/post-spotlight` skill for the curl command.

## Step 6: Report

Tell Jamie: Post ID, title, what's complete, what has placeholders, whether image was attached, and remind about media folder assignment.
