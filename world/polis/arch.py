"""Architectural pieces every builder shares: tiled roofs, columns and entablatures, doors and windows, steps.

Roofs are built in real tiles: a pan surface whose courses the material draws, and a raised rib for every row of cover tiles."""
import math, random
from mathutils import Vector
from . import core
from .core import face, mesh, wall, walls, cap, prism, boxr, lathe, cyl, beam, bar, rect, box, ccw, area, centre, Part, inst, vnorm, oriented, lerp

TILE_W = .88
def wface(key, pts, zb=0.0, **kw):
    """A wall face of any outline: UVs are metres along it and metres above zb."""
    x0, y0 = pts[0][0], pts[0][1]
    face(key, pts, [(math.hypot(p[0] - x0, p[1] - y0), p[2] - zb) for p in pts], **kw)

def tiles(pts, va=0.0, key="tile", ribs=True, fascia=.14, pitch=TILE_W):
    """A roof face in tiles. pts are its corners in space; the first edge is the eave."""
    p0 = Vector(pts[0]); e = (Vector(pts[1]) - p0).normalized(); n = vnorm(pts).normalized()
    if n.z < 0: n = -n
    s_ = n.cross(e); c = sum((Vector(p) for p in pts), Vector()) / len(pts)
    if (c - p0).dot(s_) < 0: s_ = -s_
    P2 = [((Vector(p) - p0).dot(e), (Vector(p) - p0).dot(s_)) for p in pts]
    W = lambda a, b, h=0.0: tuple(p0 + e * a + s_ * b + n * h)
    f = [W(a, b) for a, b in P2]; uv = list(P2)
    if vnorm(f).dot(n) < 0: f, uv = f[::-1], uv[::-1]
    face(key, f, uv, va=va, vb=0.0)
    if fascia:                                                                           # the eave's thickness: a shadowed edge under the lowest course
        a0, a1 = P2[0][0], P2[1][0]
        face(key, [W(a0, 0), W(a1, 0), tuple(Vector(W(a1, .06)) - Vector((0, 0, fascia))), tuple(Vector(W(a0, .06)) - Vector((0, 0, fascia)))], [(a0, 0), (a1, 0), (a1, .01), (a0, .01)], va=va, vb=0.0)
    if not ribs: return
    amin, amax = min(a for a, _ in P2), max(a for a, _ in P2); hw, hh, tw = .14, .12, .06
    k = max(1, round((amax - amin) / pitch)); step = (amax - amin) / k; a = amin + step / 2
    while a < amax - .1:
        bs = []
        for (a1, b1), (a2, b2) in zip(P2, P2[1:] + P2[:1]):
            if (a1 - a) * (a2 - a) <= 0 and a1 != a2: bs.append(b1 + (b2 - b1) * (a - a1) / (a2 - a1))
        if len(bs) >= 2 and max(bs) - min(bs) > .45:
            b0, b1 = min(bs) - .03, max(bs) - .02
            L0, L1, R0, R1 = W(a - hw, b0), W(a - hw, b1), W(a + hw, b0), W(a + hw, b1)
            TL0, TL1, TR0, TR1 = W(a - tw, b0, hh), W(a - tw, b1, hh), W(a + tw, b0, hh), W(a + tw, b1, hh)
            face(key, [L0, TL0, TL1, L1], [(a - hw, b0), (a - tw, b0), (a - tw, b1), (a - hw, b1)], va=va, vb=1.0)
            face(key, [TL0, TR0, TR1, TL1], [(a - tw, b0), (a + tw, b0), (a + tw, b1), (a - tw, b1)], va=va, vb=1.0)
            face(key, [TR0, R0, R1, TR1], [(a + tw, b0), (a + hw, b0), (a + hw, b1), (a + tw, b1)], va=va, vb=1.0)
            face(key, [L0, R0, TR0, TL0], [(a - hw, b0), (a + hw, b0), (a + tw, b0), (a - tw, b0)], va=va, vb=0.0)
        a += step
