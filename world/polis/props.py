"""Small things, each made once and instanced: jars, altars, well heads, statues and their bases, stalls, carts, boats."""
import math, random
from . import core, land
from .core import face, mesh, prism, boxr, lathe, cyl, beam, bar, Part, inst, rect, box

def part(name, fn):
    with Part(name) as p: fn()
    return p.mesh
def turned(name, prof, key, n=14):
    return part(name, lambda: lathe(key, 0, 0, prof, n, cap_top=True, cap_bot=False))

AMPH = turned("amphora", [(.02, 0), (.07, .06), (.17, .24), (.2, .42), (.18, .58), (.09, .7), (.055, .74), (.055, .86), (.075, .9)], "clay:#b4683e", 10)
PITHOS = turned("pithos", [(.18, 0), (.42, .25), (.55, .62), (.5, 1.05), (.3, 1.3), (.34, 1.38)], "clay:#a65d38", 12)
HYDRIA = turned("hydria", [(.08, 0), (.16, .12), (.2, .28), (.14, .42), (.07, .5), (.1, .56)], "clay:#8c4a2e", 10)
SACK = turned("sack", [(.18, 0), (.3, .12), (.32, .4), (.2, .62), (.08, .7)], "cloth:#c9b68e", 8)
BASKET = turned("basket", [(.22, 0), (.3, .3), (.33, .42)], "straw:#b99a5a", 10)
HAY = turned("hay", [(2.2, 0), (2.4, .6), (2.2, 1.7), (1.5, 2.8), (.6, 3.5), (.05, 3.8)], "straw:#d1b262", 16)
SHEAF = turned("sheaf", [(.25, 0), (.18, .5), (.32, .95), (.05, 1.1)], "straw:#dcbf6c", 7)
BEEHIVE = turned("beehive", [(.3, 0), (.34, .3), (.2, .55), (.05, .62)], "clay:#b08a62", 10)

def _well():
    lathe("marble:#d6cdb8", 0, 0, [(.5, 0), (.46, .55), (.52, .62), (.52, .7)], 14); cyl("dark", 0, 0, .36, .69, .71, 12)
WELL = part("wellhead", _well)                                                           # a puteal over a cistern's mouth
def _house_altar():
    boxr("marble:#e3dccb", "marble:#e3dccb", 0, 0, .7, .5, 0, .12); boxr("marble:#ece6d8", "marble:#ece6d8", 0, 0, .55, .38, .12, .8); boxr("marble:#e3dccb", "marble:#e3dccb", 0, 0, .68, .48, .8, .9)
HOUSE_ALTAR = part("house_altar", _house_altar)
def _altar():                                                                             # a long altar on its steps, wind-guards at the ends
    boxr("marble:#e2dbc9", "marble:#e9e3d4", 0, 0, 7.6, 4.2, 0, .3); boxr("marble:#e2dbc9", "marble:#e9e3d4", 0, 0, 6.9, 3.5, .3, .6)
    boxr("marble:#ece6d8", "marble:#f0ebdf", 0, .3, 6.0, 2.0, .6, 1.75); boxr("marble:#e2dbc9", "marble:#e9e3d4", 0, .3, 6.3, 2.3, 1.75, 1.9)
    for x in (-2.95, 2.95): boxr("marble:#ece6d8", "marble:#f0ebdf", x, .3, .35, 2.2, 1.9, 2.55)
    cyl("dark:#3a302a", 0, .3, .55, 1.9, 1.96, 12)
ALTAR = part("altar", _altar)
def _figure(key, h=1.9):
    """A draped standing figure: enough of a silhouette to read as a statue from the walls."""
    k = h / 1.9
    lathe(key, 0, 0, [(.26 * k, 0), (.24 * k, .5 * k), (.2 * k, .95 * k), (.24 * k, 1.3 * k), (.25 * k, 1.5 * k), (.1 * k, 1.62 * k)], 10)
    lathe(key, 0, 0, [(.07 * k, 1.6 * k), (.12 * k, 1.7 * k), (.12 * k, 1.82 * k), (.05 * k, 1.9 * k)], 10, cap_top=True)
    beam(key, (.2 * k, 0, 1.45 * k), (.34 * k, .1 * k, 1.0 * k), .055 * k, 6); beam(key, (-.2 * k, 0, 1.45 * k), (-.3 * k, .22 * k, 1.2 * k), .055 * k, 6)
