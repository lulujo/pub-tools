# WordPress Implementation Plan — Review Discussion

## Plan / Content

**Author:** PUB Integrations Claude
**Location:** `integrations/wordpress/IMPLEMENTATION_PLAN.md`

The plan is a 6-phase rollout for connecting Claude Code to Blackbird Publishing's WordPress site:

1. **Connect & Discover** — install MCP adapter, generate credentials, inventory tools/taxonomy/media folders
2. **Draft Posts** — create spotlights/interviews as WP drafts, solve content conversion
3. **Featured Images** — upload to correct media folders, attach to posts
4. **Scheduling** — create future-dated posts
5. **SEO (Rank Math)** — auto-set meta title, description, keywords, OG fields
6. **Production Workflow** — batch test, document end-to-end process

**Supporting docs:**
- `integrations/wordpress/SETUP.md` — approach comparison, WPEngine notes, plugin inventory
- `integrations/wordpress/CONTENT_PLAN.md` — content types, taxonomy, media/SEO details
- `CLAUDE.md` — project context, naming conventions, workspace mapping

---

## Discussion

**PUB Integrations Claude · 2026-02-18**

I self-reviewed the plan and updated it based on my findings. Here's what changed and what I'd like another session to weigh in on.

### Changes made to the plan

**Blocker resolved:**
- Added tool name inventory step to Phase 1 — need to verify whether the WordPress MCP Adapter supports `wp_` prefixes or uses fixed tool names. This was committed to in the Inkwren MCP server comms thread but never verified against the actual adapter.

**Issues addressed in the updated plan:**
- Phase 1 expanded to "Connect & Discover" — now includes inventorying categories, tags, media folders, permalink structure, and a REST API sanity check
- Phase 2 now has an explicit **content conversion strategy** section with three options (Classic block, Gutenberg blocks, raw HTML) and a decision point before creating the first post
- Phase 2 now includes an explicit **curly quotes test** — this is a known problem (documented in BLOG_POST_FORMATS.md) and needs to be verified before we create real posts
- Phase 3 now notes the **Media File Renamer plugin** as a potential interference point
- Phase 3 now asks where featured images actually live (was unspecified)
- Phase 4 now includes **timezone verification**
- Phase 5 now **recommends Option A** (PHP snippet) instead of leaving it as an open question
- **Cleanup steps** added to Phases 2, 3, and 6 — Blackbird is a production site
- Key Reference Files now uses full paths and notes which files are in the Dropbox publishing directory (not this repo)
- Added `wp_` prefix convention to the plan header
- Future phases now include Inkwren cross-server workflow

### Areas I'd like another session to review

1. **Content conversion strategy (Phase 2).** I listed three options but don't have strong conviction on which is best. Someone with WordPress block editor experience would be more helpful here. The key question: what gives Jamie the best editing experience in WordPress while being feasible to generate programmatically?

2. **Is Phase 1 now too heavy?** I expanded it significantly (tool inventory, taxonomy inventory, media folder check, REST API sanity check, permalink confirmation). Is this the right amount of discovery, or should some of this move to later phases where it's actually needed?

3. **The MCP Adapter is brand new (Feb 2026).** The entire plan bets on it working well. If it's buggy or limited, do we have a good enough fallback plan? Phase 1 step 7 (REST API sanity check) is meant to de-risk this, but should we consider a more explicit "if MCP doesn't work, here's the REST API path" contingency?

4. **Missing anything?** I wrote this plan and then reviewed it myself. Self-reviews have blind spots. Fresh eyes on the full plan (`integrations/wordpress/IMPLEMENTATION_PLAN.md`) plus the supporting docs would be valuable.
