"""The town's houses, after Olynthus and Priene: blank walls to the street, rooms round a small court, the main range on the
north side behind a wooden portico (the pastas) so that it faces the winter sun, lower ranges on the other sides, low-pitched
tiled roofs draining into the court. Mud brick on a stone footing, lime-plastered. Every house differs a little."""
import math, random
from . import core, land, arch, props
from .core import face, wall, walls, cap, prism, boxr, box, rect, grow, inst, lerp
from .arch import shed, gable, hip, door, window, panel, wface, column, colonnade

PLASTER = ["plaster", "plaster:#ece4d2", "plaster:#e4d6ba", "plaster:#efe9db", "plaster:#dfcfae", "plaster:#e9dcc6", "plaster:#e6dccb"]
TILE = ["tile", "tile:#a8704f", "tile:#b88360", "tile:#9c6a50", "tile:#b07a58", "tile:#c0936f", "tile:#a37258"]
SHUTTER = ["wood:#5b6f78", "wood:#6b5032", "wood:#4f5f48", "wood:#7a3e2c", "wood:#6b5032"]
EDGE = {"s": lambda x0, y0, x1, y1: ((x0, y0), (x1, y0)), "e": lambda x0, y0, x1, y1: ((x1, y0), (x1, y1)),
        "n": lambda x0, y0, x1, y1: ((x1, y1), (x0, y1)), "w": lambda x0, y0, x1, y1: ((x0, y1), (x0, y0))}
OUT = {"s": (0, -1), "e": (1, 0), "n": (0, 1), "w": (-1, 0)}
ROT = {"s": 0.0, "e": math.pi / 2, "n": math.pi, "w": -math.pi / 2}                      # turns a part whose front faces -y to face that side

def room(key, x0, y0, x1, y1, z0, z1, kw):
    walls(key, box(x0, y0, x1, y1), z0 - .7, z1, zb=z0, **kw)
def openings(x0, y0, x1, y1, side, z, g, n=None, kind="window", shutter=None, w=.55, h=.7, margin=1.0):
    p, q = EDGE[side](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1]); n = max(1, int(L / 3.2)) if n is None else n
    p_win = .3
    if core.SIEGE and kind == "window":
        dist = math.hypot((x0 + x1) / 2, (y0 + y1) / 2)
        p_win = .45 - .33 * max(0.0, min(1.0, (dist - 40.0) / 40.0))
    for i in range(n):
        if kind == "window" and g.random() < .25: continue
        t = margin + (L - 2 * margin) * (i + .5) / n + g.uniform(-.3, .3)
        lit = core.NIGHT and g.random() < (.18 if kind == "door" else p_win)                  # lamplight in a few rooms at night
        if kind == "door": panel("glow" if lit else "dark", p, q, t, w, z, z + h, .04)
        elif lit: panel("glow", p, q, t, w, z, z + h, .05)
        else: window(p, q, t, z, w, h, shutter)
def court_wall(a, b, z0, h, key, kw, tk, tva):
    """A yard wall of plastered mud brick under a coping of tiles."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    if L < .3: return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = uy * .24, -ux * .24
    P = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
    walls(key, P, z0 - .7, z0 + h, zb=z0, **kw)
    cap(tk, grow(P, .08), z0 + h + .04, va=tva, vb=1.0)

def furnish(cx0, cy0, cx1, cy1, z, g, rich=False):
    """What stands in a house court: an altar, the cistern's mouth, storage jars, a loom under the portico, a fig or a vine."""
    w, d = cx1 - cx0, cy1 - cy0
    if w < 2 or d < 2: return
    P = lambda: (g.uniform(cx0 + .7, cx1 - .7), g.uniform(cy0 + .7, cy1 - .7))
    if g.random() < .6: x, y = P(); inst(props.HOUSE_ALTAR, x, y, z, g.choice((0, math.pi / 2)))
    if g.random() < .65: x, y = P(); inst(props.WELL, x, y, z)
    for _ in range(g.randint(0, 4)): x, y = cx0 + .5 + g.random() * .6, g.uniform(cy0 + .5, cy1 - .5); inst(g.choice((props.PITHOS, props.AMPH, props.AMPH, props.HYDRIA)), x, y, z, g.uniform(0, 6))
    if g.random() < .3: inst(props.LOOM, g.uniform(cx0 + 1.2, cx1 - 1.2), cy1 - .5, z, math.pi)
    if g.random() < .25: inst(props.TABLE, *P(), z, g.uniform(0, 3))
    if g.random() < (.5 if rich else .22) and min(w, d) > 4.5: TREES.append(((cx0 + cx1) / 2 + g.uniform(-.8, .8), (cy0 + cy1) / 2 + g.uniform(-.8, .8), z, "court"))
