
M = dict(
  case=mat('WEB1 Case', '#c9cbcc', 0.62), caseIn=mat('WEB1 Case inside', '#b8babb', 0.7),
  plate=mat('WEB1 Plate black', '#0b0b0c', 0.55, 0.0), key=mat('WEB1 Key white', '#eeefee', 0.48),
  black=mat('WEB1 Gloss black', '#121213', 0.22, 0.0, 0.6), print_black=mat('WEB1 Print black', '#1b1c1e', 0.75),
  dot=mat('WEB1 Grille hole', '#141516', 0.9), glass=mat('WEB1 Screen glass', '#030304', 0.12, 0.0, 0.5),
  tpu=mat('WEB1 TPU feet', '#1a1a1b', 0.95))
cCase, cTop, cPlate, cTiles, cScreen = coll('Case'), coll('Top frame'), coll('Plate'), coll('Tiles'), coll('Screen')

# Bottom shell halves: floor + walls up to the split line
for side, nm in ((-1, 'Bottom shell L (P01)'), (1, 'Bottom shell R (P02)')):
    prism(nm + ' floor', [half(OUT, None, side)], 0, FLOOR, 0.6, [M['case']], cCase)
    prism(nm + ' wall', [half(OUT, INNER, side)], FLOOR - 0.1, SPLIT - FLOOR + 0.1, 0, [M['case']], cCase)
    # top frame band: sits on the plate and rises to the keytops
    prism(('Top frame L (P03)' if side < 0 else 'Top frame R (P04)') + ' band', [half(OUT, OPEN, side)], PLATE_TOP, FRAME_TOP - PLATE_TOP, 0.6, [M['case']], cTop)
    prism(('Top frame L (P03)' if side < 0 else 'Top frame R (P04)') + ' wall', [half(OUT, INNER, side)], SPLIT, PLATE_TOP - SPLIT + 0.1, 0, [M['case']], cTop)

# Switch plate: 1.2 mm, black, with the switch / knob / screen / speaker cut-outs
sw = [tile(*k[1:]) for k in FKEYS] + [tile(*k[:4]) for k in WKEYS] + [dict(x=X(k[4]), y=Y(k[1] + k[3] / 2)) for k in BKEYS]
loops = [rr((OPEN['x0'] + OPEN['x1']) / 2, (OPEN['y0'] + OPEN['y1']) / 2, OPEN['x1'] - OPEN['x0'] + 4, OPEN['y1'] - OPEN['y0'] + 4, OPEN['r'] + 2)]
loops += [rr(s['x'], s['y'], 13.8, 13.8, 0.3, 2) for s in sw]
loops += [rr(tile(e[0], 20, 132, 146)['x'], tile(e[0], 20, 132, 146)['y'], 15, 15, 1, 3) for e in ENCS]
v, sc, sp = tile(*VOL), tile(*SCR), tile(*SPK)
loops += [rr(v['x'], v['y'], 11, 12, 1, 3), rr(sc['x'], sc['y'], sc['w'], sc['d'], 7 * S), circ(sp['x'], sp['y'], 17)]
prism('Switch plate (H15)', loops, PLATE_TOP - PLATE_T, PLATE_T, 0, [M['plate']], cPlate, 0)

# Volume tile and speaker grille tile: case colour, flush with the keytops, real grille holes
prism('Volume tile (P09)', [rr(v['x'], v['y'], v['w'] - GAP, v['d'] - GAP, 7 * S), circ(v['x'], v['y'], 3.6, 32)], PLATE_TOP, TILE_TOP - PLATE_TOP, 0, [M['case']], cTiles)
g = [rr(sp['x'], sp['y'], sp['w'] - GAP, sp['d'] - GAP, 7 * S)]
for a in range(-5, 6):
    for b in range(-5, 6):
        if a * a + b * b <= 26: g.append(circ(sp['x'] + a * 9.4 * S, sp['y'] + b * 9.4 * S, 1.6 * S, 16))
prism('Speaker grille tile (P11)', g, PLATE_TOP, TILE_TOP - PLATE_TOP, 0, [M['case']], cTiles)
box('Speaker grille backing', sp['x'], sp['y'], PLATE_TOP + 0.3, sp['w'] - 3, sp['d'] - 3, 0.4, [M['dot']], cTiles)

# Screen: black shroud tunnel down to the display, and the window glass flush with the keytops
prism('Screen shroud (P12)', [rr(sc['x'], sc['y'], sc['w'] - GAP, sc['d'] - GAP, 7 * S), rr(sc['x'], sc['y'], sc['w'] - GAP - 2.4, sc['d'] - GAP - 2.4, 1)], DISP_TOP, SCREEN_TOP - DISP_TOP, 0, [M['print_black']], cScreen)
box('Screen window (H22)', sc['x'], sc['y'], SCREEN_TOP - 1.0, sc['w'] - GAP - 1.2, sc['d'] - GAP - 1.2, 2.0, [M['glass']], cScreen)

# Feet
for a in (-1, 1):
    for b in (-1, 1):
        lathe('Foot (P24)', [(0.001, -FEET), (6, -FEET), (6, 0), (0.001, 0)], a * (W / 2 - 14), b * (D / 2 - 12), 0, [M['tpu']], coll('Feet'), 40, 30)
