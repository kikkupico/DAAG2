"""Build the city (or the siege) of city_mockup.py as a richly detailed Blender world, in exactly the frame of its southeast picture.

The drawing is the blockout. What must not move is fixed by the page: every place and door, and every road the messengers walk,
with the walker's height along it (the dumped route samples). Everything else is free: a smooth acropolis whose stairs meet the
route heights, varied houses filling the town blocks, estates furnished for their trades, groves, rocks, boats. No people or animals:
the only things that move on the page are the messengers. With the siege scene (--siege --night --detail dump) it builds the night
siege instead: the shut enemy town, camps of tents behind ditch, bank and palisade, siege engines, cut woods, fire and torchlight.
Run:  python3 world/city_mockup.py --detail /tmp/x.svg --dump world/build3d/city.json
      blender -b --factory-startup -P world/build_world3d.py -- --scene world/build3d/city.json --out world/build3d/city.png
              [--width 2400] [--samples 128] [--border x0,y0,x1,y1] [--check]
After building it ray-casts every route sample: from above (is there ground or a stair under the walker, at the walker's height?)
and from the camera (can the walker be seen?), and prints the failures.
"""
import bpy, bmesh, json, math, os, random, sys
import numpy as np
from mathutils import Vector, noise as N
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
S = json.load(open(opt("--scene", os.path.join(HERE, "build3d", "city.json"))))
OUT = os.path.abspath(opt("--out", os.path.join(HERE, "build3d", "city.png")))
WIDTH, SAMPLES = int(opt("--width", 2400)), int(opt("--samples", 128))
SIEGE, NIGHT = S["siege"], S["night"]
SUN = S["sun"]; R2 = math.sqrt(2); TOP = S["top"]
RND = random.Random(5)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene; ROOT = scene.collection

# ================================================================ plan helpers
def inpoly(x, y, P):
    c = False
    for (ax, ay), (bx, by) in zip(P, P[1:] + P[:1]):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay): c = not c
    return c
def area(pts): return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1])) / 2
def centre(pts): return (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
def rect(cx, cy, w, d, rot=0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
def box_pts(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
SHORE = S["shore"]
def shore(x):
    if not SHORE: return -1e9
    i = max(0, min(len(SHORE) - 2, int((x - SHORE[0][0]) / 4))); (x0, y0), (x1, y1) = SHORE[i], SHORE[i + 1]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
LIGHTS = {"#fff1c4", "#ffb347", "#ffcf6e", "#cfe3ff", "#ff8c2a", "#ff9a3a", "#ffbe5c"}
def night(h):
    """The drawing's moonlight, applied to a colour (as city_mockup.py's night())."""
    if h.lower() in LIGHTS: return h
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5)); l = .3 * r + .59 * g + .11 * b; mix = lambda c: c * .68 + l * .32
    return "#%02x%02x%02x" % (int(mix(r) * .40 + 10), int(mix(g) * .44 + 16), min(255, int(mix(b) * .56 + 38)))
def lin(h):
    if NIGHT: h = night(h)
    return tuple(((int(h[i:i + 2], 16) / 255 + .055) / 1.055) ** 2.4 for i in (1, 3, 5))
def shade(h, f): return "#%02x%02x%02x" % tuple(max(0, min(255, int(int(h[i:i + 2], 16) * f))) for i in (1, 3, 5))
def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)

# ================================================================ the camera: the drawn picture's own projection
F = S["frame"]; E = F["elev"]; AW, AH = F["aw"], F["ah"]
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); ROOT.objects.link(cam); scene.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = F["width_m"]; cam.data.sensor_fit = "HORIZONTAL"; cam.data.clip_start = 100; cam.data.clip_end = 6000
TOWARD = Vector((math.cos(E) / R2, -math.cos(E) / R2, math.sin(E)))
cam.location = TOWARD * 2500; cam.rotation_euler = (-TOWARD).to_track_quat("-Z", "Y").to_euler()
scene.render.resolution_x = WIDTH; scene.render.resolution_y = round(WIDTH * AH / AW); scene.render.resolution_percentage = 100
bpy.context.view_layer.update()
worst = max(math.hypot(world_to_camera_view(scene, cam, Vector(p["xyz"])).x * AW - p["px"][0], (1 - world_to_camera_view(scene, cam, Vector(p["xyz"])).y) * AH - p["px"][1]) for p in S["probes"])
print("CAMERA worst probe error %.3f px" % worst)
if "--check" in argv: sys.exit(0)

# ================================================================ materials
IMAGES, MATS, AVG = {}, {}, {}
def image(path, cs):
    if path not in IMAGES:
        im = bpy.data.images.load(path); im.colorspace_settings.name = cs; IMAGES[path] = im
    return IMAGES[path]
def avg_luma(name):
    if name not in AVG:
        im = image(os.path.join(ASSETS, name, "Diffuse.jpg"), "sRGB"); a = np.empty(len(im.pixels), dtype=np.float32); im.pixels.foreach_get(a)
        AVG[name] = float(np.mean(a.reshape(-1, 4)[::7, :3] @ np.array([.2126, .7152, .0722], dtype=np.float32)))
    return AVG[name]
def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
    return m, nt, next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