TREES = []                                                                               # trees the houses ask for; plants.py plants them
DOORS = []

def house(x0, y0, x1, y1, g, streets=(), shops=(), z=None, door_side=None, door_at=None):
    """One courtyard house filling its lot. `streets` names the sides that face a street; `shops` those on an avenue."""
    lot = box(x0, y0, x1, y1); W, D = x1 - x0, y1 - y0; zlo = land.zmin(lot); z0 = land.pad(lot, z, blend=0, grow_by=.1); land.take(lot, .3)
    va = g.random(); decay = g.random() ** 2.4; wk = g.choice(PLASTER); tk = g.choice(TILE); tva = g.random(); kw = dict(va=va, vb=decay)
    walls("rubble", grow(lot, .04), min(zlo, z0 - .25) - .35, z0 + .05)
    cap(g.choice(("earth", "earth", "earth:#c9b592", "earth:#b6a68a")), lot, z0 + .03)
    h1 = g.uniform(2.9, 3.3); h2 = h1 + g.uniform(2.5, 2.9)
    if min(W, D) < 7.5 or W * D < 75:                                                    # a small house: one block of rooms and a yard
        if D >= W: bx = (x0, y1 - min(D * .55, 5.5), x1, y1); yard = (x0, y0, x1, bx[1])
        else: bx = (x0, y0, x0 + min(W * .55, 5.5), y1); yard = (bx[2], y0, x1, y1)
        two = g.random() < .35; hh = h2 if two else h1; room(wk, *bx, z0, z0 + hh, kw)
        bw, bd = bx[2] - bx[0], bx[3] - bx[1]
        if g.random() < .5: gable(*bx, z0 + hh, min(bw, bd) / 2 * .32, "x" if bw >= bd else "y", tva, wk, kw, zb=z0, key=tk)
        else: shed(*bx, z0 + hh, min(bw, bd) * .27, "s" if D >= W else "e", tva, wk, kw, zb=z0, key=tk)
        yb = box(*yard)
        for a, b in zip(yb, yb[1:] + yb[:1]): court_wall(a, b, z0, g.uniform(2.0, 2.5), wk, kw, tk, tva)
        openings(*bx, "s" if D >= W else "e", z0, g, 1, "door", w=1.0, h=2.0)
        if two: openings(*bx, "s" if D >= W else "e", z0 + h1 + .9, g, None, "window", g.choice(SHUTTER))
        furnish(yard[0] + .3, yard[1] + .3, yard[2] - .3, yard[3] - .3, z0 + .03, g)
        side = door_side or (streets[0] if streets else "s"); p, q = EDGE[side](*(yard if side in ("s", "e") else bx)); door(p, q, math.hypot(q[0] - p[0], q[1] - p[1]) * g.uniform(.35, .65), z0)
        return z0
    dn = min(g.uniform(4.6, 5.5), D * .4); two = g.random() < .6; hn = h2 if two else h1
    dw = g.uniform(3.3, 4.0) if (W > 9 and g.random() < .8) else 0.0; de = g.uniform(3.3, 4.0) if (W > 9 and g.random() < .6) else 0.0
    if W - dw - de < 4.2: de = 0.0
    if W - dw < 4.2: dw = 0.0
    ds = g.uniform(3.0, 3.6) if (D - dn > 8.5 and g.random() < .5) else 0.0
    cx0, cy0, cx1, cy1 = x0 + dw, y0 + ds, x1 - de, y1 - dn
    # the north range: the main rooms, often with an upper floor; a gable along the street or one slope falling to the court
    nb = (x0, y1 - dn, x1, y1); room(wk, *nb, z0, z0 + hn, kw)
    k = g.random()
    if k < .55: gable(*nb, z0 + hn, dn / 2 * g.uniform(.3, .36), "x", tva, wk, kw, zb=z0, key=tk)
    elif k < .85: shed(*nb, z0 + hn, dn * g.uniform(.24, .3), "s", tva, wk, kw, zb=z0, key=tk)
    else: shed(*nb, z0 + hn, dn * g.uniform(.24, .3), "n", tva, wk, kw, zb=z0, key=tk)
    openings(*nb, "s", z0, g, max(2, int((cx1 - cx0) / 2.6)), "door", w=1.0, h=2.05, margin=dw + .8)
    if two:
        openings(*nb, "s", z0 + h1 + .85, g, None, "window", g.choice(SHUTTER), w=.6, h=.8); openings(*nb, "n", z0 + h1 + 1.0, g, None, "window", None)
        for sd in ("e", "w"):
            if sd in streets: openings(*nb, sd, z0 + h1 + 1.0, g, 1, "window", None)
    # the pastas: a lean-to portico on posts along the main range's south face
    pd = min(2.3, (cy1 - cy0) * .4)
    if cx1 - cx0 > 3 and pd > 1.3:
        zp = z0 + (2.75 if two else h1 - .45)
        shed(cx0, cy1 - pd, cx1, cy1, zp, pd * .22, "s", tva, key=tk, ov=.25, side=0, back=0)
        n = max(2, round((cx1 - cx0) / 2.4)) + 1; stone = g.random() < .3
        colonnade((cx0 + .2, cy1 - pd + .15), (cx1 - .2, cy1 - pd + .15), n, "doric" if stone else "post", zp - z0 - .05, .16 if stone else .085, z0, "marble:#e4dccb" if stone else "wood:#6b5032")
    # the side ranges and the range along the street: stores, workrooms, the men's dining room; one storey
    for dd, bx, low_in, low_out in ((dw, (x0, y0, x0 + dw, y1 - dn), "e", "w"), (de, (x1 - de, y0, x1, y1 - dn), "w", "e")):
        if not dd: continue
        hh = h1 - g.uniform(0, .35); room(wk, *bx, z0, z0 + hh, kw); low = low_in if g.random() < .7 else low_out
        shed(*bx, z0 + hh, dd * g.uniform(.24, .3), low, tva, wk, kw, zb=z0, key=tk)
        openings(*bx, low_in, z0, g, max(1, int((bx[3] - bx[1]) / 4)), "door", w=.95, h=2.0, margin=ds + .8)
    if ds:
        bx = (cx0, y0, cx1, y0 + ds); hh = h1 - g.uniform(0, .3); room(wk, *bx, z0, z0 + hh, kw)
        shed(*bx, z0 + hh, ds * g.uniform(.24, .3), "n" if g.random() < .6 else "s", tva, wk, kw, zb=z0, key=tk)
    else: court_wall((cx0, y0 + .24), (cx1, y0 + .24), z0, g.uniform(2.5, 3.0), wk, kw, tk, tva)
    if not dw: court_wall((x0 + .24, y0), (x0 + .24, cy1), z0, g.uniform(2.5, 3.0), wk, kw, tk, tva)
    if not de: court_wall((x1 - .24, y0), (x1 - .24, cy1), z0, g.uniform(2.5, 3.0), wk, kw, tk, tva)
    furnish(cx0 + .3, cy0 + .3, cx1 - .3, cy1 - pd - .2, z0 + .03, g)
    # the street door, and shop fronts where the house stands on an avenue
    side = door_side or next((s for s in ("s", "e", "w", "n") if s in streets and s not in shops), streets[0] if streets else "s")
    p, q = EDGE[side](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1])
    t = g.uniform(.3, .7) * L if door_at is None else door_at; door(p, q, t, z0, 1.2, 2.2); DOORS.append((side, p, q, t, z0))
    for s in shops:
        p, q = EDGE[s](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1]); n = max(1, int(L / 4.6))
        for i in range(n):
            t = L * (i + .5) / n
            if s == side and abs(t - (door_at or 0)) < 2.2: continue
            panel("rubble:#b9ad94", p, q, t, 2.5, z0, z0 + 2.45, .03); panel("dark", p, q, t, 2.1, z0, z0 + 2.25, .045); panel("wood:#6b5032", p, q, t - .7, .65, z0, z0 + 2.2, .06)
            if g.random() < .7:
                ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L; inst(g.choice(props.AWNINGS), p[0] + ux * t, p[1] + uy * t, z0, ROT[s])
    return z0

