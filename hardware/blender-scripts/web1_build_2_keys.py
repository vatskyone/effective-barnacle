from mathutils import Matrix

M = dict(key=mat('WEB1 Key white', '#eeefee', 0.48), black=mat('WEB1 Gloss black', '#121213', 0.22, 0.0, 0.6),
         skirt=mat('WEB1 Knob skirt', '#f6f6f4', 0.45), hair=mat('WEB1 Knob hairline', '#8e9091', 0.6),
         pill=mat('WEB1 Pointer pill', '#ffffff', 0.3, 0.0, 0.5), collar=mat('WEB1 Volume collar', '#eceded', 0.45),
         edge=mat('WEB1 Volume edge', '#b4b6b7', 0.5), dotm=mat('WEB1 Volume dot', '#2a2b2d', 0.8),
         case=mat('WEB1 Case', '#c9cbcc', 0.62))
KN = {c: mat('WEB1 Knob ' + n, c, 0.32, 0.0, 0.4) for c, n in ((BLUE, 'blue'), (GREEN, 'green'), (WHITE, 'white'), (ORANGE, 'orange'))}

SOCK_R, CROSS_A, CROSS_T, SOCK_L = 2.75, 4.1, 1.32, 2.8   # MX-style cross socket for the Choc v2 stem
def cross(cx, cy, a=CROSS_A, t=CROSS_T):
    h, k = a / 2, t / 2
    return [(cx + x, cy + y) for x, y in [(k, h), (-k, h), (-k, k), (-h, k), (-h, -k), (-k, -k), (-k, -h), (k, -h), (k, -k), (h, -k), (h, k), (k, k)]][::-1]
def stem_socket(name, cx, cy, parent):
    s = prism(name, [circ(cx, cy, SOCK_R, 40), cross(cx, cy)], CAP_BOT - SOCK_L, SOCK_L + 0.05, 0, [M['key']], cKeys, 0)
    s.parent = parent; s.matrix_parent_inverse = Matrix.Translation(-parent.location); return s

cKeys, cBlack, cPods, cKnobs = coll('Keycaps'), coll('Black-key dishes', 'Keycaps'), coll('Knob pods'), coll('Knobs')

def dish(R, depth, base):   # concave profile, traced bottom → wall → rim → centre so faces point up
    return [(0.001, base), (R, base)] + [(max(0.001, R * i / 12), -depth * (1 - (i / 12) ** 2)) for i in range(12, -1, -1)]

# Function keycaps (P13/P14): rounded cap, concave centre inside the ring
for (a, x, y, w, h) in FKEYS:
    t = tile(x, y, w, h)
    nm = 'Key %s (%s)' % (a, 'P14' if h > 65 else 'P13')
    cap = slab(nm, t['x'], t['y'], t['w'] - GAP, t['d'] - GAP, 7 * S, CAP_BOT, CAP_H, 0.5, [lambda b, t=t: circ(t['x'], t['y'], RING_R + b, 48)], [M['key']], cKeys)
    d = lathe(nm + ' dish', dish(RING_R + 0.05, RING_DEPTH, -(CAP_H - 0.6)), t['x'], t['y'], CAP_TOP, [M['key']], cKeys)
    d.parent = cap; d.matrix_parent_inverse = Matrix.Translation(-cap.location)
    stem_socket(nm + ' stem socket', t['x'], t['y'], cap)

# White keys (P15): pill groove 39 × 112 px
for (x, y, w, h, s) in WKEYS:
    t = tile(x, y, w, h); pw, pd, pz = 39 * S, 112 * S, -(9 - 11) / 2 * S
    cap = slab('White key %02d (P15)' % s, t['x'], t['y'], t['w'] - GAP, t['d'] - GAP, 7 * S, CAP_BOT, CAP_H, 0.5,
               [lambda b, t=t: pill(t['x'], t['y'] + pz, pw + 2 * b, pd + 2 * b)], [M['key']], cKeys)
    fl = prism('White key %02d groove floor' % s, [pill(t['x'], t['y'] + pz, pw + 0.2, pd + 0.2)], CAP_BOT + 0.4, CAP_H - 1.0, 0, [M['key']], cKeys)
    fl.parent = cap; fl.matrix_parent_inverse = Matrix.Translation(-cap.location)
    stem_socket('White key %02d stem socket' % s, t['x'], t['y'], cap)

