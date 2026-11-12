"""Model the city (or the siege) of city_mockup.py in Blender, in exactly the frame of its southeast picture, and render it.

Every footprint, height, road, field and tree comes from the scene city_mockup.py dumps, so the page's places, doors and
routes land on the rendered picture exactly as they do on the drawn one. The detail is added inside those outlines: textures,
tiles, columns, doors and windows, planting.
Run:  python3 world/city_mockup.py --detail /tmp/x.svg --dump world/build3d/city.json
      blender -b --factory-startup -P world/build_city3d.py -- --scene world/build3d/city.json --out world/build3d/city.png
              [--width 1800] [--samples 96] [--check]
--check only places the camera and prints how far the scene's probe points land from where the drawn picture puts them.
"""
import bpy, json, math, os, random, sys
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
S = json.load(open(opt("--scene", os.path.join(HERE, "build3d", "city.json"))))
OUT = os.path.abspath(opt("--out", os.path.join(HERE, "build3d", "city.png")))
WIDTH, SAMPLES = int(opt("--width", 1800)), int(opt("--samples", 96))
CHECK = "--check" in argv
SIEGE, NIGHT = S["siege"], S["night"]
SUN = S["sun"]; R2 = math.sqrt(2)
random.seed(5)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
ROOT = scene.collection

# ---------------------------------------------------------------- plan helpers, as in city_mockup.py
def inpoly(x, y, P):
    c = False
    for (ax, ay), (bx, by) in zip(P, P[1:] + P[:1]):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay): c = not c
    return c
HILL = S["hill"]
def zat(x, y):
    for h in reversed(HILL):
        if inpoly(x, y, h["pts"]): return h["z"] + h["h"]
    return 0.0
def area(pts): return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1])) / 2
def centre(pts): return (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
def rect(cx, cy, w, d, rot=0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
SHORE = S["shore"]
def shore(x):
    i = max(0, min(len(SHORE) - 2, int((x - SHORE[0][0]) / 4))); (x0, y0), (x1, y1) = SHORE[i], SHORE[i + 1]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
LIGHTS = {"#fff1c4", "#ffb347", "#ffcf6e", "#cfe3ff", "#ff8c2a", "#ff9a3a", "#ffbe5c"}
def night(h):
    """The drawing's moonlight, applied to a colour: most of its own hue kept, darkened and cooled (as city_mockup.py's night())."""
    if h.lower() in LIGHTS: return h
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5)); l = .3 * r + .59 * g + .11 * b; mix = lambda c: c * .68 + l * .32
    return "#%02x%02x%02x" % (int(mix(r) * .40 + 10), int(mix(g) * .44 + 16), min(255, int(mix(b) * .56 + 38)))
def lin(h):
    """An sRGB hex colour, as linear RGB for Blender (cooled first, at night)."""
    if NIGHT: h = night(h)
    return tuple(((int(h[i:i + 2], 16) / 255 + .055) / 1.055) ** 2.4 for i in (1, 3, 5))
def shade(h, f): return "#%02x%02x%02x" % tuple(max(0, min(255, int(int(h[i:i + 2], 16) * f))) for i in (1, 3, 5))

# ---------------------------------------------------------------- the camera: the drawn picture's own projection
F = S["frame"]; E = F["elev"]; AW, AH = F["aw"], F["ah"]
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); ROOT.objects.link(cam); scene.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = F["width_m"]; cam.data.sensor_fit = "HORIZONTAL"
cam.data.clip_start = 100; cam.data.clip_end = 6000
toward = Vector((math.cos(E) / R2, -math.cos(E) / R2, math.sin(E)))          # from the crossroads to the camera: southeast and up
cam.location = toward * 2500; cam.rotation_euler = (-toward).to_track_quat("-Z", "Y").to_euler()
scene.render.resolution_x = WIDTH; scene.render.resolution_y = round(WIDTH * AH / AW); scene.render.resolution_percentage = 100
bpy.context.view_layer.update()
worst = 0
for p in S["probes"]:
    co = world_to_camera_view(scene, cam, Vector(p["xyz"])); px = (co.x * AW, (1 - co.y) * AH)
    err = math.hypot(px[0] - p["px"][0], px[1] - p["px"][1]); worst = max(worst, err)
    print("probe %-22s drawn (%7.1f, %7.1f)  rendered (%7.1f, %7.1f)  off %.3f px" % (p["xyz"], *p["px"], *px, err))
print("CAMERA worst probe error %.3f px (of %d)" % (worst, AW))
if CHECK: sys.exit(0)

# ---------------------------------------------------------------- materials
IMAGES, MATS, AVG = {}, {}, {}
def image(path, cs):
    if path not in IMAGES:
        im = bpy.data.images.load(path); im.colorspace_settings.name = cs; IMAGES[path] = im
    return IMAGES[path]
def avg_luma(name):
    """The mean linear luminance of a texture, so tinting by it keeps the drawn colour as the average."""
    if name not in AVG:
        im = image(os.path.join(ASSETS, name, "Diffuse.jpg"), "sRGB"); a = np.empty(len(im.pixels), dtype=np.float32); im.pixels.foreach_get(a)
        a = a.reshape(-1, 4)[::7, :3]; AVG[name] = float(np.mean(a @ np.array([.2126, .7152, .0722], dtype=np.float32)))
    return AVG[name]
def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
    return m, nt, next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