def tinted(nt, tex, rgb, scale, uv=False, bump=.6, vary=.12, raw=0.0):
    """A downloaded texture's light and dark laid over a chosen colour; box-projected textures are sampled twice against tiling."""
    L = nt.links.new
    co = nt.nodes.new("ShaderNodeUVMap").outputs[0] if uv else nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / scale,) * 3; L(co, mp.inputs["Vector"])
    t = {}
    if not uv:
        mp.inputs["Location"].default_value = (.37, .71, .13)
        mp2 = nt.nodes.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (1 / (scale * 2.3),) * 3; mp2.inputs["Rotation"].default_value = (0, 0, .7)
        mp2.inputs["Location"].default_value = (.11, .53, .29); L(co, mp2.inputs["Vector"])
        nzm = nt.nodes.new("ShaderNodeTexNoise"); nzm.inputs["Scale"].default_value = .9 / scale; nzm.inputs["Detail"].default_value = 2; L(co, nzm.inputs["Vector"])
        msk = nt.nodes.new("ShaderNodeMapRange"); msk.inputs[1].default_value = .42; msk.inputs[2].default_value = .58; L(nzm.outputs[0], msk.inputs[0])
    for key, cs in (("Diffuse", "sRGB"), ("Rough", "Non-Color"), ("nor_gl", "Non-Color")):
        path = os.path.join(ASSETS, tex, key + ".jpg")
        if not os.path.exists(path) or (key == "nor_gl" and not uv): continue
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = image(path, cs); L(mp.outputs[0], n.inputs["Vector"]); t[key] = n.outputs["Color"]
        if not uv:
            n.projection = "BOX"; n.projection_blend = .3
            n2 = nt.nodes.new("ShaderNodeTexImage"); n2.image = n.image; n2.projection = "BOX"; n2.projection_blend = .3; L(mp2.outputs[0], n2.inputs["Vector"])
            mm = nt.nodes.new("ShaderNodeMix"); mm.data_type = "RGBA"; L(msk.outputs[0], mm.inputs[0]); L(n.outputs["Color"], mm.inputs[6]); L(n2.outputs["Color"], mm.inputs[7]); t[key] = mm.outputs[2]
    bw = nt.nodes.new("ShaderNodeRGBToBW"); L(t["Diffuse"], bw.inputs[0])
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 1 / avg_luma(tex); L(bw.outputs[0], k.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .045; nz.inputs["Detail"].default_value = 3
    L(nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"], nz.inputs["Vector"])
    vr = nt.nodes.new("ShaderNodeMapRange"); vr.inputs[3].default_value = 1 - vary; vr.inputs[4].default_value = 1 + vary; L(nz.outputs[0], vr.inputs[0])
    k2 = nt.nodes.new("ShaderNodeMath"); k2.operation = "MULTIPLY"; L(k.outputs[0], k2.inputs[0]); L(vr.outputs[0], k2.inputs[1])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1
    mx.inputs[6].default_value = (*rgb, 1); L(k2.outputs[0], mx.inputs[7]); col = mx.outputs[2]
    if raw:
        mr = nt.nodes.new("ShaderNodeMix"); mr.data_type = "RGBA"; mr.inputs[0].default_value = raw; L(col, mr.inputs[6]); L(t["Diffuse"], mr.inputs[7]); col = mr.outputs[2]
    out = dict(col=col, rough=t.get("Rough"), nor=None)
    if uv and "nor_gl" in t:
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump; L(t["nor_gl"], nm.inputs["Color"]); out["nor"] = nm.outputs[0]
    elif not uv:
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .35 * bump; bp.inputs["Distance"].default_value = .04 * scale
        L(bw.outputs[0], bp.inputs["Height"]); out["nor"] = bp.outputs[0]
    return out
def principled(nt, out, d, rough=None):
    b = nt.nodes.new("ShaderNodeBsdfPrincipled"); L = nt.links.new
    L(d["col"], b.inputs["Base Color"])
    if d.get("rough") is not None and rough is None: L(d["rough"], b.inputs["Roughness"])
    else: b.inputs["Roughness"].default_value = rough or .85
    if d.get("nor") is not None: L(d["nor"], b.inputs["Normal"])
    L(b.outputs[0], out.inputs["Surface"]); return b
def noisy(nt, out, rgb, scale=1.7, lo=.45, hi=1.35, bump=.9, rough=.75, a=.35, b_=.68):
    """A plain colour broken into clumps, with relief: foliage, cloth, straw, clay."""
    L = nt.links.new; b = nt.nodes.new("ShaderNodeBsdfPrincipled"); pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = .65; L(pos, nz.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); e = cr.color_ramp.elements
    e[0].color = (*[c * lo for c in rgb], 1); e[1].color = (*[min(1, c * hi) for c in rgb], 1); e[0].position = a; e[1].position = b_
    L(nz.outputs[0], cr.inputs[0]); L(cr.outputs[0], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = .3; L(nz.outputs[0], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = rough; L(b.outputs[0], out.inputs["Surface"])
TEX = dict(plaster=("white_stucco_02", 3.5, .35), stucco=("white_stucco_02", 2.5, .5), ochre=("yellow_plaster", 2.5, .5), stone=("medieval_blocks_05", 2.6, .9),
           rock=("rocky_terrain_02", 7, 1.0), dirt=("dry_ground_rocks", 4, .8), road=("stony_dirt_path", 4, .8), pave=("medieval_blocks_05", 1.3, .7),
           marble=("marble_01", 3, .3), wood=("brown_planks_09", 2, .6), canvas=("hessian_230", 1.2, .4),
           sand=("coast_sand_01", 4, .5), grass=("aerial_grass_rock", 9, .6), thatch=("thatch_roof_angled", 2, .8))
def mat(key):
    """Materials are named kind:colour and made the first time they are asked for."""
    if key in MATS: return MATS[key]
    kind, _, col = key.partition(":"); rgb = lin(col) if col.startswith("#") else (.5, .5, .5)
    m, nt, out = new_mat(key); L = nt.links.new
    if kind in TEX:
        tex, sc, bump = TEX[kind]
        principled(nt, out, tinted(nt, tex, rgb, sc, uv=False, bump=bump, raw=.15 if kind in ("stone", "rock", "dirt", "grass") else 0))
    elif kind == "tile": noisy(nt, out, rgb, scale=7, lo=.82, hi=1.1, bump=.25, rough=.62, a=.3, b_=.75)
    elif kind == "leaf": noisy(nt, out, rgb)
    elif kind == "straw": noisy(nt, out, rgb, scale=6, lo=.6, hi=1.2, bump=.6, rough=.9)
    elif kind == "cloth": noisy(nt, out, rgb, scale=3, lo=.82, hi=1.08, bump=.15, rough=.9)
    elif kind == "clay": noisy(nt, out, rgb, scale=5, lo=.8, hi=1.1, bump=.2, rough=.6)
    elif kind == "wheat":
        b = nt.nodes.new("ShaderNodeBsdfPrincipled"); pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
        sep = nt.nodes.new("ShaderNodeSeparateXYZ"); L(pos, sep.inputs[0]); att = nt.nodes.new("ShaderNodeAttribute"); att.attribute_name = "h"
        hz = nt.nodes.new("ShaderNodeMapRange"); hz.inputs[1].default_value = .1; hz.inputs[2].default_value = 1.0; hz.inputs[3].default_value = .38; L(att.outputs["Fac"], hz.inputs[0])
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.6; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = .62; L(pos, nz.inputs["Vector"])
        cr = nt.nodes.new("ShaderNodeValToRGB"); e = cr.color_ramp.elements
        e[0].position = .3; e[0].color = (rgb[0] * .55, rgb[1] * .5, rgb[2] * .32, 1); e[1].position = .7; e[1].color = (rgb[0] * .95, rgb[1] * .9, rgb[2] * .72, 1); L(nz.outputs[0], cr.inputs[0])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1; L(cr.outputs[0], mx.inputs[6]); L(hz.outputs[0], mx.inputs[7])
        L(mx.outputs[2], b.inputs["Base Color"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .7; bp.inputs["Distance"].default_value = .3; L(nz.outputs[0], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
        b.inputs["Roughness"].default_value = .9; L(b.outputs[0], out.inputs["Surface"])
    elif kind == "emit":
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*rgb, 1); em.inputs[1].default_value = float(opt("--glow", 9)) * (2.2 if NIGHT and col.lower() in ("#ff8c2a", "#ffb347", "#ffcf6e", "#ff9a3a") else 1); L(em.outputs[0], out.inputs["Surface"])
    elif kind == "water": water(nt, out, rgb)
    elif kind == "net":                                          # a net hung to dry: a dark mesh you see the ground through
        b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Alpha"].default_value = .55; L(b.outputs[0], out.inputs["Surface"])
    else:
        b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .45 if kind == "glaze" else .8
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14; nz.inputs["Detail"].default_value = 6; L(nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"], nz.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .25; L(nz.outputs[0], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
        L(b.outputs[0], out.inputs["Surface"])
    MATS[key] = m; return m
def water(nt, out, rgb):
    """Clear water: transmission over the sea floor, absorption that deepens the colour offshore, small waves catching the sun."""
    L = nt.links.new; b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (.85, .97, 1, 1); b.inputs["Roughness"].default_value = .04; b.inputs["IOR"].default_value = 1.33; b.inputs["Transmission Weight"].default_value = 1
    pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .5; nz.inputs["Detail"].default_value = 8; L(pos, nz.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = .12; wv.inputs["Distortion"].default_value = 6; L(pos, wv.inputs["Vector"])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = "ADD"; L(nz.outputs[0], ad.inputs[0]); L(wv.outputs[1], ad.inputs[1])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .08; bp.inputs["Distance"].default_value = .5; L(ad.outputs[0], bp.inputs["Height"]); L(bp.outputs[0], b.inputs["Normal"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    L(lp.outputs["Is Shadow Ray"], mx.inputs[0]); L(b.outputs[0], mx.inputs[1]); L(tr.outputs[0], mx.inputs[2])
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption"); vol.inputs["Color"].default_value = (*rgb, 1); vol.inputs["Density"].default_value = .22
    L(mx.outputs[0], out.inputs["Surface"]); L(vol.outputs[0], out.inputs["Volume"])

# ================================================================ geometry: faces gathered per material, one object each
GEO = {}; TARGET = [GEO]
def face(key, pts, uv=None):
    g = TARGET[-1].setdefault(key, ([], [], [])); i = len(g[0])
    g[0].extend(pts); g[1].append(list(range(i, i + len(pts)))); g[2].extend(uv or [(p[0], p[1]) for p in pts])
def nrm(pts):
    n = Vector((0, 0, 0))
    for p, q in zip(pts, pts[1:] + pts[:1]): n += Vector(p).cross(Vector(q))
    return n
def walls(key, pts, z0, z1, inward=False):
    if (area(pts) > 0) == inward: pts = pts[::-1]
    z0s = z0 if isinstance(z0, list) else [z0] * len(pts)
    if isinstance(z0, list) and (area(pts) > 0) == inward: pass
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(pts, pts[1:] + pts[:1])): face(key, [(x1, y1, z0), (x2, y2, z0), (x2, y2, z1), (x1, y1, z1)])
def cap(key, pts, z, down=False):
    if (area(pts) > 0) == down: pts = pts[::-1]
    face(key, [(x, y, z) for x, y in pts])
def prism(side, top, pts, z0, z1):
    walls(side, pts, z0, z1)
    if top: cap(top, pts, z1)
def oriented(key, pts, want):
    """A face whose normal points the way wanted."""
    n = nrm(pts)
    face(key, pts if n.dot(Vector(want)) >= 0 else pts[::-1])
def clip_band(P, lo, hi):
    """A convex polygon in (a, b) cut to lo <= b <= hi."""
    def cut(P, keep, at):
        out = []
        for p, q in zip(P, P[1:] + P[:1]):
            ip, iq = keep(p), keep(q)
            if ip: out.append(p)
            if ip != iq: t = (at - p[1]) / (q[1] - p[1]); out.append((p[0] + (q[0] - p[0]) * t, at))
        return out
    P = cut(P, lambda p: p[1] >= lo, lo)
    return cut(P, lambda p: p[1] <= hi, hi) if len(P) > 2 else []
def tiled(key, pts):
    """A roof face built in real tiles: courses of pan tiles, each a slightly different fired colour and lapping over the one
    below, and rows of round cover tiles running from the eave to the ridge, with their open ends showing at the eave."""
    base = key.split(":")[1]; p0 = Vector(pts[0]); e = (Vector(pts[1]) - p0).normalized(); n = nrm(pts).normalized()
    if n.z < 0: n = -n
    s_ = n.cross(e); c = sum((Vector(p) for p in pts), Vector()) / len(pts)
    if (c - p0).dot(s_) < 0: s_ = -s_
    P2 = [((Vector(p) - p0).dot(e), (Vector(p) - p0).dot(s_)) for p in pts]
    if area(P2) < 0: P2 = P2[::-1]
    W = lambda a, b, h=0.0: tuple(p0 + e * a + s_ * b + n * h)
    g = random.Random(int(abs(p0.x * 13 + p0.y * 7 + p0.z * 3) * 10)); bmax = max(b for _, b in P2); CO = .42
    shades = (.86, .92, .97, 1.0, 1.04, 1.1)
    b = 0.0
    while b < bmax - 1e-3:                                                             # courses, each lifted at its lower edge where it laps the course below
        band = clip_band(P2, b, min(bmax, b + CO))
        if len(band) > 2:
            k = "tile:" + shade(base, g.choice(shades))
            oriented(k, [W(a, bb, .045 * (1 - (bb - b) / CO)) for a, bb in band], tuple(n))
        b += CO
    amin, amax = min(a for a, _ in P2), max(a for a, _ in P2); a = amin + .32
    while a < amax - .2:                                                               # cover tiles: a low ridge down the slope, its cut end at the eave
        bs = []
        for (a1, b1), (a2, b2) in zip(P2, P2[1:] + P2[:1]):
            if (a1 - a) * (a2 - a) <= 0 and a1 != a2: bs.append(b1 + (b2 - b1) * (a - a1) / (a2 - a1))
        if len(bs) >= 2 and max(bs) - min(bs) > .4:
            b0, b1 = min(bs) + .02, max(bs) - .05; k = "tile:" + shade(base, g.choice(shades) * .96)
            L0, R0, T0 = W(a - .15, b0, .03), W(a + .15, b0, .03), W(a, b0, .17); L1, R1, T1 = W(a - .15, b1, .03), W(a + .15, b1, .03), W(a, b1, .17)
            oriented(k, [L0, L1, T1, T0], tuple(n - e)); oriented(k, [T0, T1, R1, R0], tuple(n + e)); oriented("tile:" + shade(base, .55), [L0, T0, R0], tuple(-s_))
        a += .58
def roof_face(key, pts):
    """A sloping face whose first edge is the eave: tiles run along the eave and up the slope; the face looks up."""
    if key.startswith("tile:"):
        tiled(key, pts); return
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
def beam(key, p, q, r=.12, n=6):
    """A round timber from one 3-D point to another."""
    p, q = Vector(p), Vector(q); ax = (q - p); L_ = ax.length; ax.normalize()
    u = ax.orthogonal().normalized(); v = ax.cross(u)
    ring = lambda c: [tuple(c + (u * math.cos(2 * math.pi * i / n) + v * math.sin(2 * math.pi * i / n)) * r) for i in range(n)]
    a, b = ring(p), ring(q)
    for i in range(n): j = (i + 1) % n; face(key, [a[i], a[j], b[j], b[i]])
def opening(key, p, q, t, w, z0, z1, out=.04):
    dx, dy = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln; nx, ny = uy * out, -ux * out
    cx, cy = p[0] + dx * t + nx, p[1] + dy * t + ny; hw = w / 2
    face(key, [(cx - ux * hw, cy - uy * hw, z0), (cx + ux * hw, cy + uy * hw, z0), (cx + ux * hw, cy + uy * hw, z1), (cx - ux * hw, cy - uy * hw, z1)])
def to_mesh(name, G):
    """Faces gathered per material into one mesh with material slots."""
    V, Fc, UV, mi = [], [], [], []
    for k, (key, (v, f, uv)) in enumerate(G.items()):
        o = len(V); V += v; UV += uv; Fc += [[i + o for i in ff] for ff in f]; mi += [k] * len(f)
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], Fc); me.validate()
    uvl = me.uv_layers.new(name="UVMap")
    if len(uvl.data) == len(UV): uvl.data.foreach_set("uv", [c for u in UV for c in u])
    for key in G: me.materials.append(mat(key))
    me.polygons.foreach_set("material_index", mi); return me
class Part:
    """Build a reusable prop mesh: `with Part("amphora") as P: ...faces...`; then P.mesh is instanced with inst()."""
    def __init__(s, name): s.name = name; s.G = {}
    def __enter__(s): TARGET.append(s.G); return s
    def __exit__(s, *a): TARGET.pop(); s.mesh = to_mesh(s.name, s.G)
def inst(me, x, y, z, rot=0.0, sc=1.0):
    o = bpy.data.objects.new(me.name, me); ROOT.objects.link(o); o.location = (x, y, z); o.rotation_euler.z = rot
    o.scale = sc if isinstance(sc, tuple) else (sc,) * 3; return o
def put(me, x, y, dz=0.0, rot=0.0, sc=1.0, r=.6):
    """A prop on the ground, unless the ground there is a road or taken."""
    if not free(x, y, r): return None
    return inst(me, x, y, zt(x, y) + dz, rot, sc)
def build_geo():
    for key, G in GEO.items():
        o = bpy.data.objects.new(key, to_mesh(key, {key: G})); ROOT.objects.link(o)

# ================================================================ downloaded models
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
        def mw(o):                                                                     # the object's own transform, through its parents (the collection is not in the scene yet)
            m = o.matrix_basis.copy()
            while o.parent: m = o.parent.matrix_basis @ o.matrix_parent_inverse @ m; o = o.parent
            return m
        pts = [mw(o) @ Vector(v) for o in group for v in o.bound_box]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        c.instance_offset = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)
        if (hi - lo).z > .15 * max((hi - lo).x, (hi - lo).y) and max(hi - lo) > .12: variants.append((c, hi - lo))
    LIB[name] = variants
def place(name, x, y, z, h=None, scale=1.0, rot=None, g=RND):
    if not LIB.get(name): return None
    c, size = g.choice(LIB[name])
    if h: scale = scale * h / max(1e-3, size.z)
    e = bpy.data.objects.new(name, None); ROOT.objects.link(e); e.instance_type = "COLLECTION"; e.instance_collection = c
    e.location = (x, y, z); e.scale = (scale,) * 3; e.rotation_euler = (0, 0, g.uniform(0, 6.3) if rot is None else rot); return e
for a in ["tree_small_02", "island_tree_02", "searsia_burchellii", "searsia_lucida", "shrub_02", "wild_rooibos_bush", "grass_medium_01", "boulder_01",
          "ceramic_vase_01", "jug_01", "wicker_basket_01", "wooden_crate_02"]:
    try: load_asset(a)
    except Exception as ex: print("ASSET FAILED", a, ex); LIB[a] = []
def tint_asset(name, hexcol, fac=.75):
    """Pull a downloaded model's colours toward a chosen one (keeping its light and dark): the boulders become the hill's limestone."""
    mats = {s_.material for c, _ in LIB.get(name, []) for o in c.all_objects if o.type == "MESH" for s_ in o.material_slots if s_.material}
    for m in mats:
        for b in [n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"]:
            src = b.inputs["Base Color"]
            if not src.links: continue
            nt = m.node_tree; bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(src.links[0].from_socket, bw.inputs[0])
            k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 2.6; nt.links.new(bw.outputs[0], k.inputs[0])
            mm = nt.nodes.new("ShaderNodeMix"); mm.data_type = "RGBA"; mm.blend_type = "MULTIPLY"; mm.inputs[0].default_value = 1; mm.inputs[6].default_value = (*lin(hexcol), 1); nt.links.new(k.outputs[0], mm.inputs[7])
            mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs[0].default_value = fac; nt.links.new(src.links[0].from_socket, mx.inputs[6]); nt.links.new(mm.outputs[2], mx.inputs[7])
            nt.links.new(mx.outputs[2], src)
tint_asset("boulder_01", "#cfc8b6")
if NIGHT:                                                                              # the models' own colours, cooled like everything else
    for m in bpy.data.materials:
        if not m.node_tree: continue
        for b in [n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"]:
            src = b.inputs["Base Color"]; mx = m.node_tree.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1
            mx.inputs[7].default_value = (.30, .36, .55, 1)
            if src.links: m.node_tree.links.new(src.links[0].from_socket, mx.inputs[6])
            else: mx.inputs[6].default_value = src.default_value[:]
            m.node_tree.links.new(mx.outputs[2], src)

# ================================================================ the routes: what the ground must carry, and where
ROUTE_SEGS = set()
for r in S["routes"]:
    for a, b in zip(r, r[1:]):
        if a[:2] != b[:2]: ROUTE_SEGS.add((tuple(a), tuple(b)) if tuple(a) < tuple(b) else (tuple(b), tuple(a)))
ROUTE_SEGS = sorted(ROUTE_SEGS)
RAISED = [s for s in ROUTE_SEGS if s[0][2] > 0 or s[1][2] > 0]
ROUTE_PTS = sorted({tuple(p) for r in S["routes"] for p in r})

# ================================================================ the land: one height field, with the acropolis, the shore and gentle undulation
HALF, STEP = 250, 1.0
NX = int(2 * HALF / STEP) + 1
gx = np.linspace(-HALF, HALF, NX); X, Y = np.meshgrid(gx, gx, indexing="xy")      # Z[j, i] is at (gx[i], gx[j])
def np_seg_dist(ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9
    t = np.clip(((X - ax) * dx + (Y - ay) * dy) / L2, 0, 1); return np.hypot(X - ax - t * dx, Y - ay - t * dy)
def np_inpoly(P):
    c = np.zeros(X.shape, dtype=bool)
    for (ax, ay), (bx, by) in zip(P, P[1:] + P[:1]):
        if ay == by: continue
        cond = (ay > Y) != (by > Y); xc = ax + (Y - ay) * (bx - ax) / (by - ay); c ^= cond & (X < xc)
    return c
def np_polydist(P):
    d = np.full(X.shape, 1e9)
    for a, b in zip(P, P[1:] + P[:1]): d = np.minimum(d, np_seg_dist(a[0], a[1], b[0], b[1]))
    return np.where(np_inpoly(P), 0, d)
def fbm(x, y, sc, z=0, oct_=4):
    v = np.zeros_like(x); a = 1.0; f = 1.0
    for _ in range(oct_):
        v += a * np.vectorize(lambda p, q: N.noise(Vector((p * sc * f, q * sc * f, z + f))))(x, y); a *= .5; f *= 2.07
    return v
def chaikin(P, n=2):
    for _ in range(n):
        Q = []
        for a, b in zip(P, P[1:] + P[:1]): Q += [(.75 * a[0] + .25 * b[0], .75 * a[1] + .25 * b[1]), (.25 * a[0] + .75 * b[0], .25 * a[1] + .75 * b[1])]
        P = Q
    return P
def np_edgedist(P):
    d = np.full(X.shape, 1e9)
    for a, b in zip(P, P[1:] + P[:1]): d = np.minimum(d, np_seg_dist(a[0], a[1], b[0], b[1]))
    return d
# The acropolis, redrawn for the rendered world: a long summit running north from the head of the broad stair, its temple on the
# stair's axis facing the gate. Fixed by the page: the summit's level (20 m) and its south-west corner, where the forecourt route
# runs from the stair head (0,104) to (0,114) and west to the west stair at (-46,114); the stair lines themselves; and the ring road
# west of the hill, which messengers walk at ground level. No route goes north of y = 130, so the hill can run on to the north.
PRE3 = [(-26, 101.5), (26, 101.5), (44, 110), (50, 150), (47, 196), (28, 216), (-24, 216), (-46, 198), (-50, 150), (-46, 124), (-46, 106)]
FOOT = chaikin([(0, 40), (40, 47), (72, 64), (102, 96), (122, 142), (126, 192), (112, 242), (70, 270), (0, 278), (-72, 264), (-106, 222), (-110, 170), (-97, 128),
                (-89.5, 114), (-86, 90), (-72, 62), (-40, 47)], 2) if not SIEGE else []
TRACK = [(90, 57), (112, 92), (134, 140), (139, 192), (124, 250), (78, 285), (0, 292), (-80, 278), (-120, 226), (-124, 170), (-112, 128), (-100.6, 112.5)]
ROADS3 = []                                                                            # the roads as built: the drawing's, less the stretch of the north ring road the
for w, kind, pts in S["roads"]:                                                        # larger hill now covers (no messenger walks it), plus a track round the hill's foot
    if kind == "road" and FOOT:
        run = []
        for q in pts:
            if inpoly(q[0], q[1], FOOT): 
                if len(run) > 1: ROADS3.append((w, kind, run))
                run = []
            else: run.append(q)
        if len(run) > 1: ROADS3.append((w, kind, run))
    else: ROADS3.append((w, kind, pts))
if FOOT:
    ROADS3.append((4.5, "road", TRACK))
    ROADS3 += [(6, "paving", [(0, 112), (0, 134)]), (2.6, "road", [(-6, 136), (-30, 150), (-36, 168), (-30, 190), (-10, 200)]), (2.4, "road", [(10, 136), (26, 136), (30, 124)]),
               (2.4, "road", [(10, 178), (24, 190), (10, 200)])]
Z = np.zeros(X.shape)
road_d = np.full(X.shape, 1e9)                                                         # distance to the nearest road
for w, kind, pts in ROADS3:
    for a, b in zip(pts, pts[1:]):
        bx0, bx1 = min(a[0], b[0]) - 40, max(a[0], b[0]) + 40; by0, by1 = min(a[1], b[1]) - 40, max(a[1], b[1]) + 40
        i0, i1 = max(0, int(bx0 + HALF)), min(NX, int(bx1 + HALF) + 1); j0, j1 = max(0, int(by0 + HALF)), min(NX, int(by1 + HALF) + 1)
        if i0 >= i1 or j0 >= j1: continue
        sub = (slice(j0, j1), slice(i0, i1)); xs, ys = X[sub], Y[sub]
        dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy or 1e-9; t = np.clip(((xs - a[0]) * dx + (ys - a[1]) * dy) / L2, 0, 1)
        road_d[sub] = np.minimum(road_d[sub], np.hypot(xs - a[0] - t * dx, ys - a[1] - t * dy) - w / 2)
slow = np.vectorize(lambda p, q: N.noise(Vector((p * .012, q * .012, 7.3))))(X[::4, ::4], Y[::4, ::4])
slow = np.kron(slow, np.ones((4, 4)))[:NX, :NX]
und = np.clip((road_d - 8) / 25, 0, 1) * 1.6 * slow
calm = np.full(X.shape, 1e9)                                                            # and is level round every place, camp and the town
for pl in S["places"].values(): calm = np.minimum(calm, np.hypot(X - pl["at"][0], Y - pl["at"][1]))
for (c, _) in S["camps"].values(): calm = np.minimum(calm, np.hypot(X - c[0], Y - c[1]) - 20)
und = und * np.clip((calm - 40) / 25, 0, 1) * (~np_inpoly([(x * 1.25, y * 1.25) for x, y in S["octagon"]]))                                    # the open country rolls a little; never under a road
if not SIEGE:
    # The hill: from its foot it rises gently, then steepens into a band of crags under the summit's walls. Near the stair
    # lines it leans to the walkers' exact slope, and under each raised route it is carved to that line.
    PRE = PRE3; d_pre = np_polydist(PRE); infoot = np_inpoly(FOOT); d_foot = np_edgedist(FOOT)
    t = np.where(infoot, d_pre / np.maximum(1e-6, d_pre + d_foot), 1.0); u = 1 - t
    rock = fbm(X, Y, .045, 3.1, 5)
    cl = np.clip((u - .38) / .52, 0, 1); cl = cl * cl * (3 - 2 * cl)
    shape = TOP * (.2 * u + .8 * cl) + 5.0 * rock * np.clip(u * (1 - u) * 4, 0, 1) * (u > 0)
    lin_ = TOP * u
    corr = np.full(X.shape, 1e9)
    for (a, b) in RAISED: corr = np.minimum(corr, np_seg_dist(a[0], a[1], b[0], b[1]))
    w = np.clip(1 - (corr - 5) / 12, 0, 1); w = w * w * (3 - 2 * w)
    HILLZ = shape * (1 - w) + lin_ * w
    Z = np.where(infoot, np.maximum(HILLZ, 0), 0)
    Z = np.where(Z > .05, Z, und)
    Z = np.where(np_inpoly(PRE), TOP, Z)
    best = np.full(X.shape, 4.5)
    for (a, b) in RAISED:                                                                  # the walkers' line itself, carved exactly under each raised route (the nearest)
        dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy
        tt = np.clip(((X - a[0]) * dx + (Y - a[1]) * dy) / L2, 0, 1); dd = np.hypot(X - a[0] - tt * dx, Y - a[1] - tt * dy)
        zz = a[2] + (b[2] - a[2]) * tt; Z = np.where(dd < best, zz, Z); best = np.minimum(best, dd)
    sd = Y - np.interp(X, [p[0] for p in SHORE], [p[1] for p in SHORE])                    # metres inland of the waterline
    Z = np.where(sd < 3, np.where(sd > -1, -.15 + .05 * sd, -.2 - np.minimum(16, .06 * (-1 - sd) + .0022 * (-1 - sd) ** 2)), Z)
    SAND = np.clip((9 - sd) / 3, 0, 1)
else:
    Z = und; SAND = np.zeros(X.shape)
ROCKM = np.zeros(X.shape)
gy_, gx_ = np.gradient(Z, STEP); slope = np.hypot(gx_, gy_)
ROCKM = np.clip((slope - .38) / .35, 0, 1)
if not SIEGE:                                                                            # and bare rock breaking through the hill's upper slopes
    rn = np.clip((fbm(X, Y, .08, 8.2, 3) + .15) * 3, 0, 1); inpre = np_inpoly(PRE3)
    ROCKM = np.maximum(ROCKM, np.clip((Z - 6) / 6, 0, 1) * np.where(inpre, .35 + .5 * rn, rn))
def zt(x, y):
    """Ground height anywhere: the height field, bilinear."""
    fx, fy = (x + HALF) / STEP, (y + HALF) / STEP
    if not (0 <= fx < NX - 1 and 0 <= fy < NX - 1): return 0.0
    i, j = int(fx), int(fy); a, b = fx - i, fy - j
    return float(Z[j, i] * (1 - a) * (1 - b) + Z[j, i + 1] * a * (1 - b) + Z[j + 1, i] * (1 - a) * b + Z[j + 1, i + 1] * a * b)
def zmin(pts): return min(zt(x, y) for x, y in pts + [centre(pts)])
def zmax(pts): return max(zt(x, y) for x, y in pts + [centre(pts)])

RES = .25; NI = int(2 * HALF / RES)
def road_image():
    """The dirt roads as a picture laid over the ground: per quarter metre, how far the nearest road's edge is (negative on it)
    and how far across that road the point lies (0 at its middle, 1 at its edge). The ground's material draws the road from it."""
    D = np.full((NI, NI), 30.0, np.float32); LAT = np.ones((NI, NI), np.float32); KIND = np.zeros((NI, NI), np.float32); c = (np.arange(NI) + .5) * RES - HALF
    for w, kind, pts in ROADS3:
        if kind not in ("road", "street", "paving"): continue
        kv = 0.0 if kind == "road" else 1.0
        hw = w / 2
        for a, b in zip(pts, pts[1:]):
            i0, i1 = max(0, int((min(a[0], b[0]) - hw - 8 + HALF) / RES)), min(NI, int((max(a[0], b[0]) + hw + 8 + HALF) / RES) + 1)
            j0, j1 = max(0, int((min(a[1], b[1]) - hw - 8 + HALF) / RES)), min(NI, int((max(a[1], b[1]) + hw + 8 + HALF) / RES) + 1)
            if i0 >= i1 or j0 >= j1: continue
            sx, sy = c[i0:i1][None, :], c[j0:j1][:, None]; dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy or 1e-9
            t = np.clip(((sx - a[0]) * dx + (sy - a[1]) * dy) / L2, 0, 1); dist = np.hypot(sx - a[0] - t * dx, sy - a[1] - t * dy)
            m = (dist - hw) < D[j0:j1, i0:i1]
            D[j0:j1, i0:i1] = np.where(m, dist - hw, D[j0:j1, i0:i1]); LAT[j0:j1, i0:i1] = np.where(m, dist / hw, LAT[j0:j1, i0:i1]); KIND[j0:j1, i0:i1] = np.where(m, kv, KIND[j0:j1, i0:i1])
    img = bpy.data.images.new("roads", NI, NI, alpha=False, float_buffer=True); img.colorspace_settings.name = "Non-Color"
    px = np.zeros((NI, NI, 4), np.float32); px[..., 0] = D; px[..., 1] = LAT; px[..., 2] = KIND; px[..., 3] = 1; img.pixels.foreach_set(px.ravel()); return img
def road_paint(nt, base_col, base_nor):
    """Mix a dirt road into the ground's colour: an edge eaten into by the verge at two scales, a trodden margin, two wheel
    ruts and a grassy crown; stones and dust from the path texture."""
    L = nt.links.new; pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / (2 * HALF),) * 3; mp.inputs["Location"].default_value = (.5, .5, 0); L(pos, mp.inputs["Vector"])
    im = nt.nodes.new("ShaderNodeTexImage"); im.image = road_image(); im.interpolation = "Linear"; im.extension = "EXTEND"; L(mp.outputs[0], im.inputs["Vector"])
    sp = nt.nodes.new("ShaderNodeSeparateColor"); L(im.outputs["Color"], sp.inputs[0])
    def nz(scale, det, z):
        n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = det; n.inputs["Roughness"].default_value = .65
        if "W" in n.inputs: n.noise_dimensions = "4D"; n.inputs["W"].default_value = z
        L(pos, n.inputs["Vector"]); s_ = nt.nodes.new("ShaderNodeMath"); s_.operation = "SUBTRACT"; L(n.outputs[0], s_.inputs[0]); s_.inputs[1].default_value = .5; return s_.outputs[0]
    def madd(a, k, b):
        m = nt.nodes.new("ShaderNodeMath"); m.operation = "MULTIPLY_ADD"; L(a, m.inputs[0]); m.inputs[1].default_value = k
        (L(b, m.inputs[2]) if not isinstance(b, float) else m.inputs[2].__setattr__("default_value", b)); return m.outputs[0]
    amp = nt.nodes.new("ShaderNodeMath"); amp.operation = "MULTIPLY_ADD"; L(sp.outputs[2], amp.inputs[0]); amp.inputs[1].default_value = -.78; amp.inputs[2].default_value = 1.0
    wig = madd(nz(.16, 3, 1.3), 3.2, madd(nz(1.1, 4, 2.7), 1.2, 0.0))
    wm = nt.nodes.new("ShaderNodeMath"); wm.operation = "MULTIPLY"; L(wig, wm.inputs[0]); L(amp.outputs[0], wm.inputs[1])
    e = nt.nodes.new("ShaderNodeMath"); e.operation = "ADD"; L(wm.outputs[0], e.inputs[0]); L(sp.outputs[0], e.inputs[1]); e = e.outputs[0]
    def rng(v, a, b, lo=0., hi=1.):
        m = nt.nodes.new("ShaderNodeMapRange"); L(v, m.inputs[0]); m.inputs[1].default_value = a; m.inputs[2].default_value = b; m.inputs[3].default_value = lo; m.inputs[4].default_value = hi; return m.outputs[0]
    road = rng(e, .3, -.5); margin = rng(e, 3.2, .1, 0, .85)
    nk = nt.nodes.new("ShaderNodeMath"); nk.operation = "MULTIPLY_ADD"; L(sp.outputs[2], nk.inputs[0]); nk.inputs[1].default_value = -1; nk.inputs[2].default_value = 1
    mm_ = nt.nodes.new("ShaderNodeMath"); mm_.operation = "MULTIPLY"; L(margin, mm_.inputs[0]); L(nk.outputs[0], mm_.inputs[1]); margin = mm_.outputs[0]          # streets have no trodden verge
    rd = tinted(nt, "stony_dirt_path", lin("#b9936a"), 4, bump=.9, vary=.22)
    dr = tinted(nt, "dry_ground_rocks", lin("#c2a47a"), 5, bump=.7)
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = "SUBTRACT"; L(sp.outputs[1], ab.inputs[0]); ab.inputs[1].default_value = .45
    ra = nt.nodes.new("ShaderNodeMath"); ra.operation = "ABSOLUTE"; L(ab.outputs[0], ra.inputs[0])
    rut = rng(madd(nz(2.5, 3, 5.1), .08, ra.outputs[0]), .16, .03, 0, .45)
    crown = rng(madd(nz(1.6, 4, 7.7), .9, sp.outputs[1]), .12, -.05, 0, .8)
    def mix(f, a, b, blend="MIX"):
        m = nt.nodes.new("ShaderNodeMix"); m.data_type = "RGBA"; m.blend_type = blend; L(f, m.inputs[0]); (L(a, m.inputs[6]) if not isinstance(a, tuple) else m.inputs[6].__setattr__("default_value", a)); (L(b, m.inputs[7]) if not isinstance(b, tuple) else m.inputs[7].__setattr__("default_value", b)); return m.outputs[2]
    rc = mix(rut, rd["col"], (.62, .55, .47, 1), "MULTIPLY")
    rc = mix(crown, rc, base_col)
    # a town street: worn paving in patches over packed earth, a darker drain down the middle
    pv = tinted(nt, "medieval_blocks_05", lin("#d6c8aa"), 1.3, bump=.7, vary=.15); pe = tinted(nt, "dry_ground_rocks", lin("#c4ae86"), 4, bump=.6)
    patch = rng(madd(nz(.35, 5, 9.1), 1.0, madd(nz(2.2, 3, 3.3), .35, 0.0)), -.12, .12)
    sc = mix(patch, pe["col"], pv["col"]); drain = rng(sp.outputs[1], .1, .04, 0, .55); sc = mix(drain, sc, (.5, .46, .4, 1), "MULTIPLY")
    rc = mix(sp.outputs[2], rc, sc)
    col = mix(margin, base_col, dr["col"]); col = mix(road, col, rc)
    nm = nt.nodes.new("ShaderNodeMix"); nm.data_type = "VECTOR"; L(road, nm.inputs[0]); L(base_nor, nm.inputs[4]); L(rd["nor"], nm.inputs[5])
    return col, nm.outputs[1]
def terrain():
    V = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    idx = np.arange(NX * NX).reshape(NX, NX); a = idx[:-1, :-1].ravel(); b = idx[:-1, 1:].ravel(); c = idx[1:, 1:].ravel(); d = idx[1:, :-1].ravel()
    me = bpy.data.meshes.new("ground"); me.vertices.add(len(V)); me.vertices.foreach_set("co", V.astype(np.float32).ravel())
    nq = len(a); me.loops.add(nq * 4); me.loops.foreach_set("vertex_index", np.stack([a, b, c, d], 1).ravel().astype(np.int32))
    me.polygons.add(nq); me.polygons.foreach_set("loop_start", (np.arange(nq) * 4).astype(np.int32)); me.update(); me.validate()
    for nm, arr in (("sand", SAND), ("rock", ROCKM)):
        at = me.attributes.new(nm, "FLOAT", "POINT"); at.data.foreach_set("value", arr.ravel().astype(np.float32))
    m, nt, out = new_mat("ground"); L = nt.links.new
    gr = tinted(nt, "aerial_grass_rock", lin("#b4bd72" if not SIEGE else shade(S["ground"], .97)), 14, bump=.6, vary=.25, raw=.05)
    dr = tinted(nt, "dry_ground_rocks", lin("#cdbb8c" if not SIEGE else shade(S["ground"], .85)), 5, bump=.6)
    rk = tinted(nt, "rocky_terrain_02", lin("#d2cbbb"), 5, bump=1.4, vary=.2, raw=.1)
    sd = tinted(nt, "coast_sand_01", lin("#efdfb4"), 4, bump=.4)
    pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .022; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = .62; L(pos, nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange"); ramp.inputs[1].default_value = .44; ramp.inputs[2].default_value = .6; L(nz.outputs[0], ramp.inputs[0])
    def mix(f, a_, b_):
        mm = nt.nodes.new("ShaderNodeMix"); mm.data_type = "RGBA"; L(f, mm.inputs[0]); L(a_, mm.inputs[6]); L(b_, mm.inputs[7]); return mm.outputs[2]
    ra = nt.nodes.new("ShaderNodeAttribute"); ra.attribute_name = "rock"; sa = nt.nodes.new("ShaderNodeAttribute"); sa.attribute_name = "sand"
    col = mix(sa.outputs["Fac"], mix(ra.outputs["Fac"], mix(ramp.outputs[0], gr["col"], dr["col"]), rk["col"]), sd["col"])
    nr = nt.nodes.new("ShaderNodeMix"); nr.data_type = "VECTOR"; L(ra.outputs["Fac"], nr.inputs[0]); L(gr["nor"], nr.inputs[4]); L(rk["nor"], nr.inputs[5])
    col, nor = road_paint(nt, col, nr.outputs[1])
    principled(nt, out, dict(col=col, rough=None, nor=nor), rough=.9)
    me.materials.append(m); o = bpy.data.objects.new("ground", me); ROOT.objects.link(o)
    if not SIEGE:
        me = bpy.data.meshes.new("sea"); me.from_pydata([(-HALF - 200, -HALF - 200, -.12), (HALF + 200, -HALF - 200, -.12), (HALF + 200, HALF, -.12), (-HALF - 200, HALF, -.12)], [], [[0, 1, 2, 3]])
        me.materials.append(mat("water:#2c7fbf")); o = bpy.data.objects.new("sea", me); ROOT.objects.link(o)
        g = random.Random(2); V, Fc = [], []
        x = HALF
        while x < HALF:
            ln = g.uniform(2, 7)
            if g.random() < .75:
                for k in range(int(ln)):
                    xa, xb = x + k, x + k + 1; o_ = g.uniform(-.2, .2); w_ = g.uniform(.4, .9)
                    V += [(xa, shore(xa) + o_ - w_, -.1), (xb, shore(xb) + o_ - w_, -.1), (xb, shore(xb) + o_ + .2, -.1), (xa, shore(xa) + o_ + .2, -.1)]; Fc.append(list(range(len(V) - 4, len(V))))
            x += ln + g.uniform(0, 3)
        me = bpy.data.meshes.new("foam"); me.from_pydata(V, [], Fc); me.materials.append(mat("cloth:#f6f2e8")); ROOT.objects.link(bpy.data.objects.new("foam", me))
terrain()

# ================================================================ where things stand: a 1 m grid of taken ground, for furnishing and planting
OCC = np.zeros((NX, NX), dtype=bool)
def take_poly(pts, pad=0):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    for ix in range(max(0, int(min(xs) - pad + HALF)), min(NX, int(max(xs) + pad + HALF) + 1)):
        for iy in range(max(0, int(min(ys) - pad + HALF)), min(NX, int(max(ys) + pad + HALF) + 1)):
            if pad or inpoly(ix - HALF + .5, iy - HALF + .5, pts): OCC[iy, ix] = True
def free(x, y, r=0):
    for dx in ((-r, 0, r) if r else (0,)):
        for dy in ((-r, 0, r) if r else (0,)):
            ix, iy = int(x + dx + HALF), int(y + dy + HALF)
            if not (0 <= ix < NX and 0 <= iy < NX) or OCC[iy, ix]: return False
    return True
OCC |= (road_d < 1.6).T.T                                                               # roads and a margin: nothing stands on a messenger's way
if not SIEGE: OCC |= (Y < np.interp(X, [p[0] for p in SHORE], [p[1] for p in SHORE]) + 7)

g = random.Random(31)                                                                    # weeds and tufts along the dirt roads' verges
for _ in range(int(opt("--verge", 9000))):
    x, y = g.uniform(-HALF + 3, HALF - 3), g.uniform(-HALF + 3, HALF - 3); d = road_d[int(y + HALF), int(x + HALF)]
    if (abs(x) < 6 and 36 < y < 106) or (abs(y - 114) < 4 and -92 < x < 0) or inpoly(x, y, S["octagon"]) or (FOOT and inpoly(x, y, PRE3)): continue
    if 0 < d < 1.8 and N.noise(Vector((x * .3, y * .3, 2.2))) > -.1 and (SIEGE or y > shore(x) + 6):
        place(g.choice(("grass_medium_01", "grass_medium_01", "wild_rooibos_bush", "searsia_lucida")), x, y, zt(x, y), h=g.uniform(.3, .6), g=g)

# ================================================================ roads, draped on the ground
ROAD_MAT = {"road": "road:#d6b98f", "street": "pave:#dccfb6", "paving": "pave:#e9e1cf"}
def ribbon(key, pts, w, lift):
    hw = w / 2
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        ln = math.hypot(x2 - x1, y2 - y1)
        if ln < 1e-6: continue
        ux, uy = (x2 - x1) / ln, (y2 - y1) / ln; nx, ny = -uy * hw, ux * hw; n = max(1, int(ln / 1.0))
        for k in range(n):
            a, b = k / n, (k + 1) / n; ax, ay, bx, by = x1 + (x2 - x1) * a, y1 + (y2 - y1) * a, x1 + (x2 - x1) * b, y1 + (y2 - y1) * b
            q = [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)]
            face(key, [(p[0], p[1], zt(*p) + lift) for p in q][::-1])
    for j, (x, y) in enumerate(pts):
        if 0 < j < len(pts) - 1:
            (ax, ay), (bx, by) = pts[j - 1], pts[j + 1]; t = math.atan2(by - y, bx - x) - math.atan2(y - ay, x - ax)
            if abs((t + math.pi) % (2 * math.pi) - math.pi) < .2: continue
        ring = [(x + hw * math.cos(t / 8 * math.pi), y + hw * math.sin(t / 8 * math.pi)) for t in range(16)]
        face(key, [(p[0], p[1], zt(*p) + lift + .006 + .002 * (j % 4)) for p in ring])
def mud_mat():
    """A dirt road: the path texture, two darker wheel ruts and a grassy crown, and edges eaten away by the verge in a ragged line."""
    if "mud" in MATS: return MATS["mud"]
    m, nt, out = new_mat("mud"); L = nt.links.new
    rd = tinted(nt, "stony_dirt_path", lin("#d3b58a"), 4, bump=.8, vary=.16)
    gr = tinted(nt, "aerial_grass_rock", lin("#a9b26c"), 10, bump=.5)
    pos = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    ea = nt.nodes.new("ShaderNodeAttribute"); ea.attribute_name = "edge"; la = nt.nodes.new("ShaderNodeAttribute"); la.attribute_name = "lat"
    n1 = nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = .55; n1.inputs["Detail"].default_value = 6; n1.inputs["Roughness"].default_value = .7; L(pos, n1.inputs["Vector"])
    a1 = nt.nodes.new("ShaderNodeMath"); a1.operation = "MULTIPLY_ADD"; L(n1.outputs[0], a1.inputs[0]); a1.inputs[1].default_value = 1.1; L(ea.outputs["Fac"], a1.inputs[2])
    cut = nt.nodes.new("ShaderNodeMapRange"); cut.inputs[1].default_value = 1.02; cut.inputs[2].default_value = 1.12; L(a1.outputs[0], cut.inputs[0])     # 0 on the road, 1 off it
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; L(la.outputs["Fac"], ab.inputs[0])
    rut = nt.nodes.new("ShaderNodeMath"); rut.operation = "SUBTRACT"; L(ab.outputs[0], rut.inputs[0]); rut.inputs[1].default_value = .42
    ra = nt.nodes.new("ShaderNodeMath"); ra.operation = "ABSOLUTE"; L(rut.outputs[0], ra.inputs[0])
    rm = nt.nodes.new("ShaderNodeMapRange"); rm.inputs[1].default_value = .14; rm.inputs[2].default_value = .02; rm.inputs[4].default_value = .62; L(ra.outputs[0], rm.inputs[0])
    dark = nt.nodes.new("ShaderNodeMix"); dark.data_type = "RGBA"; dark.blend_type = "MULTIPLY"; L(rm.outputs[0], dark.inputs[0]); L(rd["col"], dark.inputs[6]); dark.inputs[7].default_value = (.72, .64, .55, 1)
    crown = nt.nodes.new("ShaderNodeMapRange"); crown.inputs[1].default_value = .16; crown.inputs[2].default_value = .02; L(ab.outputs[0], crown.inputs[0])
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 1.4; n2.inputs["Detail"].default_value = 4; L(pos, n2.inputs["Vector"])
    cg = nt.nodes.new("ShaderNodeMath"); cg.operation = "MULTIPLY"; L(crown.outputs[0], cg.inputs[0]); L(n2.outputs[0], cg.inputs[1])
    cgm = nt.nodes.new("ShaderNodeMapRange"); cgm.inputs[1].default_value = .3; cgm.inputs[2].default_value = .5; L(cg.outputs[0], cgm.inputs[0])
    col = nt.nodes.new("ShaderNodeMix"); col.data_type = "RGBA"; L(cgm.outputs[0], col.inputs[0]); L(dark.outputs[2], col.inputs[6]); L(gr["col"], col.inputs[7])
    b = principled(nt, out, dict(col=col.outputs[2], rough=None, nor=rd["nor"]), rough=.92)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
    L(cut.outputs[0], mx.inputs[0]); L(b.outputs[0], mx.inputs[1]); L(tr.outputs[0], mx.inputs[2]); L(mx.outputs[0], out.inputs["Surface"])
    MATS["mud"] = m; return m
def mud_road(pts, w, lift, seed):
    """A dirt road as one strip along its whole line (mitred, so it never overlaps itself), wider than its drawn width by a
    ragged verge that the material eats away; its width wanders a little."""
    P = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 1.0)); P += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    P.append(tuple(pts[-1])); hw = w / 2
    offs = [(-hw - 1.3, 1.25), (-hw - .2, .55), (-hw + .7, 0), (0, 0), (hw - .7, 0), (hw + .2, .55), (hw + 1.3, 1.25)]
    V, Fc, EDGE, LAT = [], [], [], []
    for i, (x, y) in enumerate(P):
        a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        wob = 1 + .1 * N.noise(Vector((x * .08, y * .08, seed)))
        for o, e in offs:
            oo = o * (wob if abs(o) > hw - .8 else 1); px, py = x + nx * oo, y + ny * oo
            V.append((px, py, zt(px, py) + lift - (.03 if e > 1 else 0))); EDGE.append(e); LAT.append(o / hw)
    k = len(offs)
    for i in range(len(P) - 1):
        for j in range(k - 1):
            a = i * k + j; Fc.append([a + k, a + k + 1, a + 1, a])
    me = bpy.data.meshes.new("mud"); me.from_pydata(V, [], Fc)
    for nm, arr in (("edge", EDGE), ("lat", LAT)):
        at = me.attributes.new(nm, "FLOAT", "POINT"); at.data.foreach_set("value", arr)
    me.materials.append(mud_mat()); ROOT.objects.link(bpy.data.objects.new("mud", me))
    g = random.Random(seed)                                                                # tufts and weeds along the verges
    for i in range(0, len(P), 2):
        x, y = P[i]; a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) or 1
        for side in (-1, 1):
            if g.random() < .45: continue
            o = side * (hw + g.uniform(-.2, 1.2)); px, py = x - dy / ln * o, y + dx / ln * o
            if not OCC[int(py + HALF), int(px + HALF)] or road_d[int(py + HALF), int(px + HALF)] > -.4:
                place(g.choice(("grass_medium_01", "grass_medium_01", "wild_rooibos_bush")), px, py, zt(px, py), h=g.uniform(.35, .8), g=g)
for i, (w, kind, pts) in enumerate(ROADS3):
    if kind in ("road", "street", "paving"): continue                                      # roads and streets are painted into the ground itself
    if False:
        for a, b in zip(pts, pts[1:]):
            ln = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            for s_ in (-1, 1):
                ox, oy = -uy * (w / 2 + .15) * s_, ux * (w / 2 + .15) * s_; n = max(1, int(ln / 2))
                for k in range(n):
                    p = (a[0] + (b[0] - a[0]) * k / n + ox, a[1] + (b[1] - a[1]) * k / n + oy); q = (a[0] + (b[0] - a[0]) * (k + 1) / n + ox, a[1] + (b[1] - a[1]) * (k + 1) / n + oy)
                    zz = min(zt(*p), zt(*q)); boxr("stone:#cfc3aa", "pave:#d8ccb2", (p[0] + q[0]) / 2, (p[1] + q[1]) / 2, abs(q[0] - p[0]) + .3, abs(q[1] - p[1]) + .3, zz - .1, zz + .18)

# ================================================================ reusable props
def lathe_part(name, prof, key, n=14, wob=0.0, seed=1, smooth=True):
    """A turned shape from (radius, height) pairs: jars, domes, tree crowns."""
    g = random.Random(seed); V = []; rings = []
    bm = bmesh.new()
    for r, z in prof: rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / n) * (1 + g.uniform(-wob, wob)), r * math.sin(2 * math.pi * i / n) * (1 + g.uniform(-wob, wob)), z)) for i in range(n)])
    for a, b in zip(rings, rings[1:]):
        for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(rings[-1][::-1] if prof[-1][0] > 0 else rings[-1])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = smooth
    me.materials.append(mat(key)); return me
