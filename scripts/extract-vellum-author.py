#!/usr/bin/env python3
"""Extract author bio and social links from a Vellum file.

The Vellum file is an NSKeyedArchiver binary plist inside a zip archive.
Structure: book → rootElementContainer → children[2] ("Author and collection
information") → 3 alphabetical parts (A-H, J-M, N-Z) → individual author
entries → sub-children with bio text and social profiles.

Usage:
    python3 extract-vellum-author.py "Author Name"
    python3 extract-vellum-author.py --list
    python3 extract-vellum-author.py --json "Author Name"
"""

import argparse
import json
import os
import plistlib
import sys
import zipfile

VELLUM_PATH = os.path.expanduser(
    "~/Dropbox/Jamie/Writing and Publishing/Blackbird Publishing/"
    "Publishing/Book files : formatting/Info to reuse/"
    "Author and Collection Information.vellum"
)


def load_vellum(path):
    with zipfile.ZipFile(path) as z:
        with z.open("content.vellumcontent") as f:
            return plistlib.load(f)


def resolve(objects, obj):
    if isinstance(obj, plistlib.UID):
        return objects[obj.data]
    return obj


def get_children(objects, container):
    children_ref = container.get("children")
    children = resolve(objects, children_ref)
    if isinstance(children, dict) and "NS.objects" in children:
        return [resolve(objects, uid) for uid in children["NS.objects"]]
    return []


def get_text(objects, element):
    text_ref = element.get("text")
    if text_ref is None:
        return ""
    resolved = resolve(objects, text_ref)
    if isinstance(resolved, str):
        return resolved
    if isinstance(resolved, dict):
        ns = resolved.get("NSString")
        if ns:
            return resolve(objects, ns)
    return ""


def get_social(objects, element):
    sv_ref = element.get("socialProfileValues")
    if sv_ref is None:
        return {}
    sv = resolve(objects, sv_ref)
    if not isinstance(sv, dict) or "NS.keys" not in sv:
        return {}
    keys = [resolve(objects, k) for k in sv["NS.keys"]]
    vals = []
    for v in sv["NS.objects"]:
        rv = resolve(objects, v)
        if isinstance(rv, dict) and "NS.string" in rv:
            rv = resolve(objects, rv["NS.string"])
        vals.append(rv)
    return dict(zip(keys, vals))


def get_all_authors(objects, data):
    """Return list of (name, author_element) tuples."""
    book = resolve(objects, data["$top"]["book"])
    root = resolve(objects, book["rootElementContainer"])
    root_children = get_children(objects, root)
    author_volume = root_children[2]  # "Author and collection information"
    parts = get_children(objects, author_volume)

    authors = []
    for part in parts:
        for author_el in get_children(objects, part):
            name = resolve(objects, author_el.get("title", ""))
            if name and name != "Copyright / author name":
                authors.append((name, author_el))
    return authors


def extract_author_info(objects, author_el):
    """Extract bio text(s) and social links from an author element."""
    children = get_children(objects, author_el)

    bios = []
    social = {}
    last_updated = None

    for child in children:
        title = resolve(objects, child.get("title", ""))
        text = get_text(objects, child)
        child_social = get_social(objects, child)

        # First child is usually a date
        if not last_updated and title and len(title) == 10 and "-" in title:
            last_updated = title
            continue

        # Skip "Copyright / author name" and "Author links" entries
        if title == "Copyright / author name":
            continue
        if title == "Author links":
            continue

        if text:
            label = title if title else "bio"
            bios.append({"label": label, "text": text})

        if child_social:
            # Merge, keeping non-empty values
            for k, v in child_social.items():
                if v and (k not in social or not social[k]):
                    social[k] = v

    return {
        "last_updated": last_updated,
        "bios": bios,
        "social": social,
    }


def find_author(authors, query):
    """Find author by name (case-insensitive, partial match)."""
    query_lower = query.lower()

    # Exact match first
    for name, el in authors:
        if name.lower() == query_lower:
            return name, el

    # Partial match
    matches = [(name, el) for name, el in authors if query_lower in name.lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        names = [m[0] for m in matches]
        print(f"Multiple matches for '{query}': {', '.join(names)}", file=sys.stderr)
        print("Please be more specific.", file=sys.stderr)
        sys.exit(1)

    print(f"No author found matching '{query}'.", file=sys.stderr)
    sys.exit(1)


def format_social_url(platform, value):
    """Ensure social link has https:// prefix."""
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return f"https://{value}"


def main():
    parser = argparse.ArgumentParser(description="Extract author info from Vellum file")
    parser.add_argument("name", nargs="?", help="Author name to search for")
    parser.add_argument("--list", action="store_true", help="List all authors")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--file", default=VELLUM_PATH, help="Path to Vellum file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Vellum file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    data = load_vellum(args.file)
    objects = data["$objects"]
    authors = get_all_authors(objects, data)

    if args.list:
        for name, _ in authors:
            print(name)
        return

    if not args.name:
        parser.print_help()
        sys.exit(1)

    name, author_el = find_author(authors, args.name)
    info = extract_author_info(objects, author_el)

    if args.json:
        output = {"name": name, **info}
        # Ensure social URLs have https://
        for k, v in output.get("social", {}).items():
            output["social"][k] = format_social_url(k, v)
        print(json.dumps(output, indent=2))
    else:
        print(f"Author: {name}")
        if info["last_updated"]:
            print(f"Last updated: {info['last_updated']}")
        print()
        for bio in info["bios"]:
            if bio["label"] != "bio":
                print(f"[{bio['label']}]")
            print(bio["text"])
            print()
        if info["social"]:
            print("Social links:")
            for platform, url in sorted(info["social"].items()):
                if url:
                    full_url = format_social_url(platform, url)
                    print(f"  {platform}: {full_url}")


if __name__ == "__main__":
    main()