def peristyle_house(x0, y0, x1, y1, g, door_side, z=None):
    """A rich man's house, as on Delos: two storeys round a colonnaded court paved in pebble mosaic."""
    lot = box(x0, y0, x1, y1); zlo = land.zmin(lot); z0 = land.pad(lot, z, blend=0, grow_by=.1); land.take(lot, .3)
    va = g.random(); wk = "plaster:#efe8d9"; tk = "tile:#b46c48"; tva = .15; kw = dict(va=va, vb=.03); h1, h2 = 3.5, 6.6; d = 4.0
    walls("rubble", grow(lot, .04), min(zlo, z0 - .25) - .35, z0 + .05)
    cap("paving:#d6cdb8", lot, z0 + .03)
    cx0, cy0, cx1, cy1 = x0 + d, y0 + d, x1 - d, y1 - d
    for bx, low, hh in (((x0, y1 - d, x1, y1), "s", h2), ((x0, y0, x0 + d, y1 - d), "e", h2), ((x1 - d, y0, x1, y1 - d), "w", h1), ((x0 + d, y0, x1 - d, y0 + d), "n", h1)):
        room(wk, *bx, z0, z0 + hh, kw); shed(*bx, z0 + hh, d * .27, low, tva, wk, kw, zb=z0, key=tk)
        openings(*bx, low, z0, g, 2, "door", w=1.1, h=2.2, margin=d + .6 if low in ("s",) else 1.0)
        if hh == h2: openings(*bx, low, z0 + h1 + 1.0, g, 3, "window", "wood:#5b6f78", w=.7, h=.9, margin=d + .5 if low == "s" else 1.0)
    pd = 1.7; zp = z0 + 2.9                                                               # the peristyle: four lean-to porticoes on Doric columns
    for bx, low in (((cx0, cy1 - pd, cx1, cy1), "s"), ((cx0, cy0, cx0 + pd, cy1), "e"), ((cx1 - pd, cy0, cx1, cy1), "w"), ((cx0, cy0, cx1, cy0 + pd), "n")):
        shed(*bx, zp, pd * .2, low, tva, key=tk, ov=.15, side=0, back=0)
    a, b = (cx0 + pd, cy0 + pd), (cx1 - pd, cy1 - pd)
    for p, q in (((a[0], a[1]), (b[0], a[1])), ((b[0], a[1]), (b[0], b[1])), ((b[0], b[1]), (a[0], b[1])), ((a[0], b[1]), (a[0], a[1]))):
        colonnade(p, q, 4, "doric", 2.85, .17, z0, "marble:#efe9dc")[:-1]
    cap("paving:#b9b6ad", box(a[0] + .2, a[1] + .2, b[0] - .2, b[1] - .2), z0 + .05); cap("paving:#e9e4d6", box(a[0] + .7, a[1] + .7, b[0] - .7, b[1] - .7), z0 + .06)
    inst(props.HOUSE_ALTAR, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z0 + .06); inst(props.WELL, a[0] + .9, b[1] - .9, z0 + .06)
    p, q = EDGE[door_side](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1]); door(p, q, L / 2, z0, 1.5, 2.5, frame="marble:#e6dfcf")
    for s in (-1, 1): panel("marble:#efe9dc", p, q, L / 2 + s * 1.15, .3, z0, z0 + 2.9, .12)
    return z0

