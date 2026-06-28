#!/usr/bin/env python3
"""Scrape a StoryBundle's contents (books, authors, covers, detail links).

Given a bundle slug (e.g. 'humor', 'timetravel'), fetch the live bundle page
and return the list of books as JSON -- id, title, author, byline, cover URL,
tier, and detail link. With --details, also fetch each per-book page for a
fuller description.

Why this exists (and why it has to run WHILE the bundle is live):

  - An ACTIVE bundle page (https://storybundle.com/<slug>) is server-rendered
    STATIC HTML containing the full book list. A plain HTTP GET + tolerant
    HTML parse works -- no headless browser, no JS rendering needed.
  - A per-book page (https://storybundle.com/books/<id>) is ALSO static HTML
    with title/author/cover, an author bio, and the book's synopsis in the
    body (the bio and synopsis are separate page blocks -- we keep them as
    separate fields).
  - EXPIRED bundles are stripped to a JS shell with ZERO book links in the
    raw HTML. You CANNOT recover the data after the bundle ends -- so pull it
    during the promo window.
  - There is no clean JSON endpoint (<slug>.json returns HTTP 500). HTML
    parsing is the only path.

The markup can change without notice, so the parser is deliberately tolerant
(regex over a few stable anchors rather than exact structure) and pinned by
test_storybundle.py against saved fixtures -- same discipline as the
md_to_gutenberg.py suite next door. If StoryBundle redesigns and the parser
returns zero books, the tests will catch it; re-save a fresh fixture and
adjust the anchors.

Each book in the listing looks like (whitespace trimmed):

    <li class="book">
      <a class="book_detail_link" data-name="Title"
         href="https://storybundle.com/books/4827"><img src="<cover>" /></a>
      <span class="bonus tier_1"><img .../></span>        # bonus-tier only
      <span>
        <a class="book_detail_link book_name" ...>Title</a>
      </span>
      <em>by Author</em>                                  # or "edited by ..."
    </li>

Usage:
    # List a live bundle's books as JSON:
    python3 storybundle.py humor

    # Also fetch each book's detail page (slower; one GET per book):
    python3 storybundle.py humor --details

    # Pretty-print and save:
    python3 storybundle.py humor --pretty -o humor_bundle.json
"""

import argparse
import html as _html
import json
import re
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "https://storybundle.com"
USER_AGENT = "pub-tools-storybundle/1.0 (+https://blackbirdpublishing.com; Jamie Ferguson)"

# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------


def fetch(url, *, retries=3, backoff=2.0):
    """GET a URL with a polite User-Agent and retry on transient 5xx.

    WPEngine/Cloudflare-style stacks occasionally throw 522/525; StoryBundle
    is a different host but the same courtesy applies. A missing UA gets some
    CDNs to 1010 you, so always send one.
    """
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            # 5xx are worth retrying; 4xx (404 bad slug, 500 .json) are not.
            if 500 <= exc.code < 600 and attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
                continue
            raise
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"unreachable: exhausted retries for {url}")


# --------------------------------------------------------------------------
# Parsing -- bundle listing
# --------------------------------------------------------------------------

# Each book is one <li class="book"> ... </li>. Split on the opening tag and
# keep everything up to the next one (the trailing </li></ul> on the last
# entry is harmless -- we only read stable anchors out of each chunk).
_LI_BOOK = re.compile(
    r'<li\s+class="book">(.*?)(?=<li\s+class="book">|</ul>|\Z)', re.S
)

# Inside a chunk: the /books/<id> detail link, the data-name (cleanest title
# source), the cover <img src>, the byline <em>, and the bonus-tier marker.
_BOOK_HREF = re.compile(r'href="(https?://[^"]*?/books/(\d+))"')
_DATA_NAME = re.compile(r'data-name="([^"]*)"')
_COVER_IMG = re.compile(r'<img[^>]*\bsrc="([^"]*?/book_covers/[^"]*)"')
_BYLINE = re.compile(r"<em>(.*?)</em>", re.S)
_BONUS_TIER = re.compile(r'class="bonus\s+tier_(\d+)"')

# Byline prefixes StoryBundle uses; strip to get a bare author, keep the role.
_BYLINE_PREFIX = re.compile(
    r"^(written and illustrated by|written by|edited by|compiled by|by)\s+",
    re.I,
)


def _clean(text):
    """Collapse whitespace and decode HTML entities to plain text."""
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", _html.unescape(text)).strip()


def parse_byline(raw):
    """Split an <em> byline into (role, author).

    'by Gini Koch'            -> ('author', 'Gini Koch')
    'edited by Alex Shvartsman'-> ('editor', 'Alex Shvartsman')
    """
    text = _clean(raw)
    match = _BYLINE_PREFIX.match(text)
    if not match:
        return ("author", text)
    prefix = match.group(1).lower()
    author = text[match.end():].strip()
    role = "editor" if prefix.startswith("edited") else "author"
    return (role, author)