def _statue(metal, base_h=1.2, h=1.9):
    def f():
        boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, .95, .95, 0, .18); boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, .78, .78, .18, base_h); boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, .92, .92, base_h, base_h + .1)
        with core.placed(0, 0, 0, base_h + .1): _figure("bronze" if metal else "marble:#f1ece0", h)
    return f
STATUE_B = part("statue_bronze", _statue(True)); STATUE_M = part("statue_marble", _statue(False))
def _colossus():
    boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 3.4, 3.4, 0, .4); boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, 2.8, 2.8, .4, 2.8); boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 3.1, 3.1, 2.8, 3.05)
    with core.placed(0, 0, 0, 3.05): _figure("bronze", 6.2)
    beam("bronze", (.95, .3, 3.1), (1.0, .3, 10.4), .06, 6)                              # her spear
COLOSSUS = part("colossus", _colossus)
STELE = part("stele", lambda: (boxr("marble:#ddd5c2", "marble:#ddd5c2", 0, 0, .7, .34, 0, .16), boxr("marble:#e9e3d4", "marble:#efe9dc", 0, 0, .52, .16, .16, 1.5)))
HERM = part("herm", lambda: (boxr("marble:#e3dccb", "marble:#e3dccb", 0, 0, .3, .26, 0, 1.45), lathe("marble:#ece6d8", 0, 0, [(.1, 1.45), (.14, 1.55), (.13, 1.7), (.05, 1.78)], 8)))
BASE = part("base", lambda: (boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 1.5, 1.5, 0, .25), boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, 1.25, 1.25, .25, 1.0)))
VOTIVE = part("votive_column", lambda: (boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, .9, .9, 0, .3), lathe("marble:#ece6d8", 0, 0, [(.28, .3), (.24, 4.2), (.36, 4.4)], 12),
                                        boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, .8, .8, 4.4, 4.6), core.STACK[-1].face("bronze", [(-.2, -.2, 4.6), (.2, -.2, 4.6), (0, 0, 5.4)]), core.STACK[-1].face("bronze", [(.2, .2, 4.6), (-.2, .2, 4.6), (0, 0, 5.4)])))
BENCH = part("bench", lambda: (boxr("marble:#e0d8c6", "marble:#e9e3d4", 0, 0, 2.4, .5, .3, .45), boxr("marble:#d8cfbb", None, -.9, 0, .3, .45, 0, .3), boxr("marble:#d8cfbb", None, .9, 0, .3, .45, 0, .3)))
def _exedra():                                                                            # a curved stone bench for sitting and talking
    n = 10
    for k in range(n):
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        for r0, r1, z0, z1 in ((2.0, 2.6, 0, .45), (2.5, 2.8, 0, 1.15)):
            prism("marble:#e0d8c6", "marble:#e9e3d4", [(r0 * math.cos(a0), r0 * math.sin(a0)), (r1 * math.cos(a0), r1 * math.sin(a0)), (r1 * math.cos(a1), r1 * math.sin(a1)), (r0 * math.cos(a1), r0 * math.sin(a1))], z0, z1)
EXEDRA = part("exedra", _exedra)
TABLE = part("table", lambda: (boxr("marble:#e0d8c6", "marble:#e9e3d4", 0, 0, 1.4, .7, .7, .8), boxr("marble:#d8cfbb", None, -.5, 0, .14, .5, 0, .7), boxr("marble:#d8cfbb", None, .5, 0, .14, .5, 0, .7)))
def _stall(c):
    def f():
        for x, y in ((-1.4, -1), (1.4, -1), (-1.4, 1), (1.4, 1)): beam("wood:#6b5032", (x, y, 0), (x, y, 2.4 if y < 0 else 1.95), .055)
        boxr("wood:#8c6a44", "wood:#9d784c", 0, -.5, 2.6, .8, 0, .85)
        face("cloth:" + c, [(-1.65, -1.25, 2.45), (1.65, -1.25, 2.45), (1.65, 1.25, 1.95), (-1.65, 1.25, 1.95)], [(0, 0), (3.3, 0), (3.3, 2.5), (0, 2.5)])
    return f
STALLS = [part("stall%d" % i, _stall(c)) for i, c in enumerate(("#d9ceb4", "#cfc3a4", "#b0563a", "#d4c9ad", "#7d8fa0", "#c8b98f"))]
def _awning(c, w=3.0, d=1.8):
    def f():
        face("cloth:" + c, [(-w / 2, 0, 2.7), (w / 2, 0, 2.7), (w / 2, -d, 2.15), (-w / 2, -d, 2.15)][::-1], [(0, 0), (w, 0), (w, d), (0, d)])
        for x in (-w / 2 + .1, w / 2 - .1): beam("wood:#6b5032", (x, -d + .08, 0), (x, -d + .08, 2.17), .045)
    return f
