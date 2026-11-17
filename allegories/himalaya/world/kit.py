"""The kit both Himalayan worlds are built from: the land (a height grid the paths are cut into, and the maps its material
reads), Tibetan building, what grows and lies about, the light, and the render.

It stands on the Greek town's own tools (world/polis: the mesh gatherer, the shader vocabulary, the materials made from Poly
Haven textures in world/assets, fetched by world/fetch_assets.py) and on tools/blender_stage.py for the road check. A world
script sets HIM_STAGE ("city" or "siege") and HIM_NIGHT before importing this.

Options after `--`:  --draft (1000 px, few samples, into work/)  --width N  --samples N  --no-render  --guides (path ribbons)"""
import json, math, os, random, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ALLEGORY = os.path.dirname(HERE); REPO = os.path.dirname(os.path.dirname(ALLEGORY))
STAGE = os.environ.get("HIM_STAGE", "city"); NIGHT = os.environ.get("HIM_NIGHT") == "1"
_a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
DRAFT = "--draft" in _a; GUIDES = "--guides" in _a
ELEV = float(os.environ.get("HIM_ELEV", math.degrees(math.asin(.75))))      # the camera's height above the horizon, in degrees: lower shows more of the walls and the mountains
R2 = math.sqrt(2); SPAN = 215 * R2; K = 1600 / SPAN; SIN, COS = math.sin(math.radians(ELEV)), math.cos(math.radians(ELEV))
_scene = os.path.join(tempfile.gettempdir(), "himalaya-%s-scene.json" % STAGE)
json.dump(dict(frame=dict(aw=1600, ah=1200, k=K, elev=math.radians(ELEV), width_m=SPAN), siege=STAGE == "siege", night=NIGHT), open(_scene, "w"))
OUT = os.path.join(ALLEGORY, "work", STAGE + "-draft.png") if DRAFT else os.path.join(ALLEGORY, STAGE + ".png")
os.makedirs(os.path.join(ALLEGORY, "work"), exist_ok=True)
def _has(k): return k in _a
sys.argv = sys.argv[:sys.argv.index("--")] if "--" in sys.argv else sys.argv
sys.argv += ["--", "--scene", _scene, "--out", OUT] + (["--glow", "16", "--lamp", "3.2"] if NIGHT else []) + ([] if _has("--width") else ["--width", "1000" if DRAFT else "2400"]) + ([] if _has("--samples") else ["--samples", "20" if DRAFT else "110"]) + _a
sys.path.insert(0, os.path.join(REPO, "world")); sys.path.insert(0, os.path.join(REPO, "tools"))
import bpy
from mathutils import Vector
from polis import core, mats
from polis.core import (ROOT, ASSETS, scene, Part, Scatter, collection_of, face, mesh, prism, cap, walls, wall, boxr, lathe, cyl, beam, bar, rect, grow, ccw, inst,
                        placed, lin, along, chaikin, smooth, lerp, opt, flag, TOWARD, project)
from polis.sh import Sh, image
import blender_stage
blender_stage.set_elev(ELEV)

U = 1.4        # how much larger than life everything built is drawn, so it reads in a picture 900 px wide
def _to_world(x, y, z=0.0):
    for t in reversed(core.XF):
        zs = t[6] if len(t) > 6 else 1.0; x, y, z = t[0] * x - t[1] * y + t[2], t[1] * x + t[0] * y + t[3], z * zs + t[4]
    return x, y, z
core.to_world = _to_world
class placed_s:
    """Like polis.core.placed, and scaled: what is built inside is in its own metres, turned, enlarged U times and set down at (x, y, z)."""
    def __init__(s, x, y, rot=0.0, z=0.0, sc=None):
        sc = U if sc is None else sc; r = math.radians(rot); s.t = (math.cos(r) * sc, math.sin(r) * sc, x, y, z, r, sc)
    def __enter__(s): core.XF.append(s.t); return s
    def __exit__(s, *a): core.XF.pop()
def loc(x, y, rot, lx, ly, sc=None):
    sc = U if sc is None else sc; c, sn = math.cos(math.radians(rot)) * sc, math.sin(math.radians(rot)) * sc; return (x + lx * c - ly * sn, y + lx * sn + ly * c)

def m2px(x, y, z=0.0): return (800 + K * (x + y) / R2, 600 - K * (SIN * (y - x) / R2 + COS * z))
def px2m(u, v):
    a, b = (u - 800) * R2 / K, (600 - v) * R2 / (K * SIN); return ((a - b) / 2, (a + b) / 2)

# ---------------------------------------------------------------- noise
def _hash(i, j, seed): return np.modf(np.sin(i * 127.1 + j * 311.7 + seed * 74.7) * 43758.5453)[0] % 1.0
def vnoise(x, y, seed=0):
    xi, yi = np.floor(x), np.floor(y); fx, fy = x - xi, y - yi; fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b, c, d = _hash(xi, yi, seed), _hash(xi + 1, yi, seed), _hash(xi, yi + 1, seed), _hash(xi + 1, yi + 1, seed)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy
def fbm(x, y, scale, octaves=4, seed=0, gain=.5, lac=2.03):
    """Smooth noise about zero, roughly within -0.5 .. 0.5; `scale` is the size of its largest features in metres."""
    v = 0.0; a = .5; f = 1.0 / scale
    for o in range(octaves): v = v + a * (vnoise(x * f, y * f, seed + o * 17) - .5); a *= gain; f *= lac
    return v
def sstep(a, b, t):
    t = np.clip((t - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

# ---------------------------------------------------------------- the land: a grid of heights
HALF, STEP = 400.0, .8; N = int(2 * HALF / STEP) + 1
_ax = np.linspace(-HALF, HALF, N, dtype=np.float32); X, Y = np.meshgrid(_ax, _ax)
class L:      # the land's state
    Z = np.zeros((N, N), np.float32); PD = np.full((N, N), 99.0, np.float32); PS = np.zeros((0, 3), np.float32)
    COV = {}; BUILT = []; SPANS = []        # cover maps by name; what stands where: (x, y, radius, height); where a path crosses in the air
for _k in ("field", "snow", "rock", "lush", "plot", "pave", "bare", "scree"): L.COV[_k] = np.zeros((N, N), np.float32)

def _ij(x, y): return (x + HALF) / STEP, (y + HALF) / STEP
def bil(A, x, y):
    fi, fj = _ij(x, y); i = int(min(N - 2, max(0, math.floor(fi)))); j = int(min(N - 2, max(0, math.floor(fj)))); a, b = min(1, max(0, fi - i)), min(1, max(0, fj - j))
    return float((A[j, i] * (1 - a) + A[j, i + 1] * a) * (1 - b) + (A[j + 1, i] * (1 - a) + A[j + 1, i + 1] * a) * b)
def zt(x, y): return bil(L.Z, x, y)
def _win(x, y, r):
    fi, fj = _ij(x, y); k = int(r / STEP) + 2
    return slice(max(0, int(fj) - k), min(N, int(fj) + k + 2)), slice(max(0, int(fi) - k), min(N, int(fi) + k + 2))
def ground_px(u, v):
    """The plan point of the land that the picture shows at pixel (u, v): the first ground the camera's ray meets, coming down
    from above (a lower camera can have higher ground standing in front of what a simple sum would find)."""
    hi = float(L.Z.max()) + 2; lo = float(L.Z.min()) - 2; z = hi; prev = None
    while z > lo:
        x, y = px2m(u, v + K * COS * z)
        if abs(x) < HALF - 2 and abs(y) < HALF - 2 and zt(x, y) >= z:
            if prev is None: return x, y
            za, zb = z, prev                                      # between the last clear height and this one, closer
            for _ in range(12):
                zm = (za + zb) / 2; xm, ym = px2m(u, v + K * COS * zm)
                if zt(xm, ym) >= zm: za = zm
                else: zb = zm
            return px2m(u, v + K * COS * za)
        prev = z; z -= .5
    return px2m(u, v)
def _rect_d(cx, cy, w, d, rot, xs, ys):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot)); lx = (xs - cx) * c + (ys - cy) * s; ly = -(xs - cx) * s + (ys - cy) * c
    return np.maximum(np.abs(lx) - w / 2, np.abs(ly) - d / 2)
