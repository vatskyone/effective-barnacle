
# STEP 5 · Electronics, at datasheet dimensions (CM5 datasheet Fig. 4, Alps EC11E drawing, Kailh CPG135001S30 drawing,
#          Waveshare 43H-800480 panel 105.42 × 67.07 × 2.90, WM8960, BQ25895, LiPo 505060, OS102011, SPH8878)
L = layout(); MM = M_int()
cE, cP, cS, cF = coll('Electronics', 'Internals'), coll('Main PCB', 'Internals'), coll('Switches & sockets', 'Internals'), coll('Fasteners', 'Internals')

# ── Compute Module 5: 55 × 40 × 1.24 mm, built SoC-side up around its centre, then hung SoC-down on 4.0 mm connectors ──
def cm5_part():
    p = Part('Compute Module 5 (H01)', cE, [MM['cm5']])
    o = lambda xd, yd: (xd - 27.5, yd - 20.0)
    holes = [(x, y) for x in (3.5, 51.5) for y in (3.5, 36.5)]
    p.prism([rr(0, 0, 55, 40, 0.8)] + [circ(*o(x, y), 1.35, 20) for (x, y) in holes], 0, 1.24, MM['cm5'])
    for (x, y) in holes:
        for z in (1.24, -0.03): p.prism([circ(*o(x, y), 2.4, 24), circ(*o(x, y), 1.35, 20)], z, 0.03, MM['gold'])
    sx, sy = o(31.9875, 16.975)
    p.box(sx, sy, 1.24, 15, 15, 0.9, MM['chip']).box(sx, sy, 2.14, 13.2, 13.2, 1.06, MM['lid'])       # BCM2712: 2.2 mm with balls
    p.box(*o(14.5, 19.5), 1.24, 10.0, 14.5, 0.95, MM['chip'])                                        # LPDDR4x
    p.box(*o(47.0, 19.5), 1.24, 7.0, 11.5, 0.9, MM['chip'])                                          # eMMC
    p.box(*o(16.0, 32.5), 1.24, 7.0, 6.0, 0.9, MM['chip'])                                           # PMIC
    p.box(*o(11.0, 10.0), 1.24, 9.5, 9.5, 1.3, MM['shield'])                                         # wireless module can (clear of the screw head)
    p.cyl(*o(2.567, 31.0), 1.24, 1.0, 1.25, MM['gold'], 16).box(*o(2.567, 31.0), 1.24, 2.6, 2.6, 0.5, MM['steel'])   # U.FL
    for i in range(60):                                                                                # passives, clear of the mounting-hole keep-outs
        x, y = 6.5 + (i * 7.3) % 42, 5 + (i * 11.7) % 30
        if abs(x - 31.99) < 9 and abs(y - 16.975) < 9: continue
        if any((x - hx) ** 2 + (y - hy) ** 2 < 9.0 for (hx, hy) in holes): continue
        p.box(*o(x, y), 1.24, 1.0, 0.5, 0.5, MM['mlcc'] if i % 3 else MM['chip'])
    for y in (3.0, 37.0):                                                                              # two 100-pin plugs (connector side)
        cx, cy = o(25.0, y); p.box(cx, cy, -1.16, 23.3, 3.1, 1.16, MM['bp'])
        for j in range(50): p.box(cx - 9.8 + j * 0.4, cy, -1.17, 0.18, 2.4, 0.04, MM['gold'])
    return p.build(30)
cm5 = cm5_part(); cm5.location = (CM5_X, CM5_Y, PCB_BOT - 4.0); cm5.rotation_euler = (PI, 0, 0)
for dy in (17.0, -17.0):                                                                                # Amphenol 10164227-1004A1RLF receptacles
    r = Part('CM5 receptacle 10164227-1004 (H27)', cP, [MM['bp']]); r.box(0, 0, -2.84, 25.4, 4.6, 2.84, MM['bp'])
    for j in range(50): r.box(-9.8 + j * 0.4, -2.45, -0.3, 0.2, 0.4, 0.3, MM['gold']).box(-9.8 + j * 0.4, 2.45, -0.3, 0.2, 0.4, 0.3, MM['gold'])
    ob_ = r.build(0); ob_.location = (CM5_X - 2.5, CM5_Y + dy, PCB_BOT)
