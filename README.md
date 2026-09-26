**RVIP port** of [FAangband](https://github.com/NickMcConnell/FAangband) 2.0.1
(First Age Angband) by Nick McConnell, from upstream `main` at
[`0d85203`](https://github.com/NickMcConnell/FAangband/tree/0d85203a0927eeaf653580498c2c16bc35379e02)
(2026-09-15; the full upstream history is kept, our commits follow it).
Play: https://ruzzoli.de/roguelikes/faangband/
Our changes: https://github.com/memmaker/faangband/compare/0d85203a0...main

Lineage: Moria (1985) → Umoria (1989) → Angband → Oangband → FAangband
(Nick McConnell; 0.3.6 by Si Griffin); FAangband 2.0 is rebuilt on the
**Angband 4.2** code base. It sets Angband in Beleriand during the War of the
Jewels: a wilderness map of towns, forests, mountains and dungeons instead of
one town above one pit (a classic single-dungeon world is a birth choice).
Upstream docs: `docs/` (manual), `changes.txt`, `lib/help/`.

What this port adds:
- **Web frontend** `src/main-web.c` (4.2 z-term hooks to canvases,
  Emscripten + Asyncify), saves in the browser's IndexedDB, autosave; page
  `web/index.html` + `web/faangband.js` with the shared `rvip-wm.js`
  windows: Map, Inventory, Visible monsters, Visible items, Messages, Recall,
  Equipment. No `-more-` stops, map centred on the player.
- **Explore** `p` and **`<` / `>`** that walk to the nearest known staircase
  or wilderness path and take it (4.2's autoexplore, finished:
  `src/cmd-cave.c`, `src/player-path.c`).
- **Enter menu** of all commands with letters (`src/ui-context.c`,
  `src/ui-game.c`), **inventory cursor** with item menus: letter = main
  action, Shift+letter = drop, Ctrl+letter = inspect, Enter = all actions
  (`src/ui-object.c`, `src/ui-knowledge.c`).
- **Tiles**: the game's own Shockbolt set, drawn nearest-neighbour, plus
  generated same-set stand-ins for FAangband's additions
  (`web/mkgraf-standins.py`, 100% coverage by `web/tile-coverage.py`).
- **Sound and music**: the Dubtrain pack FAangband ships, every sound event
  mapped (`lib/customize/sound.prf`), town music; both off by default.
- One upstream bug fix: `main-gcu.c` colour index out of range (`port:` commit).

Controls: arrows / numpad move and attack (Shift runs), `p` explore,
`<`/`>` stairs and paths, Enter command menu, `i`/`e` inventory and
equipment, `?` help, Ctrl-S save, Ctrl-X save and quit. The Help button opens
the game guide.

Build: `sh web/build.sh` → `web/dist` (Homebrew `emcc` 6.0.10 and `cwebp`;
`web/toolchain.sh`). Tests: `web/test/*.mjs` (Playwright). Deploy:
`sh web/deploy.sh`. Notes: `HANDOVER.md`.

Credits: FAangband by Nick McConnell (0.3.6 by Si Griffin), based on Moria,
Umoria, Angband and Oangband with ideas from NPPangband and Unangband;
contributors Robert Alan Koeneke, James E. Wilson, Ben Harrison, Robert
Ruehlmann, Leon Marrick, Bahman Rabii, Andi Sidwell and others
(`lib/screens/news.txt`). Tiles: Shockbolt tileset © Raymond Gaustadnes.
Sounds: Dubtrain Angband Sound Pack (Dubtrain). Licence: GNU GPL 2 or the
Angband licence, at your choice (source headers, `docs/copying.rst`).
Web port: memmaker.

---

# [FAangband](https://github.com/NickMcConnell/FAangband) 2.0.1

First Age Angband is a variant of [Angband](http://angband.github.io/angband/).

For descriptions, see the main [FAangband web page](http://nickmcconnell.github.io/FAangband/).

For other Angband-related things, see the live site (http://angband.live/).
