"""Outside the walls: the farm with its granary and tower, the winery among terraced vines, the fishery and the harbour mole,
the potters' quarter, two schools in their groves (the libraries), tombs along the roads out of the gates, and small tilled
plots divided by dry-stone walls. What grows on all this is planted afterwards by plants.py from the lists gathered here."""
import math, random
from . import core, land, arch, props, houses, civic
from .core import S, face, wall, walls, cap, prism, boxr, box, rect, grow, inst, lerp, placed, in_view, centre
from .arch import shed, gable, hip, door, panel, colonnade

GROVES = []        # (polygon, kind, spacing): orchards and sacred groves for plants.py
VINEYARDS = []     # (polygon, angle)
KEEP_CLEAR = []    # polygons nothing wild grows in
PL = S["places"]

def drystone(pts, closed=False, h=.95, gaps=()):
    """A dry-stone field wall along a line, following the ground."""
    P = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / 2.5)); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = -uy * .32, ux * .32
        for k in range(n):
            p, q = (a[0] + ux * L * k / n, a[1] + uy * L * k / n), (a[0] + ux * L * (k + 1) / n, a[1] + uy * L * (k + 1) / n); m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if land.road_dist(*m) < 1.2 or any(math.hypot(m[0] - gx, m[1] - gy) < gr for gx, gy, gr in gaps) or not land.free(*m): continue
            seg = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]; z = land.zt(*m)
            prism("drystone", "drystone", seg, land.zmin(seg) - .3, z + h + .12 * math.sin(k * 1.7 + a[0]))
def compound(R, gate, h=1.9, key="rubble:#b9ad94"):
    """A yard wall round an estate, with a gap for its gate at `gate` (x, y)."""
    P = box(*R)
    for a, b in zip(P, P[1:] + P[:1]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; n = max(1, int(L / 3))
        for k in range(n):
            p, q = (a[0] + ux * L * k / n, a[1] + uy * L * k / n), (a[0] + ux * L * (k + 1) / n, a[1] + uy * L * (k + 1) / n); m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if math.hypot(m[0] - gate[0], m[1] - gate[1]) < 2.6: continue
            seg = [(p[0] + uy * .3, p[1] - ux * .3), (q[0] + uy * .3, q[1] - ux * .3), (q[0] - uy * .3, q[1] + ux * .3), (p[0] - uy * .3, p[1] + ux * .3)]
            prism(key, "paving:#c4b89e", seg, land.zmin(seg) - .4, land.zt(*m) + h)
    for s in (-1, 1):
        d = (0, 1) if abs(gate[0] - R[0]) < .5 or abs(gate[0] - R[2]) < .5 else (1, 0)
        boxr(key, "paving:#c4b89e", gate[0] + d[0] * s * 2.4, gate[1] + d[1] * s * 2.4, .9, .9, land.zt(*gate) - .4, land.zt(*gate) + h + .5)
def pyrgos(x0, y0, x1, y1, h=10.5, z=None, va=.4):
    """A farm tower in squared stone: store below, refuge above, a tiled roof. Such towers stood on Hellenistic farms all over Greece."""
    R = box(x0, y0, x1, y1); z0 = land.pad(R, z, blend=1.0); land.take(R, .5); kw = dict(va=va, vb=z0)
    walls("ashlar:#cdc1a6", R, z0 - 1, z0 + h, zb=0, **kw); hip(x0, y0, x1, y1, z0 + h, 1.2, va, ov=.45)
    door(*houses.EDGE["s"](x0, y0, x1, y1), (x1 - x0) / 2, z0, 1.1, 2.1)
    for sd in "nsew":
        p, q = houses.EDGE[sd](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1])
        panel("dark", p, q, L / 2, .7, z0 + h - 2.2, z0 + h - 1.2, .04); panel("dark", p, q, L / 2, .14, z0 + 4.5, z0 + 5.5, .04)
    return z0