for x in (3.5, 51.5):
    for y in (3.5, 36.5):
        wx, wy = CM5_X + (x - 27.5), CM5_Y - (y - 20.0)
        s = Part('M2.5 SMT standoff 4 mm (H24)', cF, [MM['brass']]); s.lathe([(1.35, 0), (2.1, 0), (2.1, 4.0), (1.35, 4.0)], 0, 0, -4.0, MM['brass'], 6)
        o_ = s.build(0); o_.location = (wx, wy, PCB_BOT)
        sc_ = Part('M2.5×4 pan screw (H24)', cF, [MM['steel']]); sc_.cyl(0, 0, -1.75, 2.25, 1.75, MM['steel'], 24).cyl(0, 0, 0, 1.25, 4.0, MM['steel'], 12)
        o_ = sc_.build(0); o_.location = (wx, wy, PCB_BOT - 4.0 - 1.24)
socx, socy = L['soc']
hs = Part('Heat spreader 1 mm Al (H02)', cE, [MM['alu']]); hs.prism([rr(0, 0, SPREAD_W, SPREAD_D, 2)], 0, 1.0, MM['alu']); o_ = hs.build(0); o_.location = (socx, socy, 0)
tp = Part('Thermal pad (H02)', cE, [MM['pad']]); tp.box(0, 0, 0, 17, 17, PCB_BOT - 4.0 - 1.24 - 2.2 - 1.0, MM['pad']); o_ = tp.build(0); o_.location = (socx, socy, 1.0)

# ── RP2040 (Pico reference circuit) on the PCB underside ──
blk('RP2040 QFN-56 (H06)', RP_X, RP_Y, PCB_BOT - 0.9, 7.0, 7.0, 0.9, MM['chip'], cP)
blk('W25Q16JV flash (H06)', RP_X - 9.0, RP_Y + 1.5, PCB_BOT - 0.55, 3.0, 2.0, 0.55, MM['chip'], cP)
blk('12 MHz crystal (H06)', RP_X + 8.0, RP_Y - 1.0, PCB_BOT - 0.8, 3.2, 2.5, 0.8, MM['steel'], cP)
blk('3V3 LDO (H06)', RP_X + 8.0, RP_Y + 4.0, PCB_BOT - 1.0, 2.9, 1.6, 1.0, MM['chip'], cP)
blk('BOOTSEL button (H06)', RP_X - 9.0, RP_Y - 4.5, PCB_BOT - 1.5, 4.2, 3.2, 1.5, MM['white'], cP)
for k in range(14): blk('RP2040 decoupling C%d (H06)' % (k + 1), RP_X - 4.6 + (k % 7) * 1.5, RP_Y + (4.6 if k < 7 else -4.6), PCB_BOT - 0.5, 1.0, 0.5, 0.5, MM['mlcc'], cP)

# ── Display: bare panel, cover glass, active area, folded driver FPC with its 15-pin ZIF socket ──
dx, dy = L['disp']
p = Part('4.3in DSI display (H05)', cE, [MM['steel']])
p.prism([rr(0, 0, DISP_W, DISP_H, 0.6)], -DISP_T, DISP_T - 0.7, MM['steel']).prism([rr(0, 0, DISP_W - 0.2, DISP_H - 0.2, 0.4)], -0.7, 0.7, MM['glass'])
p.box(0, DISP_H / 2 - ACT_TOP_BORDER - ACT_H / 2, 0.0, ACT_W, ACT_H, 0.01, MM['chip'])
yb = -DISP_H / 2
p.box(0, yb - 1.2, -1.6, 28, 2.4, 0.12, MM['ffc']).box(0, yb - 2.3, -DISP_T - 1.0, 28, 0.12, 1.6, MM['ffc']).box(0, yb + 13.0, -DISP_T - 0.12, 28, 28, 0.12, MM['ffc'])
for (x, y, w, d, h) in [(-8, -5, 7, 7, 0.9), (4, -2, 3, 2, 0.6), (8, 4, 2, 1.2, 0.5), (-2, 6, 1.6, 0.8, 0.5)]: p.box(x, y, -DISP_T - 0.12 - h, w, d, h, MM['chip'])
p.box(0, yb + 24.0, -DISP_T - 0.12 - 1.2, 19.5, 4.6, 1.2, MM['bp'])
o_ = p.build(30); o_.location = (dx, dy, DISP_TOP)