def tinted(nt, tex, rgb, scale, uv=False, bump=.6, vary=.12, raw=0.0):
    """Colour, roughness and normal of a downloaded texture whose brightness pattern is laid over a drawn colour."""
    L = nt.links.new
    if uv: co = nt.nodes.new("ShaderNodeUVMap").outputs[0]
    else: co = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / scale,) * 3; L(co, mp.inputs["Vector"])
    if not uv: mp.inputs["Location"].default_value = (.37, .71, .13)
    t = {}
    if not uv:                                                # a second, larger and turned sampling, blended in by noise, so no tile repeats
        mp2 = nt.nodes.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (1 / (scale * 2.3),) * 3; mp2.inputs["Rotation"].default_value = (0, 0, .7)
        mp2.inputs["Location"].default_value = (.11, .53, .29); L(co, mp2.inputs["Vector"])
        nzm = nt.nodes.new("ShaderNodeTexNoise"); nzm.inputs["Scale"].default_value = .9 / scale; nzm.inputs["Detail"].default_value = 2; L(co, nzm.inputs["Vector"])
        msk = nt.nodes.new("ShaderNodeMapRange"); msk.inputs[1].default_value = .42; msk.inputs[2].default_value = .58; L(nzm.outputs[0], msk.inputs[0])
    for key, cs in (("Diffuse", "sRGB"), ("Rough", "Non-Color"), ("nor_gl", "Non-Color")):
        path = os.path.join(ASSETS, tex, key + ".jpg")
        if not os.path.exists(path): continue
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = image(path, cs); L(mp.outputs[0], n.inputs["Vector"]); t[key] = n.outputs["Color"]
        if not uv:
            n.projection = "BOX"; n.projection_blend = .3
            if key == "nor_gl": continue
            n2 = nt.nodes.new("ShaderNodeTexImage"); n2.image = n.image; n2.projection = "BOX"; n2.projection_blend = .3; L(mp2.outputs[0], n2.inputs["Vector"])
            mm = nt.nodes.new("ShaderNodeMix"); mm.data_type = "RGBA"; L(msk.outputs[0], mm.inputs[0]); L(n.outputs["Color"], mm.inputs[6]); L(n2.outputs["Color"], mm.inputs[7]); t[key] = mm.outputs[2]
    bw = nt.nodes.new("ShaderNodeRGBToBW"); L(t["Diffuse"], bw.inputs[0])
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 1 / avg_luma(tex); L(bw.outputs[0], k.inputs[0])
    # slow variation in brightness, so neither repetition nor flatness shows
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .045; nz.inputs["Detail"].default_value = 3
    L(nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"], nz.inputs["Vector"])
    vr = nt.nodes.new("ShaderNodeMapRange"); vr.inputs[3].default_value = 1 - vary; vr.inputs[4].default_value = 1 + vary; L(nz.outputs[0], vr.inputs[0])
    k2 = nt.nodes.new("ShaderNodeMath"); k2.operation = "MULTIPLY"; L(k.outputs[0], k2.inputs[0]); L(vr.outputs[0], k2.inputs[1])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1
    mx.inputs[6].default_value = (*rgb, 1); L(k2.outputs[0], mx.inputs[7]); col = mx.outputs[2]
    if raw:                                                   # a little of the texture's own colour back in
        mr = nt.nodes.new("ShaderNodeMix"); mr.data_type = "RGBA"; mr.inputs[0].default_value = raw; L(col, mr.inputs[6]); L(t["Diffuse"], mr.inputs[7]); col = mr.outputs[2]
    out = dict(col=col, rough=t.get("Rough"), nor=None)
    if uv and "nor_gl" in t:                                  # UV-mapped (roof tiles): the texture's own normal map
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump; L(t["nor_gl"], nm.inputs["Color"]); out["nor"] = nm.outputs[0]
    elif not uv:                                              # box-projected: relief from the brightness itself (tangent-space maps need UVs)
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .35 * bump; bp.inputs["Distance"].default_value = .04 * scale
        L(bw.outputs[0], bp.inputs["Height"]); out["nor"] = bp.outputs[0]
    return out
def principled(nt, out, d, rough=None, emit=None):
    b = nt.nodes.new("ShaderNodeBsdfPrincipled"); L = nt.links.new
    L(d["col"], b.inputs["Base Color"])
    if d.get("rough") is not None and rough is None: L(d["rough"], b.inputs["Roughness"])
    else: b.inputs["Roughness"].default_value = rough or .85
    if d.get("nor") is not None: L(d["nor"], b.inputs["Normal"])
    L(b.outputs[0], out.inputs["Surface"]); return b

TEX = dict(plaster=("white_rough_plaster", 2.5, .5), stone=("medieval_blocks_05", 2.6, .9), rock=("rocky_terrain_02", 7, 1.0), dirt=("dry_ground_rocks", 4, .8),
           road=("stony_dirt_path", 4, .8), pave=("medieval_blocks_05", 1.3, .7), marble=("marble_01", 3, .3), tile=("clay_roof_tiles", 1.8, 1.0),
           wood=("brown_planks_09", 2, .6), canvas=("hessian_230", 1.2, .4), sand=("coast_sand_01", 4, .5), grass=("aerial_grass_rock", 9, .6), thatch=("thatch_roof_angled", 2, .8))
def mat(key):
    """Materials are named kind:colour, made the first time they are asked for."""
    if key in MATS: return MATS[key]
    kind, _, col = key.partition(":"); rgb = lin(col) if col.startswith("#") else (.5, .5, .5)
    m, nt, out = new_mat(key); L = nt.links.new
    if kind in TEX:
        tex, sc, bump = TEX[kind]
        principled(nt, out, tinted(nt, tex, rgb, sc, uv=kind == "tile", bump=bump, raw=.15 if kind in ("stone", "rock", "dirt", "grass") else 0))
    elif kind == "leaf":                                       # foliage: clumped colour and deep relief, no texture to repeat
        b = nt.nodes.new("ShaderNodeBsdfPrincipled"); pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.7; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = .65; L(pos, nz.inputs["Vector"])
        cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*[c * .45 for c in rgb], 1); cr.color_ramp.elements[1].color = (*[min(1, c * 1.35) for c in rgb], 1)
        cr.color_ramp.elements[0].position = .35; cr.color_ramp.elements[1].position = .68; L(nz.outputs[0], cr.inputs[0]); L(cr.outputs[0], b.inputs["Base Color"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .9; bp.inputs["Distance"].default_value = .4; L(nz.outputs[0], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
        b.inputs["Roughness"].default_value = .75; L(b.outputs[0], out.inputs["Surface"])
    elif kind == "wheat":                                      # standing wheat: grainy heads, darkening down into the furrows
        b = nt.nodes.new("ShaderNodeBsdfPrincipled"); pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
        sep = nt.nodes.new("ShaderNodeSeparateXYZ"); L(pos, sep.inputs[0])
        hz = nt.nodes.new("ShaderNodeMapRange"); hz.inputs[1].default_value = .1; hz.inputs[2].default_value = 1.05; hz.inputs[3].default_value = .38; L(sep.outputs[2], hz.inputs[0])
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.6; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = .62; L(pos, nz.inputs["Vector"])
        cr = nt.nodes.new("ShaderNodeValToRGB"); e = cr.color_ramp.elements
        e[0].position = .3; e[0].color = (rgb[0] * .55, rgb[1] * .5, rgb[2] * .32, 1); e[1].position = .7; e[1].color = (rgb[0] * .95, rgb[1] * .9, rgb[2] * .72, 1)
        L(nz.outputs[0], cr.inputs[0])
        pt = nt.nodes.new("ShaderNodeTexNoise"); pt.inputs["Scale"].default_value = .05; pt.inputs["Detail"].default_value = 3; L(pos, pt.inputs["Vector"])
        pr = nt.nodes.new("ShaderNodeMapRange"); pr.inputs[3].default_value = .85; pr.inputs[4].default_value = 1.12; L(pt.outputs[0], pr.inputs[0])
        f1 = nt.nodes.new("ShaderNodeMath"); f1.operation = "MULTIPLY"; L(hz.outputs[0], f1.inputs[0]); L(pr.outputs[0], f1.inputs[1])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1; L(cr.outputs[0], mx.inputs[6]); L(f1.outputs[0], mx.inputs[7])
        L(mx.outputs[2], b.inputs["Base Color"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .7; bp.inputs["Distance"].default_value = .3; L(nz.outputs[0], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
        b.inputs["Roughness"].default_value = .9; L(b.outputs[0], out.inputs["Surface"])
    elif kind == "emit":
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*rgb, 1); em.inputs[1].default_value = float(opt("--glow", 5)); L(em.outputs[0], out.inputs["Surface"])
    elif kind == "water": water(nt, out, rgb)
    else:                                                      # a plain colour, with a little grain
        b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .45 if kind == "glaze" else .8
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14; nz.inputs["Detail"].default_value = 6; L(nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"], nz.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .25; L(nz.outputs[0], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
        L(b.outputs[0], out.inputs["Surface"])
    MATS[key] = m; return m
def water(nt, out, rgb):
    L = nt.links.new; b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (.8, .95, .95, 1); b.inputs["Roughness"].default_value = .05; b.inputs["IOR"].default_value = 1.33; b.inputs["Transmission Weight"].default_value = 1
    pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .35; nz.inputs["Detail"].default_value = 6; L(pos, nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .06; bp.inputs["Distance"].default_value = .6; L(nz.outputs[0], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    L(lp.outputs["Is Shadow Ray"], mx.inputs[0]); L(b.outputs[0], mx.inputs[1]); L(tr.outputs[0], mx.inputs[2])
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption"); vol.inputs["Color"].default_value = (*rgb, 1); vol.inputs["Density"].default_value = .22
    L(mx.outputs[0], out.inputs["Surface"]); L(vol.outputs[0], out.inputs["Volume"])

# ---------------------------------------------------------------- geometry, gathered per material and made into one object each
GEO = {}
def face(key, pts, uv=None):
    g = GEO.setdefault(key, ([], [], [])); i = len(g[0])
    g[0].extend(pts); g[1].append(list(range(i, i + len(pts)))); g[2].extend(uv or [(p[0], p[1]) for p in pts])
def nrm(pts):
    a, b, c = (Vector(p) for p in pts[:3]); n = Vector((0, 0, 0))
    for p, q in zip(pts, pts[1:] + pts[:1]): n += Vector(p).cross(Vector(q))
    return n
def walls(key, pts, z0, z1, inward=False):
    if (area(pts) > 0) == inward: pts = pts[::-1]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]): face(key, [(x1, y1, z0), (x2, y2, z0), (x2, y2, z1), (x1, y1, z1)])
def cap(key, pts, z, down=False):
    if (area(pts) > 0) == down: pts = pts[::-1]
    face(key, [(x, y, z) for x, y in pts])
def prism(side, top, pts, z0, z1):
    walls(side, pts, z0, z1)
    if top: cap(top, pts, z1)
def roof_face(key, pts):
    """A sloping face whose first edge is the eave: tiles run along the eave and up the slope, and the face looks up."""
    p0, p1 = Vector(pts[0]), Vector(pts[1]); e = (p1 - p0).normalized(); c = sum((Vector(p) for p in pts), Vector()) / len(pts)
    s = (c - p0) - e * (c - p0).dot(e); s.normalize()
    uv = [((Vector(p) - p0).dot(e), (Vector(p) - p0).dot(s)) for p in pts]
    if nrm(pts).z < 0: pts, uv = pts[::-1], uv[::-1]
    face(key, pts, uv)
def cyl(key, cx, cy, r, z0, z1, n=10, r1=None, top=True):
    r1 = r if r1 is None else r1
    ring = lambda rr, z: [(cx + rr * math.cos(2 * math.pi * i / n), cy + rr * math.sin(2 * math.pi * i / n), z) for i in range(n)]
    a, b = ring(r, z0), ring(r1, z1)
    for i in range(n): j = (i + 1) % n; face(key, [a[i], a[j], b[j], b[i]])
    if top and r1 > 0: face(key, b)
def boxr(side, top, cx, cy, w, d, z0, z1, rot=0): prism(side, top, rect(cx, cy, w, d, rot), z0, z1)
def opening(key, p, q, t, w, z0, z1, out=.04):
    """A door or window: a dark panel on the wall from p to q, centred at fraction t."""
    dx, dy = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln; nx, ny = uy * out, -ux * out
    cx, cy = p[0] + dx * t + nx, p[1] + dy * t + ny; hw = w / 2
    face(key, [(cx - ux * hw, cy - uy * hw, z0), (cx + ux * hw, cy + uy * hw, z0), (cx + ux * hw, cy + uy * hw, z1), (cx - ux * hw, cy - uy * hw, z1)])
def build_geo():
    for key, (V, Fc, UV) in GEO.items():
        me = bpy.data.meshes.new(key); me.from_pydata(V, [], Fc); me.validate()
        uvl = me.uv_layers.new(name="UVMap")
        if len(uvl.data) == len(UV): uvl.data.foreach_set("uv", [c for u in UV for c in u])
        me.materials.append(mat(key)); o = bpy.data.objects.new(key, me); ROOT.objects.link(o)

# ---------------------------------------------------------------- downloaded models
LIB = {}; JOIN = {"tree_small_02", "wooden_crate_02"}
def load_asset(name):
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
        if (hi - lo).z > .15 * max((hi - lo).x, (hi - lo).y) and max(hi - lo) > .12: variants.append((c, hi - lo))
    LIB[name] = variants
def place(name, x, y, z, h=None, scale=1.0, rot=None):
    if not LIB.get(name): return None
    c, size = random.choice(LIB[name])
    if h: scale = scale * h / max(1e-3, size.z)
    e = bpy.data.objects.new(name, None); ROOT.objects.link(e); e.instance_type = "COLLECTION"; e.instance_collection = c
    e.location = (x, y, z); e.scale = (scale,) * 3; e.rotation_euler = (0, 0, random.uniform(0, 6.3) if rot is None else rot); return e
for a in ["tree_small_02", "island_tree_02", "searsia_burchellii", "searsia_lucida", "shrub_02", "wild_rooibos_bush", "grass_medium_01", "boulder_01", "ceramic_vase_01", "jug_01"]:
    try: load_asset(a)
    except Exception as ex: print("ASSET FAILED", a, ex); LIB[a] = []

if NIGHT:                                                                           # the downloaded models' own colours, cooled like everything else
    for m in bpy.data.materials:
        if not m.node_tree or m.name in MATS.values(): continue
        for b in [n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"]:
            src = b.inputs["Base Color"]; mx = m.node_tree.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1
            mx.inputs[7].default_value = (.30, .36, .55, 1)
            if src.links: m.node_tree.links.new(src.links[0].from_socket, mx.inputs[6])
            else: mx.inputs[6].default_value = src.default_value[:]
            m.node_tree.links.new(mx.outputs[2], src)

# ---------------------------------------------------------------- ground, sea and beach
GROUND = S["ground"]; HALF, STEP = 340, 2.0
def ground():
    n = int(2 * HALF / STEP) + 1; V, Fc, sand = [], [], []
    for j in range(n):
        for i in range(n):
            x, y = -HALF + i * STEP, -HALF + j * STEP
            if SIEGE: z = 0; s = 0
            else:
                d = y - shore(x)                                          # metres inland of the waterline
                z = 0 if d > 3 else (-.15 + .05 * d if d > -1 else -.2 - min(5, .09 * (-1 - d)))
                s = 1 if d < 5.5 else (0 if d > 8 else (8 - d) / 2.5)
            V.append((x, y, z)); sand.append(s)
    for j in range(n - 1):
        for i in range(n - 1):
            a = j * n + i; Fc.append([a, a + 1, a + n + 1, a + n])
    me = bpy.data.meshes.new("ground"); me.from_pydata(V, [], Fc)
    at = me.color_attributes.new("sand", "FLOAT_COLOR", "POINT"); at.data.foreach_set("color", [c for s in sand for c in (s, s, s, 1)])
    m, nt, out = new_mat("ground"); L = nt.links.new
    gr = tinted(nt, "aerial_grass_rock", lin(shade(GROUND, .97) if SIEGE else "#c4d389"), 9, bump=.6, vary=.16, raw=.08)
    dr = tinted(nt, "dry_ground_rocks", lin(shade(GROUND, .9) if SIEGE else "#c9c08e"), 5, bump=.6)
    sd = tinted(nt, "coast_sand_01", lin("#efe0b8"), 4, bump=.4)
    pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .035; nz.inputs["Detail"].default_value = 6; L(pos, nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange"); ramp.inputs[1].default_value = .52; ramp.inputs[2].default_value = .62; L(nz.outputs[0], ramp.inputs[0])
    m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = "RGBA"; L(ramp.outputs[0], m1.inputs[0]); L(gr["col"], m1.inputs[6]); L(dr["col"], m1.inputs[7])
    attr = nt.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "sand"
    m2 = nt.nodes.new("ShaderNodeMix"); m2.data_type = "RGBA"; L(attr.outputs["Fac"], m2.inputs[0]); L(m1.outputs[2], m2.inputs[6]); L(sd["col"], m2.inputs[7])
    principled(nt, out, dict(col=m2.outputs[2], rough=None, nor=gr["nor"]), rough=.9)
    me.materials.append(m); o = bpy.data.objects.new("ground", me); ROOT.objects.link(o)
    if not SIEGE:
        me = bpy.data.meshes.new("sea"); me.from_pydata([(-HALF, -HALF, -.12), (HALF, -HALF, -.12), (HALF, HALF, -.12), (-HALF, HALF, -.12)], [], [[0, 1, 2, 3]])
        me.materials.append(mat("water:#86c4dc")); o = bpy.data.objects.new("sea", me); ROOT.objects.link(o)
        foam = mat("flat:#f4efe2")
        for off, w_, gap in ():
            V, Fc = [], []; xs = list(range(-HALF, HALF, 2)); g = random.Random(int(off * 10))
            for x in xs:
                if g.random() < gap: continue
                y = shore(x) + off; V += [(x, y - w_ / 2, -.1), (x + 2, shore(x + 2) + off - w_ / 2, -.1), (x + 2, shore(x + 2) + off + w_ / 2, -.1), (x, y + w_ / 2, -.1)]
                Fc.append([len(V) - 4, len(V) - 3, len(V) - 2, len(V) - 1])
            me = bpy.data.meshes.new("foam"); me.from_pydata([(x, y, -.09) for x, y, _ in V], [], Fc); me.materials.append(foam); o = bpy.data.objects.new("foam", me); ROOT.objects.link(o)
ground()

# ---------------------------------------------------------------- where things stand: a 1 m grid of taken ground, for planting
OCC = np.zeros((2 * HALF, 2 * HALF), dtype=bool)
def take_poly(pts, pad=0):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    for gx in range(max(0, int(min(xs) - pad + HALF)), min(2 * HALF, int(max(xs) + pad + HALF) + 1)):
        for gy in range(max(0, int(min(ys) - pad + HALF)), min(2 * HALF, int(max(ys) + pad + HALF) + 1)):
            if pad or inpoly(gx - HALF + .5, gy - HALF + .5, pts): OCC[gx, gy] = True
def take_line(pts, r):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        ln = max(1e-6, math.hypot(x2 - x1, y2 - y1))
        for gx in range(max(0, int(min(x1, x2) - r + HALF)), min(2 * HALF, int(max(x1, x2) + r + HALF) + 1)):
            for gy in range(max(0, int(min(y1, y2) - r + HALF)), min(2 * HALF, int(max(y1, y2) + r + HALF) + 1)):
                px, py = gx - HALF + .5, gy - HALF + .5; t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / ln ** 2))
                if math.hypot(px - x1 - t * (x2 - x1), py - y1 - t * (y2 - y1)) < r: OCC[gx, gy] = True
def free(x, y):
    gx, gy = int(x + HALF), int(y + HALF)
    return 0 <= gx < 2 * HALF and 0 <= gy < 2 * HALF and not OCC[gx, gy]

# ---------------------------------------------------------------- the acropolis
def notch(pts, hw, ytop):
    """A terrace outline with the broad stair's slot cut out of its south side, so the stair stands clear as in the drawing.
    The outline runs anticlockwise, so along its south side it heads east."""
    out = []
    for p, q in zip(pts, pts[1:] + pts[:1]):
        south = p[1] < 122 and q[1] < 122
        if not (south and abs(p[0]) < hw): out.append(p)
        if south and p[0] < -hw <= q[0]: out += [(-hw, p[1] + (q[1] - p[1]) * (-hw - p[0]) / (q[0] - p[0])), (-hw, ytop), (hw, ytop)]
        if south and p[0] < hw <= q[0]: out.append((hw, p[1] + (q[1] - p[1]) * (hw - p[0]) / (q[0] - p[0])))
    return out
STAIR_S = S.get("stair")
for i, h in enumerate(HILL):
    top = i == len(HILL) - 1 and not SIEGE
    if STAIR_S and not top and not SIEGE: h = dict(h, pts=notch(h["pts"], STAIR_S["w"] / 2 + 1.05, STAIR_S["y1"]))
    prism("stone:" + h["wall"] if top else "rock:" + h["wall"], ("marble:" if top else "dirt:") + h["roof"], h["pts"], h["z"], h["z"] + h["h"])
    if top: take_poly(h["pts"])

# ---------------------------------------------------------------- roads, draped on whatever level they cross
ROAD_KIND = {"road": ("road", .04), "street": ("pave", .12), "paving": ("pave", .12)}
ROAD_TINT = dict(S["road_col"], paving="#f3eee2"); ROAD_TINT["road"] = "#d9bc93"
def ribbon(key, pts, w, lift):
    hw = w / 2
    def z(x, y): return zat(x, y) + lift
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        ln = math.hypot(x2 - x1, y2 - y1)
        if ln < 1e-6: continue
        ux, uy = (x2 - x1) / ln, (y2 - y1) / ln; nx, ny = -uy * hw, ux * hw; n = max(1, int(ln / 1.0))
        for k in range(n):
            a, b = k / n, (k + 1) / n; ax, ay, bx, by = x1 + (x2 - x1) * a, y1 + (y2 - y1) * a, x1 + (x2 - x1) * b, y1 + (y2 - y1) * b
            q = [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)]; zs = [z(*p) for p in q]
            if max(zs) - min(zs) > .5: continue                                      # a terrace edge: the road is cut, the rock face shows
            face(key, [(p[0], p[1], zz) for p, zz in zip(q, zs)][::-1])
    for j, (x, y) in enumerate(pts):                                                  # round ends, and joins where the road turns
        if 0 < j < len(pts) - 1:
            (ax, ay), (bx, by) = pts[j - 1], pts[j + 1]; t = math.atan2(by - y, bx - x) - math.atan2(y - ay, x - ax)
            if abs((t + math.pi) % (2 * math.pi) - math.pi) < .2: continue
        zz = z(x, y) + .006 + .002 * (j % 4); ring = [(x + hw * math.cos(t / 8 * math.pi), y + hw * math.sin(t / 8 * math.pi)) for t in range(16)]
        if all(abs(z(*p) - zz) < .5 for p in ring): face(key, [(p[0], p[1], zz) for p in ring])
for i, (w, kind, pts) in enumerate(S["roads"]):                                       # each road a few millimetres above the last: coincident
    if kind not in ROAD_KIND: continue                                                    # faces shadow each other and render black
    tex, lift = ROAD_KIND[kind]; ribbon(tex + ":" + ROAD_TINT[kind], pts, w, lift + .012 * (i % 6)); take_line(pts, w / 2 + 1.2)
for w, kind, pts in S["roads"]:
    if kind == "stair": take_line(pts, w / 2 + 1)

# ---------------------------------------------------------------- flat things: fields, vineyards, tanks, jetties, boats, camps, scrub
VINE = None
def vine_mesh():
    """A vine on its stake: a low leafy clump, made once and instanced along every row."""
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=.62)
    g = random.Random(4)
    for v in bm.verts: v.co.x *= 1.15; v.co.z = v.co.z * .8 + .9; v.co += v.normal * g.uniform(-.08, .1)
    me = bpy.data.meshes.new("vine"); bm.to_mesh(me); bm.free(); me.materials.append(mat("leaf:#5f7d34")); return me
def inst(me, x, y, z, rot=0, sc=(1, 1, 1)):
    o = bpy.data.objects.new(me.name, me); ROOT.objects.link(o); o.location = (x, y, z); o.rotation_euler.z = rot; o.scale = sc; return o
def wheat_field(pts, fill, ax, step):
    """Standing wheat: one surface over the whole field, raised into rounded rows with ragged tops and furrows between."""
    (x0, y0), _, (x1, y1), _ = pts; R = .5; nx, ny = int((x1 - x0) / R) + 1, int((y1 - y0) / R) + 1
    from mathutils import noise as N
    V, Fc = [], []
    for j in range(ny):
        for i in range(nx):
            x, y = min(x1, x0 + i * R), min(y1, y0 + j * R); t = ((x - x0) if ax == "x" else (y - y0)) / step
            ph = (t - math.floor(t)); prof = min(1, max(0, math.cos((ph - .5) * math.pi * 1.2)) * 1.8) ** .8
            edge = min(x - x0, x1 - x, y - y0, y1 - y); fade = max(0, min(1, (edge - .3) / .8))
            h = (.85 + .25 * N.noise(Vector((x * .4, y * .4, 3)))) * prof * fade
            V.append((x, y, .03 + .95 * h + .22 * N.noise(Vector((x * .9, y * .9, 9))) * prof * fade))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i; Fc.append([a, a + 1, a + nx + 1, a + nx])
    me = bpy.data.meshes.new("wheat"); me.from_pydata(V, [], Fc)
    for pl in me.polygons: pl.use_smooth = True
    me.materials.append(mat("wheat:" + fill)); o = bpy.data.objects.new("wheat", me); ROOT.objects.link(o)
for f in S["flat"]:
    if "circle" in f:
        cx, cy, r = f["circle"]; ring = [(cx + r * math.cos(a / 12 * math.pi), cy + r * math.sin(a / 12 * math.pi)) for a in range(24)]
        if f["fill"] in ("#ffb347", "#e8792c", "#fff1c4"):                            # a cooking fire: a ring of stones round embers
            if f["fill"] == "#fff1c4": continue
            for k in range(9): cyl("rock:#8f897c", cx + r * math.cos(k * .7), cy + r * math.sin(k * .7), .28, 0, .3, n=6)
            cap("emit:#ff8c2a", ring, .06); continue
        prism("pave:" + f["stroke"], "pave:" + f["fill"], ring, 0, .25); take_poly(ring, 1); continue  # the threshing floor
    pts, fill, stroke = f["pts"], f["fill"], f["stroke"]
    if fill == "none":                                                                # an estate's boundary: a low dry-stone wall
        for p, q in zip(pts, pts[1:] + pts[:1]):
            dx, dy = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dy); nx, ny = -dy / ln * .35, dx / ln * .35
            prism("stone:#b3a385", "stone:#b3a385", [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)], 0, .9)
            take_line([p, q], 1)
        continue
    take_poly(pts, 0)
    if f.get("rows") and fill != "#c9cf8a":                                           # wheat: standing rows over darker stubble
        wheat_field(pts, fill, *f["rows"]); continue
    if fill == "#c9cf8a":                                                             # a vineyard: rows of vines on stakes, bare earth between
        global_vine = VINE or vine_mesh(); VINE = global_vine
        cap("dirt:#b8ab80", pts, .03)
        (x0, y0), _, (x1, y1), _ = pts; y = y0 + 2.5
        while y < y1:
            x = x0 + 2.2
            while x < x1 - 2: inst(VINE, x + random.uniform(-.15, .15), y, 0, random.uniform(0, 6.3), (1, random.uniform(.8, 1.1), random.uniform(.8, 1.15))); x += 1.5
            y += f["rows"][1]
        continue
    if fill == "#9fd0d6":                                                             # a salting tank: a stone rim round brine
        walls("stone:#d6cbb0", pts, 0, .6); cx, cy = centre(pts); inner = rect(cx, cy, 6.2, 4.2)
        walls("stone:#d6cbb0", inner, 0, .6, inward=True)
        for (a, b), (c, d) in zip(zip(pts, pts[1:] + pts[:1]), zip(inner, inner[1:] + inner[:1])): face("stone:#e2d8bf", [(a[0], a[1], .6), (b[0], b[1], .6), (d[0], d[1], .6), (c[0], c[1], .6)][::-1])
        cap("flat:#a9d6da", inner, .45); continue
    if fill == "#a7865b":                                                             # a jetty: a plank deck on posts
        prism("wood:#8a6a48", "wood:" + fill, pts, .1, .55)
        (ax, ay), (bx, by), (cx_, cy_), (dx, dy) = pts
        for t in (0, .33, .66, 1):
            for (px, py), (qx, qy) in (((ax, ay), (dx, dy)), ((bx, by), (cx_, cy_))): cyl("wood:#5d4630", px + (qx - px) * t, py + (qy - py) * t, .18, -1.5, .8, n=6)
        continue
    if fill == "#7a5a3a":                                                             # a boat: a hull, pointed at both ends
        cx, cy = centre(pts); (ax, ay), (bx, by), (_, _), (dx, dy) = pts
        ux, uy = (dx - ax) / 9, (dy - ay) / 9; vx, vy = (bx - ax) / 3, (by - ay) / 3
        hull = [(cx + ux * 4.5 * c + vx * 1.5 * s * math.sin(math.pi * (c + 1) / 2) ** .7, cy + uy * 4.5 * c + vy * 1.5 * s * math.sin(math.pi * (c + 1) / 2) ** .7)
                for s, cs in ((1, [i / 8 - 1 for i in range(17)]), (-1, [1 - i / 8 for i in range(17)])) for c in cs]
        inner = [(cx + (x - cx) * .78, cy + (y - cy) * .78) for x, y in hull]
        walls("wood:#6d4c2e", hull, -.3, .55); walls("wood:#8e6a44", inner, .1, .55, inward=True); cap("wood:#5a3e26", inner, .12)
        for (a, b), (c, d) in zip(zip(hull, hull[1:] + hull[:1]), zip(inner, inner[1:] + inner[:1])): face("wood:#a07a50", [(a[0], a[1], .55), (b[0], b[1], .55), (d[0], d[1], .55), (c[0], c[1], .55)][::-1])
        continue
    if fill == "#b79d78":                                                             # the clay pit: wet clay, a little below the ground
        cap("dirt:#a8845e", pts, .02); continue
    if fill == "#d6c79c":                                                             # a camp's trampled ground
        cap("road:" + ("#cbb98d"), pts, .02); continue
    # scrub and dry grass round the siege: a patch of rougher ground, then bushes on it
    cap("grass:" + fill, pts, .015)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]; n = int(abs(area(pts)) / 14)
    for _ in range(n):
        x, y = random.uniform(min(xs), max(xs)), random.uniform(min(ys), max(ys))
        if inpoly(x, y, pts) and free(x, y):
            dry = fill in ("#cbb97c", "#a9a56c")
            place(random.choice(("grass_medium_01", "wild_rooibos_bush") if dry else ("searsia_lucida", "wild_rooibos_bush", "searsia_burchellii")), x, y, 0, h=random.uniform(.5, 1.0) if dry else random.uniform(.8, 1.8))

# ---------------------------------------------------------------- buildings and the rest of the solids
STONE_WALLS = {"#c4b594", "#cbbd9e", "#c9bb9c", "#cfc5ae", "#e2d9c4", "#d6ccb8"}
WOOD = {"#8a6a48", "#6b4f33", "#6f5236", "#a9774e", "#7a5a3a"}
TILES = {"#c8673e", "#b5582f", "#d0603a", "#7f9fdc", "#5aa37c", "#a7865b"}
PAVED = {"#d9cdb2", "#ece6d8", "#e8e2d4", "#e4ddcc", "#ece5d6", "#efe6d2", "#ece3cf"}
def side_mat(wall): return ("stone:" if wall in STONE_WALLS else "rock:" if wall == "#9a9486" else "wood:" if wall in WOOD else "plaster:") + wall
def top_mat(roof): return ("tile:" if roof in TILES else "pave:" if roof in PAVED else "wood:" if roof in WOOD else "flat:") + roof
def footing(pts, z):
    """Where a building stands on ground that is not level (a terrace edge), its walls go down to the lowest ground under it."""
    if z <= 0: return z
    cx, cy = centre(pts)
    if abs(z - zat(cx, cy)) > .01: return z
    return min([zat(x, y) for x, y in pts] + [z])
WIN = "flat:#2c2118" if not NIGHT else "flat:#141418"
LITWIN = "emit:#ffbe5c"
def doors_windows(pts, z0, h, rnd, lit=False, door=True, wins=2):
    pts = pts if area(pts) > 0 else pts[::-1]
    edges = list(zip(pts, pts[1:] + pts[:1])); dside = rnd.randrange(len(edges))
    for k, (p, q) in enumerate(edges):
        ln = math.hypot(q[0] - p[0], q[1] - p[1])
        if ln < 3: continue
        if door and k == dside: opening("wood:#4a3524", p, q, rnd.uniform(.3, .7), 1.3, z0, z0 + 2.2)
        for t in [(i + .5) / wins for i in range(wins)] if ln > 6 else [.5]:
            if door and k == dside and abs(t - .5) < .2: continue
            on = lit and rnd.random() < .5
            opening(LITWIN if on else WIN, p, q, t, .8, z0 + h * .5, z0 + h * .5 + 1.1)
def house(s):
    """A courtyard house: rendered walls on a stone footing, a tiled roof sloping out and into the court, a court with a tree or a jar."""
    z0, h = s["z"], s["h"]; top = z0 + h; cx, cy = centre(s["pts"]); zb = footing(s["pts"], z0); rnd = random.Random(int(cx * 7 + cy * 13))
    O7 = rect(cx, cy, 14, 14); wall = side_mat(s["wall"])
    walls(wall, O7, zb, top); walls("stone:#c9b996", rect(cx, cy, 14.12, 14.12), zb, z0 + .7)
    walls(wall, rect(cx, cy, 5, 5), z0, top, inward=True); cap("pave:#e4d6bb", rect(cx, cy, 5, 5), z0 + .03)
    a, m, r, c = 7.5, 4.9, 1.7, 2.5
    sq = lambda e, zz: [(cx - e, cy - e, zz), (cx + e, cy - e, zz), (cx + e, cy + e, zz), (cx - e, cy + e, zz)]
    O, R, I = sq(a, top - .15), sq(m, top + r), sq(c, top); roof = "tile:" + s["roof"]
    for i in range(4):
        j = (i + 1) % 4
        roof_face(roof, [O[i], O[j], R[j], R[i]]); roof_face(roof, [I[j], I[i], R[i], R[j]])
        face("tile:" + shade(s["roof"], .8), [O[i], O[j], (O[j][0], O[j][1], O[j][2] - .22), (O[i][0], O[i][1], O[i][2] - .22)][::-1])   # the eave's edge
        (x1, y1, _), (x2, y2, _) = R[i], R[j]; ux, uy = (x2 - x1) / (2 * m), (y2 - y1) / (2 * m)                               # ridge tiles
        boxr("tile:" + shade(s["roof"], .78), "tile:" + shade(s["roof"], .78), (x1 + x2) / 2, (y1 + y2) / 2, abs(x2 - x1) + .36, abs(y2 - y1) + .36, top + r - .12, top + r + .12)
    doors_windows(O7, z0, h, rnd, lit=s.get("lit"))
    if s.get("jar"): place(rnd.choice(("ceramic_vase_01", "jug_01")), cx - c + 1, cy + c - 1, z0, h=.9)
    k = rnd.random()
    if k < .45: place("island_tree_02", cx + rnd.uniform(-.6, .6), cy + rnd.uniform(-.6, .6), z0, h=rnd.uniform(3.4, 4.6))
    elif k < .7: cyl("stone:#cfc2a4", cx + .8, cy - .8, .55, z0, z0 + .7, n=10); cap("flat:#1e2a2c", [(cx + .8 + .4 * math.cos(t / 5 * math.pi), cy - .8 + .4 * math.sin(t / 5 * math.pi)) for t in range(10)], z0 + .72)
    take_poly(s["pts"], 1)
def hipped(s):
    """A small house with a hipped roof whose ridge runs along its longer side."""
    pts = s["pts"]; z0 = s["z"]; zb = footing(pts, z0); zt = z0 + s["h"]; cx, cy = centre(pts); rnd = random.Random(int(cx * 3 + cy * 5))
    walls(side_mat(s["wall"]) if s["wall"] != "#e9dcc4" else "plaster:#e9dcc4", pts, zb, zt); walls("stone:#c9b996", [(x + (x - cx) * .015, y + (y - cy) * .015) for x, y in pts], zb, z0 + .6)
    xs, ys = [x for x, _ in pts], [y for _, y in pts]; ov = .5
    x0, x1, y0, y1 = min(xs) - ov, max(xs) + ov, min(ys) - ov, max(ys) + ov; zt2 = zt - .1; zr = zt + 1.8; roof = "tile:" + s["roof"]
    if x1 - x0 >= y1 - y0:
        hd = (y1 - y0) / 2; ra, rb = (x0 + hd, cy, zr), (x1 - hd, cy, zr)
        roof_face(roof, [(x1, y1, zt2), (x0, y1, zt2), ra, rb]); roof_face(roof, [(x0, y0, zt2), (x1, y0, zt2), rb, ra])
        roof_face(roof, [(x0, y1, zt2), (x0, y0, zt2), ra]); roof_face(roof, [(x1, y0, zt2), (x1, y1, zt2), rb])
    else:
        hw = (x1 - x0) / 2; ra, rb = (cx, y0 + hw, zr), (cx, y1 - hw, zr)
        roof_face(roof, [(x0, y0, zt2), (x0, y1, zt2), rb, ra]); roof_face(roof, [(x1, y1, zt2), (x1, y0, zt2), ra, rb])
        roof_face(roof, [(x1, y0, zt2), (x0, y0, zt2), ra]); roof_face(roof, [(x0, y1, zt2), (x1, y1, zt2), rb])
    boxr("tile:" + shade(s["roof"], .78), None, (ra[0] + rb[0]) / 2, (ra[1] + rb[1]) / 2, abs(rb[0] - ra[0]) + .3, abs(rb[1] - ra[1]) + .3, zr - .1, zr + .12)
    doors_windows(pts, z0, s["h"], rnd, wins=1); take_poly(pts, 1.5)
def kiln(s):
    """A potter's kiln: a round clay dome on a low drum, with a dark stoking mouth."""
    cx, cy = centre(s["pts"]); r = 2.9; key = "plaster:#b98a62"
    cyl(key, cx, cy, r, 0, 1.2, n=20, top=False)
    for k in range(6):
        a0, a1 = k / 6 * math.pi / 2, (k + 1) / 6 * math.pi / 2
        cyl(key, cx, cy, r * math.cos(a0), 1.2 + 2 * math.sin(a0), 1.2 + 2 * math.sin(a1), n=20, r1=r * math.cos(a1), top=k == 5)
    opening("flat:#24160e", (cx + r, cy - 1), (cx + r, cy + 1), .5, 1.1, .1, 1.1, out=.1); take_poly(s["pts"], 1.5)
def hall(s):
    """A colonnaded hall: stepped base, a walled core, columns, an entablature, a tiled gable roof with pediments."""
    cx, cy, w, d, z = s["cx"], s["cy"], s["w"], s["d"], s["z"]; tent = SIEGE and s["roof"] in ("#efe4cc", "#b5452f")
    stonek = "marble:#ece5d6"
    if tent:                                                                          # a soldier's tent: canvas walls and a canvas ridge
        tk = "canvas:" + s["wall"]; zt = z + s["col_h"] + 1.2; zr = zt + s["roof_h"]
        walls(tk, rect(cx, cy, w, d), z, zt)
        x0, x1, y0, y1 = cx - w / 2 - .2, cx + w / 2 + .2, cy - d / 2 - .2, cy + d / 2 + .2; rk = "canvas:" + s["roof"]
        roof_face(rk, [(x0, y1, zt - .2), (x1, y1, zt - .2), (x1, cy, zr), (x0, cy, zr)]); roof_face(rk, [(x1, y0, zt - .2), (x0, y0, zt - .2), (x0, cy, zr), (x1, cy, zr)])
        for xe, sgn in ((cx - w / 2, -1), (cx + w / 2, 1)): face(tk, [(xe, cy - d / 2, zt), (xe, cy + d / 2, zt), (xe, cy, zr)][::sgn])
        opening("flat:#3b2a1a", (cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2), .5, .9, z, zt - .1); take_poly(s["pts"], 1); return
    if s["steps"]:
        zb = footing(s["pts"], z)
        for i, g in enumerate((2, 1, 0)): prism(stonek, stonek, rect(cx, cy, w + g, d + g), zb if i == 0 else z + .5 * i, z + .5 * (i + 1))
        z += 1.5
    else:
        zb = footing(s["pts"], z)
        if zb < z: prism("stone:#c9b996", None, rect(cx, cy, w, d), zb, z)
    wall = side_mat(s["wall"]); col_h = s["col_h"]
    if s["core"]:
        ox, oy, cw, cd = s["core"]; core = rect(cx + ox, cy + oy, cw, cd); walls(wall, core, z, z + col_h)
        if not s["cols"]: doors_windows(core, z, col_h, random.Random(int(cx * 5 + cy)), wins=max(1, int(max(cw, cd) / 5)))
        else: opening("wood:#4a3524", *[(p[0], p[1]) for p in (core[1], core[2])], .5, 1.8, z, z + min(col_h - .6, 3.8)) if s["cols"] == "all" else None
    def run(x0, y0, x1, y1):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2.4) + 1)
        return [(x0 + (x1 - x0) * k / (n - 1), y0 + (y1 - y0) * k / (n - 1)) for k in range(n)]
    hw, hd = w / 2 - .7, d / 2 - .7
    if s["cols"] == "all": spots = run(-hw, -hd, hw, -hd) + run(-hw, hd, hw, hd) + run(-hw, -hd, -hw, hd)[1:-1] + run(hw, -hd, hw, hd)[1:-1]
    else:
        side = {"n": run(-hw, hd, hw, hd), "s": run(-hw, -hd, hw, -hd), "e": run(hw, -hd, hw, hd), "w": run(-hw, -hd, -hw, hd)}
        spots = [q for k in s["cols"] for q in side[k]]
    ck = "marble:#f7f2e6"
    for a, b in spots:                                                                # base, fluted-looking shaft (many sides), capital
        boxr(ck, ck, cx + a, cy + b, 1.0, 1.0, z, z + .22); cyl(ck, cx + a, cy + b, .4, z + .22, z + col_h - .3, n=14, r1=.34, top=False)
        cyl(ck, cx + a, cy + b, .34, z + col_h - .3, z + col_h - .18, n=14, r1=.5); boxr(ck, ck, cx + a, cy + b, 1.05, 1.05, z + col_h - .18, z + col_h)
    if s["cols"]: cap("pave:#e9e1cf", rect(cx, cy, w - .1, d - .1), z + .02)
    zt = z + col_h; band = "plaster:#efe6d2" if s["cols"] else wall
    prism(band, None, rect(cx, cy, w, d), zt, zt + 1.2)
    if s["cols"]:                                                                     # triglyphs: a row of dark blocks along the frieze
        for p, q in zip(rect(cx, cy, w, d), rect(cx, cy, w, d)[1:] + rect(cx, cy, w, d)[:1]):
            n = int(math.hypot(q[0] - p[0], q[1] - p[1]) / 1.2)
            for k in range(n): opening("plaster:#b8ad97", p, q, (k + .5) / n, .35, zt + .55, zt + 1.1, out=.03)
    zt += 1.2; zr, ov = zt + s["roof_h"], .5; x0, x1, y0, y1 = cx - w / 2 - ov, cx + w / 2 + ov, cy - d / 2 - ov, cy + d / 2 + ov
    roof = "tile:" + s["roof"]; ridge = "tile:" + shade(s["roof"], .78); ped = "marble:#f1eadb" if s["cols"] else wall
    if s["ridge"] == "x":
        roof_face(roof, [(x0, y1, zt), (x1, y1, zt), (x1, cy, zr), (x0, cy, zr)]); roof_face(roof, [(x1, y0, zt), (x0, y0, zt), (x0, cy, zr), (x1, cy, zr)])
        boxr(ridge, ridge, cx, cy, x1 - x0, .36, zr - .12, zr + .14)
        for xe in (cx - w / 2, cx + w / 2):
            tri = [(xe, cy - d / 2, zt), (xe, cy + d / 2, zt), (xe, cy, zr - .1)]
            face(ped, tri if xe > cx else tri[::-1])
    else:
        roof_face(roof, [(x0, y0, zt), (x0, y1, zt), (cx, y1, zr), (cx, y0, zr)]); roof_face(roof, [(x1, y1, zt), (x1, y0, zt), (cx, y0, zr), (cx, y1, zr)])
        boxr(ridge, ridge, cx, cy, .36, y1 - y0, zr - .12, zr + .14)
        for ye in (cy - d / 2, cy + d / 2):
            tri = [(cx + w / 2, ye, zt), (cx - w / 2, ye, zt), (cx, ye, zr - .1)]
            face(ped, tri if ye < cy else tri[::-1])
    take_poly(rect(cx, cy, w + 2, d + 2), 1)
