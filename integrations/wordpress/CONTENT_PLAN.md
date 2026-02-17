# WordPress Content Plan

## Target Site

**Blackbird Publishing** — blackbirdpublishing.com (WPEngine)

Other sites (author site, etc.) can be added later using the same framework.

---

## Content Types

### Tier 1: High-Volume, Repeating (biggest automation payoff)

These follow defined formats (see `protocols/BLOG_POST_FORMATS.md`) and repeat for every anthology.

| Content Type | Frequency | Schedule | Source Files | WP Category |
|---|---|---|---|---|
| Story Spotlights | ~15 per anthology | Thursdays | `anthologies/[name]/posts/Spotlight_*.md` | Story Spotlights |
| Interview Posts | ~8-15 per anthology | Mondays | `anthologies/[name]/posts/Interview_*.md` | Interviews |

**What automation does:**
- Takes finished `.md` file → creates WordPress draft post (or scheduled post)
- Sets category and tags
- Uploads featured image to organized media folder, attaches to post
- Adds `[ADD CTA PATTERN]` reminder (Jamie adds the Kadence block manually)
- Jamie reviews draft in WP → publishes (or confirms schedule)

### Tier 2: Occasional, One-Off

| Content Type | When | Source Files |
|---|---|---|
| Launch Post | Anthology release day | `anthologies/[name]/HauntedWaters_LaunchPost.md` etc. |
| Landing Pages | One per anthology | To be created |
| Introduction Posts | One per anthology | `anthologies/[name]/*_Introduction*.md` |

### Tier 3: Maintenance

| Task | When | Example |
|---|---|---|
| Batch cross-promotion updates | After new spotlights go live | Add "Also Featured in..." links to older posts |
| CTA updates | As needed | Update purchase links across multiple posts |
| Category/tag cleanup | As needed | Standardize taxonomy across posts |

---

## Anthology Pipeline

| Anthology | Spotlights | Interviews | Status |
|---|---|---|---|
| Haunted Waters | 15 written | 8 written | Posts exist, being published manually |
| Haunted Places | Not started | Not started | Early stage |
| Into the Briny Deep | Not started | Not started | Future |

Each new anthology follows the same pattern — the framework should handle any anthology, not just one.

---

## WordPress Details (Blackbird)

| Setting | Value |
|---|---|
| Site URL | blackbirdpublishing.com |
| Theme | Kadence |
| CTA method | Kadence pattern block (added manually by Jamie) |
| Featured image size | 1200x628px |
| Categories | Story Spotlights, Interviews |
| Permalink structure | *(confirm — likely post-name)* |

---

## Workflow Vision

```
1. Claude creates spotlight/interview as .md file (existing workflow)
2. Jamie reviews .md file, approves
3. Claude uploads featured image to appropriate media folder
4. Claude creates WordPress draft post from .md file
   - Sets category + tags
   - Attaches featured image
5. Jamie reviews draft in WP, adds CTA pattern
6. Jamie publishes — or Claude schedules the post for a specific date
```

---

## Post Status & Scheduling

- **During testing:** Create as drafts
- **Once stable:** Support scheduling posts for specific dates
  - Spotlights: Thursdays
  - Interviews: Mondays
- Could eventually batch-schedule a whole anthology's worth of posts

---

## Media Management

- **Plugin:** WP Media folder (by JoomUnited)
- Uses a custom taxonomy `wpmf-category` to assign media to folders
- Featured images should be uploaded to the appropriate folder (e.g., "Haunted Waters promo images")
- Featured image size: 1200x628px
- **API approach:** Upload via `/wp-json/wp/v2/media`, then assign the `wpmf-category` term to place it in the right folder
- **To verify:** Check that `wpmf-category` taxonomy has `show_in_rest` enabled — test by hitting `/wp-json/wp/v2/taxonomies/wpmf-category` once credentials are set up
- Other relevant media plugins: Enable Media Replace, Media File Renamer (AI-Powered), Envira Gallery

---

## Taxonomy (Categories & Tags)

**Categories (broad groupings):**
- Story Spotlights
- Interviews
- *(others TBD — launch posts, etc.)*

**Tags (specific, per-post):**
- Author name
- Anthology name
- Story title
- Themes/genre tags (e.g., "ghost stories", "coastal horror")
- *(Need to review existing tags on Blackbird to see what's already in use)*

---

## SEO (Rank Math)

- **Plugin:** Rank Math SEO (installed on Blackbird)
- Rank Math does **not** expose its fields via REST API by default
- **Two options to enable:**
  1. Add a small code snippet to `functions.php` (or a custom plugin) that registers the meta fields with `show_in_rest => true`
  2. Install the Rank Math API Manager plugin (third-party, provides a dedicated endpoint)
- **Key meta fields we can set:**
  - `rank_math_title` — SEO title
  - `rank_math_description` — meta description
  - `rank_math_focus_keyword` — focus keyword
  - `rank_math_facebook_title` / `rank_math_facebook_description` / `rank_math_facebook_image` — OG fields
  - `rank_math_twitter_title` / `rank_math_twitter_description` / `rank_math_twitter_image`
  - `rank_math_canonical_url`
- **Approach:** Generate sensible defaults from post content (story premise → meta description, author + story title → SEO title, genre/themes → focus keyword)
- **Status:** Enhancement — get basic posting working first, then layer in SEO

---

## Future Enhancements

- **GEO (Generative Engine Optimization):** Inkwren already generates GEO content; integrate when ready
- **Schema.org JSON-LD:** Existing ticket to generate structured data; can be injected via custom fields or plugin
- **Batch scheduling:** Schedule a full anthology's spotlight/interview calendar in one go
- **Cross-site publishing:** Extend to Jamie's author site and other properties