def parse_bundle(html):
    """Parse a bundle listing page into a list of book dicts.

    Returns [] if no books are found -- which is exactly what happens on an
    EXPIRED bundle (JS shell, no server-rendered list). Callers should treat
    an empty result as "too late / wrong slug", not "bundle has no books".
    """
    books = []
    seen = set()
    for chunk in _LI_BOOK.finditer(html):
        block = chunk.group(1)

        href_match = _BOOK_HREF.search(block)
        if not href_match:
            # Non-book entry (e.g. an 'amazon' data-name with no /books/ href).
            continue
        detail_url, book_id = href_match.group(1), href_match.group(2)
        if book_id in seen:
            continue
        seen.add(book_id)

        name_match = _DATA_NAME.search(block)
        title = _clean(name_match.group(1)) if name_match else None

        cover_match = _COVER_IMG.search(block)
        cover_url = cover_match.group(1) if cover_match else None

        byline_match = _BYLINE.search(block)
        if byline_match:
            role, author = parse_byline(byline_match.group(1))
            byline = _clean(byline_match.group(1))
        else:
            role, author, byline = "author", None, None

        tier_match = _BONUS_TIER.search(block)
        tier = "bonus" if tier_match else "base"

        books.append(
            {
                "id": book_id,
                "title": title,
                "author": author,
                "role": role,
                "byline": byline,
                "cover_url": cover_url,
                "tier": tier,
                "detail_url": detail_url,
            }
        )
    return books


# --------------------------------------------------------------------------
# Parsing -- per-book detail page
# --------------------------------------------------------------------------

_BOOK_TITLE = re.compile(r"<title>(.*?)\s*-\s*StoryBundle</title>", re.S)
# The book page repeats the title + byline in an <h2> at the top of the body.
_BOOK_H2 = re.compile(r"<h2[^>]*>\s*(.*?)<em>(.*?)</em>", re.S)
# The FIRST scrolling "overview" pane (right after the cover) is the author /
# curator bio -- NOT the book's synopsis. Keep them as separate fields so a
# bio never gets mistaken for book promo copy (Bramble's call -- see the
# storybundle-scraper-details-field comms thread).
_BOOK_AUTHOR_BIO = re.compile(r'class="overview"[^>]*>(.*?)</div>\s*</div>', re.S)
# The book's own synopsis lives in <div class="description"> inside the
# book_section_wrapper. Best-effort: treated as reference context, not output
# (house style doesn't lift scraped synopsis text verbatim into promo).
_BOOK_SYNOPSIS = re.compile(r'<div\s+class=[\'"]description[\'"]>(.*?)</div>', re.S)
_BOOK_COVER = re.compile(r'(https?://[^"\']*?/book_covers/\d+/[^"\'\s]+)')


def parse_book(html):
    """Parse a per-book detail page into a dict (best-effort, tolerant).

    `author_bio` and `synopsis` are deliberately distinct: the first text pane
    on a StoryBundle book page is the author/curator bio, while the book's own
    blurb sits in a separate `description` div. A field named "description"
    holding a bio is a latent bug (it reads as book copy), so we name them for
    what they actually are. `synopsis` is best-effort and may be None.
    """
    title_match = _BOOK_TITLE.search(html)
    title = _clean(title_match.group(1)) if title_match else None

    h2_match = _BOOK_H2.search(html)
    if h2_match:
        if not title:
            title = _clean(h2_match.group(1))
        role, author = parse_byline(h2_match.group(2))
    else:
        role, author = "author", None

    cover_match = _BOOK_COVER.search(html)
    cover_url = cover_match.group(1) if cover_match else None

    bio_match = _BOOK_AUTHOR_BIO.search(html)
    author_bio = _clean(bio_match.group(1)) if bio_match else None

    synopsis_match = _BOOK_SYNOPSIS.search(html)
    synopsis = _clean(synopsis_match.group(1)) if synopsis_match else None

    return {
        "title": title,
        "author": author,
        "role": role,
        "cover_url": cover_url,
        "author_bio": author_bio,
        "synopsis": synopsis,
    }


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def scrape_bundle(slug, *, details=False, delay=1.0):
    """Fetch and parse a bundle; optionally enrich with per-book detail."""
    url = f"{BASE_URL}/{slug.strip('/')}"
    books = parse_bundle(fetch(url))

    if details:
        for i, book in enumerate(books):
            if i:
                time.sleep(delay)  # be polite between detail fetches
            try:
                book["details"] = parse_book(fetch(book["detail_url"]))
            except (urllib.error.URLError, urllib.error.HTTPError) as exc:
                book["details"] = {"error": str(exc)}

    return {"slug": slug.strip("/"), "url": url, "count": len(books), "books": books}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Scrape a live StoryBundle's contents to JSON.",
    )
    parser.add_argument("slug", help="bundle slug, e.g. 'humor' or 'timetravel'")
    parser.add_argument(
        "--details",
        action="store_true",
        help="also fetch each book's detail page (one GET per book)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="seconds between per-book detail fetches (default 1.0)",
    )
    parser.add_argument("--pretty", action="store_true", help="indent the JSON output")
    parser.add_argument("-o", "--output", help="write JSON here instead of stdout")
    args = parser.parse_args(argv)

    try:
        result = scrape_bundle(args.slug, details=args.details, delay=args.delay)
    except urllib.error.HTTPError as exc:
        sys.exit(f"error: HTTP {exc.code} fetching bundle '{args.slug}' ({exc.reason})")
    except urllib.error.URLError as exc:
        sys.exit(f"error: could not reach StoryBundle: {exc.reason}")

    if result["count"] == 0:
        # Empty almost always means an expired bundle (JS shell) or bad slug.
        print(
            f"warning: 0 books parsed for '{args.slug}'. The bundle may have "
            "ended (expired pages are JS-only and cannot be scraped) or the "
            "slug may be wrong.",
            file=sys.stderr,
        )

    text = json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
        print(f"wrote {result['count']} books to {args.output}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
