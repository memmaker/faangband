# FAangband: handover

Web port, all RVIP stages 1–9 done (procedure: `~/Games/rvip-tools/RVIP.md`,
case A, Angband 4.2 family like Tactical Angband).
Public repo **memmaker/faangband** (remote `memmaker`, branch `main`);
upstream NickMcConnell/FAangband (remote `upstream`) @ `0d85203`, README has
the compare view. The import started in a cloud session (private
`memmaker/faangband-cloud`, deleted 2026-09-27; its `rvip/` bundle is gone).
Live: https://ruzzoli.de/roguelikes/faangband/ · shrine
https://ruzzoli.de/roguelikes/shrine/faangband.html

## The game
- FAangband **2.0.1** (Nick McConnell; 0.1.0 = 28 Nov 2005 from Oangband
  0.7.0; 2.0 (2021) rebuilt on Angband 4.2). Licence GPL 2 or Angband
  licence (`docs/copying.rst`).
- Birth starts with a world menu (a Standard Wilderness, b Extended, c Hybrid
  Dungeon, d Angband Dungeon); the town is part of the wilderness.
- Native builds: `.github/workflows/release.yml` (Linux/macOS curses, Windows).

## Build, test, deploy
- `sh web/build.sh` → `web/dist` (~1.5 min; `web/toolchain.sh`): sources =
  `ANGFILES`/`ZFILES` of `src/Makefile.src` + `main.c main-web.c`, `-DUSE_WEB`,
  Asyncify, IDBFS; preload `lib/{gamedata,customize,help,screens,ghost}` +
  tile prefs as `/faangband/lib`; `tiles.webp` from
  `lib/tiles/shockbolt/64x64.png` by `cwebp -lossless` (gitignored, rebuilt
  when missing). Page `web/index.html` + `web/faangband.js`, loads shared
  `../rvip-wm.js` and `../rvip-app.js`.
- `sh web/deploy.sh` (guard: clean tree, pushed HEAD, fetches `memmaker`).
- Tests: Playwright `web/test/*.mjs` (`lib.mjs` text shadow of every term,
  `birth.mjs`, `stage1..6.mjs`). ASan: native curses build of the same
  sources (`-DUSE_GCU -DUSE_NCURSES -fsanitize=address`), pty + pyte driver,
  isolated HOME, `-d<dir>=` before `-u`.

## File map (port code)
- `src/main-web.c` (Tactical Angband's, `Module.fa`), registered first in
  `modules[]` (`src/main.c`). `USE_WEB` edits: `config.h` no
  `PRIVATE_USER_PATH` (saves in `lib/save|user|scores|panic|bone`, IDBFS),
  `savefile.c` `web_sync_files()`, `list-options.h` `WEB_ON` for
  `autoexplore_commands`, `center_player`, `auto_more`; `src/main.c` does not
  chain `extended_quit_hook` (`hook_quit()` → `Module.fa.quit`).
- Terms (page `TERMS`): main, Messages, Inventory, Visible monsters, Visible
  items, Recall, Equipment (`default_window_flag[]` term 6 = `PW_EQUIP` under
  `USE_WEB`; savefiles keep their own flags).
- Explore `p` (4.2 `CMD_EXPLORE`), `<`/`>` = `do_cmd_navigate_up/down()`:
  `src/cmd-cave.c`, `src/player-path.c` (goal state, per-level skip list for
  targets that add no known grid, locked doors skipped); arrival hook at the
  end of `run_step()` → `path_arrived()`.
- Enter menu: 4.2's `cmd_menu()` (`src/ui-context.c`, `cmds_all[]` in
  `src/ui-game.c`), "Hidden" regrouped, renamed "Wizard and debug".
  Inventory browser: `item_menu_browse` in `src/ui-object.c`, actions via
  `context_menu_object_act/browse/main()` (`src/ui-context.c`), reopen hook
  at the top of `textui_process_command()`.
- Tiles: Shockbolt Dark (`lib/tiles/shockbolt`, GraphicsID 5), toggle
  Shockbolt/none (`web_set_tiles`). Upstream prefs cover 92.7%; same-set
  stand-ins from `web/mkgraf-standins.py` (marked block at the end of both
  `graf-shb-*.prf`, idempotent) → 1316/1316 (`web/tile-coverage.py`). Trees
  get the grass tile as background (`grid_data_as_text()`, `src/ui-map.c`).
- Sound: the game's own Dubtrain mp3s in `lib/sounds`,
  `lib/customize/sound.prf` (added BIRTH, BR_ICE, BR_STORM, BR_DRAGONFIRE,
  BR_HELLFIRE, SCRAMBLE; WALK silent), read from the preload with
  `FS.readFile`; build copies only the named mp3s. Music
  `web/music/new_town.ogg`.
- Help: `web/make-help.py` reads the Docs entry `faangband.html`
  (`~/Desktop/Games/Roguelikes/Docs`).
- Beacon: `src/score.c enter_score()` → `web_run_end(p, total_points(p))`
  (death, retire = `ev=quit`, winner = `ev=win`; also debug runs). Killer art:
  roguelikes-index `killers/make.py tactical('faangband')`.

## Open
- Explore in the wilderness is nearly useless (monsters always in view); a
  level whose rest lies behind locked doors ends in "Nothing left to
  explore."; objects in the path stop every walk (upstream `run_step()`).
- A stair walk that must cross a known trap in a one-wide corridor does
  nothing and prints nothing.
- Not done: ASan run of the stage 3–5 changes, tile census of deep levels,
  live test of the win beacon.
- Browser pane: the birth name prompt dropped typed letters (name stayed
  PLAYER).
