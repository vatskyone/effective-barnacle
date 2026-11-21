from mathutils import Matrix

import os
SVGDIR = os.path.join(bpy.app.tempdir or '/tmp', 'web1_icons'); os.makedirs(SVGDIR, exist_ok=True)
ICON = {
  'synth': (['M2 12c3-9 6-9 9 0s6 9 9 0'], []), 'drum': ([], [(12, 12, 7), (12, 12, 2)]),
  'tape': (['M7 16h10'], [(7, 12, 4), (17, 12, 4)]), 'mixer': (['M6 4v16M12 4v16M18 4v16M4 9h4M10 15h4M16 7h4'], []),
  'left': (['M14 6l-6 6 6 6'], []), 'right': (['M10 6l6 6-6 6'], []), 'loop': (['M5 13a7 5 0 1 0 7-6M12 4l-3 3 3 3'], []),
  'lift': (['M12 19V6M7 11l5-5 5 5'], []), 'drop': (['M12 5v13M7 13l5 5 5-5'], []), 'seq': (['M3 18h4v-4h4v-4h4V6h6'], []),
  'tempo': (['M8 20l3-16h2l3 16zM12 16l4-6'], []), 'metro': (['M12 8v4l3 2'], [(12, 12, 7)]),
}
FILLED = {'play': 'M8 5l11 7-11 7z', 'stop': 'M7.5 6.5h9a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-9a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1z', 'rec': 'M18 12a6 6 0 1 1-12 0a6 6 0 1 1 12 0z'}
COLOR = {'synth': BLUE, 'drum': GREEN, 'tape': ORANGE, 'seq': GREEN, 'lift': ORANGE, 'drop': ORANGE, 'loop': ORANGE, 'rec': '#e5352b'}
LABEL = {'fx': 'FX', 't0': 'T1', 't1': 'T2', 't2': 'T3', 't3': 'T4', 'shift': 'shift'}
SUB = {'s0': 'BRAKE', 's1': 'STUTTER', 's2': 'REVERSE', 's3': 'SAMPLE'}
cLeg = coll('Legends', 'Keycaps')
KIMP = 0.006773471832275391 / 24          # importer units per SVG px
UNIT = 22 / 24 * S                        # mm per icon viewBox unit (the app draws icons at 22 px)
SCALE = UNIT / KIMP
ZDISH = CAP_TOP - RING_DEPTH              # bottom of the dish
ringm = mat('WEB1 Key ring', '#a3a5a6', 0.6)

def import_icon(name, svg):
    p = os.path.join(SVGDIR, name + '.svg'); open(p, 'w').write(svg)
    before = set(bpy.data.objects.keys()); bpy.ops.import_curve.svg(filepath=p)
    objs = [bpy.data.objects[n] for n in set(bpy.data.objects.keys()) - before]
    for o in objs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
            if c.name.startswith(name) and not c.objects and c.name in bpy.data.collections: bpy.data.collections.remove(c)
        cLeg.objects.link(o)
    return objs

def place(o, cx, cy, z, parent):
    o.scale = (SCALE, SCALE, SCALE)
    o.location = (cx - 12 * UNIT, cy - 12 * UNIT, z)
    o.parent = parent; o.matrix_parent_inverse = Matrix.Translation(-parent.location)

def text(body, size, cx, cy, z, col, parent, name, extrude=0.06):
    bpy.ops.object.text_add(location=(cx, cy, z)); t = bpy.context.active_object
    t.name = name; t.data.body = body; t.data.size = size; t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'; t.data.extrude = extrude
    t.data.materials.append(mat('WEB1 Ink ' + col, col, 0.5)); finish(t, [], cLeg, 0)
    t.parent = parent; t.matrix_parent_inverse = Matrix.Translation(-parent.location); return t

for (a, x, y, w, h) in FKEYS:
    t = tile(x, y, w, h)
    cap = bpy.data.objects['Key %s (%s)' % (a, 'P14' if h > 65 else 'P13')]
    # the ring around the dish
    rg = prism('Key %s ring' % a, [circ(t['x'], t['y'], RING_R + 0.22, 64), circ(t['x'], t['y'], RING_R - 0.22, 64)], CAP_TOP - 0.02, 0.05, 0, [ringm], cLeg, 0)
    rg.parent = cap; rg.matrix_parent_inverse = Matrix.Translation(-cap.location)
    col = COLOR.get(a, INK)
    if a in ICON:
        paths, circles = ICON[a]
        body = ''.join('<path d="%s"/>' % d for d in paths) + ''.join('<circle cx="%g" cy="%g" r="%g"/>' % c for c in circles)
        for o in import_icon('icon_' + a, '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="#000" stroke-width="1.8">%s</g></svg>' % body):
            o.name = 'Key %s icon' % a; cu = o.data
            cu.dimensions = '3D'; cu.fill_mode = 'FULL'; cu.bevel_depth = 0.9 * KIMP; cu.bevel_resolution = 2
            cu.materials.clear(); cu.materials.append(mat('WEB1 Ink ' + col, col, 0.5))
            place(o, t['x'], t['y'], ZDISH + 0.12, cap)
    elif a in FILLED:
        for o in import_icon('icon_' + a, '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="%s" fill="#000"/></svg>' % FILLED[a]):
            o.name = 'Key %s icon' % a; cu = o.data
            cu.dimensions = '2D'; cu.fill_mode = 'BOTH'; cu.extrude = 0.05 / SCALE * 1.0
            cu.materials.clear(); cu.materials.append(mat('WEB1 Ink ' + col, col, 0.5))
            place(o, t['x'], t['y'], ZDISH + 0.1, cap)
    elif a in LABEL:
        if a == 'fx':
            text('FX', 10 * S, t['x'], t['y'] + 3 * S, ZDISH + 0.12, INK, cap, 'Key fx label')
            for i in range(4):
                d = lathe('Key fx dot %d' % i, [(0.001, 0), (2 * S, 0), (2 * S, 0.08), (0.001, 0.08)], t['x'] + (-10.5 + 7 * i) * S, t['y'] - 7 * S, ZDISH + 0.12, [mat('WEB1 FX dot', '#c3c5c6', 0.6)], cLeg, 16, 30)
                d.parent = cap; d.matrix_parent_inverse = Matrix.Translation(-cap.location)
        else:
            text(LABEL[a], 10 * S, t['x'], t['y'], ZDISH + 0.12, INK, cap, 'Key %s label' % a)
    elif a.startswith('s'):
        n = str(int(a[1:]) + 1); sub = SUB.get(a)
        text(n, 19 * S, t['x'], t['y'] + (4 * S if sub else 0), ZDISH + 0.14, INK, cap, 'Key %s number' % a)
        if sub: text(sub, 6 * S, t['x'], t['y'] - 10.5 * S, ZDISH + 0.2, ORANGE, cap, 'Key %s sub-label' % a)