AWNINGS = [part("awning%d" % i, _awning(c)) for i, c in enumerate(("#d9ceb4", "#cbbf9f", "#a9553c", "#d1c6aa", "#8794a0"))]   # y = 0 at the wall, reaching out toward -y
def _cart():
    boxr("wood:#8c6a44", "wood:#9d784c", 0, 0, 2.4, 1.4, .75, .9)
    for s in (-1, 1):
        boxr("wood:#7d5c3a", "wood:#7d5c3a", 0, s * .68, 2.4, .08, .9, 1.3)
        V = [(.55 * math.cos(k / 12 * 2 * math.pi) - .1, s * .86, .55 + .55 * math.sin(k / 12 * 2 * math.pi)) for k in range(12)]
        face("wood:#5e4329", V if s > 0 else V[::-1]); beam("wood:#7d5c3a", (1.2, s * .5, .85), (3.4, s * .4, .08), .06)
        for k in range(12):
            a0, a1 = k / 12 * 2 * math.pi, (k + 1) / 12 * 2 * math.pi
            face("wood:#4e3722", [(.55 * math.cos(a0) - .1, s * .8, .55 + .55 * math.sin(a0)), (.55 * math.cos(a1) - .1, s * .8, .55 + .55 * math.sin(a1)), (.55 * math.cos(a1) - .1, s * .92, .55 + .55 * math.sin(a1)), (.55 * math.cos(a0) - .1, s * .92, .55 + .55 * math.sin(a0))])
CART = part("cart", _cart)
def _hull(L, B, D, secs, outer, inner, deck_z, rocker=.25, stern=0.0):
    prev = None
    for i in range(secs + 1):
        t = i / secs; x = (t - .5) * L; hw = B / 2 * math.sin(math.pi * min(1, t * 1.03)) ** .6 + .03; sh = rocker * (2 * t - 1) ** 2 + (stern * max(0, t - .85) / .15) ** 2
        sec = [(x, -hw, D + sh), (x, -hw * .88, D * .42), (x, 0, 0), (x, hw * .88, D * .42), (x, hw, D + sh)]
        if prev:
            for k in range(4): face(outer, [prev[k], sec[k], sec[k + 1], prev[k + 1]][::-1])
            face(inner, [(prev[1][0], prev[1][1] * 1.08, deck_z), (sec[1][0], sec[1][1] * 1.08, deck_z), (sec[3][0], sec[3][1] * 1.08, deck_z), (prev[3][0], prev[3][1] * 1.08, deck_z)])
        prev = sec
def _boat():                                                                              # a fishing boat: planked hull, thwarts, a short mast with its yard lowered
    _hull(6.5, 1.9, .8, 14, "wood:#5f4129", "wood:#a08257", .45)
    for xx in (-1.2, .3, 1.6): boxr("wood:#8a6a44", "wood:#8a6a44", xx, 0, .2, 1.5, .62, .7)
    beam("wood:#6b5032", (.2, 0, .5), (.2, 0, 3.4), .06); beam("wood:#6b5032", (-1.9, .25, .95), (2.2, .25, 1.1), .05)
    beam("cloth:#d8cdb2", (-1.6, .32, 1.05), (1.9, .32, 1.2), .12, 6)
BOAT = part("boat", _boat)
def _ship():                                                                              # a round merchantman, sail furled on its yard, steering oars at the stern
    D = 2.3; _hull(16, 5.0, D, 22, "wood:#4a321f", "wood:#a98860", D - .15, .8, 1.5)
    boxr("wood:#7a5a38", "wood:#8f6a42", -5.3, 0, 2.8, 3.0, D - .15, D + 1.0)
    beam("wood:#5b4128", (.8, 0, D), (.8, 0, D + 9.5), .17); beam("wood:#5b4128", (.8, -5.0, D + 8.8), (.8, 5.0, D + 8.8), .1)
    beam("cloth:#d9ceb4", (.95, -4.6, D + 8.55), (.95, 4.6, D + 8.55), .28, 7)
    for s in (-1, 1): beam("wood:#6b4a2c", (-6.6, s * 2.0, D + .6), (-8.2, s * 2.6, -.9), .07); beam("wood:#3a2a1e", (.8, 0, D + 9.3), (7.4 , s * .2, D + 1.0), .02, 4); beam("wood:#3a2a1e", (.8, 0, D + 9.3), (-7.2, s * .2, D + 1.6), .02, 4)