# ── Audio codec: WM8960 (QFN-32 5 × 5 × 0.9) — line in, headphone/line out, mic in, 1 W class-D speaker driver ──
cx_, cy_ = L['codec']
p = Part('WM8960 audio codec (H16)', cP, [MM['chip']])
p.box(0, 0, -0.9, 5.0, 5.0, 0.9, MM['chip'])
for k in range(12): p.box(-4.6 + (k % 6) * 1.84, (3.9 if k < 6 else -3.9), -0.5, 1.0, 0.5, 0.5, MM['mlcc'])
p.box(-4.0, 0, -1.0, 2.0, 1.25, 1.0, MM['mlcc']).box(4.0, 0, -1.0, 2.0, 1.25, 1.0, MM['mlcc'])        # 10 µF bulk, 0805
o_ = p.build(0); o_.location = (cx_, cy_, PCB_BOT)
# ── Power: BQ25895 charger/boost (QFN-24 4 × 4), 1 µH XAL4020 inductor, MAX17048 fuel gauge, input/output caps ──
px_, py_ = L['pmic']
p = Part('BQ25895 charger + MAX17048 gauge (H30)', cP, [MM['chip']])
p.box(-3.5, 0, -0.8, 4.0, 4.0, 0.8, MM['chip'])                                       # BQ25895
p.box(3.0, 0.5, -2.1, 4.0, 4.0, 2.1, MM['steel'])                                     # XAL4020 1.0 µH
p.box(-3.5, 4.0, -0.6, 2.0, 2.0, 0.6, MM['chip'])                                     # MAX17048 DFN-8
for k in range(8): p.box(-7.0 + k * 1.9, -4.6, -1.0, 1.6, 0.8, 1.0, MM['mlcc'])          # 10 µF 0603/0805 bank
o_ = p.build(0); o_.location = (px_, py_, PCB_BOT)
# charge LED: side-view 0603 (1.6 × 0.8 × 0.6) facing the back wall, under the PCB
lx_, ly_ = L['chg_led']
p = Part('Charge LED side-view (H10)', cP, [MM['white']]); p.box(0, 0, -0.8, 1.6, 1.0, 0.8, MM['white']).box(0, 0.5, -0.75, 1.0, 0.02, 0.6, MM['ledl'])
o_ = p.build(0); o_.location = (lx_, ly_, PCB_BOT)

