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
                             parse_interview, assemble_interview, SEP_MARKER)

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

    # --- parallel / joint-editor format (--- dividers between questions) ---
    PARALLEL = '''# Interview: A & B on Thing

[Featured image: x.png]
Alt text: "x"

Intro paragraph here.

---

## The Interview

**Q1?**

**A:** answer one.

**B:** answer two.

---

**Q2?**

**A:** answer three.

**B:** answer four.

---

## About the Editors

**A** is a writer.

**B** is also a writer.

## Find A & B

- A: [a.com](https://a.com/)
- B: [b.com](https://b.com/)

---

[Bundle montage image: media library item 5698]
Alt text: "bundle"

*Thing* is available now.
'''
    parallel_checks = []
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "interview_post.md")
        open(p, "w", encoding="utf-8").write(PARALLEL)
        pi = parse_interview(p)
        parallel_checks = [
            ("intro parsed", pi["intro"], ["Intro paragraph here."]),
            ("about heading captured (Editors)", pi["about_heading"], "About the Editors"),
            ("multi-name find", pi["find_name"], "A & B"),
            ("two bios", len(pi["bio"]), 2),
            ("two find links", len(pi["find"]), 2),
            ("one divider between the 2 questions (trailing trimmed)",
             pi["qa"].count(SEP_MARKER), 1),
            ("qa does not start/end with a divider",
             pi["qa"][0] != SEP_MARKER and pi["qa"][-1] != SEP_MARKER, True),
            ("both editor answers kept under Q1",
             pi["qa"][1].startswith("**A:**") and pi["qa"][2].startswith("**B:**"), True),
        ]
        for desc, got, expected in parallel_checks:
            if got != expected:
                failures += 1
                print(f"FAIL (parallel): {desc} — expected {expected!r}, got {got!r}")
        # assemble: divider renders as a separator; About heading is "Editors"
        html = assemble_interview(pi, 1, "u", "a", 5698, "bu", "ba")
        asm_checks = [
            ("About the Editors heading rendered",
             '<h2 class="wp-block-heading">About the Editors</h2>' in html),
            ("separator between questions rendered",
             html.count('wp:separator') >= 3),  # before interview, between Qs, before CTA
            ("editor label bolded", "<strong>A:</strong> answer one." in html),
            ("no separator sentinel leaked into output", SEP_MARKER not in html),
        ]
        parallel_checks += asm_checks
        for desc, ok in asm_checks:
            if not ok:
                failures += 1
                print(f"FAIL (parallel/assemble): {desc}")

    total = (len(CASES) + len(verify_cases) + 1
             + len(sidecar_checks) + len(resolve_checks) + len(parallel_checks))
    if failures:
        print(f"\n{failures} of {total} checks FAILED")
        return 1
    print(f"All {total} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
