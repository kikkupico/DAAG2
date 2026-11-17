"""The fixed stage for a world built in Blender: the page's camera, the network's roads as meshes, and the check that every
road can be seen. Import it from your own world script; it builds nothing of the world itself.

    import sys; sys.path.insert(0, "tools")
    import blender_stage as stage
    net = stage.network("allegories/<id>/city.json")       # units must be "m": plan units, x east, y north, z up
    stage.camera(width=2400)                                # the page's camera, 4:3; never move, turn or rescale it
    guides = stage.roads(net)                               # a ribbon along every path, as a guide for test renders
    ... build the ground, the landmarks at net["places"][k]["at"], everything else ...
    stage.check(net)                                        # prints every stretch of path the camera cannot see
    for g in guides: bpy.data.objects.remove(g)             # a path need not be a road in the world: leave walkable ground
    stage.render("allegories/<id>/city.png")

Run:  blender -b --factory-startup -P your_world.py

The frame shows a square of ground 304 units on a side, standing on its corner: north at the upper right corner (0, 215),
east at the lower right (215, 0), south at the lower left (0, -215), west at the upper left (-215, 0). Tall things lean
toward the top of the picture, so nothing tall may stand just south-east of a road: it would hide the messengers on it.
Heights: the ground under a road must be at the road's own z, since the page draws the messenger at the projection of
[x, y, z]. If your land decides the heights, write them back into the network file before `tools/allegory.py build`."""
import bpy, json, math
from mathutils import Vector

W, H = 1600, 1200
R2 = math.sqrt(2); SPAN = 215 * R2; ELEV = math.asin(.75)
TOWARD = Vector((math.cos(ELEV) / R2, -math.cos(ELEV) / R2, math.sin(ELEV)))      # from the world to the camera

def network(path):
    net = json.load(open(path))
    if net.get("units") != "m": raise SystemExit('%s: a world built in Blender needs "units": "m"' % path)
    return net

def camera(width=2400, scene=None):
    """The page's camera: orthographic, from the south-east, asin(0.75) above the horizon, the frame 304 units wide."""
    scene = scene or bpy.context.scene
    cam = bpy.data.objects.new("stage camera", bpy.data.cameras.new("stage camera")); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.type = "ORTHO"; cam.data.ortho_scale = SPAN; cam.data.sensor_fit = "HORIZONTAL"; cam.data.clip_start = 100; cam.data.clip_end = 6000
    cam.location = TOWARD * 2500; cam.rotation_euler = (-TOWARD).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x = width; scene.render.resolution_y = round(width * H / W); scene.render.resolution_percentage = 100
    return cam

def project(x, y, z=0.0):
    """Where a world point lands in the picture, in its 1600 x 1200 pixels (the same sum as tools/allegory.py's m2px)."""
    return (W / 2 + (W / SPAN) * (x + y) / R2, H / 2 - (W / SPAN) * (.75 * (y - x) / R2 + math.cos(ELEV) * z))

def roads(net, material=None, lift=.03, widths=None, scene=None):
    """One mesh ribbon along every road of the network, `lift` above the heights the file gives. widths: {kind: width} to
    replace the file's own. Returns the objects. They are guides for test renders: a path need not be a road in the world,
    only clear ground a person could walk, so remove them (or restyle them into whatever the setting has there) at the end."""
    scene = scene or bpy.context.scene; out = []
    for i, r in enumerate(net["roads"]):
        P = [Vector((p[0], p[1], (p[2] if len(p) > 2 else 0) + lift)) for p in r["pts"]]; w = (widths or {}).get(r["kind"], r.get("width", 5)) / 2
        V, F = [], []
        for j, p in enumerate(P):
            a, b = P[max(0, j - 1)], P[min(len(P) - 1, j + 1)]; d = Vector((b.x - a.x, b.y - a.y, 0))
            n = Vector((-d.y, d.x, 0)).normalized() if d.length > 1e-9 else Vector((1, 0, 0))
            V += [p + n * w, p - n * w]
            if j: k = 2 * j; F.append((k - 2, k - 1, k + 1, k))
        me = bpy.data.meshes.new("road %d" % i); me.from_pydata([tuple(v) for v in V], [], F); me.update()
        ob = bpy.data.objects.new("road %d %s" % (i, r["kind"]), me); scene.collection.objects.link(ob)
        if material: me.materials.append(material)
        out.append(ob)
    return out

def check(net, step=3.0, scene=None):
    """Walks every road and asks, every `step` units, whether the camera sees a messenger standing there. Prints what hides
    each hidden stretch; returns the hidden points. A few hidden points behind a low wall are fine; a hidden stretch is not."""
    scene = scene or bpy.context.scene; bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); hidden, n = [], 0
    for r in net["roads"]:
        P = [(p[0], p[1], p[2] if len(p) > 2 else 0) for p in r["pts"]]
        for a, b in zip(P, P[1:]):
            m = max(1, int(math.dist(a[:2], b[:2]) / step))
            for j in range(m + 1):
                p = Vector([a[k] + (b[k] - a[k]) * j / m for k in range(3)]) + Vector((0, 0, .9)); u, v = project(p.x, p.y, p.z)
                if not (0 <= u <= W and 0 <= v <= H): continue
                n += 1; hit, loc, _, _, ob, _ = scene.ray_cast(dg, p + TOWARD * 500, -TOWARD)
                if hit and (loc - p).length > 1.6: hidden.append((round(p.x, 1), round(p.y, 1), ob.name))
    by = {}
    for h in hidden: by[h[2]] = by.get(h[2], 0) + 1
    print("ROAD CHECK: %d points in the frame, %d hidden from the camera" % (n, len(hidden)))
    for name, c in sorted(by.items(), key=lambda kv: -kv[1])[:15]: print("  hidden by %-30s %d" % (name, c))
    return hidden

def render(path, scene=None):
    scene = scene or bpy.context.scene; scene.render.image_settings.file_format = "PNG"; scene.render.filepath = path
    bpy.ops.render.render(write_still=True); print("WROTE", path)
