#!/usr/bin/env python3
"""Convert a StoryBundle interview markdown file to Gutenberg blocks and
create a WordPress draft on Blackbird Publishing.

This is the reusable engine behind the `/post-bundle-interview` skill. It
exists as committed, tested code (rather than a script rebuilt in /tmp each
session) because the markdown->Gutenberg conversion has sharp edges that we
kept rediscovering. The edge cases are pinned by test_md_to_gutenberg.py --
run that after any change here.

Source files come from Bramble (the publishing repo) and use STRAIGHT quotes
plus a handful of Unicode punctuation chars. The conversion rules:

  - Straight quotes -> curly entities (&ldquo; &rdquo; &lsquo; &rsquo;).
    An opening quote can be preceded by whitespace, an open bracket, a
    markdown `*`, or a dash -- all must count as "opening" or the quote
    flips to a closing entity. (Bit us on `**"Comstock"` and `justice--"x"`.)
  - Em dash -> &mdash; with surrounding spaces stripped (house style).
  - En dash -> &ndash; (number ranges; spaces left alone).
  - Ellipsis -> &hellip; ; superscript two -> &sup2;.
  - Bare ampersand -> &amp; via negative-lookahead so existing entities
    aren't double-encoded. Run FIRST.
  - Accented letters (a-grave, etc.) are left as UTF-8 -- WordPress stores
    UTF-8 fine; only quotes/dashes/ellipsis/&/superscript need entities.
  - Markdown bold uses a NON-GREEDY match so a bold span can contain inner
    *italics* (e.g. `**a question with *Gray Lady* inside**`). Links are
    converted before italics so `[*Title*](url)` nests <em> inside <a>.

Expected markdown structure (the Bramble bundle-interview template):

    # Interview: <Author> on <Book Title>
    [Featured image: ...]  / Alt text: "..."
    [Book cover image: ...] / Alt text: "..."

    <intro paragraph(s)>
    ---
    ## The Interview
    **<question>**

    <answer paragraph(s)>
    ... (repeat) ...
    ---
    ## About the Author
    <bio paragraph(s)>
    ## Find <Author>
    - [label](url)
    ---
    [Bundle montage image: ...] / Alt text: "..."
    <bundle CTA paragraph>

Usage:
    # Dry run -- convert + self-check, print Gutenberg HTML, touch nothing:
    python3 md_to_gutenberg.py --config batch.json --dry-run

    # Create the drafts on WordPress:
    python3 md_to_gutenberg.py --config batch.json

See the `/post-bundle-interview` skill for the config format and full workflow.
"""

import argparse
import base64
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# --------------------------------------------------------------------------
# Inline markdown -> HTML (with entities)
# --------------------------------------------------------------------------

# A double/single quote counts as "opening" when preceded by start-of-string,
# whitespace, an open bracket, a markdown asterisk, or an em/en dash.
_OPEN_DQUOTE = re.compile(r'(^|[\s\(\[\{\*—–])"')
_OPEN_SQUOTE = re.compile(r"(^|[\s\(\[\{\*—–])'")
_BARE_AMP = re.compile(r'&(?!(?:[a-zA-Z]+|#\d+);)')
_EM_DASH = re.compile(r'\s*—\s*')          # strip surrounding spaces
_MD_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_MD_BOLD = re.compile(r'\*\*(.+?)\*\*')         # non-greedy: allows inner *italics*
_MD_ITALIC = re.compile(r'\*([^*]+)\*')


