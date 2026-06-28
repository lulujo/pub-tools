#!/usr/bin/env python3
"""Backfill Rank Math SEO (focus keyword + meta description) onto spotlight/interview posts.

Dry run by default (prints proposed copy); pass --apply to write and verify round-trips.
Skips posts that already have Rank Math data. See integrations/wordpress/RANK_MATH_SEO.md.

Usage:
  python3 seo_backfill.py --tag 378 --anthology "Haunted Waters: 15 Tales from the Depths"
  python3 seo_backfill.py --tag 378 --anthology "Haunted Waters: 15 Tales from the Depths" --apply
"""
import argparse, base64, html, json, os, re, sys, time, urllib.request, urllib.error

BASE = "https://blackbirdpublishing.com/wp-json/wp/v2"
USER = "claude"
UA = "pub-tools/seo-backfill (Rookwood)"
ENV = os.path.join(os.path.dirname(__file__), "..", "..", ".env")

# "by" format: anthology spotlights/interviews — Interview/Story Spotlight: "Title" by Author
TITLE_RE = re.compile(r'^(Interview|Story Spotlight):\s*[“"”]?(.+?)[”"“]?\s+by\s+(.+?)\s*$', re.I)
# "on" format: StoryBundle author interviews — Interview: Author on Work Title
BUNDLE_RE = re.compile(r'^Interview:\s*(.+?)\s+on\s+(.+?)\s*$', re.I)


def load_auth():
    pw = None
    with open(os.path.abspath(ENV)) as f:
        for line in f:
            if line.startswith("CLAUDE_BLACKBIRD_WP_PASSWORD"):
                pw = line.split("=", 1)[1].strip().strip('"').strip("'").replace(" ", "")
    if not pw:
        sys.exit("No CLAUDE_BLACKBIRD_WP_PASSWORD in .env")
    return base64.b64encode(f"{USER}:{pw}".encode()).decode()


def req(auth, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method)
    r.add_header("Authorization", "Basic " + auth)
    r.add_header("User-Agent", UA)
    if data:
        r.add_header("Content-Type", "application/json")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503, 504, 520, 522, 525) and attempt < 3:
                time.sleep(2 * (attempt + 1)); continue
            return e.code, e.read().decode()[:300]
    return None, "exhausted"


def fetch_posts(auth, tag):
    posts = {}
    for status in ("publish", "future", "draft", "pending", "private"):
        page = 1
        while True:
            st, batch = req(auth, "GET", f"/posts?tags={tag}&status={status}&per_page=50&page={page}&context=edit")
            if st != 200 or not isinstance(batch, list) or not batch:
                break
            for p in batch:
                posts[p["id"]] = p
            if len(batch) < 50:
                break
            page += 1
    return posts


def _pick(*candidates):
    """Return the first candidate <= 155 chars, else the last truncated."""
    for c in candidates:
        if len(c) <= 155:
            return c
    return candidates[-1][:154] + "…"


def propose(title, anthology, bundle=False):
    title = html.unescape(title)
    if bundle:
        # StoryBundle author interview: "Interview: Author on Work" (check "on" before "by",
        # since a work title can itself contain " by ", e.g. "Brick by Brick").
        m = BUNDLE_RE.match(title)
        if not m:
            return None
        author, work = m.group(1).strip(), m.group(2).strip()
        desc = _pick(
            f"{author} on {work}, in the {anthology} StoryBundle—an author interview from Blackbird Publishing.",
            f"{author} on {work}, in the {anthology} StoryBundle.",
            f"{author} on {work}.",
        )
        return {"kind": "Bundle Interview", "rank_math_focus_keyword": work, "rank_math_description": desc}
    m = TITLE_RE.match(title)
    if not m:
        return None
    kind, story, author = m.group(1), m.group(2).strip().strip('“”"'), m.group(3).strip()
    # Guard against a nested prefix from a title bug, e.g. the interview titles
    # "Interview: Story Spotlight: "X" by Author" (posts 5199/5206) — keep just the story.
    story = re.sub(r'^(Story Spotlight|Interview):\s*', '', story, flags=re.I).strip().strip('“”"')
    if kind.lower() == "story spotlight":
        desc = _pick(
            f"{author}’s {story}—a story spotlight from {anthology}, from Blackbird Publishing.",
            f"{author}’s {story}—a story spotlight from {anthology}.",
        )
    else:
        desc = _pick(
            f"{author} on writing {story} for {anthology}—an author interview from Blackbird Publishing.",
            f"{author} on writing {story} for the anthology {anthology}.",
        )
    return {"kind": kind, "rank_math_focus_keyword": story, "rank_math_description": desc}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", type=int, required=True, help="Anthology tag ID (e.g. 378 = Haunted Waters)")
    ap.add_argument("--anthology", required=True, help='Anthology/bundle name, e.g. "Haunted Waters: 15 Tales from the Depths" or "Escape from 2026"')
    ap.add_argument("--bundle", action="store_true", help='StoryBundle interviews ("Author on Title" format) — use the bundle description template')
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry run)")
    args = ap.parse_args()

    auth = load_auth()
    posts = fetch_posts(auth, args.tag)
    work = []
    for pid, p in sorted(posts.items()):
        meta = p.get("meta", {})
        if any(meta.get(k) for k in ("rank_math_title", "rank_math_description", "rank_math_focus_keyword")):
            continue  # already has SEO
        title = p["title"]["rendered"] if isinstance(p["title"], dict) else p["title"]
        prop = propose(title, args.anthology, bundle=args.bundle)
        if not prop:
            print(f"  [{pid}] SKIP (title did not parse): {html.unescape(title)}")
            continue
        work.append((pid, p["status"], html.unescape(title), prop))

    print(f"\n{'APPLY' if args.apply else 'DRY RUN'}: {len(work)} post(s) tagged {args.tag} need SEO\n")
    ok = fail = 0
    for pid, status, title, prop in work:
        print(f"[{pid}] {status:>7} | {prop['kind']}")
        print(f"    focus: {prop['rank_math_focus_keyword']}")
        print(f"    desc ({len(prop['rank_math_description'])}): {prop['rank_math_description']}")
        if not args.apply:
            continue
        meta = {"rank_math_focus_keyword": prop["rank_math_focus_keyword"],
                "rank_math_description": prop["rank_math_description"]}
        st, _ = req(auth, "POST", f"/posts/{pid}", {"meta": meta})
        st2, got = req(auth, "GET", f"/posts/{pid}?context=edit")
        gm = got.get("meta", {}) if isinstance(got, dict) else {}
        if st in (200, 201) and gm.get("rank_math_description") == meta["rank_math_description"] \
                and gm.get("rank_math_focus_keyword") == meta["rank_math_focus_keyword"]:
            ok += 1; print("    -> OK")
        else:
            fail += 1; print(f"    -> FAIL (write {st})")
        time.sleep(0.3)

    if args.apply:
        print(f"\n=== {ok} OK, {fail} failed of {len(work)} ===")
    else:
        print("\n(dry run — re-run with --apply to write)")


if __name__ == "__main__":
    main()
