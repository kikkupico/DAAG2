"""Shared state and tools for the polis build: arguments, the scene file, the camera, plan geometry helpers,
the mesh accumulator every builder writes faces into, reusable parts and their instances."""
import bpy, json, math, os, random, sys
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

WORLD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(WORLD, "assets")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def opt(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
def flag(k): return k in argv

S = json.load(open(opt("--scene", os.path.join(WORLD, "build3d", "city.json"))))
OUT = os.path.abspath(opt("--out", os.path.join(WORLD, "build3d", "polis.png")))
WIDTH, SAMPLES = int(opt("--width", 2400)), int(opt("--samples", 96))
ONLY = set(opt("--only", "").split(",")) - {""}
SKIP = set(opt("--skip", "").split(",")) - {""}
def stage(name): return (not ONLY or name in ONLY) and name not in SKIP
SIEGE, NIGHT = S["siege"], S["night"]
R2 = math.sqrt(2)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
ROOT = scene.collection

# ---------------------------------------------------------------- plan helpers
def inpoly(x, y, P):
    c = False
    for (ax, ay), (bx, by) in zip(P, P[1:] + P[:1]):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay): c = not c
    return c
def area(pts): return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1])) / 2
def centre(pts): return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
def ccw(pts): return list(pts) if area(pts) > 0 else list(pts)[::-1]
def rect(cx, cy, w, d, rot=0.0):
    """A w x d rectangle centred on (cx, cy), turned rot degrees; counter-clockwise from its south-west corner."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
def box(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
def bbox(pts): return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)
def grow(pts, d):
    """A convex polygon pushed out by d (in, if negative) along its edge normals."""
    P = ccw(pts); n = len(P); out = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        def nrm(p, q):
            dx, dy = q[0] - p[0], q[1] - p[1]; l = math.hypot(dx, dy) or 1; return dy / l, -dx / l
        n1, n2 = nrm(a, b), nrm(b, c); k = 1 + n1[0] * n2[0] + n1[1] * n2[1]
        out.append((b[0] + (n1[0] + n2[0]) * d / k, b[1] + (n1[1] + n2[1]) * d / k))
    return out
def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)
def chaikin(P, n=2, closed=True):
    for _ in range(n):
        Q = []
        for a, b in zip(P, (P[1:] + P[:1]) if closed else P[1:]):
            Q += [(.75 * a[0] + .25 * b[0], .75 * a[1] + .25 * b[1]), (.25 * a[0] + .75 * b[0], .25 * a[1] + .75 * b[1])]
        P = Q if closed else [P[0]] + Q + [P[-1]]
    return P
def along(pts, step):
    """Points every `step` metres along a polyline, with the direction there: (x, y, ux, uy, distance)."""
    out = []; carry = 0.0; run = 0.0
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-9: continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; t = carry
        while t < L: out.append((a[0] + ux * t, a[1] + uy * t, ux, uy, run + t)); t += step
        carry = t - L; run += L
    return out
def lerp(a, b, t): return a + (b - a) * t
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def hexrgb(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
def lin(h):
    """A #rrggbb colour as linear RGB."""
    return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in hexrgb(h))

# ---------------------------------------------------------------- the camera: the drawn picture's own projection
F = S["frame"]; ELEV = F["elev"]; AW, AH = F["aw"], F["ah"]
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); ROOT.objects.link(cam); scene.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = F["width_m"]; cam.data.sensor_fit = "HORIZONTAL"; cam.data.clip_start = 100; cam.data.clip_end = 6000
TOWARD = Vector((math.cos(ELEV) / R2, -math.cos(ELEV) / R2, math.sin(ELEV)))            # from the world to the camera
cam.location = TOWARD * 2500; cam.rotation_euler = (-TOWARD).to_track_quat("-Z", "Y").to_euler()
scene.render.resolution_x = WIDTH; scene.render.resolution_y = round(WIDTH * AH / AW); scene.render.resolution_percentage = 100
bpy.context.view_layer.update()
def project(x, y, z=0.0):
    """Where a world point lands in the picture, in the drawing's 1600 x 1200 pixels."""
    c = world_to_camera_view(scene, cam, Vector((x, y, z))); return c.x * AW, (1 - c.y) * AH
HALF_VIEW = F["width_m"] / 2 * R2                                                       # the ground the picture shows: |x + y| and |x - y| below this
def in_view(x, y, z=0.0, pad=0.0):
    return abs(x + y) < HALF_VIEW + pad and abs(x - y - 1.25 * z) < HALF_VIEW + pad

