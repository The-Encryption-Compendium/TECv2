#!/usr/bin/env python3
"""
Script to pull data from Zotero
"""

import requests
from time import sleep
import os
import argparse


"""
Global variables
"""

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
BIB_FILE = os.path.relpath(os.path.join(BASE_DIR, "data", "data.bib"), os.getcwd())


class FetchUpdates:
    """
    Fetch all articles from Zotero
    """

    def __init__(self, key):
        """
        Sets url paramaters and headers
        """
        self.url = "https://api.zotero.org/groups/2433843/items?sort=dateModified&format=bibtex"
        self.params = {"sort": "dateModified", "format": "bibtex"}
        self.headers = {"Authorization": "Bearer " + key}
        self.next = True

    def get_total_entries(self):
        """
        Return total number of entries in the Zotero library
        """
        self.r = requests.get(self.url, headers=self.headers)
        return self.r.headers["Total-Results"]

    def _get_results(self, url):
        """
        Fetches results from Zotero in bibtex format
        """
        r = requests.get(url, headers=self.headers)
        print(r.status_code)
        if "next" in r.links:
            self.url = r.links["next"]["url"]
        else:
            self.next = False
        return r.text

    def update_database(self, file):
        """
        Zotero limits maximum number of results in one API call.
        This function recurcively calls the helper function to fetch all results
        and writes it to the file passed to it.

        Arguments
        =========
        file: Bibtex file to update
        """
        with open(file, "w") as f:
            while self.next:
                f.write(self._get_results(self.url))
                sleep(1)


"""
Argument parser
"""

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "api_key", help="API key to access zotero group library",
)

if __name__ == "__main__":
    args = parser.parse_args()
    updates = FetchUpdates(args.api_key)
    updates.update_database(BIB_FILE)
