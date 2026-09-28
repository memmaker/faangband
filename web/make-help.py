#!/usr/bin/env python3
"""Writes the in-page game guide (dist/help.html) for the web build.

The game content comes from the desktop key guides in
~/Desktop/Games/Roguelikes/Docs (build-docs.py + guides.py, entry
faangband.html), so both guides stay in sync; only the saving and "playing
in the browser" parts are written here, because they differ on the web.
  python3 web/make-help.py > web/dist/help.html"""
import html, importlib.util, os, sys

DOCS = os.path.expanduser('~/Desktop/Games/Roguelikes/Docs')
PAGE = 'faangband.html'
BASE = '0d85203a0927eeaf653580498c2c16bc35379e02'

sys.path.insert(0, DOCS)
spec = importlib.util.spec_from_file_location('build_docs', os.path.join(DOCS, 'build-docs.py'))
docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(docs)
from guides import GUIDES, SAVING   # noqa: E402

game = next(g for g in docs.GAMES if g['file'] == PAGE)
guide = dict(GUIDES[PAGE])
info = dict(game['info'])
kbd = docs.kbd
esc = html.escape

WEB = '''<ul>
<li><strong>Windows:</strong> the tiled map (the game's own Shockbolt tiles); Inventory, Visible monsters and Visible items on the right; Messages along the bottom. Recall and Equipment are in the <em>Windows</em> menu. Menus, stores and help pop up over the map.</li>
<li><strong>Resize windows</strong> by dragging the gaps between them. <em>Reset windows</em> puts everything back.</li>
<li><strong>Zoom:</strong> <em>A−</em> / <em>A+</em> on the Map title bar (shown on hover) change the size of the map tiles. Hover over a text window's title to show its <em>A−</em> / <em>A+</em> buttons; click a title to rename the window.</li>
<li><strong>Sound</strong> and <strong>Music</strong> are off until you switch them on in the top bar: the game's own sound events with the Dubtrain Angband Sound Pack that ships with FAangband, and town music.</li>
<li><strong>Keys:</strong> the arrow keys or the numeric keypad move you; Shift+arrow runs. <em>Center map</em> and <em>auto_more</em> are on by default here (change them under <kbd>=</kbd>).</li>
<li>Browsers keep a few shortcuts for themselves (<kbd>Ctrl+W</kbd>, <kbd>Ctrl+T</kbd>, <kbd>Ctrl+N</kbd>, and <kbd>Cmd</kbd> shortcuts on a Mac), so those never reach the game. <kbd>Ctrl+S</kbd> and <kbd>Ctrl+X</kbd> do.</li>
<li>If the game ever crashes, a message appears at the top; reload the page to continue from the last save.</li>
</ul>'''

KEY_HINTS = [
    ('?', 'In-game help: the list of all commands'),
    ('p', 'Auto-explore until something turns up'),
    ('Enter', 'Menu of all commands (letters pick an entry)'),
    ('i', 'Inventory: letter = use, Shift+letter = drop, Ctrl+letter = inspect, Enter = all actions'),
    ('<', 'Go up: takes the stairs or path here, or walks to the nearest known one'),
    ('>', 'Go down: same, downwards'),
    ('^S', 'Save'),
]


def dl(items):
    return '<dl>' + ''.join(f'<dt>{kbd(k)}</dt><dd>{esc(d)}</dd>' for k, d in items) + '</dl>'


def section(anchor, title, body):
    return f'<h2 id="h-{anchor}">{esc(title)}</h2>{body}'


parts = []
toc = [('about', 'About the game'), ('keys', 'Keyboard controls'), ('saving', 'Saving your game'),
       ('tips', 'Tips'), ('guide', "New player's guide"), ('web', 'Playing in the browser'),
       ('credits', 'Credits'), ('version', 'About this version')]
parts.append('<p>' + esc(game['tagline']) + '</p><ul class="toc">' +
             ''.join(f'<li><a href="#h-{a}">{esc(t)}</a></li>' for a, t in toc) + '</ul>')
parts.append(section('about', 'About the game', guide.pop('What makes FAangband special')))

ess = ''.join(f'<div class="box"><h3>{esc(cat)}</h3>{dl(items)}</div>' for cat, items in game['essentials'])
all_keys = game['all']() if callable(game['all']) else game['all']
full = ''.join(f'<div>{kbd(k)}<span>{esc(d)}</span></div>' for k, d in all_keys)
parts.append(section('keys', 'Keyboard controls',
                     '<div class="box key"><h3>The keys to remember</h3>' + dl(KEY_HINTS) + '</div>'
                     '<h3>Essential keys</h3><div class="grid">' + ess + '</div>'
                     '<h3>Auto-explore, stairs and the item lists</h3>' + info['In the browser'] +
                     '<details><summary>Complete key list (' + str(len(all_keys)) + ' commands)</summary>'
                     '<div class="all">' + full + '</div></details>'))
parts.append(section('saving', 'Saving your game', SAVING[PAGE]))
parts.append(section('tips', 'Tips', info['Tips']))
parts.append(section('guide', "New player's guide",
                     ''.join(f'<h3>{esc(t)}</h3>{b}' for t, b in guide.items())))
parts.append(section('web', 'Playing in the browser', WEB))
parts.append(section('credits', 'Credits', info['Credits']))

# RVIP W1: Source and changes
parts.append(section('version', 'About this version',
             '<ul><li>Based on <strong>FAangband 2.0.1</strong> (Nick McConnell; Angband 4.2 code base), '
             f'upstream <code>main</code> at commit <code>{BASE[:9]}</code>.</li>'
             f'<li>Original source: <a href="https://github.com/NickMcConnell/FAangband/tree/{BASE}" target="_blank" rel="noopener">NickMcConnell/FAangband at {BASE[:9]}</a></li>'
             '<li>Our changes (auto-explore, stair walking, command menu, inventory item actions, tile stand-ins, sound, web build): '
             f'<a href="https://github.com/memmaker/faangband/compare/{BASE[:9]}...main" target="_blank" rel="noopener">memmaker/faangband</a></li></ul>'))
print('\n'.join(parts))