MASONRY_N = 0
def masonry(s):
    """A stretch of wall or a tower: dressed stone, a paved walk on top, merlons along the outer edge."""
    pts = s["pts"]; z0 = s["z"]; zt = z0 + s["h"]; zb = footing(pts, z0)
    global MASONRY_N
    MASONRY_N += 1; zt += .004 * (MASONRY_N % 5)                                               # neighbouring stretches overlap at corners: not coincident
    prism("stone:" + s["wall"], "pave:" + s["roof"], pts, zb, zt)
    for x, y, ang in s.get("merl", []): boxr("stone:" + s["wall"], "pave:" + s["roof"], x, y, 1.2, .9, zt, zt + .95, ang)
    take_poly(pts, 1.5)
def palisade(s):
    """A camp fence: a row of sharpened stakes."""
    pts = s["pts"]; (ax, ay), (bx, by), (cx, cy), (dx, dy) = pts
    p, q = ((ax + dx) / 2, (ay + dy) / 2), ((bx + cx) / 2, (by + cy) / 2); ln = math.hypot(q[0] - p[0], q[1] - p[1]); n = max(1, int(ln / .38))
    g = random.Random(int(p[0] * 31 + p[1] * 17))
    for k in range(n + 1):
        x, y = p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n; h = s["h"] * g.uniform(.9, 1.05)
        cyl("wood:#6f5236", x, y, .18, 0, h, n=6, top=False); cyl("wood:#8a6a48", x, y, .18, h, h + .4, n=6, r1=0)
    take_poly(pts, 1)
