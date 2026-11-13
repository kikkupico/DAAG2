"""The land: one height field (a plain rising gently from the shore, the acropolis, a vine-hill in the west), the roads graded
into it, maps of what covers the ground, and at the end the terrain mesh and the sea.

Builders change the land before the mesh is made: pad() levels a site, paint() lays a ground cover, take() marks ground as used."""
import bpy, math, os
import numpy as np
from . import core
from .core import S, SIEGE, ROOT, inpoly, area, centre, bbox, chaikin, grow, seg_dist, lin, HALF_VIEW
from .sh import Sh

HALF, STEP, MRES = 250.0, 0.5, 0.25
NX = int(2 * HALF / STEP) + 1; NM = int(2 * HALF / MRES) + 1
gx = np.linspace(-HALF, HALF, NX); X, Y = np.meshgrid(gx, gx, indexing="xy")          # Z[j, i] is the ground at (gx[i], gx[j])
gm = np.linspace(-HALF, HALF, NM); XM, YM = np.meshgrid(gm, gm, indexing="xy")        # the cover maps' finer grid

# ---------------------------------------------------------------- noise in numpy
def _hash(i, j, seed):
    n = (i.astype(np.int64) * 374761393 + j.astype(np.int64) * 668265263 + seed * 1442695041) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0
def vnoise(x, y, seed=0):
    x = np.asarray(x, np.float64); y = np.asarray(y, np.float64)
    xi = np.floor(x); yi = np.floor(y); u = x - xi; v = y - yi; u = u * u * (3 - 2 * u); v = v * v * (3 - 2 * v)
    a, b, c, d = _hash(xi, yi, seed), _hash(xi + 1, yi, seed), _hash(xi, yi + 1, seed), _hash(xi + 1, yi + 1, seed)
    return (a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v) * 2 - 1
def fbm(x, y, scale, octaves=4, seed=0, gain=.5, lac=2.03):
    """Fractal noise in about -1..1; `scale` is the size in metres of its largest features."""
    out = 0.0; amp = 1.0; f = 1.0 / scale; tot = 0.0
    for o in range(octaves): out = out + amp * vnoise(x * f + 17.3 * o, y * f - 9.1 * o, seed + o); tot += amp; amp *= gain; f *= lac
    return out / tot
