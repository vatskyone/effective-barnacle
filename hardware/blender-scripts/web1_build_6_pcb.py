
# STEP 6 · Support posts (auto-placed), main PCB (H14), switch plate (H15), frame screws and inserts
L = layout(); MM = M_int()
cP, cF, cPI = coll('Main PCB', 'Internals'), coll('Fasteners', 'Internals'), coll('Printed internals', 'Internals')
P, sc, v = L['pcb'], L['sc'], L['vol']

# obstacles on the PCB underside / floor (rectangles x0, y0, x1, y1)
R = []
for i, (x, y) in enumerate(L['sw']):
    if i not in L['nosock']: R.append((x - 6.9, y - 8.5, x + 11.9, y - 1.2))
    R.append((x - 2.8, y - 2.8, x + 2.8, y + 2.8))
def rect(cx, cy, hw, hh): R.append((cx - hw, cy - hh, cx + hw, cy + hh))
rect(CM5_X, CM5_Y, 29, 22); rect(*L['soc'], SPREAD_W / 2 + 2, SPREAD_D / 2 + 2); rect(RP_X, RP_Y, 13, 7)
dx, dy = L['disp']; rect(dx, dy - 3, DISP_W / 2 + 3.5, DISP_H / 2 + 6)
rect(L['spk']['x'], L['spk']['y'], 23.5, 23.5)
for (x, y) in L['enc']: rect(x, y, 7.5, 9)
rect(v['x'], v['y'], 6, 7); rect(*L['boot'], 4.5, 4.5); rect(*L['jvu'], 3.5, 5)
for (x, y) in L['jacks']: rect(x + 1.0, y, 8, 5.5)                                   # jack + cradle
rect(W / 2 - WALL - 4.0, L['switch'][1], 6.5, 7.0)                                    # slide switch + bracket
rect(USBC_X, D / 2 - 4, 7, 5); rect(*L['chg_led'], 3, 3)
for (x, y, sd) in L['bats']: rect(x, y, BAT_W / 2 + 0.4, BAT_D / 2 + 1.6)              # cell pockets + front / back fences (the gaps stay free for posts)
rect(*L['codec'], 6.5, 5.5); rect(*L['pmic'], 8.5, 6.5)
rect(L['jaud'][0], L['jaud'][1] - 1.0, 8.5, 5.0); rect(L['jsw'][0], L['jsw'][1] - 1.0, 3.5, 5.0)
for (lx, py) in L['batpads']: rect(lx, (BAT_Y + py) / 2, 1.6, abs(BAT_Y - py) / 2 + 2.6)          # battery leads rising to their pads
R.append((L['car_x1'] - 1.0, L['ffc_y'] - 7.5, L['j3'][0] + 8.5, L['ffc_y'] + 7.5)); rect(*L['j3'], 8.8, 3.5)          # display FFC lane and J3
rect(SEAM_PLATE[0], SEAM_PLATE[1], SEAM_PLATE[2] / 2 + 0.5, SEAM_PLATE[3] / 2 + 0.5)                     # seam joiner
rect(84.0, 40.0, 1.5, 22.0); rect(92.0, 60.0, 9.0, 1.8)                                 # Wi-Fi coax lane
for (x, y) in FRAME_SCREWS: rect(x, y, 4.5, 4.5)
for (x, y) in L['ledpcb']: rect(x, y, 2.4, 2.2)
for i in L['nosock']:
    x, y = L['sw'][i]; rect(x, y - 5.9, 1.6, 1.6); rect(x + 5.0, y - 3.8, 1.6, 1.6)          # soldered switch pins under the PCB                         # reverse-mount LEDs under the switch windows
def on_steel(px, py, r=3.0):
    for st in STEEL:
        if st['x0'] + r + 0.5 < px < st['x1'] - r - 0.5 and st['y0'] + r + 0.5 < py < st['y1'] - r - 0.5: return st
        if st['x0'] - r - 1.0 < px < st['x1'] + r + 1.0 and st['y0'] - r - 1.0 < py < st['y1'] + r + 1.0: return False     # straddles an edge
    return None
