# Social Media Automation Research

**From:** Rookwood
**Date:** 2026-02-22 (evening)
**Updated:** 2026-02-23 -- REST API testing confirmed key findings
**Status:** Recommendation ready. Jamie is thinking it over.

---

## The Problem

When a Blackbird post goes live, Jamie has to manually post to social media. With 15+ Haunted Waters posts rolling out and plans to increase to ~5 posts/week, that's a lot of manual social posting across 5 platforms.

**Goal:** Full automation with custom, personal-voice messages. Written ahead of time, auto-posted on publish day. Zero intervention on publish day.

---

## Confirmed Recommendation: Autoblue + Jetpack Social Basic ($48/year)

### What was tested (2026-02-23)

**Jetpack Social custom message via REST API: CONFIRMED WORKING.**
- Meta field: `jetpack_publicize_message`
- Registered with `show_in_rest` &mdash; fully readable and writable via WordPress REST API
- Test: Created draft post 5541, set custom message via REST API, read it back successfully, deleted test post
- Also confirmed: `jetpack_publicize_feature_enabled` (boolean) can be toggled per post

**Autoblue custom message via REST API: CONFIRMED from source code review.**
- Meta field: `autoblue_custom_message`
- Registered with `show_in_rest: true` in `includes/Meta.php`
- Also has `autoblue_enabled` (boolean, `show_in_rest: true`)
- Triggers on `wp_after_insert_post` when status transitions to &ldquo;publish&rdquo;

### The Stack

| Platform | Tool | Custom message field | Cost |
|----------|------|---------------------|------|
| **Bluesky** | Autoblue (WP plugin) | `autoblue_custom_message` | $0 |
| **Facebook** | Jetpack Social Basic | `jetpack_publicize_message` | $48/yr total |
| **LinkedIn** | Jetpack Social Basic | (same field) | (included) |
| **Instagram** | Jetpack Social Basic | (same field) | (included) |
| **Pinterest** | Jetpack Social Basic | (same field) | (included) |

### Workflow

1. Rookwood creates/schedules a WP post (existing workflow)
2. Jamie writes custom social messages at her own pace, days or weeks before publish
3. Rookwood stores them in post meta via REST API:
   - `autoblue_custom_message` for Bluesky
   - `jetpack_publicize_message` for FB/LI/IG/Pinterest
4. Post goes live at 9 AM MT
5. **Autoblue** fires instantly &mdash; posts to Bluesky with featured image + custom message
6. **Jetpack Social** fires instantly &mdash; posts to FB/LI/IG/Pinterest with custom message
7. Zero intervention on publish day

### What Jamie needs to set up (one-time)

1. Install Autoblue plugin (WP Admin &gt; Plugins &gt; Add New &gt; search &ldquo;Autoblue&rdquo;)
2. Connect Bluesky account in Autoblue settings (handle + app password)
3. Upgrade Jetpack Social to Basic ($4.95/mo billed monthly, or ~$48/yr)
4. Connect social accounts in Jetpack Social settings (Facebook Page, LinkedIn, Instagram Business, Pinterest)

### What Rookwood builds

- Update `/post-spotlight` and `/post-interview` skills to set social meta fields when creating posts
- Optional: `/promote` skill for generating social copy for existing posts
- Social message generation as part of the post-creation workflow

### Still to verify (needs Jamie&rsquo;s involvement)

- Whether Jetpack Social actually fires auto-share for REST API-created posts when they transition to &ldquo;publish&rdquo; via WP cron (likely yes, but untested)
- Whether Jetpack Social Basic covers all 4 platforms (FB, LI, IG, Pinterest) or has limitations
- Instagram requires a Business/Creator account (Meta API restriction)

---

## Alternative: Zapier Free ($0)

If Jamie decides against the $48/yr Jetpack Social cost, Zapier free is a viable $0 option for FB/LI/IG/Pinterest with template-based messages (not custom per-post). Tami Veldura uses Zapier and could help with setup.

- 5 zaps (one per platform), RSS-triggered
- 100 tasks/month (enough for ~5 posts/week x 5 platforms = ~100/month at the upper limit)
- Template-based messages using RSS fields (title, excerpt, URL)
- 15-minute delay on all platforms
- No per-post custom messages on free tier (two-step zaps only, no formatters)

Zapier also has a Buffer integration (&ldquo;Add to Queue&rdquo; action), so RSS &rarr; Zapier &rarr; Buffer &rarr; platforms is possible. But Buffer free tier&rsquo;s 10-post-per-channel queue limit becomes a constraint at higher posting volumes.

**Trade-off:** $0 but template messages only vs. $48/yr with full custom messages.

---

## Key Finding: Buffer API Is Private

Buffer&rsquo;s API is **not publicly available** &mdash; it&rsquo;s internal to Buffer&rsquo;s teams. This kills the originally planned pub-tools Buffer integration. Buffer still works as a manual dashboard or as a Zapier action target.

Sources: [Buffer Pricing](https://buffer.com/pricing) | [Buffer API Info](https://getlate.dev/blog/buffer-api)

---

## Options Not Recommended

| Option | Why Not |
|--------|---------|
| **Buffer alone** | API is private. Manual only. |
| **Blog2Social** | Bluesky auto-posting only works from WP editor click, not REST API-created posts. $84/yr. |
| **Direct Facebook/LinkedIn API** | Meta app review (days/weeks), LinkedIn Marketing Platform approval, token refresh every 60 days. Too much ongoing maintenance. |
| **Jetpack Social free** | No custom message text &mdash; just title + link. Robotic. |
| **IFTTT Pro ($36/yr)** | Template-based only. No per-post custom messages. Jamie wants personal voice. |
| **Zapier paid ($29.99/mo)** | Wildly overpriced for this use case. |

---

## Sources

- [Autoblue on WordPress.org](https://wordpress.org/plugins/autoblue/) | [GitHub](https://github.com/posty-studio/autoblue)
- [Jetpack Social](https://jetpack.com/social/)
- [Buffer Pricing](https://buffer.com/pricing) | [Buffer Bluesky](https://buffer.com/bluesky)
- [IFTTT Pricing](https://ifttt.com/plans) | [IFTTT Bluesky](https://ifttt.com/explore/how-to-automate-bluesky)
- [Zapier Pricing](https://zapier.com/pricing) | [Zapier Free Plan](https://help.zapier.com/hc/en-us/articles/32337438839565)
- [Zapier Bluesky + RSS](https://zapier.com/apps/bluesky/integrations/rss)
- [Zapier Buffer Integration](https://zapier.com/apps/buffer/integrations)
