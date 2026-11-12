"""What grows and what lies about: olives, cypresses, pines and planes; vines in rows; the maquis of the open ground; crags
and boulders on the acropolis; rocks along the shore.

Trees are built as clouds of small leaf cards on a trunk (each species in several individuals); scanned shrubs and rocks come
from Poly Haven. Nothing is planted on a road, and no tree where it would stand between the camera and a walker."""
import bpy, math, os, random
import numpy as np
from mathutils import Vector
from . import core, land, houses, country, props
from .core import S, ASSETS, ROOT, Part, face, beam, inst, in_view, inpoly, Scatter, collection_of, lin
from .land import fbm

# ---------------------------------------------------------------- trees and bushes as leaf clouds
def cards(key, blobs, n, size, g, inner=.5, up=.35):
    """n leaf cards scattered through ellipsoids (cx, cy, cz, rx, ry, rz), each facing outward and a little up."""
    wts = [b[3] * b[4] * b[5] for b in blobs]
    for _ in range(n):
        bx, by, bz, rx, ry, rz = g.choices(blobs, wts)[0]
        d = Vector((g.gauss(0, 1), g.gauss(0, 1), g.gauss(0, 1))).normalized()
        if d.z < -.2: d.z *= -.6
        u = g.uniform(inner, 1) ** .6; p = Vector((bx + d.x * rx * u, by + d.y * ry * u, bz + d.z * rz * u))
        nrm = (d + Vector((g.gauss(0, .35), g.gauss(0, .35), up + g.gauss(0, .2)))).normalized()
        t1 = nrm.orthogonal().normalized(); t2 = nrm.cross(t1); a = g.uniform(0, 6.283); t1, t2 = t1 * math.cos(a) + t2 * math.sin(a), t2 * math.cos(a) - t1 * math.sin(a)
        s = size * g.uniform(.65, 1.35)
        face(key, [tuple(p - t1 * s - t2 * s * .8), tuple(p + t1 * s - t2 * s * .8), tuple(p + t1 * s + t2 * s * .8), tuple(p - t1 * s + t2 * s * .8)], va=g.random(), vb=u)
def limb(key, pts, r0, r1):
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        t0, t1 = k / (len(pts) - 1), (k + 1) / (len(pts) - 1); beam(key, a, b, r0 + (r1 - r0) * (t0 + t1) / 2, 6)
def make(name, fn, k=5):
    out = []
    for i in range(k):
        g = random.Random(hash(name) % 1000 + i * 31)
        with Part("%s%d" % (name, i)) as p: fn(g)
        out.append(p.mesh)
    return out
def _cypress(g):
    H = g.uniform(8.5, 12.5); R = g.uniform(.95, 1.35); beam("bark", (0, 0, 0), (0, 0, H * .5), .16, 6)
    blobs = [(g.uniform(-.1, .1), g.uniform(-.1, .1), .7 + (H - .9) * t, R * math.sin(math.pi * (.12 + .86 * t)) ** .55 * (1 - .28 * t), R * math.sin(math.pi * (.12 + .86 * t)) ** .55 * (1 - .28 * t), H / 9) for t in (i / 11 for i in range(12))]
    cards("leaf:#34502f", blobs, 1500, .3, g, .55, .15)
def _olive(g):
    h = g.uniform(1.3, 1.9); lean = g.uniform(-.3, .3); limb("bark:#6b6252", [(0, 0, 0), (lean * .4, .1, h * .5), (lean, -.1, h)], .26, .16)
    blobs = []
    for i in range(g.randint(3, 5)):
        a = g.uniform(0, 6.283); r = g.uniform(.5, 1.5); c = (lean + r * math.cos(a), r * math.sin(a), h + g.uniform(.9, 1.8)); rr = g.uniform(1.2, 1.9)
        blobs.append((*c, rr, rr, rr * .75)); limb("bark:#6b6252", [(lean, -.1, h), (c[0] * .7, c[1] * .7, c[2] - .2)], .13, .06)
    cards("leaf:#7f8b62", blobs, 950, .26, g, .45, .3)
