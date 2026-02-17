# WordPress Integration Setup

## Overview

Connect Claude Code to WordPress for creating/updating posts, pages, and media. Designed for publisher workflows (spotlights, interviews, blog posts).

## Hosting

Jamie's sites are on **WPEngine** (managed WordPress hosting). No compatibility issues — WPEngine fully supports the WordPress REST API and Application Passwords. The official WordPress MCP adapter also works on WPEngine.

**One thing to check:** Permalinks must be set to something other than "Plain" (WPEngine typically defaults to a pretty permalink structure, so this is likely already fine).

## Authentication Options

### Option 1: WordPress REST API + Application Passwords (Built-in)
- Available since WordPress 5.6, no plugins needed
- Generate in WP Admin: Users → Your Profile → Application Passwords
- Each password is unique, can be revoked independently
- Auth via Basic Auth header: `Authorization: Basic base64(username:app_password)`

### Option 2: WordPress MCP Adapter (Official)
- Official WordPress core team project, launched Feb 2026
- Repo: https://github.com/WordPress/mcp-adapter
- Install as a WordPress plugin, then configure Claude Code to connect
- Supports Application Passwords, JWT, OAuth 2.1
- AI-optimized: Claude auto-discovers available tools

### Option 3: InstaWP mcp-wp (Community)
- Repo: https://github.com/InstaWP/mcp-wp
- ~35 tools, well-documented, production-tested
- Node.js-based, multiple deployment options (npx, Docker, CLI)
- Does not require a WP plugin — connects via REST API externally

## Credential Storage

Store credentials locally, never in the repo:
- Use environment variables, or
- A local config file added to `.gitignore`

## Capabilities

All approaches support:
- Create/update/delete posts and pages
- Upload and manage media (images)
- Manage categories and tags
- Set featured images
- Handle custom fields/meta
- Work with custom post types

## Which Approach to Use?

| | REST API | MCP Adapter | InstaWP mcp-wp |
|---|---|---|---|
| Setup complexity | Low | Medium | Medium |
| Requires WP plugin | No | Yes | No |
| AI-optimized | No | Yes | Yes |
| Tool auto-discovery | No | Yes | Yes |
| Hosting requirements | Any | Any (self-hosted) | Any |
| Best for | Quick start, sharing with others | Long-term integrated workflow | Feature-rich, no plugin install |

## Chosen Approach

**Primary:** WordPress MCP Adapter (Option 2) — official, AI-optimized, auto-discovers tools
**Fallback:** Direct REST API calls for anything MCP doesn't cover (WP Media folder taxonomy, Rank Math meta)

See `IMPLEMENTATION_PLAN.md` for the phased rollout.

## Sites to Connect

| Site | URL | Purpose | Status |
|---|---|---|---|
| Blackbird Publishing | blackbirdpublishing.com | Publishing site (spotlights, interviews, launches) | First target |

## Relevant Plugins on Blackbird

| Plugin | Relevance |
|---|---|
| Rank Math SEO | SEO meta fields on posts (Phase 5) |
| WP Media folder | Organize uploaded images into folders (Phase 3) |
| Enable Media Replace | Replace existing media — useful for updates |
| Media File Renamer | AI-powered rename for SEO — may auto-rename uploads |
| Envira Gallery | Gallery management — not directly relevant yet |
| CMS Tree Page View | Page organization — not directly relevant |
| Yoast Duplicate Post | Duplicate posts — not directly relevant |