AMPH = lathe_part("amphora", [(.02, 0), (.07, .06), (.17, .24), (.2, .42), (.18, .58), (.09, .7), (.055, .74), (.055, .86), (.075, .9), (.01, .91)], "clay:#b4683e")
PITHOS = lathe_part("pithos", [(.18, 0), (.42, .25), (.55, .62), (.5, 1.05), (.3, 1.3), (.32, 1.38), (.02, 1.4)], "clay:#a65d38")
SACK = lathe_part("sack", [(.18, 0), (.3, .12), (.32, .4), (.2, .62), (.08, .7), (.01, .72)], "canvas:#cbb48a", n=9, wob=.08)
HAY = lathe_part("hay", [(2.4, 0), (2.6, .6), (2.4, 1.8), (1.7, 3.0), (.7, 3.8), (.05, 4.1)], "straw:#d7b45f", n=16, wob=.05)
SHEAF = lathe_part("sheaf", [(.25, 0), (.18, .5), (.32, .95), (.05, 1.1)], "straw:#dcbf6c", n=7, wob=.1)
CYPRESS = [lathe_part("cypress%d" % k, [(.3, 0), (.9, .6)] + [(1.6 * math.sin(math.pi * (.08 + .92 * t)) ** .7 * (1 - .25 * t), .6 + 10.4 * t) for t in (i / 12 for i in range(1, 13))] + [(.05, 11.1)], "leaf:#3c6634", n=12, wob=.12, seed=k) for k in range(4)]
PINE = []
for k in range(4):
    prof = [(.25, 0), (.25, 1.6)]
    for r_, z0, z1 in ((2.7, 1.6, 4.6), (2.1, 3.8, 6.6), (1.4, 5.8, 8.2), (.7, 7.6, 9.2)): prof += [(r_ * .45, z0), (r_, z0 + .25), (r_ * .15, z1)]
    PINE.append(lathe_part("pine%d" % k, prof + [(.02, 9.3)], "leaf:#2e5838", n=11, wob=.18, seed=10 + k))
VINE = lathe_part("vine", [(.15, .1), (.55, .5), (.7, .95), (.55, 1.35), (.1, 1.5)], "leaf:#5b7a32", n=9, wob=.2)
with Part("crate") as P_: boxr("wood:#9a7448", "wood:#a98052", 0, 0, .9, .7, 0, .6); CRATE = P_
CRATE = P_.mesh
with Part("cart") as P_:                                                               # a two-wheeled cart, its shafts resting on the ground
    boxr("wood:#8c6a44", "wood:#9d784c", 0, 0, 2.4, 1.4, .75, .9)
    for s_ in (-1, 1): boxr("wood:#7d5c3a", "wood:#7d5c3a", 0, s_ * .68, 2.4, .08, .9, 1.3)
    for s_ in (-1, 1):
        for k in range(12):
            a0, a1 = k / 12 * 2 * math.pi, (k + 1) / 12 * 2 * math.pi; r_ = .55
            face("wood:#5e4329", [(r_ * math.cos(a0) - .1, s_ * .82, .55 + r_ * math.sin(a0)), (r_ * math.cos(a1) - .1, s_ * .82, .55 + r_ * math.sin(a1)), (r_ * math.cos(a1) - .1, s_ * .9, .55 + r_ * math.sin(a1)), (r_ * math.cos(a0) - .1, s_ * .9, .55 + r_ * math.sin(a0))])
        face("wood:#5e4329", [(.55 * math.cos(k / 12 * 2 * math.pi) - .1, s_ * .9, .55 + .55 * math.sin(k / 12 * 2 * math.pi)) for k in range(12)])
    for s_ in (-1, 1): beam("wood:#7d5c3a", (1.2, s_ * .5, .85), (3.4, s_ * .4, .08), r=.06)
CART = P_.mesh
with Part("boat") as P_:                                                               # a fishing boat: planked hull, thwarts, a stubby mast
    L_, B_, D_ = 6.5, 1.9, .8; secs = 14; prev = None
    for i in range(secs + 1):
        t = i / secs; x = (t - .5) * L_; hw = B_ / 2 * math.sin(math.pi * t) ** .65 + .02; sh = .25 * (2 * t - 1) ** 2
        sec = [(x, -hw, D_ + sh), (x, -hw * .85, .35), (x, 0, 0), (x, hw * .85, .35), (x, hw, D_ + sh)]
        if prev:
            for k in range(4): face("wood:#6e4a2c", [prev[k], sec[k], sec[k + 1], prev[k + 1]][::-1])
            face("wood:#a8875c", [(prev[1][0], prev[1][1], .45), (sec[1][0], sec[1][1], .45), (sec[3][0], sec[3][1], .45), (prev[3][0], prev[3][1], .45)])
        prev = sec
    for xx in (-1.2, .3, 1.6): boxr("wood:#8a6a44", "wood:#8a6a44", xx, 0, .2, B_ * .8, .62, .7)
    beam("wood:#6b5032", (.2, 0, .5), (.2, 0, 3.8), r=.07); beam("wood:#6b5032", (-1.8, 0, 3.4), (2.0, 0, 3.6), r=.04)
    face("cloth:#e7dcc3", [(-1.7, .05, 3.3), (1.9, .05, 3.5), (1.6, .05, 3.0), (-1.4, .05, 2.9)])
BOAT = P_.mesh
with Part("ship") as P_:                                                               # a merchant ship: deep hull, curved stern post, square sail on its yard
    L_, B_, D_ = 17, 5.2, 2.4; secs = 22; prev = None
    for i in range(secs + 1):
        t = i / secs; x = (t - .5) * L_; hw = B_ / 2 * math.sin(math.pi * min(1, t * 1.05)) ** .55 + .05; sh = .9 * (2 * t - 1) ** 2 + (1.6 * max(0, t - .85) / .15) ** 2
        sec = [(x, -hw, D_ + sh), (x, -hw * .9, 1.0), (x, 0, -.4), (x, hw * .9, 1.0), (x, hw, D_ + sh)]
        if prev:
            for k in range(4): face("wood:#5d3d24" if k in (0, 3) else "wood:#3e2818", [prev[k], sec[k], sec[k + 1], prev[k + 1]][::-1])
            face("wood:#b08a5c", [(prev[1][0], prev[1][1], D_ - .1), (sec[1][0], sec[1][1], D_ - .1), (sec[3][0], sec[3][1], D_ - .1), (prev[3][0], prev[3][1], D_ - .1)])
        prev = sec
    boxr("wood:#7a5a38", "wood:#8f6a42", -5.6, 0, 3, 3.2, D_ - .1, D_ + 1.2)
    beam("wood:#5b4128", (1, 0, D_), (1, 0, D_ + 11), r=.18); beam("wood:#5b4128", (1, -5.5, D_ + 10), (1, 5.5, D_ + 10), r=.1)
    for k in range(6):
        y0, y1 = -5.2 + k * 10.4 / 6, -5.2 + (k + 1) * 10.4 / 6
        face("cloth:" + ("#efe4cc" if k % 2 else "#b8442e"), [(1.35, y0, D_ + 10), (1.35, y1, D_ + 10), (1.7, y1, D_ + 4.5), (1.7, y0, D_ + 4.5)])
    for k in range(9): beam("wood:#6b4a2c", (-6 + k * 1.5, 2.7, D_ - .2), (-6.5 + k * 1.5, 4.2, .1), r=.05); beam("wood:#6b4a2c", (-6 + k * 1.5, -2.7, D_ - .2), (-6.5 + k * 1.5, -4.2, .1), r=.05)