def _plane(g):
    h = g.uniform(3.6, 4.8); limb("bark:#8f8a78", [(0, 0, 0), (.1, .1, h * .5), (0, 0, h)], .42, .3)
    blobs = []
    for i in range(g.randint(4, 6)):
        a = g.uniform(0, 6.283); r = g.uniform(1.2, 3.4); c = (r * math.cos(a), r * math.sin(a), h + g.uniform(1.8, 4.6)); rr = g.uniform(2.4, 3.6)
        blobs.append((*c, rr, rr, rr * .7)); limb("bark:#8f8a78", [(0, 0, h), (c[0] * .5, c[1] * .5, h + 1.4), (c[0] * .85, c[1] * .85, c[2])], .22, .08)
    cards("leaf:#56703a", blobs, 1900, .5, g, .45, .35)
def _stonepine(g):
    h = g.uniform(6.5, 9.5); lean = g.uniform(-.6, .6); limb("bark:#7a5a44", [(0, 0, 0), (lean * .3, 0, h * .5), (lean, 0, h)], .3, .2)
    blobs = []
    for i in range(g.randint(4, 6)):
        a = g.uniform(0, 6.283); r = g.uniform(.6, 2.6); c = (lean + r * math.cos(a), r * math.sin(a), h + g.uniform(.6, 1.6)); rr = g.uniform(1.8, 2.7)
        blobs.append((*c, rr, rr, rr * .45)); limb("bark:#7a5a44", [(lean, 0, h - .6), (c[0], c[1], c[2] - .3)], .12, .06)
    cards("leaf:#3d5a36", blobs, 1300, .34, g, .5, .5)
def _aleppo(g):
    h = g.uniform(3.0, 4.6); lean = g.uniform(-.8, .8); H = h + g.uniform(4.5, 7.0); limb("bark:#7b6a58", [(0, 0, 0), (lean * .4, .15, h), (lean, 0, H * .8)], .24, .1)
    blobs = [(lean * t + g.uniform(-.7, .7), g.uniform(-.7, .7), h + (H - h) * t, (2.4 - 1.5 * t) * g.uniform(.8, 1.15), (2.4 - 1.5 * t) * g.uniform(.8, 1.15), 1.1) for t in (i / 5 for i in range(6))]
    cards("leaf:#48653a", blobs, 1300, .32, g, .4, .4)
def _fig(g):
    limb("bark:#8a8474", [(0, 0, 0), (.1, 0, 1.0)], .16, .12); blobs = [(g.uniform(-.8, .8), g.uniform(-.8, .8), g.uniform(1.6, 2.6), 1.3, 1.3, .9) for _ in range(3)]
    cards("leaf:#4f7030", blobs, 520, .3, g, .4, .4)
def _vine(g):
    limb("bark:#5c4a38", [(0, 0, 0), (0, 0, .5)], .04, .03); cards("leaf:#62803a", [(0, 0, .62, .55, .55, .32)], 46, .17, g, .2, .5)
def _bush(col, r, n, size):
    def f(g):
        blobs = [(g.uniform(-r * .6, r * .6), g.uniform(-r * .6, r * .6), r * g.uniform(.3, .5), r * g.uniform(.5, .9), r * g.uniform(.5, .9), r * g.uniform(.3, .5)) for _ in range(g.randint(2, 4))]
        cards("leaf:" + col, blobs, n, size, g, .3, .5)
    return f
def _tuft(g): cards("leaf:#b3a468", [(0, 0, .18, .32, .32, .2)], 22, .13, g, .2, .8)
def _reed(g): cards("leaf:#8c9a52", [(0, 0, .9, .5, .5, .9)], 60, .16, g, .2, .1)