def sstep(a, b, t):
    t = np.clip((t - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

# ---------------------------------------------------------------- windows of the grids, polygons on them
def win(x0, y0, x1, y1, pad=0.0, res=STEP, n=NX):
    i0, i1 = max(0, int((x0 - pad + HALF) / res)), min(n, int((x1 + pad + HALF) / res) + 2)
    j0, j1 = max(0, int((y0 - pad + HALF) / res)), min(n, int((y1 + pad + HALF) / res) + 2)
    return (slice(j0, j1), slice(i0, i1))
def np_inpoly(P, xs, ys):
    c = np.zeros(xs.shape, dtype=bool)
    for (ax, ay), (bx, by) in zip(P, P[1:] + P[:1]):
        if ay == by: continue
        c ^= ((ay > ys) != (by > ys)) & (xs < ax + (ys - ay) * (bx - ax) / (by - ay))
    return c
def np_segdist(ax, ay, bx, by, xs, ys):
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9
    t = np.clip(((xs - ax) * dx + (ys - ay) * dy) / L2, 0, 1); return np.hypot(xs - ax - t * dx, ys - ay - t * dy), t
def np_edgedist(P, xs, ys, closed=True):
    d = np.full(xs.shape, 1e9)
    for a, b in zip(P, (P[1:] + P[:1]) if closed else P[1:]): d = np.minimum(d, np_segdist(a[0], a[1], b[0], b[1], xs, ys)[0])
    return d

# ---------------------------------------------------------------- the shore, and how far inland every point is
SHORE = [tuple(p) for p in S["shore"] if -330 <= p[0] <= 330] if S.get("shore") and not SIEGE else []
def shore_y(x):
    if not SHORE: return -1e9
    i = max(0, min(len(SHORE) - 2, int((x - SHORE[0][0]) / (SHORE[1][0] - SHORE[0][0])))); (x0, y0), (x1, y1) = SHORE[i], SHORE[i + 1]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
if SHORE:
    SD = np_edgedist(SHORE, X, Y, closed=False)
    SD = np.where(Y > np.interp(X, [p[0] for p in SHORE], [p[1] for p in SHORE]), SD, -SD)
    SD = SD + 2.2 * fbm(X, Y, 38, 3, seed=5) * np.clip(1 - np.abs(SD) / 40, 0, 1)      # the waterline wanders a little
else: SD = np.full(X.shape, 400.0)

# ---------------------------------------------------------------- the smooth land: what roads are graded to
def plain(x, y, sd):
    z = np.where(sd > 0, .12 + 9.0 * (1 - np.exp(-np.maximum(sd, 0) / 170.0)), -np.minimum(14.0, .05 * np.abs(sd) + .0016 * sd * sd))
    if not SIEGE:
        z = z + 5.5 * np.exp(-((x + 205) ** 2 + (y - 25) ** 2) / (2 * 75.0 ** 2)) * sstep(0, 30, sd)        # the vine-hill in the west
        z = z + 1.4 * np.exp(-((x - 185) ** 2 + (y - 60) ** 2) / (2 * 60.0 ** 2))                              # a swell in the eastern fields
    else:                                                                                 # the besieged town's country: rolling ground, the town on a low rise
        z = 6.0 + 2.4 * fbm(x, y, 240, 2, seed=3) + 2.2 * np.exp(-(x ** 2 + y ** 2) / (2 * 80.0 ** 2))
    return z
ZS = plain(X, Y, SD)
def bil(A, x, y, res=STEP, n=NX):
    fx, fy = (x + HALF) / res, (y + HALF) / res
    if not (0 <= fx < n - 1 and 0 <= fy < n - 1): return float(A[min(n - 1, max(0, int(fy))), min(n - 1, max(0, int(fx)))])
    i, j = int(fx), int(fy); a, b = fx - i, fy - j
    return float(A[j, i] * (1 - a) * (1 - b) + A[j, i + 1] * a * (1 - b) + A[j + 1, i] * (1 - a) * b + A[j + 1, i + 1] * a * b)

# The acropolis. Fixed by the page: the broad stair on x = 0 from y = 40 to 104, the forecourt path to (0, 114) and west along
# y = 114 to (-46, 114), and the west stair down that line to the postern and the ring road. Everything else is free.
HILL = not SIEGE
STAIR_Y0, STAIR_Y1, RISE = 40.0, 104.0, 20.0
Z40 = bil(ZS, 0, STAIR_Y0); TOP = round(Z40 + RISE, 2) if HILL else 0.0
SUMMIT = [(-26, 101.5), (26, 101.5), (46, 107), (54, 126), (52, 154), (38, 169), (-30, 170), (-48, 160), (-52, 132), (-47, 107)]
FOOT = chaikin([(0, 34), (46, 40), (78, 54), (89, 82), (97, 100), (104, 118), (108, 150), (104, 190), (80, 226), (30, 246), (-40, 244), (-86, 222),
                (-104, 182), (-100, 140), (-90, 114), (-89, 84), (-80, 56), (-46, 40)], 2)
POSTERN = (-83.2, 114.0)
if HILL:
    d_sum = np.where(np_inpoly(SUMMIT, X, Y), 0, np_edgedist(SUMMIT, X, Y)); infoot = np_inpoly(FOOT, X, Y); d_foot = np_edgedist(FOOT, X, Y)
    U = np.where(infoot, d_foot / np.maximum(1e-6, d_foot + d_sum), 0.0)                 # 0 at the hill's foot, 1 on the summit
    P_NAT = .30 * U + .70 * sstep(.38, .93, U)                                            # gentle below, a band of crags under the summit
    T_S = np.clip((Y - STAIR_Y0) / (STAIR_Y1 - STAIR_Y0), 0, 1)                           # the south slope the town climbs: an even ramp
    G_S = sstep(84, 60, np.abs(X)) * sstep(108, 100, Y)
    P = P_NAT * (1 - G_S) + T_S * G_S
    ZS = ZS * (1 - P) + TOP * P
    CRAG = np.clip(U * (1 - U) * 4, 0, 1) * (1 - G_S) * infoot
else:
    P = np.zeros(X.shape); CRAG = np.zeros(X.shape); G_S = np.zeros(X.shape)

# ---------------------------------------------------------------- roads: the drawing's, less the stretches the hill covers
ROADS = []                                                                               # (width, kind, [(x, y), ...])
def _cut_north(pts):
    """The ring road's unused northern loop, replaced by a track that leaves the picture round the hill's foot."""
    keep = [p for p in pts]
    i_e = max(i for i, p in enumerate(keep) if p[0] > 0 and p[1] < 128 and i < len(keep) / 2)   # last point going up the east side
    i_w = min(i for i, p in enumerate(keep) if p[0] < 0 and p[1] < 116)                         # first point coming down the west side
    east = keep[:i_e + 1] + [(112, 140), (116, 170), (110, 215), (86, 250)]
    west = [(-70, 250), (-98, 222), (-110, 180), (-106, 140), (-98.6, 124)] + keep[i_w:]
    return east, west
for w, kind, pts in S["roads"]:
    pts = [tuple(p) for p in pts]
    if kind == "stair":
        if abs(pts[0][0]) < 1: ROADS.append((w, "stair", pts))
        else: ROADS.append((w, "stair", [(-46.0, 114.0), POSTERN, (-97.7, 114.0)]))
    elif kind == "road" and len(pts) > 20 and HILL:
        e, wst = _cut_north(pts); ROADS += [(w, "road", e), (w, "road", wst)]
    elif kind == "street" and w >= 8: ROADS.append((w, "avenue", pts))
    elif kind == "street" and HILL and len(pts) == 2 and pts[0][0] == pts[1][0] == 38: ROADS.append((w, kind, [pts[0], (38, 40.5)]))      # the theatre takes the rest of this street (no messenger walks it)
    else: ROADS.append((w, kind, pts))
KIND_V = {"road": 0.0, "path": 0.0, "street": .5, "lane": .5, "avenue": 1.0, "paving": 1.0, "stair": 1.0}
def add_road(w, kind, pts): ROADS.append((w, kind, [tuple(p) for p in pts]))

ROAD_D = np.full((NM, NM), 40.0, np.float32); ROAD_LAT = np.ones((NM, NM), np.float32); ROAD_K = np.zeros((NM, NM), np.float32)
GRADED = []                                                                              # (a, b, za, zb, half-width, kind): every graded stretch
Z = None; LOCK = np.zeros((NX, NX), bool); OCC = np.zeros((NX, NX), bool)
def _subdivide(pts, step=3.0):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    return out
def _profile(kind, pts):
    """Heights along a road: the smooth land's, or an even climb for the stairs."""
    if kind == "stair" and abs(pts[0][0]) < 1: return [(p, Z40 + (TOP - Z40) * (p[1] - STAIR_Y0) / (STAIR_Y1 - STAIR_Y0)) for p in _subdivide(pts)]
    if kind == "stair":
        zp = bil(ZS0, *POSTERN) + .6; ze = bil(ZS0, pts[-1][0], pts[-1][1]); out = []
        for p in _subdivide(pts):
            out.append((p, TOP + (zp - TOP) * (p[0] - pts[0][0]) / (POSTERN[0] - pts[0][0]) if p[0] >= POSTERN[0] else zp + (ze - zp) * (p[0] - POSTERN[0]) / (pts[-1][0] - POSTERN[0])))
        return out
    if kind == "paving": return [(p, TOP) for p in _subdivide(pts)]
    return [(p, bil(ZS, p[0], p[1])) for p in _subdivide(pts)]
ZS0 = plain(X, Y, SD)                                                                    # the land without the hill (for the foot of the west stair)

def _round_corners(pts, rad=5.5):
    """Smooth sharp polyline corners on country roads with a local quadratic fillet."""
    if len(pts) < 3: return list(pts)
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        la = math.hypot(b[0] - a[0], b[1] - a[1]); lc = math.hypot(c[0] - b[0], c[1] - b[1])
        if la < 1e-6 or lc < 1e-6: continue
        d = min(rad, la * .35, lc * .35)
        p0 = (b[0] + (a[0] - b[0]) * d / la, b[1] + (a[1] - b[1]) * d / la)
        p2 = (b[0] + (c[0] - b[0]) * d / lc, b[1] + (c[1] - b[1]) * d / lc)
        for k in range(5):
            t = k / 4; mt = 1 - t
            out.append((mt * mt * p0[0] + 2 * mt * t * b[0] + t * t * p2[0], mt * mt * p0[1] + 2 * mt * t * b[1] + t * t * p2[1]))
    out.append(pts[-1]); return out

def _meander_pts(pts, hw):
    """Gently curve and wander country tracks away from gates and junctions."""
    pts = _subdivide(_round_corners(pts), 3.0)
    if len(pts) < 3: return pts
    s = [0.0]
    for a, b in zip(pts, pts[1:]): s.append(s[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = s[-1]; amp = min(1.15, hw * .38); out = [pts[0]]
    for i in range(1, len(pts) - 1):
        ax, ay = pts[i - 1]; bx, by = pts[i + 1]; L = math.hypot(bx - ax, by - ay) or 1.0
        nx, ny = -(by - ay) / L, (bx - ax) / L; px, py = pts[i]
        fade = min(1.0, s[i] / 8.0) * min(1.0, (total - s[i]) / 8.0)
        fade = fade * fade * (3 - 2 * fade)
        w = float(fbm(px, py, 26.0, 3, seed=71)) * amp * fade
        out.append((px + nx * w, py + ny * w))
    out.append(pts[-1]); return out

def grade_roads():
    """Carve every road into the height field at its own profile, and write the road maps the ground's material draws from."""
    global Z
    best = np.full(X.shape, 1e9)
    road_wig = fbm(XM, YM, 14.0, 3, seed=53) * 1.15 + fbm(XM, YM, 4.5, 3, seed=89) * 0.65
    for w, kind, pts in ROADS:
        prof = _profile(kind, pts); hw = w / 2; mud = kind in ("road", "path")
        for (a, za), (b, zb) in zip(prof, prof[1:]):
            GRADED.append((a, b, za, zb, hw, kind))
            sub = win(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), hw + 5)
            d, t = np_segdist(a[0], a[1], b[0], b[1], X[sub], Y[sub]); zl = za + (zb - za) * t
            reach = 2.2 if kind in ("stair", "paving") else 3.5
            wgt = np.clip(1 - (d - hw - .3) / reach, 0, 1); wgt = wgt * wgt * (3 - 2 * wgt)
            near = d < best[sub]
            Zs = Z[sub]; Zs[near] = (Zs * (1 - wgt) + zl * wgt)[near]; bs = best[sub]; bs[near & (wgt > 0)] = d[near & (wgt > 0)]
            LOCK[sub] |= d < hw + .4
            if kind == "stair" or mud: continue                                           # stairs are built; mud roads painted below
            subm = win(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), hw + 10, MRES, NM)
            dm, _ = np_segdist(a[0], a[1], b[0], b[1], XM[subm], YM[subm]); m = (dm - hw) < ROAD_D[subm]
            ROAD_D[subm] = np.where(m, dm - hw, ROAD_D[subm]); ROAD_LAT[subm] = np.where(m, dm / hw, ROAD_LAT[subm]); ROAD_K[subm] = np.where(m, KIND_V[kind], ROAD_K[subm])
        if mud:
            vpts = _meander_pts(pts, hw)
            for a, b in zip(vpts, vpts[1:]):
                subm = win(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), hw + 12, MRES, NM)
                dm, _ = np_segdist(a[0], a[1], b[0], b[1], XM[subm], YM[subm])
                dm_e = dm + road_wig[subm] * np.clip(dm / max(hw, .5), 0.0, 1.0)
                m = (dm_e - hw) < ROAD_D[subm]
                ROAD_D[subm] = np.where(m, dm_e - hw, ROAD_D[subm]); ROAD_LAT[subm] = np.where(m, np.clip(dm_e / max(hw, .5), 0.0, 4.0), ROAD_LAT[subm]); ROAD_K[subm] = np.where(m, KIND_V[kind], ROAD_K[subm])
def zroute(x, y):
    """A walker's height at a point on a road: the graded profile of the nearest stretch."""
    bd = 1e9; bz = None
    for a, b, za, zb, hw, kind in GRADED:
        dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy or 1e-9
        t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / L2)); d = math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)
        if d < bd: bd = d; bz = za + (zb - za) * t
    return bz, bd
