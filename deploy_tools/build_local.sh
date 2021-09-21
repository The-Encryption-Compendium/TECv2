#!/bin/bash

###
### Build the site locally for testing purposes
###

CURRENT_DIR=$(dirname "$0")
VENV_DIR="${CURRENT_DIR}/venv"

# Download compendium entries locally
wget https://raw.githubusercontent.com/The-Encryption-Compendium/the-encryption-compendium.github.io/main/data/data.bib \
    -O "${CURRENT_DIR}/../data/data.bib"

"${CURRENT_DIR}/normalize_unicode.py" "${CURRENT_DIR}/../data/data.bib"

# Download dependencies
python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
python3 -m pip install -r "${CURRENT_DIR}/requirements.txt"

# Generate compendium entry files from data.bib
python3 "${CURRENT_DIR}/generate_compendium.py" "${CURRENT_DIR}/../data/data.bib"

# Generate HTML and CSS files with Hugo
cd "${CURRENT_DIR}/.."
hugo
