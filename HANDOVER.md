# FAangband: handover

## Cloud experiment (read this first)

This repo runs the RVIP import in a Claude Code **cloud** session. Everything
the procedure normally takes from sibling folders on the maintainer's Mac is
bundled under `rvip/`:

- `rvip/RVIP.md` — the procedure (snapshot; the canonical copy lives on the
  Mac). **Write lessons into `rvip/LESSONS.md`** (new file, one bullet per
  lesson naming the RVIP section it belongs to); never edit `rvip/RVIP.md`.
- `rvip/web/rvip-wm.js`, `rvip/web/rvip-sound.js` — shared page code every
  game loads (window manager, sound). Use, don't fork.
- `rvip/templates/tactical-angband/` — the **Angband 4.2** web port
  (Tactical Angband, RVIP section A-4.2): `main-web.c` (z-term frontend for
  the 4.2 code base, `#ifdef USE_WEB`), `web/build.sh` (emcc + Asyncify +
  IDBFS, converts the Shockbolt sheet to `tiles.webp`), `web/tactical.js` +
  `web/index.html` (page with rvip-wm.js windows, tiles blit, sound),
  `web/make-help.py`, `HANDOVER.md`, `README.md`. FAangband is 4.2-based
  too, so this template is the closest fit: copy its solutions.
