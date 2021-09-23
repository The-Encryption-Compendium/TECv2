#!/usr/bin/env python3
"""
Script to pull data from Zotero
"""

from time import sleep
import os
import argparse
import requests


## Global variables

BASE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
BIB_FILE = os.path.relpath(os.path.join(BASE_DIR, "data", "data.bib"), os.getcwd())

class FetchUpdates:
    """
    Fetch all articles from Zotero
    """

    def __init__(self, key: str) -> None:
        """
        Sets url paramaters and headers
        """
        self.url = "https://api.zotero.org/groups/2433843/items?sort=dateModified&format=bibtex"
        self.params = {"sort": "dateModified", "format": "bibtex"}
        self.headers = {"Authorization": "Bearer " + key}
        self.next = True

    def get_total_entries(self) -> str:
        """
        Return total number of entries in the Zotero library
        """
        response = requests.get(self.url, headers=self.headers)
        return response.headers["Total-Results"]

    def _get_results(self, url: str) -> str:
        """
        Fetches results from Zotero in bibtex format
        """
        response = requests.get(url, headers=self.headers)
        print(response.status_code)
        if "next" in response.links:
            self.url = response.links["next"]["url"]
        else:
            self.next = False
        return response.text

    def update_database(self, file: str) -> None:
        """
        Zotero limits maximum number of results in one API call.
        This function recurcively calls the helper function to fetch all results
        and writes it to the file passed to it.

        Arguments
        =========
        file: Bibtex file to update
        """
        with open(file, "w") as outf:
            while self.next:
                outf.write(self._get_results(self.url))
                sleep(1)


## Argument parser

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "api_key", help="API key to access zotero group library",
)

if __name__ == "__main__":
    args = parser.parse_args()
    updates = FetchUpdates(args.api_key)
    updates.update_database(BIB_FILE)
