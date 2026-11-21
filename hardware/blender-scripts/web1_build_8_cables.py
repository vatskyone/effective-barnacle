
# STEP 8 · Connectors and cables: FFC, 28 AWG silicone leads (Ø0.9) with JST-SH plugs, a twisted speaker pair, Ø1.13 coax
L = layout(); MM = M_int()
cC, cP, cE = coll('Cables', 'Internals'), coll('Main PCB', 'Internals'), coll('Electronics', 'Internals')
P, sc = L['pcb'], L['sc']
WIRE = {c: mat('WEB1 Wire ' + n, c, 0.45) for c, n in (('#d63a2f', 'red'), ('#202124', 'black'), ('#e8c13a', 'yellow'), ('#2fb673', 'green'), ('#3f7fe8', 'blue'), ('#ececec', 'white'))}
RED, BLK, YEL, GRN, BLU, WHT = '#d63a2f', '#202124', '#e8c13a', '#2fb673', '#3f7fe8', '#ececec'

# J3 position: nearest free spot to the panel's flex, clear of sockets, posts, CM5, encoders
R = []
for i, (x, y) in enumerate(L['sw']):
    if i not in L['nosock']: R.append((x - 6.9, y - 8.5, x + 11.9, y - 1.2))
    R.append((x - 2.8, y - 2.8, x + 2.8, y + 2.8))
for (x, y) in bpy.context.scene.get('web1_posts', []): R.append((x - 3.5, y - 3.5, x + 3.5, y + 3.5))
R += [(RP_X - 13, RP_Y - 7, RP_X + 13, RP_Y + 7)] + [r_ for r_ in L['tall'] if r_ not in L['R']]
def free(px, py, hw, hh):
    if not (P['x0'] + 2 < px - hw and px + hw < P['x1'] - 2 and P['y0'] + 2 < py - hh and py + hh < P['y1'] - 2): return False
    if abs(px - sc['x']) < sc['w'] / 2 + hw + 0.5 and abs(py - sc['y']) < sc['d'] / 2 + hh + 0.5: return False
    return all(not (x0 - hw < px < x1 + hw and y0 - hh < py < y1 + hh) for (x0, y0, x1, y1) in R)
best = None
dx, dy = L['disp']
for i in range(-80, 81):
    for j in range(-40, 41):
        px, py = dx + 12 + i * 0.5, -12.0 + j * 0.5
        if free(px, py, 8.0, 2.6):
            d = (px - dx - 12) ** 2 + (py + 12) ** 2
            if best is None or d < best[0]: best = (d, px, py)
J3 = best[1:]; JA, JS, J8 = L['jaud'], L['jsw'], L['jvu']
cB = coll('Power & ballast', 'Internals')

# PCB-side connectors and mated plugs (side entry; the plug faces -y for JA, JS and the battery headers, +x for J8)
blk('J3 FPC 22p 0.5 mm (H23)', J3[0], J3[1], PCB_BOT - 2.0, 15.3, 4.3, 2.0, MM['bp'], cP)
JAH = JA[1] + 1.6; JSH = JS[1] + 1.6
blk('J6 JST-SH 10p audio (H25)', JA[0], JAH, PCB_BOT - 2.95, 12.0, 4.25, 2.95, MM['nylon'], cP)
blk('JST-SH plug J6 (H25)', JA[0], JAH - 3.725, PCB_BOT - 2.85, 11.0, 3.2, 2.75, MM['nylon'], cC)
blk('J7 JST-SH 2p power switch (H25)', JS[0], JSH, PCB_BOT - 2.95, 4.0, 4.25, 2.95, MM['nylon'], cP)
blk('JST-SH plug J7 (H25)', JS[0], JSH - 3.725, PCB_BOT - 2.85, 3.0, 3.2, 2.75, MM['nylon'], cC)
blk('J8 JST-SH 5p VU + mic (H25)', J8[0], J8[1], PCB_BOT - 2.95, 7.0, 4.25, 2.95, MM['nylon'], cP, PI / 2)
blk('JST-SH plug J8 (H25)', J8[0] + 3.725, J8[1], PCB_BOT - 2.85, 6.0, 3.2, 2.75, MM['nylon'], cC, PI / 2)
for k, (x, y) in enumerate(L['jbat']):
    blk('J%d JST-PH 2p battery %s (H31)' % (9 + k, 'L' if k == 0 else 'R'), x, y + 2.25, PCB_BOT - 4.6, 6.0, 4.5, 4.6, MM['nylon'], cP)
    blk('JST-PH plug battery %s (H31)' % ('L' if k == 0 else 'R'), x, y - 2.25, PCB_BOT - 4.5, 5.8, 4.5, 4.3, MM['nylon'], cC)

