#!/usr/bin/env python3

from __future__ import annotations

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
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

"""
Global variables
"""

BASE_DIR = Path(__file__).parent.parent
ENTRIES_JSON = BASE_DIR / "static" / "data" / "entries.json"
MARKDOWN_ENTRIES = BASE_DIR / "content" / "entries"

"""
Helper functions
"""

# Dictionary mapping month numbers to month names
ID_MONTH_MAPPING = dict((num, name) for (num, name) in enumerate(calendar.month_name))

# Dictionary mapping month names to month numbers
MONTH_ID_MAPPING = dict((name, num) for (num, name) in enumerate(calendar.month_name))

def truncate_abstract(abstract: str, max_len: int = 0):
    """Truncate an abstract to a maximum possible length. If the maximum length is set to
    zero then we don't perform any truncation at all."""
    return (abstract if max_len <= 0 else abstract[:max_len])

@dataclass
class PublicationDate:
    year: int
    month: Optional[int]

    # Create a mapping between month number and month name, and vice-versa
    __NUM_TO_MONTH_MAPPING = dict((num, name) for (num, name) in enumerate(calendar.month_name))
    __MONTH_TO_NUM_MAPPING = dict((name, num) for (num, name) in enumerate(calendar.month_name))

    @classmethod
    def parse_bibtex(cls, bibtex_entry: dict) -> Optional[PublicationDate]:
        if "year" not in bibtex_entry:
            return None
        else:
            year = int(bibtex_entry["year"])
            month = cls.__MONTH_TO_NUM_MAPPING.get(bibtex_entry.get("month"))
            return cls(year, month)

    def __str__(self) -> str:
        if self.month is None:
            return str(self.year)
        else:
            return f"{self.__NUM_TO_MONTH_MAPPING[self.month]} {self.year}"


@dataclass
class CompendiumEntry:
    """Wraps a single entry in the compendium."""

    title: str
    abstract: Optional[str]
    date: Optional[PublicationDate]
    authors: List[str]
    publisher: Optional[str]
    url: Optional[str]
    tags: List[str]

    __AUTHORS_REGEX = re.compile(r"\{([^\}]+)\}")

    @classmethod
    def parse_bibtex(cls, bibtex_entry: dict) -> CompendiumEntry:
        date = PublicationDate.parse_bibtex(bibtex_entry)
        abstract = bibtex_entry.get("abstract")
        url = bibtex_entry.get("url")

        # Tags are comma-separated under the 'keywords' field
        tags = bibtex_entry.get("keywords", [])
        if tags != []:
            tags = tags.split(", ")

        # Publisher info is usually contained under one of multiple possible keys
        publisher = (bibtex_entry.get(k) for k in ("publisher", "journal", "journaltitle"))
        publisher = next(filter(lambda info: info is not None, publisher), None)

        # TODO (kernelmethod): less hacky way to get around removing brackets from titles
        title = bibtex_entry.get("title")
        if title is not None:
            title = title.replace("{", "").replace("}", "")

            # Replace weird character strings in the title that sometimes occur, e.g. "\&"
            title = title.replace("\\", "\\\\")

        authors = bibtex_entry.get("author", [])
        if authors != []:
            matches = cls.__AUTHORS_REGEX.findall(authors)
            authors = matches if len(authors) > 0 else [authors]

        return cls(title, abstract, date, authors, publisher, url, tags)

    def to_markdown(self) -> str:
        # The title is expected to be wrapped in quotes, so we have to replace occurrences of
        # " with \"
        title = self.title.replace('"', '\\"')
        markdown = f"""\
+++
draft = false
title = "{title}"
tags = {self.tags}
+++\n\n"""

        content = []

        if len(self.authors) > 0:
            content.append(f"**Authors**: {', '.join(self.authors)}")
        if self.date is not None:
            content.append(f"**Published**: {self.date}")
        if self.url is not None:
            content.append(f"**URL**: [{self.url}]({self.url})")
        if len(self.tags) > 0:
            tags = map(lambda t: f"{{{{< tag tagname=\"{t}\" >}}}}", self.tags)
            content.append(f"**Tags**: {' '.join(tags)}")
        if self.abstract is not None:
            content.append(f"**Abstract**: {self.abstract}")

        content = "\n\n".join(content)
        markdown += content
        return markdown

    def to_json(self) -> dict:
        """Convert the CompendiumEntry to a dictionary compatible
        with JSON."""
        return {
            "title": self.title,
            "abstract": truncate_abstract(self.abstract),
            "publisher": self.publisher,
            "date": str(self.date) if self.date is not None else None,
            "url": self.url,
            "authors": self.authors,
            "tags": self.tags,
        }

    def slug(
        self,
        max_length: int = 50,
        add_hash: bool = False,
        hash_len: int = 8,
    ) -> str:
        """Return a slug for the entry name."""
        from hashlib import sha256
        from slugify import slugify

        slug = slugify(self.title, max_length=max_length)

        if add_hash:
            # Create a hash of the entire CompendiumEntry and add its first few characters
            # to the slug.
            data = json.dumps(self.to_json()).encode("utf-8")
            h = sha256(data).hexdigest()
            slug += "-" + h[:hash_len]

        return slug


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

    return [CompendiumEntry.parse_bibtex(v) for v in bib_db.values()]

"""
Argument parser
"""

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "infile", help="BibTeX file containing the site's compendium entries.",
)
parser.add_argument(
    "--remove-old-entries",
    action="store_true",
    help="Remove old entries from the content directory",
)

"""
Main script
"""

if __name__ == "__main__":
    args = parser.parse_args()
    entries = parse_bibtex(args.infile)

    # Check that all slugs are unique (otherwise we could end up overwriting a compendium
    # entry). If they aren't, that's probably an indicator that two entries are identical.
    slugs = [e.slug(add_hash=True) for e in entries]
    duplicate_slugs = [slug for (slug, count) in Counter(slugs).items() if count > 1]
    if len(duplicate_slugs) > 0:
        raise RuntimeError(f"Duplicate slugs detected: {duplicate_slugs}")

    # If --remove-old-entries was specified, we should delete existing entries before
    # writing new ones
    if args.remove_old_entries:
        old_entries = MARKDOWN_ENTRIES.glob("*.md")
        old_entries = [p for p in old_entries if p.is_file()]
        for path in old_entries:
            path.unlink()

        print(f"Removed {len(old_entries)} old entries")

    # Save all of the entries as markdown files
    print(f"Writing markdown files to {MARKDOWN_ENTRIES}")
    for slug, entry in zip(slugs, entries):
        # Write markdown to corresponding file
        outfile = MARKDOWN_ENTRIES / f"{slug}.md"
        with open(outfile, "w") as f:
            f.write(entry.to_markdown())

    print(f"Wrote {len(entries)} entries")

    # Write entries to JSON
    entries_json = []
    for slug, e in zip(slugs, entries):
        e_json = e.to_json()
        e_json["slug"] = slug
        entries_json.append(e_json)

    entries_json = json.dumps(entries_json)

    with open(ENTRIES_JSON, "w") as f:
        f.write(entries_json)
    print(f"Wrote entries to {ENTRIES_JSON}")

