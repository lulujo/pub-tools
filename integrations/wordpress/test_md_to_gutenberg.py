#!/usr/bin/env python3
"""Tests for the md_to_gutenberg inline converter and verifier.

Each case here is a bug we actually hit while posting the Escape from 2026
StoryBundle interviews. Run after any change to md_to_gutenberg.py:

    python3 integrations/wordpress/test_md_to_gutenberg.py

Exits non-zero on the first failure.
"""

import sys

from md_to_gutenberg import inline, verify, list_block

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

    total = len(CASES) + len(verify_cases) + 1
    if failures:
        print(f"\n{failures} of {total} checks FAILED")
        return 1
    print(f"All {total} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
