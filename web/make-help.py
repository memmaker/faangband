#!/usr/bin/env python3
"""Writes the FAangband game guide: the in-page Help (dist/help.html, a
fragment for #help-body) and a standalone Docs page
(docs/web/faangband-docs.html, for the Mac side's Docs build: fold it into
build-docs.py / guides.py as a GAMES entry).  Cloud run: the Docs repo
(~/Desktop/Games/Roguelikes/Docs) is not here, so the guide text lives in
this file; the key lists are parsed from the game's own lib/help files.
  python3 web/make-help.py [out-fragment]"""
import html, re, sys
esc = html.escape

def kbd(k):
    return '<kbd>' + esc(k) + '</kbd>'

def keys(fname):
    """Two-column key tables of lib/help/commands.txt / r_comm.txt."""
    out = []
    for line in open(f'lib/help/{fname}', encoding='utf-8'):
        m = re.match(r'^  (\S{1,2})\s{2,}(.*?)(?:\s{2,}(\S{1,2})\s{2,}(.*))?\s*$', line.rstrip('\n'))
        if not m: continue
        for k, d in ((m.group(1), m.group(2)), (m.group(3), m.group(4))):
            if k and d and d.strip() != '-' and not d.startswith('(special'):
                out.append((k, d.strip()))
    return out

KEY_HINTS = [
    ('?', 'In-game help: the list of all commands'),
    ('p', 'Auto-explore until something turns up'),
    ('Enter', 'Menu of all commands (letters pick an entry)'),
    ('i', 'Inventory: letter = use, Shift+letter = drop, Ctrl+letter = inspect, Enter = all actions'),
    ('<', 'Go up: takes the stairs or path here, or walks to the nearest known one'),
    ('>', 'Go down: same, downwards'),
    ('^S', 'Save'),
]

ABOUT = '''<p><strong>FAangband</strong> (First Age Angband) by Nick McConnell is an
Angband variant set in Beleriand during the War of the Jewels (Tolkien's First
Age). Instead of one dungeon under a town you travel a wilderness map of
Beleriand: forests, mountains, rivers and the towns of Men, Elves and Dwarves,
with dungeons such as Angband itself at the end. Based on Moria, Umoria,
Angband 4.2 and Oangband, with ideas from NPPangband and Unangband.</p>'''

TIPS = '''<ul>
<li>At birth you choose the world: <em>Standard Wilderness</em> (the full map of Beleriand), <em>Extended</em>, <em>Hybrid Dungeon</em>, or <em>Angband Dungeon</em> (one classic dungeon below a town, closest to Vanilla Angband).</li>
<li>Wilderness levels are joined by paths at their edges (easy and hard paths, drawn as up and down stairs); the status line names the path you stand on. <kbd>&lt;</kbd> / <kbd>&gt;</kbd> walk to the nearest known one.</li>
<li>Specialties are FAangband's feats: when the status line shows <em>Spec.</em>, press <kbd>S</kbd> to learn one.</li>
<li>Rogues can set monster traps with <kbd>+</kbd>; <kbd>s</kbd> steals from a monster.</li>
<li>Rest (<kbd>R</kbd> then <kbd>&amp;</kbd>) before you move on; read unknown scrolls and quaff unknown potions when you are safe, that is how items get identified.</li>
<li>Keep a Scroll of Word of Recall: it takes you back to your home town and later down to your deepest level.</li>
</ul>'''

GUIDE = '''<ol>
<li><strong>Start</strong>: pick <em>Angband Dungeon</em> for a first game (one town, one dungeon). A Warrior or a Dwarf/Easterling fighter is the forgiving choice.</li>
<li><strong>Shop</strong>: buy Flasks of Oil (throw them with <kbd>v</kbd>), Cure Light Wounds potions and a few Phase Door scrolls in the General Store and Alchemist.</li>
<li><strong>Explore</strong>: <kbd>p</kbd> walks to the next unexplored place and stops when a monster appears. Fight in corridors so only one enemy reaches you.</li>
<li><strong>Stairs</strong>: take <kbd>&gt;</kbd> when the level is done; go deeper only while you win most fights easily. Check <kbd>C</kbd> for your resistances.</li>
<li><strong>Retreat</strong> early: Phase Door, then walk away; quaff a potion before your hit points turn yellow.</li>
</ol>'''

