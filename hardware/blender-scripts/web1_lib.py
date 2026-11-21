
import bpy, bmesh, math
from mathutils import Vector

# ── Layout: the desktop app's 1215 × 454 px grid; one key pitch (67 px) = 19.05 mm ──
S = 19.05 / 67
DW, DH = 1215, 454
W, D = DW * S, DH * S
def X(px): return (px - DW / 2) * S
def Y(py): return -(py - DH / 2) * S          # Blender +Y is the back (screen side)
FLOOR, SPLIT, PLATE_TOP, PLATE_T = 2.0, 9.0, 14.0, 1.2      # 2.0 mm floor (1.0 under the battery pockets)
PCB_TOP, PCB_T = 10.6, 1.6
PCB_BOT = PCB_TOP - PCB_T
CHOC_TOP, CHOC_TRAVEL = 0.8, 3.2          # Choc v2 top housing above the plate; total travel 3.2 ± 0.25 mm
CAP_BOT, CAP_H = PLATE_TOP + CHOC_TOP + CHOC_TRAVEL + 0.3, 3.0   # keycap underside clears the housing at full travel
CAP_TOP = CAP_BOT + CAP_H
FRAME_TOP = TILE_TOP = POD_TOP = SCREEN_TOP = CAP_TOP
DISP_TOP, FEET = 7.8, 2.5
WALL, R_CASE, GAP = 3.0, 16 * S, 0.8                 # 3.0 mm walls
RING_R, RING_DEPTH = 24 * S, 0.8
SEAM = 34.0                                   # case halves split here: a gap between two cells, under the green knob pod's left edge
OPEN = dict(x0=X(18), x1=X(1159), y0=Y(436), y1=Y(18), r=8.5 * S)
PI = math.pi

BLUE, GREEN, WHITE, ORANGE, INK = '#3f7fe8', '#2fb673', '#f4f4ef', '#ff6427', '#3a3b3d'
def tile(x, y, w, h): return dict(x=X(x + w / 2), y=Y(y + h / 2), w=w * S, d=h * S)
FKEYS = [
  ('fx', 1092, 20, 65, 72), ('tempo', 154, 94, 65, 72), ('metro', 1092, 94, 65, 72),
  ('synth', 20, 168, 65, 65), ('drum', 87, 168, 65, 65), ('tape', 154, 168, 65, 65), ('mixer', 221, 168, 65, 65),
  ('t0', 288, 168, 65, 65), ('t1', 355, 168, 65, 65), ('t2', 422, 168, 65, 65), ('t3', 489, 168, 65, 65),
] + [('s%d' % i, 556 + 67 * i, 168, 65, 65) for i in range(8)] + [
  ('seq', 1092, 168, 65, 65), ('lift', 20, 235, 65, 65), ('drop', 87, 235, 65, 65), ('loop', 154, 235, 65, 65),
  ('rec', 20, 302, 65, 65), ('play', 87, 302, 65, 65), ('stop', 154, 302, 65, 65),
  ('left', 20, 369, 65, 65), ('right', 87, 369, 65, 65), ('shift', 154, 369, 65, 65)]
WHITE_SEMI = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23]
BLACK_SEMI = [1, 3, 6, 8, 10, 13, 15, 18, 20, 22]
WKEYS = [(221 + 67 * i, 302, 65, 132, s) for i, s in enumerate(WHITE_SEMI)]
_bk = [(0, 98.5, 66), (100.5, 98.5, 32.5), (201, 98.5, 66), (301.5, 65, 32.5), (368.5, 98.5, 32.5), (469, 98.5, 66), (569.5, 98.5, 32.5), (670, 98.5, 66), (770.5, 65, 32.5), (837.5, 98.5, 32.5)]
BKEYS = [(221 + b[0], 235, b[1], 65, 221 + b[0] + b[2], BLACK_SEMI[i]) for i, b in enumerate(_bk)]
ENCS = [(556, BLUE, 'Blue'), (690, GREEN, 'Green'), (824, WHITE, 'White'), (958, ORANGE, 'Orange')]
VOL, SCR, SPK = (154, 20, 65, 72), (221, 20, 333, 146), (20, 20, 132, 146)