# VU + mic strip board in the top-frame pocket (mic port hole Ø0.9 under the gasket); flexible Wi-Fi antenna on the back wall
vx, vy = X(1189.5), Y(92.5); vy0 = vy - (64 * S + 8) / 2; vy1 = L['mic'][1] + 3.2; vlen = vy1 - vy0; vyc = (vy0 + vy1) / 2
prism('VU + mic strip PCB (H14)', [rr(vx, vyc, 4.6, vlen, 0.3), circ(L['mic'][0], L['mic'][1], 0.45, 16)], PLATE_TOP + 0.05, 0.8, 0, [MM['pcb']], coll('Top frame'), 0)
for i in range(5): blk('VU strip LED %d (H10)' % (i + 1), vx, Y(64.5 + 14 * i), PLATE_TOP + 0.05 + 0.1, 3.2, 2.8, 0.75, MM['white'], coll('Top frame'))
blk('VU strip JST-SH 5p (H25)', vx, vy, PLATE_TOP + 0.05 - 2.95, 7.0, 4.25, 2.95, MM['nylon'], coll('Top frame'), PI / 2)     # opening faces the PCB
blk('JST-SH plug VU strip (H25)', vx - 3.725, vy, PLATE_TOP + 0.05 - 2.85, 6.0, 3.2, 2.75, MM['nylon'], cC, PI / 2)
blk('Flex Wi-Fi antenna Molex 146153 (H04)', 120.0, D / 2 - WALL - 0.08, FLOOR + 0.6, 40.0, 0.12, 6.0, MM['ant'], cE)

# ── smooth paths ──
def catmull(pts, step=0.5):
    pts = [Vector(p) for p in pts]; out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        n = max(2, int((p2 - p1).length / step))
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1]); return out
def frames(c):
    out = []
    for i, p in enumerate(c):
        t = (c[min(i + 1, len(c) - 1)] - c[max(i - 1, 0)]); t = t.normalized() if t.length > 1e-9 else Vector((1, 0, 0))
        n = Vector((-t.y, t.x, 0)); n = n.normalized() if n.length > 1e-6 else Vector((1, 0, 0))
        out.append((t, n, t.cross(n).normalized()))
    return out
def tube(name, c, m, r, profile=None):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.use_fill_caps = True
    if profile is not None: cu.bevel_mode = 'OBJECT'; cu.bevel_object = profile; cu.twist_mode = 'Z_UP'
    else: cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(len(c) - 1)
    for k, p in enumerate(c): sp.points[k].co = (p.x, p.y, p.z, 1)
    o = bpy.data.objects.new(name, cu); cC.objects.link(o); cu.materials.append(m); return o
def bundle(name, pts, colors, pitch=1.05, r=0.45, ends=None):
    c = catmull(pts); F = frames(c)
    for k, col in enumerate(colors):
        off = (k - (len(colors) - 1) / 2) * pitch
        cc = [p + F[i][1] * off for i, p in enumerate(c)]
        if ends:   # pin the two ends onto exact pads
            a, b = Vector(ends[k][0]), Vector(ends[k][1]); cc[0] = a; cc[-1] = b
        tube('%s %d' % (name, k + 1), cc, WIRE[col], r)
R30 = 0.40      # 30 AWG silicone (Ø0.8) for everything crimped into 1.0 mm JST-SH

