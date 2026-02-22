---
name: author-info
description: Extract author bio and social links from the Vellum file. Use when Jamie asks for author info, or when building a blog post that needs a bio. Pass the author name as the argument.
user_invocable: true
---

# Author Info

Extract author bio and social links from the Vellum master file and format for WordPress.

## Usage

`/author-info <author name>`

Examples:
- `/author-info Steve Vernon`
- `/author-info Anthea Sharp`
- `/author-info --list` (list all available authors)

## Step 1: Extract from Vellum

Run the extraction script:

```bash
python3 /Users/jamieferguson/Dropbox/dev/pub-tools/scripts/extract-vellum-author.py --json "<author name>"
```

For a list of all authors:
```bash
python3 /Users/jamieferguson/Dropbox/dev/pub-tools/scripts/extract-vellum-author.py --list
```

The script reads from:
```
~/Dropbox/Jamie/Writing and Publishing/Blackbird Publishing/Publishing/Book files : formatting/Info to reuse/Author and Collection Information.vellum
```

## Step 2: Format for WordPress

Convert the extracted data to Gutenberg blocks with HTML entities.

### Bio Block

```html
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">About the Author</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>[Bio text with HTML entities for special characters]</p>
<!-- /wp:paragraph -->
```

Use HTML entities for all special characters (see CLAUDE.md table).

### Social Links

If the author has a website URL in their bio text, extract it. Format social links as a paragraph after the bio:

```html
<!-- wp:paragraph -->
<p>Find out more about [First Name] at <a href="https://example.com" rel="noopener" target="_blank">example.com</a></p>
<!-- /wp:paragraph -->
```

If additional social profiles exist, list them:

```html
<!-- wp:paragraph -->
<p>Connect with [First Name]: <a href="https://facebook.com/..." rel="noopener" target="_blank">Facebook</a> · <a href="https://bookbub.com/..." rel="noopener" target="_blank">BookBub</a> · <a href="https://goodreads.com/..." rel="noopener" target="_blank">Goodreads</a> · <a href="https://amazon.com/..." rel="noopener" target="_blank">Amazon</a></p>
<!-- /wp:paragraph -->
```

**Social link display order:** Website (from bio text) first, then: Facebook, Instagram, BookBub, Goodreads, Amazon, X, Bluesky, others alphabetically.

**Omit empty social links** (some authors have platform keys with blank values).

### Bio Text Cleanup

The raw bio may contain:
- `\u2029` (paragraph separator) — replace with paragraph breaks (new `<!-- wp:paragraph -->` blocks)
- `\u00a0` (non-breaking space) — replace with regular space
- Trailing whitespace — trim
- "Find out more about [name] at: URL" lines — extract the URL for the social links block, remove from bio text

**Do not edit the author's words, voice, or spellings.** Only convert formatting.

## Step 3: If Multiple Bios Exist

Some authors have multiple bio variants (e.g., fiction vs. non-fiction). The JSON output includes a `label` field for each bio. Present all variants to Jamie and ask which one to use, or default to the unlabeled "bio" entry.

## Step 4: Report

Tell Jamie:
- Author name and last-updated date from Vellum
- The formatted bio (Gutenberg blocks ready to paste)
- Social links found
- If the bio looks stale (last_updated more than a year ago), mention it
