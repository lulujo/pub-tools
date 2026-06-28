# Direct Sales — Planning & Requirements

**Status:** Platform chosen — **WooCommerce** · **Owner:** Jamie · **Drafted by:** Rookwood · **Started:** 2026-06-28 · **Decided:** 2026-06-28

**Linear:** [Direct Sales project](https://linear.app/inkwren/project/direct-sales-ff694c5e0823) (PUB team) — PUB-12 → PUB-26 across Phase 1/2/3 milestones.

Goal: sell Blackbird Publishing titles **direct to readers** — ebooks, print, and bundles — from infrastructure Blackbird controls. This doc defines requirements first, then maps platforms against them. **No platform decision has been made yet.**

---

## 1. Design horizon

Plan for the **target state ~1 year out**, not today's small sellable list:

- A **growing catalog**, including **10–20 print titles** plus a larger ebook catalog.
- New titles added on an ongoing basis — so catalog management and (ideally) automation matter.
- This is **multi-year infrastructure**, chosen once and lived with. Bias toward durability over fastest-launch.

---

## 2. Sellable catalog

The gating filter is **rights**, not technology: a title can only go in the store if Blackbird holds direct-sales rights.

### Excluded — rights (parked)
- **13 anthologies + 4 bundles.** Multi-author works distributed through **PubShare.com**; selling them direct would require re-contracting every contributor. Revisit only if Jamie decides to pursue new contracts.

### Included — Blackbird controls the rights
Single-author works. **Current backlist = 17 titles:**

| Type | Count | Titles |
|---|---|---|
| Short stories | 13 | The Gate · And Never Return to the Sea · To Speak to the Gods · Be Nice to Statues · The Porta Alchemica · Dance Hall Days · The Center of the Maze · A Better Place · A Different Turn · When the Wind Blows · The Tommys · Diamond Betty · Inside a Fairy Tale |
| Novels | 2 | Entangled by Midsummer · With Perfect Clarity |
| Novelette | 1 | Bewitchery |
| Non-fiction | 1 | Bundle Up! 2nd Edition |

Trajectory: catalog grows over the next year toward **10–20 print titles** plus an expanding ebook list.

### Bundles as a *product*, not a problem
The existing multi-author bundles are out on rights — but every single-author title is Blackbird's to recombine. **New bundles of Jamie's own work** (collected shorts, themed sets) are a free-and-clear product line. Ties into the StoryBundle/PUB-11 tooling.

---

## 3. Requirements

### Must-have (functional)
- **Sell ebooks** (EPUB + PDF) — the bulk of the catalog, especially short stories.
- **Sell print** as a *first-class* format for 10–20 titles — via **print-on-demand dropship** (no inventory, printer ships white-labelled direct to reader). *[OPEN: confirm POD-only, vs also wanting to hold stock / ship signed copies yourself.]*
- **Sell bundles** (Jamie's own titles combined).
- **Ebook delivery** that handles **send-to-Kindle/Kobo** and **per-buyer watermarking** (social DRM), and ideally absorbs reader tech-support. → BookFunnel is the standout here regardless of platform.
- **North America first:** US + Canada at launch (no customs for NA buyers — both leading POD services print in US *and* Canada).

### Strongly wanted (strategic)
- **Own the customer email list** — feeds Jamie's newsletter; every direct buyer becomes a reachable reader.
- **Automatable by Rookwood** — create products from Inkwren catalog data, add buy-links to spotlight/interview posts, push new releases. *Native on WordPress (existing pub-tools wiring); new tooling on Shopify.*
- **Unified brand/domain** — store living on/with blackbirdpublishing.com vs a separate storefront.

### Constraints
- **Tax home: US.** Sales tax via state economic nexus (won't trigger at low volume). Launch **US/Canada only** to defer EU/UK VAT (no threshold — VAT owed from the first sale into the EU/UK).
- **No channel exclusivity** — Jamie does **not** use KDP Select, so ebooks are free to sell direct. ✅
- **All files production-ready** — no content gate; launch bounded by store build. ✅

### Decisions made (2026-06-28)
- **Platform: WooCommerce.** Chosen primarily to avoid a fixed monthly platform fee while direct-sales revenue is small (Shopify Basic ≈ $39/mo). Woo's real cost is maintenance *time*, not dollars — substantially offset because Rookwood can manage/automate the store natively (same WordPress). Revisit Shopify only if volume grows enough that managed-hosting convenience outweighs the monthly fee.
- **Merchant-of-record: self.** Blackbird is MoR. Mitigated by launching **US/Canada only** (defers EU/UK VAT) and US economic-nexus not triggering at low volume. Add Quaderno + broader geography in Phase 3.
- **Product model:** one **variable product per title** with a **Format** attribute = **Ebook / Paperback** (variations, not separate products). Ebook variation = virtual + downloadable (BookFunnel delivery); Paperback variation = physical (Phase 2 POD). Phase 1 builds the ebook variation; paperback added per-title in Phase 2.
- **Budget: minimize fixed monthly cost.** WooCommerce core, the watermark plugin, and payments (per-transaction only) add no monthly fee. **BookFunnel:** Jamie may already have a subscription (to verify). *If* it exists **and** the tier is Mid-List+ **and** covers the WooCommerce sales integration → use it in Phase 1 (no marginal cost, better delivery). Otherwise defer (~$20/mo) until volume justifies.
- **✅ Hosting cost — RESOLVED, Phase 1 ≈ $0 incremental (PUB-12, 2026-06-28).** Current plan is **WP Engine Growth ($1,150/yr ≈ $96/mo)** with large headroom (8,088/100,000 visits, 5/10 sites, 7.4/20 GB). WP Engine runs WooCommerce on the **standard managed WordPress platform** with automatic cache-exclusions for `/cart/`, `/checkout/`, `/my-account/`; the Managed WooCommerce tier / eCommerce Performance Pack is an **optional** add-on, not required. So **no plan upgrade is needed** — the store runs on the existing Growth plan at ~$0 incremental cost. The original "avoid a monthly fee" logic fully holds: Shopify would be ~$39/mo *on top of* the WP Engine hosting kept anyway for the content site. Residual (in store-config **PUB-16**): confirm cache-exclusions are active at setup. Avoid: any fully-hosted rent-a-store SaaS (Shopify / Woo Express) — the model we passed on.

---

## 4. Platform landscape (mapped to requirements)

Researched 2026. Print being first-class is the key discriminator — it eliminates digital-only options.

| Platform | Ebooks | Print POD | Owns customer list | Merchant of record (tax handled) | Maintenance | Rookwood-automatable | Verdict |
|---|---|---|---|---|---|---|---|
| **WooCommerce** (on existing WP site) | ✅ (BookFunnel plugin) | ✅ Lulu Direct / Bookvault | ✅ | ❌ you're MoR (add Quaderno; geo-limit US/CA) | **Yours** (updates, security, PCI SAQ-A) | ✅ native — same WP I already drive | **Finalist** |
| **Shopify** | ✅ (BookFunnel / app) | ✅ Lulu / Bookvault apps (mature) | ✅ | ❌ you're MoR (Shopify Tax calculates US well) | **Managed** (near-zero) | ⚠️ new tooling (Admin API) | **Finalist** |
| **Gumroad** | ✅ | ⚠️ weak | ✅ | ✅ full global | Managed | ⚠️ | Print too weak for 10–20 titles |
| **Payhip** | ✅ | ✅ | ✅ | ⚠️ EU/UK digital VAT only | Managed | ⚠️ | Partial MoR; print secondary |
| **Lemon Squeezy / Paddle** | ✅ | ❌ digital-only | partial | ✅ full global | Managed | ❌ | **Disqualified — no print** |

**Delivery layer (platform-independent):** **BookFunnel** — unique download links, EPUB/MOBI/PDF, send-to-Kindle/Kobo, per-buyer watermarking, reader support. Integrates with WooCommerce, Shopify, and Payhip. Plan on using it whichever store wins.

**POD layer:** **Lulu Direct** (best North-American coverage — prints US *and* Canada, no customs either way) or **Bookvault** (cheaper per unit, better hardcover/special editions). Both have real WooCommerce *and* Shopify integrations with automated order routing (no manual re-keying).

---

## 5. Decision: WooCommerce

Chosen 2026-06-28. The finalists were WooCommerce and Shopify (both own the customer list and do ebooks + POD print well). WooCommerce wins because:

- **No fixed monthly platform fee** — Shopify Basic ≈ $39/mo would bleed money while direct-sales revenue is small (small single-author catalog, mostly low-price short stories). Woo carries no subscription.
- **Woo's real cost is maintenance time, not dollars** — and that's largely offset because Rookwood manages/automates the store natively in the same WordPress. A solo Woo operator eats the upkeep alone; Blackbird has an automation layer.
- **Unified on blackbirdpublishing.com** — one domain/brand, shared with the content site Rookwood already drives via pub-tools/Inkwren.

**Reconsider Shopify** only if volume grows enough that managed-hosting convenience (zero maintenance/PCI) outweighs the monthly fee.

---

## 6. Phasing (WooCommerce)

1. **Phase 1 — Ebooks + bundles, near-$0/mo fixed cost.** Install + configure WooCommerce on blackbirdpublishing.com (WPEngine). Delivery via Woo's built-in secure downloads + a free PDF-watermark plugin (WaterWoo) — **BookFunnel deferred**. Stripe + PayPal (per-transaction only). List the current single-author titles; geo-limit checkout to US/CA. Validates the whole pipeline at no monthly cost.
2. **Phase 2 — Print POD.** Add Lulu Direct / Bookvault; enable print for the novels + any title long enough, scaling toward 10–20 print titles.
3. **Phase 3 — Scale & expand.** Add **BookFunnel** when send-to-Kindle + reader-support volume justify ~$20/mo. Tax automation (Quaderno) + broader geography when volume justifies. Deeper Rookwood automation (Inkwren → product creation, WP buy-links). Own-work bundles.

---

## 7. Long-term direction — Shopify + Klaviyo

Tami's preference is to move to **Shopify + Klaviyo** eventually. Assessment: a legitimate, best-in-class commerce + marketing stack — the right *destination* once direct sales are a real, marketing-driven revenue channel. Premature *now* (Shopify ~$39/mo + Klaviyo scaling with list size ≈ $60–100+/mo before matching revenue), which is why we start on Woo. Starting on WooCommerce does **not** block this future:

- **Portability:** the two things painful to lose — the **customer email list** and **POD/BookFunnel know-how** — are fully portable. A Woo→Shopify migration at small catalog scale is straightforward (export customers, re-create ~20 products, set redirects).
- **Decouple email from commerce:** **Klaviyo has a first-class WooCommerce integration** — it is not Shopify-only. So adopt **Klaviyo as the durable marketing layer on Woo now/early**, and migrate only the **commerce engine** to Shopify later. Klaviyo persists across the move.
- **Caution — email-tool sprawl:** decide how Klaviyo relates to Jamie's existing newsletter platform and **Rookery** before adopting it; avoid running 2–3 overlapping email systems. Klaviyo is ecommerce-marketing-flavoured (abandoned-cart, post-purchase flows).

**Recommended sequence:** Woo now → layer **Klaviyo on Woo** when marketing automation is wanted → move the store to **Shopify** when revenue justifies the monthly cost, keeping Klaviyo throughout.

*To verify before committing specifics: current Klaviyo pricing tiers + WooCommerce integration depth; Woo→Shopify migration mechanics.*

## 8. Next steps

- [x] ~~Pick platform~~ → **WooCommerce** (2026-06-28).
- [ ] Confirm print model: POD-dropship only, or also hold stock / signed copies? (§3 OPEN) — affects Phase 2, not Phase 1.
- [ ] Verify WooCommerce can be installed on the WPEngine site (plugin install permissions, any WPEngine eCommerce hosting considerations).
- [ ] Write the **Phase 1 build spec**: WooCommerce install/config, product schema (title → ebook product mapping), Stripe/PayPal setup, WaterWoo, US/CA geo-limit, test purchase.
- [ ] Create Linear ticket (PUB project) for the WooCommerce Phase 1 build.