# ---------------------------------------------------------------- scanned shrubs and rocks from Poly Haven
def load(name, lods=("LOD2", "LOD1", "LOD3", "LOD0"), skip=("leaves_", "branches_", "geometry_nodes", "_trunk", "dead_branch")):
    """The asset's objects (one per variant, at the first level of detail available), each in its own collection with its size."""
    path = os.path.join(ASSETS, name, name + ".blend")
    try:
        with bpy.data.libraries.load(path, link=False) as (src, dst): dst.objects = list(src.objects)
    except Exception as ex: print("ASSET FAILED", name, ex); return []
    for im in bpy.data.images:
        if im.filepath.startswith("//"):
            cand = os.path.join(ASSETS, name, im.filepath[2:].replace("\\", "/"))
            if os.path.exists(cand): im.filepath = cand
    objs = [o for o in dst.objects if o is not None and o.type == "MESH" and not any(t in o.name.lower() for t in skip)]; groups = {}
    for o in objs:
        base = o.name; lod = ""
        for l in ("LOD0", "LOD1", "LOD2", "LOD3"):
            if o.name.endswith("_" + l): base, lod = o.name[:-5], l
        groups.setdefault(base, {})[lod] = o
    out = []
    for base, d in sorted(groups.items()):
        o = next((d[l] for l in lods if l in d), d.get(""))
        if o is None: continue
        pts = [o.matrix_basis @ Vector(v) for v in o.bound_box]; lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        c = bpy.data.collections.new(base); c.objects.link(o); c.instance_offset = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z); out.append((c, hi - lo))
    for o in dst.objects:                                                                 # the levels of detail not used are dropped
        if o is not None and not o.users_collection: bpy.data.objects.remove(o)
    return out
def retint(variants, hexcol, fac=.7, gain=2.4, only=None):
    """Pull a scanned model's colours toward a chosen one, keeping its light and dark."""
    mats = {sl.material for c, _ in variants for o in c.all_objects for sl in o.material_slots if sl.material}
    for m in mats:
        if only and not any(t in m.name.lower() for t in only): continue
        nt = m.node_tree
        for b in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
            src = b.inputs["Base Color"]
            if not src.links: continue
            s0 = src.links[0].from_socket; bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(s0, bw.inputs[0])
            k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = gain; nt.links.new(bw.outputs[0], k.inputs[0])
            mm = nt.nodes.new("ShaderNodeMix"); mm.data_type = "RGBA"; mm.blend_type = "MULTIPLY"; mm.inputs[0].default_value = 1; mm.inputs[6].default_value = (*lin(hexcol), 1); nt.links.new(k.outputs[0], mm.inputs[7])
            mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs[0].default_value = fac; nt.links.new(s0, mx.inputs[6]); nt.links.new(mm.outputs[2], mx.inputs[7]); nt.links.new(mx.outputs[2], src)
def place(variants, x, y, z, g, h=None, scale=1.0, rot=None, tilt=None, sink=0.0):
    """One instance of a scanned model as an object (trees and big rocks: the visibility check must see them)."""
    c, size = g.choice(variants)
    if h: scale = scale * h / max(1e-3, size.z)
    e = bpy.data.objects.new(c.name, None); ROOT.objects.link(e); e.instance_type = "COLLECTION"; e.instance_collection = c
    e.location = (x, y, z - sink * scale * size.z); e.scale = scale if isinstance(scale, tuple) else (scale,) * 3
    e.rotation_euler = ((tilt[0], tilt[1]) if tilt else (0, 0)) + (g.uniform(0, 6.283) if rot is None else rot,); return e
def strew(variants, x, y, z, g, h=None, scale=1.0, sink=0.0, tilt=0.0):
    """One instance among thousands (through the scatter modifier)."""
    c, size = g.choice(variants)
    if h: scale = scale * h / max(1e-3, size.z)
    Scatter.add(c, x, y, z - sink * scale * size.z, g.uniform(0, 6.283), scale, (g.uniform(-tilt, tilt), g.uniform(-tilt, tilt)))

def hides_road(x, y, h, r):
    """Would something this tall and wide stand between the camera and a road?"""
    t = 0.0
    while t < h * .62 + r:
        if land.road_dist(x - t, y + t) < .6 + r * .5: return True
        t += 1.2
    return False

