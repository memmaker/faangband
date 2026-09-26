#!/bin/sh
# Upload web/dist to https://ruzzoli.de/roguelikes/faangband/
# RVIP step 9: deploy only from committed and pushed trees.
set -e
cd "$(dirname "$0")"
if [ -n "$(git status --porcelain)" ]; then echo "deploy: working tree not clean, commit first" >&2; exit 1; fi
git fetch -q memmaker
if [ -z "$(git branch -r --contains HEAD)" ]; then echo "deploy: HEAD is not pushed" >&2; exit 1; fi
[ -f dist/faangband-core.wasm ] || { echo "deploy: build first (sh web/build.sh)" >&2; exit 1; }
ssh ruzzoli.de 'sudo mkdir -p /var/www/ruzzoli.de/roguelikes/faangband && sudo chown -R felix:www-data /var/www/ruzzoli.de/roguelikes/faangband'
rsync -rtz --delete dist/ ruzzoli.de:/var/www/ruzzoli.de/roguelikes/faangband/
curl -sI https://ruzzoli.de/roguelikes/faangband/ | head -1