# ── Five LiPo pouch cells 505060 in parallel (5.0 × 50 × 60 mm, 3.7 V 2000 mAh each, protection board in the tab end), on foam in floor pockets ──
cB = coll('Power & ballast', 'Internals')
BAT_Z = FLOOR - BAT_POCKET + 0.5                                     # 0.5 mm foam under the cell
for k, (bx_, by_, sd) in enumerate(L['bats']):
    p = Part('LiPo 505060 2000 mAh B%d (H31)' % (k + 1), cB, [MM['lipo']])
    md = -sd                                                          # the tab end faces the middle of the case
    p.prism([rr(-md * BAT_TAB / 2, 0, BAT_W - BAT_TAB - 1.6, BAT_D - 1.6, 1.0)], 0, BAT_T, MM['lipo'], 0.8)     # pouch (the 0.8 bevel brings it to 55 × 50)
    p.box(md * (BAT_W / 2 - BAT_TAB / 2), 0, 0.8, BAT_TAB + 0.02, BAT_D - 4, BAT_T - 1.6, MM['kapton'])          # sealed tab edge + PCM under Kapton
    p.box(-md * BAT_TAB / 2, 0, BAT_T, 30, 18, 0.01, MM['silk'])                                               # label
    o_ = p.build(30); o_.location = (bx_, by_, BAT_Z)
    prism('Battery foam under B%d (H33)' % (k + 1), [rr(bx_, by_, BAT_W - 2, BAT_D - 2, 1.5)], FLOOR - BAT_POCKET, 0.5, 0, [MM['foam']], coll('Foam', 'Internals'), 0)
    prism('Battery foam over B%d (H33)' % (k + 1), [rr(bx_ + sd * 3, by_, BAT_W - 10, BAT_D - 6, 1.5)], BAT_Z + BAT_T, 0.5, 0, [MM['foam']], coll('Foam', 'Internals'), 0)

# ── Steel ballast (S235, 4 mm, tapped M3 from below) ──
for st in STEEL:
    o_ = prism(st['name'], [rr((st['x0'] + st['x1']) / 2, (st['y0'] + st['y1']) / 2, st['x1'] - st['x0'] - 0.8, st['y1'] - st['y0'] - 0.8, 1.6)] + [circ(x, y, 1.25, 20) for (x, y) in st['screws']], FLOOR, STEEL_T, 0.4, [MM['steel']], cB, 30)
    for k, (x, y) in enumerate(st['screws']):
        lathe('M3×5 countersunk steel %s %d (H24)' % (st['tag'], k + 1), [(0.001, 0.0), (2.75, 0.0), (1.5, 1.65), (1.5, 5.0), (0.001, 5.0)], x, y, 0.0, [MM['steel']], cF, 32, 40)

# ── MEMS microphone (Knowles SPH8878LR5H-1, bottom port, 3.5 × 2.65 × 0.98) on the underside of the VU strip, port up through the board ──
mx_, my_ = L['mic']
p = Part('MEMS microphone SPH8878 (H32)', coll('Top frame'), [MM['shield']])
p.box(0, 0, -0.98, 3.5, 2.65, 0.73, MM['shield']).box(0, 0, -0.25, 3.5, 2.65, 0.25, MM['chip'])
o_ = p.build(0); o_.location = (mx_, my_, PLATE_TOP + 0.05)
o_ = prism('Mic acoustic gasket (H33)', [rr(mx_, my_, 4.4, 6.0, 0.8), circ(mx_, my_, 1.8, 32)], PLATE_TOP + 0.85, 0.75, 0, [MM['foam']], coll('Foam', 'Internals'), 0)

# ── 3.5 mm stereo jacks (PJ-320D style, 12 × 6 × 5, Ø6 barrel): LINE/PHONES OUT and LINE IN, both on the left wall ──
for (nm, jy_), (jx_, _) in zip(JACKS, L['jacks']):
    p = Part('3.5 mm stereo jack %s (H19)' % nm, cE, [MM['bp']]); p.box(0, 0, 0, 12.0, 6.0, 5.0, MM['bp'])
    for k, dy_ in enumerate((2.25, 0.75, -0.75, -2.25)): p.box(6.6, dy_, 2.0, 1.2, 0.3, 1.0, MM['steel'])     # rear solder tabs (tip, ring, sleeve, switch)
    o_ = p.build(0); o_.location = (jx_, jy_, FLOOR)
    jb = lathe('Jack barrel %s (H19)' % nm, [(1.8, 0), (2.4, 0), (2.4, WALL - 0.4), (1.8, WALL - 0.4)], 0, 0, 0, [MM['bp']], cE, 32, 30)
    jb.location = (-W / 2 + WALL + 0.1, jy_, FLOOR + 2.5); jb.rotation_euler = (0, -PI / 2, 0)