CORNER = {}                                                                              # a tighter limit for one corner: (east?, north?) -> |x| + |y|
LIMIT = 120.2                                                                            # |x| + |y| inside the corner walls and the lane behind them
def fill(r, g, block, shops=(), z=None, mn=9.0, mx=16.5):
    """Divide a rectangle into house lots and build on each; lots the corner walls cut into are trimmed to fit."""
    x0, y0, x1, y1 = r; w, d = x1 - x0, y1 - y0
    if w > mx or (w >= 2 * mn and g.random() < .55 and w >= d):
        c = x0 + w * g.uniform(.42, .58); fill((x0, y0, c, y1), g, block, shops, z, mn, mx); fill((c, y0, x1, y1), g, block, shops, z, mn, mx); return
    if d > mx or (d >= 2 * mn and g.random() < .55):
        c = y0 + d * g.uniform(.42, .58); fill((x0, y0, x1, c), g, block, shops, z, mn, mx); fill((x0, c, x1, y1), g, block, shops, z, mn, mx); return
    if y0 < 40 or not land.HILL:                                                         # trim against the diagonal walls of the corners
        xo, yo = max(abs(x0), abs(x1)), max(abs(y0), abs(y1)); LIM = CORNER.get((x0 + x1 > 0, y0 + y1 > 0), LIMIT)
        if xo + yo > LIM:
            ax, ay = LIM - yo, LIM - xo                                              # the furthest |x| keeping y, or the furthest |y| keeping x
            keep_x = (ax - min(abs(x0), abs(x1))) * d > (ay - min(abs(y0), abs(y1))) * w
            if keep_x:
                if x1 > 0: x1 = ax
                else: x0 = -ax
            else:
                if y1 > 0 and y0 > 0: y1 = ay
                else: y0 = -ay
            if x1 - x0 < 5 or y1 - y0 < 5: return
    bx0, by0, bx1, by1 = block
    streets = [s for s, on in (("s", abs(y0 - by0) < .1), ("e", abs(x1 - bx1) < .1), ("n", abs(y1 - by1) < .1), ("w", abs(x0 - bx0) < .1)) if on]
    house(x0, y0, x1, y1, g, streets, [s for s in shops if s in streets], z)