def road_dist(x, y):
    """Metres to the nearest road's edge (negative on a road)."""
    return bil(ROAD_D, x, y, MRES, NM)

# ---------------------------------------------------------------- the rough land: relief everywhere a road or a building is not
def roughen():
    global Z
    rd = ROAD_D[::2, ::2]; away = np.clip((rd - 1.5) / 9, 0, 1)
    octa = [(x * 1.02, y * 1.02) for x, y in S["octagon"]]
    town = np_inpoly(octa, X, Y)
    if HILL: town |= (np.abs(X) < 80) & (Y > 50) & (Y < 100) & (G_S > .5)
    wild = away * (~town) * sstep(-2, 12, SD)
    Z = ZS.copy()
    Z += wild * (.55 * fbm(X, Y, 46, 4, seed=11) + .16 * fbm(X, Y, 9, 3, seed=12))
    if HILL:                                                                              # crags: ledges and hollows in the steep band under the summit
        ledge = fbm(X, Y, 22, 5, seed=21, gain=.55); ridged = 1 - np.abs(fbm(X, Y, 15, 4, seed=22))
        Z += CRAG * np.clip((rd - 1) / 6, 0, 1) * (2.6 * ledge + 1.8 * (ridged - .6))
        Z = np.where(np_inpoly(SUMMIT, X, Y), TOP, Z)
    Z = np.where(SD < 0, ZS, Z)

