
import numpy as np
cScene = coll('Lights & camera')

# Screen picture: the WEB-1 splash (four coloured waves on black), drawn into an image texture
Wpx, Hpx = 1000, 438
img = bpy.data.images.get('WEB1 screen') or bpy.data.images.new('WEB1 screen', Wpx, Hpx, alpha=False)
px = np.zeros((Hpx, Wpx, 4), np.float32); px[..., :3] = 0.012; px[..., 3] = 1
cols = [(0.25, 0.50, 0.91), (0.18, 0.71, 0.45), (0.96, 0.96, 0.94), (1.0, 0.39, 0.15)]
yy = np.arange(Hpx)[:, None]
for i, c in enumerate(cols):
    xs = np.arange(int(Wpx * 0.19), int(Wpx * 0.81)); u = (xs - xs[0]) / (xs[-1] - xs[0])
    yc = Hpx * 0.48 + np.sin(u * PI * (3 + i * 0.35) + i * 1.3) * Hpx * 0.13 * np.sin(PI * u)
    d = np.abs(yy - yc[None, :]); a = np.clip(2.2 - d, 0, 1)
    for ch in range(3): px[:, xs, ch] = np.maximum(px[:, xs, ch], a * c[ch])
img.pixels.foreach_set(px.ravel()); img.pack()
sm = mat('WEB1 Screen image', '#000000', 0.1, 0.0, 0.6)
nt = sm.node_tree; bsdf = nt.nodes['Principled BSDF']
tex = nt.nodes.get('Screen tex') or nt.nodes.new('ShaderNodeTexImage'); tex.name = 'Screen tex'; tex.image = img; tex.location = (-400, 0)
nt.links.new(tex.outputs['Color'], bsdf.inputs['Emission Color']); bsdf.inputs['Emission Strength'].default_value = 1.6
sc = tile(*SCR)
bpy.ops.mesh.primitive_plane_add(size=1, location=(sc['x'], sc['y'], SCREEN_TOP - 1.0))
pl = bpy.context.active_object; pl.name = 'Screen picture'; pl.scale = (sc['w'] - GAP - 1.6, sc['d'] - GAP - 1.6, 1)
pl.data.materials.append(sm); finish(pl, [], coll('Screen'), 0)
win = bpy.data.objects.get('Screen window (H22)')
if win:   # the window glass becomes a thin clear-coat layer over the picture
    gm = mat('WEB1 Screen glass', '#030304', 0.05, 0.0, 1.0)
    b = gm.node_tree.nodes['Principled BSDF']
    if 'Transmission Weight' in b.inputs: b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1)
    win.location.z = SCREEN_TOP - 0.5; win.scale.z = 0.25
# "WEB-1" title on the screen
bpy.ops.object.text_add(location=(sc['x'], sc['y'] + sc['d'] * 0.3, SCREEN_TOP - 0.95))
tx = bpy.context.active_object; tx.name = 'Screen title'; tx.data.body = 'WEB-1'; tx.data.size = 3.2; tx.data.align_x = 'CENTER'; tx.data.align_y = 'CENTER'
tx.data.materials.append(mat('WEB1 Screen text', '#f4f4ef', 0.5, 0.0, 0.0, 2.0)); finish(tx, [], coll('Screen'), 0)

# Engraving on the right rail: WEB-1 (reading upward) and the signature
rail = mat('WEB1 Engraving', '#7d8081', 0.7)
for body, size, x, y in (('WEB-1', 30 * S * 0.72, X(1181), Y(384)), ('by Snow Bayles - 2026', 7.5 * S * 0.8, X(1205), Y(384.5))):
    bpy.ops.object.text_add(location=(x, y, FRAME_TOP - 0.25), rotation=(0, 0, PI / 2))
    t = bpy.context.active_object; t.name = 'Rail text ' + body.split()[0]; t.data.body = body; t.data.size = size
    t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'; t.data.extrude = 0.15
    t.data.materials.append(rail); finish(t, [], coll('Top frame'), 0)
for (x, y) in ((1184, 24), (1191, 24), (1184, 31), (1191, 31)):
    lathe('Mic hole', [(0.001, -0.6), (2 * S, -0.6), (2 * S, 0.02), (0.001, 0.02)], X(x + 2), Y(y + 2), FRAME_TOP, [mat('WEB1 Grille hole', '#141516', 0.9)], coll('Top frame'), 16, 30)
pipe = mat('WEB1 Light pipe', '#eef4ff', 0.15, 0.0, 0.0, 0.0, 0.6)
for i in range(5):
    lathe('VU light pipe %d (P20)' % (i + 1), [(0.001, -1), (2.5 * S, -1), (2.5 * S, 0.03), (0.001, 0.03)], X(1189.5), Y(64.5 + 14 * i), FRAME_TOP, [pipe], coll('Top frame'), 16, 30)

# Studio: soft key light, fill, rim, a floor that catches shadows, and a 3/4 camera
for o in list(cScene.objects): bpy.data.objects.remove(o)
def light(name, kind, loc, rot, energy, size):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy
    if kind == 'AREA': ld.size = size
    ob = bpy.data.objects.new(name, ld); ob.location = loc; ob.rotation_euler = rot; cScene.objects.link(ob); return ob
light('Key light', 'AREA', (-180, -260, 420), (math.radians(38), 0, math.radians(-30)), 2.2e6, 260)
light('Fill light', 'AREA', (320, -120, 220), (math.radians(60), 0, math.radians(70)), 6e5, 300)
light('Rim light', 'AREA', (60, 380, 260), (math.radians(-55), 0, math.radians(175)), 9e5, 220)
bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, -FEET))
fl = bpy.context.active_object; fl.name = 'Floor'; fl.data.materials.append(mat('WEB1 Floor', '#d9dad6', 0.8)); finish(fl, [], cScene, 0)
cam_d = bpy.data.cameras.new('WEB-1 camera'); cam_d.lens = 70; cam_d.clip_start = 1; cam_d.clip_end = 10000
cam = bpy.data.objects.new('WEB-1 camera', cam_d); cScene.objects.link(cam)
cam.location = (250, -520, 360)
cam.rotation_euler = (Vector((0, 0, 4)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
w = bpy.context.scene.world or bpy.data.worlds.new('World'); bpy.context.scene.world = w
try: w.use_nodes = True
except Exception: pass
bg = w.node_tree.nodes.get('Background')
if bg: bg.inputs['Color'].default_value = lin('#cfd0cc'); bg.inputs['Strength'].default_value = 0.6
r = bpy.context.scene.render; r.resolution_x, r.resolution_y = 1920, 1200