# ── ON/OFF slide switch (C&K OS102011MA1QN1: 8.6 × 4.4 × 4.5 body, 2.0 actuator, 4.0 tall) on the right wall ──
swx, swy = L['switch']; SW_Z = 5.6
p = Part('ON/OFF slide switch OS102011 (H21)', cE, [MM['steel']])
p.box(0, 0, -2.2, 4.5, 8.6, 4.4, MM['steel']).box(4.5 / 2 + 2.0, 1.0, -0.8, 4.0, 2.0, 1.6, MM['bp'])    # actuator in the ON position
for k in range(3): p.box(-4.5 / 2 - 1.75, -2.0 + 2.0 * k, -0.25, 3.5, 0.5, 0.5, MM['steel'])
o_ = p.build(0); o_.location = (W / 2 - WALL - 4.5 / 2, swy, SW_Z)

# ── Slim 40 mm speaker under the grille ──
spx, spy = L['spk']['x'], L['spk']['y']
p = Part('Speaker 40 mm slim (H18)', cE, [MM['cone']])
p.lathe([(0.001, 0.0), (6, 0.2), (14, 1.6), (19.4, 3.8), (20, 4.2), (20, 4.8), (19, 4.8), (12, 2.6), (0.001, 2.2)], 0, 0, 0, MM['cone'], 64)
p.cyl(0, 0, -0.01, 7.0, 1.6, MM['steel'], 32).box(19.2, 0, 1.0, 2.4, 5.0, 1.2, MM['ada'])
o_ = p.build(30); o_.location = (spx, spy, PCB_BOT - 0.3 - 4.8)

# ── EC11E encoders (Alps drawing) with shafts trimmed to sit inside the knobs; M7 nuts on the pod pocket floor ──
SHAFT_TOP = KNOB_BASE + 0.6 + 8.95 - 1.45
def ec11(name):
    p = Part(name, cP, [MM['steel']])
    p.box(0, 0, 0, 11.7, 12.0, 4.5, MM['steel']).cyl(0, 0, 4.5, 3.5, 7.0, MM['brass'], 32).cyl(0, 0, 11.5, 3.0, 24.5 - 10 - 11.5, MM['steel'], 32)
    p.prism([dshape(0, 0)], 24.5 - 10, SHAFT_TOP - PCB_TOP - (24.5 - 10), MM['steel'])
    for x in (-2.5, 0, 2.5): p.box(x, 7.5, -3.5, 0.8, 0.3, 3.5, MM['steel'])
    for x in (-2.5, 2.5): p.box(x, -7.0, -3.5, 0.8, 0.3, 3.5, MM['steel'])
    for x in (-6.25, 6.25): p.box(x, 0, -2.6, 0.3, 1.5, 2.6 + 4.5, MM['steel'])
    return p.build(30)
for i, (x, y) in enumerate(L['enc']):
    e = ec11('EC11E encoder %s (H12)' % ENCS[i][2]); e.location = (x, y, PCB_TOP)
    n = Part('M7 nut %s (H12)' % ENCS[i][2], cF, [MM['steel']]); n.prism([circ(0, 0, 10 / math.sqrt(3), 6), circ(0, 0, 3.5, 32)], 0, 2.0, MM['steel'])
    o_ = n.build(0); o_.location = (x, y, POD_POCKET)
# volume pot (RK09-style, 9.8 × 11 × 6.5 body, M7 × 7 bushing, D shaft): body sizes approximate, check your part
v = L['vol']; POT_SHAFT_TOP = TILE_TOP + VOL_LIFT + 7.5 - 1.0
p = Part('Volume pot 10k (H13)', cP, [MM['bp']])
p.prism([rr(0, 0, 9.8, 11.0, 0.3)], 0, 6.5, MM['bp']).cyl(0, 0, 6.5, 3.5, 7.0, MM['brass'], 32).cyl(0, 0, 13.5, 3.0, (TILE_TOP + 2.4) - PCB_TOP - 13.5, MM['steel'], 32)
p.prism([dshape(0, 0)], (TILE_TOP + 2.4) - PCB_TOP, POT_SHAFT_TOP - (TILE_TOP + 2.4), MM['steel'])
for x in (-2.5, 0, 2.5): p.box(x, 5.0, -3.5, 0.8, 0.3, 3.5, MM['steel'])
o_ = p.build(30); o_.location = (v['x'], v['y'], PCB_TOP)
n = Part('M7 nut volume (H13)', cF, [MM['steel']]); n.prism([circ(0, 0, 10 / math.sqrt(3), 6), circ(0, 0, 3.5, 32)], 0, 2.0, MM['steel']); o_ = n.build(0); o_.location = (v['x'], v['y'], TILE_TOP)

