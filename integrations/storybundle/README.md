# StoryBundle scraper

Pull a StoryBundle's contents (books, authors, covers, detail links) for promo,
tracking, and cross-referencing against the Inkwren catalog.

stdlib-only Python — no dependencies, no headless browser. Same tolerant,
fixture-tested style as `integrations/wordpress/md_to_gutenberg.py`.

## Why it must run while the bundle is live

- An **active** bundle page (`https://storybundle.com/<slug>`) is server-rendered
  static HTML with the full book list embedded. A plain GET + HTML parse works.
- An **expired** bundle is stripped to a JS shell — the raw HTML has **zero**
  book links. You cannot recover the data after the bundle ends.
- There is no JSON endpoint (`<slug>.json` returns HTTP 500).

**Implication:** scrape during the promo window. An empty result almost always
means the bundle has ended (or the slug is wrong) — the CLI warns when it
parses zero books.

## Usage

```bash
# List a live bundle's books as JSON (one GET):
python3 storybundle.py humor

# Pretty-print and save:
python3 storybundle.py humor --pretty -o humor_bundle.json

# Also fetch each book's detail page for a fuller description (one GET/book):
python3 storybundle.py humor --details
```

### Output shape

```json
{
  "slug": "humor",
  "url": "https://storybundle.com/humor",
  "count": 15,
  "books": [
    {
      "id": "4827",
      "title": "Touched by an Alien",
      "author": "Gini Koch",
      "role": "author",                 // or "editor"
      "byline": "by Gini Koch",
      "cover_url": "https://storybundle.com/system/book_covers/4827/...jpg",
      "tier": "base",                    // "base" or "bonus" (bonus-tier unlock)
      "detail_url": "https://storybundle.com/books/4827"
    }
  ]
}
```

With `--details`, each book gains a `"details"` object: `title`, `author`,
`role`, `cover_url`, `author_bio`, and `synopsis`.

`author_bio` and `synopsis` are **separate fields on purpose**: the first text
pane on a StoryBundle book page is the author/curator bio, while the book's own
blurb sits in a separate block. A single field named "description" holding a bio
reads as book copy and invites mistakes, so they're named for what they are.
`synopsis` is **best-effort** (may be `null`) and is intended as drafting
*reference*, not promo output — per house style we don't lift scraped synopsis
text verbatim.

## Tests

```bash
python3 test_storybundle.py
```

Tests parse against committed HTML fixtures in `fixtures/` (captured 2026-06-27
from the live `/humor` bundle and `/books/4837`) rather than the network — the
markup can change without notice and expired bundles can't be re-captured. The
pre-commit hook (`.githooks/pre-commit`) runs these automatically when the
engine or tests are staged.

**If the parser ever returns zero books for a live bundle**, StoryBundle has
likely changed its markup: re-capture a fresh fixture (`curl -A '<UA>'
https://storybundle.com/<slug> -o fixtures/<slug>_bundle.html`) and adjust the
regex anchors in `storybundle.py`.
