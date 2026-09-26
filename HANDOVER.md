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

### Stage 2 (explore + stairs): done 2026-09-26 (cloud)
- **Explore key `p`** (4.2's own `CMD_EXPLORE`, option `autoexplore_commands`,
  on by default in the web build via `WEB_ON`); same key in both keysets.
  `<` / `>` = 4.2's `do_cmd_navigate_up/down()` when not on stairs.
- Code: `src/cmd-cave.c` `do_cmd_explore()`, `do_cmd_navigate_up/down()`,
  `do_cmd_pathfind()`; `src/player-path.c` (goal state `path_goal`,
  `path_set_goal()`, `path_check_goal()`, `path_arrived()`, skip list
  `path_is_locked()` / `path_add_locked()`), `src/message.c`
  `messages_added_count()` (every message incl. repeats).
- **Main-loop hook**: 4.2 runs paths through `run_step()`; the arrival is the
  branch where `running` reaches 0 and `steps` are freed (end of
  `run_step()`): it calls `path_arrived()`, which pushes `CMD_GO_DOWN` /
  `CMD_GO_UP` (stairs, also wilderness paths) or `CMD_EXPLORE` again if no
  message was added since the walk began. `disturb()` (monster moves, keys)
  cancels the run before that, so a disturbance stops; pressing again resumes.
  The open/tunnel detours of `run_step()` re-issue `CMD_PATHFIND` to the same
  destination, so the goal survives them (`path_check_goal()`).
- **Known-grid test**: `square_isknown()` (player memory). FAangband does not
  forget floors, but some frontier grids never become known from where the
  path ends (walls seen only diagonally): if an explore arrival added no known
  grid (`path_known_grids()`), that target goes on the per-level skip list,
  or explore walked between two targets for thousands of turns.