# 1. Display FFC (15→22 pin, 12 mm wide, 0.15 mm thick), from the panel's ZIF out through the carrier slot into J3
prof = bpy.data.curves.new('FFC profile', 'CURVE'); prof.dimensions = '2D'
sp_ = prof.splines.new('POLY'); sp_.points.add(3)
for k, (x, y) in enumerate([(-6.0, -0.075), (6.0, -0.075), (6.0, 0.075), (-6.0, 0.075)]): sp_.points[k].co = (x, y, 0, 1)
sp_.use_cyclic_u = True
pobj = bpy.data.objects.new('FFC profile', prof); cC.objects.link(pobj); pobj.hide_viewport = pobj.hide_render = True
zif_y = dy - DISP_H / 2 + 24.0
tube('Display FFC 15→22p (H23)', catmull([(dx, zif_y - 2.2, 3.78), (dx, dy - DISP_H / 2 + 4, 3.6), (dx, dy - DISP_H / 2 - 4, 3.6), ((dx + J3[0]) / 2, J3[1] + 4.5, 5.2), (J3[0], J3[1] + 5.0, 7.3), (J3[0], J3[1] + 2.15, PCB_BOT - 1.0)], 0.4), MM['ffc'], 0, pobj)

R26 = 0.55      # 26 AWG silicone battery leads (Ø1.1), crimped into JST-PH

# 2. J6 → stereo jacks (rear solder tabs at y +2.25 … -2.25): OUT (tip, ring, sleeve, switch) on pins 0-3, IN (tip, ring, sleeve) on pins 4-6
ex = JAH - 5.3; ez = PCB_BOT - 1.45; TABS = (2.25, 0.75, -0.75, -2.25); tz = FLOOR + 2.5
(jox, joy), (jix, jiy) = L['jacks']
for k, col in enumerate([RED, WHT, BLK, YEL]):                 # OUT: south, then a right turn to the west (nested L-shapes)
    px = JA[0] - 4.5 + k; yo = joy + TABS[k]
    tube('Jack OUT lead %d' % (k + 1), catmull([(px, ex, ez), (px, ex - 1.0, ez - 0.6), (px, yo + 1.6, 5.0), (px - 1.2, yo, 4.6), (jox + 9.0, yo, tz), (jox + 7.25, yo, tz)]), WIRE[col], R30)
for k, col in enumerate([GRN, BLU, BLK]):                      # IN: a vertical U-turn under the plug, north, then a left turn to the west
    px = JA[0] - 4.5 + 4 + k; yo = jiy + TABS[3 - k]
    tube('Jack IN lead %d' % (k + 1), catmull([(px, ex, ez), (px, ex - 1.0, ez - 0.5), (px, ex - 1.6, 5.8), (px, ex - 0.9, 4.5), (px, ex + 1.0, 4.4), (px, yo - 1.4, 4.4), (px - 1.4, yo, 4.4),
         (jix + 9.0, yo, tz), (jix + 7.25, yo, tz)]), WIRE[col], R30)
# 3. J6 → speaker: twisted pair (one twist per 8 mm) east past the codec, then up the corridor beside the display carrier
spx, spy = L['spk']['x'], L['spk']['y']
path = [(JA[0] + 4.0, ex, ez), (JA[0] + 4.0, ex - 1.5, 6.6), (JA[0] + 7.5, 4.0, 5.0), (-131.0, 3.6, 4.4), (-123.5, 6.0, 4.0), (-121.8, 12.0, 3.6), (-121.8, 30.0, 3.6), (spx + 22.8, spy, 4.4),
        (spx + 19.2, spy, PCB_BOT - 0.3 - 4.8 + 1.2)]