SAVING = '''<ul>
<li><strong>Saving is automatic.</strong> The game is stored in this browser (IndexedDB) while it waits for your next command, when you switch to another tab, and on every level change. Reloading the page continues from there.</li>
<li><kbd>Ctrl+S</kbd> saves right away. <kbd>Ctrl+X</kbd> saves and ends the session; <em>Play again</em> continues.</li>
<li>When your character dies, <em>Play again</em> starts a new one (based on the old one).</li>
<li>Each browser keeps one character. <em>New character</em> deletes it; <em>Export save</em> / <em>Import save</em> move it between browsers or to the desktop game.</li>
<li>Private windows and "clear site data" delete the stored game.</li>
</ul>'''

WEB = '''<ul>
<li><strong>Windows:</strong> the tiled map (Shockbolt tiles), Inventory, Visible monsters and Visible items on the right, Messages at the bottom; Recall and Equipment are in the <em>Windows</em> menu. Drag the gaps to resize.</li>
<li><strong>Zoom −</strong> / <strong>Zoom +</strong> change the tile size; <em>center_player</em> and <em>auto_more</em> are on by default here (<kbd>=</kbd> changes them).</li>
<li><strong>Sound</strong> and <strong>Music</strong> are off until you switch them on: the game's own sound events with the Dubtrain Angband Sound Pack that ships with FAangband, and town music.</li>
<li>Browsers keep some shortcuts (<kbd>Ctrl+W</kbd>, <kbd>Ctrl+T</kbd>, <kbd>Ctrl+N</kbd>); <kbd>Ctrl+S</kbd> and <kbd>Ctrl+X</kbd> reach the game.</li>
</ul>'''

CREDITS = '''<p>FAangband 0.1.0–2.0.1 by Nick McConnell (FAangband 0.3.6 by Si Griffin),
<a href="https://github.com/NickMcConnell/FAangband">github.com/NickMcConnell/FAangband</a>.
Contributors include Robert Alan Koeneke, James E. Wilson, Ben Harrison, Robert
Ruehlmann, Leon Marrick, Bahman Rabii, Jeff Greene, Diego Gonzalez, Andrew
Doull, Andi Sidwell, Pete Mack and others (news screen). Licence: GPL 2 /
Angband licence (source headers). Tiles: Shockbolt © Raymond Gaustadnes.
Sounds: Dubtrain Angband Sound Pack (Dubtrain Records). Browser port: RVIP.</p>'''

def keylist():
    orig, rogue = keys('commands.txt'), keys('r_comm.txt')
    rows = ''.join(f'<tr><td>{kbd(k)}</td><td>{esc(d)}</td></tr>' for k, d in orig)
    rows += ''.join(f'<tr><td>{kbd(k)}</td><td>{esc(d)} (roguelike keyset)</td></tr>' for k, d in rogue)
    return f'<details><summary>All keys ({len(orig)} original, {len(rogue)} roguelike)</summary><table>{rows}</table></details>'

def body():
    hints = '<dl>' + ''.join(f'<dt>{kbd(k)}</dt><dd>{esc(d)}</dd>' for k, d in KEY_HINTS) + '</dl>'
    return (f'<h1>FAangband</h1>{ABOUT}<h2>Keys to remember</h2>{hints}{keylist()}'
            f'<h2>Saving</h2>{SAVING}<h2>Tips</h2>{TIPS}<h2>New player\'s guide</h2>{GUIDE}'
            f'<h2>Playing in the browser</h2>{WEB}<h2>Credits</h2>{CREDITS}')

out = sys.argv[1] if len(sys.argv) > 1 else 'web/dist/help.html'
open(out, 'w', encoding='utf-8').write(body() + '\n')
open('docs/web/faangband-docs.html', 'w', encoding='utf-8').write(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FAangband</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;max-width:860px;margin:2em auto;padding:0 16px;background:#111;color:#ddd}}
kbd{{background:#333;border:1px solid #555;border-radius:3px;padding:0 4px;font-family:monospace}}
dt{{float:left;clear:left;width:5em}}dd{{margin-left:6em}}a{{color:#9cf}}td{{padding:1px 8px}}h1,h2{{color:#fc6}}</style>
</head><body>{body()}</body></html>
''')
print('wrote', out, 'and docs/web/faangband-docs.html')