# ---------------------------------------------------------------- reading and changing the land
def zt(x, y): return bil(Z, x, y)
def zmin(pts): return min(zt(x, y) for x, y in list(pts) + [centre(pts)])
def zmax(pts): return max(zt(x, y) for x, y in list(pts) + [centre(pts)])
def sd_at(x, y): return bil(SD, x, y)
def pad(P, z=None, blend=2.0, lock=True, how="mean", grow_by=.3):
    """Level the ground inside a polygon (to z, or to its own mean / highest / lowest ground) and ease the ground outside to meet it.
    Roads and earlier pads are left alone. Returns the level."""
    Pg = grow(P, grow_by) if grow_by else list(P); x0, y0, x1, y1 = bbox(Pg); sub = win(x0, y0, x1, y1, blend + 1)
    xs, ys = X[sub], Y[sub]; m = np_inpoly(Pg, xs, ys); Zs = Z[sub]; fr = ~LOCK[sub]
    if z is None:
        vals = Zs[m] if m.any() else np.array([zt(*centre(P))])
        z = float({"mean": np.mean, "max": np.max, "min": np.min, "median": np.median}[how](vals))
    if blend > 0:
        d = np_edgedist(Pg, xs, ys); w = np.clip(1 - d / blend, 0, 1); w = w * w * (3 - 2 * w); o = (~m) & fr
        Zs[o] = (Zs * (1 - w) + z * w)[o]
    Zs[m & fr] = z
    if lock: LOCK[sub] |= m
    return z
def take(P, margin=0.0):
    """Mark ground as used: nothing is scattered or planted there."""
    Pg = grow(P, margin) if margin else list(P); x0, y0, x1, y1 = bbox(Pg); sub = win(x0, y0, x1, y1, 1)
    OCC[sub] |= np_inpoly(Pg, X[sub], Y[sub])
def take_disc(x, y, r):
    sub = win(x - r, y - r, x + r, y + r, 1); OCC[sub] |= np.hypot(X[sub] - x, Y[sub] - y) < r
def free(x, y, r=0.0):
    """Is this spot (and a circle of radius r round it) unused ground?"""
    if r <= 0:
        i, j = int(round((x + HALF) / STEP)), int(round((y + HALF) / STEP))
        return 0 <= i < NX and 0 <= j < NX and not OCC[j, i]
    sub = win(x - r, y - r, x + r, y + r, 0)
    return not OCC[sub][np.hypot(X[sub] - x, Y[sub] - y) <= r].any()

COVERS = ("sand", "rock", "earth", "pave", "gravel", "wet", "stubble", "plough", "green", "fcos", "fsin", "lush")
COV = {k: np.zeros((NM, NM), np.float32) for k in COVERS}
def paint(name, P, v=1.0, feather=.6, how="max", closed=True, width=0.0):
    """Lay a ground cover inside a polygon (or along a line `width` wide), feathered at its edge."""
    x0, y0, x1, y1 = bbox(P); sub = win(x0, y0, x1, y1, feather + width + 1, MRES, NM); xs, ys = XM[sub], YM[sub]
    if closed:
        m = np_inpoly(list(P), xs, ys); d = np.where(m, 0, np_edgedist(list(P), xs, ys))
    else: d = np.maximum(0, np_edgedist(list(P), xs, ys, closed=False) - width / 2)
    val = v * np.clip(1 - d / max(1e-6, feather), 0, 1)
    A = COV[name]
    if how == "max": A[sub] = np.maximum(A[sub], val)
    elif how == "set": A[sub] = np.where(d <= 0, v, A[sub])
    elif how == "clear": A[sub] = A[sub] * (1 - np.clip(1 - d / max(1e-6, feather), 0, 1))
def paint_disc(name, x, y, r, v=1.0, feather=1.0):
    sub = win(x - r, y - r, x + r, y + r, feather + 1, MRES, NM); d = np.hypot(XM[sub] - x, YM[sub] - y) - r
    COV[name][sub] = np.maximum(COV[name][sub], v * np.clip(1 - d / feather, 0, 1))
def clear_disc(name, x, y, r, feather=1.0):
    sub = win(x - r, y - r, x + r, y + r, feather + 1, MRES, NM); d = np.hypot(XM[sub] - x, YM[sub] - y) - r
    COV[name][sub] = COV[name][sub] * np.clip(d / feather, 0, 1)