SHIP = P_.mesh
with Part("stall") as P_:                                                              # a market stall: four posts, a counter, a sloping cloth awning
    for x, y in ((-1.4, -1), (1.4, -1), (-1.4, 1), (1.4, 1)): beam("wood:#6b5032", (x, y, 0), (x, y, 2.4 if y < 0 else 2.0), r=.06)
    boxr("wood:#8c6a44", "wood:#9d784c", 0, -.6, 2.8, .9, 0, .95)
STALL = P_.mesh
AWNINGS = []
for c_ in ("#b8442e", "#d9c49a", "#3f6a8a", "#c98a2e", "#7b8f4a"):
    with Part("awning") as P_:
        face("cloth:" + c_, [(-1.6, -1.25, 2.45), (1.6, -1.25, 2.45), (1.6, 1.2, 2.0), (-1.6, 1.2, 2.0)])
        face("cloth:" + shade(c_, .8), [(-1.6, -1.25, 2.45), (1.6, -1.25, 2.45), (1.6, -1.25, 2.1), (-1.6, -1.25, 2.1)][::-1])
    AWNINGS.append(P_.mesh)
with Part("rack") as P_:                                                               # a drying rack hung with split fish
    for y in (-2, 2): beam("wood:#6d5236", (0, y, 0), (0, y, 2.3), r=.08)
    for z_ in (1.5, 2.2): beam("wood:#8a6a48", (0, -2.1, z_), (0, 2.1, z_), r=.05)
    for k in range(16):
        y = -1.9 + k * 3.8 / 15
        for z_ in (1.5, 2.2): boxr("flat:#c7bda6", "flat:#c7bda6", 0, y, .05, .16, z_ - .55, z_ - .02)
RACK = P_.mesh
with Part("netframe") as P_:                                                           # fishing nets hung over a pole to dry
    for x in (-2.2, 2.2): beam("wood:#6d5236", (x, 0, 0), (x, 0, 2.2), r=.07)
    beam("wood:#8a6a48", (-2.4, 0, 2.2), (2.4, 0, 2.2), r=.05)
    for s_ in (-1, 1):
        pts = []
        for k in range(9):
            x = -2.2 + k * 4.4 / 8; sag = .25 * math.sin(math.pi * k / 8)
            pts.append(((x, 0, 2.2), (x, s_ * 1.1, .2 + sag)))
        for (a, b), (c, d) in zip(pts, pts[1:]): face("net:#4a3a2a", [a, c, d, b] if s_ > 0 else [b, d, c, a])
NETS = P_.mesh
with Part("woodpile") as P_:
    for k in range(5):
        for j in range(4 - k % 2): beam("wood:#7a5634", (-1.2, -.9 + j * .45 + (k % 2) * .22, .12 + k * .22), (1.2, -.9 + j * .45 + (k % 2) * .22, .12 + k * .22), r=.11, n=7)
WOODPILE = P_.mesh
with Part("well") as P_:
    cyl("stone:#cbbd9f", 0, 0, .75, 0, .8, n=14); cyl("flat:#1f2b2d", 0, 0, .55, .79, .8, n=14)
    for x in (-.8, .8): beam("wood:#6d5236", (x, 0, .8), (x, 0, 2.1), r=.06)
    beam("wood:#6d5236", (-.9, 0, 2.05), (.9, 0, 2.05), r=.06)
WELL = P_.mesh
with Part("press") as P_:                                                              # a beam press for grapes: stone treading floor, the long beam, the weight stone
    boxr("stone:#cdbf9f", "stone:#d8cdb3", 0, 0, 3.6, 3.0, 0, .55); boxr("flat:#5a2f3a", None, 0, 0, 3.0, 2.4, .5, .56)
    beam("wood:#5b3f26", (-2.4, 0, 2.3), (4.5, 0, 1.5), r=.18); beam("wood:#5b3f26", (-2.4, -.4, 0), (-2.4, -.4, 2.8), r=.15); beam("wood:#5b3f26", (-2.4, .4, 0), (-2.4, .4, 2.8), r=.15)
    cyl("stone:#9b9483", 4.5, 0, .5, 0, .8, n=10)
PRESS = P_.mesh
with Part("statue") as P_:                                                             # a marble figure on its plinth
    boxr("marble:#e9e2d2", "marble:#efe9db", 0, 0, 1.1, 1.1, 0, 1.3)
    for z0, z1, r0, r1 in ((1.3, 2.3, .3, .25), (2.3, 2.95, .25, .2), (2.95, 3.05, .09, .09)): cyl("marble:#f4efe4", 0, 0, r0, z0, z1, n=10, r1=r1)
    cyl("marble:#f4efe4", 0, 0, .14, 3.05, 3.3, n=10, r1=.1)
STATUE = P_.mesh
with Part("bench") as P_: boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, 2.4, .5, 0, .45); BENCH = P_
BENCH = P_.mesh
with Part("altar") as P_:
    boxr("marble:#e4ddcc", "marble:#ece6d8", 0, 0, 6.5, 3.5, 0, .35); boxr("marble:#ece6d8", "marble:#f2ede2", 0, 0, 5, 2.4, .35, 1.6)
    for x in (-2.3, 2.3): cyl("marble:#f2ede2", x, 0, .35, 1.6, 2.0, n=10)
    cyl("emit:#ff9a3a" if NIGHT else "flat:#2c2420", 0, 0, .45, 1.6, 1.75, n=10)
ALTAR = P_.mesh
with Part("beehive") as P_: cyl("straw:#c9a75a", 0, 0, .35, 0, .5, n=10, r1=.12); BEEHIVE = P_
BEEHIVE = P_.mesh
with Part("loom") as P_:                                                               # a potter's wheel under its little shade
    cyl("stone:#b9ac90", 0, 0, .45, 0, .5, n=12); cyl("clay:#9c5a36", 0, 0, .25, .5, .8, n=10, r1=.12)
WHEEL = P_.mesh
def scatter_jars(cx, cy, z, n, r, g, kinds=(AMPH, AMPH, AMPH, PITHOS)):
    """A heap of jars on the ground, standing or tipped against each other."""
    for k in range(n):
        a = g.uniform(0, 6.3); d = r * math.sqrt(g.random()); x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        if not free(x, y): continue
        o = inst(g.choice(kinds), x, y, zt(x, y) if z is None else z, g.uniform(0, 6.3), g.uniform(.9, 1.15))
        if g.random() < .2: o.rotation_euler.x = g.uniform(1.2, 1.5); o.location.z += .2
def amph_rows(x0, y0, x1, y1, z, g, gap=.48):
    """Amphorae in ordered rows, as in a store or a drying yard."""
    y = y0
    while y < y1:
        x = x0
        while x < x1: inst(AMPH, x + g.uniform(-.05, .05), y, z, g.uniform(0, 6.3), g.uniform(.95, 1.05)); x += gap
        y += gap

# ================================================================ buildings
WALLCOLS = ["#f1e7d2", "#eddcc0", "#f4ecdc", "#e8d3ac", "#efe0c6", "#e2c79a"]
TILECOLS = ["#c0643f", "#b05a36", "#c27250", "#a5583a", "#c98060", "#b8694a", "#a8664c"]
WIN = "flat:#2c2118" if not NIGHT else "flat:#141418"
LITWIN = "emit:#ffbe5c"
def wall_kind(col): return ("ochre:" if col in ("#e3d2b2", "#d9c49e") else "plaster:") + col
def fenestrate(pts, z0, storeys, g, lit=False, door_side=None, shutters=True):
    """Doors on the ground floor, shuttered windows above: on every outer wall long enough to take them."""
    pts = pts if area(pts) > 0 else pts[::-1]; edges = list(zip(pts, pts[1:] + pts[:1]))
    ds = g.randrange(len(edges)) if door_side is None else door_side
    for k, (p, q) in enumerate(edges):
        ln = math.hypot(q[0] - p[0], q[1] - p[1])
        if ln < 3: continue
        if k == ds: opening("wood:#4a3524", p, q, g.uniform(.3, .7), 1.3, z0, z0 + 2.3)
        nwin = max(1, int(ln / 3.4))
        for s_ in range(storeys):
            zw = z0 + 1.15 + s_ * 3.1 + (.4 if s_ == 0 else 0)
            for i in range(nwin):
                t = (i + .5) / nwin
                if s_ == 0 and k == ds and abs(t - .5) < .3: continue
                if g.random() < .25: continue
                on = lit and g.random() < .45
                opening(LITWIN if on else WIN, p, q, t, .75, zw, zw + 1.0)
                if shutters and not NIGHT and g.random() < .6:
                    col = g.choice(("#5f7f8f", "#6b5032", "#4f6b4a", "#8a3b2a"))
                    for o_ in (-.6, .6): opening("wood:" + col, p, q, t + o_ / ln, .38, zw, zw + 1.0, out=.06)
def hip_roof(x0, y0, x1, y1, zt_, rise, key):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; zr = zt_ + rise
    if x1 - x0 >= y1 - y0:
        hd = (y1 - y0) / 2; ra, rb = (x0 + hd, cy, zr), (x1 - hd, cy, zr)
        roof_face(key, [(x1, y1, zt_), (x0, y1, zt_), ra, rb]); roof_face(key, [(x0, y0, zt_), (x1, y0, zt_), rb, ra])
        roof_face(key, [(x0, y1, zt_), (x0, y0, zt_), ra]); roof_face(key, [(x1, y0, zt_), (x1, y1, zt_), rb])
    else:
        hw = (x1 - x0) / 2; ra, rb = (cx, y0 + hw, zr), (cx, y1 - hw, zr)
        roof_face(key, [(x0, y0, zt_), (x0, y1, zt_), rb, ra]); roof_face(key, [(x1, y1, zt_), (x1, y0, zt_), ra, rb])
        roof_face(key, [(x1, y0, zt_), (x0, y0, zt_), ra]); roof_face(key, [(x0, y1, zt_), (x1, y1, zt_), rb])
    rk = key.split(":")[0] + ":" + shade(key.split(":")[1], .78)
    boxr(rk, rk, (ra[0] + rb[0]) / 2, (ra[1] + rb[1]) / 2, abs(rb[0] - ra[0]) + .3, abs(rb[1] - ra[1]) + .3, zr - .1, zr + .12)
def gable_roof(x0, y0, x1, y1, zt_, rise, key, wallk, along_x=None):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; zr = zt_ + rise; ax = (x1 - x0 >= y1 - y0) if along_x is None else along_x; ov = .45
    rk = key.split(":")[0] + ":" + shade(key.split(":")[1], .78)
    if ax:
        roof_face(key, [(x0 - ov, y1 + ov, zt_ - .15), (x1 + ov, y1 + ov, zt_ - .15), (x1 + ov, cy, zr), (x0 - ov, cy, zr)]); roof_face(key, [(x1 + ov, y0 - ov, zt_ - .15), (x0 - ov, y0 - ov, zt_ - .15), (x0 - ov, cy, zr), (x1 + ov, cy, zr)])
        boxr(rk, rk, cx, cy, x1 - x0 + 2 * ov, .3, zr - .1, zr + .12)
        for xe in (x0, x1): face(wallk, [(xe, y0, zt_), (xe, y1, zt_), (xe, cy, zr - .05)][::(1 if xe == x1 else -1)])
    else:
        roof_face(key, [(x0 - ov, y0 - ov, zt_ - .15), (x0 - ov, y1 + ov, zt_ - .15), (cx, y1 + ov, zr), (cx, y0 - ov, zr)]); roof_face(key, [(x1 + ov, y1 + ov, zt_ - .15), (x1 + ov, y0 - ov, zt_ - .15), (cx, y0 - ov, zr), (cx, y1 + ov, zr)])
        boxr(rk, rk, cx, cy, .3, y1 - y0 + 2 * ov, zr - .1, zr + .12)
        for ye in (y0, y1): face(wallk, [(x1, ye, zt_), (x0, ye, zt_), (cx, ye, zr - .05)][::(1 if ye == y0 else -1)])
def footing(pts, side="stone:#c7b794"):
    """A level base for a building on sloping ground: the highest ground under it, with stone walls down to the lowest."""
    lo, hi = zmin(pts), zmax(pts)
    if hi - lo > .15: prism(side, None, pts, lo - .3, hi)
    return hi
def court_house(x0, y0, x1, y1, g, lit=False, roofc=None, storeys=1):
    """A courtyard house: rooms round an open court, a tiled roof sloping out to the street and in to the court."""
    pts = box_pts(x0, y0, x1, y1); z0 = footing(pts); h = 3.1 * storeys + .5; top = z0 + h
    wallc = g.choice(WALLCOLS); wk = wall_kind(wallc); roofk = "tile:" + (roofc or g.choice(TILECOLS))
    walls(wk, pts, z0, top); walls("stone:#c9b996", box_pts(x0 - .06, y0 - .06, x1 + .06, y1 + .06), z0 - .3, z0 + .6)
    wing = min(4.2, (x1 - x0) * .32, (y1 - y0) * .32); cx0, cy0, cx1, cy1 = x0 + wing, y0 + wing, x1 - wing, y1 - wing
    court = box_pts(cx0, cy0, cx1, cy1); walls(wk, court, z0, top, inward=True); cap("pave:#e2d4b8", court, z0 + .03)
    ov = .45; O = [(x0 - ov, y0 - ov, top - .12), (x1 + ov, y0 - ov, top - .12), (x1 + ov, y1 + ov, top - .12), (x0 - ov, y1 + ov, top - .12)]
    I = [(cx0, cy0, top), (cx1, cy0, top), (cx1, cy1, top), (cx0, cy1, top)]; m = wing / 2 + .1; rise = 1.5
    R = [(x0 + m, y0 + m, top + rise), (x1 - m, y0 + m, top + rise), (x1 - m, y1 - m, top + rise), (x0 + m, y1 - m, top + rise)]
    for i in range(4):
        j = (i + 1) % 4; roof_face(roofk, [O[i], O[j], R[j], R[i]]); roof_face(roofk, [I[j], I[i], R[i], R[j]])
        rk = "tile:" + shade(roofk[5:], .78); (ax, ay, _), (bx, by, _) = R[i], R[j]
        boxr(rk, rk, (ax + bx) / 2, (ay + by) / 2, abs(bx - ax) + .3, abs(by - ay) + .3, top + rise - .1, top + rise + .12)
    fenestrate(pts, z0, storeys, g, lit)
    cw, cd = cx1 - cx0, cy1 - cy0
    if g.random() < .5 and cw > 3.5:                                                  # a portico along one side of the court
        for k in range(int(cw / 1.8) + 1): cyl("marble:#efe8d8", cx0 + .4 + k * (cw - .8) / max(1, int(cw / 1.8)), cy1 - .6, .16, z0, top - .1, n=8)
    k = g.random(); ccx, ccy = (cx0 + cx1) / 2, (cy0 + cy1) / 2
    if k < .4: place(g.choice(("island_tree_02", "tree_small_02")), ccx + g.uniform(-.5, .5), ccy + g.uniform(-.5, .5), z0, h=g.uniform(3.2, 4.6), g=g)
    elif k < .6: inst(WELL, ccx, ccy, z0, g.uniform(0, 3))
    elif k < .8:
        for _ in range(g.randint(2, 4)): inst(g.choice((PITHOS, AMPH)), ccx + g.uniform(-cw / 3, cw / 3), ccy + g.uniform(-cd / 3, cd / 3), z0, g.uniform(0, 6.3))
    else:                                                                             # a vine pergola over the court
        for xx in (cx0 + .3, cx1 - .3):
            for yy in (cy0 + .3, cy1 - .3): beam("wood:#6b5032", (xx, yy, z0), (xx, yy, z0 + 2.4), r=.07)
        for t in range(5): beam("wood:#7a5c3a", (cx0 + .3, cy0 + .3 + t * (cd - .6) / 4, z0 + 2.45), (cx1 - .3, cy0 + .3 + t * (cd - .6) / 4, z0 + 2.45), r=.05)
        for _ in range(5): inst(VINE, ccx + g.uniform(-cw / 3, cw / 3), ccy + g.uniform(-cd / 3, cd / 3), z0 + 1.6, g.uniform(0, 6.3), (1.2, 1.2, .5))
    take_poly(pts, .5)
def simple_house(x0, y0, x1, y1, g, lit=False, storeys=None, roofc=None, wallc=None):
    """A house of one or two storeys under a hipped or gabled roof; now and then a flat roof terrace instead, or a balcony."""
    pts = box_pts(x0, y0, x1, y1); z0 = footing(pts); storeys = storeys or g.choice((1, 1, 2, 2, 2)); h = 3.1 * storeys + .3; top = z0 + h
    wallc = wallc or g.choice(WALLCOLS); wk = wall_kind(wallc); roofk = "tile:" + (roofc or g.choice(TILECOLS))
    walls(wk, pts, z0, top); walls("stone:#c9b996", box_pts(x0 - .06, y0 - .06, x1 + .06, y1 + .06), z0 - .3, z0 + .6)
    k = g.random(); rise = .38 * min(x1 - x0, y1 - y0) / 2 + .3
    if k < .07 and storeys == 2:                                                      # a flat roof with a parapet: a terrace with jars and a pergola
        cap("pave:#cdb48e", pts, top); walls(wk, pts, top, top + .7); walls(wk, box_pts(x0 + .25, y0 + .25, x1 - .25, y1 - .25), top, top + .7, inward=True)
        for (a, b), (c, d) in zip(zip(pts, pts[1:] + pts[:1]), zip(box_pts(x0 + .25, y0 + .25, x1 - .25, y1 - .25), box_pts(x0 + .25, y0 + .25, x1 - .25, y1 - .25)[1:] + box_pts(x0 + .25, y0 + .25, x1 - .25, y1 - .25)[:1])):
            face(wk, [(a[0], a[1], top + .7), (b[0], b[1], top + .7), (d[0], d[1], top + .7), (c[0], c[1], top + .7)][::-1])
        for _ in range(g.randint(1, 3)): inst(AMPH, g.uniform(x0 + 1, x1 - 1), g.uniform(y0 + 1, y1 - 1), top, g.uniform(0, 6))
    elif k < .6: hip_roof(x0 - .45, y0 - .45, x1 + .45, y1 + .45, top - .12, rise, roofk)
    else: gable_roof(x0, y0, x1, y1, top, rise, roofk, wk)
    fenestrate(pts, z0, storeys, g, lit)
    if storeys == 2 and g.random() < .25:                                             # a wooden balcony on the upper floor
        side = g.randrange(4); p, q = pts[side], pts[(side + 1) % 4]; dx, dy = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dy); nx, ny = dy / ln, -dx / ln
        a = (p[0] + dx * .25, p[1] + dy * .25); b = (p[0] + dx * .75, p[1] + dy * .75); zb = z0 + 3.3
        face("wood:#7a5634", [(a[0], a[1], zb), (b[0], b[1], zb), (b[0] + nx * 1.0, b[1] + ny * 1.0, zb), (a[0] + nx * 1.0, a[1] + ny * 1.0, zb)][::-1 if area(pts) < 0 else 1])
        for t in range(9): x_, y_ = a[0] + (b[0] - a[0]) * t / 8 + nx, a[1] + (b[1] - a[1]) * t / 8 + ny; beam("wood:#5f4429", (x_, y_, zb), (x_, y_, zb + .9), r=.03, n=4)
        beam("wood:#5f4429", (a[0] + nx, a[1] + ny, zb + .9), (b[0] + nx, b[1] + ny, zb + .9), r=.04, n=4)
    take_poly(pts, .5)
def yard_walls(pts, h=1.6, gap_side=0, key="plaster:#e6dac2"):
    pts = pts if area(pts) > 0 else pts[::-1]
    for k, (p, q) in enumerate(zip(pts, pts[1:] + pts[:1])):
        dx, dy = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dy); nx, ny = -dy / ln * .25, dx / ln * .25
        segs = [(0, .4), (.6, 1)] if k == gap_side else [(0, 1)]
        for t0, t1 in segs:
            a = (p[0] + dx * t0, p[1] + dy * t0); b = (p[0] + dx * t1, p[1] + dy * t1); seg = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
            prism(key, "stone:#d6c9ad", seg, zmin(seg) - .2, zmax(seg) + h)
