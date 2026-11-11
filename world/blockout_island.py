"""Block out the whole island of Paxos at low detail: coastline, hills, a marker at every reserved site, and the roads.

This is for judging distances, sight lines and how each group's overview frames. Nothing here is final art.
The south coast uses the same positions as build_world.py, so the finished district drops into this plan unchanged.
Run:  blender -b --factory-startup -P world/blockout_island.py -- --out world/plan
Then: python3 world/label_plan.py world/plan      (writes the site names onto the pictures)
"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector, Matrix, noise
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
OUT = os.path.abspath(opt("--out", os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan")))
random.seed(5); R2 = math.sqrt(2)
bpy.ops.wm.read_factory_settings(use_empty=True); scene = bpy.context.scene; ROOT = scene.collection

# (l, d): l runs across the picture, d towards the viewer. Metres. The viewer looks north-west, so the south coast is at the bottom.
def ld(l, d): return ((l + d) / R2, (l - d) / R2)
def smooth(a, b, v):
    t = min(1, max(0, (v - a) / (b - a))); return t * t * (3 - 2 * t)
def shore(l): return 60 + 18 * math.sin(l * 0.012) + 6 * math.sin(l * 0.04 + 1)       # the south coast, as in build_world.py
def bump(v, at, width): return math.exp(-((v - at) / width) ** 2)
def inland(l, d):
    """Metres from the sea; negative out at sea. Bays cut in and headlands push out; the north is not sea but the edge of the map."""
    n = 26 * noise.noise(Vector((l * .005, d * .005, 9))) + 9 * noise.noise(Vector((l * .018, d * .018, 4)))
    south = shore(l) - .0042 * max(0, abs(l - 40) - 270) ** 2 - d                      # the south coast curls away at both ends
    west = l - (-440 + 45 * math.sin(d * .007) + 95 * bump(d, -330, 75) - 70 * bump(d, -150, 60) - 60 * bump(d, -560, 70))
    east = 520 + 75 * bump(d, -235, 95) - 110 * bump(d, -470, 80) + 55 * bump(d, -650, 70) + 40 * math.sin(d * .006 + 1) - l
    return min(south, d + 1010, west + n, east + n)

HILLS = [(-60, -180, 82, 58), (175, -250, 80, 26), (-225, -110, 60, 16), (-168, -26, 30, 9),      # the four already built
         (60, -335, 60, 30), (435, -235, 55, 14), (345, -570, 95, 36),                            # school hill, east cape, eastern ridge
         (-60, -775, 64, 84), (-205, -842, 78, 74), (85, -842, 78, 74),                           # the ridge the enemy city stands on, at the edge of the map
         (51, -660, 40, 40), (-60, -612, 40, 40), (-171, -660, 40, 40),                           # three spurs that hide the camps from each other,
         (112, -605, 34, 30), (-60, -535, 34, 30), (-232, -605, 34, 30)]                          # each running out past the camps as a ridge
GROUPS = {"merchants": (.70, .30, .16), "legislators": (.16, .30, .62), "scholars": (.20, .50, .30), "soldiers": (.62, .12, .10), "enemy": (.18, .16, .16), "common": (.85, .82, .74)}
SITES = {  # name: (l, d, group, kind)
    "fishery": (-120, 37, "merchants", "house"), "granary": (125, -58, "merchants", "house"), "winery": (-22, -100, "merchants", "house"), "amphora maker": (40, 6, "merchants", "house"),
    "town": (-58, 10, "common", "town"), "temple": (-168, -26, "legislators", "temple"),
    "legislator A": (-268, -50, "legislators", "house"), "legislator B": (214, -8, "legislators", "house"), "legislator C": (-118, -112, "legislators", "house"),
    "proposer P": (62, -142, "legislators", "house"), "proposer Q": (196, -162, "legislators", "house"),
    "town library": (-34, 24, "scholars", "hall"), "cape library": (438, -238, "scholars", "hall"), "hill school": (60, -335, "scholars", "hall"),
    "the enemy city": (-60, -772, "enemy", "city"),
    "commander's camp": (-157, -552, "soldiers", "camp"), "camp A": (37, -552, "soldiers", "camp"), "camp B": (156, -681, "soldiers", "camp"), "camp C": (-276, -681, "soldiers", "camp"),
}
PADS = {"temple": 16, "town": 40, "the enemy city": 1}
def raw(l, d):
    s = inland(l, d)
    if s < 0: return max(-5, .16 * s)
    z = .9 * smooth(0, 14, s) + .012 * min(s, 160)
    for hl, hd, r, hh in HILLS: z += hh * math.exp(-((l - hl) ** 2 + (d - hd) ** 2) / (2 * r * r)) * smooth(0, 30, s)
    return z + min(1, s / 15) * (1.6 * noise.noise(Vector((l * .011, d * .011, 5))) + .5 * noise.noise(Vector((l * .05, d * .05, 0))))
for k, v in SITES.items(): SITES[k] = v + (raw(v[0], v[1]),)
def height(l, d):
    z = raw(l, d)
    for k, (sl, sd, g, kind, sz) in SITES.items():
        r = PADS.get(k, 12); dist = math.hypot(l - sl, d - sd)
        if dist < r * 2: z += (sz - z) * (1 - smooth(r, r * 2, dist))
    return z

def way(a, b, bend=.12):
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / 40)); px, py = -(b[1] - a[1]) / L, (b[0] - a[0]) / L; ph = random.uniform(0, 6)
    return [(a[0] + (b[0] - a[0]) * t + px * bend * L * .5 * math.sin(math.pi * t) * math.sin(2.3 * math.pi * t + ph),
             a[1] + (b[1] - a[1]) * t + py * bend * L * .5 * math.sin(math.pi * t) * math.sin(2.3 * math.pi * t + ph)) for t in [i / n for i in range(n + 1)]]
P = lambda k: SITES[k][:2]
LINKS = [("fishery", "amphora maker"), ("amphora maker", "granary"), ("fishery", "winery"), ("winery", "granary"), ("amphora maker", "winery"), ("fishery", "temple"),
         ("temple", "legislator A"), ("granary", "legislator B"), ("winery", "legislator C"), ("winery", "proposer P"), ("proposer P", "proposer Q"), ("granary", "proposer Q"),
         ("town", "town library"), ("granary", "cape library"), ("proposer Q", "hill school"), ("hill school", "cape library"), ("winery", "hill school"),
         ("legislator C", "commander's camp"), ("hill school", "camp A")]
ROADS = {a + " - " + b: way(P(a), P(b)) for a, b in LINKS}
# messengers between the camps go round the foot of the hill, never over it
ring = [("camp C", "commander's camp", (-292, -552)), ("commander's camp", "camp A", (-60, -462)), ("camp A", "camp B", (172, -552))]
for a, b, via in ring: ROADS[a + " - " + b] = way(P(a), via, .05) + way(via, P(b), .05)[1:]
SEGS = [(r[i], r[i + 1]) for r in ROADS.values() for i in range(len(r) - 1)]
def road_dist(l, d):
    best = 9.0
    for (ax, ay), (bx, by) in SEGS:
        if min(ax, bx) - 9 <= l <= max(ax, bx) + 9 and min(ay, by) - 9 <= d <= max(ay, by) + 9:
            vx, vy = bx - ax, by - ay; t = max(0, min(1, ((l - ax) * vx + (d - ay) * vy) / (vx * vx + vy * vy + 1e-9))); best = min(best, math.hypot(l - ax - t * vx, d - ay - t * vy))
    return best

def flat(name, rgb, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; return m
MAT = {g: flat(g, c) for g, c in GROUPS.items()}; MAT["wall"] = flat("wall", (.88, .84, .74)); MAT["tent"] = flat("tent", (.85, .78, .6))
def obj(bm, name, mat, loc=(0, 0, 0), rot=(0, 0, 0), smooth_shade=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth_shade: me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    o = bpy.data.objects.new(name, me); ROOT.objects.link(o); o.location = loc; o.rotation_euler = rot; me.materials.append(mat); return o
def box(size, loc, mat, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Diagonal((*size, 1))); return obj(bm, "box", mat, loc, rot)
def cone(r, h, loc, mat, seg=12, r2=0.01):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r2, depth=h); return obj(bm, "cone", mat, loc, smooth_shade=seg > 8)
def roofed(x, y, z, w, d, h, group, rot=0.0):
    box((w, d, h + 2), (x, y, z + h / 2 - 1), MAT["wall"], (0, 0, rot))
    bm = bmesh.new(); a = w / 2 + .4; b = d / 2 + .4; v = [bm.verts.new(p) for p in [(-a, -b, 0), (a, -b, 0), (a, b, 0), (-a, b, 0), (-a, 0, h * .45), (a, 0, h * .45)]]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]: bm.faces.new([v[i] for i in f])
    obj(bm, "roof", MAT[group], (x, y, z + h), (0, 0, rot))

# terrain, coloured by height, with roads and sea
N, half = 560, 760.0; cx, cy = ld(40, -390); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=N, y_segments=N, size=half)
col = bm.loops.layers.color.new("col"); vals = {}
for v in bm.verts:
    v.co.x += cx; v.co.y += cy; l, d = (v.co.x + v.co.y) / R2, (v.co.x - v.co.y) / R2; z = height(l, d); v.co.z = z
    if z <= 0: c = (.72, .66, .5)
    else:
        t = smooth(0, 60, z); n = .06 * noise.noise(Vector((l * .03, d * .03, 1))); c = (.56 - .16 * t + n, .58 - .08 * t + n, .30 - .08 * t)
        if z < 1.2: c = (.80, .72, .52)
        if road_dist(l, d) < 2.6: c = (.50, .38, .26)
    vals[v.index] = c
for f in bm.faces:
    for lp in f.loops: lp[col] = (*vals[lp.vert.index], 1)
ground = bpy.data.materials.new("ground"); ground.use_nodes = True; nt = ground.node_tree; at = nt.nodes.new("ShaderNodeVertexColor"); at.layer_name = "col"
nt.links.new(at.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); nt.nodes["Principled BSDF"].inputs["Roughness"].default_value = .95
obj(bm, "terrain", ground, smooth_shade=True)
box((3200, 3200, .2), (cx, cy, -.1), flat("sea", (.05, .30, .42), .2))

# a marker at every site
for name, (l, d, group, kind, z) in SITES.items():
    x, y = ld(l, d)
    if kind == "house": roofed(x, y, z, 9, 6, 3.4, group, .1)
    elif kind == "hall":                                    # a library: a long hall with a porch of columns
        roofed(x, y, z, 20, 9, 5, group)
        for i in range(8): cone(.4, 4.2, (x - 8.4 + i * 2.4, y - 6, z + 2.1), MAT["wall"], 10, .34)
        box((20, 3, .5), (x, y - 5.5, z + 4.4), MAT[group])
    elif kind == "temple":
        box((24, 13, 1.2), (x, y, z + .6), MAT["wall"]); roofed(x, y, z + 6, 22, 11, 1.5, group)
        for i in range(11):
            for sy in (-5, 5): cone(.45, 5.4, (x - 10 + i * 2, y + sy, z + 3.6), MAT["wall"], 10, .38)
    elif kind == "town":
        for i in range(40):
            hx, hy = x + random.uniform(-50, 50), y + random.uniform(-34, 34); hl, hd = (hx + hy) / R2, (hx - hy) / R2
            if inland(hl, hd) > 10 and road_dist(hl, hd) > 4: roofed(hx, hy, height(hl, hd), random.uniform(6, 8), random.uniform(5, 6), 3, "common", random.choice([0, 1.57]))
    elif kind == "city":                                    # only its wall is on the map: a curve along the crest, with towers and one gate
        C = (-60, -1000); R = 240; arc = [(C[0] + R * math.sin(math.radians(a)), C[1] + R * math.cos(math.radians(a))) for a in range(-48, 49, 4)]
        for i, ((l1, d1), (l2, d2)) in enumerate(zip(arc, arc[1:])):
            (x1, y1), (x2, y2) = ld(l1, d1), ld(l2, d2); zt = max(height(l1, d1), height(l2, d2))
            box((math.hypot(x2 - x1, y2 - y1) + .6, 3.5, 50), ((x1 + x2) / 2, (y1 + y2) / 2, zt - 3), MAT["wall"], (0, 0, math.atan2(y2 - y1, x2 - x1)))
            if i % 3 == 0: box((8, 8, 60), (x1, y1, height(l1, d1) - 2), MAT["wall"]); cone(6.2, 5, (x1, y1, height(l1, d1) + 30.5), MAT["enemy"], 4)
        gx, gy = ld(C[0], C[1] + R); gz = height(C[0], C[1] + R); box((13, 10, 64), (gx, gy, gz), MAT["wall"]); box((5.5, 10.4, 9), (gx, gy, gz + 4.5), MAT["enemy"])
        for i in range(70):                                 # roofs just inside, enough to say there is a city
            a = math.radians(random.uniform(-44, 44)); r = R - random.uniform(12, 70); hl, hd = C[0] + r * math.sin(a), C[1] + r * math.cos(a)
            roofed(*ld(hl, hd), height(hl, hd), random.uniform(7, 11), random.uniform(6, 8), random.uniform(4, 9), "enemy", random.uniform(0, 3))
    elif kind == "camp":                                    # tents round a standard
        for i in range(14):
            a = i * 2.4; r = 5 + 2.1 * i ** .75; tx, ty = x + r * math.cos(a), y + r * math.sin(a); cone(2.2, 2.6, (tx, ty, height((tx + ty) / R2, (tx - ty) / R2) + 1.3), MAT["tent"], 6)
        cone(.12, 9, (x, y, z + 4.5), MAT["wall"], 6, .1); box((.1, 2.4, 1.4), (x, y + 1.2, z + 8), MAT["soldiers"])

# sun, sky, camera
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); ROOT.objects.link(sun); sun.data.energy = 4.6; sun.data.angle = math.radians(2)
sun.rotation_euler = Vector((.46, .80, -.50)).normalized().to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True; bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (.55, .70, .95, 1); bg.inputs[1].default_value = 1.1
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); ROOT.objects.link(cam); scene.camera = cam
cam.data.type = "ORTHO"; cam.rotation_euler = (math.radians(60), 0, math.radians(45)); cam.data.clip_end = 6000
scene.render.engine = "CYCLES"; scene.cycles.samples = 40; scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()
    for dev in prefs.devices: dev.use = True
    scene.cycles.device = "GPU"
except Exception as ex: print("GPU not enabled:", ex)
try: scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
VIEWS = {"island": dict(at=(40, -420), scale=1130, aspect=2.1), "merchants": dict(at=(2, -76), scale=455, aspect=2.0), "legislators": dict(at=(30, -80), scale=560, aspect=1.8),
         "scholars": dict(at=(200, -175), scale=780, aspect=1.7), "soldiers": dict(at=(-60, -660), scale=620, aspect=2.14)}
os.makedirs(OUT, exist_ok=True); info = {}
def screen(l, d, z):
    v = world_to_camera_view(scene, cam, Vector((*ld(l, d), z))); return [round(v.x, 4), round(1 - v.y, 4)]
for name, V in VIEWS.items():
    cam.data.ortho_scale = V["scale"]; tx, ty = ld(*V["at"]); cam.location = Vector((tx, ty, 10)) + cam.rotation_euler.to_matrix() @ Vector((0, 0, 2500))
    scene.render.resolution_x, scene.render.resolution_y = 2400, int(2400 / V["aspect"]); bpy.context.view_layer.update()
    info[name] = {"size": [scene.render.resolution_x, scene.render.resolution_y], "metres_across": V["scale"],
                  "sites": {k: {"at": screen(l, d, z + 8), "group": g} for k, (l, d, g, kind, z) in SITES.items()},
                  "roads": {k: [screen(l, d, height(l, d)) for l, d in r] for k, r in ROADS.items()}}
    scene.render.filepath = os.path.join(OUT, name + ".png"); bpy.ops.render.render(write_still=True); print("RENDERED", name)
dist = {a + " - " + b: round(math.hypot(P(a)[0] - P(b)[0], P(a)[1] - P(b)[1])) for a in SITES for b in SITES if a < b and SITES[a][2] == SITES[b][2] and SITES[a][2] not in ("common", "enemy")}
json.dump({"views": info, "groups": GROUPS, "distances_m": dist}, open(os.path.join(OUT, "plan.json"), "w"), indent=1)