def boulder(s):
    cx, cy = centre(s["pts"]); r = max(math.hypot(x - cx, y - cy) for x, y in s["pts"])
    e = place("boulder_01", cx, cy, -.2, h=s["h"] + .3)
    if e: e.scale = (e.scale[0] * r / .9, e.scale[0] * r / .9, e.scale[2])
    take_poly(s["pts"], 1)
def fish_rack(s):
    """Fish racks: posts, two rails, rows of hanging fish."""
    pts = s["pts"]; (ax, ay), (bx, by), (cx, cy), (dx, dy) = pts; x = (ax + bx) / 2
    for y in (ay, dy): cyl("wood:#6d5236", x, y, .12, 0, 2.4, n=6)
    for zr in (1.6, 2.3): boxr("wood:#8a6a48", "wood:#8a6a48", x, (ay + dy) / 2, .1, abs(dy - ay), zr, zr + .1)
    for k in range(14):
        y = ay + (dy - ay) * (k + .5) / 14
        for zr in (1.6, 2.3): boxr("flat:#b9b2a0", "flat:#b9b2a0", x, y, .06, .2, zr - .6, zr)
def solid(s):
    if s.get("kind") == "hall": return hall(s)
    if s.get("hip"): return house(s)
    if s.get("hipr"): return kiln(s) if s["roof"] == "#b98a62" else hipped(s)
    if s.get("merl"): return masonry(s)
    roof, wall = s["roof"], s["wall"]
    if wall == "#6f5236": return palisade(s)
    if roof == "#b2ada0": return boulder(s)
    if roof == "#8a6a48" and wall == "#8a6a48": return fish_rack(s)
    pts, z0 = s["pts"], s["z"]; zt = z0 + s["h"]
    if roof == "#c0281c":                                                             # the standard's cloth
        cx, cy = centre(pts); face("canvas:#b22a1e", [(cx - 1.5, cy, z0), (cx + 1.5, cy, z0 + .2), (cx + 1.5, cy, zt - .1), (cx - 1.5, cy, zt)]); return
    if roof == "#7a5a3a" and abs(area(pts)) < 1:                                      # a pole
        cx, cy = centre(pts); cyl("wood:#5d4630", cx, cy, .2, z0, zt, n=8); return
    if wall in STONE_WALLS or roof in PAVED: return masonry(s)
    prism(side_mat(wall), top_mat(roof), pts, footing(pts, z0), zt); take_poly(pts, 1)
