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

(nothing yet — start with stage 1)
