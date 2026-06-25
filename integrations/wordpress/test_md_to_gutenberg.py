#!/usr/bin/env python3
"""Tests for the md_to_gutenberg inline converter and verifier.

Each case here is a bug we actually hit while posting the Escape from 2026
StoryBundle interviews. Run after any change to md_to_gutenberg.py:

    python3 integrations/wordpress/test_md_to_gutenberg.py

Exits non-zero on the first failure.
"""

import os
import sys
import tempfile

from md_to_gutenberg import (inline, verify, list_block,
                             parse_sidecar_text, read_sidecar, resolve_post,
                             parse_interview, assemble_interview, process_post)


def _parse_text(md):
    """Helper: write markdown to a temp file and parse it."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "interview_post.md")
        open(p, "w", encoding="utf-8").write(md)
        return parse_interview(p)


def _headings(body):
    return [t for k, t in ((i[0], i[1] if len(i) > 1 else None) for i in body)
            if k == "heading"]


def _kinds(body):
    return [i[0] for i in body]

CASES = [
    # (description, markdown input, expected HTML output)
    ("apostrophe -> rsquo",
     "don't", "don&rsquo;t"),
    ("simple double quotes",
     'she said "hello" there', "she said &ldquo;hello&rdquo; there"),
    ("em dash strips surrounding spaces",
     "grief — and loss", "grief&mdash;and loss"),
    ("en dash kept, spaces untouched (number range)",
     "killed 10–15 million", "killed 10&ndash;15 million"),
    ("ellipsis -> hellip",
     "as for my narrator… hm", "as for my narrator&hellip; hm"),
    ("superscript two -> sup2",
     "E=mc²", "E=mc&sup2;"),
    ("bare ampersand -> amp",
     "Crime & Mayhem", "Crime &amp; Mayhem"),
    ("existing entity not double-encoded",
     "a &amp; b", "a &amp; b"),
    ("accented letter left as UTF-8",
     "à la Wells", "à la Wells"),
    ("simple italics",
     "in *whack* instead", "in <em>whack</em> instead"),
    ("underscore italics",
     "read _Monster Road Trip_ now", "read <em>Monster Road Trip</em> now"),
    ("snake_case is NOT italicized",
     "the monster_road_trip folder", "the monster_road_trip folder"),
    ("bold wraps the whole question",
     "**Why this?**", "<strong>Why this?</strong>"),
    # The two that bit us hardest:
    ("nested italics inside a bold question (non-greedy bold)",
     "**You co-write *Gray Lady* novels?**",
     "<strong>You co-write <em>Gray Lady</em> novels?</strong>"),
    ("opening quote right after bold markers",
     '**"Comstock" appears here**',
     "<strong>&ldquo;Comstock&rdquo; appears here</strong>"),
    ("opening quote right after an em dash",
     'justice—"something we need"',
     "justice&mdash;&ldquo;something we need&rdquo;"),
    # Links, including a link whose text is italicized:
    ("plain markdown link",
     "[King Leopold](https://atrocitieswatch.org/x/)",
     '<a href="https://atrocitieswatch.org/x/" target="_blank" '
     'rel="noopener">King Leopold</a>'),
    ("link with italic text nests em inside a",
     "[*Laserblasted*](https://mwl.io/x.html)",
     '<a href="https://mwl.io/x.html" target="_blank" rel="noopener">'
     '<em>Laserblasted</em></a>'),
    ("bold link in CTA",
     "**[Escape from 2026 StoryBundle](https://storybundle.com/timetravel)**",
     '<strong><a href="https://storybundle.com/timetravel" target="_blank" '
     'rel="noopener">Escape from 2026 StoryBundle</a></strong>'),
]


def run():
    failures = 0
    for desc, src, expected in CASES:
        got = inline(src)
        if got != expected:
            failures += 1
            print(f"FAIL: {desc}")
            print(f"   in:       {src!r}")
            print(f"   expected: {expected!r}")
            print(f"   got:      {got!r}")
    # verify() should flag the things it's meant to catch.
    verify_cases = [
        ("clean content", "<p>all good here</p>", []),
        ("stray asterisk", "<p>a * b</p>", ["stray markdown asterisk in text"]),
        ("flipped opening quote",
         "<p>&rdquo;Comstock</p>",
         ["opening quote rendered as a closing &rdquo;"]),
        ("leftover jamie flag",
         "<p>[Jamie: confirm socials]</p>",
         ["leftover [JAMIE:] reviewer flag in body"]),
    ]
    for desc, content, expected in verify_cases:
        got = verify(content)
        if got != expected:
            failures += 1
            print(f"FAIL (verify): {desc}")
            print(f"   expected: {expected!r}")
            print(f"   got:      {got!r}")

    # list_block sanity
    lb = list_block(["[smithwriter.com](http://www.smithwriter.com/)"])
    if "wp-block-list" not in lb or "smithwriter.com</a>" not in lb:
        failures += 1
        print("FAIL: list_block did not render link list item")

    # --- sidecar (post.yaml) parsing ---
    SIDECAR = '''# Escape from 2026 — Douglas Smith
title: "Interview: Douglas Smith on Into the Time Slip"
slug: interview-douglas-smith-into-the-time-slip
banner: blog_header_images/douglas_smith.png
cover: "All Covers/Into the Time Slip Cover Final.jpg"
banner_alt: "Interview with Douglas Smith — Into the Time Slip — Escape from 2026 StoryBundle"
cover_alt: "Cover of Into the Time Slip by Douglas Smith"
author_tag: "Douglas Smith"
excerpt: "A short excerpt."
'''
    sc = parse_sidecar_text(SIDECAR)
    sidecar_checks = [
        ("title keeps its colon", sc.get("title"), "Interview: Douglas Smith on Into the Time Slip"),
        ("unquoted slug", sc.get("slug"), "interview-douglas-smith-into-the-time-slip"),
        ("unquoted path", sc.get("banner"), "blog_header_images/douglas_smith.png"),
        ("quoted path with spaces", sc.get("cover"), "All Covers/Into the Time Slip Cover Final.jpg"),
        ("author_tag", sc.get("author_tag"), "Douglas Smith"),
        ("comment line ignored", "# Escape from 2026 — Douglas Smith" in sc, False),
    ]
    for desc, got, expected in sidecar_checks:
        if got != expected:
            failures += 1
            print(f"FAIL (sidecar): {desc} — expected {expected!r}, got {got!r}")

    # resolve_post: relative paths join project_root; absolute untouched; sidecar
    # interview_md defaults to interview_post.md beside the sidecar.
    rp = resolve_post(
        {"banner": "b/x.png", "cover": "c/y.jpg", "interview_md": "a/i.md"},
        {"project_root": "/ROOT"})
    resolve_checks = [
        ("relative banner", rp["banner"], "/ROOT/b/x.png"),
        ("relative cover", rp["cover"], "/ROOT/c/y.jpg"),
        ("relative interview_md", rp["interview_md"], "/ROOT/a/i.md"),
    ]
    abs_rp = resolve_post({"banner": "/abs/x.png"}, {"project_root": "/ROOT"})
    resolve_checks.append(("absolute path untouched", abs_rp["banner"], "/abs/x.png"))

    with tempfile.TemporaryDirectory() as d:
        scp = os.path.join(d, "post.yaml")
        open(scp, "w", encoding="utf-8").write(SIDECAR)
        rp2 = resolve_post({"sidecar": scp}, {"project_root": d})
        resolve_checks.append(
            ("sidecar fills slug", rp2.get("slug"), "interview-douglas-smith-into-the-time-slip"))
        resolve_checks.append(
            ("interview_md defaults beside sidecar", rp2.get("interview_md"),
             os.path.join(d, "interview_post.md")))
        resolve_checks.append(
            ("sidecar relative banner joins root", rp2.get("banner"),
             os.path.join(d, "blog_header_images/douglas_smith.png")))

    for desc, got, expected in resolve_checks:
        if got != expected:
            failures += 1
            print(f"FAIL (resolve): {desc} — expected {expected!r}, got {got!r}")

    # --- format-agnostic body parsing (3 real formats) ---
    format_checks = []

    # (1) single-author: one '## The Interview', '---' before About, Find list
    SINGLE = ('# T\n\n[Featured image: x]\nAlt text: "x"\n\nIntro.\n\n---\n\n'
              '## The Interview\n\n**Q?**\n\nAnswer.\n\n---\n\n'
              '## About the Author\n\nBio para.\n\n## Find X\n\n- [x.com](https://x.com/)\n\n'
              '---\n\n[Bundle montage image: 5698]\nAlt text: "b"\n\n*T* is available.\n')
    s = _parse_text(SINGLE)
    format_checks += [
        ("single: intro", s["intro"], ["Intro."]),
        ("single: headings in order", _headings(s["body"]),
         ["The Interview", "About the Author", "Find X"]),
        ("single: one internal separator (before About)",
         _kinds(s["body"]).count("sep"), 1),
        ("single: Find rendered as a list", any(k == "list" for k in _kinds(s["body"])), True),
        ("single: cta", s["cta"], ["*T* is available."]),
    ]

    # (2) parallel/joint: '---' between questions, two editors per Q
    PARALLEL = ('# T\n\nIntro.\n\n---\n\n## The Interview\n\n**Q1?**\n\n'
                '**A:** one.\n\n**B:** two.\n\n---\n\n**Q2?**\n\n**A:** three.\n\n**B:** four.\n\n'
                '---\n\n## About the Editors\n\n**A** writes.\n\n**B** writes.\n\n---\n\nDone.\n')
    pp = _parse_text(PARALLEL)
    html = assemble_interview(pp, 1, "u", "a", 5698, "bu", "ba")
    format_checks += [
        ("parallel: about heading captured", "About the Editors" in _headings(pp["body"]), True),
        ("parallel: 2 internal separators (between Qs + before About)",
         _kinds(pp["body"]).count("sep"), 2),
        ("parallel: both editor answers kept",
         "<strong>A:</strong> one." in html and "<strong>B:</strong> two." in html, True),
        ("parallel: About the Editors heading rendered",
         '<h2 class="wp-block-heading">About the Editors</h2>' in html, True),
    ]

    # (3) compiled group: a '## <name>' section per contributor + bulleted About
    COMPILED = ('# T\n\nIntro.\n\n---\n\n## Mark — "S"\n\n**Q?**\n\nMark ans.\n\n---\n\n'
                '## Dee — "P"\n\n**Q?**\n\nDee ans.\n\n---\n\n## And, asked of all…\n\n'
                '**Q?**\n\n**Mark:** m.\n\n**Dee:** d.\n\n---\n\n## About the Contributors\n\n'
                '- **Mark** writes. [m.com](https://m.com/)\n- **Dee** writes. [d.com](https://d.com/)\n\n'
                '---\n\n[Bundle montage image: 5698]\nAlt text: "b"\n\n*T* is available.\n')
    cp = _parse_text(COMPILED)
    chtml = assemble_interview(cp, 1, "u", "a", 5698, "bu", "ba")
    format_checks += [
        ("compiled: per-contributor + shared headings (raw text)",
         _headings(cp["body"]),
         ['Mark — "S"', 'Dee — "P"', 'And, asked of all…', 'About the Contributors']),
        ("compiled: bulleted About becomes a list",
         any(k == "list" for k in _kinds(cp["body"])), True),
        ("compiled: contributor heading em-dash/quotes encoded in output",
         '<h2 class="wp-block-heading">Mark&mdash;&ldquo;S&rdquo;</h2>' in chtml, True),
        ("compiled: shared-question names bolded",
         "<strong>Mark:</strong> m." in chtml and "<strong>Dee:</strong> d." in chtml, True),
        ("compiled: About list has both bios with links",
         chtml.count('<li>') == 2 and 'href="https://m.com/"' in chtml, True),
    ]

    for desc, got, expected in format_checks:
        if got != expected:
            failures += 1
            print(f"FAIL (format): {desc} — expected {expected!r}, got {got!r}")

    # --- process_post dry-run (exercises the CLI path, not just parse/assemble;
    #     this is the layer where a parser-shape change can break the report) ---
    proc_checks = []
    with tempfile.TemporaryDirectory() as d:
        mp = os.path.join(d, "interview_post.md")
        open(mp, "w", encoding="utf-8").write(SINGLE)
        defaults = {"category": 4, "author": 2, "series_tag": 393,
                    "bundle_banner_id": 5698, "bundle_banner_url": "u",
                    "bundle_banner_alt": "b", "cover_width_px": 300}
        post = {"interview_md": mp, "title": "T", "slug": "t", "banner": "b.png",
                "banner_alt": "ba", "cover": "c.jpg", "cover_alt": "ca",
                "author_tag": "X"}
        rep = process_post(None, post, defaults, dry_run=True)  # wp=None ok in dry-run
        proc_checks = [
            ("process_post dry-run reports no problems", rep.get("problems"), []),
            ("process_post dry-run produced content", bool(rep.get("content")), True),
            ("process_post dry-run counted body blocks", rep.get("blocks", 0) > 0, True),
        ]
        for desc, got, expected in proc_checks:
            if got != expected:
                failures += 1
                print(f"FAIL (process_post): {desc} — expected {expected!r}, got {got!r}")

    total = (len(CASES) + len(verify_cases) + 1 + len(sidecar_checks)
             + len(resolve_checks) + len(format_checks) + len(proc_checks))
    if failures:
        print(f"\n{failures} of {total} checks FAILED")
        return 1
    print(f"All {total} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
