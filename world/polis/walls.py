"""The fortifications: a Hellenistic circuit in coursed ashlar, with a battlemented wall-walk, two-storey artillery towers under
tiled roofs (as at Aigosthena and Messene), arched gates between flanking towers, and walls climbing the hill to a citadel."""
import math, random
from . import core, land, arch
from .core import S, face, wall, walls, cap, prism, boxr, rect, box, placed, oriented, lerp
from .arch import panel, hip, wface

COURSE = .46
def q(z): return round(z / COURSE) * COURSE
H_WALL, THICK = 7.4, 2.6
RND = random.Random(61)
CIRCUIT = [(-56, 141), (-70, 135), (-83.2, 122), (-83.2, 100), (-85, 78), (-78, 52), (-78, -52), (-52, -78), (52, -78), (78, -52), (78, 52),
           (86, 78), (88, 104), (80, 124), (58, 129.5)]
GATES = [(gx, gy, 2.4) for gx, gy in S["gates"]]
POSTERN = (land.POSTERN[0], land.POSTERN[1], 1.3)

def parapet(a, b, n, ztop, key, va):
    """Breastwork and merlons along the outer edge of a stretch from a to b (n = outward unit normal)."""
    L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    o0, o1 = THICK_NOW[0] / 2, THICK_NOW[0] / 2 - .5
    A, B = (a[0] + n[0] * o0, a[1] + n[1] * o0), (b[0] + n[0] * o0, b[1] + n[1] * o0); C, D = (b[0] + n[0] * o1, b[1] + n[1] * o1), (a[0] + n[0] * o1, a[1] + n[1] * o1)
    prism(key, "paving:#cfc6b0", [A, B, C, D], ztop, ztop + .95, zb=0, va=va, vb=ztop - 6)
    m = max(1, round(L / 2.15))
    for k in range(m):
        t0, t1 = (k + .2) / m * L, (k + .8) / m * L
        P = lambda t, o: (a[0] + ux * t + n[0] * o, a[1] + uy * t + n[1] * o)
        prism(key, "paving:#cfc6b0", [P(t0, o0), P(t1, o0), P(t1, o1), P(t0, o1)], ztop + .95, ztop + 1.8, zb=0, va=va, vb=ztop - 6)
THICK_NOW = [THICK]