def free(px, py, RR, r=3.0):
    if not (P['x0'] + 4 < px < P['x1'] - 4 and P['y0'] + 4 < py < P['y1'] - 4): return False
    if abs(px - sc['x']) < sc['w'] / 2 + r + 1 and abs(py - sc['y']) < sc['d'] / 2 + r + 1: return False
    if on_steel(px, py) is False: return False
    if abs(px - SEAM) < r + 0.5: return False                                          # nothing straddles the case seam
    return all(not (x0 - r < px < x1 + r and y0 - r < py < y1 + r) for (x0, y0, x1, y1) in RR)
anchors = [(g, y) for g in GAPS if abs(g - SEAM) > 4 for y in (-46.0, -21.0)]                       # posts between the cells: they also hold the cells in place
anchors += [(x, y) for y in (4.0, 30.0, 52.0) for x in range(-160, 161, 32)]          # a grid: the search snaps each to the nearest free spot
posts = []
for (ax, ay) in anchors:
    best = None; RR = [r_ for r_ in R if r_[0] < ax + 20 and r_[2] > ax - 20 and r_[1] < ay + 20 and r_[3] > ay - 20]
    for i in range(-32, 33):
        for j in range(-32, 33):
            px, py = ax + i * 0.5, ay + j * 0.5
            if free(px, py, RR) and all((px - qx) ** 2 + (py - qy) ** 2 > 324 for (qx, qy) in posts):
                d = (px - ax) ** 2 + (py - ay) ** 2
                if best is None or d < best[0]: best = (d, px, py)
    if best: posts.append((best[1], best[2]))
for k, (x, y) in enumerate(posts):
    st = on_steel(x, y); z0 = FLOOR + STEEL_T if st else FLOOR - 0.2                # on the ballast: a separate printed rest (P26), glued to the steel
    p = prism(('PCB rest on ballast %d (P26)' if st else 'PCB support post %d (P01/P02)') % (k + 1), [circ(x, y, 3.0, 32)], z0, PCB_BOT - z0, 0, [MM['pb'] if st else MM['shell']], cPI, 0)
    pin = prism(p.name.split(' (')[0] + ' pin', [circ(x, y, 1.2, 24)], PCB_BOT, PCB_T - 0.3, 0, [MM['shell']], cPI, 0)
    pin.parent = p; pin.matrix_parent_inverse = Matrix.Translation(-p.location)

for o in [o for o in bpy.data.objects if o.name.startswith('Switch plate (H15)')]: bpy.data.objects.remove(o)
# main PCB: every hole the parts need
holes = [rr(sc['x'], sc['y'], sc['w'], sc['d'], 2.0, 4), circ(L['spk']['x'], L['spk']['y'], 18.0, 64)]
for i, (x, y) in enumerate(L['sw']):
    holes.append(circ(x, y, 2.55, 32))                                                   # Choc v2 centre post
    if i in L['nosock']: holes += [circ(x, y - 5.9, 0.75, 16), circ(x + 5.0, y - 3.8, 0.75, 16)]   # soldered switch pins
    else: holes += [circ(x, y - 5.9, 1.5, 20), circ(x + 5.0, y - 3.7, 1.5, 20)]                       # hot-swap socket cups
for (x, y) in L['ledpcb']: holes.append(rr(x, y, 3.4, 2.9, 0.2, 2))
for (x, y) in L['enc']:
    holes += [circ(x + d_, y + 7.5, 0.5, 12) for d_ in (-2.5, 0, 2.5)] + [circ(x + d_, y - 7.0, 0.5, 12) for d_ in (-2.5, 2.5)]
    holes += [rr(x + s_ * 6.25, y, 1.5, 2.6, 0.3, 2) for s_ in (-1, 1)]
holes += [circ(v['x'] + d_, v['y'] + 5.0, 0.5, 12) for d_ in (-2.5, 0, 2.5)]
for (x, y) in posts: holes.append(circ(x, y, 1.3, 20))
jx, jy = L['jvu']; holes += [circ(jx, jy + d_, 0.45, 12) for d_ in (-2, 0, 2)]
pcb = prism('Main PCB (H14)', [rr((P['x0'] + P['x1']) / 2, (P['y0'] + P['y1']) / 2, P['x1'] - P['x0'], P['y1'] - P['y0'], 2.0)] + holes, PCB_BOT, PCB_T, 0, [MM['pcb']], cP, 0)
cuts = [tmp([rr(USBC_X, P['y1'], 9.2, 4.0, 0.3, 2)], PCB_BOT - 1, PCB_T + 2)]                                # USB-C notch
cuts += [tcyl(x, y, PCB_BOT - 1, 3.0, PCB_T + 2) for (x, y) in FRAME_SCREWS if x < P['x1'] + 2.5]                              # frame-screw boss clearance
boolean(pcb, merge('_pcbcuts', cuts))