# ---------------------------------------------------------------- geometry: faces gathered per material
class Geo:
    """Faces gathered per material key. Each face carries its corners' UVs and two numbers the materials read:
    va (a random value for the thing the face belongs to: a house, a tile course) and vb (a material-specific amount)."""
    def __init__(s): s.B = {}
    def bucket(s, key):
        b = s.B.get(key)
        if b is None: b = s.B[key] = dict(v=[], li=[], lt=[], uv=[], va=[], vb=[], sm=[], n=0)
        return b
    def face(s, key, pts, uv=None, va=0.0, vb=0.0, smooth=False):
        b = s.bucket(key); n = len(pts); i = b["n"]
        b["v"].extend(pts); b["li"].extend(range(i, i + n)); b["lt"].append(n); b["n"] = i + n
        b["uv"].extend(uv if uv is not None else [(p[0], p[1]) for p in pts])
        b["va"].append(va); b["vb"].append(vb); b["sm"].append(smooth)
    def mesh(s, key, verts, faces, uvs=None, va=0.0, vb=0.0, smooth=True):
        """Faces that share vertices (so they can shade smoothly)."""
        b = s.bucket(key); o = b["n"]; b["v"].extend(verts); b["n"] += len(verts)
        for f in faces:
            b["li"].extend(i + o for i in f); b["lt"].append(len(f))
            b["uv"].extend((uvs[i] for i in f) if uvs is not None else ((verts[i][0], verts[i][1]) for i in f))
            b["va"].append(va); b["vb"].append(vb); b["sm"].append(smooth)

MATERIAL = [None]                                                                        # set by mats.py: key -> bpy material
def to_mesh(name, items):
    """One mesh from (key, bucket) pairs, a material slot for each key."""
    items = [(k, b) for k, b in items if b["lt"]]
    me = bpy.data.meshes.new(name)
    if not items: return me
    V = np.concatenate([np.asarray(b["v"], np.float32).reshape(-1, 3) for _, b in items])
    off = np.cumsum([0] + [b["n"] for _, b in items])
    LI = np.concatenate([np.asarray(b["li"], np.int32) + off[k] for k, (_, b) in enumerate(items)])
    LT = np.concatenate([np.asarray(b["lt"], np.int32) for _, b in items])
    UV = np.concatenate([np.asarray(b["uv"], np.float32).reshape(-1, 2) for _, b in items])
    MI = np.concatenate([np.full(len(b["lt"]), k, np.int32) for k, (_, b) in enumerate(items)])
    VA = np.concatenate([np.asarray(b["va"], np.float32) for _, b in items]); VB = np.concatenate([np.asarray(b["vb"], np.float32) for _, b in items])
    SM = np.concatenate([np.asarray(b["sm"], bool) for _, b in items])
    me.vertices.add(len(V)); me.vertices.foreach_set("co", V.ravel())
    me.loops.add(len(LI)); me.loops.foreach_set("vertex_index", LI)
    me.polygons.add(len(LT)); me.polygons.foreach_set("loop_start", (np.cumsum(LT) - LT).astype(np.int32))
    me.update(calc_edges=True)
    for k, _ in items: me.materials.append(MATERIAL[0](k))
    me.polygons.foreach_set("material_index", MI); me.polygons.foreach_set("use_smooth", SM)
    me.uv_layers.new(name="UVMap").data.foreach_set("uv", UV.ravel())
    me.attributes.new("va", "FLOAT", "FACE").data.foreach_set("value", VA)
    me.attributes.new("vb", "FLOAT", "FACE").data.foreach_set("value", VB)
    return me

STACK = [Geo()]
XF = []                                                                                  # placements in force: (cos, sin, x, y, z)
class placed:
    """Build in local coordinates: everything made inside is turned `rot` degrees about the origin and moved to (x, y, z)."""
    def __init__(s, x, y, rot=0.0, z=0.0): s.t = (math.cos(math.radians(rot)), math.sin(math.radians(rot)), x, y, z, math.radians(rot))
    def __enter__(s): XF.append(s.t); return s
    def __exit__(s, *a): XF.pop()
def to_world(x, y, z=0.0):
    for c, sn, tx, ty, tz, _ in reversed(XF): x, y, z = c * x - sn * y + tx, sn * x + c * y + ty, z + tz
    return x, y, z
def face(key, pts, uv=None, va=0.0, vb=0.0, smooth=False):
    if XF:
        if uv is None: uv = [(p[0], p[1]) for p in pts]
        pts = [to_world(*p) for p in pts]
    STACK[-1].face(key, pts, uv, va, vb, smooth)
def mesh(key, verts, faces, uvs=None, va=0.0, vb=0.0, smooth=True):
    if XF:
        if uvs is None: uvs = [(p[0], p[1]) for p in verts]
        verts = [to_world(*p) for p in verts]
    STACK[-1].mesh(key, verts, faces, uvs, va, vb, smooth)