c = catmull(path, 0.25); F = frames(c); Ltot = sum((c[j + 1] - c[j]).length for j in range(len(c) - 1))
for k, col in enumerate([RED, BLK]):
    tw, acc = [], 0.0
    for i, p in enumerate(c):
        if i: acc += (p - c[i - 1]).length
        a = 2 * PI * (min(max(acc, 4.0), Ltot - 4.0) - 4.0) / 8.0 + k * PI     # no twist in the first and last 4 mm
        tw.append(p + (F[i][1] * math.cos(a) + F[i][2] * math.sin(a)) * 0.55)
    tube('Speaker twisted pair %d' % (k + 1), tw, WIRE[col], 0.42)
# 4. Battery leads (26 AWG pair) from each cell's tab end to its JST-PH plug (pins 2.0 apart)
for k, ((bx_, by_, sd), (jx, jy)) in enumerate(zip(L['bats'], L['jbat'])):
    md = -sd; tx = bx_ + md * BAT_W / 2; tzb = FLOOR - BAT_POCKET + 0.5 + BAT_T / 2; py_ = jy - 4.5
    pts = [(tx - md * 0.5, by_, tzb), (tx + md * 1.5, by_, tzb + 0.3), (tx + md * 2.5, by_ + 3.0, 5.0), (jx, py_ - 2.0, 5.8), (jx, py_ - 0.6, PCB_BOT - 2.3), (jx, py_, PCB_BOT - 2.3)]
    nm = 'L' if sd < 0 else 'R'
    # heading ±x the horizontal normal is ±y, heading +y it is -x: pin the ends to match
    ends = [((tx - md * 0.5, by_ - md * 1.0, tzb), (jx + 1.0, py_, PCB_BOT - 2.3)), ((tx - md * 0.5, by_ + md * 1.0, tzb), (jx - 1.0, py_, PCB_BOT - 2.3))]
    bundle('Battery lead %s' % nm, pts, [RED, BLK], 2.0, R26, ends=ends)
# 5. J7 → ON/OFF slide switch: south, round the right cell's back corner, to the common and ON pins
swx, swy = L['switch']; SW_Z = 5.6; pin_x = W / 2 - WALL - 4.5 - 3.5
pts = [(JS[0], JSH - 5.3, ez), (JS[0], JSH - 6.5, 6.8), (JS[0] + 3.0, -2.0, 6.2), (153.0, -5.5, 6.0), (157.5, -10.0, 5.8), (157.5, swy + 6.0, SW_Z), (159.0, swy + 1.0, SW_Z), (pin_x + 0.3, swy + 1.0, SW_Z)]
bundle('Power switch lead', pts, [BLK, WHT], 1.05, R30, ends=[((JS[0] - 0.5, JSH - 5.3, ez), (pin_x + 0.3, swy, SW_Z)), ((JS[0] + 0.5, JSH - 5.3, ez), (pin_x + 0.3, swy + 2.0, SW_Z))])
# 6. J8 → VU + mic strip (5V, GND, DIN, MIC, MIC GND), out past the PCB and plate edges
bundle('VU + mic lead', [(J8[0] + 5.3, J8[1], PCB_BOT - 1.45), (J8[0] + 6.3, J8[1], PCB_BOT - 1.4), (vx - 6.6, vy, 11.9), (vx - 5.4, vy, PLATE_TOP + 0.05 - 1.45)], [RED, BLK, BLU, WHT, GRN], 1.0, R30)
# 7. Wi-Fi coax (Ø1.13 mm) from the CM5 U.FL, round the module's left and back edges, to the antenna on the back wall
ux, uy = L['ufl']; uz = PCB_BOT - 4.0 - 1.24 - 1.25
blk('U.FL plug (H04)', ux, uy, uz - 1.05, 2.0, 2.0, 1.05, MM['steel'], cC)
tube('Wi-Fi coax 1.13 (H04)', catmull([(ux, uy, uz - 0.6), (ux - 1.5, uy + 0.5, 2.8), (84.0, 31.0, 2.7), (84.0, 50.0, 2.7), (85.5, 58.6, 2.7), (92.0, 59.8, 2.9), (99.0, 60.2, 4.0), (100.8, D / 2 - WALL - 0.8, 4.6)], 0.4), MM['coax'], 0.565)
result_info = dict(J3=J3)
