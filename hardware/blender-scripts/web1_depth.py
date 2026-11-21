
# Penetration test that works on parts made of many touching pieces: every connected piece is a closed solid,
# and a point is "inside" a part if a ray from it crosses one piece's surface an odd number of times.
from mathutils.bvhtree import BVHTree
from mathutils import Vector
import bmesh
TOL = 0.05
_dg = bpy.context.evaluated_depsgraph_get()
_cache = {}
def _pieces(o):
    if o.name in _cache: return _cache[o.name]
    e = o.evaluated_get(_dg); me = e.to_mesh(); bm = bmesh.new(); bm.from_mesh(me); e.to_mesh_clear(); bm.transform(o.matrix_world)
    bm.verts.ensure_lookup_table(); parent = list(range(len(bm.verts)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for ed in bm.edges:
        a, b = find(ed.verts[0].index), find(ed.verts[1].index)
        if a != b: parent[a] = b
    groups = {}
    for f in bm.faces: groups.setdefault(find(f.verts[0].index), []).append(f)
    pcs, allv = [], [v.co.copy() for v in bm.verts]
    for fs in groups.values():
        idx = sorted({v.index for f in fs for v in f.verts}); remap = {i: k for k, i in enumerate(idx)}
        vs = [bm.verts[i].co.copy() for i in idx]
        t = BVHTree.FromPolygons(vs, [tuple(remap[v.index] for v in f.verts) for f in fs])
        lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
        pcs.append((t, lo, hi))
    bm.free(); _cache[o.name] = (pcs, allv); return _cache[o.name]
def _inside_piece(t, p):
    n, q, d = 0, p.copy(), Vector((0.0123, 0.0071, 1.0)).normalized()
    for _ in range(64):
        hit = t.ray_cast(q, d)
        if hit[0] is None: break
        n += 1; q = hit[0] + d * 1e-4
    return n % 2 == 1
def depth_in(o, p):
    pcs, _ = _pieces(o); best = 0.0
    for (t, lo, hi) in pcs:
        if all(lo[i] - 1e-6 <= p[i] <= hi[i] + 1e-6 for i in range(3)) and _inside_piece(t, p):
            best = max(best, t.find_nearest(p)[3])
    return best
def penetration(a, b):
    worst, cnt = 0.0, 0
    for (x, y) in ((a, b), (b, a)):
        for p in _pieces(x)[1]:
            if abs(p.z) < 1e-4: continue                     # points lying on the case's bottom plane (lathe axis vertices) confuse the inside test
            d = depth_in(y, p)
            if d > TOL: cnt += 1; worst = max(worst, d)
    return cnt, round(worst, 3)