def block(r, g, shops=(), reserve=None):
    """A block of houses; `reserve` is a rectangle inside it already built on."""
    if reserve is None: fill(r, g, r, shops); return
    x0, y0, x1, y1 = r; hx0, hy0, hx1, hy1 = reserve
    for q in ((x0, y0, x1, hy0), (x0, hy1, x1, y1), (x0, hy0, hx0, hy1), (hx1, hy0, x1, hy1)):
        if q[2] - q[0] > 5 and q[3] - q[1] > 5: fill(q, g, r, shops)

def terraced(r, g, rows=3):
    """A block on the acropolis' lower slope: rows of small houses on terraces held by rubble walls, as in Priene's upper town."""
    x0, y0, x1, y1 = r
    for k in range(rows):
        ya, yb = lerp(y0, y1, k / rows), lerp(y0, y1, (k + 1) / rows) - .9             # a stepped lane's width between the rows
        zf = land.zt((x0 + x1) / 2, ya); zt_ = land.zt((x0 + x1) / 2, (ya + yb) / 2 + .8)
        fill((x0, ya, x1, yb), g, (x0, ya, x1, yb), (), zt_, mn=7.5, mx=12.5)
        walls("rubble:#b3a78e", box(x0 - .25, ya - .45, x1 + .25, ya + .1), zf - 1.0, zt_ + .1)   # the terrace's retaining wall