def pad(cx, cy, w, d, rot=0.0, z=None, blend=3.0, how="mean"):
    """Levels the land under a rectangle (and eases it back over `blend` metres); returns the level."""
    sj, si = _win(cx, cy, math.hypot(w, d) / 2 + blend + 1); dd = _rect_d(cx, cy, w, d, rot, X[sj, si], Y[sj, si])
    if z is None:
        zs = [zt(*p) for p in rect(cx, cy, w, d, rot)] + [zt(cx, cy)]; z = max(zs) if how == "max" else sum(zs) / len(zs) if how == "mean" else min(zs)
    f = 1 - sstep(0.0, blend, dd); L.Z[sj, si] = L.Z[sj, si] * (1 - f) + z * f; return z
def paint(name, cx, cy, w, d, rot=0.0, v=1.0, feather=1.2):
    sj, si = _win(cx, cy, math.hypot(w, d) / 2 + feather + 1); dd = _rect_d(cx, cy, w, d, rot, X[sj, si], Y[sj, si])
    L.COV[name][sj, si] = np.maximum(L.COV[name][sj, si], v * (1 - sstep(0.0, feather, dd)))
def paint_disc(name, x, y, r, v=1.0, feather=1.5):
    sj, si = _win(x, y, r + feather + 1); dd = np.hypot(X[sj, si] - x, Y[sj, si] - y) - r
    L.COV[name][sj, si] = np.maximum(L.COV[name][sj, si], v * (1 - sstep(0.0, feather, dd)))