def build():
    g = random.Random(23); zt = land.zt
    CYP = make("cypress", _cypress, 6); OLI = make("olive", _olive, 7); PLA = make("plane", _plane, 4); SPI = make("stonepine", _stonepine, 4); ALE = make("aleppo", _aleppo, 5)
    FIG = make("fig", _fig, 3); VINE = [collection_of(m, m.name) for m in make("vine", _vine, 4)]
    def bushes(name, col, r, n, size, k=4): return [(collection_of(m, m.name), Vector((2 * r, 2 * r, 1.3 * r))) for m in make(name, _bush(col, r, n, size), k)]
    LENT = bushes("lentisk", "#586b3e", 1.0, 230, .15); KERM = bushes("kermes", "#4c5d38", .8, 190, .13); BROOM = bushes("broom", "#87895a", .7, 150, .12); SAGE = bushes("sage", "#9b9d82", .5, 100, .1)
    BURN = bushes("burnet", "#a08f5c", .45, 90, .1)
    TUFT = [(collection_of(m, m.name), Vector((.6, .6, .4))) for m in make("tuft", _tuft, 3)]; REED = [(collection_of(m, m.name), Vector((1, 1, 1.8))) for m in make("reed", _reed, 3)]
    ROCK = load("rock_moss_set_01", ("",)) + load("rock_moss_set_02", ("",)); BOUL = load("boulder_01", ("LOD3",)) + load("namaqualand_boulder_03", ("LOD3",))
    FACE = load("rock_face_01", ("",)) + load("rock_face_02", ("",)); CLIFF = load("namaqualand_cliff_02", ("LOD3",))
    for v in (ROCK, BOUL, FACE, CLIFF): retint(v, "#cdc6b4", .78)
    TREE = dict(cypress=CYP, olive=OLI, plane=PLA, stonepine=SPI, aleppo=ALE, fig=FIG, court=FIG + OLI[:2])
    SIZE = dict(cypress=(1.3, 11), olive=(2.6, 4.6), plane=(4.4, 9), stonepine=(4.2, 9.5), aleppo=(3.0, 9), fig=(1.8, 3.2), court=(1.8, 3.4))
    planted = []
    def tree(kind, x, y, z=None, sc=None, check=True):
        r, h = SIZE[kind]; sc = sc or g.uniform(.85, 1.15)
        if check and (not land.free(x, y, r * .5) or hides_road(x, y, h * sc, r * sc) or land.sd_at(x, y) < 5): return False
        inst(g.choice(TREE[kind]), x, y, (zt(x, y) if z is None else z) - .05, g.uniform(0, 6.283), (sc * g.uniform(.92, 1.08), sc * g.uniform(.92, 1.08), sc))
        land.take_disc(x, y, max(.8, r * .45)); land.paint_disc("lush", x, y, r * .9, .5, r); planted.append((x, y)); return True
    def clear_of(x, y, polys): return not any(inpoly(x, y, P) for P in polys)
    # --- trees the builders asked for: in house courts, the agora, the sanctuaries
    for x, y, z, kind in houses.TREES: tree(kind, x, y, z, sc=.72 if kind == "plane" else None, check=False)
    # --- groves: olive orchards in loose rows; planes and cypresses round the schools; cypresses by the tombs
    for P, kind, sp in country.GROVES:
        x0, y0, x1, y1 = core.bbox(P); y = y0 + sp / 2
        while y < y1:
            x = x0 + sp / 2 + (sp / 2 if int(y / sp) % 2 else 0)
            while x < x1:
                px, py = x + g.uniform(-sp * .18, sp * .18), y + g.uniform(-sp * .18, sp * .18)
                if inpoly(px, py, P) and in_view(px, py, 0, 25):
                    if kind == "olive": tree("olive", px, py)
                    elif kind == "school": tree(g.choice(("plane", "plane", "cypress", "stonepine")), px, py)
                    elif kind == "sacred" and g.random() < .5 and clear_of(px, py, country.KEEP_CLEAR): tree(g.choice(("cypress", "cypress", "stonepine", "olive")), px, py)
                    elif kind == "tombs" and g.random() < .4: tree("cypress", px, py)
                x += sp
            y += sp * .9
    # --- the vineyards: head-trained vines in rows on turned red soil, a dry-stone terrace wall now and then
    for P, ang in country.VINEYARDS:
        x0, y0, x1, y1 = core.bbox(P); land.field(P, "plough", ang, 2.0)
        for K in country.KEEP_CLEAR:
            for k in ("plough",): land.paint(k, K, how="clear", feather=2.0)
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; ext = math.hypot(x1 - x0, y1 - y0) / 2
        v = -ext; row = 0
        while v < ext:
            u = -ext
            while u < ext:
                px, py = cx + c * u - s * v + g.uniform(-.15, .15), cy + s * u + c * v + g.uniform(-.15, .15)
                if x0 < px < x1 and y0 < py < y1 and in_view(px, py, 0, 10) and land.free(px, py) and land.road_dist(px, py) > 2.6 and clear_of(px, py, country.KEEP_CLEAR) and g.random() < .93:
                    Scatter.add(g.choice(VINE), px, py, zt(px, py), g.uniform(0, 6.283), g.uniform(.85, 1.25))
                u += 1.5
            if row % 7 == 6: country.drystone([(max(x0, min(x1, cx + c * t - s * (v + 1.1))), max(y0, min(y1, cy + s * t + c * (v + 1.1)))) for t in (-ext, ext)], h=.7)
            v += 2.2; row += 1
        land.take(P)
    if core.SIEGE:
        # --- the besiegers' country: pine and oak woods, felled for a bowshot round the lines (the palisades and engines came from there)
        from . import siege
        far = [core.grow(P, 15) for P in siege.CLEAR]; STUMP = collection_of(siege.STUMP, "stump")
        for _ in range(16000):
            x, y = g.uniform(-240, 240), g.uniform(-240, 240)
            if not in_view(x, y, 0, 24) or any(inpoly(x, y, P) for P in siege.CLEAR) or not land.free(x, y, 1.0): continue
            dense = float(fbm(x, y, 85, 3, seed=61))
            if any(inpoly(x, y, P) for P in far):
                if dense > -.3 and g.random() < .7: Scatter.add(STUMP, x, y, zt(x, y), g.uniform(0, 6.3), g.uniform(.7, 1.3)); land.take_disc(x, y, .6)
            elif dense > -.25 and all(math.hypot(x - a, y - b) > 3.0 for a, b in planted[-40:]): tree(g.choice(("aleppo", "aleppo", "aleppo", "stonepine", "plane", "cypress")), x, y, sc=g.uniform(.75, 1.2))
    # --- olives scattered over the open country in old, loose groves; a line of cypresses or pines here and there
    for _ in range(0 if core.SIEGE else 7000):
        x, y = g.uniform(-235, 235), g.uniform(-235, 235)
        if not in_view(x, y, 0, 20) or float(fbm(x, y, 70, 3, seed=61)) < -.02: continue
        if land.HILL and inpoly(x, y, land.FOOT): continue
        px, py = round(x / 9.5) * 9.5 + g.uniform(-1.6, 1.6), round(y / 8.5) * 8.5 + g.uniform(-1.4, 1.4)
        if clear_of(px, py, country.KEEP_CLEAR) and all(math.hypot(px - a, py - b) > 5.5 for a, b in planted[-60:]): tree("olive", px, py)
    for w, kind, pts in land.ROADS:
        if kind != "road" or core.SIEGE: continue
        for x, y, ux, uy, d in core.along(pts, 13.0):
            if g.random() < .72: continue
            s = g.choice((-1, 1)); px, py = x - uy * (w / 2 + 3.2) * s, y + ux * (w / 2 + 3.2) * s
            if in_view(px, py, 0, 15) and clear_of(px, py, country.KEEP_CLEAR): tree(g.choice(("cypress", "cypress", "stonepine")), px, py)
    # --- inside the walls: figs and olives in the odd corners the grid leaves over
    octa = [(x * .93, y * .93) for x, y in S["octagon"]]
    for _ in range(500):
        x, y = g.uniform(-74, 74), g.uniform(-74, 74)
        if inpoly(x, y, octa) and land.free(x, y, 2.6) and land.road_dist(x, y) > 2.5: tree(g.choice(("fig", "olive", "olive")), x, y, sc=g.uniform(.7, .95))
    if land.HILL:
        # --- the acropolis: crags of scanned rock in the steep band, boulders fallen below, pines and cypresses clinging to the slopes
        for _ in range(900):
            x, y = g.uniform(-110, 112), g.uniform(36, 200)
            if not in_view(x, y, 12, 14) or not land.free(x, y, 1.5): continue
            i, j = int((x + land.HALF) / land.STEP), int((y + land.HALF) / land.STEP); cr = land.CRAG[j, i]; u = land.U[j, i]
            if cr > .35 and g.random() < cr * .5 and land.road_dist(x, y) > 6:
                if g.random() < .3 and u > .45: place(FACE, x, y, zt(x, y), g, h=g.uniform(4, 8), sink=.3, tilt=(g.uniform(-.2, .2), g.uniform(-.2, .2))); land.take_disc(x, y, 3.2)
                else: place(ROCK + BOUL, x, y, zt(x, y), g, h=g.uniform(1.2, 3.4), sink=.3, tilt=(g.uniform(-.3, .3), g.uniform(-.3, .3))); land.take_disc(x, y, 1.6)
        for _ in range(700):
            x, y = g.uniform(-110, 112), g.uniform(36, 215)
            if not in_view(x, y, 10, 16): continue
            i, j = int((x + land.HALF) / land.STEP), int((y + land.HALF) / land.STEP); u = land.U[j, i]
            if .03 < u < .8 and land.G_S[j, i] < .5 and float(fbm(x, y, 40, 3, seed=71)) > -.05: tree(g.choice(("aleppo", "aleppo", "aleppo", "cypress", "stonepine")), x, y)
        for _ in range(26):                                                               # cypresses beside the broad stair
            y = g.uniform(44, 99); sx = g.choice((-1, 1)); x = sx * g.uniform(5.6, 8.4)
            if land.free(x, y, 1.0): tree("cypress", x, y, check=False)
    # --- the shore: rocks where the coast turns stony, a rubble skirt along the mole
    for _ in range(360):
        x = g.uniform(-235, 120); y = land.shore_y(x) + g.uniform(-5, 7)
        if not in_view(x, y, 0, 10): continue
        stony = float(fbm(x, 0, 60, 2, seed=81)) + (.5 if x < -70 else -.25 if -64 < x < 46 else .1)
        if stony > .1 and g.random() < .8 and clear_of(x, y, country.KEEP_CLEAR): strew(ROCK + BOUL, x, y, min(zt(x, y), .6), g, h=g.uniform(.5, 2.0), sink=.35, tilt=.4)
    for M, off in country.ROCKS:
        for x, y, ux, uy, d in core.along(M, .9):
            for s in (-1, 1): strew(ROCK + BOUL, x - uy * s * (off - .6 + g.uniform(0, 1.4)), y + ux * s * (off - .6 + g.uniform(0, 1.4)), g.uniform(-.9, .1), g, h=g.uniform(.8, 1.6), sink=.2, tilt=.5)
    # --- the open ground: maquis in drifts (lentisk, kermes oak, broom, sage), straw-dry grass, stones; thicker on rocky slopes
    n_sh = 0
    for _ in range(int(core.opt("--scatter", 130000))):
        x, y = g.uniform(-240, 240), g.uniform(-240, 240)
        if not in_view(x, y, 0, 12) or not land.free(x, y): continue
        sd = land.sd_at(x, y)
        if sd < 9: continue
        i, j = int((x + land.HALF) / land.STEP), int((y + land.HALF) / land.STEP)
        cov = max(land.COV[k][2 * j, 2 * i] for k in ("stubble", "plough", "green", "earth", "pave"))
        if cov > (.62 if core.SIEGE else .25): continue
        dens = float(fbm(x, y, 55, 4, seed=91)) * 1.6 + .15 + (.2 if land.HILL and land.U[j, i] > .02 else 0) + (.25 if sd < 30 else 0)
        rd = land.road_dist(x, y); z = zt(x, y); k = g.random()
        if g.random() < max(.06, dens):
            if rd < 1.6: continue
            if k < .26: strew(LENT, x, y, z, g, scale=g.uniform(.5, 1.5)); land.paint_disc("lush", x, y, 1.2, .5, 1.5)
            elif k < .44: strew(KERM, x, y, z, g, scale=g.uniform(.5, 1.3))
            elif k < .62: strew(BROOM, x, y, z, g, scale=g.uniform(.5, 1.3))
            elif k < .78: strew(SAGE, x, y, z, g, scale=g.uniform(.6, 1.4))
            elif k < .93: strew(BURN, x, y, z, g, scale=g.uniform(.6, 1.5))
            else: strew(ROCK + BOUL, x, y, z, g, h=g.uniform(.3, 1.0), sink=.3, tilt=.4)
            n_sh += 1
        elif g.random() < .35: strew(TUFT, x, y, z, g, scale=g.uniform(.7, 1.4))
    print("PLANTED %d trees, %d shrubs and stones" % (len(planted), n_sh))
