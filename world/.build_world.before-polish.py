"""Build and render the trading side of Paxos: the fishery on the harbour, the granary among its wheat fields,
the winery on its terraced hill, and the amphora maker at the crossroads between them.

Everything is placed by this script, so the world is reproducible and every measure is a parameter.
Run:  blender -b --factory-startup --disable-autoexec -P world/build_world.py -- --out world/render [--width 6000] [--samples 160] [--views overview,fishery]
Writes one picture per view, and world.json saying where each place and road lands in each picture.
"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector, Matrix, noise
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
OUT = os.path.abspath(opt("--out", os.path.join(HERE, "render")))
WIDTH, SAMPLES = int(opt("--width", 6000)), int(opt("--samples", 160))
random.seed(11)
R2 = math.sqrt(2)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
ROOT = scene.collection

# ---------------------------------------------------------------- layout
# Positions are given as (l, d): l runs across the picture, d towards the viewer and the sea. Distances are metres.
def ld(l, d): return ((l + d) / R2, (l - d) / R2)
def to_ld(x, y): return ((x + y) / R2, (x - y) / R2)
def smooth(a, b, v):
    t = min(1, max(0, (v - a) / (b - a))); return t * t * (3 - 2 * t)
def shore(l): return 60 + 18 * math.sin(l * 0.012) + 6 * math.sin(l * 0.04 + 1)
def bump(v, at, width): return math.exp(-((v - at) / width) ** 2)
def inland(l, d):
    """Metres from the sea, negative out at sea: the outline of blockout_island.py. Near the harbour it is just the south coast."""
    south = shore(l) - .0042 * max(0, abs(l - 40) - 270) ** 2 - d
    if abs(l) < 300 and d > -250: return south
    n = 26 * noise.noise(Vector((l * .005, d * .005, 9))) + 9 * noise.noise(Vector((l * .018, d * .018, 4)))
    west = l - (-440 + 45 * math.sin(d * .007) + 95 * bump(d, -330, 75) - 70 * bump(d, -150, 60) - 60 * bump(d, -560, 70))
    east = 520 + 75 * bump(d, -235, 95) - 110 * bump(d, -470, 80) + 55 * bump(d, -650, 70) + 40 * math.sin(d * .006 + 1) - l
    return min(south, d + 1010, west + n, east + n)

HILLS = [(-60, -180, 82, 58), (175, -250, 80, 26), (-225, -110, 60, 16), (-168, -26, 30, 9), (60, -335, 60, 30), (435, -235, 55, 14), (345, -570, 95, 36),
         (-60, -762, 64, 84), (-204, -808, 78, 74), (84, -808, 78, 74),                          # the ridge the enemy city stands on
         (51, -660, 40, 40), (-60, -612, 40, 40), (-171, -660, 40, 40), (112, -605, 34, 30), (-60, -535, 34, 30), (-232, -605, 34, 30)]   # ridges that hide the camps from each other     # centre l, centre d, spread, height
def plot(l, d, hx, hy):                                                      # a plot centred at (l, d), square to the buildings
    x, y = ld(l, d); return (x - hx, x + hx, y - hy, y + hy)
VINEYARD = plot(-24, -62, 36, 30)
FIELDS = [plot(84, -84, 26, 22), plot(170, -92, 24, 28), plot(96, -14, 30, 16), plot(158, -30, 20, 18), plot(44, -40, 14, 20)]
def box_edge(x, y, b): return min(x - b[0], b[1] - x, y - b[2], b[3] - y)    # metres inside the plot; negative outside

def raw_height(x, y):
    l, d = to_ld(x, y); s = inland(l, d)                      # metres inland; negative is out at sea
    if s < 0: return max(-5.0, 0.16 * s)
    z = 0.9 * smooth(0, 14, s) + 0.012 * s
    for hl, hd, r, hh in HILLS: z += hh * math.exp(-((l - hl) ** 2 + (d - hd) ** 2) / (2 * r * r)) * smooth(0, 30, s)
    z += min(1, s / 15) * (1.3 * noise.noise(Vector((x * .011, y * .011, 5))) + .5 * noise.noise(Vector((x * .05, y * .05, 0))) + .2 * noise.noise(Vector((x * .14, y * .14, 3))))
    e = box_edge(x, y, VINEYARD)
    if e > 0: z += (math.floor(z / 1.5) * 1.5 + .2 - z) * smooth(0, 5, e)        # terraces
    return z

FL = -120; FD = shore(FL) - 9
PLACES = {  # name: centre (l, d), footprint (x size, y size), wall height, turn in degrees
    "fishery": dict(at=(FL, FD), size=(9, 5.5), h=3.0, rot=8),
    "granary": dict(at=(125, -58), size=(7.5, 7), h=5.2, rot=-6),
    "winery": dict(at=(-22, -100), size=(11, 6), h=3.3, rot=4),
    "potter": dict(at=(40, 6), size=(6, 4.6), h=2.8, rot=-12),
}
PADS = []
for name, p in PLACES.items():
    p["xy"] = ld(*p["at"]); p["z"] = raw_height(*p["xy"]) + 0.15
    PADS.append((p["xy"][0], p["xy"][1], max(p["size"]) * 0.75, p["z"]))
THRESH = ld(125 + 10.5, -58 - 2.5); PADS.append((*THRESH, 4.2, raw_height(*THRESH) + 0.1))
YARD = ld(FL - 2, FD + 5.5); PADS.append((*YARD, 5.5, max(0.5, raw_height(*YARD))))
TEMPLE = ld(-168, -26); TEMPLE_Z = raw_height(*TEMPLE) + .2; PADS.append((*TEMPLE, 17, TEMPLE_Z))        # on its own rise, above the harbour
LIBS = {"town library": ld(-34, 24), "hill school": ld(60, -335), "cape library": ld(438, -238)}     # the scholars' three, a long walk apart
LIB_Z = {k: raw_height(*v) + .2 for k, v in LIBS.items()}
for k, v in LIBS.items(): PADS.append((*v, 15, LIB_Z[k]))
def lib_door(k): return (LIBS[k][0], LIBS[k][1] - 9.5)
CAMPS = {"commander's camp": ld(-157, -552), "camp A": ld(37, -552), "camp B": ld(156, -681), "camp C": ld(-276, -681)}     # the besiegers, each in its own valley
CAMP_Z = {k: raw_height(*v) + .1 for k, v in CAMPS.items()}
for k, v in CAMPS.items(): PADS.append((*v, 17, CAMP_Z[k]))
CITY_C = (-60, -1000); CITY_R = 240       # the enemy city's wall is an arc of this circle; only the arc is on the map
TOWN = plot(-58, 10, 62, 42); AGORA = plot(-58, 10, 11, 9)                                          # a grid of streets by the harbour

def height(x, y):
    z = raw_height(x, y)
    for px, py, r, pz in PADS:
        dist = math.hypot(x - px, y - py)
        b = 6 + r * .7                                  # blend width: wide pads on slopes need a gentler apron
        if dist < r + b: z = z + (pz - z) * (1 - smooth(r, r + b, dist))
    return z

def door(name, off=1.6):   # a point just outside the front door, which is on the -y wall
    p = PLACES[name]; a = math.radians(p["rot"]); dy = p["size"][1] / 2 + off
    return (p["xy"][0] + math.sin(a) * dy, p["xy"][1] - math.cos(a) * dy)

HOMES = {"legislator A": (-268, -50), "legislator B": (214, -8), "legislator C": (-118, -112), "proposer P": (62, -142), "proposer Q": (196, -162)}   # legislators work from home
def home(name): x, y = ld(*HOMES[name]); return (x, y - 7.5)                    # a point in front of a legislator's door
QL = FL + 11; QD = shore(QL) + 3.5; QUAY = ld(QL, QD)
def q(l, d): return ld(l + QL + 3, d + QD - 16.5)        # the quay's own frame
def way(a, b, bend=0.14):
    """A winding road from a to b: a point every 30 metres or so, pushed sideways a little."""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / 30)); px, py = -(b[1] - a[1]) / L, (b[0] - a[0]) / L; ph = random.uniform(0, 6)
    return [(a[0] + (b[0] - a[0]) * t + px * bend * L * .5 * math.sin(math.pi * t) * math.sin(2.3 * math.pi * t + ph),
             a[1] + (b[1] - a[1]) * t + py * bend * L * .5 * math.sin(math.pi * t) * math.sin(2.3 * math.pi * t + ph)) for t in [i / n for i in range(n + 1)]]
def via(a, pts, b):                      # a path through given (l, d) points, gently winding between them
    pts = [a] + [ld(*p) for p in pts] + [b]; out = [a]
    for p, q in zip(pts, pts[1:]): out += way(p, q, .04)[1:]
    return out
ROADS = [way(door("fishery"), door("potter")), way(door("potter"), door("granary")), way(door("fishery"), door("winery"), .2), way(door("winery"), door("granary"), .1),
         way(door("potter"), door("winery")), [door("fishery"), ld(FL + 5, FD + 6), ld(QL - 2, QD - 3)], way(door("fishery"), (TEMPLE[0] + 17, TEMPLE[1] - 1), .1),
         way((TEMPLE[0] + 17, TEMPLE[1] - 1), home("legislator A"), .1), way(door("granary"), home("legislator B")), way(door("winery"), home("legislator C")),
         way(door("winery"), home("proposer P")), way(home("proposer P"), home("proposer Q")), way(door("granary"), home("proposer Q")),
         way(lib_door("town library"), door("potter"), .05), way(door("granary"), lib_door("cape library")), way(home("proposer Q"), lib_door("hill school")),
         way(lib_door("hill school"), lib_door("cape library")), way(door("winery"), lib_door("hill school")),
         # messengers between camps go round the foot of each ridge, never over it
         way(CAMPS["camp C"], ld(-292, -552), .05) + way(ld(-292, -552), CAMPS["commander's camp"], .05)[1:], way(CAMPS["commander's camp"], ld(-60, -462), .05) + way(ld(-60, -462), CAMPS["camp A"], .05)[1:],
         way(CAMPS["camp A"], ld(172, -552), .05) + way(ld(172, -552), CAMPS["camp B"], .05)[1:], way(home("legislator C"), CAMPS["commander's camp"]), way(lib_door("hill school"), CAMPS["camp A"]),
         via(CAMPS["commander's camp"], [(-112, -478), (-60, -438), (72, -458), (198, -578)], CAMPS["camp B"]), via(CAMPS["camp A"], [(-8, -478), (-60, -438), (-192, -458), (-318, -578)], CAMPS["camp C"]),
         via(CAMPS["camp B"], [(212, -556), (160, -428), (-60, -398), (-280, -428), (-332, -556)], CAMPS["camp C"])]
ROAD_NAMES = ["fishery-potter", "potter-granary", "fishery-winery", "winery-granary", "potter-winery", "fishery-quay", "fishery-temple", "temple-legislator A",
              "granary-legislator B", "winery-legislator C", "winery-proposer P", "proposer P-proposer Q", "granary-proposer Q",
              "town library-potter", "granary-cape library", "proposer Q-hill school", "hill school-cape library", "winery-hill school",
              "camp C-commander's camp", "commander's camp-camp A", "camp A-camp B", "legislator C-commander's camp", "hill school-camp A",
              "commander's camp-camp B", "camp A-camp C", "camp B-camp C"]
SEGS = [(r[i], r[i + 1], min(r[i][0], r[i + 1][0]) - 6, max(r[i][0], r[i + 1][0]) + 6, min(r[i][1], r[i + 1][1]) - 6, max(r[i][1], r[i + 1][1]) + 6) for r in ROADS for i in range(len(r) - 1)]

def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p; vx, vy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy + 1e-9)))
    return math.hypot(px - ax - t * vx, py - ay - t * vy)
def road_dist(x, y):      # distance to the nearest road, or 6 if none is that close
    best = 6.0
    for a, b, x0, x1, y0, y1 in SEGS:
        if x0 <= x <= x1 and y0 <= y <= y1: best = min(best, seg_dist((x, y), a, b))
    return best

# ---------------------------------------------------------------- materials
IMAGES = {}
def image(path, label):
    if path not in IMAGES: IMAGES[path] = bpy.data.images.load(path); IMAGES[path].name = label
    return IMAGES[path]

def tex_nodes(nt, name, coord, scale, bump=1.0):
    """Colour, roughness and normal sockets for one downloaded texture, box-projected at real-world size."""
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / scale,) * 3; nt.links.new(coord, mp.inputs["Vector"])
    out = {}
    for key, cs in (("Diffuse", "sRGB"), ("Rough", "Non-Color"), ("nor_gl", "Non-Color")):
        path = os.path.join(ASSETS, name, key + ".jpg")
        if not os.path.exists(path): continue
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = image(path, name + "_" + key); n.image.colorspace_settings.name = cs
        n.projection = "BOX"; n.projection_blend = 0.25; nt.links.new(mp.outputs["Vector"], n.inputs["Vector"]); out[key] = n.outputs["Color"]
    if "nor_gl" in out:
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump; nt.links.new(out["nor_gl"], nm.inputs["Color"]); out["nor_gl"] = nm.outputs["Normal"]
    return out

def bsdf_from(nt, t, tint=None):
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = t["Diffuse"]
    if tint:
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1
        nt.links.new(col, mx.inputs[6]); mx.inputs[7].default_value = (*tint, 1); col = mx.outputs[2]
    nt.links.new(col, b.inputs["Base Color"])
    if "Rough" in t: nt.links.new(t["Rough"], b.inputs["Roughness"])
    if "nor_gl" in t: nt.links.new(t["nor_gl"], b.inputs["Normal"])
    return b

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
    return m, nt, next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")

def pbr(name, tex, scale, tint=None, bump=1.0):
    m, nt, out = new_mat(name); tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(bsdf_from(nt, tex_nodes(nt, tex, tc.outputs["Object"], scale, bump), tint).outputs[0], out.inputs["Surface"]); return m

def flat(name, rgb, rough=0.8, bump=0.0):
    m, nt, out = new_mat(name); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 18; nz.inputs["Detail"].default_value = 6
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs["Surface"]); return m

def terrain_mat():
    m, nt, out = new_mat("terrain"); tc = nt.nodes.new("ShaderNodeTexCoord"); co = tc.outputs["Object"]
    sand = bsdf_from(nt, tex_nodes(nt, "coast_sand_01", co, 3.0)); dry = bsdf_from(nt, tex_nodes(nt, "dry_ground_rocks", co, 3.5), (1.25, 1.12, .92))
    green = bsdf_from(nt, tex_nodes(nt, "aerial_grass_rock", co, 6.0), (1.05, 1.1, .8)); rock = bsdf_from(nt, tex_nodes(nt, "rocky_terrain_02", co, 5.0), (1.0, .95, .82))
    path = bsdf_from(nt, tex_nodes(nt, "stony_dirt_path", co, 2.6), (1.45, 1.3, 1.05))
    def attr(n):
        a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = n; return a.outputs["Fac"]
    def mix(f, a, b):
        x = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(f, x.inputs[0]); nt.links.new(a.outputs[0], x.inputs[1]); nt.links.new(b.outputs[0], x.inputs[2]); return x
    wheat = nt.nodes.new("ShaderNodeBsdfPrincipled"); wheat.inputs["Roughness"].default_value = .85
    wm = nt.nodes.new("ShaderNodeMapping"); wm.inputs["Rotation"].default_value = (0, 0, math.pi / 4); nt.links.new(co, wm.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 2.4; wv.inputs["Distortion"].default_value = 1.2; nt.links.new(wm.outputs[0], wv.inputs["Vector"])
    wc = nt.nodes.new("ShaderNodeMix"); wc.data_type = "RGBA"; wc.inputs[6].default_value = (.62, .40, .07, 1); wc.inputs[7].default_value = (.40, .24, .035, 1)
    wb = nt.nodes.new("ShaderNodeBump"); wb.inputs["Strength"].default_value = .7; wb.inputs["Distance"].default_value = .3
    nt.links.new(wv.outputs[1], wc.inputs[0]); nt.links.new(wc.outputs[2], wheat.inputs["Base Color"]); nt.links.new(wv.outputs[1], wb.inputs["Height"]); nt.links.new(wb.outputs[0], wheat.inputs["Normal"])
    s = mix(attr("grass"), sand, dry); s = mix(attr("green"), s, green); s = mix(attr("rock"), s, rock); s = mix(attr("wheat"), s, wheat); s = mix(attr("road"), s, path)
    nt.links.new(s.outputs[0], out.inputs["Surface"]); return m

def water_mat():
    m, nt, out = new_mat("water"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (.75, .95, .95, 1); b.inputs["Roughness"].default_value = 0.06; b.inputs["IOR"].default_value = 1.33
    b.inputs["Transmission Weight"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 6
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.05; bp.inputs["Distance"].default_value = 0.6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0]); nt.links.new(b.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption"); vol.inputs["Color"].default_value = (.10, .62, .70, 1); vol.inputs["Density"].default_value = 0.55
    nt.links.new(mx.outputs[0], out.inputs["Surface"]); nt.links.new(vol.outputs[0], out.inputs["Volume"]); return m

MAT = dict(
    plaster=pbr("plaster", "white_rough_plaster", 2.4, (1.2, 1.17, 1.1)), ochre=pbr("ochre", "yellow_plaster", 2.4, (1.5, 1.25, .9)),
    worn=pbr("worn", "white_stucco_02", 2.0, (1.15, 1.08, .98)), tiles=pbr("tiles", "clay_roof_tiles", 1.7, (1.15, .95, .85), 2.0),
    stone=pbr("stone", "medieval_blocks_05", 2.0, (1.0, .97, .9)), rubble=pbr("rubble", "medieval_blocks_05", 1.6, (.95, .9, .82)),
    wood=pbr("wood", "brown_planks_09", 1.4, (.9, .78, .62)), darkwood=pbr("darkwood", "brown_planks_09", 1.4, (.5, .4, .32)),
    hessian=pbr("hessian", "hessian_230", 0.5, (1.0, .9, .7)), thatch=pbr("thatch", "thatch_roof_angled", 1.8, (2.3, 1.95, 1.4), 2.0),
    marble=pbr("marble", "marble_01", 2.6, (1.08, 1.03, .95)), blue=flat("blue", (.05, .16, .5), .5), red=flat("red", (.55, .08, .06), .5),
    clay=flat("clay", (.60, .27, .14), .7, .15), fish=flat("fish", (.55, .56, .56), .35), dark=flat("dark", (.03, .025, .02), 1.0),
    rope=flat("rope", (.55, .45, .3), .9, .3), grain=flat("grain", (.78, .62, .28), .9, .4))

# ---------------------------------------------------------------- geometry helpers
def obj_from(bm, name, mat, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), smooth_shade=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth_shade: me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    o = bpy.data.objects.new(name, me); ROOT.objects.link(o); o.location = loc; o.rotation_euler = rot
    if mat: me.materials.append(mat)
    if parent: o.parent = parent
    return o

def box(name, size, loc, mat, parent=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((*size, 1)))
    return obj_from(bm, name, mat, parent, loc, rot)

def cyl(name, r, h, loc, mat, parent=None, rot=(0, 0, 0), seg=20, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    return obj_from(bm, name, mat, parent, loc, rot, True)

def prism(name, pts, depth, loc, mat, parent=None, rot=(0, 0, 0)):
    """A profile in the x-z plane, extruded along y."""
    bm = bmesh.new(); a = [bm.verts.new((x, -depth / 2, z)) for x, z in pts]; b = [bm.verts.new((x, depth / 2, z)) for x, z in pts]
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(len(pts)): bm.faces.new([a[i], b[i], b[(i + 1) % len(pts)], a[(i + 1) % len(pts)]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return obj_from(bm, name, mat, parent, loc, rot)

def empty(name, loc, rot_z=0.0, parent=None):
    e = bpy.data.objects.new(name, None); ROOT.objects.link(e); e.location = loc; e.rotation_euler.z = rot_z; e.parent = parent; return e

def cut(wall, size, loc, parent):
    c = box("cutter", size, loc, None, parent); c.hide_render = True; c.display_type = "WIRE"
    m = wall.modifiers.new("cut", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = c; m.solver = "EXACT"

def gable_roof(root, w, d, h, pitch, mat, over=0.55, thick=0.16, ridge=True):
    """Two sloping slabs over a w by d box whose walls stop at height h. The ridge runs along x."""
    rise = math.tan(pitch) * d / 2; run = d / 2 + over; L = run / math.cos(pitch)
    for s in (-1, 1):
        yc = s * run / 2; zc = h + rise - math.tan(pitch) * run / 2 + thick / 2
        box("roof", (w + 2 * over, L, thick), (0, yc, zc), mat, root, (-s * pitch, 0, 0))
        n = int(w / 0.9)
        for i in range(n + 1):   # rafter ends under the eaves
            box("rafter", (.1, .5, .12), (-w / 2 + i * w / n, s * (d / 2 + over * .45), h - .02 - math.tan(pitch) * over * .45), MAT["darkwood"], root, (-s * pitch, 0, 0))
    if ridge:
        n = int((w + 2 * over) / 0.42)
        for i in range(n): cyl("ridge", .13, .44, (-(w + 2 * over) / 2 + .22 + i * .42, 0, h + rise + thick * .9), mat, root, (0, math.pi / 2, 0), 10, .11)
    return rise

def building(name, wall="plaster", pitch=24, plinth=0.45, windows=2, door_w=1.3, door_h=2.1, high_windows=False):
    p = PLACES[name] if isinstance(name, str) else name; w, d = p["size"]; h = p["h"]
    root = empty(name if isinstance(name, str) else "house", (*p["xy"], p["z"]), math.radians(p["rot"]))
    box("plinth", (w + .5, d + .5, plinth + 1.6), (0, 0, plinth - (plinth + 1.6) / 2), MAT["stone"], root)
    walls = box("walls", (w, d, h), (0, 0, plinth + h / 2), MAT[wall], root); z0 = plinth
    rise = gable_roof(root, w, d, plinth + h, math.radians(pitch), MAT["tiles"])
    for sx in (-1, 1):   # the two gable ends
        prism("gable", [(-d / 2, 0), (d / 2, 0), (0, rise)], 0.3, (sx * (w / 2 - .15), 0, plinth + h), MAT[wall], root, (0, 0, math.pi / 2))
    # door on the -y wall, with frame, leaf and step
    dx = -w * 0.18
    cut(walls, (door_w, .7, door_h), (dx, -d / 2, z0 + door_h / 2), root)
    box("leaf", (door_w, .08, door_h), (dx, -d / 2 + .3, z0 + door_h / 2), MAT["darkwood"], root)
    box("lintel", (door_w + .5, .22, .22), (dx, -d / 2 - .04, z0 + door_h + .11), MAT["wood"], root)
    box("step", (door_w + .8, 1.0, plinth * .9), (dx, -d / 2 - .55, plinth * .45 - .02), MAT["stone"], root)
    box("step2", (door_w + 1.4, 1.7, plinth * .45), (dx, -d / 2 - .85, plinth * .22 - .04), MAT["stone"], root)
    # windows on the -y and +x walls, with shutters
    wz = z0 + (h - 1.0 if high_windows else 1.55); ws = (.55, .5) if high_windows else (.85, 1.05)
    for i in range(windows):
        wx = w * (0.12 + 0.3 * i)
        if wx < w / 2 - .7:
            cut(walls, (ws[0], .5, ws[1]), (wx, -d / 2, wz), root); box("pane", (ws[0], .05, ws[1]), (wx, -d / 2 + .2, wz), MAT["dark"], root)
            for s in (-1, 1): box("shutter", (ws[0] / 2, .05, ws[1]), (wx + s * ws[0] * .78, -d / 2 - .04, wz), MAT["darkwood"], root, (0, 0, s * .0))
            box("sill", (ws[0] + .3, .2, .1), (wx, -d / 2 - .05, wz - ws[1] / 2 - .05), MAT["stone"], root)
        wy = -d * 0.25 + i * d * 0.5
        cut(walls, (.5, ws[0], ws[1]), (w / 2, wy, wz), root); box("pane", (.05, ws[0], ws[1]), (w / 2 - .2, wy, wz), MAT["dark"], root)
        for s in (-1, 1): box("shutter", (.05, ws[0] / 2, ws[1]), (w / 2 + .04, wy + s * ws[0] * .78, wz), MAT["darkwood"], root)
        box("sill", (.2, ws[0] + .3, .1), (w / 2 + .05, wy, wz - ws[1] / 2 - .05), MAT["stone"], root)
    return root

def shed(root, loc, w, d, h, roof="thatch"):
    """An open lean-to on four posts, sloping away from the building."""
    e = empty("shed", loc, 0, root); pitch = math.radians(14)
    for sx in (-1, 1):
        for sy in (-1, 1): cyl("post", .09, h + (0 if sy < 0 else .0), (sx * w / 2, sy * d / 2, h / 2), MAT["darkwood"], e, seg=10)
        box("beam", (.12, d + .5, .12), (sx * w / 2, 0, h + .02), MAT["darkwood"], e)
    box("leanroof", (w + .7, (d + .9) / math.cos(pitch), .22), (0, 0, h + .22), MAT[roof], e, (pitch, 0, 0)); return e

def amphora_mesh():
    prof = [(0, 0), (.03, 0), (.05, .07), (.12, .27), (.19, .5), (.2, .62), (.17, .74), (.09, .82), (.06, .86), (.06, .95), (.078, .965), (.078, .985), (.05, .985), (.045, .9)]
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]; es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, axis=(0, 0, 1), cent=(0, 0, 0), angle=2 * math.pi, steps=28, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    for s in (-1, 1):   # two ear handles
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=.018, radius2=.018, depth=.16, matrix=Matrix.Translation((s * .125, 0, .84)) @ Matrix.Rotation(s * .5, 4, "Y"))
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=.018, radius2=.018, depth=.1, matrix=Matrix.Translation((s * .1, 0, .925)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("amphora"); bm.to_mesh(me); bm.free(); me.polygons.foreach_set("use_smooth", [True] * len(me.polygons)); me.materials.append(MAT["clay"]); return me
AMPHORA = amphora_mesh()
def amphora(x, y, z=None, lean=0.0, scale=1.0):
    o = bpy.data.objects.new("amphora", AMPHORA); ROOT.objects.link(o); o.location = (x, y, (height(x, y) if z is None else z) - .04)
    o.rotation_euler = (lean * random.uniform(-1, 1), lean * random.uniform(-1, 1), random.uniform(0, 6.3)); o.scale = (scale,) * 3; return o

# ---------------------------------------------------------------- downloaded models
LIB = {}
JOIN = {"tree_small_02", "wooden_crate_02"}   # assets whose separate pieces make up one object
def load_asset(name):
    """Each top-level object in the asset's file becomes one variant, held in a collection that instances can point at."""
    path = os.path.join(ASSETS, name, name + ".blend")
    with bpy.data.libraries.load(path, link=False) as (src, dst): dst.objects = list(src.objects)
    objs = [o for o in dst.objects if o is not None]
    for im in bpy.data.images:
        if im.filepath.startswith("//"):
            cand = os.path.join(ASSETS, name, im.filepath[2:].replace("\\", "/"))
            if os.path.exists(cand): im.filepath = cand
    skip = ("LOD1", "LOD2", "LOD3", "GEONODES", "GEOMETRY_NODES", "LEAVES_", "BRANCHES_", "_TINY_")
    meshes = [o for o in objs if o.type == "MESH" and not any(t in o.name.upper() for t in skip)]
    tops = [o for o in meshes if o.parent is None or o.parent not in meshes]
    if name in JOIN: tops = tops[:1]
    variants = []
    for t in tops:
        c = bpy.data.collections.new(name + "." + t.name); group = meshes if name in JOIN else [t] + [o for o in meshes if o.parent is t]
        for o in group: c.objects.link(o)
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(v) for o in group for v in o.bound_box]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        c.instance_offset = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)
        if (hi - lo).z > 0.15 * max((hi - lo).x, (hi - lo).y): variants.append((c, hi - lo))
    LIB[name] = variants
    print("ASSET", name, [(c.name.split(".", 1)[1], tuple(round(v, 2) for v in s)) for c, s in variants]); return variants