for s in S["solids"]: solid(s)

# ---------------------------------------------------------------- trees
def lathe(name, prof, n=12, wob=.12, seed=1):
    """A tree crown turned from a profile of (radius, height) pairs, roughened so no two read the same way."""
    import bmesh
    bm = bmesh.new(); g = random.Random(seed); rings = []
    for r, z in prof:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / n) * (1 + g.uniform(-wob, wob)), r * math.sin(2 * math.pi * i / n) * (1 + g.uniform(-wob, wob)), z)) for i in range(n)])
    for a, b in zip(rings, rings[1:]):
        for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(rings[-1]); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me
CYPRESS = [lathe("cypress%d" % k, [(.3, 0), (.9, .6)] + [(1.6 * math.sin(math.pi * (.08 + .92 * t)) ** .7 * (1 - .25 * t), .6 + 10.4 * t) for t in (i / 12 for i in range(1, 13))] + [(0.05, 11.1)], n=12, seed=k) for k in range(4)]
for me in CYPRESS: me.materials.append(mat("leaf:#3f6b3a"))
PINE = []
for k in range(4):
    prof = [(.25, 0), (.25, 1.6)]
    for tier, (r, z0, z1) in enumerate(((2.7, 1.6, 4.6), (2.1, 3.8, 6.6), (1.4, 5.8, 8.2), (.7, 7.6, 9.2))):
        prof += [(r * .45, z0), (r, z0 + .25), (r * .15, z1)]
    me = lathe("pine%d" % k, prof + [(0.02, 9.3)], n=11, wob=.18, seed=10 + k); me.materials.append(mat("leaf:#2f5a3c")); PINE.append(me)