def flush():
    """Everything gathered so far, as one object per material."""
    for key, b in STACK[0].B.items():
        if b["lt"]: ROOT.objects.link(bpy.data.objects.new(key, to_mesh(key, [(key, b)])))
    STACK[0] = Geo()

class Part:
    """A reusable mesh: `with Part("amphora") as p: ...faces...`; afterwards p.mesh is instanced with inst()."""
    def __init__(s, name): s.name = name
    def __enter__(s): s.g = Geo(); STACK.append(s.g); s.xf = XF[:]; XF.clear(); return s
    def __exit__(s, *a): STACK.pop(); XF.extend(s.xf); s.mesh = to_mesh(s.name, list(s.g.B.items())); s.coll = None
def inst(me, x, y, z, rot=0.0, sc=1.0, tilt=None):
    """An object sharing a part's mesh."""
    if XF and len(STACK) == 1:
        x, y, z = to_world(x, y, z); rot += sum(t[5] for t in XF)
    o = bpy.data.objects.new(me.name, me); ROOT.objects.link(o); o.location = (x, y, z)
    o.rotation_euler = (tilt[0], tilt[1], rot) if tilt else (0, 0, rot)
    o.scale = sc if isinstance(sc, tuple) else (sc,) * 3; return o

# ---------------------------------------------------------------- primitives (all write into the current Geo)
def vnorm(pts):
    n = Vector((0, 0, 0))
    for p, q in zip(pts, pts[1:] + pts[:1]): n += Vector(p).cross(Vector(q))
    return n
def oriented(key, pts, want, **kw):
    """A face whose normal points the way wanted."""
    if vnorm(pts).dot(Vector(want)) < 0: pts = pts[::-1]
    face(key, pts, **kw)
def wall(key, p, q, z0, z1, u0=0.0, zb=None, **kw):
    """A vertical face from plan point p to q; it faces right of that direction. UV: metres along, metres above zb."""
    L = math.hypot(q[0] - p[0], q[1] - p[1])
    z0p, z0q = (z0 if isinstance(z0, tuple) else (z0, z0)); z1p, z1q = (z1 if isinstance(z1, tuple) else (z1, z1)); zb = min(z0p, z0q) if zb is None else zb
    face(key, [(p[0], p[1], z0p), (q[0], q[1], z0q), (q[0], q[1], z1q), (p[0], p[1], z1p)],
         [(u0, z0p - zb), (u0 + L, z0q - zb), (u0 + L, z1q - zb), (u0, z1p - zb)], **kw)
def walls(key, pts, z0, z1, inward=False, zb=None, **kw):
    """The vertical faces round a plan polygon, facing out (or in)."""
    pts = ccw(pts)
    if inward: pts = pts[::-1]
    u = 0.0
    for p, q in zip(pts, pts[1:] + pts[:1]):
        wall(key, p, q, z0, z1, u, zb, **kw); u += math.hypot(q[0] - p[0], q[1] - p[1])
def cap(key, pts, z, down=False, **kw):
    pts = ccw(pts)
    if down: pts = pts[::-1]
    face(key, [(x, y, z) for x, y in pts], **kw)
def prism(side, top, pts, z0, z1, zb=None, **kw):
    walls(side, pts, z0, z1, zb=zb, **kw)
    if top: cap(top, pts, z1, **kw)
def slab(key, x0, y0, x1, y1, z0, z1, top=None, **kw): prism(key, top or key, box(x0, y0, x1, y1), z0, z1, **kw)
def boxr(side, top, cx, cy, w, d, z0, z1, rot=0.0, **kw): prism(side, top, rect(cx, cy, w, d, rot), z0, z1, **kw)
def ring(cx, cy, r, z, n, a0=0.0): return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cy + r * math.sin(a0 + 2 * math.pi * i / n), z) for i in range(n)]
def lathe(key, cx, cy, prof, n=12, smooth=True, cap_top=True, cap_bot=False, **kw):
    """A turned shape from (radius, z) pairs, bottom to top."""
    V = []; Fc = []; UVs = []
    for k, (r, z) in enumerate(prof):
        V += ring(cx, cy, r, z, n); UVs += [(i / n * 2 * math.pi * max(r, .01), z) for i in range(n)]
    for k in range(len(prof) - 1):
        for i in range(n):
            j = (i + 1) % n; Fc.append((k * n + i, k * n + j, (k + 1) * n + j, (k + 1) * n + i))
    mesh(key, V, Fc, UVs, smooth=smooth, **kw)
    if cap_top and prof[-1][0] > 1e-3: face(key, ring(cx, cy, prof[-1][0], prof[-1][1], n), **kw)
    if cap_bot and prof[0][0] > 1e-3: face(key, ring(cx, cy, prof[0][0], prof[0][1], n)[::-1], **kw)