def field(P, kind, angle, feather=.8):
    """A tilled plot: its cover and the direction of its rows (degrees from east)."""
    for k in ("stubble", "plough", "green"): paint(k, P, feather=feather, how="clear")
    paint(kind, P, feather=feather)
    x0, y0, x1, y1 = bbox(P); sub = win(x0, y0, x1, y1, feather + 1.5, MRES, NM); m = np_inpoly(grow(P, feather + .5), XM[sub], YM[sub])
    COV["fcos"][sub] = np.where(m, math.cos(math.radians(angle)) * .5 + .5, COV["fcos"][sub]); COV["fsin"][sub] = np.where(m, math.sin(math.radians(angle)) * .5 + .5, COV["fsin"][sub])

def earthwork(P, bumps, closed=True, keep_clear=2.2):
    """Dig and heap along a line: `bumps` are (offset from the line, half-width, height) with negative heights for ditches.
    Offsets are positive outward (outside a closed outline, or right of an open line's direction). Roads are left alone."""
    P = list(P); x0, y0, x1, y1 = bbox(P); pad_ = max(abs(o) + hw for o, hw, h in bumps) + 1; sub = win(x0, y0, x1, y1, pad_); xs, ys = X[sub], Y[sub]
    d = np_edgedist(P, xs, ys, closed)
    if closed: sd = np.where(np_inpoly(P, xs, ys), -d, d)
    else:
        best = np.full(xs.shape, 1e9); sd = np.zeros(xs.shape)
        for a, b in zip(P, P[1:]):
            dd, t = np_segdist(a[0], a[1], b[0], b[1], xs, ys); side = np.sign((xs - a[0]) * (b[1] - a[1]) - (ys - a[1]) * (b[0] - a[0]))
            m = dd < best; sd = np.where(m, dd * side, sd); best = np.minimum(best, dd)
    fade = np.clip((ROAD_D[::2, ::2][sub] - .3) / keep_clear, 0, 1)
    for off, hw, h in bumps: Z[sub] += h * np.clip(1 - ((sd - off) / hw) ** 2, 0, 1) * fade
def init():
    global Z
    Z = ZS.copy(); grade_roads(); zr = Z.copy(); roughen()
    best = np.full(X.shape, 1e9)                                                          # the roads again, over the rough land
    for a, b, za, zb, hw, kind in GRADED:
        sub = win(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]), hw + 5)
        d, t = np_segdist(a[0], a[1], b[0], b[1], X[sub], Y[sub]); zl = za + (zb - za) * t
        reach = 2.2 if kind in ("stair", "paving") else 3.5
        wgt = np.clip(1 - (d - hw - .3) / reach, 0, 1); wgt = wgt * wgt * (3 - 2 * wgt); near = d < best[sub]
        Zs = Z[sub]; Zs[near] = (Zs * (1 - wgt) + zl * wgt)[near]; bs = best[sub]; bs[near & (wgt > 0)] = d[near & (wgt > 0)]
    OCC[:] = (ROAD_D[::2, ::2] < 1.2) | (SD < 4)

# ---------------------------------------------------------------- the terrain mesh, its material, and the sea
def map_image(name, chans, float_=False):
    """A picture of the land for the materials to read: up to three arrays as its red, green and blue."""
    n = chans[0].shape[0]; img = bpy.data.images.new(name, n, n, alpha=False, float_buffer=float_); img.colorspace_settings.name = "Non-Color"
    px = np.ones((n, n, 4), np.float32)
    for k, c in enumerate(chans): px[..., k] = c
    img.pixels.foreach_set(px.ravel()); return img
def map_tex(s, img):
    n = img.size[0]; res = 2 * HALF / (n - 1)
    v = s.mapping(s.pos, 1 / (n * res), ((HALF + res / 2) / (n * res), (HALF + res / 2) / (n * res), 0))
    return s.node("ShaderNodeSeparateColor", name="sep"), s.img(img, v, ext="EXTEND")
def read_map(s, img):
    sep, col = map_tex(s, img); s.set(sep.inputs[0], col); return sep.outputs

def _maps(s):
    """The land's maps as shader values: road (edge distance, across, kind), covers 1-4."""
    if "road" not in MAPIMG:
        MAPIMG["road"] = map_image("m_road", (ROAD_D, ROAD_LAT, ROAD_K), True)
        MAPIMG["c1"] = map_image("m_cov1", (COV["sand"], COV["rock"], COV["earth"])); MAPIMG["c2"] = map_image("m_cov2", (COV["pave"], COV["gravel"], COV["wet"]))
        MAPIMG["c3"] = map_image("m_cov3", (COV["stubble"], COV["plough"], COV["green"])); MAPIMG["c4"] = map_image("m_cov4", (COV["fcos"], COV["fsin"], COV["lush"]), True)
    return {k: read_map(s, im) for k, im in MAPIMG.items()}
MAPIMG = {}
def _finish(s, col, alpha=None, rough=.92, bump=.55, height=None):
    big = s.noise(.012, 5, .6)
    col = s.mix(s.rng(big, .25, .8, .0, .22), col, s.mix(1.0, col, (.78, .74, .66), "MULTIPLY"))   # slow light and dark over everything
    kw = {} if alpha is None else dict(Alpha=alpha)
    nor = s.bump(s.lum(col), bump, .12)
    if height is not None: nor = s.bump(height, .9, .22, nor)
    return s.surface(s.bsdf(col, rough, nor, **kw))
