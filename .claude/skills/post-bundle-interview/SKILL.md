---
name: post-bundle-interview
description: Create StoryBundle author-interview drafts on Blackbird Publishing from Bramble's markdown (Escape from 2026, Write Stuff, future bundles). Per-author featured banner + book cover + inline bundle CTA banner. Use when Jamie or Bramble hands off bundle interview posts. Pass the author name(s) or .md path(s).
---

# Post Bundle Interview

**This is a format conversion task, not a creative writing task.** The content is written and approved by Bramble. Convert format, upload images, create the draft, verify, report. Preserve author voice verbatim — do not edit word choices, spellings (Canadian: harbour, favourite), coinages, or approved profanity/politics. Move quickly.

This skill is for **StoryBundle author interviews** (per-author featured banner, individual book cover near the top, a shared bundle CTA banner at the bottom). For Haunted Waters interviews/spotlights that use a by-reference CTA pattern, use `/post-interview` or `/post-spotlight` instead.

The conversion + WordPress writes are done by a committed, tested script — **do not rebuild a converter in /tmp**:

- Engine: `integrations/wordpress/md_to_gutenberg.py`
- Tests: `integrations/wordpress/test_md_to_gutenberg.py` (run after any change to the engine)

## Usage

`/post-bundle-interview <author name, or path(s) to interview_post.md>`

## Step 1: Read the request and source files

Bramble's requests live in `~/Dropbox/dev/publishing/docs/session-comms/rookwood-<bundle>-interviews.md`. Each post has a markdown file (current convention: `projects/<bundle>/authors/ready to publish/<author>/interview_post.md`). Read the thread entry for: title, book title, banner path, cover path, alt texts, author tag, and any voice notes.

**Clean-posts convention (current):** posts arrive publish-ready with **no `[JAMIE: ...]` flags** and no placeholders. Do not add reviewer notes to the body. (Older posts left a `[JAMIE:]` socials flag to preserve — the engine's `verify()` flags any that leak through, so you'll catch a regression either way.)

## Step 2: Know the per-bundle constants

| Bundle | Series tag | Bundle CTA banner (media ID) |
|---|---|---|
| Escape from 2026 StoryBundle | 393 | 5698 |
| Write Stuff StoryBundle | 387 | 5620 |

- Category: **Interviews (4)**. Author: **Blackbird Publishing (2)**.
- Get the bundle banner's `source_url` once: `GET /wp-json/wp/v2/media/<id>?_fields=source_url`.
- If a new bundle has no CTA banner yet, upload one (1200×675 has rendered well) and record its ID on the thread.

## Step 3: Build a batch config

Write a JSON config (one entry per post — batches of 1–3 are normal):

```json
{
  "rest": {"base": "https://blackbirdpublishing.com/wp-json/wp/v2", "user": "claude"},
  "defaults": {
    "category": 4, "author": 2, "series_tag": 393,
    "bundle_banner_id": 5698,
    "bundle_banner_url": "https://blackbirdpublishing.com/wp-content/uploads/2026/06/escape-from-2026-bundle-banner-1200x675-1.png",
    "bundle_banner_alt": "Escape from 2026 StoryBundle: 15 exclusive books of alternate history and time travel, available at storybundle.com/timetravel",
    "cover_width_px": 300, "reuse_media": true
  },
  "posts": [
    {
      "interview_md": "/Users/jamieferguson/Dropbox/dev/publishing/projects/escape_from_2026/authors/ready to publish/doug_smith/interview_post.md",
      "title": "Interview: Douglas Smith on Into the Time Slip",
      "slug": "interview-douglas-smith-into-the-time-slip",
      "banner": ".../blog_header_images/douglas_smith.png",
      "banner_alt": "Interview with Douglas Smith — Into the Time Slip — Escape from 2026 StoryBundle",
      "cover": ".../All Covers/Into the Time Slip Cover Final.jpg",
      "cover_alt": "Cover of Into the Time Slip by Douglas Smith",
      "author_tag": "Douglas Smith",
      "excerpt": "<optional 1–2 sentence excerpt, HTML entities ok>"
    }
  ]
}
```

Notes:
- **Title:** `Interview: <Author> on <Book Title>` — plain text (WordPress titles don't render HTML, so no italics).
- **Slug:** `interview-<author>-<book-title>`, lowercase-hyphenated.
- **Banners** live at the project root: `projects/<bundle>/blog_header_images/<author>.png`. **Covers:** `projects/<bundle>/All Covers/<Book Title> Cover Final.jpg` (filenames vary — copy the exact path from the thread; odd capitalization like "FInal" is fine, WordPress normalizes the URL).
- `author_tag` is the display name; the engine finds it or creates it (search is case-insensitive). Don't pre-create tags.
- The engine sets `featured_media` to the banner and places the cover (resized to `cover_width_px`) at the top.

## Step 4: Dry-run, then create

```bash
cd /Users/jamieferguson/Dropbox/dev/pub-tools
# 1) Convert + self-check, write nothing to WordPress:
python3 integrations/wordpress/md_to_gutenberg.py --config /tmp/<bundle>_batch.json --dry-run
# 2) If every post reports "checks: clean", create the drafts:
python3 integrations/wordpress/md_to_gutenberg.py --config /tmp/<bundle>_batch.json
```

The engine: uploads banner + cover (with retry on transient 5xx, and **reuses** an already-uploaded file of the same name so a re-run after a failure doesn't duplicate media), finds/creates the author tag, converts + assembles the body, runs `verify()`, and **refuses to create a post that fails its own checks** or whose slug already exists. It prints the post ID, media IDs, tag, and permalink for each.

`verify()` catches: stray markdown `*`, an opening quote mis-rendered as a closing `&rdquo;`, a leaked `[JAMIE:]` flag, and leaked image-meta lines. If it flags something, fix the engine (and add a test case) — don't hand-patch the post.

## Step 5: Report and reply on the thread

In the session and on the Bramble thread, give per post: **post ID, the will-be permalink** (`https://blackbirdpublishing.com/<slug>/`, live once Jamie publishes), media IDs, author tag (and whether newly created), and confirmation that voice notes were honored. Provide live permalinks for any posts Jamie has since published (the tracker + each `social.md` need them). Remind Jamie that WP Media folders are assigned manually (taxonomy not API-accessible).

Drafts only — **never publish.** Jamie reviews and publishes.