- `rvip/templates/zangband/` — `HANDOVER.md` (all nine stage sections of the
  newest complete import, for the stage checklists), `web/sounds.py` (edit
  `PACK` to `rvip/templates/dubtrain`), `web/tile-coverage.py` (adapt to
  4.2's `lib/gamedata/*.txt` and `lib/tiles/*/graf-*.prf`).
- `rvip/templates/dubtrain/` — the Dubtrain Angband Sound Pack for stage 6.

**The game.** FAangband (First Age Angband) by Nick McConnell,
github.com/NickMcConnell/FAangband, upstream history in this repo (remote
`upstream`), HEAD = 2.0.1 + ~1090 commits on `master` (check
`src/buildid.h`/`VERSION_STRING` and the newest tag; pick HEAD unless it
doesn't build). Angband 4.2 code base (`src/main-*.c`, `lib/gamedata`,
`lib/tiles/{adam-bolt,gervais,nomad,old,shockbolt}`). Case **A**, section
**A-4.2** of RVIP.md is the worked example; read A-Zangband / A-FrogComposband
/ A-Hengband for the newest stage notes and Part W.

**Tiles:** FAangband ships its own tile sets in `lib/tiles/`. Count coverage
of the Shockbolt set (64x64, `lib/tiles/shockbolt/graf-*.prf`) against every
monster/object/terrain/trap/flavour entry of `lib/gamedata/*.txt`; ≥95% →
Shockbolt as the game ships it (it is 4.2's own set, so gaps are FAangband
additions: same-set stand-ins); report the numbers. One set, never mix.

**Differences from a local run**
- No browser pane and no ruzzoli.de deploy key. Stages 1–6 are in scope.
  Tests: Playwright/Chromium (preinstalled under `/opt/pw-browsers` in the
  cloud image, else `npx playwright install chromium`) driving `web/dist`
  served by `python3 -m http.server`: character creation, random keys,
  save/reload/restore, explore, stairs, menus, tiles (read canvas pixels),
  screenshots into `web/shots/`. Write `web/deploy.sh` like the template's
  (target `ruzzoli.de/roguelikes/faangband/`); never run it.
- Toolchain: Emscripten (`git clone https://github.com/emscripten-core/emsdk
  && ./emsdk install latest && ./emsdk activate latest`, ~2 min), gcc/clang
  for the native ASan build (`-DUSE_GCU` curses + pty + random keys, isolated
  `HOME`; `pyte` in a venv for reading screens). Record every command in
  `web/toolchain.sh`. If Emscripten cannot be installed, write that file with
  what you tried and the errors, commit, push, stop.
- Commit after every stage (`RVIP: stage N <topic>`) and **push to `origin`**
  (github.com/memmaker/faangband, private). Every commit message ends with
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Never force-push.
- Never `fetch()` `.cfg`/`.prf` files from the page: stage them into the
  preload and read them with `Module.FS.readFile` (the template's
  `loadSoundCfg()` pattern).
- The Docs page (stage 6) is not here: write `docs/web/faangband-docs.html`
  in the shape of the template's `make-help.py` output and note it for the
  Mac side.

## RVIP progress

### Stage 1 (get + build): done 2026-09-26 (cloud)
- Base: FAangband **2.0.1** (`VERSION_STRING`, `src/Makefile.src`), upstream
  NickMcConnell/FAangband `master` @ `0d85203` ("Forget when in remembered
  impassable terrain with no light"; no tags in this clone). **Case A**, A-4.2.
- Web frontend: `src/main-web.c` = Tactical Angband's, renamed (`Module.fa`,
  `js_beacon` g=`faangband`, not hooked yet). Registered as `"web"` first in
  `modules[]` (`src/main.c`, `#ifdef USE_WEB`; 4.2 `init_web(argc, argv)`
  has the right signature), prototypes in `src/main.h`.
- Port edits (`USE_WEB`): `config.h` no `PRIVATE_USER_PATH` (saves in
  `lib/save|user|scores|panic|bone`, all IDBFS mounts); `savefile.c`
  `web_sync_files()` after a successful `savefile_save()`; `list-options.h`
  `WEB_ON` = true in the web build for `autoexplore_commands`,
  `center_player`, `auto_more` (3d: birth has no `-more-`).
- Page: `web/index.html`, `web/faangband.js` (template's `tactical.js`;
  ROOT `/faangband`, save `-uPLAYER` → `lib/save/PLAYER`), shared
  `rvip/web/rvip-wm.js` copied by the build. 7 terms: main, Messages,
  Inventory, Visible monsters, Visible items, Recall, Equipment (4.2
  default subwindow flags; stage 5 checks them).
- Build: `sh web/build.sh` → `web/dist` (~1.5 min): sources = `ANGFILES`/
  `ZFILES` of `src/Makefile.src` + `main.c main-web.c`, `emcc -O2 -std=gnu99
  -DUSE_WEB -DHAVE_MKSTEMP -w -sASYNCIFY -sASYNCIFY_STACK_SIZE=131072
  -sSTACK_SIZE=2097152 -sALLOW_MEMORY_GROWTH -sINITIAL_MEMORY=128MB
  -sFORCE_FILESYSTEM -lidbfs.js -sENVIRONMENT=web`, preload
  `lib/{gamedata,customize,help,screens,ghost}` + `lib/tiles/list.txt` +
  shockbolt prefs as `/faangband/lib`; `tiles.webp` from
  `lib/tiles/shockbolt/64x64.png` by `cwebp -lossless` (13 MB, gitignored,
  rebuilt when missing). No wasm-ld warnings, no function-pointer casts
  (`-Wcast-function-type-strict` over all sources: none).
- Toolchain: `web/toolchain.sh` (emsdk latest = emcc 6.0.10 in
  `/home/user/emsdk`, `apt-get install webp`, venv `/home/user/venv` with
  pyte + pillow, `npm install --no-save playwright` in `web/`).
- Tests (Playwright, Chromium `/opt/pw-browsers/chromium-1194`, `web/test/`):
  `lib.mjs` (http.server on 127.0.0.1, text shadow of every term by wrapping
  `Module.fa.text/wipe/clear/pict`, tile counter), `birth.mjs` (splash Enter,
  `a` Standard Wilderness, Enter × 7 = Easterling Warrior, point-based
  defaults, name PLAYER), `stage1.mjs <seed> <n>`: birth → n random keys →
  ^S "Saving game... done." → reload → Enter → character restored. Seeds
  1–4 (200–800 keys): no page errors; only 404s are `sounds/sound.prf` and
  `music/new_town.ogg` (stage 6). Screenshots `web/shots/`.
- ASan: native curses build of the same sources (`-DUSE_GCU -DUSE_NCURSES
  -fsanitize=address`, objects in the scratchpad), pty + pyte driver
  (isolated HOME, `-d<dir>=` before `-u`, random keys without ^C ^Z ^\\ ^Y Q),
  4 seeds × (2500 keys new + ^S ^X + 1500 keys restored). One upstream bug,
  fixed in `port:` commit `70d590f`: `main-gcu.c` `Term_text_gcu()` indexed
  `colortable[a & 127]` (30 entries) with attrs from the knowledge menus'
  visual editor. Then clean.
- **Tiles: Shockbolt Dark** (the game's own `lib/tiles/shockbolt`, 64x64).
  Coverage by `web/tile-coverage.py` (4.2 name prefs vs `lib/gamedata`):
  Shockbolt Dark **1220/1316 = 92.7%** (monsters 588/624, objects 331/362,
  terrain 26/40, traps 38/53, flavours 237/237); Light 92.9%, Gervais 91.6%,
  Adam Bolt 91.6%. Below 95%, but every set has the same FAangband gaps and
  Shockbolt is the best and the RVIP default: stage 4 adds same-set stand-ins
  for the 96 misses (wilderness paths, trees, water, sand dune, secret door,
  travelling merchant; material rings/amulets; new monsters and traps).
- Quirks: birth starts with a world menu (a Standard Wilderness, b Extended,
  c Hybrid Dungeon, d Angband Dungeon); the town is part of the wilderness
  ("Hard path south" edges). The template page `fetch()`es
  `sounds/sound.prf` (against the rule: stage 6 moves it into the preload).
- Open problems: no browser pane here, only headless Chromium screenshots;
  shops 1–9 show text numbers where Shockbolt has no FAangband shop, `>` is
  text in town (stage 4).

### Next: stage 2 (explore + stairs)
- 4.2 already has explore (`autoexplore_commands`, on in the web build) and
  stair pathing: `grep -n explore src/player-path.c src/cmd-cave.c
  src/ui-game.c`; apply the A-4.2 fixes (arrival in `run_step()`, continue
  explore via `cmdq_push(CMD_EXPLORE)`, `messages_added` stop, doors).
- Test with Playwright: `web/test/birth.mjs` + keys; the Standard
  Wilderness town has one staircase down (`>` at the top left).
