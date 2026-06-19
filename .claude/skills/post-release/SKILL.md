---
name: post-release
description: Create a new release / launch post for an anthology on Blackbird Publishing. Use when Jamie says to create a launch post or release announcement. Pass the anthology name as the argument.
---

# Post Release

Create a WordPress draft release announcement for a new anthology on blackbirdpublishing.com.

## Usage

`/post-release <anthology name>`

Examples:
- `/post-release Haunted Waters`
- `/post-release Haunted Shores`

## Reference Posts

These published release posts define the format:

| Anthology | Post ID | Slug |
|-----------|---------|------|
| Haunted Waters | 5399 | `haunted-waters-15-tales-from-the-depths` |
| Haunted Places | 5313 | `haunted-places-stories-of-memory-mystery-and-haunting` |

Use `mcp__blackbird-wp__get_post` to pull one as a structural reference if needed.

## Step 1: Gather Information

Ask Jamie for (or locate in Dropbox):
- **Anthology title and subtitle**
- **Series context** (e.g., "Volume 3 of The Haunted Anthology series")
- **Theme/mood** — what's the atmospheric hook?
- **Number of stories**
- **Author list** — full names, in the order they appear in the book
- **Universal buy link** (books2read.com URL)
- **Cover image** — path to the ebook cover file
- **Cover image media ID** — if already uploaded to WordPress

If a CTA pattern already exists for this anthology, use it. If not, tell Jamie you can provide the block markup for her to create one.

## Step 2: Write the Post Content

Follow this structure (matching the established Blackbird launch post format):

### Block Structure

```
1. <!-- wp:heading -->        Atmospheric section title (2-4 words, evocative)
2. <!-- wp:paragraph -->      Hook lines (short, punchy, 2-3 sentences setting mood)
3. <!-- wp:paragraph -->      Anthology description (what the book is, series context, theme)
4. <!-- wp:paragraph -->      Tagline (one atmospheric line)
5. <!-- wp:paragraph -->      "Featuring stories by:" + full author list
6. <!-- wp:paragraph -->      Buy link: <a href="...">Buy the book from your favorite store</a>
7. <!-- wp:image -->           Cover image, centered, 300px wide (or CTA pattern reference)
8. <!-- wp:heading -->        "Coming Soon"
9. <!-- wp:paragraph -->      Teaser for Story Spotlights
10. <!-- wp:paragraph -->     Teaser for Author Interviews
11. <!-- wp:paragraph -->     Closing atmospheric hook (2-3 sentences)
```

### Tone and Style

- **Atmospheric, not salesy.** These read like invitations, not advertisements.
- **Short paragraphs.** Often single sentences for dramatic effect.
- **Theme-forward.** Lead with the emotional/mythic resonance, not plot summaries.
- **The "Coming Soon" section** teases spotlights and interviews that will follow over the next weeks.
- **Closing hook** ties back to the anthology's central theme with a final evocative line.

### Special Characters

Always use HTML entities (see CLAUDE.md for the full table):
- Curly quotes: `&ldquo;` `&rdquo;` `&lsquo;` `&rsquo;`
- Em dash: `&mdash;`
- Ellipsis: `&hellip;`

### Cover Image

If using the CTA pattern (which includes buy link + cover), insert via reference:
```
<!-- wp:block {"ref":PATTERN_ID} /-->
```

If no pattern exists yet, use a standalone image block:
```
<!-- wp:image {"id":MEDIA_ID,"width":"300px","sizeSlug":"full","linkDestination":"none","align":"center"} -->
<figure class="wp-block-image aligncenter size-full is-resized">
  <img src="IMAGE_URL" alt="DESCRIPTION" class="wp-image-MEDIA_ID" style="width:300px"/>
</figure>
<!-- /wp:image -->
```

## Step 3: Create the Draft

Use `mcp__blackbird-wp__create_post` with:
- `title`: `Anthology Title&mdash;Subtitle` (em dash between title and subtitle)
- `content`: Gutenberg block markup from Step 2
- `status`: `draft` (NEVER publish without Jamie's approval)
- `slug`: `anthology-title-subtitle-words` (lowercase, hyphens)
- `categories`: `[16]` (New Releases)
- `tags`: anthology tag ID if one exists
- `author`: `2` (Blackbird Publishing). Posts default to the `claude` user otherwise, which isn't visible in the editor UI but shows on the published post. Always set this.

**Title note:** Use an em dash (`&mdash;`) between title and subtitle: "Haunted Waters&mdash;15 Tales from the Depths". This matches Jamie's house style (em dashes, no spaces).

## Step 4: Featured Image

Release posts use the promo image (1200x628), NOT the book cover (that goes in the post body). Upload via REST API if a local promo image is provided. See `/upload-image` skill.

## Step 5: Report

Tell Jamie:
- Post ID and title
- Whether the CTA pattern was used or if she needs to create one
- Whether featured image was attached
- Remind about media folder assignment