def ridge(p, q, va=0.0, key="tile", r=.19):
    """A line of cover tiles along a ridge or a hip."""
    p, q = Vector(p), Vector(q); ax = (q - p).normalized(); side = ax.cross(Vector((0, 0, 1))).normalized(); up = side.cross(ax)
    L = (q - p).length; sec = [(-r, -.02), (-r * .5, r * .7), (r * .5, r * .7), (r, -.02)]
    for (s0, h0), (s1, h1) in zip(sec, sec[1:]):
        face(key, [tuple(p + side * s0 + up * h0), tuple(p + side * s1 + up * h1), tuple(q + side * s1 + up * h1), tuple(q + side * s0 + up * h0)],
             [(0, 0), (.3, 0), (.3, L), (0, L)], va=va, vb=1.0)

def _sides(x0, y0, x1, y1, low):
    """A rectangle's corners, counter-clockwise, starting with the side named `low` ('s', 'n', 'e' or 'w')."""
    return {"s": [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "n": [(x1, y1), (x0, y1), (x0, y0), (x1, y0)],
            "e": [(x1, y0), (x1, y1), (x0, y1), (x0, y0)], "w": [(x0, y1), (x0, y0), (x1, y0), (x1, y1)]}[low]
def shed(x0, y0, x1, y1, z, rise, low, va=0.0, wk=None, wkw=None, ov=.4, side=.15, back=.15, zb=None, key="tile", ribs=True):
    """A single-pitch roof over a rectangle, its eave on the `low` side at height z, climbing `rise` to the far side.
    With wk it also builds the wall above z that the slope leaves open: the back wall and the two sloping side walls."""
    A, B, C, D = _sides(x0, y0, x1, y1, low); depth = math.hypot(D[0] - A[0], D[1] - A[1]); sl = rise / depth
    u = ((B[0] - A[0]) / math.hypot(B[0] - A[0], B[1] - A[1]), (B[1] - A[1]) / math.hypot(B[0] - A[0], B[1] - A[1])); v = ((D[0] - A[0]) / depth, (D[1] - A[1]) / depth)
    P = lambda p, du, dv: (p[0] + u[0] * du + v[0] * dv, p[1] + u[1] * du + v[1] * dv, z + ((p[0] - A[0]) * v[0] + (p[1] - A[1]) * v[1] + dv) * sl + .03)
    tiles([P(A, -side, -ov), P(B, side, -ov), P(C, side, back), P(D, -side, back)], va, key, ribs)
    if wk:
        kw = wkw or {}; zb = z if zb is None else zb; zh = z + rise
        wface(wk, [(C[0], C[1], z), (D[0], D[1], z), (D[0], D[1], zh), (C[0], C[1], zh)], zb, **kw)
        wface(wk, [(B[0], B[1], z), (C[0], C[1], z), (C[0], C[1], zh)], zb, **kw); wface(wk, [(D[0], D[1], z), (A[0], A[1], z), (D[0], D[1], zh)], zb, **kw)
def gable(x0, y0, x1, y1, z, rise, axis, va=0.0, wk=None, wkw=None, ov=.4, rake=.2, zb=None, key="tile", ribs=True, ridge_tiles=True):
    """A two-pitch roof over a rectangle, its ridge along `axis` ('x' or 'y'); with wk, the two gable walls above z."""
    kw = wkw or {}; zb = z if zb is None else zb
    if axis == "x":
        cy = (y0 + y1) / 2; d = cy - y0; sl = rise / d; ze = z - ov * sl + .03; zr = z + rise + .03
        tiles([(x0 - rake, y0 - ov, ze), (x1 + rake, y0 - ov, ze), (x1 + rake, cy, zr), (x0 - rake, cy, zr)], va, key, ribs)
        tiles([(x1 + rake, y1 + ov, ze), (x0 - rake, y1 + ov, ze), (x0 - rake, cy, zr), (x1 + rake, cy, zr)], va, key, ribs)
        if ridge_tiles: ridge((x0 - rake, cy, zr), (x1 + rake, cy, zr), va, key)
        if wk:
            wface(wk, [(x1, y0, z), (x1, y1, z), (x1, cy, z + rise)], zb, **kw); wface(wk, [(x0, y1, z), (x0, y0, z), (x0, cy, z + rise)], zb, **kw)
    else:
        cx = (x0 + x1) / 2; d = cx - x0; sl = rise / d; ze = z - ov * sl + .03; zr = z + rise + .03
        tiles([(x0 - ov, y1 + rake, ze), (x0 - ov, y0 - rake, ze), (cx, y0 - rake, zr), (cx, y1 + rake, zr)], va, key, ribs)
        tiles([(x1 + ov, y0 - rake, ze), (x1 + ov, y1 + rake, ze), (cx, y1 + rake, zr), (cx, y0 - rake, zr)], va, key, ribs)
        if ridge_tiles: ridge((cx, y0 - rake, zr), (cx, y1 + rake, zr), va, key)
        if wk:
            wface(wk, [(x0, y0, z), (x1, y0, z), (cx, y0, z + rise)], zb, **kw); wface(wk, [(x1, y1, z), (x0, y1, z), (cx, y1, z + rise)], zb, **kw)
def hip(x0, y0, x1, y1, z, rise, va=0.0, ov=.4, key="tile", ribs=True):
    """A hipped roof over a rectangle (a pyramid over a square)."""
    x0, y0, x1, y1 = x0 - ov, y0 - ov, x1 + ov, y1 + ov; w, d = x1 - x0, y1 - y0; h = min(w, d) / 2; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; zr = z + rise
    ra, rb = ((x0 + h, cy, zr), (x1 - h, cy, zr)) if w >= d else ((cx, y0 + h, zr), (cx, y1 - h, zr))
    c = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    if w >= d:
        tiles([c[0], c[1], rb, ra], va, key, ribs); tiles([c[2], c[3], ra, rb], va, key, ribs); tiles([c[1], c[2], rb], va, key, ribs); tiles([c[3], c[0], ra], va, key, ribs)
        for a, b in ((c[0], ra), (c[3], ra), (c[1], rb), (c[2], rb)): ridge(a, b, va, key, .18)
    else:
        tiles([c[1], c[2], rb, ra], va, key, ribs); tiles([c[3], c[0], ra, rb], va, key, ribs); tiles([c[0], c[1], ra], va, key, ribs); tiles([c[2], c[3], rb], va, key, ribs)
        for a, b in ((c[0], ra), (c[1], ra), (c[2], rb), (c[3], rb)): ridge(a, b, va, key, .18)
    if math.hypot(ra[0] - rb[0], ra[1] - rb[1]) > .3: ridge(ra, rb, va, key)

# ---------------------------------------------------------------- openings in walls
def _at(p, q, t, out):
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    return p[0] + ux * t + uy * out, p[1] + uy * t - ux * out, ux, uy
def panel(key, p, q, t, w, z0, z1, out=.03, **kw):
    """A flat panel on a wall from p to q (the wall faces right of that direction), centred t metres along it."""
    cx, cy, ux, uy = _at(p, q, t, out); hw = w / 2
    face(key, [(cx - ux * hw, cy - uy * hw, z0), (cx + ux * hw, cy + uy * hw, z0), (cx + ux * hw, cy + uy * hw, z1), (cx - ux * hw, cy - uy * hw, z1)],
         [(0, 0), (w, 0), (w, z1 - z0), (0, z1 - z0)], **kw)
def door(p, q, t, z, w=1.15, h=2.15, leaf="wood:#5a4028", frame="rubble:#b9ad94", ajar=False):
    """A doorway: stone jambs and lintel, the dark of the passage, and its wooden leaves."""
    panel(frame, p, q, t, w + .44, z, z + h + .28, .035)
    panel("dark", p, q, t, w, z, z + h, .05)
    if ajar: panel(leaf, p, q, t - w * .27, w * .42, z, z + h, .065)
    else: panel(leaf, p, q, t - w * .252, w * .485, z + .03, z + h - .02, .065); panel(leaf, p, q, t + w * .252, w * .485, z + .03, z + h - .02, .065)
def window(p, q, t, z, w=.55, h=.7, shutter=None, frame=None):
    """A small window, high in the wall; with shutters where it lights an upper room."""
    if frame: panel(frame, p, q, t, w + .24, z - .1, z + h + .12, .03)
    panel("dark", p, q, t, w, z, z + h, .045)
    if shutter:
        for s in (-1, 1): panel(shutter, p, q, t + s * (w * .5 + w * .26), w * .5, z, z + h, .06)

# ---------------------------------------------------------------- the orders
COLS = {}
def column(order, h, r, key="marble"):
    """A column mesh (made once per size): a Doric shaft with echinus and abacus, an Ionic one on its base under a volute
    capital, or a plain timber post on a stone base."""
    k = (order, round(h, 2), round(r, 3), key)
    if k in COLS: return COLS[k]
    with Part("col_%s_%g_%g" % (order, h, r)) as p:
        if order == "doric":
            hs = h - .62 * r; n = 8
            prof = [(r * (1 - .2 * (i / n) ** 1.6), hs * i / n) for i in range(n + 1)]
            prof += [(r * .82, hs + .04 * r), (r * 1.02, hs + .16 * r), (r * 1.2, hs + .3 * r)]
            lathe(key, 0, 0, prof, 16)
            boxr(key, key, 0, 0, 2.5 * r, 2.5 * r, hs + .3 * r, h)
        elif order == "ionic":
            hb = .5 * r; hs = h - .7 * r; n = 8
            lathe(key, 0, 0, [(r * 1.38, 0), (r * 1.4, hb * .3), (r * 1.18, hb * .5), (r * 1.3, hb * .75), (r * 1.02, hb)], 16)
            lathe(key, 0, 0, [(r * (1 - .14 * (i / n) ** 1.5), hb + (hs - hb) * i / n) for i in range(n + 1)], 16)
            boxr(key, key, 0, 0, 2.9 * r, 2.0 * r, hs, hs + .42 * r)
            for sx in (-1, 1): beam(key, (sx * 1.25 * r, -r, hs + .2 * r), (sx * 1.25 * r, r, hs + .2 * r), .34 * r, 10)
            boxr(key, key, 0, 0, 2.3 * r, 2.3 * r, hs + .42 * r, h)
        else:                                                                             # a timber post on a stone base
            boxr("rubble:#b9ad94", "rubble:#b9ad94", 0, 0, r * 3.2, r * 3.2, 0, .18)
            boxr(key, key, 0, 0, r * 2, r * 2, .18, h - .14); boxr(key, key, 0, 0, r * 4.4, r * 2.4, h - .14, h)
    COLS[k] = p.mesh; return p.mesh
def colonnade(p, q, n, order, h, r, z, key="marble", ends=True, rot=None):
    """n columns evenly from plan point p to q."""
    me = column(order, h, r, key); ang = math.atan2(q[1] - p[1], q[0] - p[0]) if rot is None else rot; out = []
    for i in range(n):
        if not ends and i in (0, n - 1): continue
        t = i / (n - 1) if n > 1 else .5; x, y = lerp(p[0], q[0], t), lerp(p[1], q[1], t); inst(me, x, y, z, ang); out.append((x, y))
    return out
def entablature(pts, z, hc, order="doric", key="marble", over=.0):
    """Architrave, frieze and cornice round a plan outline, scaled to columns hc high. Returns the height of its top."""
    ha, hf, hk = hc * .11, hc * .11, hc * .05; P = ccw(pts)
    prism(key, None, P, z, z + ha)
    walls("frieze" if order == "doric" else key, P, z + ha, z + ha + hf)
    prism(key, key, core.grow(P, hc * .06 + over), z + ha + hf, z + ha + hf + hk)
    return z + ha + hf + hk
def krepis(x0, y0, x1, y1, z_ground, z_top, steps=3, tread=.38, key="marble", top="paving:#d9d1bf"):
    """The stepped platform a temple or stoa stands on: its top (the stylobate) at z_top."""
    rise = min(.34, (z_top - z_ground) / steps) if z_top > z_ground else .3
    for i in range(steps):
        g = (steps - 1 - i) * tread; zt_ = z_top - (steps - 1 - i) * rise
        prism(key, top if i == steps - 1 else key, box(x0 - g, y0 - g, x1 + g, y1 + g), min(z_ground, zt_ - rise) - .4 if i == 0 else zt_ - rise, zt_)
def flight(x0, y0, x1, y1, z0, z1, up, key="marble", side=None):
    """Steps filling a rectangle, climbing from z0 to z1 toward `up` ('n', 's', 'e' or 'w')."""
    n = max(1, round(abs(z1 - z0) / .19))
    for i in range(n):
        a, b = i / n, 1.0
        zt_ = z0 + (z1 - z0) * (i + 1) / n
        if up == "n": r = box(x0, lerp(y0, y1, a), x1, y1)
        elif up == "s": r = box(x0, y0, x1, lerp(y1, y0, a))
        elif up == "e": r = box(lerp(x0, x1, a), y0, x1, y1)
        else: r = box(x0, y0, lerp(x1, x0, a), y1)
        prism(side or key, key, r, z0 - .3 if i == 0 else zt_ - (z1 - z0) / n, zt_)