def _wild(s, c4):
    """The wild ground: summer grass gone to straw, greener in patches, red earth showing through."""
    big = s.noise(.012, 5, .6); mid = s.noise(.06, 5, .65); fine = s.noise(.9, 4, .7)
    grass = s.tint(s.tex2("withered_grass", 7), "withered_grass", lin("#b9a56b"), raw=.25)
    green = s.tint(s.tex("aerial_grass_rock", 26), "aerial_grass_rock", lin("#8d9156"), raw=.3)
    earth = s.tint(s.tex2("dirt_aerial_03", 17), "dirt_aerial_03", lin("#b39069"), raw=.2)
    wild = s.mix(s.rng(s.madd(mid, .6, big), .68, .98), grass, green)
    wild = s.mix(s.rng(c4[2], .05, .9), wild, s.tint(s.tex("sparse_grass", 6), "sparse_grass", lin("#76864a"), raw=.3))
    return s.mix(s.rng(s.madd(fine, .22, s.noise(.035, 5, .65, w=3.3)), .6, .76), wild, earth), fine

def ground_material():
    """The base layer: wild ground, bare rock, trodden earth, gravel."""
    s = Sh("ground"); M = s.mix; m = _maps(s); c1, c2 = m["c1"], m["c2"]
    col, fine = _wild(s, m["c4"])
    rockc = s.tint(s.tex2("marble_cliff_03", 13), "marble_cliff_03", lin("#cbc3b2"), raw=.35)
    rockc = M(s.rng(s.noise(.11, 4, .7, w=1.7), .5, .75), rockc, s.tint(s.tex("rocky_terrain_03", 11), "rocky_terrain_03", lin("#b9ab8e"), raw=.2))
    col = M(s.rng(s.madd(fine, .5, c1[1]), .45, .85), col, rockc)
    trod = s.tint(s.tex2("dirt_aerial_03", 12), "dirt_aerial_03", lin("#c6ad84"), raw=.2)
    trod = M(s.rng(s.noise(.13, 5, .7, w=11.0), .42, .72, 0, .55), trod, s.tint(s.tex("dirt_aerial_02", 15), "dirt_aerial_02", lin("#a8906c"), raw=.2))   # darker, damper, dung-stained ground in patches
    trod = M(s.rng(s.noise(.5, 4, .7, w=12.0), .6, .8, 0, .5), trod, lin("#d9c9a4"))                                                                       # dust and chaff
    col = M(s.rng(s.madd(fine, .35, c1[2]), .35, .75), col, trod)
    grav = s.tint(s.tex("gravelly_sand", 3), "gravelly_sand", lin("#bfb7a6"), raw=.3)
    col = M(s.rng(s.madd(fine, .3, c2[1]), .4, .7), col, grav)
    return _finish(s, col)

def field_material():
    """Tilled plots, laid over the base: rows along each plot's own direction."""
    s = Sh("fields"); M = s.mix; m = _maps(s); c3, c4 = m["c3"], m["c4"]; fine = s.noise(.9, 4, .7)
    px = s.xyz(s.pos); cosv = s.madd(c4[0], 2, -1); sinv = s.madd(c4[1], 2, -1)
    across = s.add(s.mul(px[0], s.math("MULTIPLY", sinv, -1)), s.mul(px[1], cosv))       # metres across the rows
    def rows(period, wob=.15):
        ph = s.madd(s.noise(.25, 2, .5, w=9.1), wob * 6.283, s.mul(across, 6.283 / period)); return s.madd(s.math("SINE", ph), .5, .5)
    patch = s.noise(.11, 4, .65, w=6.6); weeds = s.rng(s.noise(.3, 5, .7, w=2.9), .6, .78)
    r_st, r_pl, r_gr = rows(1.3), rows(.85, .18), rows(1.4, .08)
    stub = s.tint(s.tex2("withered_grass", 5), "withered_grass", lin("#dfc472"), raw=.12)
    stub = M(s.rng(patch, .3, .75, 0, .5), stub, lin("#c7a858")); stub = M(s.mul(r_st, .52), stub, lin("#987b44"))
    plo = s.tint(s.tex2("farm_soil", 4), "farm_soil", lin("#7c5843"), raw=.3)
    plo = M(s.rng(patch, .3, .75, 0, .7), plo, lin("#977258")); plo = M(s.mul(r_pl, .16), plo, lin("#553a2c"))
    plo = M(s.rng(s.noise(2.2, 3, .7, w=4.1), .5, .8, 0, .3), plo, lin("#a5846a")); plo = M(s.mul(weeds, .6), plo, lin("#8f8a55"))
    grn = M(s.rng(s.madd(s.sub(s.noise(1.2, 3, .7, w=8.2), .5), .5, r_gr), .3, .8), lin("#86694a"), s.tint(s.tex("sparse_grass", 4), "sparse_grass", lin("#62803e"), raw=.3))
    col = M(s.rng(c3[1], .3, .7), stub, plo); col = M(s.rng(c3[2], .3, .7), col, grn)
    hgt = s.mixf(s.rng(c3[1], .3, .7), s.mul(r_st, .32), s.mul(r_pl, .35))
    cov = s.maxf(c3[0], s.maxf(c3[1], c3[2]))
    edge_n = s.add(s.mul(s.sub(s.noise(.12, 4, .65, w=1.9), .5), 2.8), s.mul(s.sub(s.noise(.38, 4, .7, w=7.3), .5), 2.2))
    a = s.rng(s.madd(edge_n, s.rng(cov, .08, .92, 1.0, .18), s.madd(s.sub(fine, .5), .4, cov)), .34, .62)
    return _finish(s, col, a, height=hgt)