def hall(cx, cy, w, d, z, col_h, roofc, ridge="x", cols="all", core=None, steps=True, roof_h=2.6, wallc="#efe6d3", sculpt=False, g=RND):
    """A colonnaded building in dressed marble: stepped base, a walled core, fluted columns, a frieze of triglyphs, a tiled gable
    roof with antefixes along the eaves and a pediment at each end."""
    stonek = "marble:#ece5d6"; pts = rect(cx, cy, w + 2.6, d + 2.6)
    if z == 0: z = zmax(rect(cx, cy, w, d))
    zb = min(zmin(pts), z)
    if steps:
        prism(stonek, stonek, rect(cx, cy, w + 2.4, d + 2.4), zb - .3, z + .5)
        for i, gg in enumerate((1.6, .8)): prism(stonek, stonek, rect(cx, cy, w + gg, d + gg), z + .5 * (i + 1), z + .5 * (i + 2))
        z += 1.5
    elif zb < z - .05: prism("stone:#c9b996", None, rect(cx, cy, w, d), zb - .3, z)
    wallk = ("marble:" if cols else wall_kind(wallc)[:-7]) + wallc
    if core:
        ox, oy, cw, cd = core; cr = rect(cx + ox, cy + oy, cw, cd); walls(wallk, cr, z, z + col_h)
        if not cols: fenestrate(cr, z, max(1, int(col_h / 3.1)), g, door_side=None)
        else: opening("wood:#4a3524", cr[1], cr[2], .5, 1.8, z, z + min(col_h - .6, 4.2))
    def run(x0, y0, x1, y1):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2.4) + 1)
        return [(x0 + (x1 - x0) * k / (n - 1), y0 + (y1 - y0) * k / (n - 1)) for k in range(n)]
    hw, hd = w / 2 - .7, d / 2 - .7
    if cols == "all": spots = run(-hw, -hd, hw, -hd) + run(-hw, hd, hw, hd) + run(-hw, -hd, -hw, hd)[1:-1] + run(hw, -hd, hw, hd)[1:-1]
    else:
        side = {"n": run(-hw, hd, hw, hd), "s": run(-hw, -hd, hw, -hd), "e": run(hw, -hd, hw, hd), "w": run(-hw, -hd, -hw, hd)}
        spots = [q for k in (cols or "") for q in side[k]]
    ck = "marble:#f7f2e6"
    for a, b in spots:
        boxr(ck, ck, cx + a, cy + b, 1.0, 1.0, z, z + .22); cyl(ck, cx + a, cy + b, .42, z + .22, z + col_h - .3, n=16, r1=.35, top=False)
        cyl(ck, cx + a, cy + b, .35, z + col_h - .3, z + col_h - .18, n=16, r1=.52); boxr(ck, ck, cx + a, cy + b, 1.08, 1.08, z + col_h - .18, z + col_h)
    if cols: cap("pave:#e9e1cf", rect(cx, cy, w - .1, d - .1), z + .02)
    zt_ = z + col_h; band = "marble:#efe6d2" if cols else wallk
    prism(band, None, rect(cx, cy, w, d), zt_, zt_ + 1.3)
    if cols:
        R_ = rect(cx, cy, w, d)
        for p, q in zip(R_, R_[1:] + R_[:1]):
            n = int(math.hypot(q[0] - p[0], q[1] - p[1]) / 1.2)
            for k in range(n):
                opening("marble:#b9ae98", p, q, (k + .5) / n, .38, zt_ + .6, zt_ + 1.2, out=.03)
                if sculpt: opening("marble:#d8cfbd", p, q, (k + 1) / n, .7, zt_ + .65, zt_ + 1.15, out=.02)
    zt_ += 1.3; zr, ov = zt_ + roof_h, .55; x0, x1, y0, y1 = cx - w / 2 - ov, cx + w / 2 + ov, cy - d / 2 - ov, cy + d / 2 + ov
    roof = "tile:" + roofc; rk = "tile:" + shade(roofc, .78); ped = "marble:#f1eadb" if cols else wallk
    if ridge == "x":
        roof_face(roof, [(x0, y1, zt_), (x1, y1, zt_), (x1, cy, zr), (x0, cy, zr)]); roof_face(roof, [(x1, y0, zt_), (x0, y0, zt_), (x0, cy, zr), (x1, cy, zr)])
        boxr(rk, rk, cx, cy, x1 - x0, .36, zr - .12, zr + .14)
        for xe in (cx - w / 2, cx + w / 2):
            face(ped, [(xe, cy - d / 2, zt_), (xe, cy + d / 2, zt_), (xe, cy, zr - .1)][::(1 if xe > cx else -1)])
            if cols:                                                                   # the tympanum's sculpture: a shadowed band of relief
                face("marble:#cfc5b1", [(xe + (.05 if xe > cx else -.05), cy - d / 4, zt_ + .25), (xe + (.05 if xe > cx else -.05), cy + d / 4, zt_ + .25), (xe + (.05 if xe > cx else -.05), cy, zr - .7)][::(1 if xe > cx else -1)])
                for yy in (cy - d / 2, cy + d / 2, cy): boxr(ck, ck, xe, yy, .5, .5, (zr if yy == cy else zt_) - .05, (zr if yy == cy else zt_) + .7)
        for k in range(int((x1 - x0) / .9)):
            for yy in (y0, y1): boxr(rk, rk, x0 + .45 + k * .9, yy, .22, .12, zt_ - .05, zt_ + .25)
    else:
        roof_face(roof, [(x0, y0, zt_), (x0, y1, zt_), (cx, y1, zr), (cx, y0, zr)]); roof_face(roof, [(x1, y1, zt_), (x1, y0, zt_), (cx, y0, zr), (cx, y1, zr)])
        boxr(rk, rk, cx, cy, .36, y1 - y0, zr - .12, zr + .14)
        for ye in (cy - d / 2, cy + d / 2):
            face(ped, [(cx + w / 2, ye, zt_), (cx - w / 2, ye, zt_), (cx, ye, zr - .1)][::(1 if ye < cy else -1)])
            if cols:
                for xx in (cx - w / 2, cx + w / 2, cx): boxr(ck, ck, xx, ye, .5, .5, (zr if xx == cx else zt_) - .05, (zr if xx == cx else zt_) + .7)
        for k in range(int((y1 - y0) / .9)):
            for xx in (x0, x1): boxr(rk, rk, xx, y0 + .45 + k * .9, .12, .22, zt_ - .05, zt_ + .25)
    take_poly(rect(cx, cy, w + 3, d + 3), .5)
    return z
STONES = ["#d3c6a8", "#cdbf9f", "#d8ccb0", "#c6b896", "#d1c2a0"]
MG = random.Random(61)
def masonry(pts, h, wallc="#d3c6a8", merl=None, top_follow=True, abs_top=None):
    """A stretch of wall or a tower in old stone, standing on the ground wherever that is: each stretch a slightly different
    stone and height, merlons along its top with now and then one fallen, rubble and weeds at its foot."""
    g = MG; wallc = g.choice(STONES) if wallc == "#d3c6a8" else wallc
    zb = zmin(pts) - .5; zt_ = (abs_top if abs_top is not None else (zt(*centre(pts)) if top_follow else 0) + h) + g.uniform(-.3, .25)
    prism("stone:" + wallc, "pave:" + shade(wallc, 1.04), pts, zb, zt_)
    walls("stone:" + shade(wallc, .9), [(x + (x - centre(pts)[0]) * .025, y + (y - centre(pts)[1]) * .025) for x, y in pts], zb, zb + .9 + g.uniform(0, .5))   # a weathered plinth course
    for x, y, ang in merl or []:
        if g.random() < .07: continue
        boxr("stone:" + wallc, "pave:" + shade(wallc, 1.04), x, y, 1.2, .9, zt_, zt_ + g.uniform(.75, 1.0), ang)
    cx, cy = centre(pts)
    for _ in range(g.randint(0, 2)):                                                    # tumbled stones and a bush at the foot
        a = g.uniform(0, 6.3); x, y = cx + math.cos(a) * g.uniform(2.5, 4.5), cy + math.sin(a) * g.uniform(2.5, 4.5)
        if free(x, y): place(g.choice(("boulder_01", "searsia_lucida", "wild_rooibos_bush")), x, y, zt(x, y) - .2, h=g.uniform(.5, 1.3), g=g)
    take_poly(pts, 1)
def wall_line(poly, h=7.5, thick=3.2, towers=3, closed=False, wallc="#d3c6a8", tower_h=10.5, skip_first=False, abs_top=None):
    """A curtain wall along a line, cut into stretches of about 10 m (each standing on its own ground), with a tower every few
    stretches and merlons along the outer edge; openings in HOLES are left out."""
    P = poly + ([poly[0]] if closed else []); k = 0
    for (x1, y1), (x2, y2) in zip(P, P[1:]):
        ln = math.hypot(x2 - x1, y2 - y1); n = max(1, round(ln / 10)); ux, uy = (x2 - x1) / ln, (y2 - y1) / ln; nx, ny = -uy * thick / 2, ux * thick / 2
        for i in range(n):
            a, b = (x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n), (x1 + (x2 - x1) * (i + 1) / n, y1 + (y2 - y1) * (i + 1) / n)
            seg = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
            ang = math.degrees(math.atan2(uy, ux)); L_ = ln / n; m = max(1, int(L_ / 2.2))
            for part in cut_wall(seg):
                pc = centre(part)
                merl = [(a[0] + (b[0] - a[0]) * (j + .5) / m + nx * .55 * sd, a[1] + (b[1] - a[1]) * (j + .5) / m + ny * .55 * sd, ang) for j in range(m) for sd in (-1, 1)]
                merl = [q for q in merl if inpoly(q[0], q[1], [(x + (x - pc[0]) * .05, y + (y - pc[1]) * .05) for x, y in part])]
                masonry(part, h, wallc, merl, abs_top=abs_top)
            k += 1
            if towers and k % towers == 0 and not (skip_first and k == 1) and all(math.hypot(b[0] - hx, b[1] - hy) > half + 4 for hx, hy, half in HOLES):
                masonry(rect(b[0], b[1], 7.5, 7.5, ang), tower_h, wallc, [(b[0] + dx, b[1] + dy, ang) for dx in (-3, 0, 3) for dy in (-3, 0, 3) if dx or dy], abs_top=None if abs_top is None else abs_top + 3.5)

# ================================================================ the walls of the city (or the enemy town), from the drawing's courses
# The drawing's courses run straight through its gates (only towers and a lintel mark them); here each opening is cut out.
HOLES = [] if SIEGE else [(gx, gy, 4.6) for gx, gy in S["gates"]] + ([(*S["postern"], 3.0)] if S.get("postern") else []) + [(0, 101.5, 8.2), (-46, 114.5, 2.6)]
def cut_wall(pts):
    """A stretch of wall as rectangles, with any opening that lies on it left out."""
    p = ((pts[0][0] + pts[3][0]) / 2, (pts[0][1] + pts[3][1]) / 2); q = ((pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2)
    ln = math.hypot(q[0] - p[0], q[1] - p[1])
    if ln < 1e-6: return [pts]
    ux, uy = (q[0] - p[0]) / ln, (q[1] - p[1]) / ln; hw = math.hypot(pts[0][0] - pts[3][0], pts[0][1] - pts[3][1]) / 2; nx, ny = -uy * hw, ux * hw
    keep = [(0, ln)]
    for hx, hy, half in HOLES:
        t = (hx - p[0]) * ux + (hy - p[1]) * uy; d = abs((hx - p[0]) * uy - (hy - p[1]) * ux)
        if d > 3 or t < -half or t > ln + half: continue
        keep = [seg for a, b in keep for seg in ((a, min(b, t - half)), (max(a, t + half), b)) if seg[1] - seg[0] > .2]
    if keep == [(0, ln)]: return [pts]
    return [[(p[0] + ux * a + nx, p[1] + uy * a + ny), (p[0] + ux * b + nx, p[1] + uy * b + ny), (p[0] + ux * b - nx, p[1] + uy * b - ny), (p[0] + ux * a - nx, p[1] + uy * a - ny)] for a, b in keep]
skip_houses = []
for s in S["solids"]:
    if s.get("merl") and s.get("kind") != "hall":
        cx, cy = centre(s["pts"])
        if not SIEGE and cy > 53: continue                                               # the drawing's hill walls: replaced by the new citadel's, below
        if abs(s["z"] - 6.2) < .01: continue                                             # the drawing's lintel: the gatehouses below replace it
        parts = cut_wall(s["pts"])
        for part in parts: masonry(part, s["h"], "#d3c6a8", s["merl"] if len(parts) == 1 else [m for m in s["merl"] if inpoly(m[0], m[1], [(x + (x - centre(part)[0]) * .3, y + (y - centre(part)[1]) * .3) for x, y in part])])
    elif not s.get("kind") and s["roof"] == "#d9cdb2" and s["wall"] in ("#cbbd9e", "#c4b594") and abs(area(s["pts"])) > 30:
        masonry(s["pts"], s["h"], "#d3c6a8", None)                                         # plain stretches and towers away from the detail pass

def arch_gate(cx, cy, ux, uy, span, ow, spring, height, thick, shut=False, inside=1, wallc="#d3c6a8", base=None):
    """A gate: a block of masonry across the wall with a round-arched passage through it. ux, uy is the wall's direction;
    the passage runs across it. Open gates have their two leaves swung back against the passage; shut ones fill the arch."""
    vx, vy = -uy, ux; zb = (zmin([(cx + ux * a + vx * b, cy + uy * a + vy * b) for a in (-span / 2, span / 2) for b in (-thick / 2, thick / 2)]) - .6) if base is None else base
    zg = zt(cx, cy) if base is None else base; zs = zg + spring; r = ow / 2; ztop = zg + height
    P = lambda a, b, z: (cx + ux * a + vx * b, cy + uy * a + vy * b, z)
    sk, ck, vk = "stone:" + wallc, "pave:" + shade(wallc, 1.04), "stone:" + shade(wallc, .86)
    arch = [(-r + 2 * r * k / 14, zs + math.sqrt(max(0, r * r - (-r + 2 * r * k / 14) ** 2))) for k in range(15)]
    for side in (-1, 1):
        b = side * thick / 2; want = (vx * side, vy * side, 0)
        oriented(sk, [P(-span / 2, b, zb), P(-r, b, zb), P(-r, b, ztop), P(-span / 2, b, ztop)], want)
        oriented(sk, [P(r, b, zb), P(span / 2, b, zb), P(span / 2, b, ztop), P(r, b, ztop)], want)
        for (a0, z0), (a1, z1) in zip(arch, arch[1:]):
            oriented(sk, [P(a0, b, z0), P(a1, b, z1), P(a1, b, ztop), P(a0, b, ztop)], want)
            b2 = b + side * .06; k0, k1 = .55, .55                                    # the voussoirs: a ring of darker stones round the arch
            oriented(vk, [P(a0, b2, z0), P(a1, b2, z1), P(a1 * (1 + k1 / r), b2, zs + (z1 - zs) * (1 + k1 / r)), P(a0 * (1 + k0 / r), b2, zs + (z0 - zs) * (1 + k0 / r))], want)
        oriented(vk, [P(-r - .55, b + side * .06, zb), P(-r, b + side * .06, zb), P(-r, b + side * .06, zs), P(-r - .55, b + side * .06, zs)], want)
        oriented(vk, [P(r, b + side * .06, zb), P(r + .55, b + side * .06, zb), P(r + .55, b + side * .06, zs), P(r, b + side * .06, zs)], want)
    for a in (-r, r):                                                                  # the passage: its jambs and the vault
        oriented(sk, [P(a, -thick / 2, zb), P(a, thick / 2, zb), P(a, thick / 2, zs), P(a, -thick / 2, zs)], (-ux * a, -uy * a, 0))
    for (a0, z0), (a1, z1) in zip(arch, arch[1:]): oriented(sk, [P(a0, -thick / 2, z0), P(a1, -thick / 2, z1), P(a1, thick / 2, z1), P(a0, thick / 2, z0)], (0, 0, -1))
    oriented(ck, [P(-span / 2, -thick / 2, ztop), P(span / 2, -thick / 2, ztop), P(span / 2, thick / 2, ztop), P(-span / 2, thick / 2, ztop)], (0, 0, 1))
    n = int(span / 2.2)
    for side in (-1, 1):
        for k in range(n):
            a = -span / 2 + (k + .5) * span / n; x, y, _ = P(a, side * (thick / 2 - .45), 0)
            boxr(sk, ck, x, y, 1.2 if abs(ux) > .5 else .9, .9 if abs(ux) > .5 else 1.2, ztop, ztop + .95)
    dk = "wood:#5a3c24"
    if shut:                                                                           # the leaves closed, studded planks filling the arch, on both faces
        for side in (-1, 1):
            b = side * .2
            oriented(dk, [P(-r, b, zg), P(r, b, zg), P(r, b, zs), P(-r, b, zs)], (vx * side, vy * side, 0))
            for (a0, z0), (a1, z1) in zip(arch, arch[1:]): oriented(dk, [P(a0, b, zs), P(a1, b, zs), P(a1, b, z1), P(a0, b, z0)], (vx * side, vy * side, 0))
            oriented("flat:#2a1d12", [P(-.05, b + side * .02, zg), P(.05, b + side * .02, zg), P(.05, b + side * .02, zs + r), P(-.05, b + side * .02, zs + r)], (vx * side, vy * side, 0))
    else:                                                                              # open: each leaf against its jamb, on the town side
        for a in (-r + .1, r - .1):
            b0, b1 = inside * .2, inside * min(thick / 2, r - .1) + inside * .2
            oriented(dk, [P(a, b0, zg), P(a, b1, zg), P(a, b1, zs + .3), P(a, b0, zs + .3)], (-ux * a, -uy * a, 0))
    take_poly([P(-span / 2, -thick / 2, 0)[:2], P(span / 2, -thick / 2, 0)[:2], P(span / 2, thick / 2, 0)[:2], P(-span / 2, thick / 2, 0)[:2]], 0)
for gx, gy in S["gates"]:                                                              # the town's gates, between the drawing's gate towers
    ux, uy = (0, 1) if gy == 0 else (1, 0); ins = -1 if (gx > 0 or gy > 0) else 1
    if not SIEGE: arch_gate(gx, gy, ux, uy, 9.2, 5.6, 4.6, 9.0, 3.4, inside=ins if gy == 0 else (1 if gy < 0 else -1))
    else:                                                                              # shut: the wall runs on across; the closed gate is set in its outer face
        nx_, ny_ = (1 if gx > 0 else -1 if gx < 0 else 0), (1 if gy > 0 else -1 if gy < 0 else 0)
        arch_gate(gx + nx_ * 1.75, gy + ny_ * 1.75, ux, uy, 9.2, 5.0, 4.0, 8.4, .3, shut=True)
if not SIEGE:
    # The town's walls climb the hill's flanks from the octagon's north corners to the citadel; the west one carries the postern.
    PX, PY = S["postern"]
    WEST = [(-78, 50), (-86, 80), (PX, PY), (-70, 134), (-50, 150)]; EAST = [(78, 50), (98, 88), (96, 126), (50, 150)]
    wall_line(WEST, towers=2, skip_first=True); wall_line(EAST, towers=2, skip_first=True)
    a, b = WEST[1], WEST[3]; ln = math.hypot(b[0] - a[0], b[1] - a[1])
    arch_gate(PX, PY, (b[0] - a[0]) / ln, (b[1] - a[1]) / ln, 6.2, 3.2, 3.0, 8.0, 3.4, base=2.7)
    # the citadel: its own higher walls along the summit's edge, towers at the corners
    ring = []
    for (x1, y1), (x2, y2) in zip(PRE3, PRE3[1:] + PRE3[:1]):                          # set 1.2 m outside the summit's edge
        ln = math.hypot(x2 - x1, y2 - y1); nx, ny = (y2 - y1) / ln * 1.2, -(x2 - x1) / ln * 1.2; ring += [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny)]
    wall_line(ring[::2], h=4.5, thick=2.8, towers=3, closed=True, wallc="#ddd0b2", abs_top=TOP + 4.5)

def tree_at(x, y, kind, g, h=None):
    if not free(x, y): return
    z = zt(x, y)
    if kind == "cypress": inst(g.choice(CYPRESS), x, y, z - .1, g.uniform(0, 6.3), (g.uniform(.9, 1.1),) * 2 + (g.uniform(.85, 1.08),))
    elif kind == "pine": inst(g.choice(PINE), x, y, z - .1, g.uniform(0, 6.3), (g.uniform(.85, 1.1),) * 2 + (g.uniform(.85, 1.1),))
    else: place(g.choice(("tree_small_02", "island_tree_02", "island_tree_02")), x, y, z - .05, h=h or g.uniform(5, 6.5), g=g)
    take_poly(rect(x, y, 2.5, 2.5), 0)
