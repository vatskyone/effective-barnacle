
# STEP 7 · Functional features of the printed parts (exact booleans): shells, frames, pods, tiles, knobs, keycaps, carrier, seam plates
L = layout(); MM = M_int()
cPI = coll('Printed internals', 'Internals')
def ob(n): return bpy.data.objects[n]
inner_y = D / 2 - WALL; pcb_mid = (PCB_TOP + PCB_BOT) / 2
SHAFT_TOP = KNOB_BASE + 0.6 + 8.95 - 1.45; POT_SHAFT_TOP = TILE_TOP + VOL_LIFT + 7.5 - 1.0

# ── Bottom shell halves (P01 / P02): 2.0 mm floor, 3.0 mm walls ──
for tag in ('L (P01)', 'R (P02)'):
    fl = ob('Bottom shell %s floor' % tag); boolean(fl, ob('Bottom shell %s wall' % tag), 'UNION'); fl.name = 'Bottom shell %s' % tag
shL, shR = ob('Bottom shell L (P01)'), ob('Bottom shell R (P02)')
half = lambda x: shL if x < SEAM else shR
adds = {shL: [], shR: []}
for o in [o for o in cPI.objects if o.name.startswith('PCB support post') and not o.name.endswith('pin')]:
    pin = o.children[0]; x = sum(v.co.x for v in o.data.vertices) / len(o.data.vertices)        # mesh centre (the object origin is 0)
    mw = pin.matrix_world.copy(); pin.parent = None; pin.matrix_world = mw
    adds[half(x)].append(merge('_post', [o, pin]))
for o in [o for o in cPI.objects if o.name.startswith('PCB rest on ballast') and not o.name.endswith('pin')]:
    pin = o.children[0]; mw = pin.matrix_world.copy(); pin.parent = None; pin.matrix_world = mw; boolean(o, pin, 'UNION')
for (x, y) in FRAME_SCREWS: adds[half(x)].append(tcyl(x, y, FLOOR - 0.2, 2.8, SPLIT - FLOOR + 0.2))
sx, sy = L['spk']['x'], L['spk']['y']
adds[shL] += [tmp([circ(sx, sy, 22.2, 72), circ(sx, sy, 16.0, 72)], FLOOR - 0.2, (PCB_BOT - 0.3 - 4.8) - FLOOR + 0.2),
              tmp([circ(sx, sy, 22.2, 72), circ(sx, sy, 20.25, 72)], FLOOR - 0.2, (PCB_BOT - 0.6) - FLOOR + 0.2)]
for (jx, jy) in L['jacks']:                                                  # jack cradles
    adds[shL].append(tmp([rr(jx + 0.6, jy, 13.6, 8.8, 0.6), rr(jx, jy, 12.4, 6.4, 0.3)], FLOOR - 0.2, 5.2))
