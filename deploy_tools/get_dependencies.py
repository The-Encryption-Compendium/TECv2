#!/usr/bin/env python

"""
Install all of the third-party dependencies for the website to their respective directories
"""

import aiofiles
import aiohttp
import asyncio
import hashlib
import json
import logging, logging.handlers
import os
import re
import shutil
import sys
import tarfile
import traceback
import zipfile

from typing import List, Optional
from urllib.parse import urlparse

"""
Logging configuration
"""

formatter = logging.Formatter(
    "[%(asctime)-15s] [%(filename)s#%(lineno)d] (%(levelname)s) %(message)s"
)

stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(formatter)
stdout_handler.setLevel(logging.INFO)

file_handler = logging.handlers.RotatingFileHandler(
    "build.log", maxBytes=2 ** 20, backupCount=3
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger = logging.Logger("get_dependencies")
logger.addHandler(stdout_handler)
logger.addHandler(file_handler)

"""
Helper functions
"""

# Get the path to a file or directory relative to the current working directory
relpath = lambda path: os.path.relpath(path, os.getcwd())

"""
Global variables
"""

BASE_DIR = relpath(os.path.join(os.path.dirname(__file__), os.pardir))

# Directories where Javascript, CSS, and font files are stored respectively
VENDOR_JS_DIR = relpath(os.path.join(BASE_DIR, "assets", "js", "vendor"))
VENDOR_CSS_DIR = relpath(os.path.join(BASE_DIR, "static", "css"))
VENDOR_FONTS_DIR = relpath(os.path.join(BASE_DIR, "static", "fonts"))

# Directory to store licenses
LICENSE_DIR = relpath(os.path.join(BASE_DIR, "public", "misc", "LICENSE"))

# JSON file from which to read the dependency configuration
DEPENDENCIES_FILE = relpath(os.path.join(BASE_DIR, "deploy_tools", "dependencies.json"))

# Buffer size to use while reading files to compute their checksums
BUFFER_SIZE = 2 ** 24  # ~4Mb

# Asyncio semaphore to limit the amount of concurrent I/O
AIO_LOCK = asyncio.Semaphore(10)

# Directory where dependencies are cached
CACHE_DIR = os.path.join(BASE_DIR, "deploy_tools", "_cache")

# Whether or not checksums must be defined for all dependencies. If we
# try to install a dependency without a checksum, we error out.
REQUIRE_CHECKSUM = False


"""
Pattern matching
"""

VERSION_PATT = re.compile(r"\{\{\s*version\s*\}\}")
SHA256_PATT = re.compile(r"[0-9a-f]{64}", re.IGNORECASE)

SAVE_DIRS = [
    (VENDOR_JS_DIR, re.compile(r".*\.js$")),
    (VENDOR_CSS_DIR, re.compile(r".*\.css$")),
    (VENDOR_FONTS_DIR, re.compile(r".*\.ttf$")),
]


"""
Functions
"""


async def download_dependency(dep):
    """
    Downloads all of the files for a dependency to the cache directory. Return
    the directory to which the files were saved.
    """

    name = dep["name"]
    url = dep["url"]
    files = dep.get("files", [])
    checksum = dep.get("checksum")
    version = dep.get("version")

    # Replace occurrences of the string {{ version }} in the URL and files
    if version:
        url = VERSION_PATT.sub(version, url)
        files = [VERSION_PATT.sub(version, f) for f in files]
        dep["files"] = files
    elif not version and VERSION_PATT.search(url):
        logger.warn(
            f"{{{{ version }}}} found in URL {url}, but no version number was provided"
        )
    elif not version:
        for f in [f for f in files if VERSION_PATT.search(f)]:
            logger.warn(
                f"{{{{ version }}}} found in file name {f}, but no version number was provided"
            )

    try:
        # Ensure that the checksum is valid
        if checksum and not SHA256_PATT.match(checksum):
            logger.error(f"Invalid SHA-256 checksum received for {name} ({checksum})")
            raise Exception(f"Invalid SHA-256 checksum for {name}")

        if not checksum and REQUIRE_CHECKSUM:
            raise Exception(
                f"No checksum provided for {name}, and REQUIRE_CHECKSUM = True"
            )

        logger.info(f"Installing {name} from {url}")
        outpath = await _download(url, name, checksum=checksum)

        # If the file is a zip file or tar archive, we should extract it
        extraction_dir = os.path.join(
            CACHE_DIR, f"extracted_{os.path.basename(outpath)}"
        )
        is_zipfile, is_tarfile = (
            zipfile.is_zipfile(outpath),
            tarfile.is_tarfile(outpath),
        )

        outdir = (
            extraction_dir if (is_zipfile or is_tarfile) else os.path.dirname(outpath)
        )
        if is_zipfile:
            with zipfile.ZipFile(outpath, "r") as zip_ref:
                zip_ref.extractall(outdir)
        elif is_tarfile:
            with tarfile.open(outpath, "r") as tar_ref:
                tar_ref.extractall(path=outdir)

        # Ensure files that were specified in the dependencies exist and are
        # of a recognized file type
        # file exist.
        for path in files:
            full_path = os.path.join(outdir, path)
            if not os.path.exists(full_path):
                raise Exception(
                    f"Could not find file {path} (full path: {full_path}) for {name}"
                )
            if not os.path.isfile(full_path):
                raise Exception(
                    f"{path} (full path: {full_path}) for {name} is a directory, not a file"
                )

            # Will throw an exception if the file type is not recognized
            get_move_path(full_path)

        return outdir

    except Exception as ex:
        logger.error(f"Error occurred while trying to download {name}: {str(ex)}")
        logger.debug(f"{traceback.format_exc()}")
        raise ex


async def _download(url: str, name: str, checksum: Optional[str] = None):
    """
    Download a file from a URL and store it in _cache/{name}
    """
    url = urlparse(url)
    outdir = os.path.join(CACHE_DIR, name)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    outfile = os.path.basename(url.path)
    outfile = relpath(os.path.join(outdir, outfile))
    sha = hashlib.sha256()

    async with aiohttp.ClientSession() as sess:
        async with aiofiles.open(outfile, mode="wb") as f:
            async with sess.get(url.geturl()) as response:
                while True:
                    async with AIO_LOCK:
                        chunk = await response.content.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        if checksum:
                            sha.update(chunk)
                        await f.write(chunk)

    logger.info(f"Saved files for {name} to {outfile}")
    if checksum:
        sha = sha.hexdigest()
        checksum = checksum.lower()
        if sha == checksum:
            logger.info(f"Checksum for {outfile} OK")
        else:
            logging.error(f"Checksum for {name} did not match ({sha} != {checksum})")
            raise Exception(f"Checksum for {name} did not match")

    return outfile


def get_move_path(path: str):
    """
    Given a saved file for a dependency, find the path where that file should be
    moved to.
    """

    for (save_dir, patt) in SAVE_DIRS:
        if patt.match(path):
            return os.path.join(save_dir, os.path.basename(path))

    raise Exception(f"File type for {path} was not recognized")


def move_dependency_files(
    name: str, outdir: str, files: List[str], licenses: List[str] = []
):
    """
    Move all of the files for a dependency into its required directory within
    the repository.
    """

    license_save_dir = os.path.join(LICENSE_DIR, name)
    if len(licenses) > 0 and not os.path.exists(license_save_dir):
        os.makedirs(license_save_dir)

    # Move each file out of the cache directory and into the main repository
    files = [os.path.join(outdir, f) for f in files]
    licenses = [os.path.join(outdir, l) for l in licenses]
    paths = [get_move_path(f) for f in files]
    paths += [os.path.join(license_save_dir, os.path.basename(l)) for l in licenses]

    for (path_orig, path_new) in zip(files + licenses, paths):
        logger.info(f"Saving {path_orig} to {path_new}")
        shutil.move(path_orig, path_new)


"""
Main script
"""


def _clean_cache():
    """
    Remove all cached files
    """
    logger.info(f"Cleaning up cached files in {CACHE_DIR}")
    shutil.rmtree(CACHE_DIR)


async def main(clean_cache: bool = True):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    if not os.path.exists(LICENSE_DIR):
        os.makedirs(LICENSE_DIR)

    try:
        with open(DEPENDENCIES_FILE, "r") as f:
            deps = json.load(f)

        # First, download the files for each dependency
        jobs = [download_dependency(dep) for dep in deps]
        outdirs = await asyncio.gather(*jobs)

        # Once we've reached this point, we know that all of the
        # files exist, so we can move them to their appropriate
        # locations.
        for (outdir, dep) in zip(outdirs, deps):
            move_dependency_files(
                dep["name"],
                outdir,
                dep.get("files", []),
                licenses=dep.get("license", []),
            )

    except Exception as ex:
        logger.critical(f"Fatal error processing dependencies: {ex}")
        logger.debug(f"{traceback.format_exc()}")
        raise ex

    finally:
        if clean_cache:
            _clean_cache()


if __name__ == "__main__":
    asyncio.run(main())
