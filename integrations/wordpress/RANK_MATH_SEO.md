# Rank Math SEO via REST (PUB-6)

Status: **Done & live** as of 2026-06-28. Rank Math SEO meta fields are now readable and
writable through the WordPress REST API on blackbirdpublishing.com.

## What made this work

Rank Math does **not** expose its per-post SEO fields to REST by default. A small PHP snippet
registers them with `show_in_rest`. The canonical copy of the snippet is
[`rank-math-rest-snippet.php`](rank-math-rest-snippet.php).

It is **live** in the Blackbird **Kadence child theme**:
`wp-content/themes/kadence-child/functions.php`

> History: the snippet must live in the *active* theme. Blackbird's active theme is **Kadence**
> (a third-party theme that auto-updates), so we created a **Kadence child theme** to hold custom
> PHP/CSS that survives Kadence updates. Do **not** put snippets in the Kadence parent theme (wiped
> on update) or in `blackbirdtwentyseventeen` (dormant, not active). See handoff-2026-06-28.

## The four fields

| Meta key | Purpose |
|---|---|
| `rank_math_title` | SEO title (usually leave unset — see below) |
| `rank_math_description` | Meta description (≤ 155 chars) |
| `rank_math_focus_keyword` | Focus keyword |
| `rank_math_canonical_url` | Canonical URL (usually leave unset — WP self-canonicalizes) |

**Set only `rank_math_description` + `rank_math_focus_keyword` for normal posts.** Rank Math's
global title template already turns our descriptive post titles ("Story Spotlight: X by Y") into a
correct SEO title, so an explicit `rank_math_title` is redundant. Leave `rank_math_canonical_url`
empty unless a post genuinely needs a non-self canonical.

## SEO defaults for spotlights & interviews

These are the agreed templates (used for the Haunted Waters backfill; apply to all future posts):

- **Focus keyword** = the **story title** (unique per post; avoids Rank Math's "same keyword" warning).
- **Spotlight description:**
  `{Author}’s {Story}—a story spotlight from {Anthology}[, an anthology of <genre> from Blackbird Publishing].`
- **Interview description:**
  `{Author} on writing {Story} for {Anthology}—an author interview from Blackbird Publishing.`

Rules: keep descriptions **≤ 155 chars** (drop the trailing "from Blackbird Publishing" tagline on long
titles); curly apostrophes and em dashes are fine (they round-trip exactly in post meta — verified);
no quotation marks around the story title (cleaner in the `<meta>` tag); use "and" not "&".

`{Anthology}` is the launch post's title, e.g. Haunted Waters → "Haunted Waters: 15 Tales from the Depths".

## How to set the fields (REST — MCP can't do post meta)

MCP `create_post`/`update_post` cannot write meta. After creating the post (via MCP or REST),
PATCH the meta with a direct REST call. Always: `User-Agent` header, strip spaces from the app
password, retry on 5xx.

```bash
source /Users/jamieferguson/Dropbox/dev/pub-tools/.env
WP_PASS=$(echo "$CLAUDE_BLACKBIRD_WP_PASSWORD" | tr -d ' ')
curl -s -X POST "https://blackbirdpublishing.com/wp-json/wp/v2/posts/<POST_ID>" \
  -u "claude:${WP_PASS}" -H 'User-Agent: pub-tools' -H 'Content-Type: application/json' \
  --data '{"meta":{"rank_math_focus_keyword":"...","rank_math_description":"..."}}'
```

Always **read back** (`GET /posts/<id>?context=edit` → `.meta`) and compare to confirm the write stuck.

## Backfilling old posts (reusable)

Going forward, the posting skills set SEO automatically, so no manual work is needed. For the
historical backlog (one anthology at a time), use the committed helper:

```
# Anthology spotlights/interviews ("Title" by Author):
python3 integrations/wordpress/seo_backfill.py --tag <TAG_ID> --anthology "Anthology: Subtitle" [--apply]
# StoryBundle author interviews ("Author on Title"):
python3 integrations/wordpress/seo_backfill.py --tag <TAG_ID> --anthology "Bundle Name" --bundle [--apply]
```

Without `--apply` it prints the proposed focus keyword + description for every post tagged `<TAG_ID>`
that lacks SEO (a dry run). With `--apply` it writes them and verifies each round-trip. It skips
posts that already have Rank Math data, and any title it can't parse (panels, roundups — handle those
by hand). Anthology/bundle tag IDs live in
[the spotlight skill](../../.claude/skills/post-spotlight/SKILL.md) (e.g. Haunted Waters = 378,
Escape from 2026 = 393, Write Stuff = 387).

**Done so far:** all **2026** spotlight/interview posts —
Haunted Waters (tag 378, 27 posts) + Write Stuff (tag 387, 10) + Escape from 2026 (tag 393, 12),
backfilled 2026-06-28. (One panel post, 5749, hand-written; the dup draft 5480 left for deletion.)
**Not backfilled (optional):** ~200 pre-2026 spotlight/interview posts across ~20 older anthologies
(Haunted Places, Haunted, Wild Magic, Realm of Faerie, Ever After, Beneath the Waves, etc.). These
are years old and Rank Math's fallback template already covers them, so low priority. Mixed title
formats + a couple of title bugs (e.g. 5199/5206 read "Interview: Story Spotlight: …") mean a future
pass should review the dry run before applying.
