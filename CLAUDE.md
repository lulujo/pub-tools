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

## WordPress Integration

- **Approach:** Official WordPress MCP Adapter (primary), direct REST API (fallback)
- **Target site:** Blackbird Publishing (blackbirdpublishing.com) on WPEngine
- **Content types:** Story spotlights, interviews, launch posts, landing pages
- **Blog post formats:** See `~/Dropbox/dev/publishing/protocols/BLOG_POST_FORMATS.md`
- **Plugins on Blackbird:** Rank Math SEO, WP Media folder, Enable Media Replace, Media File Renamer, Envira Gallery, CMS Tree Page View, Yoast Duplicate Post