# ── Kailh Choc v2 switch (+ trimmed-pin variant), CPG135001S30 hot-swap socket, SOD-123 diode, SK6812MINI-E ──
under = PLATE_TOP - PLATE_T - PCB_TOP
def choc(name, trimmed=False):
    p = Part(name, cS, [MM['housing']])
    p.prism([rr(0, 0, 13.8, 13.8, 0.4)], 0, under, MM['housing'])
    for s in (-1, 1): p.box(s * 7.05, 0, under - 0.7, 0.4, 4.0, 0.7, MM['housing'])
    p.prism([rr(0, 0, 15, 15, 1.2), rr(0, 0, 6.4, 6.4, 0.8)], under + PLATE_T, CHOC_TOP, MM['housing'], 0.15)
    p.box(0, 5.6, under + PLATE_T + CHOC_TOP - 0.05, 3.4, 2.0, 0.06, MM['ledl'])
    pin_len = PCB_T + 0.8 if trimmed else 3.0
    p.cyl(0, 0, -PCB_T - 1.0, 2.45, PCB_T + 1.0, MM['housing'], 32)
    for (x, y) in ((0, -5.9), (5.0, -3.8)): p.box(x, y, -pin_len, 0.4, 1.2, pin_len, MM['steel'])
    sh = under + PLATE_T + 1.3
    p.prism([rr(0, 0, 5.9, 5.9, 1.2)], under + PLATE_T - 1.0, sh - (under + PLATE_T - 1.0), MM['stem'])
    h_, k_ = 2.0, 0.585
    crossl = [(k_, h_), (-k_, h_), (-k_, k_), (-h_, k_), (-h_, -k_), (-k_, -k_), (-k_, -h_), (k_, -h_), (k_, -k_), (h_, -k_), (h_, k_), (k_, k_)][::-1]
    p.prism([crossl], sh, (CAP_BOT - 0.1) - (PCB_TOP + sh), MM['stem'], 0.05)
    return p.build(30)
def socket():
    p = Part('Choc hot-swap socket (H08)', cS, [MM['pom']])
    p.cyl(0, 0, -1.85, 1.45, 1.85, MM['pom'], 24).cyl(5.0, 2.2, -1.85, 1.45, 1.85, MM['pom'], 24)
    p.box(2.5, 1.1, -1.85, 5.6, 2.6, 1.85, MM['pom'], math.atan2(2.2, 5.0))
    p.box(-2.6, 0, -1.25, 4.0, 4.65, 1.25, MM['pom']).box(7.6, 2.2, -1.25, 4.0, 4.65, 1.25, MM['pom'])
    p.box(-5.6, 0, -0.25, 2.0, 1.8, 0.25, MM['steel']).box(10.6, 2.2, -0.25, 2.0, 1.8, 0.25, MM['steel'])
    return p.build(0)
def diode():
    p = Part('1N4148W SOD-123 (H09)', cP, [MM['chip']])
    p.box(0, 0, 0, 2.7, 1.6, 1.1, MM['chip']).box(-1.65, 0, 0, 0.6, 0.6, 0.15, MM['steel']).box(1.65, 0, 0, 0.6, 0.6, 0.15, MM['steel']).box(-0.95, 0, 1.1, 0.3, 1.6, 0.01, MM['silk'])
    return p.build(0)