def cyl(key, cx, cy, r, z0, z1, n=10, r1=None, top=True, smooth=True, **kw):
    lathe(key, cx, cy, [(r, z0), (r if r1 is None else r1, z1)], n, smooth, cap_top=top, **kw)
def beam(key, p, q, r=.1, n=6, smooth=True, **kw):
    """A round timber from one 3-D point to another."""
    p, q = Vector(p), Vector(q); ax = (q - p).normalized(); u = ax.orthogonal().normalized(); v = ax.cross(u)
    rg = lambda c: [tuple(c + (u * math.cos(2 * math.pi * i / n) + v * math.sin(2 * math.pi * i / n)) * r) for i in range(n)]
    V = rg(p) + rg(q); mesh(key, V, [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], smooth=smooth, **kw)
    face(key, V[n:], **kw); face(key, V[:n][::-1], **kw)
def bar(key, p, q, w=.12, h=.12, **kw):
    """A squared timber or stone bar from one 3-D point to another (w across, h deep)."""
    p, q = Vector(p), Vector(q); ax = (q - p).normalized()
    side = ax.cross(Vector((0, 0, 1)))
    side = Vector((1, 0, 0)) if side.length < 1e-6 else side.normalized()
    up = side.cross(ax).normalized(); a, b = side * w / 2, up * h / 2
    c = [p - a - b, p + a - b, p + a + b, p - a + b]; d = [q - a - b, q + a - b, q + a + b, q - a + b]
    for i in range(4):
        j = (i + 1) % 4; face(key, [tuple(c[i]), tuple(c[j]), tuple(d[j]), tuple(d[i])], **kw)
    face(key, [tuple(v) for v in c][::-1], **kw); face(key, [tuple(v) for v in d], **kw)

# ---------------------------------------------------------------- scattering: thousands of instances as one object
class Scatter:
    """Points that each carry an instance of one collection (through a geometry-nodes modifier): shrubs, stones, tufts."""
    ALL = {}
    def __init__(s, coll): s.coll = coll; s.pts = []
    @classmethod
    def add(cls, coll, x, y, z, rot=0.0, sc=1.0, tilt=(0.0, 0.0)):
        s = cls.ALL.get(coll.name)
        if s is None: s = cls.ALL[coll.name] = cls(coll)
        s.pts.append((x, y, z, tilt[0], tilt[1], rot, sc))
    @classmethod
    def flush(cls):
        for name, s in cls.ALL.items():
            if not s.pts: continue
            A = np.asarray(s.pts, np.float32); me = bpy.data.meshes.new("scatter." + name)
            me.vertices.add(len(A)); me.vertices.foreach_set("co", A[:, :3].ravel())
            me.attributes.new("rot", "FLOAT_VECTOR", "POINT").data.foreach_set("vector", A[:, 3:6].ravel())
            me.attributes.new("sc", "FLOAT", "POINT").data.foreach_set("value", A[:, 6].copy())
            ob = bpy.data.objects.new("scatter." + name, me); ROOT.objects.link(ob)
            ng = bpy.data.node_groups.new("scatter." + name, "GeometryNodeTree")
            ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
            ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
            N, L = ng.nodes.new, ng.links.new
            gi, go = N("NodeGroupInput"), N("NodeGroupOutput"); ci = N("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = s.coll
            ci.transform_space = "RELATIVE"
            ar = N("GeometryNodeInputNamedAttribute"); ar.data_type = "FLOAT_VECTOR"; ar.inputs["Name"].default_value = "rot"
            asc = N("GeometryNodeInputNamedAttribute"); asc.data_type = "FLOAT"; asc.inputs["Name"].default_value = "sc"
            er = N("FunctionNodeEulerToRotation"); ip = N("GeometryNodeInstanceOnPoints")
            L(gi.outputs[0], ip.inputs["Points"]); L(ci.outputs[0], ip.inputs["Instance"]); L(ar.outputs[0], er.inputs[0]); L(er.outputs[0], ip.inputs["Rotation"])
            L(asc.outputs[0], ip.inputs["Scale"]); L(ip.outputs[0], go.inputs[0])
            ob.modifiers.new("scatter", "NODES").node_group = ng
        cls.ALL = {}
def collection_of(me_or_objs, name):
    """A collection (not in the scene) holding a mesh, for scattering."""
    c = bpy.data.collections.new(name)
    if isinstance(me_or_objs, bpy.types.Mesh): c.objects.link(bpy.data.objects.new(name, me_or_objs))
    else:
        for o in me_or_objs: c.objects.link(o)
    return c