SHIP = part("ship", _ship)
def _rack():                                                                              # a drying rack hung with split fish
    for y in (-2, 2): beam("wood:#6d5236", (0, y, 0), (0, y, 2.2), .07)
    for z in (1.45, 2.1):
        beam("wood:#8a6a48", (0, -2.1, z), (0, 2.1, z), .045)
        for k in range(16): boxr("flat:#bfb49c", "flat:#bfb49c", 0, -1.9 + k * 3.8 / 15, .05, .16, z - .52, z - .02)
RACK = part("rack", _rack)
def _nets():                                                                              # fishing nets hung over a pole to dry
    for x in (-2.2, 2.2): beam("wood:#6d5236", (x, 0, 0), (x, 0, 2.1), .06)
    beam("wood:#8a6a48", (-2.4, 0, 2.1), (2.4, 0, 2.1), .045)
    for s in (-1, 1):
        pts = [((-2.2 + k * 4.4 / 8, 0, 2.1), (-2.2 + k * 4.4 / 8, s * 1.1, .2 + .25 * math.sin(math.pi * k / 8))) for k in range(9)]
        for (a, b), (c, d) in zip(pts, pts[1:]): face("net", [a, c, d, b] if s > 0 else [b, d, c, a])
NETS = part("nets", _nets)
def _woodpile():
    for k in range(5):
        for j in range(4 - k % 2): beam("wood:#7a5634", (-1.2, -.9 + j * .45 + (k % 2) * .22, .12 + k * .22), (1.2, -.9 + j * .45 + (k % 2) * .22, .12 + k * .22), .11, 7)
WOODPILE = part("woodpile", _woodpile)
def _press():                                                                             # a lever press: stone bed, the long beam, its weight stone
    boxr("rubble:#c2b69a", "paving:#cfc5ac", 0, 0, 3.2, 2.6, 0, .5); cyl("flat:#4b2a33", 0, 0, .9, .5, .62, 12)
    bar("wood:#5b3f26", (-2.2, 0, 2.0), (4.6, 0, 1.3), .3, .3)
    for s in (-.4, .4): bar("wood:#5b3f26", (-2.2, s, 0), (-2.2, s, 2.5), .26, .26)
    cyl("rubble:#9b9483", 4.6, 0, .5, 0, .85, 10)
PRESS = part("press", _press)
def _wheel():
    cyl("rubble:#b9ac90", 0, 0, .4, 0, .35, 12); cyl("wood:#6d5236", 0, 0, .45, .35, .42, 14); lathe("clay:#9c7a5a", 0, 0, [(.14, .42), (.2, .6), (.12, .78)], 10)
POTTERS_WHEEL = part("potters_wheel", _wheel)
def _loom():
    for x in (-.8, .8): beam("wood:#6d5236", (x, 0, 0), (x, .25, 1.9), .045)
    beam("wood:#6d5236", (-.9, .25, 1.9), (.9, .25, 1.9), .045); face("cloth:#cdbf9f", [(-.7, .22, 1.85), (.7, .22, 1.85), (.7, .08, .6), (-.7, .08, .6)])
LOOM = part("loom", _loom)

def jars(cx, cy, z, n, r, g, kinds=(AMPH, AMPH, AMPH, PITHOS, HYDRIA), check=True):
    """A cluster of jars on the ground, a few tipped over."""
    for k in range(n):
        a = g.uniform(0, 6.3); d = r * math.sqrt(g.random()); x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        if check and not land.free(x, y): continue
        m = g.choice(kinds); tip = g.random() < .15 and m is not PITHOS
        inst(m, x, y, (land.zt(x, y) if z is None else z) + (.18 if tip else 0), g.uniform(0, 6.3), g.uniform(.9, 1.15), tilt=(g.uniform(1.3, 1.5), 0) if tip else None)
def jar_rows(x0, y0, x1, y1, z, g, gap=.46, kind=AMPH):
    """Amphorae stood in rows, as in a store or a potter's drying yard."""
    y = y0
    while y < y1:
        x = x0
        while x < x1: inst(kind, x + g.uniform(-.04, .04), y, z, g.uniform(0, 6.3), g.uniform(.95, 1.05)); x += gap
        y += gap
