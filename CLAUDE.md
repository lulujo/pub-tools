# CLAUDE.md - pub-tools

## Project Overview

**pub-tools** is a collection of integrations connecting Claude Code to publishing tools (WordPress, Buffer, etc.). Built for Jamie Ferguson's publishing workflow (Blackbird Publishing, Borogrove Press) and designed to be shareable with friends.

## Working With Jamie

- Jamie is a she
- **Editor:** vim (not nano) for any command-line editing
- Jamie juggles multiple projects (Inkwren, publishing, writing, interviews, life) — keep things simple and actionable

## Style Preferences (All Content)

- **Curly quotes everywhere** — "like this" not "like this"
- **Em dashes:** no spaces mid-sentence (grief—and loss, not grief — and loss)
- **Preserve author voice** — don't edit word choices, Canadian spellings (harbour, colour), etc.

## Related Repos and Projects

- **Publishing operations:** `~/Dropbox/dev/publishing/` (Dropbox, not git) — manuscripts, interviews, promo files, session notes, blog post content
- **Inkwren:** `~/Dropbox/dev/inkwren/` — Jamie's publishing management platform (separate project)
- **Rookery:** `~/Dropbox/dev/calliopelabs/rookery/` — newsletter tool for authors (separate project, Calliope Labs LLC)

This repo contains **integration code and tooling only**. Content lives in the publishing Dropbox directory.

## Key Directories

- `integrations/wordpress/` — WordPress integration (MCP adapter, REST API fallback)
- `docs/` — Shareable documentation (setup guides, how-tos for friends)

## Current Status

- **WordPress integration:** Planning complete, ready for Phase 1 (connect to Blackbird)
- **Buffer integration:** Identified as next target, not yet started
- See `integrations/wordpress/IMPLEMENTATION_PLAN.md` for the phased rollout

## MCP Tool Naming Conventions

When Jamie's Claude sessions have multiple MCP servers connected, tools must be namespaced to avoid collisions:

| Server | Prefix | Examples |
|---|---|---|
| pub-tools (WordPress) | `wp_` | `wp_create_post`, `wp_upload_media`, `wp_list_posts` |
| pub-tools (Buffer) | `buffer_` | `buffer_schedule_post`, `buffer_list_channels` |
| Inkwren | `inkwren_` | `inkwren_search_publications`, `inkwren_get_catalog_summary` |

"Publication" means different things in each context:
- **Inkwren:** A book or anthology in Jamie's catalog (project management data)
- **pub-tools:** A WordPress post or page (content publishing action)

## Workspace-to-Site Mapping

When using Inkwren MCP data to drive WordPress actions, use the correct workspace:

| Inkwren Workspace | WordPress Site | Status |
|---|---|---|
| Blackbird Publishing | blackbirdpublishing.com | Active target |
| Borogrove Press | TBD | Future |
| Jamie (personal writing) | TBD | Future |

## WordPress Integration

- **Approach:** Official WordPress MCP Adapter (primary), direct REST API (fallback)
- **Target site:** Blackbird Publishing (blackbirdpublishing.com) on WPEngine
- **Content types:** Story spotlights, interviews, launch posts, landing pages
- **Blog post formats:** See `~/Dropbox/dev/publishing/protocols/BLOG_POST_FORMATS.md`
- **Plugins on Blackbird:** Rank Math SEO, WP Media folder, Enable Media Replace, Media File Renamer, Envira Gallery, CMS Tree Page View, Yoast Duplicate Post

## Inkwren MCP Integration (Future)

Once both MCP servers are running, the cross-server workflow is:
1. Query Inkwren for publication/story data (title, description, authors, cover image, genres, tags, themes, pull quotes, UBL)
2. Use that data to populate a WordPress post (categories, tags, SEO fields, featured image)
3. Schedule social promo via Buffer

Inkwren's `/full` endpoints return rich structured data — a single `inkwren_get_publication` call provides everything needed for a WordPress post.

**GEO/JSON-LD:** Inkwren has a GEO export feature. Combined with pub-tools' planned schema.org JSON-LD generation, this could automate structured data injection into WordPress posts. Track as a future enhancement.