swx, swy = L['switch']; SW_Z = 5.6; bx0 = W / 2 - WALL - 4.5                   # slide-switch bracket: seat block, end lips, back stops clear of the pins
adds[shR] += [tmp([rr(bx0 + 2.25, swy, 4.5 + 0.2, 8.6 + 0.2, 0.3)], FLOOR - 0.2, (SW_Z - 2.2) - FLOOR + 0.2)]
adds[shR] += [tmp([rr(bx0 + 2.25, swy + s_ * 5.0, 4.5 + 0.2, 1.4, 0.3)], FLOOR - 0.2, (SW_Z + 1.4) - FLOOR + 0.2) for s_ in (-1, 1)]
adds[shR] += [tmp([rr(bx0 - 0.6, swy + s_ * 3.7, 1.2, 1.4, 0.2)], FLOOR - 0.2, (SW_Z + 1.4) - FLOOR + 0.2) for s_ in (-1, 1)]
# battery fences: a 1.2 mm wall along the front and back of every pocket (4.5 mm tall), end walls on the two outer cells;
# the posts in the 7.2 mm gaps hold the cells sideways. Behind the cells under the display the carrier is the back stop.
dxp_, dyp_ = L['disp']; car_x0, car_x1 = dxp_ - (DISP_W + 0.4) / 2 - 2.0, dxp_ + (DISP_W + 0.4) / 2 + 2.0
def fence(x0, x1, y0, y1):
    if x1 - x0 < 1.0: return
    o = tmp([rr((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.3)], FLOOR - 0.2, 4.7)
    xs = [x0, x1]; adds[half((x0 + x1) / 2)].append(o)
for i, (bx_, by_, sd) in enumerate(L['bats']):
    x0, x1, y0, y1 = bx_ - BAT_W / 2 - 0.4, bx_ + BAT_W / 2 + 0.4, by_ - BAT_D / 2 - 0.4, by_ + BAT_D / 2 + 0.4
    fence(x0 + 3.0, x1 - 3.0, y0 - 1.2, y0)                                          # front
    for (a, b) in ((x0 + 3.0, min(x1 - 3.0, car_x0 - 0.6)), (max(x0 + 3.0, car_x1 + 0.6), x1 - 3.0)):   # back, except behind the display carrier
        if b > a and not (a > car_x0 and b < car_x1): fence(a, b, y1, y1 + 1.2)
    if i == 0: fence(x0 - 1.2, x0, y0 + 4, y1 - 4)
    if i == len(L['bats']) - 1: fence(x1, x1 + 1.2, y0 + 4, y1 - 4)
sp_x, sp_y, sp_w, sp_d = SEAM_PLATE
prism('Seam joiner (P05)', [rr(sp_x, sp_y, sp_w - 0.8, sp_d - 0.8, 1.0)] + [circ(sp_x + s_ * 8.0, sp_y, 1.25, 20) for s_ in (-1, 1)], FLOOR, 3.0, 0.4, [MM['pb']], cPI, 30)
for sh_, objs in adds.items(): boolean(sh_, merge('_adds', objs), 'UNION')
cutL, cutR = [], []
for (x, y) in FRAME_SCREWS:
    (cutL if x < SEAM else cutR).append(lathe('_cs', [(0.001, -0.1), (3.0, -0.1), (3.0, 0.0), (1.7, 1.75), (1.7, SPLIT + 0.1), (0.001, SPLIT + 0.1)], x, y, 0, [], SC, 32, 0))   # one solid: countersink + clearance
for s_ in (-1, 1):                                                          # seam joiner: one M3 × 6 from below on each side
    (cutL if s_ < 0 else cutR).append(lathe('_cs', [(0.001, -0.1), (3.0, -0.1), (3.0, 0.0), (1.7, 1.75), (1.7, FLOOR + 0.1), (0.001, FLOOR + 0.1)], sp_x + s_ * 8.0, sp_y, 0, [], SC, 32, 0))
for st in STEEL:                                                             # steel ballast screws: countersink + clearance through the floor
    for (x, y) in st['screws']: (cutL if x < SEAM else cutR).append(lathe('_cs', [(0.001, -0.1), (3.0, -0.1), (3.0, 0.0), (1.7, 1.75), (1.7, FLOOR + 0.1), (0.001, FLOOR + 0.1)], x, y, 0, [], SC, 32, 0))
for (bx_, by_, sd) in L['bats']:                                             # 1.0 mm battery pockets
    (cutL if bx_ < SEAM else cutR).append(tmp([rr(bx_, by_, BAT_W + 0.8, BAT_D + 0.8, 1.6)], FLOOR - BAT_POCKET, BAT_POCKET + 0.1))
for (jx, jy) in L['jacks']:
    cutL += [tmp([rr(jx + 6.2 + 0.4, jy, 3.4, 7.4, 0.4)], FLOOR + 0.9, 6.0), through(-W / 2 + WALL / 2, jy, FLOOR + 2.5, 3.15, WALL + 2, 'X')]
cutL += [tmp([rr(sx + 21.2, sy, 3.4, 5.4, 0.4)], FLOOR + 0.6, 8.0)]                                        # speaker ring: lead notch
cutR += [through_rr(USBC_X, inner_y + WALL / 2, pcb_mid, 9.6, 3.9, 1.8, WALL + 2)]                      # USB-C data/charge
o_ = tmp([rr(0, 0, 1.6 + 0.4, 4.0 + 0.4, 0.4)], -(WALL + 2) / 2, WALL + 2); o_.location = (W / 2 - WALL / 2, swy, SW_Z); o_.rotation_euler = (0, PI / 2, 0); cutR.append(o_)   # switch slot (actuator 2.0, travel 2.0)
o_ = tmp([rr(0, 0, 5.0, 9.0, 1.2)], -0.6, 1.2); o_.location = (W / 2, swy, SW_Z); o_.rotation_euler = (0, PI / 2, 0); cutR.append(o_)       # 0.6 mm finger recess around it
cutR.append(through(L['chg_led'][0], inner_y + WALL / 2, 8.0, 0.95, WALL + 2, 'Y'))                 # charge LED light pipe
socx, socy = L['soc']
cutR += [tmp([rr(socx, socy, SPREAD_W + 0.3, SPREAD_D + 0.3, 2.1)], -0.1, 1.1), tmp([rr(socx, socy, WIN_W, WIN_D, 2.0)], -0.1, FLOOR + 0.3)]
# cooling grille: slots in the floor in front of and beside the heat spreader; the 2.5 mm feet leave an air gap under the case
for k in range(14): cutR.append(tmp([rr(95.0 + k * 3.6, 14.5, 1.6, 7.0, 0.8)], -0.1, FLOOR + 0.2))
for k in range(6): cutR.append(tmp([rr(157.0, 24.0 + k * 3.6, 14.0, 1.6, 0.8)], -0.1, FLOOR + 0.2))
cutR += [tcyl(*L['boot'], -0.1, 1.6, FLOOR + 0.3), tmp([rr(*L['ufl'], 4.0, 4.0, 0.5)], 1.0 - 0.01, FLOOR)]
dxp, dyp = L['disp']; PEGS = [(dxp + a * (DISP_W / 2 + 1.2), dyp + b * 20) for a in (-1, 1) for b in (-1, 1)]
for (x, y) in PEGS: (cutL if x < SEAM else cutR).append(tcyl(x, y, FLOOR - 1.0, 1.6, 1.2))
boolean(shL, merge('_cutL', cutL)); boolean(shR, merge('_cutR', cutR))
lathe('Charge LED light pipe (P20)', [(0.001, 0), (0.9, 0), (0.9, D / 2 - L['chg_led'][1] - 0.55), (0.001, D / 2 - L['chg_led'][1] - 0.55)], 0, 0, 0, [MM['pipe']], cPI, 16, 30)
lp = bpy.data.objects['Charge LED light pipe (P20)']; lp.location = (L['chg_led'][0], L['chg_led'][1] + 0.55, 8.0); lp.rotation_euler = (-PI / 2, 0, 0)

# ── Top frame halves (P03 / P04) ──
for tag in ('L (P03)', 'R (P04)'):
    b_ = ob('Top frame %s band' % tag); boolean(b_, ob('Top frame %s wall' % tag), 'UNION'); b_.name = 'Top frame %s' % tag
tfL, tfR = ob('Top frame L (P03)'), ob('Top frame R (P04)'); th = lambda x: tfL if x < SEAM else tfR
adds = {tfL: [], tfR: []}
for (x, y) in FRAME_SCREWS: adds[th(x)].append(tcyl(x, y, SPLIT, 2.6, (PLATE_TOP - PLATE_T if x < OPEN['x1'] + 2 + 2.6 + 0.5 else PLATE_TOP + 0.1) - SPLIT))   # outside the plate the boss runs up to the band
for t_, objs in adds.items():
    if objs: boolean(t_, merge('_tadds', objs), 'UNION')
cutL, cutR = [], []
for (x, y) in FRAME_SCREWS: (cutL if x < SEAM else cutR).append(lathe('_ins', [(0.001, SPLIT - 0.1), (1.7, SPLIT - 0.1), (1.7, PLATE_TOP - 0.1), (2.0, PLATE_TOP - 0.1), (2.0, PLATE_TOP + 4.5), (0.001, PLATE_TOP + 4.5)], x, y, 0, [], SC, 32, 0))
cutR += [through_rr(USBC_X, inner_y + WALL / 2, pcb_mid, 9.6, 3.9, 1.8, WALL + 2)]
vx = X(1189.5); vy0_ = Y(92.5) - (64 * S + 8) / 2; vy1_ = L['mic'][1] + 3.2                      # VU + mic strip pocket
cutR += [tmp([rr(vx, (vy0_ + vy1_) / 2, 5.4, vy1_ - vy0_ + 0.6, 0.4)], PLATE_TOP - 0.1, 1.7)]
cutR += [tcyl(vx, Y(64.5 + 14 * i), PLATE_TOP + 1.0, 0.75, FRAME_TOP - PLATE_TOP, 20) for i in range(5)]
cutR += [tcyl(X(x + 2), Y(y + 2), PLATE_TOP + 1.0, 2 * S + 0.05, FRAME_TOP, 20) for (x, y) in ((1184, 24), (1191, 24), (1184, 31), (1191, 31))]   # mic holes: open into the pocket
for n in ('Rail text WEB-1', 'Rail text by'):        # engrave the rail text 0.4 mm deep
    t = bpy.data.objects.get(n)
    if not t: continue
    t.data.extrude = 0.35; t.location.z = FRAME_TOP - 0.05; bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(t.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    c_ = bpy.data.objects.new('_txt', me); SC.objects.link(c_); c_.matrix_world = t.matrix_world; cutR.append(c_); bpy.data.objects.remove(t)
boolean(tfL, merge('_tcutL', cutL)); boolean(tfR, merge('_tcutR', cutR))
for o in [o for o in bpy.data.objects if o.name.startswith(('Mic hole', 'VU light pipe'))]: bpy.data.objects.remove(o)
for i in range(5):
    lathe('VU light pipe %d (P20)' % (i + 1), [(0.001, 0), (0.7, 0), (0.7, FRAME_TOP - PLATE_TOP - 1.0), (0.001, FRAME_TOP - PLATE_TOP - 1.0)], vx, Y(64.5 + 14 * i), PLATE_TOP + 1.0, [MM['pipe']], coll('Top frame'), 16, 30)

# ── Knob pods (P06), volume tile (P09) ──
for i, (x, y) in enumerate(L['enc']):
    nm = ENCS[i][2]; pod = ob('Knob pod %s (P06)' % nm); dish = ob('Knob pod %s dish' % nm)
    mw = dish.matrix_world.copy(); dish.parent = None; dish.matrix_world = mw; boolean(pod, dish, 'UNION')
    boolean(pod, merge('_enc', [tmp([rr(x, y, 13.2, 13.0, 0.5)], PLATE_TOP - 0.1, PCB_TOP + 4.5 + 0.2 - PLATE_TOP + 0.1),
                                tcyl(x, y, PLATE_TOP, 3.65, POD_TOP, 40), tcyl(x, y, POD_POCKET, 10.9, POD_TOP, 80)]))     # segment counts differ from the dish (90): no degenerate intersections
v = L['vol']
boolean(ob('Volume tile (P09)'), merge('_pot', [tmp([rr(v['x'], v['y'], 10.4, 11.6, 0.4)], PLATE_TOP - 0.1, PCB_TOP + 6.5 + 0.2 - PLATE_TOP + 0.1), tcyl(v['x'], v['y'], PLATE_TOP, 3.65, POD_TOP)]))

# ── Knobs (P07) at 0°: nut recess, round bore where the shaft is round, D-bore on the flat ──
for i, (x, y) in enumerate(L['enc']):
    nm = ENCS[i][2]; k = ob('Knob %s (P07)' % nm); k.rotation_euler.z = 0
    boolean(k, merge('_kc', [tcyl(x, y, KNOB_BASE - 0.5, 6.0, (PCB_TOP + 4.5 + 7.0 + 0.3) - KNOB_BASE + 0.5),
                             tcyl(x, y, KNOB_BASE, 3.05, (PCB_TOP + 14.5 + 0.3) - KNOB_BASE, 48), tmp([dshape(x, y, 3.05, 1.55)], KNOB_BASE, SHAFT_TOP + 0.3 - KNOB_BASE)]))
    for part in ('skirt', 'hairline'): boolean(ob('Knob %s %s' % (nm, part)), tcyl(x, y, KNOB_BASE - 0.5, 6.0, 3.0))
vk = ob('Volume knob (P10)'); vk.rotation_euler.z = 0; vk.location.z += VOL_LIFT; bpy.context.view_layer.update()
vb = TILE_TOP + VOL_LIFT
boolean(vk, merge('_vc', [tcyl(v['x'], v['y'], vb - 0.5, 5.9, (PCB_TOP + 6.5 + 7.0 + 0.2) - vb + 0.5),
                          tcyl(v['x'], v['y'], vb, 3.05, (TILE_TOP + 2.4 + 0.3) - vb, 48), tmp([dshape(v['x'], v['y'], 3.05, 1.55)], vb, POT_SHAFT_TOP + 0.3 - vb)]))
for part in ('collar', 'edge'): boolean(ob('Volume knob %s' % part), tcyl(v['x'], v['y'], vb - 0.5, 5.9, 3.0))

# ── Keycap light guides (P19): light enters above the switch LED window and is carried to the top-right dot ──
def bar(x0, y0, x1, y1, w, z0, h):
    ang = math.atan2(y1 - y0, x1 - x0); ln = math.hypot(x1 - x0, y1 - y0)
    o = tmp([rr(0, 0, ln + w, w, w / 2 - 0.01, 4)], z0, h); o.location.x, o.location.y = (x0 + x1) / 2, (y0 + y1) / 2; o.rotation_euler.z = ang; return o
for i, (a, x_, y_, w_, h_) in enumerate(FKEYS):
    cap = ob('Key %s (%s)' % (a, 'P14' if h_ > 65 else 'P13')); lx, ly = L['led'][i]; kx, ky = L['sw'][i]; wx, wy = kx, ky + 5.6
    boolean(cap, merge('_lg', [tcyl(lx, ly, CAP_BOT - 0.5, 0.6, CAP_H + 1.0, 16), bar(wx, wy, lx, ly, 1.4, CAP_BOT - 0.5, 1.7), tmp([rr(wx, wy, 3.2, 2.2, 0.4)], CAP_BOT - 0.5, 1.7)]))
    g_ = union_all('Key %s light guide (P19)' % a, [tcyl(lx, ly, CAP_BOT + 0.05, 0.55, CAP_H - 0.05, 16), bar(wx, wy, lx, ly, 1.2, CAP_BOT + 0.05, 1.05), tmp([rr(wx, wy, 3.0, 2.0, 0.3)], CAP_BOT + 0.05, 1.05)], coll('Keycaps'), [MM['pipe']])
    g_.parent = cap; g_.matrix_parent_inverse = Matrix.Translation(-cap.location)

# ── Display carrier (P21): ledge 0.5 mm lower for a foam ring under the panel ──
dW, dH = DISP_W + 0.4, DISP_H + 0.4; LEDGE = (DISP_TOP - DISP_T) - 0.5
car = union_all('Display carrier (P21)', [tmp([rr(dxp, dyp, dW + 4.0, dH + 4.0, 1.5), rr(dxp, dyp, dW, dH, 0.6)], FLOOR, (DISP_TOP - 0.8) - FLOOR),
            tmp([rr(dxp, dyp, dW, dH, 0.6), rr(dxp, dyp, dW - 8.0, dH - 8.0, 0.6)], FLOOR, LEDGE - FLOOR)] + [tcyl(x, y, FLOOR - 1.0, 1.45, 1.05) for (x, y) in PEGS], cPI, [MM['pb']])
boolean(car, merge('_carcut', [tmp([rr(dxp, dyp - DISP_H / 2, 31.0, 12.0, 0.5)], FLOOR - 1.5, DISP_TOP + 2),
          tmp([rr(dxp, inner_y + 5.0, DISP_W + 20, 10.4, 0.1)], FLOOR - 1.5, DISP_TOP + 2),                      # open at the back: the case wall is the back stop
          tmp([rr(L['car_x1'] - 3.0, L['ffc_y'], 8.0, 13.2, 0.4)], FLOOR + 0.8, (LEDGE + 0.4) - (FLOOR + 0.8))]))   # FFC slot through the right side
fr = prism('Display foam ring (H33)', [rr(dxp, dyp, dW - 0.4, dH - 0.4, 0.6), rr(dxp, dyp, dW - 7.6, dH - 7.6, 0.6)], LEDGE, 0.5, 0, [MM['foam']], coll('Foam', 'Internals'), 0)
boolean(fr, merge('_frcut', [tmp([rr(dxp, dyp - DISP_H / 2, 31.0, 12.0, 0.5)], LEDGE - 1, 2), tmp([rr(dxp, inner_y + 5.0, DISP_W + 20, 10.4, 0.1)], LEDGE - 1, 2),
                            tmp([rr(L['car_x1'] - 3.0, L['ffc_y'], 8.0, 13.2, 0.4)], LEDGE - 1, 2)]))
# speaker gasket between the speaker rim and the PCB
prism('Speaker gasket (H33)', [circ(sx, sy, 20.0, 72), circ(sx, sy, 18.2, 72)], PCB_BOT - 0.3, 0.3, 0, [MM['foam']], coll('Foam', 'Internals'), 0)

# ── Floor foam (H33): 2 mm PE foam on the floor between the cells, under the key bed (damps the case cavity) ──
fl = prism('Floor foam 2 mm (H33)', [rr(39.0, 7.0, 86.0, 26.0, 2.0)], FLOOR, 2.0, 0, [MM['foam']], coll('Foam', 'Internals'), 0)     # behind the cells, in front of the back steel
fc = [tcyl(x, y, FLOOR - 0.5, 3.6, 3.0) for (x, y) in bpy.context.scene['web1_posts']]
fc += [tmp([rr(sp_x, sp_y, sp_w + 1.0, sp_d + 1.0, 1.0)], FLOOR - 0.5, 3.0), tmp([rr(*L['boot'], 6.0, 6.0, 1.0)], FLOOR - 0.5, 3.0)]
for (x, y) in FRAME_SCREWS: fc.append(tcyl(x, y, FLOOR - 0.5, 3.4, 3.0))
for st in STEEL: fc.append(tmp([rr((st['x0'] + st['x1']) / 2, (st['y0'] + st['y1']) / 2, st['x1'] - st['x0'] + 1.0, st['y1'] - st['y0'] + 1.0, 2.0)], FLOOR - 0.5, 3.0))
boolean(fl, merge('_ffc', fc))