def carve(roads, hw=1.5, shoulder=3.4, ease=16, skip=None):
    """Cuts every path into the land as a level bench that climbs evenly, and returns the roads again as plan points
    [x, y, z] every few metres, at the heights a walker has there. Where `skip` (a grid like the land's) is over a half, the
    land is left alone and the path crosses in the air, level from bank to bank: those spans are kept in L.SPANS, for bridges."""
    PZ = np.zeros((N, N), np.float32); R = hw + shoulder; lines = []; L.SPANS = []
    for r in roads:
        pts = [(p[0], p[1]) for p in r["pts"]]; S_ = [(x, y) for x, y, *_ in along(pts, 1.0)] + [pts[-1]]
        zs = np.array([zt(x, y) for x, y in S_]); sk = np.array([skip is not None and bil(skip, x, y) > .5 for x, y in S_])
        if sk.any() and not sk.all(): idx = np.arange(len(zs)); zs[sk] = np.interp(idx[sk], idx[~sk], zs[~sk])
        k = min(ease, max(1, len(zs) // 2)); zz = np.convolve(np.pad(zs, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
        lines.append((r, S_, zz, sk)); run = []
        for i, ((x, y), z) in enumerate(zip(S_, zz)):
            if sk[i]: run.append((x, y, float(z))); continue
            if run: L.SPANS.append([(S_[i - len(run) - 1][0], S_[i - len(run) - 1][1], float(zz[i - len(run) - 1]))] + run + [(x, y, float(z))]); run = []
            sj, si = _win(x, y, R); d = np.hypot(X[sj, si] - x, Y[sj, si] - y); m = d < L.PD[sj, si]
            L.PD[sj, si] = np.where(m, d, L.PD[sj, si]); PZ[sj, si] = np.where(m, z, PZ[sj, si])
    f = (1 - sstep(hw, R, L.PD)) * (1 if skip is None else (skip < .5)); L.Z[:] = L.Z * (1 - f) + PZ * f
    out = []; ps = []
    for r, S_, zz, sk in lines:
        keep = sorted(set(list(range(0, len(S_), 5)) + [len(S_) - 1] + [i for i in range(1, len(S_)) if sk[i] != sk[i - 1]] + [i - 1 for i in range(1, len(S_)) if sk[i] != sk[i - 1]]))
        hz = lambda i: float(zz[i]) if sk[i] else zt(*S_[i])
        out.append(dict(kind=r.get("kind", "road"), width=r.get("width", 3), pts=[[round(S_[i][0], 2), round(S_[i][1], 2), round(hz(i), 2)] for i in keep]))
        ps += [(S_[i][0], S_[i][1], hz(i)) for i in range(0, len(S_), 2)]
    ends = [tuple(r["pts"][i][:2]) for r in out for i in (0, -1)]          # where one path ends on another, both get that very point, so they join
    for r in out:
        for e in ends:
            P = r["pts"]
            if any(math.dist(e, q[:2]) < .02 for q in (P[0], P[-1])): continue
            best = None
            for i, (a, b) in enumerate(zip(P, P[1:])):
                dx, dy = b[0] - a[0], b[1] - a[1]; t = max(0, min(1, ((e[0] - a[0]) * dx + (e[1] - a[1]) * dy) / max(1e-9, dx * dx + dy * dy))); dd = math.hypot(e[0] - a[0] - t * dx, e[1] - a[1] - t * dy)
                if best is None or dd < best[0]: best = (dd, i)
            if best and best[0] < 1.6: P.insert(best[1] + 1, [e[0], e[1], round((P[best[1]][2] + P[best[1] + 1][2]) / 2, 2)])
    L.PS = np.array(ps, np.float32); return out
def trail(pts, hw=1.3, shoulder=2.6, ease=8, cover="bare", v=.85, skip=None):
    """A way that no courier walks (a stair up to a gate, a path to a door): the land is benched along it and its cover painted,
    and it is left out of the network. Returns its points [(x, y, z)] every metre. Lay these before the network is carved."""
    S_ = [(x, y) for x, y, *_ in along([(p[0], p[1]) for p in pts], 1.0)] + [tuple(pts[-1][:2])]
    zs = np.array([zt(x, y) for x, y in S_]); k_ = min(ease, max(1, len(zs) // 2)); zz = np.convolve(np.pad(zs, k_, mode="edge"), np.ones(2 * k_ + 1) / (2 * k_ + 1), mode="valid"); R = hw + shoulder
    for (x, y), z in zip(S_, zz):
        if skip is not None and bil(skip, x, y) > .5: continue
        sj, si = _win(x, y, R); d = np.hypot(X[sj, si] - x, Y[sj, si] - y); f = 1 - sstep(hw, R, d); L.Z[sj, si] = L.Z[sj, si] * (1 - f) + z * f
        if cover: L.COV[cover][sj, si] = np.maximum(L.COV[cover][sj, si], v * (1 - sstep(hw * .7, hw + .8, d)))
    return [(x, y, zt(x, y)) for x, y in S_]
def steps(tr, w=2.2, key="ashlar", every=1.0, min_rise=.12):
    """Stone treads across a trail wherever it climbs."""
    for a, b in zip(tr[::1], tr[1:]):
        if abs(b[2] - a[2]) < min_rise * math.dist(a[:2], b[:2]): continue
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])); boxr(key, key, a[0], a[1], .7, w, min(a[2], b[2]) - .6, max(a[2], b[2]) + .04, ang, va=.4)
def footpath(a, b, r=1.0, v=.8, cover="bare"):
    """Ground worn bare between two points, as between a door and the lane."""
    n = max(1, int(math.dist(a, b) / 1.2))
    for i in range(n + 1): paint_disc(cover, lerp(a[0], b[0], i / n), lerp(a[1], b[1], i / n), r, v, 1.0)

def path_dist(x, y): return bil(L.PD, x, y)
def hides(x, y, r, h):
    """Would something this wide and tall, standing here, come between the camera and a walker on a path?"""
    if not len(L.PS): return False
    z = zt(x, y); dx, dy = L.PS[:, 0] - x, L.PS[:, 1] - y
    t = np.clip((-dx + dy) / R2, 0, None)                       # how far behind the thing (to the north-west) each path point lies
    across = np.abs(dx + dy) / R2; top = z + h - L.PS[:, 2] - .9      # what stands above a walker's middle there
    return bool(np.any((across < r + .4) & (t > r * .3) & (t < top * (COS / SIN) + r)))
def free(x, y, r, gap=1.0):
    return all(math.hypot(x - bx, y - by) > r + br + gap for bx, by, br, _ in L.BUILT)
def claim(x, y, r, h=0.0): L.BUILT.append((x, y, r, h))

# ---------------------------------------------------------------- the land's materials
def _map_image(name, chans):
    img = bpy.data.images.new(name, N, N, alpha=False, float_buffer=True); img.colorspace_settings.name = "Non-Color"
    px = np.ones((N, N, 4), np.float32)
    for k, c in enumerate(chans): px[..., k] = c
    img.pixels.foreach_set(px.ravel()); return img
def _read(s, img):
    v = s.mapping(s.pos, 1 / (N * STEP), ((HALF + STEP / 2) / (N * STEP), (HALF + STEP / 2) / (N * STEP), 0))
    sep = s.node("ShaderNodeSeparateColor"); s.set(sep.inputs[0], s.img(img, v, ext="EXTEND")); return sep.outputs

def ground_material(winter=False):
    """Alpine ground: dry grass and scree, rock where it is steep, barley terraces in plots, trodden earth on the paths and round
    the houses, snow high up (or, in winter, over everything but the steepest rock and the trampled ways)."""
    s = Sh("ground"); C = L.COV
    wear = np.clip(1.25 - L.PD / 1.9, 0, 1) * (L.PD < 9)
    a = _read(s, _map_image("m1", (wear, C["field"], C["snow"]))); b = _read(s, _map_image("m2", (C["rock"], C["lush"], C["plot"]))); c = _read(s, _map_image("m3", (C["pave"], C["bare"], C["scree"])))
    wear, field, snow = a[0], a[1], a[2]; rock, lush, plot = b[0], b[1], b[2]; pave, bare, scree_m = c[0], c[1], c[2]
    n1 = s.noise(.035, 5, .6); n2 = s.noise(.45, 4, .65); n3 = s.noise(2.6, 3, .6)
    g1 = s.tint(s.tex2("withered_grass", 7.0), "withered_grass", lin("#8a8450")); g2 = s.tint(s.tex2("sparse_grass", 9.0), "sparse_grass", lin("#6f7a42"))
    grass = s.mix(s.rng(n1, .35, .65), g1, g2); grass = s.mix(s.mul(lush, .85), grass, s.tint(s.tex2("sparse_grass", 6.0), "sparse_grass", lin("#4f7a36")))
    scree = s.tint(s.tex2("rocky_terrain_02", 11.0), "rocky_terrain_02", lin("#8f887a"), raw=.25)
    col = s.mix(s.rng(s.add(n2, s.mul(n1, .6)), .78, .98), grass, scree)
    col = s.mix(s.rng(s.madd(s.sub(n2, .5), .8, scree_m), .35, .65), col, s.tint(s.tex2("rocks_ground_04", 9.0), "rocks_ground_04", lin("#8d8780"), raw=.3))
    # barley terraces: each plot its own stage of the crop
    crop = s.ramp(plot, [(0, lin("#75804a")), (.2, lin("#8f9156")), (.4, lin("#a8975c")), (.58, lin("#97835a")), (.74, lin("#7c6d54")), (.88, lin("#6b7446"))], "CONSTANT")
    rows = s.rng(s.noise(4.5, 2, .5, vec=s.mapping(s.pos, (1, .1, 1), rot=(0, 0, .6))), .3, .7, .9, 1.06)
    soil = s.tint(s.tex2("farm_soil", 5.0), "farm_soil", (1, 1, 1))
    crop = s.mix(1.0, crop, s.mix(.5, soil, (.5, .5, .5)), "OVERLAY"); crop = s.mix(1.0, crop, rows, "MULTIPLY", clamp=False)
    col = s.mix(s.rng(s.madd(s.sub(n2, .5), .5, field), .42, .58), col, crop)
    # rock
    strata = s.noise(2.2, 4, .7, vec=s.mapping(s.pos, (.25, .25, 2.6), rot=(.35, .2, 0)))
    rk = s.mix(s.rng(n1, .4, .6), s.tint(s.tex2("aerial_rocks_02", 30.0), "aerial_rocks_02", lin("#8a8278"), raw=.3), s.tint(s.tex2("rock_08", 7.0), "rock_08", lin("#766e66"), raw=.3))
    rk = s.mix(s.rng(strata, .35, .7, 0, .5), rk, s.mix(1.0, rk, (.58, .55, .54), "MULTIPLY")); rk = s.mix(s.rng(n2, .55, .8, 0, .3), rk, lin("#a39584"))
    col = s.mix(s.rng(s.madd(s.sub(n2, .5), .7, rock), .38, .62), col, rk)
    # bare trodden earth round the houses, the paths themselves, paving
    earth = s.tint(s.tex2("stony_dirt_path", 4.5), "stony_dirt_path", lin("#a08c70") if not winter else lin("#6f6860"), raw=.2)
    col = s.mix(s.mul(s.rng(s.madd(s.sub(n3, .5), .5, bare), .3, .7), .9), col, earth)
    col = s.mix(s.rng(s.madd(s.sub(n3, .5), .7, wear), .34, .62), col, s.mix(1.0, earth, (1.12, 1.08, 1.02) if not winter else (.8, .8, .84), "MULTIPLY", clamp=False))
    flag_ = s.tint(s.tex2("stone_tiles_02", 3.0), "stone_tiles_02", lin("#a39c8e"), raw=.3)
    col = s.mix(s.rng(pave, .4, .6), col, flag_)
    # snow
    sn = s.tint(s.tex2("snow_02", 8.0), "snow_02", (.86, .9, .96) if not winter else (.8, .86, .97))
    sf = s.madd(s.sub(s.add(n2, s.mul(n1, .8)), .9), .6, snow)
    sf = s.rng(sf, .42, .56); col = s.mix(sf, col, sn)
    if winter:      # snow trodden to grey slush on the ways and round the fires
        tr = s.maxf(s.rng(s.madd(s.sub(n3, .5), .5, wear), .25, .7), s.mul(s.rng(s.madd(s.sub(n3, .5), .6, bare), .3, .7), .75)); col = s.mix(s.mul(tr, .85), col, s.mix(s.rng(n3, .3, .7), lin("#6f6c6c"), lin("#8a8684")))
    h = s.add(s.mul(s.lum(col), .7), s.mul(n3, .3))
    rough = s.mixf(sf, .92, .55)
    return s.surface(s.bsdf(col, rough, s.bump(s.add(h, s.mul(s.mul(rock, strata), 1.5)), .7, .2)))

def water_material():
    """A glacier-fed river: milky turquoise, white where it breaks over rocks."""
    s = Sh("water"); n = s.noise(.35, 4, .7); n2 = s.noise(2.0, 3, .6); f = s.rng(s.add(n, s.mul(n2, .3)), .66, .84)
    col = s.mix(s.rng(n2, .3, .7), lin("#5a9c9c"), lin("#7fb9b4")); col = s.mix(f, col, (.93, .97, .97))
    return s.surface(s.bsdf(col, .35, s.bump(n2, .15, .03), Emission_Color=col, Emission_Strength=.06))

def finish_land(winter=False):
    """Marks rock where the land is steep and builds the mesh of the part the picture can show."""
    gy, gx = np.gradient(L.Z, STEP); slope = np.hypot(gx, gy)
    L.COV["rock"][:] = np.maximum(L.COV["rock"], np.clip((slope - .58) / .4, 0, 1) * (L.PD > 2.2))
    L.COV["snow"][:] = L.COV["snow"] * (1 - .8 * np.clip((slope - 1.0) / .6, 0, 1))        # snow does not lie on the steepest rock
    lim = SPAN / 2 * R2 + 60; keep = (np.abs(X + Y) < lim) & (np.abs(X - Y) < (lim + 120) * .75 / SIN + 60)
    idx = np.arange(N * N).reshape(N, N); q = keep[:-1, :-1] & keep[:-1, 1:] & keep[1:, 1:] & keep[1:, :-1]
    quads = np.stack([idx[:-1, :-1][q], idx[:-1, 1:][q], idx[1:, 1:][q], idx[1:, :-1][q]], 1)
    used = np.unique(quads); remap = np.full(N * N, -1, np.int64); remap[used] = np.arange(len(used)); quads = remap[quads]
    V = np.stack([X.ravel()[used], Y.ravel()[used], L.Z.ravel()[used]], 1).astype(np.float32)
    me = bpy.data.meshes.new("ground"); me.vertices.add(len(V)); me.vertices.foreach_set("co", V.ravel())
    me.loops.add(quads.size); me.loops.foreach_set("vertex_index", quads.ravel().astype(np.int32))
    me.polygons.add(len(quads)); me.polygons.foreach_set("loop_start", (np.arange(len(quads)) * 4).astype(np.int32))
    me.polygons.foreach_set("use_smooth", np.ones(len(quads), bool)); me.update(calc_edges=True)
    me.materials.append(ground_material(winter)); ROOT.objects.link(bpy.data.objects.new("ground", me))

# ---------------------------------------------------------------- Tibetan building
WHITE, CREAM, OCHRE, MAROON, BLACK = "#efe9da", "#e6dcc4", "#c98a3c", "#6a2420", "#1a1512"
FLAGS = ("#2f63b5", "#f1eee6", "#c2352b", "#3f8a4a", "#e2b53a")       # sky, cloud, fire, water, earth
def P3(p, z): return (p[0], p[1], z)
def battered(key, cx, cy, w, d, z0, z1, rot=0.0, batter=.05, top=None, va=0.0, vb=0.0):
    """Walls that lean in as they rise. Returns the plan of the top."""
    bt = batter * (z1 - z0); B = rect(cx, cy, w, d, rot); T = rect(cx, cy, w - 2 * bt, d - 2 * bt, rot); u = 0.0
    for i in range(4):
        j = (i + 1) % 4; Lg = math.dist(B[i], B[j])
        face(key, [P3(B[i], z0), P3(B[j], z0), P3(T[j], z1), P3(T[i], z1)], [(u, 0), (u + Lg, 0), (u + Lg, z1 - z0), (u, z1 - z0)], va=va, vb=vb); u += Lg
    if top: cap(top, T, z1, va=va)
    return T
def on_wall(cx, cy, w, d, rot, side, f, out=0.0):
    """A point on one side of a rectangle (0 south, 1 east, 2 north, 3 west), a fraction f along it, `out` metres proud; and the side's direction."""
    R_ = rect(cx, cy, w, d, rot); a, b = R_[side], R_[(side + 1) % 4]; ux, uy = (b[0] - a[0]), (b[1] - a[1]); Lg = math.hypot(ux, uy); ux, uy = ux / Lg, uy / Lg
    return (a[0] + ux * Lg * f + uy * out, a[1] + uy * Lg * f - ux * out), (ux, uy), Lg
def window(cx, cy, w, d, rot, side, f, z, ww=.9, hh=1.3, lit=False, trim=None, batter_in=0.0):
    """A Tibetan window: a black surround wider at the foot, the opening, and a painted lintel with its little pelmet."""
    (px, py), (ux, uy), _ = on_wall(cx, cy, w, d, rot, side, f, .05 - batter_in); nx, ny = uy, -ux
    def q(key, a0, a1, b0, b1, z0, z1, o):      # a quad from a0..a1 metres along at z0 to b0..b1 at z1, o metres proud
        face(key, [(px + ux * a0 + nx * o, py + uy * a0 + ny * o, z0), (px + ux * a1 + nx * o, py + uy * a1 + ny * o, z0), (px + ux * b1 + nx * o, py + uy * b1 + ny * o, z1), (px + ux * b0 + nx * o, py + uy * b0 + ny * o, z1)])
    q("paint:" + BLACK, -ww / 2 - .22, ww / 2 + .22, -ww / 2 - .1, ww / 2 + .1, z - .12, z + hh + .1, 0)
    q("glow" if lit else "dark", -ww / 2, ww / 2, -ww / 2, ww / 2, z, z + hh, .02)
    q("paint:" + (trim or "#8a2f24"), -ww / 2 - .2, ww / 2 + .2, -ww / 2 - .2, ww / 2 + .2, z + hh + .1, z + hh + .3, .1)
    q("paint:#efe9da", -ww / 2 - .16, ww / 2 + .16, -ww / 2 - .16, ww / 2 + .16, z + hh - .08, z + hh + .1, .07)
def door(cx, cy, w, d, rot, side, f, z, ww=1.2, hh=2.0, trim="#8a2f24", lit=False, out=.05):
    (px, py), (ux, uy), _ = on_wall(cx, cy, w, d, rot, side, f, out); nx, ny = uy, -ux
    def q(key, a0, a1, z0, z1, o): face(key, [(px + ux * a0 + nx * o, py + uy * a0 + ny * o, z0), (px + ux * a1 + nx * o, py + uy * a1 + ny * o, z0), (px + ux * a1 + nx * o, py + uy * a1 + ny * o, z1), (px + ux * a0 + nx * o, py + uy * a0 + ny * o, z1)])
    q("paint:" + BLACK, -ww / 2 - .25, ww / 2 + .25, z, z + hh + .15, 0); q("glow" if lit else "wood:#5a4030", -ww / 2, ww / 2, z, z + hh, .03); q("paint:" + trim, -ww / 2 - .3, ww / 2 + .3, z + hh + .15, z + hh + .4, .12)
    return (px + nx * 1.2, py + ny * 1.2)

def parapet(T, z, band=MAROON, bh=.55, lip=.14, roof="earth:#93846c", va=0.0, white_top=True):
    """The top of a wall: the dark band of packed twigs under a rim, and the flat roof inside it. T is the wall's top plan."""
    O = grow(T, lip); I = grow(T, -.32)
    walls("paint:" + band, O, z - bh, z + .12, va=va); walls("paint:#3a1512", grow(T, lip + .03), z - bh - .1, z - bh, va=va)
    for a, b, c, d in zip(O, O[1:] + O[:1], I[1:] + I[:1], I): face("wash:" + WHITE if white_top else "paint:" + band, [P3(a, z + .12), P3(b, z + .12), P3(c, z + .12), P3(d, z + .12)], va=va)
    walls("wash:" + CREAM, I, z - .25, z + .12, inward=True, va=va); cap("roof", I, z - .25, va=va)
    return I
def pole(x, y, z, h=4.2, cloth=True, g=random):
    """A prayer-flag pole: a tall staff with a narrow banner down its length."""
    beam("wood:#6b5846", (x, y, z), (x, y, z + h), .06, 5)
    if cloth:
        c = g.choice(FLAGS); a = g.uniform(0, 6.28); ux, uy = math.cos(a) * .5, math.sin(a) * .5
        face("paint:" + c, [(x, y, z + h * .35), (x + ux, y + uy, z + h * .35), (x + ux, y + uy, z + h * .98), (x, y, z + h * .98)])
def flag_line(p, q, n=None, sag=.08, size=.42):
    """A string of prayer flags from one point to another, in the five colours."""
    p, q = Vector(p), Vector(q); Lg = (q - p).length; n = n or max(4, int(Lg / .62)); d = (q - p) / Lg; side = Vector((d.x, d.y, 0)).normalized() if abs(d.z) < .98 else Vector((1, 0, 0))
    pts = [p + (q - p) * (i / n) - Vector((0, 0, sag * Lg * 4 * (i / n) * (1 - i / n))) for i in range(n + 1)]
    for i in range(n):
        a, b = pts[i], pts[i + 1]; m = a + (b - a) * .12; e = a + (b - a) * .88
        face("paint:" + FLAGS[i % 5], [tuple(m), tuple(e), (e.x, e.y, e.z - size), (m.x, m.y, m.z - size)])
    for a, b in zip(pts, pts[1:]): beam("paint:#d8d2c2", tuple(a), tuple(b), .012, 3)

def m_wash(key, par):
    """Whitewash over rammed earth and stone, renewed each year by pouring it from the roof: brilliant at the top, runs and
    grey streaks down the wall, the lifts of the rammed earth showing faintly, mud splashed up at the foot, a footing of
    field stone. UV: metres along the wall, metres above its foot (which is sunk 1.8 m in the ground)."""
    s = Sh(key); base = mats.col_of(par, WHITE); va = s.attr("va"); u, v, _ = s.xyz(s.uv)
    tx = s.tex2("white_rough_plaster", 3.2, box=True); col = s.tint(tx, "white_rough_plaster", base, raw=.1)
    tone = s.ramp(va, [(0, (.9, .88, .84)), (.4, (1, 1, 1)), (.75, (.97, .95, .9)), (1, (.86, .82, .76))]); col = s.mix(1.0, col, tone, "MULTIPLY", clamp=False)
    runs = s.noise(1.0, 4, .7, vec=s.mapping(s.pos, (3.4, 3.4, .1), loc=(0, 0, 0)))
    col = s.mix(s.mul(s.rng(runs, .5, .8), .38), col, s.mix(1.0, col, (.62, .6, .58), "MULTIPLY"))                       # grey runs of rain and old wash
    lifts = s.rng(s.math("FRACT", s.mul(v, 1.55)), .0, .1, .55, 1.0); col = s.mix(s.mul(s.sub(1.0, lifts), .22), col, s.mix(1.0, col, (.78, .74, .68), "MULTIPLY"))
    splash = s.rng(s.madd(s.sub(s.noise(1.8, 3, .6, w=2.0), .5), 1.2, v), 3.6, 2.0)
    col = s.mix(s.mul(splash, .55), col, s.mix(1.0, col, (.72, .62, .5), "MULTIPLY"))                                    # mud thrown up from the yard
    stone = s.tint(s.tex2("stacked_stone_wall", 2.2, box=True), "stacked_stone_wall", lin("#9c948a"), raw=.3)
    foot = s.rng(s.madd(s.sub(s.noise(1.4, 3, .6, w=5.0), .5), .7, v), 2.75, 2.45); col = s.mix(foot, col, stone)
    h = s.add(s.mul(s.lum(tx), .5), s.mul(foot, .4))
    return s.surface(s.bsdf(col, .9, s.bump(h, .4, .06)))
mats.MAKERS["wash"] = m_wash
def m_roof(key, par):
    """A flat roof of rammed clay over brushwood: grey-brown, cracked, swept paler where people walk."""
    s = Sh(key); base = mats.col_of(par, "#8b7d68"); va = s.attr("va")
    tx = s.tex2("dry_mud_field_001", 3.0); col = s.tint(tx, "dry_mud_field_001", base, raw=.25)
    col = s.mix(1.0, col, s.ramp(va, [(0, (.86, .84, .82)), (.5, (1, 1, 1)), (1, (1.1, 1.04, .96))]), "MULTIPLY", clamp=False)
    col = s.mix(s.rng(s.noise(.9, 3, .6, w=s.mul(va, 9.0)), .5, .8, 0, .35), col, s.mix(1.0, col, (1.18, 1.14, 1.06), "MULTIPLY", clamp=False))
    return s.surface(s.bsdf(col, .95, s.bump(s.lum(tx), .6, .05)))
mats.MAKERS["roof"] = m_roof

def bridge(span, w=2.6):
    """A timber footbridge from bank to bank: stone abutments, a deck of planks on long beams, posts and a handrail, and prayer
    flags strung along both sides."""
    P = [Vector(p) for p in span]; n = len(P)
    for i, (a, b) in enumerate(zip(P, P[1:])):
        d = (b - a); d.z = 0; d.normalize(); s_ = Vector((-d.y, d.x, 0)) * (w / 2)
        face("wood:#7a6248", [tuple(a - s_ + Vector((0, 0, .02))), tuple(a + s_ + Vector((0, 0, .02))), tuple(b + s_ + Vector((0, 0, .02))), tuple(b - s_ + Vector((0, 0, .02)))], va=i * .37 % 1)
        for sd in (-1, 1):
            bar("wood:#4d3d2e", tuple(a + s_ * sd - Vector((0, 0, .25))), tuple(b + s_ * sd - Vector((0, 0, .25))), .3, .45)
            bar("wood:#5a4636", tuple(a + s_ * sd + Vector((0, 0, 1.25))), tuple(b + s_ * sd + Vector((0, 0, 1.25))), .1, .1)
            if i % 3 == 0: bar("wood:#5a4636", tuple(a + s_ * sd), tuple(a + s_ * sd + Vector((0, 0, 1.3))), .12, .12)
    d = (P[-1] - P[0]); d.z = 0; d.normalize(); s_ = Vector((-d.y, d.x, 0)) * (w / 2)
    for e, sg in ((P[0], -1), (P[-1], 1)):
        ang = math.degrees(math.atan2(d.y, d.x)); c = e + d * sg * 1.2; boxr("rubble", "rubble", c.x, c.y, 3.2, w + 1.6, e.z - 7, e.z - .02, ang)
        for sd in (-1, 1):
            q = e + s_ * sd * 1.25; beam("wood:#5a4636", (q.x, q.y, e.z - .3), (q.x, q.y, e.z + 3.6), .1, 6)
    for sd in (-1, 1): flag_line(tuple(P[0] + s_ * sd * 1.25 + Vector((0, 0, 3.5))), tuple(P[-1] + s_ * sd * 1.25 + Vector((0, 0, 3.5))), sag=.05, size=.6)

def rabsel(w, d, side, f, z, ww=2.6, hh=1.5, lit=False, trim="#8a2f24"):
    """The timber bay of the best room: a dark frame standing out from the wall, small panes, a painted beam-end cornice over it."""
    (px, py), (ux, uy), _ = on_wall(0, 0, w, d, 0, side, f, .0); nx, ny = uy, -ux; o = .42
    def q(key, a0, a1, z0, z1, off): face(key, [(px + ux * a0 + nx * off, py + uy * a0 + ny * off, z0), (px + ux * a1 + nx * off, py + uy * a1 + ny * off, z0), (px + ux * a1 + nx * off, py + uy * a1 + ny * off, z1), (px + ux * a0 + nx * off, py + uy * a0 + ny * off, z1)])
    C = [(px + ux * a + nx * off, py + uy * a + ny * off) for a, off in ((-ww / 2, -.3), (ww / 2, -.3), (ww / 2, o), (-ww / 2, o))]
    prism("wood:#3a2a20", "wood:#3a2a20", C, z - .15, z + hh + .15)
    n = max(2, int(ww / .62))
    for i in range(n): q("glow" if lit else "dark", -ww / 2 + .12 + i * (ww - .24) / n + .05, -ww / 2 + .12 + (i + 1) * (ww - .24) / n - .05, z + .1, z + hh - .1, o + .02)
    q("paint:" + trim, -ww / 2 - .2, ww / 2 + .2, z + hh + .15, z + hh + .38, o + .12); q("paint:#efe9da", -ww / 2 - .15, ww / 2 + .15, z + hh + .02, z + hh + .15, o + .1)
    C2 = [(px + ux * a + nx * off, py + uy * a + ny * off) for a, off in ((-ww / 2 - .25, -.3), (ww / 2 + .25, -.3), (ww / 2 + .25, o + .22), (-ww / 2 - .25, o + .22))]
    prism("paint:#2a1c16", "roof", C2, z + hh + .38, z + hh + .52)

def _block(w, d, x0, y0, floors, g, wash, band, trim, lit, door_side, wood, flags, va, top_floor_bay=True):
    """One block of a house, in the house's own frame, its foot at (x0, y0)."""
    h = floors * 2.75 + .5; bt = .06
    with placed_s(x0, y0, 0, 0, 1.0):
        T = battered("wash:" + wash, 0, 0, w, d, -1.8, h, 0, bt, va=va)
        O = grow(T, .16); I = grow(T, -.34)                                           # the parapet: a black band, a white rim, the roof inside
        walls("paint:" + band, O, h - .5, h + .12, va=va)
        for a, b, c, e in zip(O, O[1:] + O[:1], I[1:] + I[:1], I): face("wash:" + WHITE, [P3(a, h + .12), P3(b, h + .12), P3(c, h + .12), P3(e, h + .12)], va=va)
        walls("wash:" + CREAM, I, h - .28, h + .12, inward=True, va=va); cap("roof", I, h - .28, va=g.random())
        for side in range(4):
            Lg = w if side % 2 == 0 else d; n = max(1, int(Lg / 2.7)); south = side in (0, 1)        # the sunny sides get the large windows
            for fl in range(floors):
                top = fl == floors - 1
                if top and top_floor_bay and side == 0 and Lg > 5.5:
                    rabsel(w - 2 * bt * (fl * 2.75 + 2.6), d - 2 * bt * (fl * 2.75 + 2.6), side, .5, fl * 2.75 + 1.0, min(Lg - 2.6, g.uniform(2.6, 4.2)), 1.5, lit=g.random() < lit, trim=trim); continue
                for k_ in range(n):
                    if fl == 0 and (g.random() < .7 or side == door_side): continue
                    if not south and g.random() < .45: continue
                    f = (k_ + .5) / n + g.uniform(-.04, .04); zz = fl * 2.75 + (1.1 if fl else 1.4)
                    window(0, 0, w, d, 0, side, f, zz, (.8 if fl == 0 else 1.0) if not top else 1.15, (.7 if fl == 0 else 1.15) if not top else 1.4, lit=g.random() < lit, trim=trim, batter_in=bt * (zz + 2.4))
        if door_side is not None: door(0, 0, w, d, 0, door_side, .5 + g.uniform(-.2, .2), 0, trim=trim, lit=g.random() < lit * .6)
        zr = h - .28
        if wood:      # the winter's firewood and dung cakes, stacked all along the parapet
            for side in range(4):
                if g.random() < .72:
                    (ax, ay), _, _ = on_wall(0, 0, w - 2 * bt * h - .1, d - 2 * bt * h - .1, 0, side, .08); (bx, by), _, _ = on_wall(0, 0, w - 2 * bt * h - .1, d - 2 * bt * h - .1, 0, side, .92)
                    bar("wood:" + g.choice(("#4d3d2e", "#5a4836", "#3f3226")), (ax, ay, h + .32), (bx, by, h + .32), .55, .42, va=g.random())
        if flags:
            for c in I:
                if g.random() < .7:
                    cyl("paint:#4a3a2c", c[0] * .9, c[1] * .9, .16, zr, zr + 1.0, 5, r1=.26)
                    for a in (0, 1.6, 3.2, 4.8): face("paint:" + g.choice(FLAGS), [(c[0] * .9, c[1] * .9, zr + 1.0), (c[0] * .9 + .45 * math.cos(a), c[1] * .9 + .45 * math.sin(a), zr + 1.05), (c[0] * .9 + .45 * math.cos(a), c[1] * .9 + .45 * math.sin(a), zr + 1.55), (c[0] * .9, c[1] * .9, zr + 1.5)])
            if g.random() < .5: c = g.choice(I); pole(c[0] * .8, c[1] * .8, zr, g.uniform(3.4, 5.0), g=g)
        t = g.random()
        if t < .3: boxr("straw", "straw", g.uniform(-w / 6, w / 6), g.uniform(-d / 6, d / 6), min(2.4, w / 3), min(1.8, d / 3), zr, zr + .06, g.uniform(-20, 20))
        elif t < .5: boxr("paint:#a8322a", "paint:#a8322a", g.uniform(-w / 6, w / 6), g.uniform(-d / 6, d / 6), min(2.0, w / 4), min(1.4, d / 4), zr, zr + .07, g.uniform(-20, 20))
        if g.random() < .5: boxr("wash:" + CREAM, "paint:#2a221c", g.uniform(-w / 4, w / 4), g.uniform(-d / 4, d / 4), .7, .7, zr, zr + .8, 0)
        if g.random() < .3: lathe("wash:" + WHITE, w * .28, d * .22, [(.42, zr), (.5, zr + .5), (.28, zr + .95), (.2, zr + 1.2)], 8)
    return h

def house(cx, cy, w, d, rot=0.0, floors=2, z=None, wash=WHITE, band="#241a16", trim=None, g=random, lit=0.0, flags=True, wood=True, door_side=None, blend=2.6, claim_it=True, wing=None):
    """A Tibetan farmhouse of rammed earth and stone: a main block two or three floors high with leaning whitewashed walls, small
    windows below for the byre and stores, the timber bay of the best room above on the sunny side, a flat clay roof inside a
    dark parapet with the winter's fuel stacked along it; often a lower wing whose roof is the family's terrace.
    w and d are in its own metres; it stands U times that on the land. rot 45 turns its front to the camera."""
    wing = (g.random() < .55 and w > 6.5) if wing is None else wing; trim = trim or "#8a2f24"; va = g.random()
    ww, wd = (g.uniform(3.6, 5.2), d * g.uniform(.65, .95)) if wing else (0, 0); sgn = g.choice((-1, 1))
    full = w + ww
    if z is None: z = pad(cx, cy, (full + 1.0) * U, (d + 1.0) * U, rot, blend=blend, how="mean")
    paint("bare", cx, cy, (full + 3.0) * U, (d + 3.0) * U, rot, .9, 2.6)
    with placed_s(cx, cy, rot, z):
        x0 = -sgn * ww / 2
        h = _block(w, d, x0, 0, floors, g, wash, band, trim, lit, door_side, wood, flags, va)
        if wing:
            xw = x0 + sgn * (w / 2 + ww / 2 - .25); yw = -(d - wd) / 2 if g.random() < .7 else (d - wd) / 2
            _block(ww, wd, xw, yw, floors - 1, g, wash, band, trim, lit, None, wood and g.random() < .5, False, va, top_floor_bay=False)
            if floors - 1 >= 1 and g.random() < .7:      # the notched log that serves as a ladder to the terrace
                bar("wood:#5a4636", (xw + sgn * (ww / 2 + .5), yw - wd / 4, 0), (xw + sgn * (ww / 2 - .1), yw - wd / 4, (floors - 1) * 2.75 + .6), .22, .22)
    if claim_it: claim(cx, cy, math.hypot(full, d) / 2 * U, h * U)
    ROOFS.append((cx, cy, z + h * U, min(w, d) * U / 2))
    return z, h
ROOFS = []        # every house's roof: (x, y, height of its parapet, half its lesser side)

def chorten(cx, cy, z, sc=1.0, rot=45.0, lines=0, g=random):
    """A whitewashed stupa: stepped plinth, the dome, the square harmika, thirteen gilded rings and the sun and moon."""
    zz = z
    for k, (w, h) in enumerate(((4.6, .7), (4.0, .5), (3.4, .5), (2.9, .45))):
        boxr("wash:" + WHITE, "wash:" + WHITE, cx, cy, w * sc, w * sc, zz - (1.2 if not k else 0), zz + h * sc, rot, va=.3); zz += h * sc
    boxr("paint:" + MAROON, "paint:" + MAROON, cx, cy, 2.95 * sc, 2.95 * sc, zz - .16 * sc, zz - .02 * sc, rot)
    lathe("wash:" + WHITE, cx, cy, [(1.15 * sc, zz), (1.5 * sc, zz + .5 * sc), (1.62 * sc, zz + 1.1 * sc), (1.5 * sc, zz + 1.7 * sc), (1.05 * sc, zz + 2.2 * sc), (.6 * sc, zz + 2.4 * sc)], 16, va=.3); zz += 2.4 * sc
    boxr("wash:" + WHITE, "wash:" + WHITE, cx, cy, 1.1 * sc, 1.1 * sc, zz - .1, zz + .5 * sc, rot); zz += .5 * sc
    lathe("gold", cx, cy, [(.42 * sc, zz), (.14 * sc, zz + 1.9 * sc), (.3 * sc, zz + 2.0 * sc), (.3 * sc, zz + 2.08 * sc), (.02 * sc, zz + 2.5 * sc)], 10); top = zz + 2.4 * sc
    for k in range(6): lathe("gold", cx, cy, [(.46 * sc - k * .05 * sc, zz + (.15 + k * .3) * sc), (.48 * sc - k * .05 * sc, zz + (.22 + k * .3) * sc), (.4 * sc - k * .05 * sc, zz + (.28 + k * .3) * sc)], 10)
    for k in range(lines):
        a = math.radians(rot + 360 * k / lines + g.uniform(-12, 12)); r = g.uniform(9, 14) * sc; ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        if path_dist(ex, ey) < 2: continue
        beam("wood:#6b5846", (ex, ey, zt(ex, ey) - .3), (ex, ey, zt(ex, ey) + 2.2), .05, 5); flag_line((cx, cy, top - .3 * sc), (ex, ey, zt(ex, ey) + 2.2))
    claim(cx, cy, 3.2 * sc, 6.5 * sc); return top
def little_chorten(x, y, z, sc=.5):
    boxr("wash:" + WHITE, "wash:" + WHITE, x, y, 2.2 * sc, 2.2 * sc, z - .5, z + .8 * sc, 45, va=.4); boxr("wash:" + WHITE, "wash:" + WHITE, x, y, 1.6 * sc, 1.6 * sc, z + .8 * sc, z + 1.3 * sc, 45, va=.4)
    lathe("wash:" + WHITE, x, y, [(.6 * sc, z + 1.3 * sc), (.85 * sc, z + 1.9 * sc), (.6 * sc, z + 2.6 * sc)], 10, va=.4); lathe("gold", x, y, [(.25 * sc, z + 2.6 * sc), (.03 * sc, z + 3.9 * sc)], 8)

def stone_wall(pts, h=1.1, w=.6, key="drystone", top=None, follow=True):
    """A dry-stone wall along plan points, stepping with the land."""
    for (a, b) in zip(pts, pts[1:]):
        Lg = math.dist(a, b); n = max(1, int(Lg / 2.5))
        for k in range(n):
            p = (lerp(a[0], b[0], k / n), lerp(a[1], b[1], k / n)); q = (lerp(a[0], b[0], (k + 1) / n), lerp(a[1], b[1], (k + 1) / n)); m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            z = min(zt(*p), zt(*q), zt(*m)); zz = max(zt(*p), zt(*q), zt(*m)) + h; ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
            boxr(key, top or key, m[0], m[1], math.dist(p, q) + .1, w, z - .5, zz, ang, va=.5)
def mani_wall(x0, y0, x1, y1, h=1.3):
    """A long wall of carved prayer stones, whitewashed at the ends, slates leaning along its top."""
    stone_wall([(x0, y0), (x1, y1)], h, 1.3, "rubble", "paint:#6f6a62")
    for (x, y) in ((x0, y0), (x1, y1)): little_chorten(x, y, zt(x, y) + h * .2, .42)

def fire(x, y, z, r=.5, power=260.0, light=True, gain=3.2):
    """A fire of logs, its flame, and the light it throws."""
    for k in range(5):
        a = k * 1.256; beam("wood:#3a2c22", (x + math.cos(a) * r, y + math.sin(a) * r, z + .05), (x - math.cos(a) * r * .2, y - math.sin(a) * r * .2, z + r * .9), .09, 5)
    lathe("fire", x, y, [(r * .55, z + .1), (r * .7, z + r * .5), (r * .35, z + r * 1.3), (.03, z + r * 2.3)], 8, cap_top=False)
    if light:
        ld = bpy.data.lights.new("fire", "POINT"); ld.energy = power * gain; ld.color = (1.0, .5, .18); ld.shadow_soft_size = r * .8
        o = bpy.data.objects.new("fire", ld); ROOT.objects.link(o); o.location = (x, y, z + r * 1.6)

# ---------------------------------------------------------------- scanned trees, shrubs and rocks (Poly Haven)
def load(name, lods=("LOD2", "LOD1", "LOD3", "LOD0"), skip=("leaves_", "branches_", "geometry_nodes", "_trunk", "dead_branch")):
    """The asset's objects (one per variant), each in its own collection with its size."""
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
    for o in dst.objects:
        if o is not None and not o.users_collection: bpy.data.objects.remove(o)
    return out
def strew(variants, x, y, g, h=None, scale=1.0, sink=0.05, tilt=0.0):
    c, size = g.choice(variants)
    if h: scale = scale * h / max(1e-3, size.z)
    Scatter.add(c, x, y, zt(x, y) - sink * scale * size.z, g.uniform(0, 6.283), scale, (g.uniform(-tilt, tilt), g.uniform(-tilt, tilt)))
def snow_on(variants, amount=.8):
    """Snow lying on whatever faces the sky, for scanned trees and rocks in winter."""
    seen = set()
    for c, _ in variants:
        for o in c.all_objects:
            for sl in o.material_slots:
                m = sl.material
                if not m or m.name in seen or not m.use_nodes: continue
                seen.add(m.name); nt = m.node_tree
                for b in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
                    geo = nt.nodes.new("ShaderNodeNewGeometry"); sx = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], sx.inputs[0])
                    rp = nt.nodes.new("ShaderNodeMapRange"); rp.inputs[1].default_value = .15; rp.inputs[2].default_value = .55; nt.links.new(sx.outputs[2], rp.inputs[0])
                    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = amount; nt.links.new(rp.outputs[0], mul.inputs[0])
                    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs[7].default_value = (.82, .87, .95, 1); nt.links.new(mul.outputs[0], mx.inputs[0])
                    src = b.inputs["Base Color"]
                    if src.links: nt.links.new(src.links[0].from_socket, mx.inputs[6])
                    else: mx.inputs[6].default_value = src.default_value
                    nt.links.new(mx.outputs[2], src)