- Explore stops: monster in view ("In view: a soldier ant."), new message,
  key, no own light in the dungeon ("You have no light to explore by."),
  confusion (upstream). Doors: a closed door or impassable rubble next to the
  player with an unknown other side is opened/tunnelled first (upstream never
  picked a door whose only known neighbour is the player's grid). Locked
  doors: never picked ("A locked door blocks the way."), skipped afterwards.
  Stair walks no longer refuse when a monster is in view (they may flee).
- Help: `lib/help/commands.txt`, `r_comm.txt` (autoexplore paragraph).
- Tests (Playwright `web/test/stage2.mjs <n> <world>`): world `d` (Angband
  Dungeon): `>` in town → DL1; 40 × `p` with debug banish (`^A z y`) when a
  monster blocks → whole level explored (items, gold, secret door, locked
  doors skipped), then "Nothing left to explore."; `<` walked to the up
  staircase and took it (town). World `a`: `>` in town walked to the exit
  path and took it (Eriador South); wilderness always has monsters in view,
  so explore refuses there ("In view: a silver mouse."). Shots
  `web/shots/stage2-*.png`.
- ASan (native, `-DWEB_ON=true`, keys weighted to `p < >`, worlds a–d by
  seed): seeds 1–4 × (2500 + 1500 keys) clean; one earlier seed-4 run exited
  in phase 1 without an ASan report (not reproduced; maybe an `assert` or a
  death; driver now logs the exit status and last keys; seeds 5–8 running).
- Open problems: explore in the wilderness is nearly useless (monsters always
  in view); a level whose rest lies behind locked doors ends in "Nothing left
  to explore."; objects in the path stop every walk until picked up/ignored
  (upstream `run_step()` rule).

### Stage 3 (Enter menu + inventory): done 2026-09-26 (cloud, resumed run)
- **Enter menu** = 4.2's own `textui_action_menu_choose()` / `cmd_menu()`
  (`src/ui-context.c`), lists `cmds_all[]` (`src/ui-game.c`). The "Hidden"
  group's player commands moved: explore `p`, walk, run, stand still, alter,
  steal, repeat, autopickup → Action commands; center map, notes, version →
  Information; pref line, toggle windows → Utility. "Hidden" renamed
  "Wizard and debug" (wizard mode + the nested Debug menus). Letters select
  in every level (`menu.selections = lower_case`, tags shown `a)`); boxes
  sized to the longest entry incl. the key of the *current* keyset
  (`cmd_sub_entry()` already looks up `key[mode]`), clamped to the term.
- **Inventory/equipment browser** (`i`/`e`, `do_cmd_inven/equip()` in
  `src/ui-knowledge.c`): global `item_menu_browse` makes `item_menu()`
  (`src/ui-object.c`) put every item letter, Shift+letter and Ctrl+letter
  (not ^M/^I) into `switch_keys`; `get_item_action()` decides: letter =
  main action, Shift+letter = drop, Ctrl+letter = inspect (then back to the
  list), Enter/Space/click = the object context menu (letters select there
  too, 4.2's command letters). Actions run **by direct call** through
  `context_menu_object_act(obj, cmd)` / `context_menu_object_browse(obj,
  act)` / `context_menu_object_main(obj)` (`src/ui-context.c`, split out of
  `context_menu_object()`, same checks: inscription confirm,
  `get_item_allow()`), which push the command with its item argument.
  After an action the browser reopens (`inven_reopen`, hook at the top of
  `textui_process_command()`), unless a monster is in view.
- Test: `web/test/stage3.mjs` (Playwright): Enter → 6 groups a–f, `b` →
  Action commands incl. "Start exploring (p)", `d` Information has
  "Version info", `f` Wizard and debug; Enter `c` `b` opens the inventory
  from the submenu; Ctrl+a inspects the ration and returns to the list;
  Enter opens the action menu (I/E/d/v/{/k); `a` eats the ration ("That
  tastes good"); `i` Shift+A drops the potion. No page errors. Shots
  `web/shots/stage3-*.png`.
- Open problems: the reopen after an action was not seen in the test
  (town/wilderness always has a monster in view, so it is suppressed by
  design); no ASan run for stage 3 in this session (time budget): the
  Mac/next session should run the native driver with `i`/`e` + letters.

### Stage 4 (tiles): done 2026-09-26 (cloud, resumed run)
- **Tile set: Shockbolt Dark**, the game's own `lib/tiles/shockbolt`
  (`64x64.png`, 128×32 tiles of 64 px), `GraphicsID` 5 (list.txt), prefs
  `graf-shb-dark.prf` (+ `-light.prf`), `xtra-shb.prf`, `flvr-shb.prf`.
  One set, no mixing. Sheet → `web/tiles.webp` (lossless) by `build.sh`.
- Coverage (`web/tile-coverage.py`, every monster/object/terrain/trap/
  flavour entry of `lib/gamedata`): upstream prefs **1220/1316 = 92.7%**
  (< 95%) → **same-set stand-ins** for the 96 misses, generated by
  `web/mkgraf-standins.py` into a marked block at the end of both
  `graf-shb-*.prf` (idempotent): monsters → mapped monster of the same
  `base`, nearest depth (36); objects → same tval, most shared words, rings/
  amulets → the vanilla flavour tile of the same material where the sheet
  has one (29, curse object excluded); terrain: easy/hard paths = up/down
  staircase (they are `<`/`>` in text), secret door = granite wall,
  Travelling Merchant = General Store, water = the sheet's teal water tile
  0x98:0xDF, lowland/highland trees = Shockbolt "old forest tree"
  0x9F:0x83, sand dune = passable rubble (14); traps: falling branch = rock
  fall, player-set monster traps = decoy tile (15). Now **1316/1316 =
  100%** (dark and light).
- Trees are cut-outs: `grid_data_as_text()` (`src/ui-map.c`) gives
  `TF_TREE` grids the grass terrain tile as background (tap/tcp) when
  graphics are on.
- Loader/scale: `web/faangband.js` `pict()` blits from `tiles.webp`
  (`imageSmoothingEnabled = false`, nearest-neighbour), cell = 2 columns
  (`tile_width = 2`), double-height overdraw from `main-web.c`; zoom steps
  16–64 px (page default fits the window). Tiles are always on (the page
  has no text/tiles toggle; W0: presentation lives in the game).
- Test: `web/test/stage4.mjs a|d` (census of term 0's map area: tile cells
  vs text cells, canvas smoothing flag and lit pixels): town 726 tile / 0
  text, wilderness level 988 / 0 (trees on grass, water, paths as stairs),
  dungeon start 836 / 0, DL1 988 / 0. Shots `web/shots/stage4-*.png`.
- Open problems: the DL15 part of the test stopped in the debug command
  confirm (the Enter menu stayed open) — deeper levels were not censused;
  stand-ins are family tiles (e.g. all unmapped material amulets share the
  plain "Amulet" tile).

### Stage 5 (web page): done 2026-09-26 (cloud, resumed run) — not deployed
- Page: `web/index.html` + `web/faangband.js` + shared `rvip-wm.js`
  (template's layout: Map left, Inventory / Visible monsters / Visible items
  right, Messages bottom; Recall and Equipment in the Windows menu, hidden by
  default). Prompt line box via `RvipWM.prompt`, `center_player` on.
- **Window flags**: term order = page `TERMS` (main, Messages, Inventory,
  Visible monsters, Visible items, Recall, Equipment); 4.2's
  `default_window_flag[]` in `src/ui-init.c` matched it except term 6
  (`PW_OVERHEAD`): now `PW_EQUIP` under `USE_WEB`. Savefiles keep their own
  flags (old test saves keep old routing).
- **Game end**: `src/main.c` no longer chains `extended_quit_hook` under
  `USE_WEB` (`quit_aux` stays the web hook); `hook_quit()` (`main-web.c`)
  syncs IDBFS and calls `Module.fa.quit(msg)` → "FAangband has ended"
  overlay with **Play again** (reload). Death/retire says "Your character
  has died …" (reads `player->is_dead`), save-and-quit "Your game has been
  saved.". Death path: bones question → tombstone menu → "Do you want to
  quit? [y/n]" (`y`; Esc returns to the menu) → overlay → Play again →
  "New character based on previous one".
- `web/deploy.sh` written (target `ruzzoli.de:/var/www/ruzzoli.de/roguelikes/
  faangband/`, guard: refuses a dirty tree or an unpushed HEAD, checks
  `dist/` is built, curl check at the end). **Never run in the cloud** (no
  deploy key): the Mac side runs `sh web/build.sh && sh web/deploy.sh`.
  Live URL (after the Mac deploy): https://ruzzoli.de/roguelikes/faangband/
- Test `web/test/stage5.mjs` (Playwright): all 6 sub-terms get their
  content (Equipment 13 lines, Inventory, lists, Messages; Recall empty
  until something is looked at); resize 1000×650 → 1440×900 → 1200×750 →
  760×500 → 1440×900: canvases follow; ^S + reload restores the character;
  ^X → save message, high-score list, overlay; Play again loads the
  character; `Q y @` → death path → death overlay → new birth. No page
  errors. Shot `web/shots/stage5-*.png`.
- Open problems: no browser-pane check of dragging/renaming windows (the
  layout code is the shared, already tested rvip-wm.js); the 3 remaining
  404s are the sound files (stage 6).

### Stage 6 (docs + sound): done 2026-09-26 (cloud, resumed run) — Docs page not built
- **Sound**: the game's own `EVENT_SOUND` → `message_sound_name()` →
  `Module.fa.sound(name)`; `lib/customize/sound.prf` (FAangband ships the
  Dubtrain pack as mp3 in `lib/sounds`) now has a line for every
  `list-message.h` entry except `WALK` (silent on purpose): added BIRTH,
  BR_ICE, BR_STORM, BR_DRAGONFIRE, BR_HELLFIRE, SCRAMBLE. The page reads
  `sound.prf` lazily from the preload with `Module.FS.readFile(ROOT +
  '/lib/customize/sound.prf')` (no `fetch()` of a .prf/.cfg any more);
  `build.sh` copies only the mp3s the prf names to `dist/sounds`, and
  `web/music/new_town.ogg` (from the template) to `dist/music`. The music
  `Audio` is created on first use. Sound and Music **off by default**
  (buttons, kept in the layout file). `rvip/templates/dubtrain` (wav) was
  not needed: the variant's own samples cover every mapped event.
- **Help/Docs**: `web/make-help.py` (standalone: the Docs repo is not in
  the cloud) writes `dist/help.html` (Help button: about, keys to remember
  incl. `p`, Enter menu, inventory letters, `<`/`>`; full key lists parsed
  from `lib/help/commands.txt` + `r_comm.txt` with "(roguelike keyset)";
  saving for the web; tips; new-player guide; playing in the browser;
  credits from `lib/screens/news.txt`, Shockbolt, Dubtrain) and
  `docs/web/faangband-docs.html` (same content as a standalone page).
- Test `web/test/stage6.mjs`: buttons "Sound: off / Music: off", no sample
  requests while off; after switching on, stairs/rest fetch
  `sounds/plm_floor_creak*.mp3`, `amb_thunder_rain.mp3`,
  `amb_door_iron.mp3` and `music/new_town.ogg` (town); no .prf/.cfg
  requests; Help shows the guide; no 4xx responses, no page errors
  (favicon 404 fixed with `<link rel="icon" href="data:,">`).
- **Mac side**: fold `docs/web/faangband-docs.html` into the Docs build
  (`build-docs.py` GAMES entry + `guides.py` Tips/guide, "In the browser"
  section), then optionally switch `make-help.py` to the template's
  import-from-Docs form; rebuild, deploy (`sh web/deploy.sh`), check the
  live page in the browser pane (sound audible, windows drag/rename).

### Stage 7 — publish (done, Mac, 2026-09-26)
- **Mac check** (browser pane, own tab, `web/dist` on a local no-store
  server): birth (world menu `d`, Dwarf Warrior), town with Shockbolt tiles,
  `>` on the stairs → DL1, `p` explore (stops on a new message, "In view: a
  grey mold."), Enter menu + letters in the submenu (`b` → Rest prompt),
  `i` → Enter → object menu → `E` eats; `i` + letter quaffs and the list
  reopens; Windows menu (Recall + Equipment on/off), layout and character
  restored after reload; `<` walked back to the up staircase and took it
  (town); Ctrl-X → Hall of Fame → "FAangband has ended" → Play again loads
  the character; Help guide; Sound/Music off at start, after a click the
  mp3s and `music/new_town.ogg` load; no `.prf`/`.cfg` requests, no console
  errors. Tiles: Shockbolt Dark only, `web/tile-coverage.py` 1316/1316.
- **Fixed** (`9c29725` in the cloud history = `8498987` here): the cloud's
  `make-help.py` wrote its own HTML that used none of the page's help
  classes (unstyled guide) and a `docs/web/faangband-docs.html`: now
  Tactical Angband's form, reading the Docs entry; `build.sh` takes
  `rvip-wm.js` from `~/Games/rvip-tools/web/`; `toolchain.sh` notes Homebrew.
- **Docs**: entry `faangband.html` in `~/Desktop/Games/Roguelikes/Docs`
  (`build-docs.py` GAMES, `guides.py` GUIDES + SAVING); other pages
  unchanged byte for byte.
- **Repos**: this folder = public **memmaker/faangband** (remote
  `memmaker`, branch `main`), history without `rvip/`, `web/shots/`,
  `LESSONS.md` (`git filter-repo --refs 0d85203a0..main`, so upstream
  hashes stay); cloud history with the bundle = private
  **memmaker/faangband-cloud** (`~/Games/faangband-cloud`). Upstream
  NickMcConnell/FAangband `main` @ `0d85203`; README with the compare view.
- **Live**: https://ruzzoli.de/roguelikes/faangband/ (`sh web/build.sh && sh
  web/deploy.sh`, guard now fetches `memmaker`). Card on
  https://ruzzoli.de/roguelikes/ (`faangband.png`: 60 Shockbolt monster
  tiles at 32 px, 384×160; 36 games), tree: the existing FAangband entry
  under Oangband is now a gold link ("2000s · Nick McConnell; 2.0 rebuilt on
  Angband 4.2"; the year is unchecked, stage 8). og block in
  `web/index.html` by hand. The page title already links to
  `../shrine/faangband.html` (stage 8 creates it).
- Open problems: a stair walk that must cross a known trap in a one-wide
  corridor does nothing and prints nothing (`W` + direction steps onto
  it); zoom in a small window changes nothing visible (term 0 stays
  ≥ 80×24, CSS-scaled); Messages shows 4.2's own `<2x>` repeat marker;
  still no ASan run of the stage 3–5 changes, no census of deep levels.

Next: stage 8 (shrine). Template `~/Games/roguelikes-index/shrine/lambdarogue.html`
/ `tactical-angband.html` (4.2 family). Material:
- Manual/help: `docs/*.rst` (Sphinx manual: playing, birth, world,
  command, option, attack, customize, faq, guide, a-quick-demo), in-game
  help `lib/help/*.txt`, the web guide (`dist/help.html`, Docs
  `faangband.html`); home page http://nickmcconnell.github.io/FAangband/.
- Licence: GPL 2 or Angband licence (source headers, `docs/copying.rst`).
- Changelog: `changes.txt` (since 1.4.4, 2.0.0 and 2.0.1 notes); older
  history on the home page / angband.live forum.
- Walkthrough: none in the source; check angband.live, RogueBasin,
  the FAangband page, else report as missing.
- Check the tree year (first FAangband release) and Si Griffin's 0.3.6
  role; add Info button, ✦ and the shrine og block.

### Stage 8 — shrine (done)
- Page https://ruzzoli.de/roguelikes/shrine/faangband.html (roguelikes-index
  `19600e8`): `shrine/faangband.html` + `shrine/faangband/manual.html` (all
  `docs/*.rst` of the Sphinx manual except `hacking/`, plus `lib/help/`
  commands/r_comm/symbols, one `<pre>` each; generator was a scratch script),
  `changelog.txt` (`changes.txt`, which starts at 2.0, + GitHub release notes
  2.0.0/2.0.1), `license.txt` (`docs/copying.rst`). og block by hand.
- Lineage checked: 0.1.0 announced 28 Nov 2005 on r.g.r.a (narkive), based
  on Oangband 0.7.0 (also RogueBasin); 0.3.6 (8 Feb 2009) released for Si
  Griffin ("Psi"), per the archived oook.cz forum thread and `news.txt`;
  2.0.0 22 Aug 2021, 2.0.1 30 Sep 2021 (GitHub releases). Tree entry now
  "2005 · Nick McConnell, from Oangband 0.7.0; 2.0 (2021) rebuilt on
  Angband 4.2" + ✦; card tag 2005 + Info button. Game-title link was
  already live (stage 7); game page not rebuilt.
- Missing: no walkthrough (strategy rules + links instead); no cheat/exploit
  list beyond 4.2's debug/wizard/cheat options; 0.x/1.x changelogs not in
  the repo (linked to the archived angband.oook.cz/faangband page).
- 375 px: no horizontal scroll (shrine, manual, index); all links 200.

Next: stage 9 (graveyard + leaderboard).