# switch plate: switch, knob, pot, screen, speaker cut-outs, light-pipe holes, frame-screw holes
loops = [rr((OPEN['x0'] + OPEN['x1']) / 2, (OPEN['y0'] + OPEN['y1']) / 2, OPEN['x1'] - OPEN['x0'] + 4, OPEN['y1'] - OPEN['y0'] + 4, OPEN['r'] + 2)]
loops += [rr(x, y, 13.8, 13.8, 0.3, 2) for (x, y) in L['sw']] + [rr(x, y, 15, 15, 1, 3) for (x, y) in L['enc']]
loops += [rr(v['x'], v['y'], 11, 12, 1, 3), rr(sc['x'], sc['y'], sc['w'], sc['d'], 7 * S), circ(L['spk']['x'], L['spk']['y'], 17)]
plate = prism('Switch plate (H15)', loops, PLATE_TOP - PLATE_T, PLATE_T, 0, [MM['plate']], coll('Plate'), 0)
boolean(plate, merge('_plcuts', [tcyl(x, y, PLATE_TOP - 2, 1.7, 4) for (x, y) in FRAME_SCREWS]))

# frame screws: M3 × 16 countersunk from below; M3 heat-set inserts (Ø4.0 × 4.0) in the top band
for k, (x, y) in enumerate(FRAME_SCREWS):
    lathe('M3 countersunk ×16 %d (H24)' % (k + 1), [(0.001, 0.0), (2.75, 0.0), (1.5, 1.65), (1.5, 16.0), (0.001, 16.0)], x, y, 0.0, [MM['steel']], cF, 32, 40)
    lathe('M3 insert %d (H24)' % (k + 1), [(1.3, 0.0), (2.0, 0.0), (2.0, 4.0), (1.3, 4.0)], x, y, PLATE_TOP, [MM['brass']], cF, 24, 40)

# plate foam (H33): 2.15 mm Poron between PCB and plate, kills the plate ping and the bottom-out click; die-cut around every part on the PCB top
foam = prism('Plate foam Poron 2 mm (H33)', [rr((P['x0'] + P['x1']) / 2, (P['y0'] + P['y1']) / 2, P['x1'] - P['x0'] - 1.0, P['y1'] - P['y0'] - 1.0, 2.0)], PCB_TOP, 2.15, 0, [MM['foam']], coll('Foam', 'Internals'), 0)
fc = [tmp([rr(x, y, 14.6, 14.6, 0.5)], PCB_TOP - 0.1, 2.4) for (x, y) in L['sw']]
for (x, y) in L['sw']:
    side = 1 if x + 11.0 < P['x1'] - 1 else -1
    fc.append(tmp([rr(x + side * 9.5, y, 2.4, 4.4, 0.3)], PCB_TOP - 0.1, 2.4))
for (x, y) in L['enc']: fc += [tmp([rr(x, y, 13.0, 13.4, 0.5)], PCB_TOP - 0.1, 2.4), tmp([rr(x + 8.4, y + 0.4, 4.4, 2.4, 0.3)], PCB_TOP - 0.1, 2.4)]
fc += [tmp([rr(v['x'], v['y'], 10.8, 12.0, 0.5)], PCB_TOP - 0.1, 2.4), tmp([rr(sc['x'], sc['y'], sc['w'] + 1.0, sc['d'] + 1.0, 2.0)], PCB_TOP - 0.1, 2.4),
       tcyl(L['spk']['x'], L['spk']['y'], PCB_TOP - 0.1, 18.5, 2.4, 64), tmp([rr(USBC_X, P['y1'], 10.5, 8.0, 0.5)], PCB_TOP - 0.1, 2.4)]
fc += [tcyl(x, y, PCB_TOP - 0.1, 3.3, 2.4) for (x, y) in FRAME_SCREWS]
boolean(foam, merge('_foamcuts', fc))
bpy.context.scene['web1_posts'] = [list(p_) for p_ in posts]
result_info = dict(posts=[(round(x, 1), round(y, 1)) for x, y in posts])