def shore_material():
    """Sand, darker where the sea wets it."""
    s = Sh("shore"); M = s.mix; m = _maps(s); c1, c2 = m["c1"], m["c2"]; fine = s.noise(.9, 4, .7)
    sand = s.tint(s.tex2("aerial_beach_02", 16), "aerial_beach_02", lin("#dccba3"), raw=.2)
    sand = M(s.rng(s.noise(.2, 3, .6, w=5.5), .55, .8), sand, s.tint(s.tex("coast_sand_rocks_02", 9), "coast_sand_rocks_02", lin("#c4b592"), raw=.3))
    col = M(s.mul(s.rng(c2[2], .05, .8), .55), sand, s.mix(1.0, sand, (.42, .40, .36), "MULTIPLY"))
    return _finish(s, col, s.rng(s.madd(s.sub(fine, .5), .4, c1[0]), .4, .75), bump=.3)

def road_material():
    """Roads and paving: natural mud tracks with wandering grassy edges and ruts, packed earth in the streets, slabs on the avenues."""
    s = Sh("roads"); M = s.mix; m = _maps(s); rd, c2 = m["road"], m["c2"]; fine = s.noise(.9, 4, .7)
    trod = s.tint(s.tex("dirt_aerial_03", 11), "dirt_aerial_03", lin("#bfa278"), raw=.2)
    wig = s.add(s.mul(s.sub(s.noise(.12, 3, .6, w=1.3), .5), 5.0), s.add(s.mul(s.sub(s.noise(.45, 4, .65, w=2.7), .5), 3.2), s.mul(s.sub(s.noise(1.9, 4, .7, w=4.1), .5), 1.4)))
    soft = s.rng(rd[2], 0, .45, 1.0, .06)                                                 # mud road edges wander; streets & paving stay straight
    e = s.madd(wig, soft, rd[0])
    is_mud = s.rng(rd[2], .05, .35, 1.0, 0.0)
    e_mud = s.madd(s.mul(s.sub(s.noise(.75, 3, .7, w=9.2), .48), 2.2), is_mud, e)
    on = s.mixf(is_mud, s.rng(e, .3, -.3), s.rng(e_mud, 1.1, -.7))
    verge = s.mul(s.mul(s.rng(e_mud, 2.8, .1, 0, .55), s.rng(s.noise(.35, 3, .6, w=6.3), .35, .68)), s.rng(rd[2], 0, .5, 1.0, .2))
    mud_a = s.tint(s.tex("dirt_aerial_02", 8), "dirt_aerial_02", lin("#bfa277"), raw=.2)
    dirt = M(s.rng(s.noise(.25, 3, .65, w=2.1), .38, .65), mud_a, trod)
    gravel = s.tint(s.tex("stony_dirt_path", 5), "stony_dirt_path", lin("#bda47d"), raw=.2)
    dirt = M(s.rng(s.noise(.22, 3, .65, w=3.7), .48, .66, 0, .48), dirt, gravel)
    rut = s.rng(s.math("ABSOLUTE", s.sub(s.madd(s.sub(s.noise(1.8, 3, .6, w=5.1), .5), .22, rd[1]), .4)), .20, .03, 0, .38)
    dirt = M(rut, dirt, s.mix(1.0, dirt, (.68, .60, .52), "MULTIPLY"))
    st_earth = s.tint(s.tex("dry_ground_rocks", 7.5), "dry_ground_rocks", lin("#c5ad84"), raw=.35)
    st_cob = s.tint(s.tex("cobblestone_large_01", 7.0), "cobblestone_large_01", lin("#c4b79d"), raw=.45, gain=1.4)
    street = M(s.rng(s.noise(.38, 3, .7, w=4.4), .46, .66, 0, .65), st_earth, st_cob)
    drain_d = s.madd(s.sub(s.noise(1.5, 3, .6, w=3.1), .5), .12, rd[1])
    street = M(s.mul(s.rng(drain_d, .14, .03, 0, .42), s.rng(s.noise(.35, 3, .6, w=1.7), .35, .65)), street, s.mix(1.0, street, (.62, .57, .5), "MULTIPLY"))
    street = M(s.mul(s.rng(rd[1], .72, .98), s.rng(s.noise(1.6, 3, .7, w=6.1), .48, .72, 0, .38)), street, lin("#8d885f"))
    slabs = s.tint(s.tex("stone_tiles_02", 7.2), "stone_tiles_02", lin("#cfc4ab"), raw=.35, gain=1.9)
    slabs = M(s.rng(s.noise(.28, 3, .6, w=5.8), .4, .68, 0, .55), slabs, st_cob)
    pav = M(s.rng(s.noise(.24, 3, .65, w=3.4), .46, .72, 0, .52), slabs, st_earth)
    slabs = M(s.rng(s.noise(.35, 3, .7, w=8.8), .48, .72, 0, .58), slabs, street)         # earth trodden over the slabs in patches
    rc = M(s.rng(rd[2], .2, .35), dirt, street); rc = M(s.rng(rd[2], .7, .85), rc, slabs)
    paved = s.rng(s.madd(fine, .2, c2[0]), .45, .65)                                       # paving laid by builders: courts, the agora's margins, the sanctuary
    col = M(on, trod, rc); col = M(s.mul(paved, s.sub(1.0, on)), col, pav)
    crown = s.mul(s.rng(s.madd(s.sub(s.noise(1.2, 3, .65, w=7.7), .5), 1.1, rd[1]), .18, -.04, 0, .55), s.rng(rd[2], .1, .3, 1.0, 0.0))   # grass down the middle of a cart road
    a = s.maxf(s.maxf(s.mul(on, s.sub(1.0, crown)), verge), paved)
    hgt = s.add(s.mul(s.noise(.48, 4, .75), .55), s.mul(s.noise(1.5, 4, .7), .45))
    return _finish(s, col, a, rough=.93, bump=.95, height=hgt)

