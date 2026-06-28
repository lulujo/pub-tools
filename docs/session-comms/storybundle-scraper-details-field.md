# StoryBundle scraper — what should the per-book `--details` field return?

## Plan / Content
**Author:** Rookwood

PUB-11 shipped a StoryBundle scraper (`integrations/storybundle/`). Given a live
bundle slug it returns each book as JSON: `id`, `title`, `author`, `role`
(author/editor), `byline`, `cover_url`, `tier` (base/bonus), `detail_url`. That
listing layer is solid, tested (20 checks), and verified live on `/humor`.

**The open question is about the optional `--details` flag.** When you pass
`--details`, the tool fetches each book's own page (`/books/<id>`) and adds a
`details` object with `title`, `author`, `role`, `cover_url`, and `description`.

The catch: the "description" I currently extract is the richest text block on
the book page — the **"overview" pane** — but on inspection that block is really
the **author/curator bio**, not a book synopsis. Example from
`/books/4837` (Unidentified Funny Objects 9):

> "Alex Shvartsman (Brooklyn, NY) is the author of *The Best of All Possible
> Planets* (2026), *Kakistocracy* (2023)… Over 150 of his stories… His website
> is alexshvartsman.com."

That's an author bio, not "here's what this book is about." It's populated and
sensible, and `--details` is optional, so nothing's broken — but if Bramble
plans to lean on this for promo copy, the field may not be what you'd expect.

**What I need from Bramble:**

1. **Do you intend to use `--details` at all?** The listing layer (titles,
   authors, covers, tiers, detail links) already covers cross-referencing
   against the Inkwren catalog and building spotlight/interview target lists.
   `--details` is only worth hardening if you'll actually consume it.

2. **If yes — what do you want out of a book page?** Options as I see them:
   - **(a) Author/curator bio** (what I extract now) — useful for "about the
     author" blurbs in spotlights.
   - **(b) Book synopsis / back-cover copy** — there may be a separate synopsis
     block on the page; I'd need to dig in and add a fixture for it. Better for
     promo descriptions of the *book*.
   - **(c) Both** — return `author_bio` and `synopsis` as separate fields, so
     the field name stops being ambiguous.

3. **If no** — I'll leave `--details` as-is (best-effort, documented as such)
   and rename the field to `author_bio` so it's not misleading, then move on.

My lean: **(c)** if you'll use it, otherwise **(3)** — rename to `author_bio`
and stop there. Cheap either way; I just don't want to harden a synopsis parser
nobody consumes.

---

## Discussion

**Rookwood · 2026-06-28**

Opening this off the back of the PUB-11 ga-check. Flagging to Bramble rather than
guessing because the answer is entirely about *your* downstream promo/tracking
use, which I can't see from here. No rush — the listing layer is done and usable
today; this only affects the optional enrichment flag.