for x, y, sp in S["trees"]:
    z = zat(x, y); take_poly(rect(x, y, 3, 3), 0)
    if sp == "cypress": inst(random.choice(CYPRESS), x, y, z - .1, random.uniform(0, 6.3), (random.uniform(.9, 1.1),) * 2 + (random.uniform(.9, 1.08),))
    elif sp == "pine": inst(random.choice(PINE), x, y, z - .1, random.uniform(0, 6.3), (random.uniform(.85, 1.1),) * 2 + (random.uniform(.85, 1.1),))
    else: place(random.choice(("tree_small_02", "island_tree_02", "island_tree_02")), x, y, z - .05, h=random.uniform(5, 6.5))

# ---------------------------------------------------------------- planting the open ground: shrubs, tufts, a few stones
g = random.Random(17)
for _ in range(int(opt("--scatter", 11000))):
    x, y = g.uniform(-HALF + 5, HALF - 5), g.uniform(-HALF + 5, HALF - 5)
    if not free(x, y) or (not SIEGE and y < shore(x) + 9): continue
    z = zat(x, y); k = g.random()
    if k < .35: place("grass_medium_01", x, y, z, h=g.uniform(.45, .8))
    elif k < .6: place("wild_rooibos_bush", x, y, z, h=g.uniform(.7, 1.3))
    elif k < .85: place("searsia_lucida", x, y, z, h=g.uniform(1.0, 2.0))
    elif k < .97: place("searsia_burchellii", x, y, z, h=g.uniform(1.6, 3.0))
    else: place("boulder_01", x, y, z - .2, h=g.uniform(.5, 1.1))