def granary(g):
    """The granary's farm: the long grain store on its ventilated floor, the farmhouse and its tower, the threshing floor."""
    dx, dy = PL["granary"]["door"]; R = (dx, -31.0, dx + 46, 31.0); z = land.zt(dx + 12, 0)
    yard = box(*R); land.paint("earth", yard, 1.0, 2.5); KEEP_CLEAR.append(grow(yard, 2)); compound(R, (dx, dy))
    x0 = dx + 9; z0 = civic.hall(x0, 9.0, x0 + 27, 20.0, 5.6, "x", wk="plaster:#e6dcc4", door_side="s", windows=False, va=.55, blend=2.0)
    for k in range(10):                                                                   # buttress piers, and the vents of the raised floor between them
        xx = x0 + 1.4 + k * 2.7; boxr("rubble:#b9ad94", "paving:#c4b89e", xx, 8.75, .8, .6, z0 - .6, z0 + 4.2)
        if k < 9: panel("dark", (x0, 9.0), (x0 + 27, 9.0), 2.75 + k * 2.7, .9, z0 + .25, z0 + .55, .04)
    walls("rubble:#b9ad94", box(x0 - .15, 8.85, x0 + 27.15, 20.15), z0 - .8, z0 + 1.0)
    houses.house(dx + 6, -27.0, dx + 22, -11.5, g, ("n",), door_side="n"); pyrgos(dx + 23.5, -24.0, dx + 30.5, -17.0)
    tx, ty = dx + 33, -3.5; land.pad(rect(tx, ty, 14, 14), None, blend=3)                # the threshing floor: a paved circle open to the wind
    zt_ = land.zt(tx, ty); N = 28
    face("paving:#cdbf9c", [(tx + 6.3 * math.cos(2 * math.pi * i / N), ty + 6.3 * math.sin(2 * math.pi * i / N), zt_ + .06) for i in range(N)])
    for i in range(N):
        a0, a1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1) / N
        prism("rubble:#b9ad94", "rubble:#b9ad94", [(tx + 6.3 * math.cos(a0), ty + 6.3 * math.sin(a0)), (tx + 6.8 * math.cos(a0), ty + 6.8 * math.sin(a0)), (tx + 6.8 * math.cos(a1), ty + 6.8 * math.sin(a1)), (tx + 6.3 * math.cos(a1), ty + 6.3 * math.sin(a1))], zt_ - .3, zt_ + .3)
    land.take(rect(tx, ty, 14, 14)); inst(props.HAY, tx - 1, ty + 1, zt_, 0, .45)
    for k in range(12): inst(props.SHEAF, tx + 4.6 * math.cos(k * .5), ty + 4.6 * math.sin(k * .5), zt_ + .06, k)
    for x, y in ((dx + 39, 17), (dx + 41, 9)): inst(props.HAY, x, y, land.zt(x, y), g.uniform(0, 6), g.uniform(.85, 1.05)); land.take(rect(x, y, 6, 6))
    inst(props.CART, dx + 6, 5.5, land.zt(dx + 6, 5.5), .5); inst(props.CART, dx + 26, 3.5, land.zt(dx + 26, 3.5), 2.8)
    for k in range(14): inst(props.SACK, dx + 12 + (k % 5) * .62, 7.6 + (k // 5) * .6, land.zt(dx + 12, 7.6), g.uniform(0, 6))
    props.jars(dx + 25, -9, None, 9, 1.6, g, (props.PITHOS,), check=False); inst(props.WELL, dx + 17, -5, land.zt(dx + 17, -5), 0, 1.3)
    for k in range(5): inst(props.BEEHIVE, dx + 37 + k * 1.0, -26.5, land.zt(dx + 37, -26.5))
    land.take(yard)
    return R

def winery(g):
    """The winery: the press-house and its yard of sunk jars, a treading floor, the lever press under a shed; vines on terraces."""
    dx, dy = PL["winery"]["door"]; R = (dx - 42, -26.0, dx, 28.0); yard = box(*R); land.paint("earth", yard, 1.0, 2.5); KEEP_CLEAR.append(grow(yard, 2)); compound(R, (dx, dy))
    z0 = civic.hall(dx - 33, 6.0, dx - 11, 17.0, 4.6, "x", wk="plaster:#e9dfc8", door_side="s", windows=False, va=.3, blend=2.0)
    houses.house(dx - 38, -23.0, dx - 22, -8.0, g, ("n", "e"), door_side="e")
    px, py = dx - 9, -15.5; zp = land.pad(rect(px, py, 11, 9), None, blend=2)             # the press under its open shed
    inst(props.PRESS, px - 1, py, zp, 0)
    for x, y in ((px - 5, py - 3.6), (px + 5, py - 3.6), (px - 5, py + 3.6), (px + 5, py + 3.6)): inst(arch.column("post", 3.0, .1, "wood:#6b5032"), x, y, zp)
    gable(px - 5.3, py - 3.9, px + 5.3, py + 3.9, zp + 3.0, 1.0, "x", .6, key="tile:#a8674a", ov=.3)
    tx, ty = dx - 8, 9.5; zt_ = land.zt(tx, ty)                                           # the treading floor, its spout into a sunk vat
    boxr("rubble:#c2b69a", "paving:#cfc5ac", tx, ty, 4.2, 3.4, zt_ - .3, zt_ + .55); boxr("flat:#4b2a33", "flat:#4b2a33", tx, ty, 3.4, 2.6, zt_ + .5, zt_ + .58)
    inst(props.PITHOS, tx + 2.9, ty, zt_ - .7)
    for i in range(4):                                                                    # the pitheon: store jars sunk to their shoulders in the yard
        for j in range(5): inst(props.PITHOS, dx - 31 + i * 1.7, -3.5 + j * 1.6, land.zt(dx - 31, -3) - .75, g.uniform(0, 6))
    props.jar_rows(dx - 20, 2.0, dx - 14.5, 4.4, land.zt(dx - 17, 3), g); inst(props.CART, dx - 6, 3, land.zt(dx - 6, 3), 1.9); inst(props.WOODPILE, dx - 39, 21, land.zt(dx - 39, 21), .3)
    land.take(yard)
    for P, ang in ((box(dx - 80, -64, dx - 46, 44), 4), (box(dx - 42, 32, dx + 26, 52), 2), (box(dx - 40, -66, dx + 8, -32), -3), (box(dx + 6, -30, dx + 26, 26), 88), (box(dx - 78, 48, dx - 44, 100), 6)):
        Q = [p for p in P]
        VINEYARDS.append((Q, ang))
    return R

def fishery(g):
    """The fishery: the shed and its salting vats, racks of drying fish, nets, boats on the sand; and the harbour's stone mole."""
    dx, dy = PL["fishery"]["door"]
    z0 = civic.hall(-25.0, -130.0, -7.0, -122.5, 3.4, "x", wk="plaster:#e4d9c0", door_side="n", windows=False, va=.7, blend=2.0)
    houses.house(-23.5, -112.0, -9.5, -99.5, g, ("e", "s"), door_side="e")
    land.paint("earth", box(-28, -130, 38, -100), 1.0, 3.0)
    for i in range(3):                                                                    # salting vats: stone tanks of brine sunk in the ground
        for j in range(2):
            cx, cy = 13.0 + i * 6.4, -110.0 + j * 5.6; zv = land.pad(rect(cx, cy, 6.0, 5.2), None, blend=1.5)
            walls("rubble:#c2b69a", rect(cx, cy, 5.4, 4.6), zv - .4, zv + .5); walls("rubble:#c2b69a", rect(cx, cy, 4.6, 3.8), zv - .4, zv + .5, inward=True)
            O, I = rect(cx, cy, 5.4, 4.6), rect(cx, cy, 4.6, 3.8)
            for (a, b), (c, d) in zip(zip(O, O[1:] + O[:1]), zip(I, I[1:] + I[:1])): face("paving:#cfc5ac", [(a[0], a[1], zv + .5), (b[0], b[1], zv + .5), (d[0], d[1], zv + .5), (c[0], c[1], zv + .5)])
            cap("pool:#5d7a74" if (i + j) % 3 else "pool:#7a6a58", I, zv + .3); land.take(rect(cx, cy, 6, 5.2))
    civic.hall(34.5, -113.5, 45.0, -105.5, 3.2, "y", wk="plaster:#e4d9c0", door_side="w", windows=False, va=.5, blend=2.0)        # the store for the filled jars
    props.jar_rows(26, -100.6, 33, -98.8, land.zt(29, -100), g)
    for k in range(6):
        x, y = -34 - k * 4.4, -121 + k * 1.2
        if land.free(x, y, 2): inst(props.RACK, x, y, land.zt(x, y), .25); land.take_disc(x, y, 2.4)
    for x, y, r in ((-2, -131.5, .2), (6, -132.5, -.3), (-40, -133, .5)):
        if land.sd_at(x, y) > 2: inst(props.NETS, x, y, land.zt(x, y), r); land.take_disc(x, y, 2.6)
    for x, y, r in ((-14, -137.5, 1.3), (-21, -138.6, 1.5), (-29, -139.5, 1.1), (30, -134.5, 1.9), (-52, -134.5, .9), (-60, -131, 1.2)):   # boats drawn up on the beach
        yy = y
        while land.sd_at(x, yy) < 2.5 and yy < y + 12: yy += .5
        inst(props.BOAT, x, yy, land.zt(x, yy) + .05, r, tilt=(g.uniform(-.2, .2), 0)); land.take_disc(x, yy, 3.2)
    # the mole: a breakwater of squared blocks run out from the beach and turned along the shore, the harbour in its lee
    M = [(18.0, -136.0), (20.0, -156.0), (4.0, -168.0)]
    for a, b in zip(M, M[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; n = max(1, int(L / 3))
        for k in range(n):
            p, q = (a[0] + ux * L * k / n, a[1] + uy * L * k / n), (a[0] + ux * L * (k + 1) / n, a[1] + uy * L * (k + 1) / n)
            seg = [(p[0] + uy * 2.2, p[1] - ux * 2.2), (q[0] + uy * 2.2, q[1] - ux * 2.2), (q[0] - uy * 2.2, q[1] + ux * 2.2), (p[0] - uy * 2.2, p[1] + ux * 2.2)]
            prism("ashlar:#bdb39c", "paving:#c2b9a4", seg, -6, 1.15 + .04 * (k % 3), zb=0, vb=.2)
            if k % 2 == 0: boxr("ashlar:#bdb39c", "paving:#c2b9a4", p[0] - uy * 1.6, p[1] + ux * 1.6, .5, .5, 1.1, 1.75)
    prism("ashlar:#bdb39c", "paving:#c2b9a4", [(M[1][0] + 2.6 * math.cos(k * math.pi / 5), M[1][1] + 2.6 * math.sin(k * math.pi / 5)) for k in range(10)], -6, 1.2, zb=0, vb=.2)
    ROCKS.append((M, 3.4)); inst(props.SHIP, 6.5, -151.5, -.75, 2.3); inst(props.BOAT, 13, -146, -.28, 1.4); inst(props.BOAT, 9.5, -161.5, -.28, .4); inst(props.BOAT, -18, -150, -.28, 2.6)
    for k in range(7): inst(g.choice((props.AMPH, props.AMPH, props.SACK, props.BASKET)), 18.6 + g.uniform(-.9, .9), -140 - k * 2.0, 1.17, g.uniform(0, 6))
    KEEP_CLEAR.append(box(-66, -142, 48, -98))
ROCKS = []

def pottery(g):
    """The potters' quarter, outside the walls for the smoke's sake: kilns, a drying shed racked with jars, wheels, the clay pit."""
    dx, dy = PL["pottery"]["door"]; ax, ay = PL["pottery"]["at"]
    land.paint("earth", [(dx - 2, dy + 4), (dx - 34, dy + 2), (dx - 36, dy - 24), (dx - 10, dy - 30), (dx + 2, dy - 12)], 1.0, 3.0)
    z0 = civic.hall(ax - 16, ay - 2, ax - 3, ay + 5.5, 3.1, "x", wk="plaster:#e2d6bb", door_side="e", windows=False, va=.75, blend=2.0)
    sx0, sy0, sx1, sy1 = ax - 15, ay - 12.5, ax - 4, ay - 5.5; zs = land.pad(box(sx0, sy0, sx1, sy1), None, blend=2)          # the open drying shed
    for x in (sx0 + .3, (sx0 + sx1) / 2, sx1 - .3):
        for y in (sy0 + .3, sy1 - .3): inst(arch.column("post", 2.6, .09, "wood:#6b5032"), x, y, zs)
    shed(sx0, sy0, sx1, sy1, zs + 2.6, 1.0, "s", .8, key="tile:#a8674a", ov=.3); props.jar_rows(sx0 + .8, sy0 + .9, sx1 - .6, sy1 - .7, zs, g, .52); land.take(box(sx0, sy0, sx1, sy1))
    for kx, ky in ((ax - 24, ay - 6), (ax - 26, ay - 15)):                                # updraught kilns: a stone drum under a clay dome, the stoke-hole to the south
        zk = land.pad(rect(kx, ky, 7, 7), None, blend=2)
        core.lathe("rubble:#a99b80", kx, ky, [(3.0, zk - .3), (3.0, zk + 1.3)], 18, smooth=True, cap_top=False)
        core.lathe("clay:#a98463", kx, ky, [(3.0, zk + 1.3)] + [(3.0 * math.cos(t), zk + 1.3 + 2.0 * math.sin(t)) for t in (.3, .6, .9, 1.2, 1.45)], 18)
        boxr("dark:#2b1a12", "dark:#2b1a12", kx, ky - 3.0, 1.0, .25, zk, zk + 1.0); inst(props.WOODPILE, kx + 4.6, ky - 2.5, land.zt(kx + 4.6, ky - 2.5), g.uniform(0, 3)); land.take(rect(kx, ky, 8, 8))
        land.paint_disc("wet", kx, ky - 4.5, 2.0, .6, 2.0)
    for x, y in ((ax - 2, ay - 14), (ax + 1, ay - 9)): inst(props.POTTERS_WHEEL, x, y, land.zt(x, y))
    pit = [(ax - 33, ay + 2), (ax - 25, ay + 4), (ax - 22, ay - 1), (ax - 30, ay - 4)]; land.pad(pit, land.zt(ax - 28, ay) - .8, blend=2.5, lock=False); land.paint("wet", pit, .9, 1.5); land.paint("plough", pit, 1.0, 1.0)
    props.jars(ax - 8, ay - 17, None, 26, 3.4, g); props.jars(ax - 19, ay - 21, None, 18, 2.6, g); props.jars(ax + 3, ay - 1, None, 9, 1.6, g)
    KEEP_CLEAR.append(box(ax - 38, ay - 28, ax + 8, ay + 9))

def school(door, at, side, g, name):
    """A school in its grove, as the Academy and the Lyceum lay outside Athens: a precinct wall, a stoa to walk and talk in,
    the room where the books are kept, an exedra, an altar of the Muses, herms; plane trees and cypresses."""
    dx, dy = door
    if side == "se": R = (dx + 1.5, dy - 24.0, dx + 27.5, dy + 2.0); gate = (dx + 1.5, dy)
    else: R = (dx - 24.0, dy - 13.0, dx - 1.5, dy + 13.0); gate = (dx - 1.5, dy)
    P = box(*R); z = land.pad(P, None, blend=3.0); land.paint("earth", P, .9, 2.0); KEEP_CLEAR.append(grow(P, 1.5)); compound(R, gate, 1.7, "rubble:#c2b69a")
    x0, y0, x1, y1 = R
    if side == "se":
        civic.stoa(x0 + 4.5, y0 + 1.2, x1 - 1.2, y0 + 7.4, "n", 3.7, z=z, va=.3, blend=0)
        civic.hall(x1 - 9.2, y0 + 9.0, x1 - 1.2, y1 - 2.0, 4.6, "y", wk="plaster:#ece5d5", door_side="w", va=.45, z=z, blend=0)
        inst(props.EXEDRA, x0 + 8, y1 - 4.0, z, math.pi); inst(props.HOUSE_ALTAR, x0 + 9.5, y0 + 13, z, 0, 1.5)
        for k in range(5): inst(g.choice((props.HERM, props.STATUE_M, props.STELE)), x0 + 5.5 + k * 2.6, y0 + 9.2, z, math.pi)
        GROVES.append((box(x0 + 2, y0 + 10, x1 - 11, y1 - 1.5), "school", 7.0))
    else:
        civic.stoa(x0 + 1.2, y0 + 1.2, x0 + 7.4, y1 - 1.2, "e", 3.7, z=z, va=.3, blend=0)
        civic.hall(x0 + 9.0, y1 - 9.5, x1 - 4.0, y1 - 1.2, 4.6, "x", wk="plaster:#ece5d5", door_side="s", va=.45, z=z, blend=0)
        inst(props.EXEDRA, x1 - 5.5, y0 + 4.5, z, math.pi / 2); inst(props.HOUSE_ALTAR, x0 + 13, y0 + 9, z, 0, 1.5)
        for k in range(5): inst(g.choice((props.HERM, props.STATUE_M, props.STELE)), x0 + 9.0, y0 + 3 + k * 2.4, z, -math.pi / 2)
        GROVES.append((box(x0 + 9.5, y0 + 1.5, x1 - 1.5, y1 - 11), "school", 7.0))
    land.take(P)
    GROVES.append((grow(P, 9.0), "sacred", 9.0))

def tombs(g):
    """Roadside tombs outside the gates, as along the Street of Tombs at Athens: stelai, small walled plots, a few fine monuments."""
    for x0, x1, y in ((-100, -140, 0.0), (98, 128, 0.0)):
        n = int(abs(x1 - x0) / 3.2)
        for k in range(n):
            for sd in (-1, 1):
                if g.random() < .45: continue
                x = x0 + (x1 - x0) * (k + g.uniform(.2, .8)) / n; yy = y + sd * g.uniform(5.2, 8.5)
                if not land.free(x, yy, 1.0): continue
                zt_ = land.zt(x, yy); kind = g.random()
                if kind < .55: inst(props.STELE, x, yy, zt_, 0 if sd < 0 else math.pi, g.uniform(.8, 1.2))
                elif kind < .75: inst(props.VOTIVE, x, yy, zt_, 0, .6)
                elif kind < .9:                                                           # a family plot: a low wall of squared stone, stelai on it
                    boxr("ashlar:#cfc4a8", "paving:#cfc6b0", x, yy, 4.2, 2.6, zt_ - .3, zt_ + 1.1)
                    for i in (-1, 0, 1): inst(props.STELE, x + i * 1.2, yy, zt_ + 1.1, 0 if sd < 0 else math.pi, .8)
                else: inst(props.STATUE_M, x, yy, zt_, math.pi / 2 * sd)
                land.take_disc(x, yy, 2.6)
        GROVES.append(([(x0, y - 11), (x1, y - 11), (x1, y + 11), (x0, y + 11)], "tombs", 11.0))

def _natural_field(Q, seed):
    """Give an unwalled tilled plot organically wandering borders and rounded turn-corners."""
    rg = random.Random(seed); pts = []; ph1, ph2 = rg.uniform(0, 6.28), rg.uniform(0, 6.28)
    for idx, (a, b) in enumerate(zip(Q, Q[1:] + Q[:1])):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        nx, ny = dy / max(1e-6, L), -dx / max(1e-6, L); steps = max(5, int(L / 2.0))
        for k in range(steps):
            t = k / steps; fade = math.sin(math.pi * t) ** .55
            wob = fade * (1.15 * math.sin(t * 6.28 + ph1 + idx * 1.7) + .55 * math.sin(t * 12.56 + ph2) + rg.uniform(-.45, .45))
            pts.append((a[0] + dx * t + nx * wob, a[1] + dy * t + ny * wob))
    return core.chaikin(pts, 1)

def fields(g, estates):
    """Small tilled plots east of the town and along the coast road: stubble after the harvest, fallow under the plough, a
    few green with pulse or vegetables; each plot ploughed parallel to its own edges, walled plots neat, open ones natural."""
    def plots(x0, y0, x1, y1, w, depth, ang0):
        y = y0
        while y < y1 - 6:
            d = depth * g.uniform(.75, 1.25); x = x0 + g.uniform(-3, 3)
            while x < x1 - 6:
                ww = w * g.uniform(.7, 1.3); P = [(x + g.uniform(-.8, .8), y + g.uniform(-.8, .8)), (min(x + ww, x1) + g.uniform(-.8, .8), y + g.uniform(-.8, .8)), (min(x + ww, x1) + g.uniform(-.8, .8), min(y + d, y1) + g.uniform(-.8, .8)), (x + g.uniform(-.8, .8), min(y + d, y1) + g.uniform(-.8, .8))]
                cx, cy = centre(P); ok = in_view(cx, cy, 0, 30) and all(land.road_dist(*p) > 5 and land.sd_at(*p) > 16 for p in P + [(cx, cy)])
                ok = ok and not any(core.inpoly(px, py, K) for K in KEEP_CLEAR for px, py in P + [(cx, cy)]) and not (land.HILL and any(core.inpoly(px, py, land.FOOT) for px, py in P))
                if ok:
                    k = g.random(); kind = "stubble" if k < .5 else "plough" if k < .74 else "green" if k < .86 else None
                    Q = grow(P, -1.3)
                    which = g.choice((0, 0, 1)) if kind else 0
                    if kind: _ = g.uniform(-4, 4)
                    walled = g.random() < .5; wall_h = g.uniform(.7, 1.0) if walled else 0.0
                    ux = ((Q[1][0] - Q[0][0] + Q[2][0] - Q[3][0]) * .5, (Q[1][1] - Q[0][1] + Q[2][1] - Q[3][1]) * .5)
                    uy = ((Q[3][0] - Q[0][0] + Q[2][0] - Q[1][0]) * .5, (Q[3][1] - Q[0][1] + Q[2][1] - Q[1][1]) * .5)
                    dir_v = ux if which == 0 else uy
                    angle = math.degrees(math.atan2(dir_v[1], dir_v[0]))
                    if kind:
                        Fp = Q if walled else _natural_field(Q, int(round(cx * 31 + cy * 97)))
                        land.field(Fp, kind, angle, feather=.8 if walled else 2.8); FIELDS.append((Fp, kind))
                    else: GROVES.append((Q, "olive", 8.5))
                    if walled: drystone(P, closed=True, h=wall_h)
                    if kind == "stubble" and g.random() < .5:
                        for _ in range(g.randint(4, 10)):
                            px, py = cx + g.uniform(-ww / 3, ww / 3), cy + g.uniform(-d / 3, d / 3)
                            if core.inpoly(px, py, Q): inst(props.SHEAF, px, py, land.zt(px, py), g.uniform(0, 6))
                x += ww + g.uniform(1.5, 3.5)
            y += d + g.uniform(1.5, 4)
    plots(98, 12, 236, 124, 34, 26, 2); plots(98, -130, 236, -12, 32, 24, -5); plots(-66, -128, -34, -96, 16, 14, 8); plots(46, -128, 78, -96, 16, 14, 4)
    plots(-136, 62, -112, 110, 14, 16, 10); plots(-134, -92, -100, -40, 16, 14, 0)
FIELDS = []

def build():
    g = random.Random(77)
    e1 = granary(g); e2 = winery(g); fishery(g); pottery(g)
    school(PL["southeast library"]["door"], PL["southeast library"]["at"], "se", g, "se"); school(PL["northwest library"]["door"], PL["northwest library"]["at"], "nw", g, "nw")
    tombs(g); fields(g, (e1, e2))
