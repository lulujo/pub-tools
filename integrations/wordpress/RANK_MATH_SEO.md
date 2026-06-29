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
# A different site (default is blackbird):
python3 integrations/wordpress/seo_backfill.py --site borogrove --tag <TAG_ID> --anthology "..." [--apply]
```

Without `--apply` it prints the proposed focus keyword + description for every post tagged `<TAG_ID>`
that lacks SEO (a dry run). With `--apply` it writes them and verifies each round-trip. It skips
posts that already have Rank Math data, and any title it can't parse (panels, roundups — handle those
by hand). Anthology/bundle tag IDs live in
[the spotlight skill](../../.claude/skills/post-spotlight/SKILL.md) (e.g. Haunted Waters = 378,
Escape from 2026 = 393, Write Stuff = 387).

**Done so far:** all **2025 + 2026** spotlight/interview posts (75) —
Haunted Waters (tag 378, 27) + Write Stuff (tag 387, 10) + Escape from 2026 (tag 393, 12) +
Haunted Places (tag 367, 26), backfilled 2026-06-28. (Panel post 5749 hand-written; dup draft 5480
left for deletion.)
**Not backfilled (optional):** ~174 **pre-2025** spotlight/interview posts across ~20 older anthologies
(Haunted, Wild Magic, The Golden Door, Realm of Faerie, Ever After, Beneath the Waves, Faerie Summer,
Witches' Brew, etc.). Years old and covered by Rank Math's fallback, so low priority. Mixed title
formats + some untagged posts mean a future pass should review the dry run before applying. The script
now strips a nested "Story Spotlight:/Interview:" prefix (title bug seen on 5199/5206), but those two
posts still have the wrong **display title** — fix the titles separately if desired.

## Porting to another WordPress site (Borogrove, jamieferguson.com, a friend's site)

Everything above was done on Blackbird. The capability is per-site (each site needs its own snippet
in its own active theme). To repeat it on another site, run this checklist. `seo_backfill.py` already
knows the three sites (`--site blackbird|borogrove|jamie`); add new ones to its `SITES` map.

1. **Confirm Rank Math is installed + active** on the target site (Plugins screen). If it isn't, this
   whole approach doesn't apply — there are no `rank_math_*` fields to expose.
2. **Find the active theme** (Appearance → Themes, or MCP `get_site`). Decide where the snippet lives:
   - **Active theme is a custom/child theme already** → append the snippet to its `functions.php`.
   - **Active theme is a third-party theme that updates** (Kadence, Astra, GeneratePress, …) → create a
     **child theme** for it first, exactly like Blackbird's `kadence-child` (see
     `…/themes/kadence-child/` for a worked example: `style.css` with `Template: <parent-slug>`, a
     `functions.php` that enqueues the child style, **and the one-time `after_switch_theme` hook that
     copies the parent's theme-mods so activation doesn't reset Customizer settings/menus/Additional CSS**).
     Put the snippet in that child theme. Never edit the parent (wiped on update) or WP core.
3. **Deploy + activate** the theme change via SFTP/host (theme files are **not** REST-editable). If you
   created a child theme, back up the parent's settings first if there's no export (the migration hook
   covers theme-mods, but eyeball widgets after activating).
4. **Add credentials to `.env`**: `CLAUDE_<SITE>_WP_PASSWORD` (app password for that site's `claude`
   user, who needs an editor-capable role). Borogrove/jamie vars already exist; see CLAUDE.md.
5. **Verify the REST round-trip** before trusting it: create a throwaway draft, set the four
   `rank_math_*` fields, `GET …?context=edit` to confirm they persisted, then delete the draft.
   (`scratchpad/pub6_test.py` from 2026-06-28 is the template; point it at the new site's base URL.)
6. **Backfill** with `seo_backfill.py --site <site> --tag <id> --anthology "…"` (tag IDs are **per-site**
   — look them up on that site, they will not match Blackbird's).
7. **Wire SEO into that site's posting flow.** The `post-spotlight`/`post-interview`/`post-bundle-interview`
   skills are Blackbird-specific today; if the new site gets the same kind of content, give it equivalent
   skill steps (or generalize the skills to take a `--site`).

**Per-site gotchas:** Borogrove forces trailing slashes, so REST must use the `?rest_route=` form —
`seo_backfill.py` handles this automatically for `--site borogrove` (see its `url()` / `SITES`). Each
site has its own active theme, so the snippet's home differs site to site.
