---
name: post-interview
description: Create an interview draft on Blackbird Publishing. Use when Jamie says to post or draft an interview. Pass the author name, story title, or .md file path as the argument.
---

# Post Interview

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

**Always use HTML entities, never Unicode characters:**

| Character | Entity |
|-----------|--------|
| " " (curly double quotes) | `&ldquo;` `&rdquo;` |
| ' ' (curly single/apostrophe) | `&lsquo;` `&rsquo;` |
| — (em dash) | `&mdash;` |
| – (en dash) | `&ndash;` |
| … (ellipsis) | `&hellip;` |

### Block Structure

1. **Opening Description** — `<!-- wp:paragraph -->` (narrative hook, not a summary)
2. **Interview Questions heading** — `<!-- wp:heading -->`
3. **Q&A pairs** — Questions as `<!-- wp:paragraph -->` with `<strong>` wrapper, answers as `<!-- wp:paragraph -->` blocks
4. **About the Author** — `<!-- wp:heading -->` + bio paragraphs + website link
5. **Read the Story** — `<!-- wp:heading -->` + paragraph with anthology name
6. **CTA Pattern** — `<!-- wp:block {"ref":PATTERN_ID} /-->` (Haunted Waters: 5400, Haunted Places: 5146)

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
- `tags`: `[378]` for Haunted Waters (add author tag if it exists)

## Step 5: Featured Image

Same process as post-spotlight — check the Promo images directory for an interview-specific image:
`~/Dropbox/Jamie/Writing and Publishing/Blackbird Publishing/Publishing/Anthologies/The Haunted Anthology/#3 - Haunted Waters/Promo images/1200x628/Interviews/`

Upload via REST API if found. See `/post-spotlight` skill for the curl command.

## Step 6: Report

Tell Jamie: Post ID, title, what's complete, what has placeholders, whether image was attached, and remind about media folder assignment.