# ---------------------------------------------------------------- light and the render
def light(sun_el=38.0, sun_az=58.0, sun=5.5, sky=.5, exposure=.55, moon=2.6, hdri="kloofendal_48d_partly_cloudy_puresky"):
    el, az = math.radians(sun_el), math.radians(sun_az); sx, sy = math.cos(az), math.sin(az)      # light travels toward this bearing (degrees from east)
    so = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); ROOT.objects.link(so)
    so.rotation_euler = Vector((sx * math.cos(el), sy * math.cos(el), -math.sin(el))).to_track_quat("-Z", "Y").to_euler()
    so.data.energy = sun; so.data.color = (1, .93, .82); so.data.angle = math.radians(1.0)
    if NIGHT: so.data.energy = moon; so.data.color = (.5, .66, 1.0); so.data.angle = math.radians(1.6)
    world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True; wt = world.node_tree; bg = wt.nodes["Background"]
    env = wt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(os.path.join(ASSETS, hdri, hdri + "_2k.hdr"))
    mp = wt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(sun_az + 180 - 145.8)); tc = wt.nodes.new("ShaderNodeTexCoord")
    wt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); wt.links.new(mp.outputs[0], env.inputs["Vector"])
    cl = wt.nodes.new("ShaderNodeVectorMath"); cl.operation = "MINIMUM"; cl.inputs[1].default_value = (6, 6, 6)
    wt.links.new(env.outputs["Color"], cl.inputs[0]); wt.links.new(cl.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = sky
    if NIGHT:
        nb = wt.nodes.new("ShaderNodeMix"); nb.data_type = "RGBA"; nb.blend_type = "MULTIPLY"; nb.inputs[0].default_value = 1; nb.inputs[7].default_value = (.36, .5, 1.0, 1)
        wt.links.new(cl.outputs[0], nb.inputs[6]); wt.links.new(nb.outputs[2], bg.inputs[0]); bg.inputs[1].default_value = .16
    scene.render.engine = "CYCLES"; scene.cycles.samples = core.SAMPLES; scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6; scene.cycles.transparent_max_bounces = 24; scene.cycles.diffuse_bounces = 3
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()
        for dev in prefs.devices: dev.use = True
        scene.cycles.device = "GPU"
    except Exception as ex: print("GPU not enabled:", ex)
    scene.view_settings.view_transform = "AgX"
    try: scene.view_settings.look = "AgX - Punchy"
    except Exception as ex: print("look not set:", ex)
    scene.view_settings.exposure = .8 if NIGHT else exposure
    _grade()
    scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"; scene.render.filepath = OUT

def _grade():
    """Shade gathered where things meet, richer colour, a halo round flames by night, and a gentle S-curve."""
    ao, sat, con, bloom = (.5, 1.25, .6, 1.0) if NIGHT else (.45, 1.15, .5, 0)
    try:
        ng = bpy.data.node_groups.new("grade", "CompositorNodeTree"); ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        Nn, Ln = ng.nodes.new, ng.links.new; rl = Nn("CompositorNodeRLayers"); out = Nn("NodeGroupOutput"); img = rl.outputs["Image"]
        bpy.context.view_layer.use_pass_ambient_occlusion = True; scene.world.light_settings.distance = 2.5
        dn = Nn("CompositorNodeDenoise"); Ln(rl.outputs["Ambient Occlusion"], dn.inputs["Image"])
        mx = Nn("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = ao
        Ln(img, mx.inputs[6]); Ln(dn.outputs["Image"], mx.inputs[7]); img = mx.outputs[2]
        hs = Nn("CompositorNodeHueSat"); hs.inputs["Saturation"].default_value = sat; Ln(img, hs.inputs["Image"]); img = hs.outputs["Image"]
        if bloom > 0:
            gl = Nn("CompositorNodeGlare"); gl.inputs["Type"].default_value = "Bloom"; gl.inputs["Threshold"].default_value = 1.5
            gl.inputs["Strength"].default_value = bloom; gl.inputs["Size"].default_value = .45; Ln(img, gl.inputs["Image"]); img = gl.outputs["Image"]
        Ln(img, out.inputs[0]); scene.compositing_node_group = ng; scene.render.use_compositing = True
    except Exception as ex: print("grade not set:", ex)
    vs = scene.view_settings; vs.use_curve_mapping = True; c = vs.curve_mapping.curves[3]
    c.points.new(.25, .25 - .07 * con); c.points.new(.75, .75 + .06 * con); vs.curve_mapping.update()

def finish(net, winter=False):
    """Everything gathered becomes meshes; the roads are checked against the camera; the picture is rendered."""
    core.flush(); Scatter.flush(); finish_land(winter)
    guides = blender_stage.roads(net, lift=.12) if GUIDES else []
    blender_stage.check(net)
    if not flag("--no-render"): bpy.ops.render.render(write_still=True); print("WROTE", OUT)

def write_network(path, stage, places, roads, night=False, **extra):
    """The world's transport network, for tools/allegory.py: the places and the paths at the heights the land gave them."""
    o = dict(stage=stage, units="m", night=night, picture=stage + ".png", camera=dict(elev=ELEV), **extra, places=places, roads=roads)
    sys.path.insert(0, os.path.join(REPO, "tools")); import allegory
    open(path, "w").write(allegory.dumps(o)); return o