def inline(text):
    """Convert inline markdown + special chars in a single block of text."""
    t = _BARE_AMP.sub('&amp;', text)
    t = t.replace('…', '&hellip;').replace('²', '&sup2;')
    t = _OPEN_DQUOTE.sub(r'\1&ldquo;', t)
    t = t.replace('"', '&rdquo;')
    t = _OPEN_SQUOTE.sub(r'\1&lsquo;', t)
    t = t.replace("'", '&rsquo;')
    t = _EM_DASH.sub('&mdash;', t)
    t = t.replace('–', '&ndash;')
    t = _MD_LINK.sub(r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = _MD_BOLD.sub(r'<strong>\1</strong>', t)
    t = _MD_ITALIC.sub(r'<em>\1</em>', t)
    return t


# --------------------------------------------------------------------------
# Gutenberg block builders
# --------------------------------------------------------------------------

SEPARATOR = ('<!-- wp:separator -->\n'
             '<hr class="wp-block-separator has-alpha-channel-opacity"/>\n'
             '<!-- /wp:separator -->')


def paragraph(text):
    return f"<!-- wp:paragraph -->\n<p>{inline(text)}</p>\n<!-- /wp:paragraph -->"


def heading(text):
    return (f'<!-- wp:heading -->\n'
            f'<h2 class="wp-block-heading">{inline(text)}</h2>\n'
            f'<!-- /wp:heading -->')


def cover_block(media_id, url, alt, width_px=300):
    """Resized image (e.g. a book cover). All three of: width in the block
    JSON, the is-resized figure class, and the inline width style on the img
    must agree or Gutenberg's recovery silently drops the resize."""
    return (f'<!-- wp:image {{"id":{media_id},"width":"{width_px}px",'
            f'"sizeSlug":"full","linkDestination":"none","align":"center"}} -->\n'
            f'<figure class="wp-block-image aligncenter size-full is-resized">'
            f'<img src="{url}" alt="{alt}" class="wp-image-{media_id}" '
            f'style="width:{width_px}px"/></figure>\n'
            f'<!-- /wp:image -->')


def image_block(media_id, url, alt):
    """Full-width image (e.g. the bundle CTA banner)."""
    return (f'<!-- wp:image {{"id":{media_id},"sizeSlug":"full",'
            f'"linkDestination":"none"}} -->\n'
            f'<figure class="wp-block-image size-full">'
            f'<img src="{url}" alt="{alt}" class="wp-image-{media_id}"/></figure>\n'
            f'<!-- /wp:image -->')


def list_block(items):
    inner = "".join(f"<li>{inline(i)}</li>" for i in items)
    return f'<!-- wp:list -->\n<ul class="wp-block-list">{inner}</ul>\n<!-- /wp:list -->'


# --------------------------------------------------------------------------
# Parse + assemble
# --------------------------------------------------------------------------

_HR = re.compile(r'(?m)^---\s*$')
_H_INTERVIEW = re.compile(r'(?m)^##\s+The Interview\s*$')
_H_ABOUT = re.compile(r'(?m)^##\s+About the Author\s*$')
_H_FIND = re.compile(r'(?m)^##\s+Find\b.*$')          # accepts multi-word names
_FIND_NAME = re.compile(r'(?m)^##\s+Find\s+(.+?)\s*$')
_META_LINE = re.compile(r'^\[|^Alt text:')


def _clean_block(block):
    """Join a block's lines, dropping image-meta lines ([...] / Alt text:)."""
    lines = [ln.strip() for ln in block.splitlines()
             if not _META_LINE.match(ln.strip())]
    return ' '.join(lines).strip()


def parse_interview(path):
    """Parse a bundle-interview markdown file into its component pieces."""
    raw = open(path, encoding="utf-8").read()
    parts = _HR.split(raw)
    if len(parts) < 4:
        raise ValueError(f"{path}: expected 3 '---' separators, found {len(parts) - 1}")
    sec_a, sec_b, sec_c, sec_d = parts[0], parts[1], parts[2], parts[3]

    intro = []
    for block in re.split(r'\n\s*\n', sec_a.strip()):
        block = block.strip()
        if not block or block.startswith('# '):
            continue
        cleaned = _clean_block(block)
        if cleaned:
            intro.append(cleaned)

    body = _H_INTERVIEW.sub('', sec_b).strip()
    qa = [b.strip() for b in re.split(r'\n\s*\n', body) if b.strip()]

    about_and_find = _H_FIND.split(sec_c)
    about = _H_ABOUT.sub('', about_and_find[0]).strip()
    bio = [' '.join(ln.strip() for ln in b.splitlines())
           for b in re.split(r'\n\s*\n', about) if b.strip()]
    find_md = about_and_find[1].strip() if len(about_and_find) > 1 else ""
    find = [ln.strip()[2:].strip() for ln in find_md.splitlines()
            if ln.strip().startswith('- ')]
    name_match = _FIND_NAME.search(sec_c)
    find_name = name_match.group(1) if name_match else ""

    cta = [' '.join(x.strip() for x in b.splitlines())
           for b in re.split(r'\n\s*\n', sec_d.strip()) if b.strip()]
    cta = [c for c in cta if not _META_LINE.match(c)]

    return {"intro": intro, "qa": qa, "bio": bio, "find": find,
            "find_name": find_name, "cta": cta}


def assemble_interview(parsed, cover_id, cover_url, cover_alt,
                       bundle_id, bundle_url, bundle_alt, width_px=300):
    """Build the full Gutenberg content string for an interview post."""
    blocks = [cover_block(cover_id, cover_url, cover_alt, width_px)]
    blocks += [paragraph(t) for t in parsed["intro"]]
    blocks += [SEPARATOR, heading("The Interview")]
    blocks += [paragraph(t) for t in parsed["qa"]]
    blocks += [SEPARATOR, heading("About the Author")]
    blocks += [paragraph(t) for t in parsed["bio"]]
    if parsed["find"]:
        blocks += [heading(f"Find {parsed['find_name']}"), list_block(parsed["find"])]
    blocks += [SEPARATOR, image_block(bundle_id, bundle_url, bundle_alt)]
    blocks += [paragraph(t) for t in parsed["cta"]]
    return "\n\n".join(blocks)


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------

_TAG = re.compile(r'<[^>]+>')
_BAD_QUOTE = re.compile(r'(?:<p>|<strong>|<em>|&mdash;)&rdquo;')
_JAMIE_FLAG = re.compile(r'\[JAMIE\b|\[Jamie\b', re.IGNORECASE)
_LEAK = re.compile(r'\[(?:Featured image|Book cover|Bundle montage)\b'
                   r'|Alt text:\s*[&"“]')


def verify(content):
    """Return a list of problems with generated content (empty == clean)."""
    problems = []
    text = _TAG.sub('', content)
    if '*' in text:
        problems.append("stray markdown asterisk in text")
    if _BAD_QUOTE.search(content):
        problems.append("opening quote rendered as a closing &rdquo;")
    if _JAMIE_FLAG.search(content):
        problems.append("leftover [JAMIE:] reviewer flag in body")
    if _LEAK.search(text):
        problems.append("leaked image-meta line ([Featured image/...] or 'Alt text:')")
    return problems


# --------------------------------------------------------------------------
# WordPress REST client (retry-wrapped; transient 5xx are common on WPEngine)
# --------------------------------------------------------------------------

class WP:
    def __init__(self, base, user, password, tries=4):
        self.base = base.rstrip('/')
        self.auth = base64.b64encode(f"{user}:{password}".encode()).decode()
        self.tries = tries
        self.ctx = ssl.create_default_context()

    def request(self, path, data=None, method="GET", content_type=None,
                disposition=None):
        url = path if path.startswith("http") else self.base + path
        last = None
        for attempt in range(self.tries):
            try:
                req = urllib.request.Request(url, data=data, method=method)
                req.add_header("Authorization", f"Basic {self.auth}")
                req.add_header("User-Agent", "rookwood/1.0")  # WPEngine 1010s without a UA
                if content_type:
                    req.add_header("Content-Type", content_type)
                if disposition:
                    req.add_header("Content-Disposition", disposition)
                with urllib.request.urlopen(req, context=self.ctx, timeout=90) as resp:
                    raw = resp.read().decode("utf-8", "replace")
                    raw = re.sub(r'[\x00-\x1f]',
                                 lambda m: {'\t': '\\t', '\n': '\\n',
                                            '\r': '\\r'}.get(m.group(), ' '), raw)
                    return json.loads(raw)
            except urllib.error.HTTPError as e:
                last = e
                if e.code >= 500 and attempt < self.tries - 1:
                    sys.stderr.write(f"  retry {attempt + 1} after HTTP {e.code}\n")
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
            except Exception as e:  # noqa: BLE001 -- network flakiness, retry
                last = e
                if attempt < self.tries - 1:
                    sys.stderr.write(f"  retry {attempt + 1} after {e}\n")
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        raise last

    @staticmethod
    def _wp_filename(local_name):
        """WordPress turns spaces into hyphens on upload (case preserved on
        WPEngine). Used to match an already-uploaded file when resuming."""
        return local_name.replace(' ', '-')

    def upload_media(self, path, mime, alt, reuse=True):
        """Upload a local file and set its alt text. If reuse=True, first look
        for an already-uploaded attachment with the same (sanitized) filename
        and reuse it -- this makes a re-run after a mid-batch 5xx idempotent
        instead of creating duplicate attachments."""
        fn = os.path.basename(path)
        wp_fn = self._wp_filename(fn)
        if reuse:
            stem = os.path.splitext(fn)[0]
            hits = self.request("/media?search=%s&per_page=30&_fields=id,source_url"
                                % urllib.parse.quote(stem))
            for h in hits or []:
                base = os.path.basename(h.get("source_url", ""))
                # ignore a trailing -<n> WordPress may append on collisions
                norm = re.sub(r'-\d+(?=\.\w+$)', '', base)
                if norm.lower() == wp_fn.lower():
                    self._set_alt(h["id"], alt)
                    return h["id"], h["source_url"], True
        body = open(path, "rb").read()
        media = self.request("/media", data=body, method="POST",
                             content_type=mime,
                             disposition=f'attachment; filename="{fn}"')
        self._set_alt(media["id"], alt)
        return media["id"], media["source_url"], False

    def _set_alt(self, media_id, alt):
        self.request(f"/media/{media_id}",
                     data=json.dumps({"alt_text": alt}).encode(),
                     method="POST", content_type="application/json")

    def find_or_create_tag(self, name):
        hits = self.request("/tags?search=%s&_fields=id,name"
                            % urllib.parse.quote(name))
        for h in hits or []:
            if h["name"].lower() == name.lower():
                return h["id"], False
        tag = self.request("/tags", data=json.dumps({"name": name}).encode(),
                          method="POST", content_type="application/json")
        return tag["id"], True

    def find_post_by_slug(self, slug):
        for status in ("draft", "publish", "future", "pending", "private"):
            hits = self.request(f"/posts?slug={urllib.parse.quote(slug)}"
                               f"&status={status}&_fields=id,status")
            if hits:
                return hits[0]
        return None

    def create_post(self, payload):
        return self.request("/posts", data=json.dumps(payload).encode(),
                           method="POST", content_type="application/json")


# --------------------------------------------------------------------------
# Config + CLI
# --------------------------------------------------------------------------

def load_password(env_path):
    for line in open(env_path):
        if line.startswith("CLAUDE_BLACKBIRD_WP_PASSWORD="):
            return line.split("=", 1)[1].strip().strip('"').replace(" ", "")
    raise SystemExit(f"CLAUDE_BLACKBIRD_WP_PASSWORD not found in {env_path}")


def process_post(wp, post, defaults, dry_run):
    """Convert and (unless dry-run) create one draft. Returns a report dict."""
    parsed = parse_interview(post["interview_md"])
    width = defaults.get("cover_width_px", 300)
    report = {"title": post["title"], "slug": post["slug"], "qa_blocks": len(parsed["qa"])}

    if dry_run:
        # Use placeholder ids/urls so the conversion + checks can run offline.
        content = assemble_interview(
            parsed, "COVER", post.get("cover_alt", ""), post.get("cover_alt", ""),
            defaults["bundle_banner_id"], defaults["bundle_banner_url"],
            defaults["bundle_banner_alt"], width)
        report["problems"] = verify(content)
        report["content"] = content
        return report

    banner_id, banner_url, banner_reused = wp.upload_media(
        post["banner"], _mime(post["banner"]), post["banner_alt"],
        reuse=defaults.get("reuse_media", True))
    cover_id, cover_url, cover_reused = wp.upload_media(
        post["cover"], _mime(post["cover"]), post["cover_alt"],
        reuse=defaults.get("reuse_media", True))
    tag_id, tag_created = wp.find_or_create_tag(post["author_tag"])

    content = assemble_interview(
        parsed, cover_id, cover_url, post["cover_alt"],
        defaults["bundle_banner_id"], defaults["bundle_banner_url"],
        defaults["bundle_banner_alt"], width)
    problems = verify(content)
    report["problems"] = problems
    if problems:
        report["created"] = False
        return report  # refuse to create a post that fails its own checks

    existing = wp.find_post_by_slug(post["slug"])
    if existing:
        report["created"] = False
        report["existing_post"] = existing["id"]
        report["banner_id"] = banner_id
        report["cover_id"] = cover_id
        return report

    payload = {
        "title": post["title"], "slug": post["slug"], "status": "draft",
        "content": content, "categories": [defaults["category"]],
        "tags": [defaults["series_tag"], tag_id], "author": defaults["author"],
        "featured_media": banner_id,
    }
    if post.get("excerpt"):
        payload["excerpt"] = post["excerpt"]
    res = wp.create_post(payload)
    report.update({
        "created": True, "post_id": res["id"], "link": res["link"],
        "banner_id": banner_id, "banner_reused": banner_reused,
        "cover_id": cover_id, "cover_reused": cover_reused,
        "author_tag_id": tag_id, "author_tag_created": tag_created,
    })
    return report


def _mime(path):
    ext = os.path.splitext(path)[1].lower()
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp"}.get(ext.lstrip('.'), "image/jpeg")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, help="batch config JSON (see skill)")
    ap.add_argument("--dry-run", action="store_true",
                    help="convert + self-check + print HTML; touch nothing")
    ap.add_argument("--env", default=os.path.expanduser(
        "~/Dropbox/dev/pub-tools/.env"), help="path to .env with WP password")
    args = ap.parse_args()

    cfg = json.load(open(args.config))
    defaults = cfg["defaults"]
    rest = cfg.get("rest", {})
    base = rest.get("base", "https://blackbirdpublishing.com/wp-json/wp/v2")
    user = rest.get("user", "claude")

    wp = None
    if not args.dry_run:
        wp = WP(base, user, load_password(args.env))

    any_problem = False
    for post in cfg["posts"]:
        sys.stderr.write(f"\n=== {post['title']} ===\n")
        report = process_post(wp, post, defaults, args.dry_run)
        if args.dry_run:
            print(f"\n===== {report['title']} ({report['qa_blocks']} Q&A blocks) =====")
            if report["problems"]:
                any_problem = True
                print("  PROBLEMS:", "; ".join(report["problems"]))
            else:
                print("  checks: clean")
            print(report["content"])
        else:
            if report["problems"]:
                any_problem = True
                print(f"SKIPPED {report['slug']}: {'; '.join(report['problems'])}")
            elif report.get("existing_post"):
                print(f"EXISTS  {report['slug']}: post {report['existing_post']} "
                      f"already exists (uploaded media "
                      f"banner={report['banner_id']} cover={report['cover_id']}); "
                      f"did not create a duplicate")
            else:
                print(f"CREATED post {report['post_id']} | "
                      f"featured {report['banner_id']}"
                      f"{' (reused)' if report['banner_reused'] else ''} | "
                      f"cover {report['cover_id']}"
                      f"{' (reused)' if report['cover_reused'] else ''} | "
                      f"author tag {report['author_tag_id']}"
                      f"{' (new)' if report['author_tag_created'] else ''} | "
                      f"{report['link']}")
    sys.exit(1 if any_problem else 0)


if __name__ == "__main__":
    main()