def sea_material():
    s = Sh("sea")
    sd = read_map(s, map_image("m_shore", (SD.astype(np.float32),), True))[0]
    depth = s.madd(s.sub(s.noise(.09, 3, .6), .5), 3.0, s.mul(sd, -1))                   # metres offshore, wandering a little
    col = s.ramp(s.rng(depth, 0, 60), [(0, (.30, .50, .46)), (.05, (.11, .33, .36)), (.16, (.045, .19, .27)), (.45, (.026, .105, .19)), (1, (.018, .07, .14))])
    swell = s.noise(.035, 3, .55, vec=s.mapping(s.pos, (1, 2.6, 1), rot=(0, 0, .35)))
    col = s.mix(s.rng(swell, .35, .75, 0, .22), col, s.mix(1.0, col, (1.25, 1.2, 1.12), "MULTIPLY", clamp=False))
    surf = s.madd(s.sub(s.noise(.35, 4, .65, w=2.2), .5), 1.6, depth)                      # a broken line of foam where the sea meets the land
    foam = s.mul(s.rng(surf, 1.5, .15), s.rng(s.noise(1.9, 3, .7, w=6.1), .38, .62))
    lines = s.mul(s.rng(s.math("SINE", s.madd(s.noise(.07, 2, .5, w=4.0), 9.0, s.mul(depth, .9))), .82, 1.0), s.rng(depth, 9, 2.5, 0, .35))
    col = s.mix(s.maxf(foam, lines), col, (.86, .9, .88))
    nor = s.bump(s.add(s.noise(2.4, 4, .6), s.mul(swell, .6)), .035, .08)
    sh = s.bsdf(col, .2, nor, Specular_IOR_Level=.35)
    return s.surface(s.mix_shader(s.rng(depth, -.3, 1.6, .15, 1.0), s.transparent(), sh))

def finish():
    """Make the terrain mesh (only the part of the grid the picture can show), the covers laid over it, and the sea."""
    slope_y, slope_x = np.gradient(Z, STEP); slope = np.hypot(slope_x, slope_y)
    rock = np.clip((slope - .42) / .4, 0, 1)
    if HILL: rock = np.maximum(rock, CRAG * np.clip(fbm(X, Y, 14, 4, seed=31) * 2.4 + .5, 0, 1) * (P > .1))
    rock = np.kron(rock, np.ones((2, 2), np.float32))[:NM, :NM]; COV["rock"][:] = np.maximum(COV["rock"], rock * (ROAD_D > .5))
    sdm = np.kron(SD, np.ones((2, 2), np.float32))[:NM, :NM]
    beach = np.clip((11 + 5 * fbm(XM, YM, 30, 3, seed=41) - sdm) / 5, 0, 1) * (COV["rock"] < .5)
    COV["sand"][:] = np.maximum(COV["sand"], beach); COV["wet"][:] = np.maximum(COV["wet"], np.clip((1.6 - sdm) / 1.6, 0, 1))
    lim = HALF_VIEW + 34
    keep = (np.abs(X + Y) < lim) & (np.abs(X - Y) < lim + 30)
    idx = np.arange(NX * NX).reshape(NX, NX)
    def grid_mesh(name, mask, dz, material):
        q = mask[:-1, :-1] & mask[:-1, 1:] & mask[1:, 1:] & mask[1:, :-1]
        quads = np.stack([idx[:-1, :-1][q], idx[:-1, 1:][q], idx[1:, 1:][q], idx[1:, :-1][q]], 1)
        if not len(quads): return
        used = np.unique(quads); remap = np.full(NX * NX, -1, np.int64); remap[used] = np.arange(len(used)); quads = remap[quads]
        V = np.stack([X.ravel()[used], Y.ravel()[used], Z.ravel()[used] + dz], 1).astype(np.float32)
        me = bpy.data.meshes.new(name); me.vertices.add(len(V)); me.vertices.foreach_set("co", V.ravel())
        me.loops.add(quads.size); me.loops.foreach_set("vertex_index", quads.ravel().astype(np.int32))
        me.polygons.add(len(quads)); me.polygons.foreach_set("loop_start", (np.arange(len(quads)) * 4).astype(np.int32))
        me.polygons.foreach_set("use_smooth", np.ones(len(quads), bool)); me.update(calc_edges=True)
        me.materials.append(material); ROOT.objects.link(bpy.data.objects.new(name, me))
    def near(A, thr=.02, r=2):
        """Where a cover map is present, on the height grid, widened a little."""
        m = A[::2, ::2] > thr; out = m.copy()
        for dj in range(-r, r + 1):
            for di in range(-r, r + 1): out |= np.roll(np.roll(m, dj, 0), di, 1)
        return out
    grid_mesh("ground", keep, 0.0, ground_material())
    grid_mesh("fields", keep & near(np.maximum(COV["stubble"], np.maximum(COV["plough"], COV["green"]))), .02, field_material())
    grid_mesh("shore", keep & near(COV["sand"]), .03, shore_material())
    grid_mesh("roads", keep & (near(COV["pave"]) | near(-ROAD_D, -5.2, 2)), .045, road_material())
    if SHORE:
        a = lim + 60; me = bpy.data.meshes.new("sea"); me.from_pydata([(-a, -a, 0), (a, -a, 0), (a, a, 0), (-a, a, 0)], [], [[0, 1, 2, 3]])
        me.materials.append(sea_material()); ROOT.objects.link(bpy.data.objects.new("sea", me))