# Black keys (P16/P17) with a concave glossy black dish (P18) over the note
for (x, y, w, h, cx, s) in BKEYS:
    t = tile(x, y, w, h); rr_ = 20.5 * S + 0.2; nx = X(cx)
    cap = slab('Black key %02d (%s)' % (s, 'P16' if w > 70 else 'P17'), t['x'], t['y'], t['w'] - GAP, t['d'] - GAP, 7 * S, CAP_BOT, CAP_H, 0.5,
               [lambda b, nx=nx, t=t: circ(nx, t['y'], rr_ - 0.05 + b, 48)], [M['key']], cKeys)
    stem_socket('Black key %02d stem socket' % s, nx, t['y'], cap)
    d = lathe('Black key %02d dish (P18)' % s, dish(rr_, RING_DEPTH, -(CAP_H - 0.6)), nx, t['y'], CAP_TOP, [M['black']], cBlack)
    d.parent = cap; d.matrix_parent_inverse = Matrix.Translation(-cap.location)

# Knob pods (P06) with a dish, and the four knobs (P07) with a white pointer pill (P08)
for i, (x, col, nm) in enumerate(ENCS):
    t = tile(x, 20, 132, 146)
    pod = slab('Knob pod %s (P06)' % nm, t['x'], t['y'], t['w'] - GAP, t['d'] - GAP, 8 * S, PLATE_TOP, POD_TOP - PLATE_TOP, 0.5,
               [lambda b, t=t: circ(t['x'], t['y'], 50 * S + b, 64)], [M['key']], cPods)
    dp = lathe('Knob pod %s dish' % nm, [(3.8, PLATE_TOP + 1 - POD_TOP), (50 * S + 0.2, PLATE_TOP + 1 - POD_TOP), (50 * S + 0.2, -0.35), (13.8, -0.8), (12.5, -1.2), (9, -1.45), (3.8, -1.5)], t['x'], t['y'], POD_TOP, [M['key']], cPods, 90)   # overlaps the pod wall by 0.2 mm for a clean union
    dp.parent = pod; dp.matrix_parent_inverse = Matrix.Translation(-pod.location)
    base, r = POD_TOP - 1.4, 31 * S
    knob = lathe('Knob %s (P07)' % nm, [(0.001, 0.6), (r, 0.6), (r, 7.8), (r - 0.25, 8.35), (r - 0.9, 8.7), (r - 2.5, 8.88), (0.001, 8.95)], t['x'], t['y'], base, [KN[col]], cKnobs)
    sk = lathe('Knob %s skirt' % nm, [(0.001, 0), (36 * S, 0), (36 * S, 1.0), (0.001, 1.0)], t['x'], t['y'], base, [M['skirt']], cKnobs, 64, 30)
    hl = lathe('Knob %s hairline' % nm, [(36 * S - 0.1, 0.0), (37.5 * S, 0.0), (37.5 * S, 0.7), (36 * S - 0.1, 0.7)], t['x'], t['y'], base, [M['hair']], cKnobs, 64, 30)
    # pointer pill: a capsule 8 × 24 px, half sunk into the knob top, near the back edge like the app
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1)
    p = bpy.context.active_object; p.name = 'Knob %s pointer (P08)' % nm
    p.scale = (4 * S, 12 * S, 0.55 * 4 * S); p.location = (t['x'], t['y'] + 16 * S, base + 8.85)
    bpy.ops.object.shade_smooth()
    p.data.materials.append(M['pill']); finish(p, [], cKnobs, 0)
    for o in (sk, hl, p): o.parent = knob; o.matrix_parent_inverse = Matrix.Translation(-knob.location)
    knob.rotation_euler.z = [-0.35, 0.6, -0.15, -0.9][i]

# Volume knob (P10) at the app's 67.5°
v = tile(*VOL); base, r = TILE_TOP, 22 * S
vk = lathe('Volume knob (P10)', [(0.001, 0.9), (r, 0.9), (r, 6.5), (r - 0.3, 7.1), (r - 1.2, 7.4), (0.001, 7.5)], v['x'], v['y'], base, [M['key']], cKnobs)
for nm, prof, m in (('collar', [(0.001, 0), (26 * S, 0), (26 * S, 1.0), (0.001, 1.0)], M['collar']), ('edge', [(26 * S - 0.1, 0), (27 * S, 0), (27 * S, 0.8), (26 * S - 0.1, 0.8)], M['edge'])):
    o = lathe('Volume knob ' + nm, prof, v['x'], v['y'], base, [m], cKnobs, 48, 30); o.parent = vk; o.matrix_parent_inverse = Matrix.Translation(-vk.location)
dt = lathe('Volume knob dot', [(0.001, 7.42), (3.5 * S, 7.42), (3.5 * S, 7.6), (0.001, 7.6)], v['x'], v['y'] + 13.5 * S, base, [M['dotm']], cKnobs, 24, 30)
dt.parent = vk; dt.matrix_parent_inverse = Matrix.Translation(-vk.location)
vk.rotation_euler.z = -67.5 * PI / 180
