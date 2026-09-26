#!/bin/sh
# Mac (maintainer's machine, 2026-09-26): Homebrew only, no emsdk
#   brew install emscripten webp        # emcc 6.0.10 on PATH, cwebp
#   shared page code: ~/Games/rvip-tools/web/rvip-wm.js (copied by web/build.sh)
#   help: web/make-help.py reads the Docs entry faangband.html from
#   ~/Desktop/Games/Roguelikes/Docs (build-docs.py + guides.py)
#   sh web/build.sh && sh web/deploy.sh
#
# Toolchain used for the FAangband web port in the Claude Code cloud session
# (Ubuntu 24.04 container, 2026-09-26).  Every command that was run, in order.
set -e

# Emscripten (worked first try: emcc 6.0.10, d6c521a7f05449857c76bd99e396895583cf2083)
cd /home/user && git clone https://github.com/emscripten-core/emsdk
cd emsdk && ./emsdk install latest && ./emsdk activate latest
. /home/user/emsdk/emsdk_env.sh   # web/build.sh finds emcc there by itself

# Lossless WebP for the Shockbolt sheet (web/build.sh)
apt-get install -y webp binaryen   # binaryen from apt (resumed run), not npm wasm-opt

# Native ASan build (curses) + pty driver: gcc 13, libncurses-dev (preinstalled),
# pyte for reading the screen
python3 -m venv /home/user/venv && /home/user/venv/bin/pip install pyte pillow

# Browser tests: Playwright (Chromium preinstalled under /opt/pw-browsers)
cd "$(dirname "$0")" && npm install --no-save playwright