# ================================================================ the acropolis: precinct, temple, library, gatehouse, stairs
TEMPLE_Z = TOP
if not SIEGE:
    # The summit: bedrock and dry grass, crossed by paved ways; the propylon over the head of the stair; the temple on the stair's
    # axis facing it across a forecourt with the altar; the library's stoa west of the forecourt, by the route to the west gate;
    # an Ionic shrine to the east, treasuries along the west edge, a long stoa closing the north end, statues, olives, a cistern.
    with Part("stele") as P_: boxr("marble:#e9e3d4", "marble:#efe9dc", 0, 0, .55, .16, 0, 1.25); STELE = P_
    STELE = P_.mesh
    with Part("base") as P_: boxr("marble:#ddd5c3", "marble:#e6dfcf", 0, 0, 1.4, 1.4, 0, .9); SBASE = P_
    SBASE = P_.mesh
    hall(0, 108, 16, 9, TOP, 6.5, "#c8673e", ridge="y", cols="ns", core=None, steps=False, roof_h=2.4)          # the propylon
    for x in (-11.5, 11.5): inst(STATUE, x, 101, TOP, 0, 1.15)
    hall(0, 158, 20, 40, TOP, 8.5, "#c8673e", ridge="y", cols="all", core=(0, 1, 12, 30), sculpt=True)           # the temple, facing south down the stair
    inst(ALTAR, 10, 126, TOP, math.pi / 2)
    with Part("colossus") as P_:                                                       # the goddess in bronze, on a tall base in the forecourt
        boxr("marble:#e3dccb", "marble:#ebe5d6", 0, 0, 3, 3, 0, 2.6); boxr("marble:#ebe5d6", "marble:#f0ebdf", 0, 0, 2.4, 2.4, 2.6, 3.0)
        for z0, z1, r0, r1 in ((3.0, 6.2, .75, .55), (6.2, 7.6, .55, .45), (7.6, 7.85, .22, .22)): cyl("flat:#6d5a3a", 0, 0, r0, z0, z1, n=12, r1=r1)
        cyl("flat:#6d5a3a", 0, 0, .32, 7.85, 8.5, n=12, r1=.2); beam("flat:#6d5a3a", (.5, 0, 7.2), (.6, 0, 11), r=.07)
    inst(P_.mesh, -14, 128, TOP)
    hall(-29, 124, 28, 13, TOP, 5.5, "#c8673e", ridge="x", cols="s", core=(0, 2.4, 28, 8), steps=False)          # the temple library: a stoa on the forecourt
    for k in range(4): inst(BENCH, -40 + k * 7, 115.6, TOP, 0)
    hall(30, 130, 13, 11, TOP, 6, "#c8673e", ridge="x", cols="sw", core=(1.5, 1.5, 10, 8), sculpt=False)         # an Ionic shrine
    for y in (158, 176): hall(-36, y, 9, 13, TOP, 4.6, "#c8673e", ridge="y", cols="s", core=(0, 1.6, 9, 9.8), steps=False)   # treasuries
    hall(0, 205, 46, 9, TOP, 5, "#c8673e", ridge="x", cols="s", core=(0, 2.2, 46, 4.6), steps=False)             # the north stoa
    g = random.Random(41)
    for x, y in ((14, 140), (-14, 140), (24, 118), (-6, 120), (34, 150), (-24, 190), (24, 190), (36, 116)): inst(STATUE, x, y, TOP, g.uniform(0, 6.3))
    for x, y in ((32, 170), (36, 180), (28, 186), (-22, 170)): place("tree_small_02", x, y, TOP, h=g.uniform(5, 6.5), g=g)   # the sacred olives
    for x, y in ((-30, 196), (30, 200)): inst(WELL, x, y, TOP, g.uniform(0, 3))
    for x, y in ((18, 182), (21, 183), (-8, 186), (-26, 140)): inst(PITHOS, x, y, TOP, g.uniform(0, 6))
    for _ in range(40):                                                                  # bedrock breaking the summit's surface, a few bushes
        x, y = g.uniform(-44, 44), g.uniform(110, 212)
        if inpoly(x, y, PRE3) and free(x, y, 2) and not (abs(x) < 4 and y < 136) and not (abs(y - 114) < 4 and x < 2):
            place(g.choice(("boulder_01", "boulder_01", "searsia_lucida", "wild_rooibos_bush")), x, y, TOP - .3, h=g.uniform(.4, 1.2), g=g)
    arch_gate(-47.2, 114.5, 0, 1, 5.2, 3.0, 2.6, 5.4, 2.8, base=TOP, wallc="#ddd0b2", inside=1)       # the citadel's small west gate
    g = random.Random(44)                                                                # votives along the ways, worn stones and dry grass everywhere between
    for k in range(18): put(STELE, g.choice((-1, 1)) * 4.2 + g.uniform(-.2, .2), 113 + k * 1.2, 0, g.uniform(-.2, .2), r=.3)
    for k in range(14): put(g.choice((STELE, STELE, SBASE)), -34 + g.uniform(-1, 1), 140 + k * 4, 0, g.uniform(0, 3), r=.4)
    for _ in range(2600):
        x, y = g.uniform(-50, 50), g.uniform(100, 216)
        if not inpoly(x, y, PRE3) or not free(x, y) or road_d[int(y + HALF), int(x + HALF)] < 1.2: continue
        k = g.random()
        if k < .55: place("grass_medium_01", x, y, TOP, h=g.uniform(.3, .7), g=g)
        elif k < .75: place("wild_rooibos_bush", x, y, TOP, h=g.uniform(.4, 1.0), g=g)
        elif k < .9: place("boulder_01", x, y, TOP - .25, h=g.uniform(.25, .7), g=g)
        elif k < .99: place("searsia_lucida", x, y, TOP, h=g.uniform(.8, 1.6), g=g)
        else: scatter_jars(x, y, TOP, 2, .6, g)
    for x, y in ((40, 160), (42, 176), (-42, 186), (-40, 150), (12, 204), (-14, 204)): tree_at(x, y, "cypress", g)
    take_poly(PRE3, 0)                                                                   # the summit is furnished; nothing more is scattered on it
    # the broad stair: a step every 0.17 m on the walkers' line, a stone flight with parapets on a built base down to the ground
    sy0, sy1, hw = 40.0, 104.0, 3.5; n = int(TOP / .17)
    for i in range(n):
        y0, y1 = sy0 + (sy1 - sy0) * i / n, sy0 + (sy1 - sy0) * (i + 1) / n; zt_ = TOP * (i + 1) / n
        prism("stone:#ddd2ba", "marble:#ece6d8", box_pts(-hw, y0, hw, y1), min(zt(-hw, y0), zt(hw, y0), zt_ - .4) - .4, zt_)
    for sx in (-1, 1):                                                                     # parapets, stepping up with the stair, and statues on their piers
        for k in range(16):
            y0, y1 = sy0 + (sy1 - sy0) * k / 16, sy0 + (sy1 - sy0) * (k + 1) / 16; za, zb_ = TOP * (y0 - sy0) / (sy1 - sy0), TOP * (y1 - sy0) / (sy1 - sy0)
            seg = box_pts(sx * hw - .45 if sx > 0 else -hw - .9 + .45, y0, sx * hw + .9 - .45 if sx > 0 else -hw + .45, y1)
            seg = box_pts(min(sx * hw, sx * (hw + .9)), y0, max(sx * hw, sx * (hw + .9)), y1)
            prism("stone:#d6caae", "pave:#e2d8c2", seg, min(zmin(seg), za) - .5, zb_ + 1.0)
            if k % 4 == 3: boxr("stone:#d6caae", "pave:#e2d8c2", sx * (hw + .45), y1, 1.4, 1.4, min(zt(sx * (hw + .45), y1), zb_) - .5, zb_ + 1.5)
    for y in (40, 104): take_poly(box_pts(-hw - 1, sy0, hw + 1, sy1), 0)
    # the west stair down to the postern, on the walkers' line, and the short flight outside the gate
    west = sorted({(a[0], a[2]) for seg in RAISED for a in seg if abs(a[1] - 114) < .6} | {(b[0], b[2]) for seg in RAISED for b in seg if abs(b[1] - 114) < .6})
    xs_, zs_ = [p[0] for p in west], [p[1] for p in west]
    x = max(xs_)
    while x > min(xs_) - 3:
        x2 = x - .4; zm = float(np.interp(x2 + .2, xs_, zs_))
        if zm < .02: break
        prism("stone:#d6caae", "marble:#e9e2d2", box_pts(x2, 112.4, x, 115.6), min(zt(x2, 112.4), zt(x2, 115.6), zm) - .6, zm + .08); x = x2
    take_poly(box_pts(min(xs_) - 3, 112, max(xs_), 116), 0)

LAMPS = []                                                                               # extra lights: (x, y, z, watts, kind)
# ================================================================ the town: each block divided into lots of different sizes, each lot built on
def split(r, g, mn=8.5, mx=15):
    x0, y0, x1, y1 = r; w, d = x1 - x0, y1 - y0
    if w <= mx and d <= mx and (g.random() < .5 or max(w, d) < 2 * mn): return [r]
    if w >= d and w >= 2 * mn: c = x0 + g.uniform(mn, w - mn); return split((x0, y0, c, y1), g, mn, mx) + split((c, y0, x1, y1), g, mn, mx)
    if d >= 2 * mn: c = y0 + g.uniform(mn, d - mn); return split((x0, y0, x1, c), g, mn, mx) + split((x0, c, x1, y1), g, mn, mx)
    return [r]
OCTA = S["octagon"]
def in_town(x, y, pad=0): return inpoly(x, y, [(px * (1 - pad / 78), py * (1 - pad / 78)) for px, py in OCTA])
PROPOSERS = [(-47.5, 28.5), (47.5, -28.5)] if not SIEGE else [(-28.5, 28.5)]            # in the besieged town, that lot holds its temple
MARKET = [(4, 4, 18, 18)] if SIEGE else [(4, 4, 18, 18), (-18, -18, -4, -4)]
def build_lot(r, g, lit_p):
    x0, y0, x1, y1 = r; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; w, d = x1 - x0, y1 - y0
    if not all(in_town(x, y, 3) for x, y in box_pts(x0, y0, x1, y1)):                    # the corners the wall cuts off: kitchen gardens and olives
        for _ in range(int(w * d / 30)):
            x, y = g.uniform(x0 + 1, x1 - 1), g.uniform(y0 + 1, y1 - 1)
            if in_town(x, y, 6) and free(x, y, 1): place("tree_small_02", x, y, zt(x, y), h=g.uniform(4, 5.5), g=g); take_poly(rect(x, y, 3, 3), 0)
        return
    if not SIEGE and abs(cx) < 21.5 and cy > 40:                                         # the open court the broad stair rises through
        for yy in range(48, 80, 7):
            for xx in (-9, 9):
                if free(xx, yy): inst(g.choice(CYPRESS), xx, yy, zt(xx, yy), g.uniform(0, 6), (1, 1, g.uniform(.85, 1.05)))
        return
    k = g.random(); inset = .25
    x0, y0, x1, y1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    if k < .08 and w * d > 90:                                                           # a workshop yard: a shed against the back wall, its trade's things in the yard
        yard_walls(box_pts(x0, y0, x1, y1), 1.8, gap_side=g.randrange(4)); simple_house(x0 + .4, y1 - 4.5, x1 - .4, y1 - .4, g, storeys=1)
        for _ in range(4):
            px_, py_ = g.uniform(x0 + 1.5, x1 - 1.5), g.uniform(y0 + 1.5, y1 - 5.5)
            if free(px_, py_): g.choice((lambda: scatter_jars(px_, py_, None, 6, 1.2, g), lambda: inst(WOODPILE, px_, py_, zt(px_, py_), g.uniform(0, 3)), lambda: inst(CRATE, px_, py_, zt(px_, py_), g.uniform(0, 3))))()
        take_poly(box_pts(x0, y0, x1, y1), 0)
    elif w >= 11 and d >= 11 and k < .7: court_house(x0, y0, x1, y1, g, lit=lit_p and g.random() < .5, storeys=g.choice((1, 1, 2)))
    else: simple_house(x0, y0, x1, y1, g, lit=lit_p and g.random() < .5)
def town(seed):
    g = random.Random(seed)
    for qx in (-1, 1):
        for qy in (-1, 1):
            for bs in (4, 40.5):
                for bt in (4, 40.5):
                    xa, xb = sorted((qx * bs, qx * (bs + 31.5))); ya, yb = sorted((qy * bt, qy * (bt + 31.5)))
                    lots = None
                    for px_, py_ in PROPOSERS:                                           # a proposer's house: a fine courtyard house exactly where its pin is
                        if xa <= px_ <= xb and ya <= py_ <= yb:
                            hx0, hy0, hx1, hy1 = px_ - 7, py_ - 7, px_ + 7, py_ + 7
                            if SIEGE:
                                hall(px_, py_, 10, 13, 0, 5.5, "#b9592f", ridge="y", cols="all", core=(0, .5, 6, 8.5))
                                for s_ in (-1, 1):
                                    bx_, by_ = px_ + s_ * 3.5, py_ - 8.2; cyl("flat:#2a2622", bx_, by_, .35, 0, 1.0, n=8, r1=.5); cyl("emit:#ffb347", bx_, by_, .45, 1.0, 1.3, n=8, r1=.1); LAMPS.append((bx_, by_, 1.8, 900, "fire"))
                            else: court_house(hx0 + .25, hy0 + .25, hx1 - .25, hy1 - .25, g, storeys=2, roofc="#b9592f")
                            rest = [(xa, ya, xb, hy0), (xa, hy1, xb, yb), (xa, hy0, hx0, hy1), (hx1, hy0, xb, hy1)]
                            lots = [l for r_ in rest if r_[2] - r_[0] > 3 and r_[3] - r_[1] > 3 for l in split(r_, g)]
                    for mx0, my0, mx1, my1 in MARKET:                                    # the market by the crossroads: stalls under awnings on a paved square
                        if xa <= mx0 + .1 and mx1 <= xb + .1 and ya <= my0 + .1 and my1 <= yb + .1:
                            cap("pave:#e1d5bd", box_pts(mx0, my0, mx1, my1), .04)
                            for i in range(3):
                                for j in range(2):
                                    x, y = mx0 + 2.5 + i * 4.5, my0 + 3 + j * 7; rot = 0 if j == 0 else math.pi
                                    inst(STALL, x, y, 0, rot); inst(g.choice(AWNINGS), x, y, 0, rot)
                                    for _ in range(3):
                                        gx_, gy_ = x + g.uniform(-1.1, 1.1), y + (-.6 if rot == 0 else .6)
                                        o = inst(g.choice((AMPH, SACK)), gx_, gy_, .95, g.uniform(0, 6), .7)
                            inst(WELL, mx0 + 7, my0 + 7, 0); take_poly(box_pts(mx0, my0, mx1, my1), 0)
                            rest = [(xa, ya, xb, yb)]
                            rest = [(xa, ya, mx0, yb) if mx0 > xa + 3 else None, (mx1, ya, xb, yb) if mx1 < xb - 3 else None]
                            rest = [r_ for r_ in rest if r_] + [(mx0, my1, mx1, yb) if my1 < yb - 3 else (mx0, ya, mx1, my0)]
                            lots = [l for r_ in rest if r_[2] - r_[0] > 3 and r_[3] - r_[1] > 3 for l in split(r_, g)]
                    for r_ in lots if lots is not None else split((xa, ya, xb, yb), g): build_lot(r_, g, NIGHT)
town(9)

# ================================================================ the estates, furnished for their trades
def drystone(poly, g, closed=True, h=(.6, 1.05), gaps=.06):
    """A dry-stone wall: short lengths of piled stone, each its own height and lean, wandering a little off the line; here
    and there a gap where it has fallen, its stones lying in the grass."""
    P = poly + ([poly[0]] if closed else [])
    for (x1, y1), (x2, y2) in zip(P, P[1:]):
        ln = math.hypot(x2 - x1, y2 - y1); n = max(1, int(ln / 1.3)); ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n; wob = 1.1 * N.noise(Vector(((x1 + ux * ln * t0) * .07, (y1 + uy * ln * t0) * .07, 5.5)))
            ax, ay = x1 + (x2 - x1) * t0 - uy * wob, y1 + (y2 - y1) * t0 + ux * wob; bx, by = x1 + (x2 - x1) * t1 - uy * wob, y1 + (y2 - y1) * t1 + ux * wob
            if road_d[int(ay + HALF), int(ax + HALF)] < 2.0 or road_d[int(by + HALF), int(bx + HALF)] < 2.0: continue   # a gateway where a road passes
            if g.random() < gaps:
                for _ in range(3): place("boulder_01", ax + g.uniform(-1, 1), ay + g.uniform(-1, 1), zt(ax, ay) - .15, h=g.uniform(.25, .45), g=g)
                continue
            w_ = g.uniform(.65, .95) / 2; hh = g.uniform(*h); seg = [(ax - uy * w_, ay + ux * w_), (bx - uy * w_, by + ux * w_), (bx + uy * w_, by - ux * w_), (ax + uy * w_, ay - ux * w_)]
            z0 = zmin(seg) - .2; col = g.choice(("#b9a987", "#ae9f80", "#c2b292", "#a89878"))
            top = [(x + (x - (ax + bx) / 2) * -.12, y + (y - (ay + by) / 2) * -.12) for x, y in seg]
            walls("stone:" + col, seg, z0, z0 + .2 + hh * .75); prism("stone:" + col, "stone:" + shade(col, 1.05), top, z0 + .2 + hh * .75, z0 + .2 + hh)
            if g.random() < .12: place(g.choice(("searsia_lucida", "wild_rooibos_bush", "grass_medium_01")), ax + g.uniform(-1, 1), ay + g.uniform(-1, 1), zt(ax, ay), h=g.uniform(.5, 1.4), g=g)
            take_poly(seg, .5)
def ragged(x, y, x0, y0, x1, y1, amp=3.0, seed=0):
    """How far inside a field's ragged edge a point is: the rectangle's edge, pushed in and out by noise."""
    return min(x - x0, x1 - x, y - y0, y1 - y) - amp * (.5 + .5 * N.noise(Vector((x * .06, y * .06, seed))))
def wheat_field(pts, fill, ax, step, cut=False):
    """Standing wheat in rows that wander a little, rounded with furrows between, its edges ragged where the plough turned and
    weeds took the margin; a cut field has short stubble and sheaves stood in loose rows."""
    (x0, y0), _, (x1, y1), _ = pts; R = .5; nx, ny = int((x1 - x0) / R) + 1, int((y1 - y0) / R) + 1
    V, Fc, H, IN = [], [], [], []; seed = x0 * .13 + y0 * .07
    for j in range(ny):
        for i in range(nx):
            x, y = min(x1, x0 + i * R), min(y1, y0 + j * R); along = y if ax == "x" else x
            t = (((x - x0) if ax == "x" else (y - y0)) + .9 * N.noise(Vector((along * .03, seed, 1.7)))) / step
            ph = t - math.floor(t); prof = min(1, max(0, math.cos((ph - .5) * math.pi * 1.2)) * 1.8) ** .8
            edge = ragged(x, y, x0, y0, x1, y1, 3.5, seed); fade = max(0, min(1, (edge - .2) / 1.4)); IN.append(edge > -.6)
            thin = .75 + .35 * N.noise(Vector((x * .12, y * .12, seed + 4)))
            h = ((.85 + .25 * N.noise(Vector((x * .4, y * .4, 3)))) * prof * fade * min(1, thin)) * (.18 if cut else 1)
            hz = .95 * h + (.22 * N.noise(Vector((x * .9, y * .9, 9))) * prof * fade) * (0 if cut else 1); H.append(hz)
            V.append((x, y, zt(x, y) + .03 + hz))
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            cx_, cy_ = V[a][0] + R / 2, V[a][1] + R / 2
            if (IN[a] or IN[a + 1] or IN[a + nx] or IN[a + nx + 1]) and road_d[int(cy_ + HALF), int(cx_ + HALF)] > 1.2 + 1.5 * (.5 + .5 * N.noise(Vector((cx_ * .2, cy_ * .2, 6.1)))) and free(cx_, cy_): Fc.append([a, a + 1, a + nx + 1, a + nx])
    me = bpy.data.meshes.new("wheat"); me.from_pydata(V, [], Fc)
    at = me.attributes.new("h", "FLOAT", "POINT"); at.data.foreach_set("value", [min(1, v) for v in H])
    for pl in me.polygons: pl.use_smooth = True
    me.materials.append(mat("wheat:" + (shade(fill, .92) if cut else fill))); ROOT.objects.link(bpy.data.objects.new("wheat", me))
    g = random.Random(int(x0 * 3 + y0))
    if cut:
        y = y0 + 4
        while y < y1 - 3:
            x = x0 + 4
            while x < x1 - 3:
                if ragged(x, y, x0, y0, x1, y1, 3.5, seed) > 1 and g.random() < .85: inst(SHEAF, x + g.uniform(-.8, .8), y + g.uniform(-.8, .8), zt(x, y), g.uniform(0, 6), g.uniform(.9, 1.2))
                x += g.uniform(4, 6)
            y += g.uniform(5, 7)
    for _ in range(int((x1 - x0 + y1 - y0) * 1.6)):                                   # poppies, thistles and tufts along the margins
        x, y = g.uniform(x0, x1), g.uniform(y0, y1); e = ragged(x, y, x0, y0, x1, y1, 3.5, seed)
        if -1.2 < e < .8 and road_d[int(y + HALF), int(x + HALF)] > .5: place(g.choice(("grass_medium_01", "wild_rooibos_bush", "grass_medium_01")), x, y, zt(x, y), h=g.uniform(.4, .9), g=g)
    take_poly(pts, 0)
def vineyard(pts, g):
    """Vines in rows that bend a little with the ground, on stakes, bare earth between, a dry-stone wall round the plot; now and
    then a vine missing or a stunted one."""
    (x0, y0), _, (x1, y1), _ = pts; seed = x0 * .11
    V, Fc = [], []
    for j in range(int((y1 - y0) / 1.0) + 1):
        for i in range(int((x1 - x0) / 1.0) + 1):
            x, y = min(x1, x0 + i), min(y1, y0 + j); V.append((x, y, zt(x, y) + .03))
    nxv = int((x1 - x0) / 1.0) + 1
    for j in range(int((y1 - y0) / 1.0)):
        for i in range(nxv - 1):
            a = j * nxv + i; cx_, cy_ = V[a][0] + .5, V[a][1] + .5
            if ragged(cx_, cy_, x0, y0, x1, y1, 2.0, seed) > -.4 and road_d[int(cy_ + HALF), int(cx_ + HALF)] > .8: Fc.append([a, a + 1, a + nxv + 1, a + nxv])
    me = bpy.data.meshes.new("vineyard"); me.from_pydata(V, [], Fc); me.materials.append(mat("dirt:#b9a77c")); ROOT.objects.link(bpy.data.objects.new("vineyard", me))
    drystone(box_pts(x0 - .8, y0 - .8, x1 + .8, y1 + .8), g)
    y = y0 + 2.5
    while y < y1 - 1:
        x = x0 + 2.2
        while x < x1 - 2:
            yy = y + .5 * N.noise(Vector((x * .05, y * .1, seed)))
            if g.random() > .05 and ragged(x, yy, x0, y0, x1, y1, 2.0, seed) > .6 and road_d[int(yy + HALF), int(x + HALF)] > 2.2:
                k = g.uniform(.6, 1.15); inst(VINE, x + g.uniform(-.2, .2), yy, zt(x, yy), g.uniform(0, 6.3), (k * g.uniform(.9, 1.1), k * g.uniform(.8, 1.1), k * g.uniform(.8, 1.15)))
            x += g.uniform(1.25, 1.6)
        y += 2.5
    take_poly(pts, 0)
def farmhouse(s, g):
    xs, ys = [p[0] for p in s["pts"]], [p[1] for p in s["pts"]]
    simple_house(min(xs), min(ys), max(xs), max(ys), g, storeys=1, wallc=g.choice(("#e8dcc2", "#e3d2b2")))
