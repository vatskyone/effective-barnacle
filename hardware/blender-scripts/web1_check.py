
# Interference check: every pair of solids in these groups that touches or intersects, with a location
from mathutils.bvhtree import BVHTree
from mathutils import Vector
dg = bpy.context.evaluated_depsgraph_get()
SHRINK = 0.03
def objs(cname):
    out = []
    def walk(c):
        for o in c.objects:
            if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render and o.name != 'FFC profile': out.append(o)
        for ch in c.children: walk(ch)
    walk(bpy.data.collections[cname]); return out
cache = {}
def tree(o):
    if o.name in cache: return cache[o.name]
    e = o.evaluated_get(dg); me = e.to_mesh()
    # shrink every solid 0.03 mm along its (re-oriented, outward) vertex normals: parts that only touch are not reported, real penetrations are
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me); e.to_mesh_clear()
    bm.transform(o.matrix_world); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
    vs = [v.co - v.normal * SHRINK for v in bm.verts]; fs = [tuple(v.index for v in f.verts) for f in bm.faces]; bm.free()
    if not fs: cache[o.name] = None; return None
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    cache[o.name] = (BVHTree.FromPolygons(vs, fs), lo, hi, vs, fs); return cache[o.name]
def overl(a, b):
    ta, tb = tree(a), tree(b)
    if not ta or not tb or any(ta[2][i] < tb[1][i] or tb[2][i] < ta[1][i] for i in range(3)): return None
    pr = ta[0].overlap(tb[0])
    if not pr: return None
    fa = ta[4][pr[0][0]]; c = sum((ta[3][k] for k in fa), Vector()) / len(fa)
    return len(pr), tuple(round(v, 1) for v in c)
shells = [bpy.data.objects[n] for n in ('Bottom shell L (P01)', 'Bottom shell R (P02)', 'Top frame L (P03)', 'Top frame R (P04)')]
G = {'cables': objs('Cables'), 'elec': objs('Electronics'), 'pcbparts': objs('Main PCB'), 'switches': objs('Switches & sockets'),
     'printed': objs('Printed internals') + shells, 'power': objs('Power & ballast') if 'Power & ballast' in bpy.data.collections else [], 'foam': objs('Foam') if 'Foam' in bpy.data.collections else [], 'fast': objs('Fasteners'), 'plate': objs('Plate'), 'pods': objs('Knob pods') + objs('Tiles'), 'knobs': objs('Knobs'), 'keys': objs('Keycaps')}
PAIRS = [('cables', 'printed'), ('cables', 'switches'), ('cables', 'elec'), ('cables', 'pcbparts'), ('cables', 'fast'), ('cables', 'plate'), ('cables', 'cables'), ('elec', 'printed'), ('elec', 'switches'),
         ('elec', 'pcbparts'), ('elec', 'fast'), ('elec', 'elec'), ('pcbparts', 'printed'), ('pcbparts', 'switches'), ('switches', 'printed'), ('fast', 'switches'), ('fast', 'printed'), ('pcbparts', 'pods'),
         ('pcbparts', 'knobs'), ('fast', 'knobs'), ('fast', 'pods'), ('switches', 'plate'), ('switches', 'keys'), ('pcbparts', 'plate'), ('pods', 'knobs'), ('plate', 'printed'), ('keys', 'printed'), ('keys', 'pods'),
         ('power', 'printed'), ('power', 'elec'), ('power', 'cables'), ('power', 'pcbparts'), ('power', 'switches'), ('power', 'fast'), ('power', 'power'),
         ('foam', 'printed'), ('foam', 'elec'), ('foam', 'cables'), ('foam', 'pcbparts'), ('foam', 'switches'), ('foam', 'fast'), ('foam', 'power'), ('foam', 'plate'), ('foam', 'pods')]
def run(pairs):
    hits = []
    for ga, gb in pairs:
        A, B = G[ga], G[gb]
        for i, a in enumerate(A):
            for j, b in enumerate(B):
                if ga == gb and j <= i: continue
                r = overl(a, b)
                if r: hits.append((a.name, b.name, r[0], r[1]))
    return hits
# run(PAIRS) checks everything; run a few pairs at a time from the Python console if it is slow