def run(pts, h=H_WALL, thick=THICK, gaps=(), abs_top=None, closed=False, key="ashlar", seg=4.6, battlements=True):
    """A curtain wall along a line (outward is to the right of travel), standing on whatever ground it crosses, its top
    stepping in whole courses; `gaps` (x, y, half-width) are left open for gates."""
    THICK_NOW[0] = thick; P = list(pts) + ([pts[0]] if closed else []); u_run = 0.0; o = thick / 2
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; n = (uy, -ux); holes = []
        for gx, gy, half in gaps:
            t = (gx - a[0]) * ux + (gy - a[1]) * uy; d = abs((gx - a[0]) * uy - (gy - a[1]) * ux)
            if d < 2.5 and -half < t < L + half: holes.append((max(0, t - half), min(L, t + half)))
        ts = sorted({0.0, L} | {x for hh in holes for x in hh})
        for t0, t1 in zip(ts, ts[1:]):
            if t1 - t0 < .05 or any(h0 - 1e-6 <= (t0 + t1) / 2 <= h1 + 1e-6 for h0, h1 in holes): continue
            k = max(1, round((t1 - t0) / seg))
            for i in range(k):
                s0, s1 = t0 + (t1 - t0) * i / k, t0 + (t1 - t0) * (i + 1) / k
                pa, pb = (a[0] + ux * s0, a[1] + uy * s0), (a[0] + ux * s1, a[1] + uy * s1)
                A, B = (pa[0] + n[0] * o, pa[1] + n[1] * o), (pb[0] + n[0] * o, pb[1] + n[1] * o); C, D = (pb[0] - n[0] * o, pb[1] - n[1] * o), (pa[0] - n[0] * o, pa[1] - n[1] * o)
                zb = min(land.zt(*p) for p in (A, B, C, D)) - .8
                ztop = abs_top if abs_top is not None else q(land.zt((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2) + h)
                va = RND.random(); kw = dict(va=va, vb=zb + .8)
                wall(key, A, B, zb, ztop, u_run + s0, 0, **kw); wall(key, C, D, zb, ztop, u_run + s0, 0, **kw)
                wall(key, B, C, zb, ztop, 0, 0, **kw); wall(key, D, A, zb, ztop, 0, 0, **kw)
                cap("paving:#cfc6b0", [A, B, C, D], ztop)
                if battlements: parapet(pa, pb, n, ztop, key, va)
                land.take([A, B, C, D], .6)
        u_run += L
    if not closed:
        for v in P[1:-1]:                                                                 # a drum of masonry closes each bend
            zb = land.zt(*v) - 1; ztop = abs_top if abs_top is not None else q(land.zt(*v) + h)
            prism(key, "paving:#cfc6b0", [(v[0] + o * math.cos(k * math.pi / 5), v[1] + o * math.sin(k * math.pi / 5)) for k in range(10)], zb, ztop, zb=0, vb=zb + 1)

def tower(x, y, ux, uy, w=6.6, d=6.6, out=1.5, h=13.4, key="ashlar", abs_base=None, roof=True):
    """A tower astride the wall at (x, y), set forward of it: two storeys of loopholes and shuttered windows under a tiled roof."""
    n = (uy, -ux); cx, cy = x + n[0] * out, y + n[1] * out; ang = math.degrees(math.atan2(uy, ux)); R = rect(cx, cy, w, d, ang)
    zg = land.zt(x, y) if abs_base is None else abs_base; zb = min(land.zmin(R), zg) - 1; ze = q(zg + h); va = RND.random(); kw = dict(va=va, vb=zb + 1)
    with placed(cx, cy, ang):
        B = box(-w / 2, -d / 2, w / 2, d / 2)
        walls(key, B, zb, ze, zb=0, **kw)
        prism(key, key, box(-w / 2 - .12, -d / 2 - .12, w / 2 + .12, d / 2 + .12), q(zg + H_WALL) - .1, q(zg + H_WALL) + .22, zb=0, **kw)     # a string course at the wall-walk
        prism(key, key, box(-w / 2 - .15, -d / 2 - .15, w / 2 + .15, d / 2 + .15), ze - .3, ze, zb=0, **kw)
        for p, q_ in zip(B, B[1:] + B[:1]):
            L = math.hypot(q_[0] - p[0], q_[1] - p[1])
            for t in (L * .28, L * .72):
                panel("glow" if core.NIGHT and RND.random() < .35 else "dark", p, q_, t, .85, ze - 2.6, ze - 1.35, .03)
                panel("wood:#5c452c", p, q_, t, .95, ze - 1.3, ze - 1.18, .22)                 # the shutter, propped open
                panel("dark", p, q_, t, .16, zg + 3.2, zg + 4.4, .03)
            panel("dark", p, q_, L * .5, .16, zg + 8.6, zg + 9.8, .03)
        if roof: hip(-w / 2, -d / 2, w / 2, d / 2, ze, 1.25, va=.25 + .5 * va, ov=.5)
        else: cap("paving:#cfc6b0", B, ze)
    land.take(R, 1.0); TOWERS.append((cx, cy, ze)); return ze

TOWERS = []                                                                              # (x, y, eaves height) of every tower, for the night's watch-fires
def gate(x, y, ux, uy, half=2.4, thick=THICK, spring=3.4, key="ashlar", h=H_WALL, lintel=False, open_in=True, shut=False):
    """The masonry over a gate's passage: a round arch (or a flat lintel for a postern), the wall-walk and battlements above,
    and the leaves swung back against the passage walls."""
    ang = math.degrees(math.atan2(uy, ux)); zg = land.zroute(x, y)[0] if land.zroute(x, y)[1] < 3 else land.zt(x, y); ztop = q(land.zt(x - ux * (half + 1.5), y - uy * (half + 1.5)) + h); r = half; zs = zg + spring; T = thick
    kw = dict(va=RND.random(), vb=zg)
    with placed(x, y, ang):
        n = 14; arc = [(-r + 2 * r * k / n, (zs + math.sqrt(max(0, r * r - (-r + 2 * r * k / n) ** 2))) if not lintel else zs) for k in range(n + 1)]
        for side in (-1, 1):
            yy = side * T / 2
            for (a0, z0), (a1, z1) in zip(arc, arc[1:]):
                oriented(key, [(a0, yy, z0), (a1, yy, z1), (a1, yy, ztop), (a0, yy, ztop)], (0, side, 0), uv=[(a0, z0), (a1, z1), (a1, ztop), (a0, ztop)], **kw)
                if not lintel:                                                            # the voussoirs: a ring of wedge stones standing a little proud
                    k0, k1 = 1 + .55 / r, 1 + .55 / r; y2 = yy + side * .05
                    oriented("ashlar:#bfb49a", [(a0, y2, z0), (a1, y2, z1), (a1 * k1, y2, zs + (z1 - zs) * k1), (a0 * k0, y2, zs + (z0 - zs) * k0)], (0, side, 0),
                             uv=[(a0 * 3, 0), (a1 * 3, 0), (a1 * 3, .45), (a0 * 3, .45)], **kw)
        for (a0, z0), (a1, z1) in zip(arc, arc[1:]):
            oriented(key, [(a0, -T / 2, z0), (a1, -T / 2, z1), (a1, T / 2, z1), (a0, T / 2, z0)], (0, 0, -1), **kw)
        cap("paving:#cfc6b0", box(-r, -T / 2, r, T / 2), ztop)
        dk = "wood:#6b4f32"
        if shut:                                                                          # shut and barred: the leaves fill the arch, iron-bound, a beam across them
            for side in (-1, 1):
                yy = side * (T / 2 - .35)
                for (a0, z0), (a1, z1) in zip(arc, arc[1:]): oriented(dk, [(a0, yy, zg), (a1, yy, zg), (a1, yy, z1), (a0, yy, z0)], (0, side, 0), uv=[(a0, 0), (a1, 0), (a1, z1 - zg), (a0, z0 - zg)])
                for zb_ in (.8, 2.0, 3.2): oriented("flat:#2e2b28", [(-r + .1, yy + side * .03, zg + zb_), (r - .1, yy + side * .03, zg + zb_), (r - .1, yy + side * .03, zg + zb_ + .16), (-r + .1, yy + side * .03, zg + zb_ + .16)], (0, side, 0))
            core.bar("wood:#3e2a18", (-r - .3, T / 2 - .1, zg + 1.5), (r + .3, T / 2 - .1, zg + 1.5), .3, .3)
        for a in (() if shut else (-r + .07, r - .07)):                                   # the leaves, open against the jambs on the town side
            s = 1 if open_in else -1
            oriented(dk, [(a, s * (T / 2 - r + .2), zg), (a, s * (T / 2 + .2), zg), (a, s * (T / 2 + .2), zs + .2), (a, s * (T / 2 - r + .2), zs + .2)], (-a, 0, 0))
    THICK_NOW[0] = thick; pa, pb = (x - ux * r, y - uy * r), (x + ux * r, y + uy * r); parapet(pa, pb, (uy, -ux), ztop, key, kw["va"])

def build():
    hill = land.HILL
    gaps = GATES + ([POSTERN] if hill else [])
    line = CIRCUIT if hill else S["octagon"]
    run(line, gaps=gaps, closed=not hill)
    for gx, gy, half in GATES:                                                            # the three town gates, each between two towers
        ux, uy = (0, 1) if gy == 0 else (1, 0)                                            # along the wall, the country on the right
        if gx < 0: ux, uy = 0, -1
        if gy > 0: ux, uy = -1, 0
        gate(gx, gy, ux, uy, half, shut=core.SIEGE)
        for s in (-1, 1): tower(gx + ux * s * 8.2, gy + uy * s * 8.2, ux, uy, w=7.2, d=7.6, out=1.8, h=14.3)
    def towers_on(a, b, ts, **kw):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        for t in ts: tower(a[0] + ux * L * t, a[1] + uy * L * t, ux, uy, **kw)
    O = S["octagon"]                                                                      # east side first, counter-clockwise
    towers_on(O[0], O[1], (.0, .21, .79, 1.0)); towers_on(O[6], O[7], (.0, .21, .79, 1.0)); towers_on(O[4], O[5], (.0, .21, .79, 1.0))
    if not hill: towers_on(O[2], O[3], (.0, .25, .5, .75, 1.0)); return
    for a, b, ts in ((CIRCUIT[10], CIRCUIT[11], (1.0,)), (CIRCUIT[11], CIRCUIT[12], (1.0,)), (CIRCUIT[12], CIRCUIT[13], (1.0,)),
                     (CIRCUIT[4], CIRCUIT[5], (0.0,)), (CIRCUIT[3], CIRCUIT[4], (0.25,)), (CIRCUIT[1], CIRCUIT[2], (0.0,))):
        towers_on(a, b, ts, w=6.0, d=6.0, h=12.4)
    px, py, ph = POSTERN; gate(px, py, 0, -1, ph, spring=2.5, lintel=True)
    # the citadel: its own wall along the summit's rim, lower because the rock does the rest; open at the propylon and the west gate
    rim = core.grow(land.SUMMIT, 1.2); top = land.TOP
    wy = 114.0; (ax, ay), (bx, by) = rim[-2], rim[-1]; wx = ax + (bx - ax) * (wy - ay) / (by - ay)
    run(rim, thick=2.2, abs_top=q(top + 4.4), closed=True, gaps=[(0, rim[0][1], 7.2), (wx, wy, 1.7)], seg=5.0)
    for i in (2, 3, 4, 5, 6, 7, 8):
        a, b = rim[i - 1], rim[i]; L = math.hypot(b[0] - a[0], b[1] - a[1])
        tower(b[0], b[1], (b[0] - a[0]) / L, (b[1] - a[1]) / L, w=5.6, d=5.6, out=.9, h=9.6, abs_base=top)
    THICK_NOW[0] = 2.2; gate(wx, wy, (bx - ax) / math.hypot(bx - ax, by - ay), (by - ay) / math.hypot(bx - ax, by - ay), 1.7, thick=2.2, spring=2.6, h=4.4, lintel=True)
