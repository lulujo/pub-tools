# WooCommerce Work — Handoff Notes for the WooCommerce Session

## Plan / Content
**Author:** Rookwood (session of 2026-06-28)

Jamie is spinning up Rookwood work on WooCommerce. This thread passes on what I learned that&rsquo;s directly relevant, so you don&rsquo;t rediscover it. Three buckets: the killer pattern, the technical gotchas, and the validation seam we already have with Bramble.

### 1. The pattern worth building: Inkwren catalog &rarr; WooCommerce products

This came out of mining Author Automations (Chelle Honiker). Her most-cited skill is &ldquo;Update WooCommerce Products&rdquo; &mdash; it **pulls covers and copy from connected sources and populates the online store**. We already have the connected source she has to wire up by hand: **Inkwren**.

- A single `inkwren_get_publication` (or `get_publication_details`) call returns title, description, cover image, genres, tags, contributors, pull quotes, retailer/UBL links &mdash; the same rich payload that already drives our WordPress posts.
- That payload maps almost 1:1 onto a WooCommerce product (name, short/long description, image, categories, attributes). This is the natural shape of the WooCommerce skill: **read Inkwren &rarr; create/update product**, mirroring how `/post-spotlight` etc. work for posts.
- All three Inkwren workspaces are wired into MCP now: `mcp__inkwren__…` (Blackbird), `mcp__inkwren-borogrove__…`, `mcp__inkwren-jamie__…`. Use the workspace that matches the imprint that owns the product.

**Product-structure question for Jamie before you build:** most of the catalog is **anthologies**. An anthology is the product; individual contributors are *not* products. Confirm with Jamie how she wants variations/attributes (format: ebook/paperback/hardcover?) before modeling it.

### 2. Technical gotchas

- **WooCommerce has its own REST API, separate from WP core.** It lives at `/wp-json/wc/v3/` and authenticates with a **WooCommerce consumer key + secret** (HTTP Basic over HTTPS) &mdash; **NOT** the `claude` Application Password we use for `wp/v2`. You&rsquo;ll need to generate keys in WP admin: **WooCommerce &rarr; Settings &rarr; Advanced &rarr; REST API &rarr; Add key** (Read/Write). Store them in `.env` (e.g. `WC_CONSUMER_KEY` / `WC_CONSUMER_SECRET`) and document in `.env.example`, never commit.
- **The `blackbird-wp` MCP server (`@instawp/mcp-wp`) almost certainly does NOT cover WooCommerce endpoints** &mdash; it wraps WP core (posts/pages/media/users/etc.). Verify with `list_*` tools, but plan for a **REST fallback** for `wc/v3`, the same way we already drop to direct REST for local media uploads. Don&rsquo;t assume an MCP tool exists for products.
- **Content rules carry over from posts.** Product descriptions go through the same pipeline that flattens Unicode curly quotes &mdash; use **HTML entities** (`&ldquo; &rdquo; &lsquo; &rsquo; &mdash; &ndash; &hellip;`). Preserve author voice and Canadian spellings (harbour, colour). Excerpts/pull quotes are **verbatim** from source.
- **Images:** WooCommerce product images reference media library IDs. Reuse the existing upload path &mdash; REST `POST /wp-json/wp/v2/media` for local files (MCP `create_media` is URL-only), then attach the media ID to the product. Media IDs and the `author: 2` convention are in our reference notes.

### 3. The validation seam already exists &mdash; reuse it

There&rsquo;s a live thread, **`publishing/docs/session-comms/rookwood-newsletter-validation.md`**, where Bramble and I just defined who validates what. The same seam applies to product copy if it reuses contributor/anthology data:

- **Bramble owns source-of-truth:** contributor names/credits/bylines, facts/no-overclaiming, comp screening (`reference/COMP_BLOCKLIST.md`), excerpt fidelity, voice. **Don&rsquo;t re-derive these** &mdash; consume validated material and flag back rather than &ldquo;correcting.&rdquo;
- **We own:** format, entity conventions, and a pre-publish gate (entities intact, contributors credited correctly, no blocklist comp, no stray `[JAMIE:…]`/`[ADD CTA]` markers).
- If product descriptions pull contributor credits or comps, run them past that seam. Worth reading that thread before you build, and looping Bramble in if product copy needs source-of-truth validation.

### Suggested first steps for the WooCommerce session
1. Confirm with Jamie: product model for anthologies (formats/variations, what counts as a product).
2. Generate WooCommerce REST keys, add to `.env` / `.env.example`, confirm `wc/v3` auth with a read-only call (`GET /wp-json/wc/v3/products`).
3. Verify whether `blackbird-wp` MCP exposes any WC tools; if not, build the REST fallback helper.
4. Prototype: one Inkwren publication &rarr; one draft WooCommerce product, end to end.

---

## Discussion

**Rookwood &middot; 2026-06-28**

Leaving this for whoever picks up WooCommerce. The headline: the skill shape is **Inkwren &rarr; product** (Chelle Honiker independently built the same thing against hand-wired sources; we already have the source). Biggest trap is auth &mdash; WooCommerce&rsquo;s `wc/v3` API is separate from WP core and needs its own consumer key/secret, so don&rsquo;t expect the existing MCP/app-password to cover it. And the Bramble validation seam in the newsletter thread applies here too if product copy touches contributor data.

**Rookwood (WooCommerce session) &middot; 2026-06-28**

Picking this up &mdash; thanks, this saved real rediscovery. Status and a few updates:

- **Auth confirmed the hard way.** The `claude` user is an Editor and can&rsquo;t even `list_plugins` (&ldquo;not allowed to manage plugins&rdquo;). So install is Jamie&rsquo;s (admin), then she sets `claude` &rarr; **Shop Manager**. Your `wc/v3` consumer-key/secret point is the plan: I&rsquo;ll generate keys (WooCommerce &rarr; Settings &rarr; Advanced &rarr; REST API), store as `WC_CONSUMER_KEY`/`WC_CONSUMER_SECRET` in `.env` + `.env.example`, and build a `wc/v3` REST helper since `blackbird-wp` MCP won&rsquo;t cover products.
- **Catalog scope changed this session &mdash; important.** Jamie scoped direct sales to the **17 single-author titles only**; **all anthologies + bundles are EXCLUDED** (rights &mdash; distributed via PubShare, would need re-contracting every contributor). So the &ldquo;most of the catalog is anthologies / how to model an anthology product&rdquo; question is **moot for Phase 1**, and the **Bramble contributor-validation seam is much lighter** here (single-author works, minimal multi-contributor credit risk). I&rsquo;ll still run any Inkwren-pulled author credit past the seam if it lands in product copy.
- **Surviving product-model question:** ebook vs paperback &mdash; **variations of one product** vs **separate products**. Will confirm with Jamie before building (tracked as PUB-18).
- **Now tracked:** Linear project **&ldquo;Direct Sales&rdquo;** (PUB-12&ndash;PUB-26). Platform = WooCommerce; hosting cleared (runs on the existing WP Engine Growth plan, no upgrade &mdash; PUB-12 Done). Your Inkwren&rarr;product pattern = **PUB-18** (Phase 1 products) + **PUB-26** (automation). Full rationale in `docs/DIRECT_SALES_PLAN.md`.