# ── Collections and materials ──
def coll(name, parent='WEB-1'):
    root = bpy.data.collections.get('WEB-1')
    if root is None:
        root = bpy.data.collections.new('WEB-1'); bpy.context.scene.collection.children.link(root)
    if name == 'WEB-1': return root
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name); (bpy.data.collections.get(parent) or root).children.link(c)
    return c
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)
def mat(name, col='#ffffff', rough=0.5, metal=0.0, coat=0.0, emit=0.0, trans=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = lin(col)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = lin(col); b.inputs['Emission Strength'].default_value = emit
    if trans and 'Transmission Weight' in b.inputs: b.inputs['Transmission Weight'].default_value = trans
    m.diffuse_color = lin(col); m.roughness = rough
    return m

# ── Geometry helpers (all sizes in mm) ──
def arc(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
def rr(cx, cy, w, d, r, n=8):
    r = max(0.01, min(r, w / 2 - 1e-3, d / 2 - 1e-3))
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
    return (arc(x1 - r, y0 + r, r, -PI / 2, 0, n) + arc(x1 - r, y1 - r, r, 0, PI / 2, n)
            + arc(x0 + r, y1 - r, r, PI / 2, PI, n) + arc(x0 + r, y0 + r, r, PI, 1.5 * PI, n))
def circ(cx, cy, r, n=48): return [(cx + r * math.cos(2 * PI * i / n), cy + r * math.sin(2 * PI * i / n)) for i in range(n)]
def pill(cx, cy, w, d, n=12):   # vertical capsule: w across, d along Y
    r = w / 2
    return arc(cx, cy + d / 2 - r, r, 0, PI, n) + arc(cx, cy - d / 2 + r, r, PI, 2 * PI, n)

def finish(ob, mats, collection, smooth=30):
    me = ob.data
    for m in (mats if isinstance(mats, (list, tuple)) else [mats]):
        me.materials.append(m)
    if smooth and hasattr(me, 'set_sharp_from_angle'):
        for p in me.polygons: p.use_smooth = True
        me.set_sharp_from_angle(angle=math.radians(smooth))
    for c in list(ob.users_collection): c.objects.unlink(ob)
    collection.objects.link(ob)
    return ob

def prism(name, loops, z0, h, bevel=0.0, mats=None, collection=None, smooth=30):
    """Extrude 2D loops (first = outline, rest = holes) from z0 to z0+h, with rounded edges of radius `bevel`."""
    cu = bpy.data.curves.new(name + '_cu', 'CURVE')
    cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = max((h - 2 * bevel) / 2, 1e-4)
    cu.bevel_depth = bevel; cu.bevel_resolution = 3 if bevel > 0 else 0
    for loop in loops:
        sp = cu.splines.new('POLY'); sp.points.add(len(loop) - 1)
        for i, (x, y) in enumerate(loop): sp.points[i].co = (x, y, 0, 1)
        sp.use_cyclic_u = True
    tmp = bpy.data.objects.new('_tmp', cu); bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg)); me.name = name
    bpy.data.objects.remove(tmp); bpy.data.curves.remove(cu)
    bm = bmesh.new(); bm.from_mesh(me)                                  # weld caps to walls: a closed, printable solid
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); ob.location.z = z0 + h / 2
    bpy.context.scene.collection.objects.link(ob)
    return finish(ob, mats or [], collection or bpy.context.scene.collection, smooth)

def slab(name, cx, cy, w, d, r, z0, h, b, holes=(), mats=None, collection=None):
    """Rounded slab with exact outer size; holes are functions of the bevel b that return loops."""
    loops = [rr(cx, cy, w - 2 * b, d - 2 * b, max(r - b, 0.01))] + [f(b) for f in holes]
    return prism(name, loops, z0, h, b, mats, collection)