def place(name, x, y, z=None, scale=1.0, rot=None, variant=None, sink=0.0, tilt=0.0, h=None):
    """Put one copy of a downloaded model on the ground. `h` asks for a height in metres, whatever size the model was made at."""
    c, size = random.choice(LIB[name]) if variant is None else LIB[name][variant % len(LIB[name])]
    if h: scale = scale * h / max(1e-3, size.z)
    if scale > 14: print("SKIP huge", name, c.name, round(scale, 1)); return None
    e = bpy.data.objects.new(name, None); ROOT.objects.link(e); e.instance_type = "COLLECTION"; e.instance_collection = c
    e.location = (x, y, (height(x, y) if z is None else z) - sink); e.scale = (scale,) * 3
    e.rotation_euler = (random.uniform(-tilt, tilt), random.uniform(-tilt, tilt), random.uniform(0, 6.3) if rot is None else rot); return e

for a in ["tree_small_02", "island_tree_02", "searsia_burchellii", "searsia_lucida", "shrub_01", "shrub_02", "shrub_04", "grass_medium_01", "wild_rooibos_bush",
          "namaqualand_stones_01", "boulder_01", "wicker_basket_01", "wooden_crate_02", "ceramic_vase_01", "ceramic_vase_03", "jug_01"]:
    try: load_asset(a)
    except Exception as ex: print("ASSET FAILED", a, ex); LIB[a] = []

