#!/bin/sh
# Build FAangband for the browser (Emscripten + Asyncify).
# Output goes to web/dist; deploy with web/deploy.sh.  Run with sh, not zsh.
# Toolchain: web/toolchain.sh (emsdk, cwebp).
set -e
cd "$(dirname "$0")/.."
command -v emcc >/dev/null || PATH="${EMSDK:-/home/user/emsdk}/upstream/emscripten:$PATH"  # Mac: Homebrew emcc
OUT=web/dist
rm -rf "$OUT" web/stage && mkdir -p "$OUT" web/stage/lib/tiles/shockbolt

# Game data (lib/user, save, scores, panic are IndexedDB mounts made by the page)
for d in gamedata customize help screens ghost; do cp -R lib/$d web/stage/lib/; done
cp lib/tiles/list.txt web/stage/lib/tiles/
cp lib/tiles/shockbolt/*.prf web/stage/lib/tiles/shockbolt/
find web/stage -name Makefile -delete

SRCS=$(tr -d '\r' < src/Makefile.src | sed -n '/^ANGFILES/,/^$/p;/^ZFILES/,/^$/p' \
	| grep -o '[A-Za-z0-9_/.-]*\.o' | grep -v '^borg/' | sed 's/\.o$/.c/;s|^|src/|' | sort -u)

emcc -O2 -std=gnu99 -DUSE_WEB -DHAVE_MKSTEMP -Isrc -w \
	$SRCS src/main.c src/main-web.c \
	-o "$OUT/faangband-core.js" \
	-sASYNCIFY -sASYNCIFY_STACK_SIZE=131072 -sSTACK_SIZE=2097152 \
	-sALLOW_MEMORY_GROWTH -sINITIAL_MEMORY=128MB \
	-sEXPORTED_FUNCTIONS=_main,_web_request_save \
	-sEXPORTED_RUNTIME_METHODS=FS,IDBFS,HEAP32,addRunDependency,removeRunDependency \
	-sFORCE_FILESYSTEM -lidbfs.js -sENVIRONMENT=web \
	--preload-file web/stage/lib@/faangband/lib

cp web/index.html "$HOME/Games/rvip-tools/web/rvip-wm.js" web/faangband.js "$OUT/"
# Shockbolt tiles, lossless WebP (the PNG is 18 MB); drawn nearest-neighbour
[ web/tiles.webp -nt lib/tiles/shockbolt/64x64.png ] || \
	cwebp -quiet -lossless -z 9 -exact lib/tiles/shockbolt/64x64.png -o web/tiles.webp
cp web/tiles.webp "$OUT/"
# Sound effects (Dubtrain mp3 from lib/sounds, only those sound.prf names;
# sound.prf itself is in the preload) and town music, both fetched on demand
mkdir -p "$OUT/sounds" "$OUT/music"
for f in $(sed -n 's/^sound:[A-Z_0-9]*://p' lib/customize/sound.prf | tr ' ' '\n' | sort -u); do
	cp "lib/sounds/$f.mp3" "$OUT/sounds/"
done
cp web/music/new_town.ogg "$OUT/music/"
python3 web/make-help.py > "$OUT/help.html"
rm -rf web/stage
ls -la "$OUT"
