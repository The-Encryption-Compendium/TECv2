#!/usr/bin/env python3

from argparse import ArgumentParser
from unicodedata import is_normalized, normalize
from typing import Optional
from logging import info, basicConfig
from os import environ, rename

parser = ArgumentParser()
parser.add_argument("infile", help="BibTeX file containing the site's compendium entries.")
parser.add_argument("--loglevel", default="info", help="set the log level (default: info)")
parser.add_argument("--form", default="NFKC", help="choose the preferred Unicode normal form (default: NFKC)")

if __name__ == "__main__":
    args = parser.parse_args()
    basicConfig(level=args.loglevel.upper())
    normed:Optional[str] = None
    with open(args.infile, 'r') as dataf:
        data = dataf.read()
        if not is_normalized(args.form, data):
            normed = normalize(args.form, data)
    if normed is not None:
        rename(args.infile, f"{args.infile}.unnormalized")
        info(f"normalization to {args.form} had an effect, overwriting {args.infile} (backed up to {args.infile}.unnormalized)")
        with open(args.infile, 'w') as outf:
            outf.write(normed)