# ---------------------------------------------------------------- terrain and sea
def terrain(N, half, centre, hole=None):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=N, y_segments=N, size=half); ox, oy = centre
    for v in bm.verts: v.co.x += ox; v.co.y += oy
    if hole:                                                # leave out what another sheet already covers
        (hx, hy), hh = hole; inside = lambda v: abs(v.co.x - hx) < hh - 2 and abs(v.co.y - hy) < hh - 2
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(inside(v) for v in f.verts)], context="FACES")
    for v in bm.verts: v.co.z = height(v.co.x, v.co.y)
    bm.normal_update(); grass, green, rock, road, wheat = [], [], [], [], []
    for v in bm.verts:
        x, y = v.co.x, v.co.y; l, d = to_ld(x, y); s = inland(l, d)
        if s < -3: grass.append(0); green.append(0); rock.append(0); road.append(0); wheat.append(0); continue
        n = noise.noise(Vector((x * .09, y * .09, 7))) * .5 + noise.noise(Vector((x * .31, y * .31, 2))) * .25
        grass.append(smooth(3.5, 9, s + n * 6))
        green.append(smooth(-.15, .25, noise.noise(Vector((x * .02, y * .02, 21))) + n * .4 + v.co.z * .012) * smooth(8, 22, s) * .92)
        rock.append(max(smooth(.30, .55, n + .12) * smooth(14, 30, s) * .5, smooth(.90, .76, v.normal.z)))
        wheat.append(max(smooth(-.6, 1.2, box_edge(x, y, f) + n * 2) for f in FIELDS))
        road.append(1 - smooth(.8, 2.0, road_dist(x, y) + n * .9))
    o = obj_from(bm, "terrain", TERRAIN_MAT, smooth_shade=True)
    for key, vals in (("grass", grass), ("green", green), ("rock", rock), ("road", road), ("wheat", wheat)):
        o.data.attributes.new(key, "FLOAT", "POINT").data.foreach_set("value", vals)
    return o
