# Blackbird Publishing — Site Inventory

**URL:** https://blackbirdpublishing.com
**Hosting:** WPEngine (managed WordPress)
**Discovered:** 2026-02-18

---

## Permalink Structure

Pretty permalinks: `/%postname%/`
Example: `https://blackbirdpublishing.com/interview-the-ocean-is-my-wife-by-deanna-knippling/`

---

## Categories

| ID | Name | Slug | Parent |
|----|------|------|--------|
| 299 | *** Ready *** | ready | — |
| 248 | Behind the stories | behind-the-stories | — |
| 178 | Chatterings | chatterings | For Authors & Publishers (190) |
| 315 | Enchanted Tales | enchanted-tales | — |
| 190 | For Authors & Publishers | for-authors-publishers | — |
| 4 | **Interviews** | interviews | — |
| 13 | Just the Facts | just-the-facts | For Authors & Publishers (190) |
| 16 | **New Releases** | new-releases | — |
| 113 | News & Updates | news-and-updates | — |
| 14 | **Story Spotlights** | story-spotlights | — |
| 116 | TEMPLATE | template | — |
| 307 | The Haunted Anthology | the-haunted-anthology | — |
| 1 | Uncategorized | uncategorized | — |

**Key categories for automation:** Interviews (4), Story Spotlights (14), New Releases (16)

---

## Tags

124 total tags. Patterns observed:

- **Author names** — e.g., "Jamie Ferguson" (240), "Ron Collins" (256), "Kristine Kathryn Rusch" (241)
- **Anthology/collection names** — e.g., "Haunted Waters" (378), "Enchanted Tales" (313), "The Haunted Anthology" (308)
- **Story titles** — e.g., "A Procession of Faeries" (229), "Stolen by the Fae" (360)
- **Bundle names** — e.g., "Bundle Up" (184), "The Realm of Faerie bundle" (232)

**Note:** Some duplicate/variant tags exist:
- "Innocence and Deceit" (195) and "Innocence and Deceit" (201, slug: innocenceanddeceit)
- "Inside a Fairy Tale" (219) and "Inside a FairyTale" (213, slug: insideafairytale)
- "The Fennigsan's Challenge" (217) and "The Fenningsan's Challenge" (215) — different spellings
- "The Charming Way" (216) and "TheCharmingWay" (202)

**Haunted Waters tag:** ID 378, slug: haunted-waters

---

## Taxonomies (REST API)

| Taxonomy | Name | REST base | REST accessible |
|----------|------|-----------|-----------------|
| category | Categories | categories | Yes |
| post_tag | Tags | tags | Yes |
| nav_menu | Navigation Menus | menus | Yes |
| wp_pattern_category | Pattern Categories | wp_pattern_category | Yes |
| wpmf-category | WP Media folders | — | **No (403 Forbidden)** |

**WP Media folder issue:** The `wpmf-category` taxonomy is not exposed via REST API — the `claude` Editor user gets a 403. This may require either:
- Admin-level permissions to access (not desirable)
- A plugin setting to enable REST access for editors
- Assigning media to folders manually after upload

---

## Post Meta Fields (REST accessible)

Kadence theme fields (`_kad_post_*`) are exposed. Jetpack social/newsletter fields are exposed.

**Rank Math fields are NOT exposed in post meta.** The Rank Math REST API namespace (`rankmath/v1`) exists, but individual post SEO fields (`rank_math_title`, `rank_math_description`, etc.) are not registered with `show_in_rest` — this confirms we'll need the PHP snippet in Phase 5.

---

## REST API Namespaces

- `wp/v2` — Core WordPress API
- `rankmath/v1` — Rank Math SEO (API exists but post meta not REST-registered)
- `media-file-renamer/v1` — Media File Renamer (has API)
- `wpe/cache-plugin/v1` — WPEngine cache
- `jetpack/v4` — Jetpack
- `akismet/v1` — Akismet spam protection
- `embedpress/v1` — EmbedPress

---

## MCP Tools (blackbird-wp)

**MCP server:** InstaWP/mcp-wp, registered as `blackbird-wp`
**Tool invocation:** `mcp__blackbird-wp__<tool_name>` (Claude Code's standard MCP namespacing)
**Prefix situation:** Tools use fixed names (e.g., `list_posts`, not `wp_list_posts`). The MCP server name `blackbird-wp` provides disambiguation — no `wp_` wrapper layer needed.

### Available Tools

| Group | Tools | Notes |
|-------|-------|-------|
| Posts | `list_posts`, `get_post`, `create_post`, `update_post`, `delete_post` | Full CRUD. Supports categories, tags, status, slug, featured_media. |
| Pages | `list_pages`, `get_page`, `create_page`, `update_page`, `delete_page` | Full CRUD. Supports templates, parent pages, menu_order. |
| Media | `list_media`, `create_media`, `edit_media`, `delete_media` | `create_media` takes a `source_url` (not local file path). `edit_media` updates metadata only. |
| Categories | `list_categories`, `get_category`, `create_category`, `update_category`, `delete_category` | Full CRUD. |
| Users | `list_users`, `get_user`, `create_user`, `update_user`, `delete_user` | Full CRUD. |
| Comments | `list_comments`, `get_comment`, `create_comment`, `update_comment`, `delete_comment` | Full CRUD. |
| Plugins | `list_plugins`, `get_plugin`, `activate_plugin`, `deactivate_plugin`, `create_plugin` | `create_plugin` installs from WordPress.org by slug. |
| Plugin Repo | `search_plugin_repository`, `get_plugin_details` | Search/browse WordPress.org directory. |

### Gaps (require direct REST API fallback)

- **Tags:** No `list_tags` / `create_tag` / `update_tag` tools. Tags can be set by ID array on `create_post`/`update_post`, but can't be browsed or created via MCP. Use REST API: `GET /wp-json/wp/v2/tags`
- **Custom fields / post meta:** No tools. Can't set Rank Math SEO fields via MCP. (Phase 5 uses REST API + PHP snippet.)
- **Media upload from local file:** `create_media` requires a publicly accessible `source_url`. Local file uploads require direct REST API `POST /wp-json/wp/v2/media` with multipart form data.
- **WP Media folders (wpmf-category):** No MCP support (also blocked at REST API level — see Issues below).
- **Menus / navigation:** No tools.

### Verified Working (2026-02-20)

- `list_categories` — returned all 13 categories, matching REST API inventory exactly
- `list_posts` — returned recent Haunted Waters posts with correct categories, tags, featured images
- Post content includes Gutenberg block markup (not Classic blocks)

---

## Issues to Address

1. **WP Media folder (wpmf-category)** — not REST-accessible for editors. Need to check plugin settings or accept that media folder assignment is manual for now.
2. **Rank Math post meta** — not exposed via REST. PHP snippet needed (Phase 5, as planned).
3. **Duplicate tags** — some cleanup may be warranted, but not blocking.