def lathe(name, prof, cx, cy, z0, mats, collection, seg=64, smooth=40):
    """Revolve a profile [(r, z), ...] around a vertical axis at (cx, cy); z is relative to z0."""
    bm = bmesh.new(); rings = []
    prof = list(prof)
    if (prof[0][0] > 0.01 or prof[-1][0] > 0.01) and tuple(prof[0]) != tuple(prof[-1]):
        prof.append(prof[0])                       # close the profile so ring-shaped solids get their inner wall (manifold)
    for (r, z) in prof:
        if r < 0.01: rings.append([bm.verts.new((0.0, 0.0, z))])     # on the axis: a single pole vertex
        else: rings.append([bm.verts.new((r * math.cos(2 * PI * i / seg), r * math.sin(2 * PI * i / seg), z)) for i in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            q = [a[i % len(a)], a[j % len(a)], b[j % len(b)], b[i % len(b)]]
            q = [v for k, v in enumerate(q) if v not in q[:k]]
            if len(q) >= 3:
                try: bm.faces.new(q)
                except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); ob.location = (cx, cy, z0)
    bpy.context.scene.collection.objects.link(ob)
    return finish(ob, mats, collection, smooth)

def box(name, cx, cy, cz, w, d, h, mats, collection, bevel=0.0):
    return slab(name, cx, cy, w, d, max(bevel, 0.01) if bevel else 0.01, cz - h / 2, h, bevel, (), mats, collection) if bevel else \
        prism(name, [rr(cx, cy, w, d, 0.01, 1)], cz - h / 2, h, 0, mats, collection, 0)

def half(o, inn, side, n=8):
    """C-shaped half of a rounded-rectangle ring (inn=None → solid half). side -1 = left of SEAM, +1 = right."""
    xs, R = SEAM, o['r']; pts = []
    if side < 0:
        pts += [(xs, o['y1'])] + arc(o['x0'] + R, o['y1'] - R, R, PI / 2, PI, n) + arc(o['x0'] + R, o['y0'] + R, R, PI, 1.5 * PI, n) + [(xs, o['y0'])]
        if inn:
            r = inn['r']
            pts += [(xs, inn['y0'])] + arc(inn['x0'] + r, inn['y0'] + r, r, 1.5 * PI, PI, n) + arc(inn['x0'] + r, inn['y1'] - r, r, PI, PI / 2, n) + [(xs, inn['y1'])]
    else:
        pts += [(xs, o['y0'])] + arc(o['x1'] - R, o['y0'] + R, R, -PI / 2, 0, n) + arc(o['x1'] - R, o['y1'] - R, R, 0, PI / 2, n) + [(xs, o['y1'])]
        if inn:
            r = inn['r']
            pts += [(xs, inn['y1'])] + arc(inn['x1'] - r, inn['y1'] - r, r, PI / 2, 0, n) + arc(inn['x1'] - r, inn['y0'] + r, r, 0, -PI / 2, n) + [(xs, inn['y0'])]
    return pts

OUT = dict(x0=-W / 2, x1=W / 2, y0=-D / 2, y1=D / 2, r=R_CASE)
INNER = dict(x0=-W / 2 + WALL, x1=W / 2 - WALL, y0=-D / 2 + WALL, y1=D / 2 - WALL, r=R_CASE - WALL)


# ── Internal layout (shared by the build steps) ──
CM5_X, CM5_Y = 113.0, 38.0          # under the knob pods: the only socket-free area large enough
DISP_W, DISP_H, DISP_T = 105.42, 67.07, 2.90
ACT_W, ACT_H, ACT_TOP_BORDER = 95.04, 53.86, 3.0
SOC_DX, SOC_DY = 31.9875 - 27.5, -(16.975 - 20.0)
SPREAD_W, SPREAD_D, WIN_W, WIN_D = 56.0, 40.0, 50.0, 34.0
RP_X, RP_Y = 22.0, -28.8
FB, FF = D / 2 - 3.4, -(D / 2 - 3.4)
FRAME_SCREWS = [(-125.0, FB), (-3.0, FB), (39.5, FB), (159.0, FB), (-102.0, FF), (-34.0, FF), (102.0, FF), (163.0, 14.0)]   # front screws sit in the battery gaps
POD_POCKET = POD_TOP - 1.8
KNOB_BASE = POD_TOP - 1.4
VOL_LIFT = 0.3
# battery: five 3.7 V LiPo pouch cells 505060 (5.0 × 50 × 60 mm, 2000 mAh / 7.4 Wh each, with PCM) in parallel = 10 Ah, 37 Wh,
# in a row across the front under the keys. Power budget ≈ 5.3 W at 5 V (CM5 + Chromium 3.5, display 0.9, LEDs 0.3, audio 0.4, rest 0.2)
# → 5.8 W from the cells through the 92 % boost → about 6 h; 4.5 h flat out, 7 h+ with the screen dimmed.
BAT_T, BAT_W, BAT_D, BAT_TAB = 5.0, 60.0, 50.0, 5.0
BAT_POCKET = 1.0                    # floor is 1.0 mm thick under each cell (pocket 1.0 deep)
BAT_Y = -33.5                       # pockets run y -58.9 … -8.1: clear of the front frame bosses (gaps) and of the display carrier
GAPS = [-102.0, -34.0, 34.0, 102.0] # 7.2 mm between pockets: PCB posts, frame bosses, battery leads and the case seam live here
# centre x, y, side; the tab end faces -side (md = -side): every tab faces a gap
BATS = [(-136.0, BAT_Y, -1), (-68.0, BAT_Y, 1), (0.0, BAT_Y, 1), (68.0, BAT_Y, 1), (136.0, BAT_Y, 1)]
BAT_LEAD = [(-103.5, -1), (-100.5, 1), (-34.0, 0), (34.0, 0), (102.0, 0)]     # lead x in its gap, pad side (pads BT1-BT5 on the PCB underside)
# steel ballast (laser-cut S235, tapped M3, screwed from below); the front bar also ties the two shell halves together
STEEL_T = 4.0
# the cells now carry the weight up front; one steel plate stays at the back, spanning the seam (screws on both halves)
STEEL = [dict(name='Steel ballast back (H29)', tag='back', x0=-4.0, x1=78.0, y0=22.0, y1=56.0, screws=[(0.0, 26.0), (0.0, 52.0), (74.0, 26.0), (74.0, 52.0)])]
SEAM_PLATE = (34.0, 4.0, 26.0, 12.0)                     # printed seam joiner (P05) behind the cells: x, y, w, d; one M3 from below on each side
JACKS = [('OUT', 0.0), ('IN', 12.0)]                    # both on the left wall, between the left cell and the speaker
SWITCH_Y = 0.0                                          # ON/OFF slide switch on the right wall, behind the battery row
USBC_X = 60.0
def _find(L, ax, ay, hw, hh, R, rad=60.0, step=0.5, tall=False):
    P, sc = L['pcb'], L['sc']; best = None; n = int(rad / step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            px, py = ax + i * step, ay + j * step
            if not (P['x0'] + 2 < px - hw and px + hw < P['x1'] - 2 and P['y0'] + 2 < py - hh and py + hh < P['y1'] - 2): continue
            if abs(px - sc['x']) < sc['w'] / 2 + hw + 0.5 and abs(py - sc['y']) < sc['d'] / 2 + hh + 0.5: continue
            if any(x0 - hw < px < x1 + hw and y0 - hh < py < y1 + hh for (x0, y0, x1, y1) in R): continue
            d = (px - ax) ** 2 + (py - ay) ** 2
            if best is None or d < best[0]: best = (d, px, py)
    if not best: raise ValueError('no free spot near %s' % ((ax, ay),))
    return (best[1], best[2])
_LAYOUT = {}
def layout():
    if _LAYOUT: return dict(_LAYOUT)
    sc, spk, vol = tile(*SCR), tile(*SPK), tile(*VOL)
    L = dict(sc=sc, spk=spk, vol=vol)
    L['disp'] = (sc['x'], D / 2 - WALL - 0.3 - DISP_H / 2)
    L['soc'] = (CM5_X + SOC_DX, CM5_Y + SOC_DY)
    L['ufl'] = (CM5_X + (2.567 - 27.5), CM5_Y - (31.0 - 20.0))
    L['jack'] = (-W / 2 + WALL + 6.1, JACKS[0][1])
    L['jacks'] = [(-W / 2 + WALL + 6.1, y) for (_, y) in JACKS]
    L['switch'] = (W / 2 - WALL - 4.4, SWITCH_Y)
    L['boot'] = (84.0, 13.0)
    sw = [tile(*k[1:]) for k in FKEYS] + [tile(*k[:4]) for k in WKEYS] + [dict(x=X(k[4]), y=Y(k[1] + k[3] / 2)) for k in BKEYS]
    L['sw'] = [(s['x'], s['y']) for s in sw]
    L['enc'] = [(tile(e[0], 20, 132, 146)['x'], tile(e[0], 20, 132, 146)['y']) for e in ENCS]
    L['led'] = []
    for i, k in enumerate(FKEYS):
        t = tile(*k[1:]); x, y = L['sw'][i]
        L['led'].append((x + min(7.9, t['w'] / 2 - 1.1), y + (t['d'] / 2 - 2.0)))
    L['ledpcb'] = [(x, y + 5.0) for (x, y) in L['sw'][:len(FKEYS)]]
    L['pcb'] = dict(x0=OPEN['x0'] + 1, x1=OPEN['x1'] - 1, y0=OPEN['y0'] + 1, y1=OPEN['y1'] - 1)
    L['jvu'] = (L['pcb']['x1'] - 3.4, Y(92))
    L['mic'] = (X(1189.5) - 0.4, Y(29.5))                # under the 2 × 2 mic holes
    dx, dy = L['disp']
    cx0, cx1 = dx - (DISP_W / 2 + 2.2) - 0.3, dx + (DISP_W / 2 + 2.2) + 0.3
    cy0, cy1 = dy - (DISP_H / 2 + 2.2) - 0.3, dy + (DISP_H / 2 + 2.2) + 0.3
    L['nosock'] = [i for i, (x, y) in enumerate(L['sw']) if not (x + 11.6 < cx0 or x - 6.6 > cx1 or y - 1.5 < cy0 or y - 8.3 > cy1)]
    L['bats'] = [(x, y, s) for (x, y, s) in BATS]
    # things on the PCB underside must avoid: sockets, switch posts, LEDs, CM5, encoders, pot, display, speaker, RP2040, USB-C;
    # tall headers (JST) must also avoid the batteries and the steel (their tops are under the headers' bottoms)
    R = []
    for i, (x, y) in enumerate(L['sw']):
        if i not in L['nosock']: R.append((x - 6.9, y - 8.5, x + 11.9, y - 1.2))
        R.append((x - 2.9, y - 2.9, x + 2.9, y + 2.9))
    for (x, y) in L['ledpcb']: R.append((x - 2.2, y - 2.0, x + 2.2, y + 2.0))
    R += [(CM5_X - 29, CM5_Y - 22, CM5_X + 29, CM5_Y + 22), (RP_X - 12, RP_Y - 6.5, RP_X + 12, RP_Y + 6.5), (USBC_X - 7, D / 2 - 12, USBC_X + 7, D / 2)]
    for (x, y) in L['enc']: R.append((x - 7.5, y - 9.0, x + 7.5, y + 9.0))
    R.append((vol['x'] - 6, vol['y'] - 7, vol['x'] + 6, vol['y'] + 7))
    R.append((cx0, cy0 - 6, cx1, cy1)); R.append((spk['x'] - 23, spk['y'] - 23, spk['x'] + 23, spk['y'] + 23))
    for (x, y) in FRAME_SCREWS: R.append((x - 4, y - 4, x + 4, y + 4))
    tall = list(R)
    for (x, y, s) in L['bats']: tall.append((x - BAT_W / 2 - 0.6, y - BAT_D / 2 - 1.8, x + BAT_W / 2 + 0.6, y + BAT_D / 2 + 1.8))
    for st in STEEL: tall.append((st['x0'] - 1.5, st['y0'] - 1.5, st['x1'] + 1.5, st['y1'] + 1.5))
    tall.append((L['boot'][0] - 4, L['boot'][1] - 4, L['boot'][0] + 4, L['boot'][1] + 4))
    L['codec'] = _find(L, -115.0, 14.0, 6.0, 5.0, R)                     # WM8960 + passives (QFN-32, 5 × 5)
    R.append((L['codec'][0] - 6.5, L['codec'][1] - 5.5, L['codec'][0] + 6.5, L['codec'][1] + 5.5))
    L['pmic'] = _find(L, 40.0, 30.0, 8.0, 6.0, R)                        # BQ25895 + 1 µH inductor + MAX17048 + caps
    R.append((L['pmic'][0] - 8.5, L['pmic'][1] - 6.5, L['pmic'][0] + 8.5, L['pmic'][1] + 6.5))
    tall += [(L['codec'][0] - 6.5, L['codec'][1] - 5.5, L['codec'][0] + 6.5, L['codec'][1] + 5.5), (L['pmic'][0] - 8.5, L['pmic'][1] - 6.5, L['pmic'][0] + 8.5, L['pmic'][1] + 6.5)]
    # side-entry connectors under the PCB: the search box covers the header and its mated plug (plug toward -y)
    L['jaud'] = _find(L, -150.0, 6.0, 6.3, 3.8, tall)                     # JST-SH 10p: both jacks + speaker
    tall.append((L['jaud'][0] - 7.0, L['jaud'][1] - 4.5, L['jaud'][0] + 7.0, L['jaud'][1] + 4.5))
    # battery solder pads BT1-BT5 (2 × 2 mm each, 2 mm apart) on the PCB underside, right above each lead's gap
    L['batpads'] = []
    for (lx0, side), (bx, by, sd) in zip(BAT_LEAD, L['bats']):
        best = None
        for j in range(0, 90):
            for py in (by + 0.5 * j, by - 0.5 * j):
                for lx in ((lx0,) if side else (lx0, lx0 - 1.5, lx0 + 1.5, lx0 - 2.4, lx0 + 2.4)):
                    if not (-56.0 < py < -12.0): continue
                    if any(x0 - 1.3 < lx < x1 + 1.3 and y0 - 2.2 < py < y1 + 2.2 for (x0, y0, x1, y1) in R): continue
                    if side and any(abs(py - q[1]) < 3.0 and abs(lx - q[0]) < 2.6 for q in L['batpads']): continue
                    best = (lx, py); break
                if best: break
            if best: break
        if best is None: raise ValueError('no pad spot for the cell at %s' % bx)
        L['batpads'].append(best)
    L['jsw'] = _find(L, 150.0, 8.0, 2.3, 3.8, tall)                       # JST-SH 2p: slide switch
    tall.append((L['jsw'][0] - 3.0, L['jsw'][1] - 4.5, L['jsw'][0] + 3.0, L['jsw'][1] + 4.5))
    # display link: the FFC leaves the panel's ZIF, runs under the panel and out of the carrier's right side at y ffc_y, then up into J3
    dxl, dyl = L['disp']; L['ffc_y'] = dyl - DISP_H / 2 + 24.0 - 12.0; L['car_x1'] = dxl + (DISP_W + 0.4) / 2 + 2.0
    L['j3'] = _find(L, L['car_x1'] + 16.0, L['ffc_y'] - 8.0, 8.2, 2.8, tall)
    tall.append((L['j3'][0] - 8.5, L['j3'][1] - 3.0, L['j3'][0] + 8.5, L['j3'][1] + 3.0))
    L['chg_led'] = (USBC_X + 9.0, L['pcb']['y1'] - 1.6)                 # charge LED beside the USB-C port, light pipe through the back wall
    L['tall'] = tall; L['R'] = R
    _LAYOUT.update(L); return dict(L)

# ── Modelling tools shared by the internal build steps ──
from mathutils import Matrix
SC = bpy.context.scene.collection
class Part:
    """Collects many simple solids into one mesh object with several materials."""
    def __init__(self, name, collection, mats):
        self.name, self.c, self.mats, self.bm = name, collection, list(mats), bmesh.new()
    def _mi(self, m):
        if m not in self.mats: self.mats.append(m)
        return self.mats.index(m)
    def _tag(self, verts, m):
        mi = self._mi(m)
        for f in {f for v in verts for f in v.link_faces}: f.material_index = mi
    def box(self, x, y, z0, w, d, h, m, rz=0.0):
        vs = bmesh.ops.create_cube(self.bm, size=1)['verts']; c, s = math.cos(rz), math.sin(rz)
        for v in vs:
            px, py = v.co.x * w, v.co.y * d
            v.co = Vector((x + px * c - py * s, y + px * s + py * c, z0 + h / 2 + v.co.z * h))
        self._tag(vs, m); return self
    def cyl(self, x, y, z0, r, h, m, seg=24):
        vs = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=h, matrix=Matrix.Translation((x, y, z0 + h / 2)))['verts']
        self._tag(vs, m); return self
    def ob(self, o, m=None):
        me = o.data.copy(); me.transform(o.matrix_basis if o.parent is None else o.matrix_world)   # matrix_basis is current even before a depsgraph update
        mi = self._mi(m) if m is not None else None
        remap = [self._mi(s.material) for s in o.material_slots] or [0]
        for p in me.polygons: p.material_index = mi if mi is not None else remap[min(p.material_index, len(remap) - 1)]
        self.bm.from_mesh(me); bpy.data.meshes.remove(me); bpy.data.objects.remove(o); return self
    def prism(self, loops, z0, h, m, bevel=0.0):
        o = prism('_tmp', loops, z0, h, bevel, [m], SC, 0); return self.ob(o, m)
    def lathe(self, prof, x, y, z0, m, seg=32):
        o = lathe('_tmp', prof, x, y, z0, [m], SC, seg, 0); return self.ob(o, m)
    def build(self, smooth=35):
        me = bpy.data.meshes.new(self.name); self.bm.to_mesh(me); self.bm.free()
        ob = bpy.data.objects.new(self.name, me); SC.objects.link(ob)
        return finish(ob, self.mats, self.c, smooth)
def tmp(loops, z0, h): return prism('_cut', loops, z0, h, 0, [], SC, 0)
def tcyl(x, y, z0, r, h, seg=32): return tmp([circ(x, y, r, seg)], z0, h)
def union_all(name, objs, collection=None, mats=()):
    """Manifold union of several solids (for printed parts made of pieces)."""
    base = objs[0]
    for o in objs[1:]: boolean(base, o, 'UNION')
    base.name = name
    if collection is not None:
        for c in list(base.users_collection): c.objects.unlink(base)
        collection.objects.link(base)
    for m in mats: base.data.materials.append(m)
    return base
def merge(name, objs, collection=None, mats=()):
    bm = bmesh.new()
    for o in objs:
        me = o.data.copy(); me.transform(o.matrix_basis if o.parent is None else o.matrix_world); bm.from_mesh(me); bpy.data.meshes.remove(me); bpy.data.objects.remove(o)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); (collection or SC).objects.link(o)
    for m in mats: me.materials.append(m)
    return o