FLAT = S["flat"]
if not SIEGE:
    g = random.Random(77)
    # --- the granary, among its wheat: a raised store on stone piers, the threshing floor, ricks, carts of sacks, beehives
    hall(168, 0, 16, 14, 0, 6.5, "#b9592f", ridge="x", cols="", core=(0, 0, 16, 14), steps=False, roof_h=3.2, wallc="#e3d2b2", g=g)
    for k in range(6): boxr("stone:#c7b794", "stone:#c7b794", 160.5 + k * 3, 7.6, .7, 1.2, 0, 4.5)
    for k in range(6): boxr("stone:#c7b794", "stone:#c7b794", 160.5 + k * 3, -7.6, .7, 1.2, 0, 4.5)
    for s in S["solids"]:
        if s.get("hipr") and centre(s["pts"])[0] > 140: farmhouse(s, g)
    cyl("pave:#d9c69a", 175, -40, 7, 0, .25, n=32); cyl("stone:#bfae8a", 175, -40, 7.4, 0, .45, n=32, top=False); take_poly(rect(175, -40, 16, 16), 0)
    for k in range(14): put(SHEAF, 175 + 5 * math.cos(k * .45), -40 + 5 * math.sin(k * .45), .25, k, 1.1)
    for x, y in ((186, -22), (190, -12), (161, -27)): put(HAY, x, y, 0, g.uniform(0, 6), g.uniform(.85, 1.1)); take_poly(rect(x, y, 6, 6), 0)
    put(CART, 156, 8, 0, .4); put(CART, 181, 10, 0, 2.6)
    for k in range(12): put(SACK, 153 + (k % 4) * .65, -6 + (k // 4) * .65, 0, g.uniform(0, 6))
    for k in range(5): put(BEEHIVE, 190 + k * 1.1, 24, 0)
    put(WELL, 176, 14, 0); take_poly(rect(176, 14, 3, 3), 0)
    drystone(box_pts(150, -30, 195, 30), g)
    # --- the winery: the press house, a beam press under its shed, jars of new wine, terraced vineyards
    hall(-160, -8, 20, 11, 0, 4.5, "#b9592f", ridge="x", cols="", core=(0, 0, 20, 11), steps=False, roof_h=2.4, wallc="#e8dcc2", g=g)
    put(PRESS, -166, 9, 0); hall(-166, 9, 10, 6, 0, 2.8, "#b9592f", ridge="x", cols="ns", core=None, steps=False, roof_h=1.2)
    for s in S["solids"]:
        if s.get("hipr") and centre(s["pts"])[0] < -140: farmhouse(s, g)
    amph_rows(-152, -22, -142, -16, 0, g); scatter_jars(-147, 6, 0, 10, 2, g, (PITHOS,))
    put(CART, -146, -2, 0, 1.2); put(WOODPILE, -182, 6, 0, .3)
    drystone(box_pts(-188, -26, -140, 28), g)
    # --- the fishery on the shore: the shed, salting tanks of brine, racks of drying fish, nets, beached boats, a ship at the jetty
    hall(-16, -108, 18, 8, 0, 3.4, "#b9592f", ridge="x", cols="", core=(0, 0, 18, 8), steps=False, roof_h=1.8, wallc="#e3d2b2", g=g)
    for f in FLAT:
        if f.get("fill") == "#9fd0d6":
            pts = f["pts"]; cx, cy = centre(pts); inner = rect(cx, cy, 6.2, 4.2)
            walls("stone:#d6cbb0", pts, -.2, .6); walls("stone:#d6cbb0", inner, -.2, .6, inward=True)
            for (a, b), (c, d) in zip(zip(pts, pts[1:] + pts[:1]), zip(inner, inner[1:] + inner[:1])): face("stone:#e2d8bf", [(a[0], a[1], .6), (b[0], b[1], .6), (d[0], d[1], .6), (c[0], c[1], .6)][::-1])
            cap("water:#9fd8e0", inner, .45); take_poly(pts, 1)
        if f.get("fill") == "#a7865b" and abs(area(f["pts"])) > 50:                      # jetties: plank decks on posts
            pts = f["pts"]; prism("wood:#7a5a3a", "wood:#a7865b", pts, .1, .6)
            (ax, ay), (bx, by), (cx_, cy_), (dx, dy) = pts
            for t in (0, .25, .5, .75, 1):
                for (px, py), (qx, qy) in (((ax, ay), (dx, dy)), ((bx, by), (cx_, cy_))): cyl("wood:#5d4630", px + (qx - px) * t, py + (qy - py) * t, .18, -2, .9, n=6)
            mx_, my_ = (ax + bx) / 2, min(ay, dy) + 3
            inst(BOAT, mx_ + 2.6, my_ + 4, -.25, math.pi / 2 + g.uniform(-.1, .1)); inst(BOAT, mx_ - 2.6, my_ + 9, -.25, math.pi / 2 + g.uniform(-.1, .1))
            for _ in range(3): inst(g.choice((AMPH, CRATE)), mx_ + g.uniform(-.8, .8), my_ + g.uniform(0, 14), .6, g.uniform(0, 6))
    for k in range(5): put(RACK, -33 - k * 4.5, -106, 0, r=2.2)
    for x, y in ((-44, -128), (-58, -124), (4, -128)): put(NETS, x, y, 0, g.uniform(-.4, .4))
    for x, y, r_ in ((-30, -136, 2.3), (-52, -134, 2.0), (-70, -122, 2.6), (40, -132, .5)): inst(BOAT, x, y, zt(x, y) - .1, r_)
    inst(SHIP, -12, -172, -.9, .35)
    for k in range(10): put(g.choice((CRATE,)), -6 + (k % 5) * 1.0, -114 - (k // 5) * .8, 0, g.uniform(-.2, .2))
    scatter_jars(-26, -100, 0, 12, 2.2, g); put(CART, 8, -112, 0, .2)
    # --- the potter's yard: domed kilns with their fuel, the drying shed racked with amphorae, wheels, the clay pit, heaps of jars
    def clear_spot(x, y, r_):
        """The nearest spot to (x, y) where something r_ across stands clear of roads and of what is already built."""
        for d in [0] + [k * .8 for k in range(1, 30)]:
            for a in range(0, 360, 20):
                cx_, cy_ = x + d * math.cos(math.radians(a)), y + d * math.sin(math.radians(a))
                if all(road_d[int(cy_ + dy + HALF), int(cx_ + dx + HALF)] > 1.5 and free(cx_ + dx, cy_ + dy) for dx in (-r_, 0, r_) for dy in (-r_, 0, r_)): return cx_, cy_
        return x, y
    for kx0, ky0 in ((-90, -76), (-76, -90)):
        kx, ky = clear_spot(kx0, ky0, 4.2)
        z = zt(kx, ky); key = "clay:#b07a52"; r_ = 2.9
        cyl("stone:#a99b80", kx, ky, r_ + .3, z - .3, z + 1.2, n=20, top=False)
        for k in range(6):
            a0, a1 = k / 6 * math.pi / 2, (k + 1) / 6 * math.pi / 2
            cyl(key, kx, ky, r_ * math.cos(a0), z + 1.2 + 2 * math.sin(a0), z + 1.2 + 2 * math.sin(a1), n=20, r1=r_ * math.cos(a1), top=k == 5)
        opening("emit:#ff8c2a" if NIGHT else "flat:#24160e", (kx + r_ + .3, ky - 1), (kx + r_ + .3, ky + 1), .5, 1.1, z + .1, z + 1.1, out=.1)
        put(WOODPILE, kx + 3, ky + 4.2, 0, .8); take_poly(rect(kx, ky, 8, 8), 0)
    hall(-96, -88, 11, 6, 0, 2.6, "#b9592f", ridge="x", cols="all", core=None, steps=False, roof_h=1.4)
    amph_rows(-100.5, -90.2, -91.5, -85.8, .02, g, .5)
    for x, y in ((-82, -96), (-98, -78)): put(WHEEL, x, y, 0)
    face("dirt:#9e7a54", [(x, y, zt(x, y) + .02) for x, y in [(-112, -86), (-102, -92), (-100, -100), (-112, -98)]])
    scatter_jars(-92, -70, None, 22, 3.2, g); scatter_jars(-70, -84, None, 14, 2.4, g)
    # --- the libraries: stoas with benches before them, herms, a plane tree for shade
    hall(-106, 64, 11, 24, 0, 5.2, "#c8673e", ridge="y", cols="e", core=(-2.4, 0, 4.6, 23), g=g)
    for k in range(3): put(BENCH, -98.5, 56 + k * 7, 0, math.pi / 2)
    for x, y in ((-96, 52), (-96, 77)): put(STATUE, x, y, 0, 1.6)
    hall(92, -92, 24, 11, 0, 5.2, "#c8673e", ridge="x", cols="n", core=(0, -2.4, 23, 4.6), g=g)
    for k in range(3): put(BENCH, 84 + k * 8, -84.5, 0, 0)
    for x, y in ((80, -84), (104, -84)): put(STATUE, x, y, 0, 0)
    for x, y in ((-115, 50), (108, -100)): place("island_tree_02", x, y, zt(x, y), h=8, g=g); take_poly(rect(x, y, 4, 4), 0)
    # --- fields and vineyards from the drawing
    WH = [f for f in FLAT if f.get("rows") and f["fill"] != "#c9cf8a"]
    for i, f in enumerate(WH): wheat_field(f["pts"], f["fill"], *f["rows"], cut=i == 2)
    for f in FLAT:
        if f.get("fill") == "#c9cf8a": vineyard(f["pts"], g)
    for f in FLAT:                                                                        # estates' boundary walls drawn as outlines
        if f.get("fill") == "none" and f.get("stroke") == "#a08a68": pass

# ================================================================ the siege: camps, siege works, the cut woods
if SIEGE:
    g = random.Random(13)
    TENTS = []
    for c_, (w_, d_, zr) in (("#e2d4b4", (4.6, 3.4, 2.5)), ("#d6c5a0", (4.2, 3.2, 2.3)), ("#c9b48c", (5.2, 3.8, 2.7)), ("#b9a27c", (3.8, 3.0, 2.1)), ("#d9cdb0", (6.0, 4.2, 2.9))):
        with Part("tent") as P_:                                                       # a ridge tent: canvas over a pole, its guy ropes pegged out
            x0, x1, y0, y1 = -w_ / 2, w_ / 2, -d_ / 2, d_ / 2
            roof_face("canvas:" + c_, [(x0, y1, .15), (x1, y1, .15), (x1, 0, zr), (x0, 0, zr)]); roof_face("canvas:" + c_, [(x1, y0, .15), (x0, y0, .15), (x0, 0, zr), (x1, 0, zr)])
            face("canvas:" + shade(c_, .88), [(x0, y0, .15), (x0, y1, .15), (x0, 0, zr)][::-1]); face("canvas:" + shade(c_, .88), [(x1, y0, .15), (x1, y1, .15), (x1, 0, zr)])
            face("flat:#2a2018", [(x1 + .01, -.45, .15), (x1 + .01, .45, .15), (x1 + .01, 0, zr * .75)])
            for xe in (x0 - .1, x1 + .1): beam("wood:#6b5032", (xe, 0, 0), (xe, 0, zr + .35), r=.05)
            for xe, ye in ((x0 - .9, 0), (x1 + .9, 0)): beam("cloth:#8a7a60", (xe, ye, 0), (x0 - .1 if xe < 0 else x1 + .1, 0, zr + .3), r=.015, n=3)
        TENTS.append(P_.mesh)
    with Part("command") as P_:                                                        # the general's pavilion: walled, a double-pitched roof, a porch on poles
        prism("canvas:#b0442e", None, rect(0, 0, 8, 6), 0, 2.6)
        roof_face("canvas:#9c3a28", [(-4.3, 3.4, 2.45), (4.3, 3.4, 2.45), (4.3, 0, 4.6), (-4.3, 0, 4.6)]); roof_face("canvas:#9c3a28", [(4.3, -3.4, 2.45), (-4.3, -3.4, 2.45), (-4.3, 0, 4.6), (4.3, 0, 4.6)])
        for xe, sgn in ((-4, -1), (4, 1)): face("canvas:#b0442e", [(xe, -3, 2.6), (xe, 3, 2.6), (xe, 0, 4.6)][::sgn])
        face("canvas:#c9a36a", [(4, -2, 2.4), (4, 2, 2.4), (6.4, 2, 2.0), (6.4, -2, 2.0)][::-1])
        for y in (-2, 2): beam("wood:#5d4630", (6.4, y, 0), (6.4, y, 2.05), r=.06)
    COMMAND = P_.mesh
    with Part("standard") as P_:
        beam("wood:#4f3a26", (0, 0, 0), (0, 0, 9), r=.1); beam("wood:#4f3a26", (-.1, -1.3, 8.4), (-.1, 1.3, 8.4), r=.05)
        face("cloth:#a8261c", [(.0, -1.25, 8.35), (.0, 1.25, 8.35), (.05, 1.15, 6.2), (.05, -1.15, 6.4)]); cyl("flat:#b08a3a", 0, 0, .25, 9, 9.4, n=8, r1=.02)
    STANDARD = P_.mesh
    with Part("spears") as P_:                                                         # a rack of spears and a stack of shields beside it
        beam("wood:#5d4630", (-1.2, 0, 1.4), (1.2, 0, 1.4), r=.05)
        for x in (-1.2, 1.2): beam("wood:#5d4630", (x, 0, 0), (x, 0, 1.5), r=.05)
        for k in range(11): x = -1.1 + k * .22; beam("wood:#7a6040", (x, -.5, 0), (x + .05, .25, 2.9), r=.025, n=4); cyl("flat:#9aa0a6", x + .05, .25, .04, 2.9, 3.15, n=4, r1=0)
        for k in range(5):
            o = k * .09; cyl("flat:" + ("#a8792e" if k % 2 else "#8a3a24"), 1.9, -.3 + o * .3, .48, o, o + .07, n=14)
    SPEARS = P_.mesh
    with Part("cauldron") as P_:                                                       # a cooking fire: a ring of stones, logs, a cauldron on its tripod
        for k in range(10): cyl("rock:#8f897c", 1.0 * math.cos(k * .63), 1.0 * math.sin(k * .63), .22, 0, .25, n=6)
        for k in range(5): beam("wood:#3a2a1e", (.7 * math.cos(k * 1.26), .7 * math.sin(k * 1.26), .05), (0, 0, .45), r=.07)
        cyl("emit:#ff8c2a", 0, 0, .55, .05, .75, n=8, r1=.08)
        for k in range(3): beam("flat:#2a2622", (1.2 * math.cos(k * 2.09), 1.2 * math.sin(k * 2.09), 0), (0, 0, 2.0), r=.04, n=4)
        cyl("flat:#24211e", 0, 0, .38, 1.0, 1.45, n=12, r1=.42)
        for k in range(4): a_ = k * 1.57 + .5; beam("wood:#6b4f33", (2.4 * math.cos(a_) - .9 * math.sin(a_), 2.4 * math.sin(a_) + .9 * math.cos(a_), .25), (2.4 * math.cos(a_) + .9 * math.sin(a_), 2.4 * math.sin(a_) - .9 * math.cos(a_), .25), r=.22, n=7)
    CAULDRON = P_.mesh
    with Part("watch") as P_:                                                          # a timber watchtower: four posts, braces, a railed platform
        for x, y in ((-1.4, -1.4), (1.4, -1.4), (1.4, 1.4), (-1.4, 1.4)): beam("wood:#5d4630", (x * 1.15, y * 1.15, 0), (x, y, 6.5), r=.12)
        for z_ in (2.2, 4.4):
            for (x1, y1), (x2, y2) in (((-1.4, -1.4), (1.4, 1.4)), ((1.4, -1.4), (-1.4, 1.4))): beam("wood:#6b5032", (x1, y1, z_ - 1.8), (x2, y2, z_), r=.06)
        boxr("wood:#7a5a38", "wood:#8a6a44", 0, 0, 3.6, 3.6, 6.4, 6.6)
        for (x1, y1), (x2, y2) in zip(((-1.8, -1.8), (1.8, -1.8), (1.8, 1.8), (-1.8, 1.8)), ((1.8, -1.8), (1.8, 1.8), (-1.8, 1.8), (-1.8, -1.8))): beam("wood:#6b5032", (x1, y1, 7.5), (x2, y2, 7.5), r=.05)
        roof_face("canvas:#7d6a4c", [(-2, -2, 8.6), (2, -2, 8.6), (0, 0, 9.6)]); roof_face("canvas:#7d6a4c", [(2, -2, 8.6), (2, 2, 8.6), (0, 0, 9.6)]); roof_face("canvas:#7d6a4c", [(2, 2, 8.6), (-2, 2, 8.6), (0, 0, 9.6)]); roof_face("canvas:#7d6a4c", [(-2, 2, 8.6), (-2, -2, 8.6), (0, 0, 9.6)])
        for x, y in ((-1.8, -1.8), (1.8, -1.8), (1.8, 1.8), (-1.8, 1.8)): beam("wood:#5d4630", (x, y, 6.6), (x, y, 8.6), r=.06)
    WATCH = P_.mesh
    with Part("siegetower") as P_:                                                     # a siege tower: a tapering timber frame faced with hides, on solid wheels
        lv = [(0, 3.2), (5, 2.9), (10, 2.6), (15, 2.3)]
        for (z0, h0), (z1, h1) in zip(lv, lv[1:]):
            for k, ((ax, ay), (bx, by)) in enumerate(zip(((-1, -1), (1, -1), (1, 1), (-1, 1)), ((1, -1), (1, 1), (-1, 1), (-1, -1)))):
                face("canvas:" + ("#6e5235" if k % 2 else "#7c5e3e"), [(ax * h0, ay * h0, z0), (bx * h0, by * h0, z0), (bx * h1, by * h1, z1), (ax * h1, ay * h1, z1)])
            for ax, ay in ((-1, -1), (1, -1), (1, 1), (-1, 1)): beam("wood:#4f3a26", (ax * h0, ay * h0, z0), (ax * h1, ay * h1, z1), r=.14)
            boxr("wood:#4f3a26", "wood:#4f3a26", 0, 0, 2 * h1 + .3, 2 * h1 + .3, z1 - .2, z1)
        face("wood:#5d4129", [(2.3, -1.4, 15), (2.3, 1.4, 15), (4.4, 1.4, 16.4), (4.4, -1.4, 16.4)][::-1])
        for x, y in ((-2.2, -3.4), (2.2, -3.4), (-2.2, 3.4), (2.2, 3.4)):
            for k in range(10):
                a0, a1 = k / 10 * 2 * math.pi, (k + 1) / 10 * 2 * math.pi; r_ = .9
                face("wood:#3e2c1c", [(x + r_ * math.cos(a0), y, .9 + r_ * math.sin(a0)), (x + r_ * math.cos(a1), y, .9 + r_ * math.sin(a1)), (x + r_ * math.cos(a1), y + (.3 if y > 0 else -.3), .9 + r_ * math.sin(a1)), (x + r_ * math.cos(a0), y + (.3 if y > 0 else -.3), .9 + r_ * math.sin(a0))])
    SIEGETOWER = P_.mesh
    with Part("mantlet") as P_:                                                        # a mantlet: a wicker-and-plank screen on wheels, for creeping up to the walls
        face("wood:#6e5235", [(0, -2.2, .3), (0, 2.2, .3), (.4, 2.2, 2.6), (.4, -2.2, 2.6)]); face("wood:#6e5235", [(0, -2.2, .3), (0, 2.2, .3), (.4, 2.2, 2.6), (.4, -2.2, 2.6)][::-1])
        for y in (-2, 2): beam("wood:#4f3a26", (-.6, y, .3), (.5, y, .3), r=.25, n=8)
        for k in range(7): beam("wood:#4f3a26", (0, -2.1 + k * .7, .3), (.4, -2.1 + k * .7, 2.6), r=.04)
    MANTLET = P_.mesh
    with Part("ram") as P_:
        boxr("wood:#6b4c30", "wood:#7d5a38", 0, 0, 7, 3.4, .4, .7)
        roof_face("canvas:#5d4129", [(-3.6, 1.9, .9), (3.6, 1.9, .9), (3.6, 0, 3.2), (-3.6, 0, 3.2)]); roof_face("canvas:#5d4129", [(3.6, -1.9, .9), (-3.6, -1.9, .9), (-3.6, 0, 3.2), (3.6, 0, 3.2)])
        beam("wood:#4a3420", (-4.2, 0, 1.6), (4.6, 0, 1.6), r=.3); cyl("flat:#5a5650", 4.6, 0, .34, 1.3, 1.9, n=10)
        for x in (-2.6, 2.6):
            for s_ in (-1, 1): beam("wood:#3e2c1c", (x, s_ * 1.8, .45), (x, s_ * 2.0, .45), r=.45, n=10)
    RAM = P_.mesh
    with Part("ballista") as P_:
        boxr("wood:#6b4c30", "wood:#7d5a38", 0, 0, 2.6, 1.6, 0, .9); beam("wood:#5b4128", (-1.4, 0, 1.0), (1.8, 0, 1.6), r=.12)
        beam("wood:#5b4128", (1.4, -1.4, 1.5), (1.4, 1.4, 1.5), r=.08); beam("cloth:#b9ad92", (1.4, -1.4, 1.5), (-.6, 0, 1.2), r=.02, n=3); beam("cloth:#b9ad92", (1.4, 1.4, 1.5), (-.6, 0, 1.2), r=.02, n=3)
        for k in range(4): beam("wood:#7a6040", (-1 + k * .4, -.9, .2), (-1 + k * .4 + .1, -.9, 1.9), r=.03, n=4)
    BALLISTA = P_.mesh
    with Part("stump") as P_: cyl("wood:#6a5034", 0, 0, .35, 0, .5, n=8, r1=.3); cyl("wood:#c9a77a", 0, 0, .3, .5, .5, n=8); STUMP = P_
    STUMP = P_.mesh
    with Part("logs") as P_:
        for k in range(6): beam("wood:#5d4630", (-3, -.8 + (k % 3) * .55, .3 + (k // 3) * .5), (3, -.8 + (k % 3) * .55 + .1, .3 + (k // 3) * .5), r=.28, n=8)
    LOGS = P_.mesh
    with Part("torch") as P_: beam("wood:#3a2a1e", (0, 0, 0), (0, 0, 2.4), r=.06); cyl("flat:#2a2622", 0, 0, .14, 2.3, 2.55, n=6, r1=.18); cyl("emit:#ffcf6e", 0, 0, .14, 2.55, 3.05, n=6, r1=.02); TORCH = P_
    TORCH = P_.mesh
    def torch(x, y, z=None):
        if put(TORCH, x, y, 0, 0, 1, r=.3): LAMPS.append((x, y, zt(x, y) + 3.0, 700, "torch"))
    def fire(x, y):
        if put(CAULDRON, x, y, 0, g.uniform(0, 6), 1, r=2.4): LAMPS.append((x, y, zt(x, y) + 1.1, 3200, "fire")); take_poly(rect(x, y, 6, 6), 0)

    for name, ((cx, cy), (gx_, gy_)) in S["camps"].items():
        big = name == "commander's camp"; hw, hd = (26, 20) if big else (22, 17)
        if abs(gx_ - cx) > abs(gy_ - cy): hw, hd = hd, hw                                # the camp's long side faces the town
        dx, dy = (gx_ - cx), (gy_ - cy); dl = math.hypot(dx, dy); dx, dy = dx / dl, dy / dl
        gate = (cx + dx * (hd if abs(dy) > .5 else hw), cy + dy * (hd if abs(dy) > .5 else hw))
        fence = box_pts(cx - hw, cy - hd, cx + hw, cy + hd)
        # trampled ground, ragged at its edge, worn bare along the camp's lanes
        V, Fc = [], []; R = 1.0; x0, y0 = cx - hw - 14, cy - hd - 14; nx_, ny_ = int(2 * (hw + 14)) + 1, int(2 * (hd + 14)) + 1
        for j in range(ny_):
            for i in range(nx_): V.append((x0 + i, y0 + j, zt(x0 + i, y0 + j) + .015))
        for j in range(ny_ - 1):
            for i in range(nx_ - 1):
                x, y = x0 + i + .5, y0 + j + .5; e = min(hw + 9 - abs(x - cx), hd + 9 - abs(y - cy)) + 5 * N.noise(Vector((x * .07, y * .07, cx * .01)))
                if e > 0 and road_d[int(y + HALF), int(x + HALF)] > -.5: a_ = j * nx_ + i; Fc.append([a_, a_ + 1, a_ + nx_ + 1, a_ + nx_])
        me = bpy.data.meshes.new("camp"); me.from_pydata(V, [], Fc); me.materials.append(mat("dirt:#bfa983")); ROOT.objects.link(bpy.data.objects.new("camp", me))
        # the ditch and bank, and on the bank a palisade of sharpened stakes, with a gap at the gate
        for p, q in zip(fence, fence[1:] + fence[:1]):
            ln = math.hypot(q[0] - p[0], q[1] - p[1]); ux, uy = (q[0] - p[0]) / ln, (q[1] - p[1]) / ln; ox, oy = uy, -ux   # outward
            if (ox * (cx - p[0]) + oy * (cy - p[1])) > 0: ox, oy = -ox, -oy
            n = int(ln / .42)
            for i in range(n + 1):
                x, y = p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n
                if math.hypot(x - gate[0], y - gate[1]) < 3.4: continue
                h = 2.9 * g.uniform(.88, 1.06); lean = g.uniform(-.05, .05)
                beam("wood:#6f5236", (x, y, -.1), (x + ox * .15 + lean, y + oy * .15 + lean, h), r=.16, n=6); cyl("wood:#8a6a48", x + ox * .15 + lean, y + oy * .15 + lean, .16, h, h + .45, n=6, r1=0)
            for i in range(int(ln / 1.0)):
                a_, b_ = (p[0] + ux * i, p[1] + uy * i), (p[0] + ux * (i + 1), p[1] + uy * (i + 1))
                if min(math.hypot(a_[0] - gate[0], a_[1] - gate[1]), math.hypot(b_[0] - gate[0], b_[1] - gate[1])) < 3.4: continue
                bank = [(a_[0] - ox * .9, a_[1] - oy * .9), (b_[0] - ox * .9, b_[1] - oy * .9), (b_[0] + ox * 1.2, b_[1] + oy * 1.2), (a_[0] + ox * 1.2, a_[1] + oy * 1.2)]
                hb = .55 + .15 * N.noise(Vector((a_[0] * .2, a_[1] * .2, 4)))
                face("dirt:#a89474", [(x, y, zt(x, y) + (hb if k_ in (0, 1) else .05)) for k_, (x, y) in enumerate(bank)][::-1]); cap("dirt:#a89474", bank[:2] + [(b_[0] - ox * .2, b_[1] - oy * .2), (a_[0] - ox * .2, a_[1] - oy * .2)], zt(*a_) + hb)
                ditch = [(a_[0] + ox * 1.4, a_[1] + oy * 1.4), (b_[0] + ox * 1.4, b_[1] + oy * 1.4), (b_[0] + ox * 3.4, b_[1] + oy * 3.4), (a_[0] + ox * 3.4, a_[1] + oy * 3.4)]
                if road_d[int(ditch[0][1] + HALF), int(ditch[0][0] + HALF)] > .5: face("dirt:#5f5040", [(x, y, zt(x, y) + .02) for x, y in ditch][::-1])
        for x, y in fence: put(WATCH, x, y, 0, g.uniform(0, .2), 1, r=0); LAMPS.append((x, y, zt(x, y) + 7.6, 900, "torch"))
        for s_ in (-1, 1):                                                               # the gate: a watchtower each side, torches
            tx, ty = gate[0] + dy * s_ * 4.6, gate[1] - dx * s_ * 4.6
            inst(WATCH, tx, ty, zt(tx, ty)); LAMPS.append((tx, ty, zt(tx, ty) + 7.6, 1100, "torch")); take_poly(rect(tx, ty, 4, 4), 0)
        take_poly(rect(cx, cy, 11, 9), 0)
        inst(COMMAND, cx, cy, zt(cx, cy), math.atan2(dy, dx))
        for k, a_ in enumerate((.6, -.6, 2.2)): px_, py_ = cx + 7 * math.cos(math.atan2(dy, dx) + a_), cy + 7 * math.sin(math.atan2(dy, dx) + a_); put(STANDARD, px_, py_, 0, a_, 1, r=.3)
        lane = (gate, (cx, cy))
        for t_ in (.3, .65):                                                             # cooking fires beside the main lane and out in the tent lines
            for s_ in (-1, 1):
                fire(gate[0] + (cx - gate[0]) * t_ + dy * s_ * 6.5, gate[1] + (cy - gate[1]) * t_ - dx * s_ * 6.5)
        for s_ in (-1, 1): fire(cx + dy * s_ * (hw if abs(dy) > .5 else hd) * .62 - dx * 6, cy - dx * s_ * (hw if abs(dy) > .5 else hd) * .62 - dy * 6)
        # tents in loose lanes, turned to them, now and then a gap where a fire burns or stores are kept
        across = (abs(dy) > .5)
        for i in range(-12, 13):
            for j in range(-6, 7):
                u, v = i * 5.2 + g.uniform(-.5, .5), j * 5.6 + g.uniform(-.6, .6)
                x, y = (cx + u, cy + v) if across else (cx + v, cy + u)
                if abs(x - cx) > hw - 3.2 or abs(y - cy) > hd - 3.2: continue
                if math.hypot(x - cx, y - cy) < 10 or seg_dist(x, y, *lane[0], *lane[1]) < 4: continue
                r_ = g.random()
                if r_ < .02: fire(x, y); continue
                if r_ < .1:
                    for _ in range(4): put(g.choice((CRATE, SACK, AMPH, PITHOS)), x + g.uniform(-1.6, 1.6), y + g.uniform(-1.4, 1.4), 0, g.uniform(0, 6), 1, r=.3)
                    continue
                if r_ < .12: put(SPEARS, x, y, 0, (0 if across else math.pi / 2) + g.uniform(-.2, .2), 1, r=1.5); continue
                put(g.choice(TENTS), x, y, 0, (0 if across else math.pi / 2) + g.choice((0, math.pi)) + g.uniform(-.12, .12), 1, r=1.4)
        for k in range(3): fire(cx + g.uniform(-hw + 6, hw - 6), cy + g.uniform(-hd + 6, hd - 6))
        put(CART, cx + (hw - 5) * (1 if g.random() < .5 else -1), cy + g.uniform(-hd + 5, hd - 5), 0, g.uniform(0, 6), 1, r=2)
        put(SPEARS, gate[0] - dx * 5 + dy * 3, gate[1] - dy * 5 - dx * 3, 0, math.atan2(dy, dx), 1, r=1.2)
        take_poly(box_pts(cx - hw - 4, cy - hd - 4, cx + hw + 4, cy + hd + 4), 0)
        # the siege works out in front, toward the walls but clear of the road round them and of the camp's own road
        side = (-dy, dx); base = (cx + dx * (hd + 13 if abs(dy) > .5 else hw + 13), cy + dy * (hd + 13 if abs(dy) > .5 else hw + 13))
        if name == "camp B": base = (cx + dx * (hd + 3), cy + dy * (hd + 3))
        heading = math.atan2(dy, dx)
        for k, (off, kind) in enumerate(((-16, SIEGETOWER if big else RAM), (16, BALLISTA), (-26, MANTLET), (-21, MANTLET), (22, BALLISTA), (27, MANTLET))):
            x, y = base[0] + side[0] * off, base[1] + side[1] * off
            if free(x, y, 3) and road_d[int(y + HALF), int(x + HALF)] > 4: inst(kind, x, y, zt(x, y), heading); take_poly(rect(x, y, 8, 8), 0)
        # where the woods were cut for all this timber: stumps and log piles
        for _ in range(26):
            a_ = g.uniform(0, 6.3); d_ = g.uniform(32, 48); x, y = cx + d_ * math.cos(a_), cy + d_ * math.sin(a_)
            if free(x, y, 2) and road_d[int(y + HALF), int(x + HALF)] > 2: put(g.choice((STUMP, STUMP, STUMP, LOGS)), x, y, 0, g.uniform(0, 6), g.uniform(.8, 1.2), r=1.5)
    # the town keeps watch too: braziers on the walls' walk, fires behind the shut gates
    oc = S["octagon"]
    for p, q in zip(oc, oc[1:] + oc[:1]):
        ln = math.hypot(q[0] - p[0], q[1] - p[1])
        for k in range(1, int(ln / 22) + 1):
            t = k / (int(ln / 22) + 1); x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t; x, y = x * .985, y * .985
            cyl("flat:#2a2622", x, y, .4, zt(x, y) + 8, zt(x, y) + 8.5, n=8, r1=.5); cyl("emit:#ffb347", x, y, .38, zt(x, y) + 8.5, zt(x, y) + 8.8, n=8, r1=.1)
            LAMPS.append((x, y, zt(x, y) + 9.2, 1100, "fire"))
    for gx_, gy_ in S["gates"]:
        for s_ in (-1, 1):
            x, y = gx_ * .88 + (s_ * 5 if gx_ == 0 else 0), gy_ * .88 + (s_ * 5 if gy_ == 0 else 0)
            cyl("flat:#2a2622", x, y, .45, zt(x, y), zt(x, y) + 1.0, n=8, r1=.6); cyl("emit:#ffb347", x, y, .55, zt(x, y) + 1.0, zt(x, y) + 1.35, n=8, r1=.1)
            LAMPS.append((x, y, zt(x, y) + 1.8, 2600, "fire"))

# ================================================================ trees from the drawing, then groves, cypress lines and the wild ground
g = random.Random(23)
for x, y, sp in S["trees"]: tree_at(x, y, sp, g)
if not SIEGE:
    for _ in range(5000):                                                                 # olive groves, in loose rows, where a slow noise says grove
        x, y = g.uniform(-245, 245), g.uniform(-245, 245)
        if N.noise(Vector((x * .018, y * .018, 4.4))) < .12 or in_town(x, y, -20) or not free(x, y, 2): continue
        if x * x / 95 ** 2 + (y - 111) ** 2 / 78 ** 2 < 1: continue
        if any(abs(x - cx_) < 50 and abs(y - cy_) < 40 for cx_, cy_ in ((168, 0), (-160, -8))): continue
        tree_at(round(x / 9) * 9 + g.uniform(-1.2, 1.2), round(y / 8) * 8 + g.uniform(-1, 1), "olive", g)
    for w, kind, pts in ROADS3:                                                           # cypresses along the country roads
        if kind != "road": continue
        for a, b in zip(pts, pts[1:]):
            ln = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            for k in range(int(ln / 14)):
                if g.random() < .5: continue
                t = (k + .5) * 14; s_ = g.choice((-1, 1)); x, y = a[0] + ux * t - uy * (w / 2 + 3) * s_, a[1] + uy * t + ux * (w / 2 + 3) * s_
                if not in_town(x, y, -14): tree_at(x, y, "cypress", g)
    for _ in range(2600):                                                                 # crags, boulders and scree on the acropolis' slopes
        x, y = g.uniform(-92, 92), g.uniform(40, 185)
        rm = ROCKM[int(y + HALF), int(x + HALF)]
        if rm > .25 and free(x, y, 1) and g.random() < rm * .6:
            big = g.random() < .14 and road_d[int(y + HALF), int(x + HALF)] > 9; e = place("boulder_01", x, y, zt(x, y) - (1.2 if big else .4), h=g.uniform(2.5, 6) if big else g.uniform(.6, 2.2), g=g)
            if e and big: e.scale = (e.scale[0] * g.uniform(1.2, 1.7), e.scale[1] * g.uniform(1.2, 1.7), e.scale[2]); e.rotation_euler.x = g.uniform(-.3, .3)
            take_poly(rect(x, y, 2, 2), 0)
    for _ in range(60):                                                                   # rocks along the shore
        x = g.uniform(-240, 120); y = shore(x) + g.uniform(-4, 6)
        if free(x, y + 9) and (x < -60 or x > 40): place("boulder_01", x, y, zt(x, y) - .3, h=g.uniform(.6, 2.2), g=g)
else:
    g2 = random.Random(21)
    def clear(x, y, pad=0):
        if inpoly(x, y, [(px * (1 + (26 + pad) / 78), py * (1 + (26 + pad) / 78)) for px, py in OCTA]): return False
        return free(x, y, int(pad / 3)) and abs(x) + abs(y) < 236
    for f in FLAT:                                                                        # the drawing's scrub patches: bushes and grass
        if "pts" not in f or f.get("fill") in ("#d6c79c", "none"): continue
        pts = f["pts"]; xs, ys = [p[0] for p in pts], [p[1] for p in pts]; dry = f["fill"] in ("#cbb97c", "#a9a56c")
        for _ in range(int(abs(area(pts)) / 9)):
            x, y = g2.uniform(min(xs), max(xs)), g2.uniform(min(ys), max(ys))
            if inpoly(x, y, pts) and free(x, y): place(g2.choice(("grass_medium_01", "wild_rooibos_bush") if dry else ("searsia_lucida", "wild_rooibos_bush", "searsia_burchellii")), x, y, zt(x, y), h=g2.uniform(.5, 1.0) if dry else g2.uniform(.8, 2.0), g=g2)
    for _ in range(40):                                                                   # rocky outcrops in the wild quarters
        x, y = g2.uniform(-230, 230), g2.uniform(-230, 230)
        if clear(x, y, 10):
            for _ in range(g2.randint(3, 8)): place("boulder_01", x + g2.gauss(0, 3), y + g2.gauss(0, 3), zt(x, y) - .5, h=g2.uniform(1, 3.5), g=g2)
            take_poly(rect(x, y, 10, 10), 0)
g = random.Random(17)                                                                     # the open ground: shrubs, tufts, stones
for _ in range(int(opt("--scatter", 26000))):
    x, y = g.uniform(-HALF + 5, HALF - 5), g.uniform(-HALF + 5, HALF - 5)
    if not free(x, y): continue
    z = zt(x, y); k = g.random(); rock = ROCKM[int(y + HALF), int(x + HALF)]
    if k < .32: place("grass_medium_01", x, y, z, h=g.uniform(.45, .8), g=g)
    elif k < .55: place("wild_rooibos_bush", x, y, z, h=g.uniform(.7, 1.3), g=g)
    elif k < .82: place("searsia_lucida", x, y, z, h=g.uniform(1.0, 2.0), g=g)
    elif k < .95: place("searsia_burchellii", x, y, z, h=g.uniform(1.6, 3.0), g=g)
    else: place("boulder_01", x, y, z - .2, h=g.uniform(.5, 1.4) * (1 + 2 * rock), g=g)

# ================================================================ lights
for x, y, z, w_, kind in LAMPS:
    L = bpy.data.lights.new("lamp", "POINT"); L.energy = w_ * float(opt("--lamps", 1.5)); L.color = (1, .4, .12) if kind == "fire" else (1, .52, .2); L.shadow_soft_size = .8
    o = bpy.data.objects.new("lamp", L); ROOT.objects.link(o); o.location = (x, y, z)
for x, y, z, r_, kind in ([gl for gl in S["glows"] if gl[4] == "torch" and gl[2] > 6] if SIEGE else S["glows"]):
    L = bpy.data.lights.new("glow", "POINT"); L.energy = (1300 if kind == "fire" else 380) * (r_ / 5) ** 2; L.color = (1, .62, .3) if kind == "fire" else (1, .74, .42)
    L.shadow_soft_size = .4; o = bpy.data.objects.new("glow", L); ROOT.objects.link(o)
    zz = zt(x, y) + (z if kind == "torch" else 0); o.location = (x, y, zz + (.8 if kind == "fire" else .6))
    if kind == "torch": beam("wood:#3a2a1e", (x, y, zz - .9), (x, y, zz + .2), r=.06); cyl("emit:#ffcf6e", x, y, .2, zz + .2, zz + .8, n=6, r1=.04)
    elif not any("circle" in f and math.hypot(f["circle"][0] - x, f["circle"][1] - y) < 1 for f in FLAT): cyl("emit:#ff9a3a", x, y, .8, zz, zz + 1.3, n=8, r1=.1)
build_geo()

el = math.atan(1 / 1.05)
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); ROOT.objects.link(sun)
sun.rotation_euler = Vector((SUN[0] * math.cos(el), SUN[1] * math.cos(el), -math.sin(el))).to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True; bg = world.node_tree.nodes["Background"]
if NIGHT:
    sun.data.energy = float(opt("--moon", 4)); sun.data.color = (.78, .85, 1.0); sun.data.angle = math.radians(1.5)
    bg.inputs[0].default_value = (.30, .36, .55, 1); bg.inputs[1].default_value = float(opt("--sky", 1.0))
else:                                                                                   # a real sky (a CC0 HDRI from Poly Haven) for the light that is not the sun
    sun.data.energy = float(opt("--sun", 5.2)); sun.data.color = (1.0, .91, .78); sun.data.angle = math.radians(1.6)
    hdr = os.path.join(ASSETS, opt("--hdri", "kloofendal_48d_partly_cloudy_puresky"), opt("--hdri", "kloofendal_48d_partly_cloudy_puresky") + "_2k.hdr")
    wt = world.node_tree; env = wt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(hdr)
    mp = wt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(float(opt("--hdri-rot", 200)))); tc = wt.nodes.new("ShaderNodeTexCoord")
    wt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); wt.links.new(mp.outputs[0], env.inputs["Vector"]); wt.links.new(env.outputs["Color"], bg.inputs[0])
    bg.inputs[1].default_value = float(opt("--sky", .9))

# ================================================================ a last sweep: no scattered plant or stone may reach over a walker's line
from mathutils.kdtree import KDTree
KD = KDTree(len(ROUTE_PTS))
for i, (x, y, z) in enumerate(ROUTE_PTS): KD.insert((x, y, 0), i)
KD.balance(); SIZE = {c.name: sz for v in LIB.values() for c, sz in v}; swept = 0
for o in [o for o in ROOT.objects if o.type == "EMPTY" and o.instance_collection and o.instance_collection.name in SIZE]:
    sz = SIZE[o.instance_collection.name]; r = max(sz.x, sz.y) / 2 * o.scale[0]
    co, i, d = KD.find((o.location.x, o.location.y, 0))
    if d < r + .4 and o.location.z < ROUTE_PTS[i][2] + 3: bpy.data.objects.remove(o); swept += 1
print("SWEPT %d plants and stones off the routes" % swept)
# ================================================================ the check: is every walker on a surface at its height, and can the camera see it?
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
bad_ground, hidden = [], []
for x, y, z in ROUTE_PTS:
    hit, loc, *_ = scene.ray_cast(dg, Vector((x, y, z + 2.0)), Vector((0, 0, -1)))
    if not hit or abs(loc.z - z) > .3: bad_ground.append((x, y, z, round(loc.z, 2) if hit else None, _[2].name if hit else None))
    p = Vector((x, y, z + .3)); hit, loc, *_ = scene.ray_cast(dg, p + TOWARD * 400, -TOWARD)
    if hit and (loc - p).length > 1.5: hidden.append((x, y, z))
print("ROUTE CHECK: %d samples; %d not on a surface at their height; %d hidden from the camera" % (len(ROUTE_PTS), len(bad_ground), len(hidden)))
for b in bad_ground[:25]: print("  off the ground:", b)
for b in hidden[:25]: print("  hidden:", b)
for w in ("hidden", "bad_ground"):
    json.dump(dict(hidden=hidden, bad_ground=bad_ground), open(OUT.rsplit(".", 1)[0] + "-check.json", "w"))

scene.render.engine = "CYCLES"; scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6; scene.cycles.transparent_max_bounces = 24
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()
    for dev in prefs.devices: dev.use = True
    scene.cycles.device = "GPU"
except Exception as ex: print("GPU not enabled:", ex)
scene.view_settings.view_transform = opt("--view", "AgX")
if scene.view_settings.view_transform == "AgX": scene.view_settings.look = opt("--look", "AgX - Punchy")
scene.view_settings.exposure = float(opt("--exposure", 0))
if "--border" in argv:
    x0, y0, x1, y1 = map(float, opt("--border", "").split(",")); r = scene.render
    r.use_border = True; r.use_crop_to_border = True; r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = x0, x1, 1 - y1, 1 - y0
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"; scene.render.filepath = OUT
os.makedirs(os.path.dirname(OUT), exist_ok=True)
if "--save" in argv: bpy.ops.wm.save_as_mainfile(filepath=OUT.rsplit(".", 1)[0] + ".blend")
if "--no-render" not in argv: bpy.ops.render.render(write_still=True); print("WROTE", OUT)
