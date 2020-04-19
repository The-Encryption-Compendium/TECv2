#!/usr/bin/env python3

"""
Python script to generate compendium entries for the site
"""

import argparse
import bibtexparser
import calendar
import json
import os
import re

from bibtexparser.bparser import BibTexParser

"""
Global variables
"""

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
ENTRIES_SCRIPT = os.path.relpath(
    os.path.join(BASE_DIR, "assets", "js", "entries.js"), os.getcwd()
)
MARKDOWN_ENTRIES_DIRECTORY = os.path.relpath(
    os.path.join(BASE_DIR, "content", "entries"), os.getcwd()
)

"""
Helper functions
"""

# Dictionary mapping month numbers to month names
ID_MONTH_MAPPING = dict((num, name) for (num, name) in enumerate(calendar.month_name))

# Dictionary mapping month names to month numbers
MONTH_ID_MAPPING = dict((name, num) for (num, name) in enumerate(calendar.month_name))

"""
BibTeX parsing
"""


def parse_bibtex(bibfile: str):
    """
    Read in a .bib file of compendium entries (as exported by Zotero) and
    convert it into a dictionary.
    """
    parser = BibTexParser(common_strings=True)
    with open(bibfile, "r") as f:
        bib_db = parser.parse_file(f).entries_dict

    entries = []
    for (ii, entry) in enumerate(bib_db.values()):
        year, month, day = _extract_date(entry)
        entries.append(
            {
                "id": ii,
                "title": _extract_title(entry),
                "abstract": entry.get("abstract"),
                "publisher_text": _extract_publisher(entry),
                "year": year,
                "month": month,
                "day": day,
                "url": entry.get("url"),
                "authors": _extract_authors(entry),
                "tags": _extract_tags(entry),
            }
        )

    return entries


def _extract_date(entry):
    # TODO: day
    year = entry.get("year")
    month = entry.get("month")
    if year is not None:
        year = int(year)
    if month is not None:
        month = MONTH_ID_MAPPING.get(month)
    return year, month, None


def _extract_title(entry):
    title = entry.get("title")
    if title is not None:
        # Strip brackets { } from the title
        title = title.replace("{", "").replace("}", "")
    return title


def _extract_publisher(entry):
    for key in ("publisher", "journal", "journaltitle"):
        if key in entry:
            return entry[key]
    return None


def _extract_tags(entry):
    tags = entry.get("keywords")
    if tags is not None:
        tags = tags.split(", ")
    else:
        tags = []
    return tags


def _extract_authors(entry):
    authors = entry.get("author")
    if authors is not None:
        patt = re.compile(r"\{([^\}]+)\}")
        authors = patt.findall(authors)
    else:
        authors = []
    return authors


"""
Markdown generation
"""


def generate_page_for_entry(entry: dict):
    """
    Take an entry from the compendium and convert it into a Markdown file
    that can be used by Hugo to create a page for the entry.
    """

    fields = []

    # Title
    # - Sometimes the titles contain weird character strings like
    #   "\&", which we have to fix so that they're rendered as intended.
    # - The title is expected to be wrapped in quotes, so we have to
    #   replace occurrences of " with \".
    title = entry["title"]
    title = title.replace("\\", "\\\\")
    title = title.replace('"', '\\"')

    # Authors
    authors = entry.get("authors")
    if len(authors) > 0:
        authors = f"**Authors**: {', '.join(authors)}"
    else:
        authors = None
    fields.append(authors)

    # Publication date
    year, month = entry.get("year"), entry.get("month")
    if year and month:
        date = f"**Published**: {ID_MONTH_MAPPING[month]} {year}"
    elif year:
        date = f"**Published**: {year}"
    else:
        date = None
    fields.append(date)

    # URL
    url = entry.get("url")
    if url:
        url = f"**URL**: [{url}]({url})"
    fields.append(url)

    # Abstract
    abstract = entry.get("abstract")
    if abstract:
        abstract = f"**Abstract**: {abstract}"
    fields.append(abstract)

    # Combine fields together, filtering out fields that didn't
    # appear in the entry
    fields = [f"{field}" for field in fields if field is not None]
    fields = "\n\n".join(fields)

    page = f"""\
+++
draft = false
title = "{title}"
tags = {entry.get('tags',[])}
+++
{fields}
"""

    entry_file = os.path.join(MARKDOWN_ENTRIES_DIRECTORY, f"{entry['id']}.md")
    with open(entry_file, "w") as f:
        f.write(page)


"""
Argument parser
"""

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "infile", help="BibTeX file containing the site's compendium entries.",
)

"""
Main script
"""

if __name__ == "__main__":
    args = parser.parse_args()
    entries = parse_bibtex(args.infile)
    entries_js = f"const entries = {json.dumps(entries, indent=2)}"

    with open(ENTRIES_SCRIPT, "w") as f:
        f.write(entries_js)
        print(f"Wrote entries to {ENTRIES_SCRIPT}")

    for entry in entries:
        generate_page_for_entry(entry)

    print(f"Created {len(entries)} pages in {MARKDOWN_ENTRIES_DIRECTORY}")
