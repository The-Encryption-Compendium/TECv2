#!/bin/bash

###
### Generate files with Hugo and commit them to the
### gh-pages branch.
###

BASE_DIR="$(dirname $0)/.."

cd "${BASE_DIR}"

hugo
cd public \
&& git add --all \
&& git commit -m "Publishing to gh-pages" \
&& cd ..