TERRAIN_MAT = terrain_mat(); SOUTH = (ld(100, -150), 530.0)
terrain(1180, SOUTH[1], SOUTH[0]); terrain(1000, 450.0, ld(-60, -660), hole=SOUTH)
box("sea", (3400, 3400, 9), (0, 0, -4.5), water_mat())
box("seabed", (3400, 3400, 1), (0, 0, -5.6), flat("seabed", (.55, .5, .38)))

# ---------------------------------------------------------------- the four businesses
F = building("fishery", "plaster", windows=2)
shed(F, (PLACES["fishery"]["size"][0] / 2 + 2.3, .3, .45), 3.6, 4.4, 2.5)
G = building("granary", "ochre", pitch=27, plinth=1.0, windows=2, high_windows=True)
W = building("winery", "worn", windows=3)
shed(W, (-PLACES["winery"]["size"][0] / 2 - 2.6, 0, .45), 4.2, 5.0, 2.7)
P = building("potter", "plaster", pitch=22, windows=1)

def local(root, x, y):   # a point given in a building's own frame, as world x and y
    v = root.matrix_world @ Vector((x, y, 0)); return v.x, v.y
bpy.context.view_layer.update()

# fishery: drying racks, amphorae of salt fish, baskets and crates
fz = PLACES["fishery"]["z"]
for k in range(3):
    rx, ry = local(F, -6.5 + k * .2, -5.5 - k * 2.3); e = empty("rack", (rx, ry, height(rx, ry)), math.radians(PLACES["fishery"]["rot"]))
    for sx in (-1.8, 1.8): cyl("post", .05, 1.7, (sx, 0, .85), MAT["darkwood"], e, seg=8)
    for hz in (1.6, 1.15): cyl("rail", .012, 3.7, (0, 0, hz), MAT["rope"], e, (0, math.pi / 2, 0), 6)
    for i in range(14):
        for hz in (1.6, 1.15):
            f = cyl("fish", .045, .34, (-1.6 + i * .245, 0, hz - .2), MAT["fish"], e, seg=8, r2=.012); f.scale = (1, .35, 1)