# ---------------------------------------------------------------- lights
for x, y, z, r, kind in S["glows"]:
    L = bpy.data.lights.new("glow", "POINT"); L.energy = (1300 if kind == "fire" else 380) * (r / 5) ** 2; L.color = (1, .62, .3) if kind == "fire" else (1, .74, .42)
    L.shadow_soft_size = .4; o = bpy.data.objects.new("glow", L); ROOT.objects.link(o); o.location = (x, y, z + (.8 if kind == "fire" else .6))
    if kind == "torch": cyl("emit:#ffcf6e", x, y, .22, z, z + .7, n=6, r1=.05)
    else: cyl("emit:#ff9a3a", x, y, .7, 0, 1.1, n=8, r1=.1)
build_geo()
el = math.atan(1 / 1.05)                                                              # the drawing's shadows are 1.05 times the height
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); ROOT.objects.link(sun)
sun.rotation_euler = Vector((SUN[0] * math.cos(el), SUN[1] * math.cos(el), -math.sin(el))).to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True; bg = world.node_tree.nodes["Background"]
if NIGHT:
    sun.data.energy = float(opt("--moon", 6)); sun.data.color = (.78, .85, 1.0); sun.data.angle = math.radians(1.5)
    bg.inputs[0].default_value = (.30, .36, .55, 1); bg.inputs[1].default_value = float(opt("--sky", 1.0))
else:
    sun.data.energy = float(opt("--sun", 4.6)); sun.data.color = (1.0, .95, .86); sun.data.angle = math.radians(2.0)
    bg.inputs[0].default_value = (.58, .72, .95, 1); bg.inputs[1].default_value = float(opt("--sky", .85))

scene.render.engine = "CYCLES"; scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6; scene.cycles.transparent_max_bounces = 24
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()
    for dev in prefs.devices: dev.use = True
    scene.cycles.device = "GPU"
except Exception as ex: print("GPU not enabled:", ex)
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = opt("--look", "AgX - Punchy")
scene.view_settings.exposure = float(opt("--exposure", 0))
if "--border" in argv:                                                                # render only part of the frame (fractions of the width and height, from the top left)
    x0, y0, x1, y1 = map(float, opt("--border", "").split(",")); r = scene.render
    r.use_border = True; r.use_crop_to_border = True; r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = x0, x1, 1 - y1, 1 - y0
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"; scene.render.filepath = OUT
os.makedirs(os.path.dirname(OUT), exist_ok=True)
if "--save" in argv: bpy.ops.wm.save_as_mainfile(filepath=OUT.rsplit(".", 1)[0] + ".blend")
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
