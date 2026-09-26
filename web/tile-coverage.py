#!/usr/bin/env python3
"""Coverage of the Shockbolt set (lib/tiles/shockbolt, 64x64) over every
monster, object, terrain, trap and flavour entry of lib/gamedata/*.txt.
An entry counts when the pref files map it (4.2 name-based prefs, names
compared case-insensitively) to a non-empty tile inside the sheet.

  /home/user/venv/bin/python web/tile-coverage.py [dark|light|gervais|adam-bolt]
Not drawn, so not counted: none:<curse object>, no trap, door lock, empty space."""
import re, sys, unicodedata
from PIL import Image

SETS = {  # name: (folder, sheet, tile size, pref files)
    'dark': ('shockbolt', '64x64.png', 64, ['graf-shb-dark.prf', 'xtra-shb.prf', 'flvr-shb.prf']),
    'light': ('shockbolt', '64x64.png', 64, ['graf-shb-light.prf', 'xtra-shb.prf', 'flvr-shb.prf']),
    'gervais': ('gervais', '32x32.png', 32, ['graf-dvg.prf', 'flvr-dvg.prf', 'xtra-dvg.prf']),
    'adam-bolt': ('adam-bolt', '16x16.png', 16, ['graf-new.prf', 'flvr-new.prf', 'xtra-new.prf']),
}
variant = sys.argv[1] if len(sys.argv) > 1 else 'dark'
folder, sheet, S, PREFS = SETS[variant]
T = 'lib/tiles/' + folder
img = Image.open(f'{T}/{sheet}').convert('RGBA')
W, H = img.size

def fold(s):
    s = s.replace('& ', '').replace('~', '').replace('armour', 'armor')
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().strip()

def tile_ok(a, c):
    x, y = (c & 0x7F) * S, (a & 0x7F) * S
    if not (a & 0x80 and c & 0x80) or x + S > W or y + S > H:
        return False
    return img.crop((x, y, x + S, y + S)).getbbox() is not None

maps = {}
import os
for f in PREFS:
    if not os.path.exists(f'{T}/{f}'): continue
    for line in open(f'{T}/{f}', encoding='utf-8'):
        p = [x.split('#')[0].strip() if i >= 2 else x for i, x in enumerate(line.rstrip('\n').split(':'))]
        if p[0] == 'monster' and len(p) == 4:
            maps[('monster', fold(p[1]))] = tile_ok(int(p[2], 16), int(p[3], 16))
        elif p[0] == 'object' and len(p) == 5:
            maps[('object', fold(p[1]), fold(p[2]))] = tile_ok(int(p[3], 16), int(p[4], 16))
        elif p[0] in ('feat', 'trap') and len(p) == 5:
            k = (p[0], fold(p[1]))
            # 'unknown grid' is meant to be the empty tile
            maps[k] = maps.get(k, False) or tile_ok(int(p[3], 16), int(p[4], 16)) or k[1] == 'unknown grid'
        elif p[0] == 'flavor' and len(p) == 4:
            maps[('flavor', int(p[1]))] = tile_ok(int(p[2], 16), int(p[3], 16))

def entries(fname, kind):
    out, tval = [], None
    for line in open(f'lib/gamedata/{fname}', encoding='utf-8'):
        p = line.rstrip('\n').split(':')
        if kind == 'object':
            if p[0] == 'name': name = p[1]
            elif p[0] == 'type': out.append(('object', fold(p[1]), fold(name)))
        elif kind == 'flavor':
            if p[0] == 'flavor': out.append(('flavor', int(p[1])))
        elif p[0] == 'name':
            # trap.txt: name:<display name>:<trap name>; prefs use the latter
            out.append((kind, fold(p[2] if kind == 'trap' and len(p) > 2 else p[1])))
    return out

# Flavoured kinds show their flavour tile: count them via the flavour
flav_tvals = set()
for line in open('lib/gamedata/flavor.txt', encoding='utf-8'):
    if line.startswith('kind:'): flav_tvals.add(fold(line.split(':')[1]))

tot = hit = 0
for fname, kind in (('monster.txt', 'monster'), ('object.txt', 'object'), ('terrain.txt', 'feat'),
                    ('trap.txt', 'trap'), ('flavor.txt', 'flavor')):
    ids = [e for e in entries(fname, kind) if e[-1] not in ('<curse object>', 'no trap', 'door lock', 'empty space')]
    ok = [e for e in ids if maps.get(e) or (kind == 'object' and e[1] in flav_tvals)]
    miss = [':'.join(map(str, e[1:])) for e in ids if e not in ok]
    print(f'{fname}: {len(ok)}/{len(ids)}  missing ({len(miss)}): {miss}')
    tot += len(ids); hit += len(ok)
print(f'total: {hit}/{tot} = {100 * hit / tot:.1f}%')
