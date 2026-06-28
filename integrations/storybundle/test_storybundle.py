#!/usr/bin/env python3
"""Tests for storybundle.py, pinned against saved HTML fixtures.

StoryBundle markup can change without notice and expired bundles can't be
re-scraped, so we parse against committed fixtures (captured 2026-06-27 from
the live /humor bundle and /books/4837 detail page) rather than the network.
If StoryBundle redesigns, these break first -- re-capture a fixture and adjust
the parser anchors.

Run:  python3 test_storybundle.py
"""

import os
import unittest

import storybundle as sb

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as handle:
        return handle.read()


class ParseBylineTests(unittest.TestCase):
    def test_by_author(self):
        self.assertEqual(sb.parse_byline("by Gini Koch"), ("author", "Gini Koch"))

    def test_edited_by(self):
        self.assertEqual(
            sb.parse_byline("edited by Alex Shvartsman"),
            ("editor", "Alex Shvartsman"),
        )

    def test_no_prefix_kept_verbatim(self):
        # A byline with no recognized prefix is returned as-is (role=author).
        self.assertEqual(sb.parse_byline("Gini Koch"), ("author", "Gini Koch"))

    def test_strips_inner_tags(self):
        # On the detail page the byline wraps the name in <span><a>.
        role, author = sb.parse_byline(
            'edited by <span><a href="x">Alex Shvartsman</a></span>'
        )
        self.assertEqual((role, author), ("editor", "Alex Shvartsman"))


class ParseBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = sb.parse_bundle(load("humor_bundle.html"))
        cls.by_id = {b["id"]: b for b in cls.books}

    def test_book_count(self):
        # /humor had 15 distinct books when captured.
        self.assertEqual(len(self.books), 15)

    def test_ids_unique(self):
        ids = [b["id"] for b in self.books]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_book_has_core_fields(self):
        for book in self.books:
            self.assertTrue(book["id"], book)
            self.assertTrue(book["title"], book)
            self.assertTrue(book["author"], book)
            self.assertTrue(book["cover_url"], book)
            self.assertIn("/books/", book["detail_url"])

    def test_known_book_by_author(self):
        book = self.by_id["4827"]
        self.assertEqual(book["title"], "Touched by an Alien")
        self.assertEqual(book["author"], "Gini Koch")
        self.assertEqual(book["role"], "author")

    def test_known_book_edited_by(self):
        book = self.by_id["4837"]
        self.assertEqual(book["title"], "Unidentified Funny Objects 9")
        self.assertEqual(book["author"], "Alex Shvartsman")
        self.assertEqual(book["role"], "editor")

    def test_cover_url_points_at_book_covers(self):
        book = self.by_id["4837"]
        self.assertIn("/book_covers/4837/", book["cover_url"])

    def test_bonus_tier_detected(self):
        # 'Middling Affliction' (4826) carries the bonus tier_1 marker.
        self.assertEqual(self.by_id["4826"]["tier"], "bonus")

    def test_base_tier_default(self):
        # A book with no bonus marker is base tier.
        self.assertEqual(self.by_id["4827"]["tier"], "base")

    def test_at_least_one_of_each_tier(self):
        tiers = {b["tier"] for b in self.books}
        self.assertEqual(tiers, {"base", "bonus"})


class ParseBundleEdgeTests(unittest.TestCase):
    def test_empty_html_returns_empty_list(self):
        # An expired bundle is a JS shell -- no <li class="book">. We must
        # return [] (caller warns), never crash.
        self.assertEqual(sb.parse_bundle("<html><body></body></html>"), [])

    def test_non_book_li_skipped(self):
        # An entry with a data-name but no /books/<id> href is not a book.
        html = (
            '<li class="book">'
            '<a class="book_detail_link" data-name="amazon" '
            'href="https://amazon.com/x"></a></li>'
            '<li class="book">'
            '<a class="book_detail_link" data-name="Real Book" '
            'href="https://storybundle.com/books/999">'
            '<img src="https://storybundle.com/system/book_covers/999/p/c.jpg" /></a>'
            "<em>by Someone</em></li>"
        )
        books = sb.parse_bundle(html)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]["id"], "999")

    def test_duplicate_id_deduped(self):
        # The cover anchor and name anchor share an id; a malformed double
        # <li> for the same book must not produce two entries.
        html = (
            '<li class="book">'
            '<a class="book_detail_link" data-name="A" '
            'href="https://storybundle.com/books/1"></a></li>'
            '<li class="book">'
            '<a class="book_detail_link" data-name="A" '
            'href="https://storybundle.com/books/1"></a></li>'
        )
        self.assertEqual(len(sb.parse_bundle(html)), 1)


class ParseBookDetailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.detail = sb.parse_book(load("book_4837.html"))

    def test_title(self):
        self.assertEqual(self.detail["title"], "Unidentified Funny Objects 9")

    def test_author_and_role(self):
        self.assertEqual(self.detail["author"], "Alex Shvartsman")
        self.assertEqual(self.detail["role"], "editor")

    def test_cover(self):
        self.assertIn("/book_covers/4837/", self.detail["cover_url"])

    def test_author_bio_present(self):
        # The first overview pane is the author/curator bio.
        self.assertTrue(self.detail["author_bio"])
        self.assertIn("Alex Shvartsman", self.detail["author_bio"])

    def test_synopsis_is_book_blurb_not_bio(self):
        # The synopsis comes from the separate <div class="description"> and
        # describes the BOOK, not the author -- the whole point of splitting
        # the fields. It must not be the bio text.
        self.assertTrue(self.detail["synopsis"])
        self.assertIn("Unidentified Funny Objects", self.detail["synopsis"])
        self.assertNotEqual(self.detail["synopsis"], self.detail["author_bio"])

    def test_no_legacy_description_field(self):
        # The ambiguous "description" field was renamed; it must be gone.
        self.assertNotIn("description", self.detail)


if __name__ == "__main__":
    unittest.main(verbosity=2)