def ledp():
    # reverse mount: soldered on the PCB underside, body up inside its cut-out, lens 0.1 mm under the PCB top
    p = Part('SK6812MINI-E (H10)', cP, [MM['white']]); p.box(0, 0, 0.1, 3.2, 2.8, PCB_T - 0.2, MM['white']).cyl(0, 0, PCB_T - 0.15, 1.05, 0.05, MM['ledl'], 20)
    for sx in (-1, 1):
        for sy in (-1, 1): p.box(sx * 2.0, sy * 0.85, -0.1, 0.9, 0.8, 0.1, MM['steel'])
    return p.build(0)
protos = dict(sw=choc('Kailh Choc v2 (H07)'), swt=choc('Kailh Choc v2 trimmed pins (H07)', True), so=socket(), d=diode(), l=ledp())
for o in protos.values():
    for c in list(o.users_collection): c.objects.unlink(o)
for i, (x, y) in enumerate(L['sw']):
    a = bpy.data.objects.new('Choc v2 switch %02d (H07)' % (i + 1), (protos['swt'] if i in L['nosock'] else protos['sw']).data); cS.objects.link(a); a.location = (x, y, PCB_TOP)
    if i not in L['nosock']:
        b = bpy.data.objects.new('Hot-swap socket %02d (H08)' % (i + 1), protos['so'].data); cS.objects.link(b); b.location = (x, y - 5.9, PCB_BOT)
    side = 1 if x + 11.0 < L['pcb']['x1'] - 1 else -1          # in the 5.25 mm gap between switch housings
    d = bpy.data.objects.new('Diode D%02d (H09)' % (i + 1), protos['d'].data); cP.objects.link(d); d.location = (x + side * 9.5, y, PCB_TOP); d.rotation_euler.z = PI / 2
for i, (lx, ly) in enumerate(L['ledpcb']):
    l = bpy.data.objects.new('LED %02d (H10)' % (i + 1), protos['l'].data); cP.objects.link(l); l.location = (lx, ly, PCB_BOT)
for k_, (x, y) in enumerate(L['enc']):
    d = bpy.data.objects.new('Diode D%02d (H09)' % (54 + k_), protos['d'].data); cP.objects.link(d); d.location = (x + 8.4, y + 0.4, PCB_TOP)
for o in protos.values(): bpy.data.objects.remove(o)

# ── USB-C data/charging port (mid-mount, PCB back edge) and the nRPIBOOT button ──
def usbc(name):
    p = Part(name, cP, [MM['steel']])
    p.prism([rr(0, 0, 8.94, 3.26, 1.6), rr(0, 0, 8.34, 2.56, 1.25)], 0, 7.35, MM['steel']).box(0, 0, 1.0, 6.69, 0.7, 5.0, MM['bp'])
    for s in (-1, 1): p.box(s * 5.2, 0, 3.2, 1.2, 0.5, 2.4, MM['steel'])          # shell legs, clear of the 3 mm wall and the PCB edge
    return p.build(0)
for x, nm in ((USBC_X, 'data/charge'),):
    u = usbc('USB-C %s (H20)' % nm); u.location = (x, D / 2 - 0.4, (PCB_TOP + PCB_BOT) / 2); u.rotation_euler = (PI / 2, 0, 0)
def tact(name, c):
    p = Part(name, c, [MM['steel']]); p.box(0, 0, 0, 6, 6, 3.5, MM['steel']).cyl(0, 0, 3.5, 1.75, 1.5, MM['bp'], 24)
    for sx in (-1, 1):
        for sy in (-1, 1): p.box(sx * 3.25, sy * 2.25, 0, 1.0, 0.7, 0.3, MM['steel'])
    return p.build(0)
bb = tact('nRPIBOOT button 6×6 (H21)', cP); bb.location = (L['boot'][0], L['boot'][1], PCB_BOT); bb.rotation_euler = (PI, 0, 0)
result_info = dict(SHAFT_TOP=SHAFT_TOP, POT_SHAFT_TOP=POT_SHAFT_TOP)