def _islands(o):
    """Split a mesh object into one object per connected piece (each piece is a closed solid)."""
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); parent = list(range(len(bm.verts)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b: parent[a] = b
    groups = {}
    for f in bm.faces: groups.setdefault(find(f.verts[0].index), []).append(f)
    out = []
    if len(groups) <= 1: bm.free(); return [o]
    for fs in groups.values():
        nb = bmesh.new(); vmap = {}
        for f in fs:
            vs = []
            for v in f.verts:
                if v.index not in vmap: vmap[v.index] = nb.verts.new(v.co)
                vs.append(vmap[v.index])
            try: nb.faces.new(vs)
            except ValueError: pass
        me = bpy.data.meshes.new('_piece'); nb.to_mesh(me); nb.free()
        p = bpy.data.objects.new('_piece', me); p.matrix_world = o.matrix_basis.copy(); out.append(p)
    bm.free(); bpy.data.objects.remove(o); return out
def boolean(target, other, op='DIFFERENCE'):
    """Exact boolean. A cutter made of several overlapping pieces is applied as a collection operand, so no membranes are left behind."""
    parts = _islands(other)
    m = target.modifiers.new('bool', 'BOOLEAN'); m.operation = op; m.solver = 'EXACT'; m.use_hole_tolerant = True
    if len(parts) == 1:
        SC.objects.link(parts[0]) if not parts[0].users_collection else None
        m.object = parts[0]; m.use_self = True
    else:
        col = bpy.data.collections.new('_ops'); SC.children.link(col)
        for p in parts: col.objects.link(p)
        m.operand_type = 'COLLECTION'; m.collection = col
    bpy.context.view_layer.update()
    with bpy.context.temp_override(object=target, active_object=target, selected_objects=[target]): bpy.ops.object.modifier_apply(modifier=m.name)
    for p in parts: bpy.data.objects.remove(p)
    if len(parts) > 1: bpy.data.collections.remove(col)
def through(x, y, z, r, length, axis, seg=32):
    o = tcyl(0, 0, -length / 2, r, length, seg); o.location = (x, y, z)
    o.rotation_euler = (PI / 2, 0, 0) if axis == 'Y' else (0, PI / 2, 0); return o
def through_rr(x, y, z, w, h, r, length):
    o = tmp([rr(0, 0, w, h, r)], -length / 2, length); o.location = (x, y, z); o.rotation_euler = (PI / 2, 0, 0); return o
def blk(name, x, y, z0, w, d, h, m, c, rz=0.0):
    o = prism(name, [rr(0, 0, w, d, 0.15, 1)], z0, h, 0, [m], c, 0); o.location.x, o.location.y = x, y; o.rotation_euler.z = rz; return o
def dshape(x, y, r=3.0, flat=1.5, n=48):
    return [(x + r * math.cos(a), y + r * math.sin(a)) for a in [k * 2 * PI / n for k in range(n)] if r * math.sin(a) <= flat + 1e-6]
def M_int():
    return dict(
      pcb=mat('WEB1 PCB green', '#1d5a3a', 0.55), cm5=mat('WEB1 CM5 PCB', '#0e5a34', 0.5), ada=mat('WEB1 Adafruit PCB', '#1c1c1e', 0.5),
      gold=mat('WEB1 ENIG gold', '#d6aa52', 0.3, 1.0), steel=mat('WEB1 Steel', '#b9bcc0', 0.35, 1.0), brass=mat('WEB1 Brass', '#c9a54a', 0.35, 1.0),
      chip=mat('WEB1 Chip black', '#1a1b1d', 0.45), lid=mat('WEB1 SoC lid', '#c4c6c8', 0.3, 1.0), nylon=mat('WEB1 JST natural', '#ece4d2', 0.6),
      bp=mat('WEB1 Black plastic', '#202124', 0.55), housing=mat('WEB1 Choc housing', '#2e2f33', 0.4), stem=mat('WEB1 Choc stem red', '#d8342c', 0.4),
      pom=mat('WEB1 Socket white', '#efece4', 0.55), ffc=mat('WEB1 FFC', '#c88a2c', 0.4), glass=mat('WEB1 Panel glass', '#05070a', 0.08, 0.0, 1.0),
      ledl=mat('WEB1 LED lens', '#f4f4f0', 0.2), mlcc=mat('WEB1 MLCC', '#a88a6a', 0.5), silk=mat('WEB1 Silkscreen', '#f1f1e8', 0.6),
      cone=mat('WEB1 Speaker cone', '#2a2a2c', 0.85), alu=mat('WEB1 Aluminium', '#c8cacc', 0.35, 1.0), pad=mat('WEB1 Thermal pad', '#8a96a8', 0.9),
      shield=mat('WEB1 RF shield', '#d0d2d4', 0.25, 1.0), white=mat('WEB1 Tact white', '#f0efe9', 0.5), plate=mat('WEB1 Plate black', '#0b0b0c', 0.55),
      shell=mat('WEB1 Case', '#c9cbcc', 0.62), shellin=mat('WEB1 Case inside', '#b8babb', 0.7), key=mat('WEB1 Key white', '#eeefee', 0.48),
      pb=mat('WEB1 Print black', '#1b1c1e', 0.75), pipe=mat('WEB1 Light pipe', '#eef4ff', 0.15, 0.0, 0.0, 0.0, 0.6), coax=mat('WEB1 Coax', '#8c8e90', 0.5),
      ant=mat('WEB1 Antenna flex', '#2a2620', 0.6), foam=mat('WEB1 Foam', '#2a2b2d', 1.0),
      lipo=mat('WEB1 LiPo pouch', '#b7b9bd', 0.35, 0.8), kapton=mat('WEB1 Kapton', '#c9861e', 0.35, 0.0, 0.0, 0.0, 0.2))