for i in range(22):
    ax, ay = local(F, 1.2 + (i % 8) * .46, -3.6 - (i // 8) * .5); amphora(ax, ay, lean=.07)
for i in range(6):
    ax, ay = local(F, 6.0 + (i % 3) * .5, -1.0 + (i // 3) * .55); amphora(ax, ay, z=fz + .45, lean=.05)
for i in range(5):
    bx, by = local(F, -1.5 - i * .75, -3.5 - random.random() * .5); place("wicker_basket_01", bx, by, h=(.45))
for i in range(4):
    bx, by = local(F, 4.6 + (i % 2) * .8, -4.9 - (i // 2) * .8); place("wooden_crate_02", bx, by, h=(.6), rot=random.uniform(-.2, .2))

# granary: threshing floor, sacks, a cart-load of grain
tz = raw_height(*THRESH) + 0.1
cyl("threshing_floor", 3.6, .5, (*THRESH, tz - .1), MAT["stone"], seg=48); cyl("grain_heap", 1.2, .7, (THRESH[0] + .6, THRESH[1] - .3, tz + .45), MAT["grain"], seg=24, r2=.05)
def sack(x, y, z, lying=False):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=.5)
    o = obj_from(bm, "sack", MAT["hessian"], None, (x, y, z), (0, 0, random.uniform(0, 3.1)), True); o.scale = (.62, .42, .26) if lying else (.42, .42, .62); return o
for i in range(14):
    sx, sy = local(G, 1.3 + (i % 4) * .75, -5.0 - (i // 4 % 2) * .6); sack(sx, sy, PLACES["granary"]["z"] + .16 + (i // 8) * .3, True)
for i in range(6):
    sx, sy = THRESH[0] - 2.2 + i * .5, THRESH[1] + 2.3 + (i % 2) * .3; sack(sx, sy, tz + .42)

# winery: vineyard rows, press shed with a vat, amphorae of wine
vy = VINEYARD[2] + 2
while vy < VINEYARD[3] - 1:
    vx = VINEYARD[0] + 2
    while vx < VINEYARD[1] - 1:
        if math.hypot(vx - PLACES["winery"]["xy"][0], vy - PLACES["winery"]["xy"][1]) > 13 and road_dist(vx, vy) > 2.5:
            vz = height(vx, vy); cyl("vinepost", .04, 1.3, (vx, vy, vz + .65), MAT["darkwood"], seg=6)
            if LIB["searsia_lucida"]: place("searsia_lucida", vx, vy, h=(1.35) * random.uniform(.85, 1.15), sink=.1)
        vx += 2.0
    vy += 2.8
f = FIELDS[2]; fx = f[0] + 3                                  # the near field is cut, and stands in sheaves
while fx < f[1] - 2:
    fy = f[2] + 3
    while fy < f[3] - 2:
        sx, sy = fx + random.uniform(-.6, .6), fy + random.uniform(-.6, .6)
        if road_dist(sx, sy) > 2: cyl("sheaf", .42, 1.0, (sx, sy, height(sx, sy) + .5), MAT["grain"], seg=10, r2=.1)
        fy += 4.5
    fx += 5.0
for i in range(3):
    hx, hy = ld(125 - 14 - i * 5.5, -58 + 9 + (i % 2) * 2); cyl("haystack", 2.0, 2.2, (hx, hy, height(hx, hy) + 1.0), MAT["thatch"], seg=20, r2=1.5)
    cyl("haytop", 1.55, 1.6, (hx, hy, height(hx, hy) + 2.9), MAT["thatch"], seg=20, r2=.05)
vx, vy = local(W, -PLACES["winery"]["size"][0] / 2 - 2.6, 0)
cyl("vat", 1.1, .8, (vx, vy, PLACES["winery"]["z"] + .75), MAT["stone"], seg=28); cyl("must", 1.0, .1, (vx, vy, PLACES["winery"]["z"] + 1.12), flat("must", (.25, .04, .1), .3), seg=28)
for i in range(18):
    ax, ay = local(W, -1.5 + (i % 9) * .48, -4.3 - (i // 9) * .5); amphora(ax, ay, lean=.06)

# the amphora maker: kiln, woodpile, rows of pots
kx, ky = local(P, 5.6, .4); kz = height(kx, ky)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=14, radius=1.5); k = obj_from(bm, "kiln", MAT["rubble"], None, (kx, ky, kz + .2), smooth_shade=True); k.scale = (1, 1, 1.15)
cyl("kiln_base", 1.65, .9, (kx, ky, kz + .2), MAT["rubble"], seg=28); cyl("kiln_mouth", .42, .5, (kx, ky - 1.45, kz + .55), MAT["dark"], rot=(math.pi / 2, 0, 0), seg=16)
cyl("kiln_vent", .3, .35, (kx, ky, kz + 1.95), MAT["dark"], seg=14)
for i in range(16):
    lx, ly = local(P, 3.2 + (i % 4) * .28, -3.4); cyl("log", .09, 1.3, (lx, ly, height(lx, ly) + .1 + (i // 4) * .17), MAT["darkwood"], rot=(math.pi / 2, 0, math.radians(PLACES["potter"]["rot"])), seg=8)
for i in range(30):
    ax, ay = local(P, -2.6 + (i % 10) * .5, -3.4 - (i // 10) * .52); amphora(ax, ay, lean=.03)
for i in range(8):
    ax, ay = local(P, -5.0 + (i % 4) * .6, -1.0 + (i // 4) * .7)
    nm = random.choice(["ceramic_vase_01", "ceramic_vase_03", "jug_01"])
    if LIB[nm]: place(nm, ax, ay, h=(.55))

# ---------------------------------------------------------------- town, temple and farms
NPC = []        # (x, y, radius) of every building nobody in the stories lives in, so that nothing is planted on it

def columns(root, pts, zs, h, r, mat):
    shafts = []
    for cx, cy in pts:
        shafts.append(cyl("column", r, h, (cx, cy, zs + h / 2), mat, root, seg=20, r2=r * .8))
        cyl("echinus", r * .8, .24, (cx, cy, zs + h + .12), mat, root, seg=20, r2=r * 1.3); box("abacus", (r * 2.7, r * 2.7, .18), (cx, cy, zs + h + .33), mat, root)
    return shafts

def temple(xy, z, nx=11, ny=6, gap=2.05, col_h=5.2, col_r=.43):
    """A Doric temple: three steps, a ring of columns, a painted frieze, and a tiled roof. Its front faces east, along +x."""
    root = empty("temple", (*xy, z)); L = (nx - 1) * gap; W = (ny - 1) * gap; m = MAT["marble"]
    box("foundation", (L + 3.6, W + 3.6, 3), (0, 0, -1.5), MAT["stone"], root)
    for i in range(3): box("step", (L + 3.2 - i * .7, W + 3.2 - i * .7, .35), (0, 0, .175 + i * .35), m, root)
    zs = 1.05; xs = [-L / 2 + i * gap for i in range(nx)]; ys = [-W / 2 + j * gap for j in range(ny)]
    TEMPLE_SHAFTS.extend(columns(root, [(x, y) for x in xs for y in ys if x in (xs[0], xs[-1]) or y in (ys[0], ys[-1])], zs, col_h, col_r, m))
    za = zs + col_h + .42; box("architrave", (L + 1.3, W + 1.3, .55), (0, 0, za + .275), m, root); box("frieze", (L + 1.2, W + 1.2, .5), (0, 0, za + .8), m, root)
    box("band", (L + 1.34, W + 1.34, .07), (0, 0, za + .56), MAT["red"], root); box("cornice", (L + 1.9, W + 1.9, .16), (0, 0, za + 1.13), m, root)
    for i in range(nx * 2 - 1):
        for sy in (-1, 1): box("triglyph", (.3, .1, .46), (-L / 2 + i * gap / 2, sy * (W / 2 + .62), za + .8), MAT["blue"], root)
    for j in range(ny * 2 - 1):
        for sx in (-1, 1): box("triglyph", (.1, .3, .46), (sx * (L / 2 + .62), -W / 2 + j * gap / 2, za + .8), MAT["blue"], root)
    top = za + 1.21; rise = gable_roof(root, L + 1.5, W + 1.5, top, math.radians(15), MAT["tiles"], over=.25)
    for sx in (-1, 1):
        prism("pediment", [(-W / 2 - .75, 0), (W / 2 + .75, 0), (0, rise)], .5, (sx * (L / 2 + .5), 0, top), m, root, (0, 0, math.pi / 2))
        prism("tympanum", [(-W / 2 + .1, .2), (W / 2 - .1, .2), (0, rise - .25)], .1, (sx * (L / 2 + .78), 0, top), MAT["blue"], root, (0, 0, math.pi / 2))
    box("cella", (L - gap * 3, W - gap * 2, col_h + .42), (-gap * .4, 0, zs + (col_h + .42) / 2), m, root)
    box("doorway", (.2, 1.9, 3.6), (L / 2 - gap * 1.9 + .02, 0, zs + 1.8), MAT["dark"], root)
    box("altar", (1.4, 2.6, 1.1), (L / 2 + 6.5, 0, .55), m, root); box("altar_step", (2.4, 3.6, .3), (L / 2 + 6.5, 0, .15), m, root)
    return root
TEMPLE_SHAFTS = []                 # the columns the legislators argue about: repainted red or blue for two of the views
temple(TEMPLE, TEMPLE_Z); NPC.append((*TEMPLE, 16))

def stoa(x, y, length=24, turn=0.0):
    """A long open hall: a back wall, a row of columns in front, and a tiled roof sloping to the columns."""
    z = max(height(x + sx, y + sy) for sx in (-length / 2, length / 2) for sy in (-3, 3)) + .1; root = empty("stoa", (x, y, z), turn)
    box("floor", (length + 1, 6.4, 1.9), (0, 0, -.6), MAT["stone"], root); box("back", (length, .5, 3.9), (0, 2.6, .35 + 1.95), MAT["plaster"], root)
    for sx in (-1, 1): box("end", (.5, 3.2, 3.6), (sx * (length / 2 - .25), 1.2, .35 + 1.8), MAT["plaster"], root)
    n = int(length / 2.4); columns(root, [(-length / 2 + .6 + i * (length - 1.2) / n, -2.5) for i in range(n + 1)], .35, 2.9, .24, MAT["marble"])
    box("beam", (length, .4, .3), (0, -2.5, .35 + 3.5), MAT["marble"], root)
    box("roof", (length + .8, 6.3, .18), (0, -.1, 4.25), MAT["tiles"], root, (math.radians(-9), 0, 0)); return root

def library(key, tower=False, annex=False):
    """A scholars' hall: a long room with a colonnade down its sunny side, under one tiled roof, on a stone platform."""
    x, y = LIBS[key]; z = LIB_Z[key]; root = empty(key, (x, y, z)); L, Dp = 18.0, 8.0
    box("platform", (L + 3, Dp + 8, 2.6), (0, -2.3, -.5), MAT["stone"], root); box("steps", (8, 2.4, 2.2), (0, -9.4, -.75), MAT["stone"], root)
    box("hall", (L, Dp, 5.0), (0, 0, .8 + 2.5), MAT["plaster"], root); zr = .8 + 5.0
    columns(root, [(-L / 2 + .7 + i * (L - 1.4) / 8, -6.4) for i in range(9)], .8, 4.1, .3, MAT["marble"]); box("beam", (L, .5, .45), (0, -6.4, zr - .22), MAT["marble"], root)
    sub_root = empty("roofroot", (0, -2.9, 0), 0, root); rise = gable_roof(sub_root, L + .4, Dp + 6.2, zr, math.radians(17), MAT["tiles"], over=.35)
    for sx in (-1, 1): prism("gable", [(-(Dp + 6.2) / 2, 0), ((Dp + 6.2) / 2, 0), (0, rise)], .4, (sx * (L / 2 + .1), -2.9, zr), MAT["plaster"], root, (0, 0, math.pi / 2))
    for i in range(4): box("door", (1.5, .1, 3.0), (-6 + i * 4, -Dp / 2 - .03, .8 + 1.5), MAT["darkwood"], root)
    if tower:                                               # the cape library keeps a beacon for ships
        cyl("tower", 2.3, 11, (x + 15, y + 2, z + 5.5), MAT["stone"], seg=20, r2=1.9); cyl("tower_top", 2.6, .5, (x + 15, y + 2, z + 11.2), MAT["stone"], seg=20)
        cyl("tower_roof", 2.5, 2.4, (x + 15, y + 2, z + 12.6), MAT["tiles"], seg=20, r2=.05)
    if annex:                                               # the school has a second range and a walled court
        building(dict(xy=(x - 16, y + 1), z=z, size=(8, 6), h=3.2, rot=90), "worn", windows=2)
        wall_run([(x - 20, y - 9), (x - 11, y - 9)]); wall_run([(x - 20.5, y - 9), (x - 20.5, y - 3)])
    NPC.append((x, y - 2, 15)); return root

def wall_run(pts, h=.9, t=.45):
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / 1.6))
        for i in range(n):
            x = a[0] + (b[0] - a[0]) * (i + .5) / n; y = a[1] + (b[1] - a[1]) * (i + .5) / n
            box("yardwall", (L / n + .05, t, h + 1), (x, y, height(x, y) + h / 2 - .5), MAT["rubble"], rot=(0, 0, math.atan2(b[1] - a[1], b[0] - a[0])))

def house(x, y, turn=None, farm=False):
    size = (random.uniform(6.2, 8.4), random.uniform(5.0, 6.4)); two = random.random() < (.1 if farm else .24)
    r = max(size) / 2 + 1; z = max(height(x + sx, y + sy) for sx in (-r, 0, r) for sy in (-r, 0, r)) + .05
    spec = dict(xy=(x, y), z=z, size=size, h=5.3 if two else random.uniform(2.7, 3.3), rot=(random.choice([0, 0, 90, 180, 270]) if turn is None else turn) + random.uniform(-3, 3))
    building(spec, random.choice(["plaster", "plaster", "worn", "ochre"]), pitch=random.uniform(19, 26), plinth=.35, windows=random.choice([1, 2]))
    NPC.append((x, y, r + 1.5)); return spec

library("town library"); library("hill school", annex=True); library("cape library", tower=True)

# the town: lots on a square grid, with a street after every second lot, an open agora and a stoa along its far side
ax, ay = (AGORA[0] + AGORA[1]) / 2, (AGORA[2] + AGORA[3]) / 2
stoa(ax, AGORA[3] + 3.6, 24); NPC.append((ax, AGORA[3] + 3.6, 13)); NPC.append((ax, ay, 10))
cyl("well", .9, .8, (ax + 4, ay - 2, height(ax + 4, ay - 2) + .3), MAT["stone"], seg=18); cyl("well_water", .65, .1, (ax + 4, ay - 2, height(ax + 4, ay - 2) + .62), MAT["dark"], seg=18)
box("statue_base", (1.2, 1.2, 1.4), (ax - 3, ay + 1, height(ax - 3, ay + 1) + .7), MAT["marble"]); cyl("statue", .28, 1.9, (ax - 3, ay + 1, height(ax - 3, ay + 1) + 2.3), MAT["marble"], seg=12, r2=.16)
houses = 0; ix = 0; hx = TOWN[0] + 5
while hx < TOWN[1] - 4:
    iy = 0; hy = TOWN[2] + 5
    while hy < TOWN[3] - 4:
        l, d = to_ld(hx, hy)
        ok = inland(l, d) > 10 and math.hypot(hx - LIBS['town library'][0], hy - LIBS['town library'][1]) > 17 and road_dist(hx, hy) > 4.8 and box_edge(hx, hy, AGORA) < -5 and box_edge(hx, hy, VINEYARD) < -4 and abs(hy - (AGORA[3] + 3.6)) + max(0, abs(hx - ax) - 13) > 8
        ok = ok and all(math.hypot(hx - p["xy"][0], hy - p["xy"][1]) > 17 for p in PLACES.values()) and math.hypot(hx - QUAY[0], hy - QUAY[1]) > 16
        if ok and random.random() < .93: house(hx + random.uniform(-.5, .5), hy + random.uniform(-.5, .5)); houses += 1
        iy += 1; hy += 8.6 + (3.4 if iy % 2 == 0 else 0)
    ix += 1; hx += 9.8 + (3.4 if ix % 2 == 0 else 0)
print("houses", houses)

# farmsteads out in the country, each with a haystack and a few jars
FARMS = [(n, p) for n, p in HOMES.items()] + [(None, p) for p in [(-186, -165), (-212, 22), (122, 30), (40, -190), (-300, -150), (290, -90), (330, -300), (215, -345), (470, -120), (-70, -400), (380, -30)]]
for owner, (fl, fd) in FARMS:
    fx, fy = ld(fl, fd)
    if not owner and (any(box_edge(fx, fy, f) > -8 for f in FIELDS) or road_dist(fx, fy) < 5): continue
    spec = house(fx, fy, turn=0 if owner else None, farm=True); hx, hy = fx + 7.5, fy + 3
    cyl("haystack", 1.7, 1.9, (hx, hy, height(hx, hy) + .9), MAT["thatch"], seg=18, r2=1.3); cyl("haytop", 1.35, 1.4, (hx, hy, height(hx, hy) + 2.5), MAT["thatch"], seg=18, r2=.05)
    for i in range(4): amphora(fx - 5 + i * .5, fy - 5.5, lean=.06)
    NPC.append((hx, hy, 3))
    if owner:                                           # a legislator's home flies a blue pennant by the door
        HOMES[owner] = (fl, fd, spec["z"]); px, py = fx - 3.2, fy - 5.2
        cyl("pole", .05, 5.2, (px, py, spec["z"] + 2.6), MAT["darkwood"], seg=8); box("pennant", (.04, 1.5, .8), (px, py + .8, spec["z"] + 4.7), MAT["blue"])

# ---------------------------------------------------------------- the siege
MAT["canvas"] = pbr("canvas", "hessian_230", 1.2, (1.5, 1.42, 1.22)); MAT["rampart"] = pbr("rampart", "medieval_blocks_05", 3.2, (1.0, .96, .88))
def camp(key, turn):
    """Three rows of tents, a commander's pavilion with a red standard, cooking fires and spear racks."""
    x, y = CAMPS[key]; z = CAMP_Z[key]; ca, sa = math.cos(turn), math.sin(turn)
    for row in range(3):
        for i in range(6):
            lx, ly = (i - 2.5) * 4.0, (row - 1) * 6.0 + 8; tx, ty = x + lx * ca - ly * sa, y + lx * sa + ly * ca; e = empty("tent", (tx, ty, height(tx, ty)), turn + random.uniform(-.08, .08))
            prism("tent", [(-1.35, 0), (1.35, 0), (0, 2.0)], 3.4, (0, 0, 0), MAT["canvas"], e); cyl("tentpole", .04, 2.3, (0, -1.7, 1.15), MAT["darkwood"], e, seg=6)
    box("pavilion", (5.5, 4.5, 2.4), (x, y - 4, z + 1.2), MAT["canvas"]); cyl("pavilion_roof", 4.3, 1.9, (x, y - 4, z + 3.35), MAT["canvas"], rot=(0, 0, math.pi / 4), seg=4, r2=.05)
    cyl("standard", .06, 7, (x + 4.2, y - 4, z + 3.5), MAT["darkwood"], seg=8); box("banner", (.04, 1.9, 1.2), (x + 4.2, y - 3.05, z + 6.3), MAT["red"])
    for k in range(3):
        fx, fy = x - 8 + k * 8, y - 11; fz = height(fx, fy); cyl("fire_ring", .8, .25, (fx, fy, fz + .1), MAT["stone"], seg=12); cyl("embers", .55, .12, (fx, fy, fz + .2), MAT["dark"], seg=10)
    for k in range(2):
        for s in range(9): cyl("spear", .02, 2.5, (x - 10 + k * 20 + s * .18, y + 1, z + 1.2), MAT["darkwood"], rot=(.16, 0, 0), seg=5)
    for i in range(6): amphora(x - 3 + i * .5, y - 8, lean=.06)
    NPC.append((x, y + 4, 21))
for key, turn in (("commander's camp", .3), ("camp A", -.25), ("camp B", .6), ("camp C", -.5)): camp(key, turn)

# the enemy city: a tall wall along the crest, with towers and one gate. The city itself is off the map.
arc = [(CITY_C[0] + CITY_R * math.sin(math.radians(a)), CITY_C[1] + CITY_R * math.cos(math.radians(a))) for a in range(-52, 53, 4)]
for i, (p1, p2) in enumerate(zip(arc, arc[1:])):
    (x1, y1), (x2, y2) = ld(*p1), ld(*p2); zt = max(height(x1, y1), height(x2, y2)); L = math.hypot(x2 - x1, y2 - y1); ang = math.atan2(y2 - y1, x2 - x1); n = int(L / 1.7)
    box("citywall", (L + .6, 3.2, 56), ((x1 + x2) / 2, (y1 + y2) / 2, zt - 4), MAT["rampart"], rot=(0, 0, ang))      # 24 metres above the crest: tall enough to hide the city from this height
    for k in range(n): box("merlon", (.9, .7, 1.1), (x1 + (x2 - x1) * (k + .5) / n, y1 + (y2 - y1) * (k + .5) / n, zt + 24.5), MAT["rampart"], rot=(0, 0, ang))
    if i % 3 == 0:
        tz = height(x1, y1); box("tower", (7.5, 7.5, 66), (x1, y1, tz - 1), MAT["rampart"], rot=(0, 0, ang)); cyl("tower_roof", 6, 3.4, (x1, y1, tz + 33.7), MAT["tiles"], rot=(0, 0, ang + math.pi / 4), seg=4, r2=.05)
GATE = ld(CITY_C[0], CITY_C[1] + CITY_R); GATE_Z = height(*GATE)
box("gatehouse", (13, 9, 72), (*GATE, GATE_Z - 1), MAT["rampart"], rot=(0, 0, math.pi / 4)); box("gate", (4.6, 9.4, 7), (*GATE, GATE_Z + 3.5), MAT["darkwood"], rot=(0, 0, math.pi / 4))
cyl("gate_roof", 9, 4, (*GATE, GATE_Z + 37), MAT["tiles"], seg=4, r2=.05)
for i in range(34):                                         # roofs just inside, enough to say there is a city
    a = math.radians(random.uniform(-46, 46)); r = CITY_R - random.uniform(12, 36); hx, hy = ld(CITY_C[0] + r * math.sin(a), CITY_C[1] + r * math.cos(a))
    building(dict(xy=(hx, hy), z=height(hx, hy) + .05, size=(random.uniform(6, 9), random.uniform(5, 7)), h=random.uniform(3, 6), rot=random.uniform(0, 360)), random.choice(["plaster", "ochre", "worn"]), plinth=.35, windows=1)
for a, hh in ((9, 19), (-21, 16), (30, 16)):                # three tall roofs that show above the wall
    hx, hy = ld(CITY_C[0] + (CITY_R - 15) * math.sin(math.radians(a)), CITY_C[1] + (CITY_R - 15) * math.cos(math.radians(a)))
    building(dict(xy=(hx, hy), z=height(hx, hy), size=(13, 8), h=hh, rot=45 - a), "plaster", pitch=20, plinth=.4, windows=2, high_windows=True)

# ---------------------------------------------------------------- quay, jetty and boats
qa = math.radians(45); qz = 0.75
box("quay", (18, 6.5, 4.4), (*QUAY, qz - 2.2), MAT["stone"], rot=(0, 0, qa))
for i in range(5):
    bx, by = q(-10 + i * 3.5, 19); cyl("bollard", .16, .7, (bx, by, qz + .3), MAT["darkwood"], seg=12)
jx, jy = q(-6, 25.5); box("jetty", (2.4, 12, .16), (jx, jy, qz - .05), MAT["wood"], rot=(0, 0, qa))
for i in range(6):
    for s in (-1.1, 1.1):
        px, py = q(-6 + s, 20.5 + i * 2.1); cyl("pile", .13, 4.2, (px, py, qz - 1.9), MAT["darkwood"], seg=10)
def boat(l, d, turn, length=6.2, beam=1.9, depth=.95):
    e = empty("boat", (*q(l, d), -.28), turn); bm = bmesh.new(); rings = []; N = 16
    for i in range(N + 1):
        t = i / N; u = 2 * t - 1; b = beam / 2 * max(.02, math.sin(math.pi * t)) ** .55; sheer = .55 + .42 * u * u; keel = sheer - depth * (1 - .55 * u * u * u * u)
        rings.append([bm.verts.new((u * length / 2, sx * b * f, keel + (sheer - keel) * g)) for sx, f, g in ((-1, 1, 1), (-1, .86, .5), (-1, .5, .12), (1, 0, 0), (1, .5, .12), (1, .86, .5), (1, 1, 1))])
    for i in range(N):
        for k in range(6): bm.faces.new([rings[i][k], rings[i + 1][k], rings[i + 1][k + 1], rings[i][k + 1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); hull = obj_from(bm, "hull", MAT["wood"], e, smooth_shade=True)
    hull.modifiers.new("thick", "SOLIDIFY").thickness = .06
    for u in (-.5, -.15, .2, .52): box("thwart", (.22, beam * .86 * math.sin(math.pi * (u + 1) / 2) ** .55, .05), (u * length / 2, 0, .5), MAT["darkwood"], e)
    box("gunwale_l", (length * .78, .07, .07), (0, beam / 2 - .05, .6), MAT["darkwood"], e); box("gunwale_r", (length * .78, .07, .07), (0, -beam / 2 + .05, .6), MAT["darkwood"], e)
    cyl("mast", .06, 4.2, (.3, 0, 2.3), MAT["darkwood"], e, seg=10); cyl("yard", .04, 3.4, (.3, 0, 3.7), MAT["darkwood"], e, (math.pi / 2, 0, .25), 8)
    cyl("furled", .13, 3.0, (.3, 0, 3.56), MAT["hessian"], e, (math.pi / 2, 0, .25), 10)
    for s in (-1, 1): cyl("oar", .025, 3.0, (-.6, s * .35, .62), MAT["wood"], e, (0, math.pi / 2, s * .06), 6)
    return e
boat(-2.6, 24.5, qa + math.pi / 2); boat(7.5, 21, qa + .25, 5.2, 1.7); boat(-12, 22.5, qa + math.pi / 2 - .15, 5.6, 1.8)
for i in range(10):
    ax, ay = q(-9.5 + (i % 5) * .5, 15.2 + (i // 5) * .5); amphora(ax, ay, z=qz + .04, lean=.04)
for i in range(3):
    bx, by = q(1 + i * .9, 15.5); place("wooden_crate_02", bx, by, z=qz, h=(.6), rot=qa + random.uniform(-.2, .2))

# a low yard wall behind the fishery and beside the winery
wall_run([local(F, -6.5, 5), local(F, 7, 5), local(F, 9.5, 1)]); wall_run([local(W, 7.5, -4), local(W, 7.5, 5), local(W, -8, 5)])

# ---------------------------------------------------------------- scattering plants and stones
BLOCK = [(p["xy"][0], p["xy"][1], max(p["size"]) * .85 + 1.5) for p in PLACES.values()] + [(*THRESH, 4.6), (*QUAY, 9), (kx, ky, 3)] + NPC
def free(x, y, r=0.0, road=1.6, min_s=3.0, max_s=420):
    l, d = to_ld(x, y); s = inland(l, d)
    if not (min_s <= s <= max_s) or not -430 < l < 570 or math.hypot(l - CITY_C[0], d - CITY_C[1]) < CITY_R + 7: return False
    if box_edge(x, y, VINEYARD) > -1.5 or any(box_edge(x, y, f) > -1.5 for f in FIELDS): return False
    if road_dist(x, y) < road + r: return False
    return all(math.hypot(x - bx, y - by) > br + r for bx, by, br in BLOCK)
NORTH = (-420, 320, -1000, -470)
def scatter(n, fn, tries=30, region=(-335, 570, -470, 80), **kw):
    done = 0
    for _ in range(n * tries):
        if done >= n: break
        x, y = ld(random.uniform(region[0], region[1]), random.uniform(region[2], region[3]))
        if free(x, y, **kw) and fn(x, y) is not False: done += 1
    return done
def near_place(x, y, r): return any(math.hypot(x - p["xy"][0], y - p["xy"][1]) < r for p in PLACES.values())
def patchy(x, y, f=.07, th=.02): return noise.noise(Vector((x * f, y * f, 11))) > th
taken = set()
def tree(x, y):
    c = (int(x // 3.4), int(y // 3.4))
    if any((c[0] + i, c[1] + j) in taken for i in (-1, 0, 1) for j in (-1, 0, 1)): return False
    grove = noise.noise(Vector((x * .009, y * .009, 31))) + .5 * noise.noise(Vector((x * .03, y * .03, 8)))
    if grove < .12 and random.random() < .93: return False                     # groves, with open ground between
    nm = random.choice(["tree_small_02", "island_tree_02", "searsia_burchellii", "searsia_lucida", "searsia_lucida"])
    if not LIB[nm]: return False
    target = {"tree_small_02": 6.5, "island_tree_02": 7.5, "searsia_burchellii": 5.0, "searsia_lucida": 4.2}[nm]
    place(nm, x, y, h=(target) * random.uniform(.7, 1.45), sink=.15); taken.add(c)
print("trees", scatter(2400, tree, tries=60, r=2.2, min_s=6))
def shrub(x, y):
    if not patchy(x, y): return False
    nm = random.choice(["shrub_01", "shrub_04", "wild_rooibos_bush", "wild_rooibos_bush", "searsia_lucida", "shrub_02"])
    if LIB[nm]: place(nm, x, y, h=(random.uniform(.7, 1.7)), sink=.05)
print("shrubs", scatter(13500, shrub, r=.6, min_s=5))
def grass(x, y):
    if not near_place(x, y, 75) or not patchy(x, y, .11, -.12): return False
    if LIB["grass_medium_01"]: place("grass_medium_01", x, y, h=(random.uniform(.45, .95)))
print("grass", scatter(9000, grass, tries=60, r=.2, road=1.2, min_s=4.5))
def stone(x, y):
    if LIB["namaqualand_stones_01"]: place("namaqualand_stones_01", x, y, h=(random.uniform(.15, .45)), sink=.04, tilt=.2)
print("stones", scatter(3000, stone, r=.3, road=.9, min_s=.5))
def boulder(x, y):
    if LIB["boulder_01"]: place("boulder_01", x, y, h=(random.uniform(.7, 2.2)), sink=.3, tilt=.3)
print("boulders", scatter(90, boulder, r=1.5, min_s=-2.5, max_s=3.5))
print("north", scatter(1700, tree, tries=60, region=NORTH, r=2.2, min_s=6), scatter(9500, shrub, region=NORTH, r=.6, min_s=5), scatter(2200, stone, region=NORTH, r=.3, road=.9, min_s=.5))

# ---------------------------------------------------------------- camera, light, render
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); ROOT.objects.link(cam); scene.camera = cam
cam.data.type = "ORTHO"; cam.rotation_euler = (math.radians(60), 0, math.radians(45)); cam.data.clip_end = 4000
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); ROOT.objects.link(sun)
sun.data.energy = 5.2; sun.data.color = (1.0, .94, .84); sun.data.angle = math.radians(2.2)
sun.rotation_euler = Vector((.46, .80, -.50)).normalized().to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (.55, .70, .95, 1); bg.inputs[1].default_value = 1.15

scene.render.engine = "CYCLES"; scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()
    for dev in prefs.devices: dev.use = True
    scene.cycles.device = "GPU"
except Exception as ex: print("GPU not enabled:", ex)
try: scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
except Exception as ex: print("look not set:", ex)
os.makedirs(OUT, exist_ok=True)

# One wide picture of everything, and a closer one of each place in its surroundings.
VIEWS = {"overview": dict(at=(2, -76), scale=455, width=WIDTH, aspect=2.0)}
VIEWS["soldiers"] = dict(at=(-60, -635), scale=620, width=WIDTH, aspect=2.14); VIEWS["camp"] = dict(at=(-157, -550), scale=96, width=WIDTH // 2, aspect=1.5)
VIEWS["city-gate"] = dict(at=(-60, -728), scale=180, width=WIDTH // 2, aspect=1.5)
VIEWS["legislators"] = dict(at=(-25, -75), scale=600, width=WIDTH, aspect=2.0); VIEWS["scholars"] = dict(at=(205, -160), scale=670, width=WIDTH, aspect=2.3)
for k, off in (("hill school", (-2, 4)), ("cape library", (4, 2)), ("town library", (0, 2))): VIEWS[k.replace(" ", "-")] = dict(at=(to_ld(*LIBS[k])[0] + off[0], to_ld(*LIBS[k])[1] + off[1]), scale=96, width=WIDTH // 2, aspect=1.5)
VIEWS["town"] = dict(at=(-62, 6), scale=150, width=WIDTH // 2, aspect=1.5); VIEWS["temple"] = dict(at=(-160, -22), scale=84, width=WIDTH // 2, aspect=1.5)
for colour in ("red", "blue"): VIEWS["temple-" + colour] = dict(VIEWS["temple"], paint=colour)
for name, off in (("fishery", (6, 8)), ("granary", (4, -2)), ("winery", (-2, 16)), ("potter", (2, -2))):
    VIEWS[name] = dict(at=(PLACES[name]["at"][0] + off[0], PLACES[name]["at"][1] + off[1]), scale=84, width=WIDTH // 2, aspect=1.5)

def screen(x, y, z):
    v = world_to_camera_view(scene, cam, Vector((x, y, z))); return [round(v.x, 4), round(1 - v.y, 4)]
info = {}
for view in opt("--views", ",".join(VIEWS)).split(","):
    V = VIEWS[view]; cam.data.ortho_scale = V["scale"]; tx, ty = ld(*V["at"])
    for o in TEMPLE_SHAFTS: o.data.materials[0] = MAT[V.get("paint", "marble")]
    cam.location = Vector((tx, ty, max(0, height(tx, ty)))) + cam.rotation_euler.to_matrix() @ Vector((0, 0, 1200))
    scene.render.resolution_x, scene.render.resolution_y = V["width"], int(V["width"] / V["aspect"]); bpy.context.view_layer.update()
    rec = info[view] = {"size": [scene.render.resolution_x, scene.render.resolution_y], "metres_across": V["scale"], "places": {}, "roads": []}
    for name, p in PLACES.items():
        w, d = p["size"]; a = math.radians(p["rot"]); top = p["z"] + p["h"] + 2.2
        corners = [(p["xy"][0] + math.cos(a) * sx - math.sin(a) * sy, p["xy"][1] + math.sin(a) * sx + math.cos(a) * sy) for sx in (-w / 2, w / 2) for sy in (-d / 2, d / 2)]
        rec["places"][name] = {"door": screen(*door(name, 1.0), height(*door(name, 1.0))), "centre": screen(*p["xy"], p["z"] + p["h"] / 2),
                               "outline": [screen(cx, cy, z) for z in (p["z"], top) for cx, cy in corners]}
    rec["places"]["quay"] = {"centre": screen(*QUAY, qz), "door": screen(*ld(QL - 2, QD - 3), qz)}
    rec["places"]["temple"] = {"centre": screen(*TEMPLE, TEMPLE_Z + 4), "door": screen(TEMPLE[0] + 17, TEMPLE[1] - 1, TEMPLE_Z)}
    rec["places"]["agora"] = {"centre": screen(ax, ay, height(ax, ay))}
    for n, (hl, hd, hz) in HOMES.items(): rec["places"][n] = {"centre": screen(*ld(hl, hd), hz + 3)}
    for k, v in LIBS.items(): rec["places"][k] = {"centre": screen(*v, LIB_Z[k] + 4)}
    for k, v in CAMPS.items(): rec["places"][k] = {"centre": screen(*v, CAMP_Z[k] + 3)}
    rec["places"]["enemy city"] = {"centre": screen(*GATE, GATE_Z + 6)}
    rec["road_names"] = ROAD_NAMES
    for r in ROADS: rec["roads"].append([screen(x, y, height(x, y)) for x, y in r])
    scene.render.filepath = os.path.join(OUT, view + ".png"); bpy.ops.render.render(write_still=True); print("RENDERED", scene.render.filepath)
old = os.path.join(OUT, "world.json"); merged = json.load(open(old)) if os.path.exists(old) else {}   # a partial render keeps the other views
merged.update(info); json.dump(merged, open(old, "w"), indent=1)
if "--save" in argv: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "world.blend"))
