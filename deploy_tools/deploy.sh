#!/bin/sh

hugo --minify \
&& rsync -avz --delete public/ ec_4593@encryptioncompendium.org:encryptioncompendium.org/
