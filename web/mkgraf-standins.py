#!/usr/bin/env python3
"""Same-set stand-ins for the FAangband entries the Shockbolt prefs miss
(RVIP A4: family stand-ins, never ASCII, one set).  Appends a generated block
to lib/tiles/shockbolt/graf-shb-dark.prf and graf-shb-light.prf (idempotent:
the block between the markers is replaced).  Rules:
  monster  -> mapped monster of the same base, nearest depth
  object   -> ring/amulet: the vanilla flavour tile of the same material
              (flvr-shb.prf comments), else same tval, most shared words
  feat     -> table below (paths = stairs, trees = Shockbolt tree monster ...)
  trap     -> table below (player-set monster traps = decoy tile)
  /home/user/venv/bin/python web/mkgraf-standins.py"""
import re, os, unicodedata
T = 'lib/tiles/shockbolt'
BEGIN, END = '# --- RVIP stand-ins (web/mkgraf-standins.py) ---', '# --- end RVIP stand-ins ---'
FEAT = {'travelling merchant': 'General Store', 'secret door': 'granite wall',
        'water': None, 'lowland trees': None, 'highland trees': None,
        'sand dune': 'pile of passable rubble'}
for d in ('north', 'east', 'south', 'west'):
    FEAT[f'easy path {d}'] = 'up staircase'
    FEAT[f'hard path {d}'] = 'down staircase'
RAW = {'water': (0x98, 0xDF), 'lowland trees': (0x9F, 0x83), 'highland trees': (0x9F, 0x83)}
OBJ = {'magestaff': 'quarterstaff', 'dart': 'throwing axe'}
TRAP = {'falling branch': 'rock fall trap'}   # other misses: monster traps -> decoy

def fold(s):
    s = s.replace('& ', '').replace('~', '').replace('armour', 'armor')
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().strip()

flav = {}
cur = None
for line in open(f'{T}/flvr-shb.prf', encoding='utf-8'):
    if line.startswith('# '): cur = fold(line[2:])
    elif line.startswith('flavor:') and cur:
        a, c = line.strip().split(':')[2:4]; flav[cur] = (a, c); cur = None

def gamedata(fname):
    out, cur = [], None
    for line in open(f'lib/gamedata/{fname}', encoding='utf-8'):
        p = line.rstrip('\n').split(':')
        if p[0] == 'name':
            cur = {'name': p[1], 'name2': p[2] if len(p) > 2 else None}; out.append(cur)
        elif cur is not None and len(p) > 1:
            cur.setdefault(p[0], p[1])
    return out

def gen(pref):
    lines = open(f'{T}/{pref}', encoding='utf-8').read()
    if BEGIN in lines: lines = lines[:lines.index(BEGIN)].rstrip('\n') + '\n'
    mon, obj, feat, trap = {}, {}, {}, {}
    for l in lines.splitlines():
        p = l.split(':')
        if p[0] == 'monster' and len(p) == 4: mon[fold(p[1])] = (p[2], p[3])
        elif p[0] == 'object' and len(p) == 5: obj[(fold(p[1]), fold(p[2]))] = (p[3], p[4])
        elif p[0] == 'feat' and len(p) == 5: feat.setdefault(fold(p[1]), []).append((p[2], p[3], p[4]))
        elif p[0] == 'trap' and len(p) == 5: trap.setdefault(fold(p[1]), []).append((p[2], p[3], p[4]))
    out, n = [BEGIN], 0
    mons = gamedata('monster.txt')
    for m in mons:
        if fold(m['name']) in mon: continue
        cand = [x for x in mons if x.get('base') == m.get('base') and fold(x['name']) in mon]
        if not cand: cand = [x for x in mons if fold(x['name']) in mon]
        d = int(m.get('depth', 0) or 0)
        src = min(cand, key=lambda x: abs(int(x.get('depth', 0) or 0) - d))
        out.append(f"monster:{m['name']}:{':'.join(mon[fold(src['name'])])}  # as {src['name']}"); n += 1
    for o in gamedata('object.txt'):
        tv, nm = fold(o.get('type', '')), fold(o['name'])
        if (tv, nm) in obj or tv in ('none', 'potion', 'scroll', 'staff', 'wand', 'rod', 'mushroom'): continue
        if tv in ('ring', 'amulet') and f'{nm} {tv}' in flav:
            ac, why = flav[f'{nm} {tv}'], f'flavour {nm} {tv}'
        else:
            same = [k for k in obj if k[0] == tv]
            if not same: continue
            w = set(nm.split())
            if nm in OBJ: w = set(OBJ[nm].split())
            k = max(same, key=lambda k: len(w & set(k[1].split())))
            ac, why = obj[k], k[1]
        out.append(f"object:{o['type']}:{o['name']}:{ac[0]}:{ac[1]}  # as {why}"); n += 1
    for f in gamedata('terrain.txt'):
        k = fold(f['name'])
        if k in feat or k in ('empty space',): continue
        if k in RAW:
            a, c = RAW[k]; out.append(f"feat:{f['name']}:*:0x{a:02X}:0x{c:02X}")
        elif k in FEAT:
            for li, a, c in feat[fold(FEAT[k])]: out.append(f"feat:{f['name']}:{li}:{a}:{c}  # as {FEAT[k]}")
        else: continue
        n += 1
    for t in gamedata('trap.txt'):
        k = fold(t['name2'] or t['name'])
        if k in trap or k in ('no trap', 'door lock'): continue
        src = TRAP.get(k, 'decoy')
        for li, a, c in trap[fold(src)]: out.append(f"trap:{t['name2']}:{li}:{a}:{c}  # as {src}")
        n += 1
    out.append(END)
    open(f'{T}/{pref}', 'w', encoding='utf-8').write(lines + '\n' + '\n'.join(out) + '\n')
    print(pref, n, 'stand-ins')

for p in ('graf-shb-dark.prf', 'graf-shb-light.prf'): gen(p)
