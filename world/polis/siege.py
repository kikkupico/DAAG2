"""The siege, by night. The model is Philip V before Phthiotic Thebes (Polybius 5.99): the army in separate camps round the
town, "the ground between the camps secured by a trench and a double palisade, with wooden towers at every hundred feet".
The messengers' ring road runs between the two palisades. Against the walls stand the engines of a Hellenistic siege: a wheeled
tower (helepolis), a battery of torsion stone-throwers behind wicker mantlets, and a mound with a ram under its tortoise
(as Polybius describes at Echinous, 9.41). Inside, the gates are barred and the defenders are raising a second wall behind
the threatened corner. No people: watch-fires, torches and a few lamps stand in for them."""
import bpy, math, random
from . import core, land, arch, props, houses, walls, civic
from .core import S, ROOT, face, wall, walls as wallsf, cap, prism, boxr, box, rect, grow, inst, lerp, placed, beam, bar, lathe, cyl, Part, centre, along, inpoly
from .arch import panel

OCT = [tuple(p) for p in S["octagon"]]
D_IN, D_OUT, D_ROAD = 27.5, 52.5, 40.0                                                   # the two palisades and the road between, metres out from the town wall's line
LIGHTS = []                                                                              # (x, y, z, watts, kind)
CLEAR = []                                                                               # polygons kept clear of trees and scrub
STUMPS = []
WOOD, DARKWOOD, HIDE = "wood:#6a5239", "wood:#4d3a28", "canvas:#5c4a3a"

def part(name, fn):
    with Part(name) as p: fn()
    return p.mesh
# ---------------------------------------------------------------- timber works
def _panel(seed):
    def f():
        g = random.Random(seed); n = 9
        for k in range(n):
            x = -1.2 + 2.4 * (k + .5) / n; h = g.uniform(2.9, 3.5); r = g.uniform(.1, .135); y = g.uniform(-.04, .04)
            lathe(WOOD if k % 3 else DARKWOOD, x, y, [(r, -.5), (r, h - .35), (.02, h)], 5, cap_top=False)
        bar(DARKWOOD, (-1.2, .16, 1.9), (1.2, .16, 1.9), .1, .12)
    return f
PANELS = [part("palisade%d" % i, _panel(i)) for i in range(4)]
def _watchtower():
    for x, y in ((-1.5, -1.5), (1.5, -1.5), (1.5, 1.5), (-1.5, 1.5)): bar(DARKWOOD, (x * 1.2, y * 1.2, -.3), (x, y, 6.6), .24, .24)
    for z in (2.2, 4.4, 6.5):
        for a, b in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            k = 1.2 - .2 * z / 6.6; bar(WOOD, (a[0] * 1.5 * k, a[1] * 1.5 * k, z), (b[0] * 1.5 * k, b[1] * 1.5 * k, z), .14, .14)
            if z < 6: bar(WOOD, (a[0] * 1.5 * k, a[1] * 1.5 * k, z - 2.1), (b[0] * 1.5 * k, b[1] * 1.5 * k, z), .1, .1)
    boxr(WOOD, "wood:#7a6040", 0, 0, 3.8, 3.8, 6.5, 6.7)
    for a, b in (((-1.9, -1.9), (1.9, -1.9)), ((1.9, -1.9), (1.9, 1.9)), ((1.9, 1.9), (-1.9, 1.9)), ((-1.9, 1.9), (-1.9, -1.9))):       # a breastwork of wicker
        wall("straw:#8f7a52", a, b, 6.7, 7.9); wall("straw:#8f7a52", b, a, 6.7, 7.9)
    for x, y in ((-1.8, -1.8), (1.8, -1.8), (1.8, 1.8), (-1.8, 1.8)): bar(DARKWOOD, (x, y, 6.7), (x, y, 9.0), .14, .14)
    for a, b in (((-2.3, -2.3), (2.3, -2.3)), ((2.3, -2.3), (2.3, 2.3)), ((2.3, 2.3), (-2.3, 2.3)), ((-2.3, 2.3), (-2.3, -2.3))): face(HIDE, [(a[0], a[1], 8.9), (b[0], b[1], 8.9), (0, 0, 9.9)])
    for k in range(14): bar(WOOD, (-.35, -1.75, .3 + k * .46), (.35, -1.75, .3 + k * .46), .06, .06)
    for sx in (-.35, .35): bar(WOOD, (sx, -2.3, 0), (sx, -1.6, 6.6), .08, .08)
WATCH = part("watchtower", _watchtower)
def tent(name, w, l, wall_h, ridge, col, porch=0.0, trim=None):
    """A ridge tent, its length along y and its door at the -y end."""
    def f():
        x0, x1, y0, y1 = -w / 2, w / 2, -l / 2, l / 2; k = "canvas:" + col
        for sx in (-1, 1):
            face(k, [(sx * x1, y0, 0), (sx * x1, y1, 0), (sx * x1, y1, wall_h), (sx * x1, y0, wall_h)][::sx])
            face(k, [(sx * (x1 + .12), y0 - .1, wall_h - .05), (sx * (x1 + .12), y1 + .1, wall_h - .05), (0, y1 + .1, ridge), (0, y0 - .1, ridge)][::sx])
            if trim: face("canvas:" + trim, [(sx * (x1 + .14), y0 - .12, wall_h - .08), (sx * (x1 + .14), y1 + .12, wall_h - .08), (sx * (x1 * .8), y1 + .12, wall_h + (ridge - wall_h) * .22), (sx * (x1 * .8), y0 - .12, wall_h + (ridge - wall_h) * .22)][::sx])
        for yy, sg in ((y0, -1), (y1, 1)): face(k, [(x0, yy, 0), (x1, yy, 0), (x1, yy, wall_h), (0, yy, ridge), (x0, yy, wall_h)][::-sg])
        face("dark:#1d1712", [(-w * .16, y0 - .02, 0), (w * .16, y0 - .02, 0), (w * .16, y0 - .02, wall_h * 1.15), (0, y0 - .02, ridge * .8), (-w * .16, y0 - .02, wall_h * 1.15)])
        for yy in (y0 - .15, y1 + .15): beam(DARKWOOD, (0, yy, 0), (0, yy, ridge + .3), .05, 5)
        if porch:
            face(k, [(x0 * .8, y0, ridge * .8), (x1 * .8, y0, ridge * .8), (x1 * .8, y0 - porch, wall_h + .2), (x0 * .8, y0 - porch, wall_h + .2)][::-1])
            for sx in (x0 * .8, x1 * .8): beam(DARKWOOD, (sx, y0 - porch, 0), (sx, y0 - porch, wall_h + .25), .05, 5)
    return part(name, f)
TENTS = [tent("tent%d" % i, w, l, wh, r, c) for i, (w, l, wh, r, c) in enumerate(((4.6, 6.0, 1.0, 2.7, "#c9bb9b"), (4.2, 5.4, .9, 2.5, "#b9a888"), (5.0, 6.4, 1.1, 2.9, "#a8946f"), (4.4, 5.8, 1.0, 2.6, "#8d7a5e")))]
OFFICER = tent("tent_officer", 5.6, 7.4, 1.5, 3.4, "#cfc2a4", porch=2.0)
PAVILION = tent("pavilion", 8.4, 11.5, 2.2, 4.8, "#d8ccb0", porch=3.2, trim="#7d2a2a")
def _arms():                                                                              # sarissas stacked in a cone, shields leaning round its foot
    for k in range(10):
        a = k * .63; beam("wood:#8a744e", (.75 * math.cos(a), .75 * math.sin(a), 0), (.1 * math.cos(a + 2), .1 * math.sin(a + 2), 4.9), .035, 4)
    for k in range(6):
        a = k * 1.05 + .3; c = (1.05 * math.cos(a), 1.05 * math.sin(a)); tx, ty = -math.sin(a), math.cos(a)
        face("bronze", [(c[0] + .36 * tx * math.cos(t) - .12 * math.cos(a) * math.sin(t), c[1] + .36 * ty * math.cos(t) - .12 * math.sin(a) * math.sin(t), .38 + .34 * math.sin(t)) for t in [i * .785 for i in range(8)]])
ARMS = part("arms", _arms)
def _standard():
    beam(DARKWOOD, (0, 0, 0), (0, 0, 7.5), .07); bar(DARKWOOD, (-.9, 0, 7.0), (.9, 0, 7.0), .08, .08)
    face("canvas:#8a2a26", [(-.85, .02, 6.95), (.85, .02, 6.95), (.8, .02, 5.4), (0, .02, 5.0), (-.8, .02, 5.4)]); face("canvas:#8a2a26", [(-.85, -.02, 6.95), (.85, -.02, 6.95), (.8, -.02, 5.4), (0, -.02, 5.0), (-.8, -.02, 5.4)][::-1])
    lathe("bronze", 0, 0, [(.02, 7.5), (.16, 7.7), (.02, 8.0)], 6)
STANDARD = part("standard", _standard)
def _fire():
    for k in range(9): lathe("rubble:#8a857a", .85 * math.cos(k * .7), .85 * math.sin(k * .7), [(.2, 0), (.16, .22)], 6)
    for k in range(5): beam("wood:#2e2218", (.65 * math.cos(k * 1.26), .65 * math.sin(k * 1.26), .06), (0, 0, .4), .07, 5)
    lathe("fire", 0, 0, [(.5, .08), (.36, .5), (.05, 1.15)], 8, cap_top=False)
FIRE = part("campfire", _fire)
def _torch():
    beam(DARKWOOD, (0, 0, 0), (0, 0, 2.3), .05, 5); lathe("flat:#2a2622", 0, 0, [(.1, 2.3), (.17, 2.5)], 6); lathe("fire", 0, 0, [(.16, 2.5), (.12, 2.75), (.02, 3.05)], 6, cap_top=False)
TORCH = part("torch", _torch)
def _catapult():                                                                          # a torsion stone-thrower: the stock on its stand, the spring-frame, two arms; it points along +x
    for s in (-.28, .28): bar(DARKWOOD, (-2.6, s, .35), (1.9, s, 2.3), .16, .2)
    bar(WOOD, (-2.2, 0, .68), (2.0, 0, 2.5), .34, .1)
    for s in (-1, 1):
        bar(DARKWOOD, (1.0, s * .9, 0), (1.3, s * .3, 2.0), .16, .16); bar(DARKWOOD, (-2.6, s * .7, 0), (-2.6, s * .28, .5), .14, .14)
        boxr(WOOD, WOOD, 1.95, s * .82, .5, .62, 1.55, 3.25); lathe("flat:#8a8274", 1.95, s * .82, [(.17, 1.45), (.17, 3.35)], 8)
        bar(WOOD, (1.95, s * .95, 2.4), (.75, s * 1.95, 2.25), .11, .11)
    for z in (1.6, 3.2): bar(DARKWOOD, (1.95, -1.15, z), (1.95, 1.15, z), .5, .14)
    bar(DARKWOOD, (-.2, -1.0, 0), (-.2, 1.0, 0), .16, .16)
CATAPULT = part("lithobolos", _catapult)
def _ram():                                                                               # the ram's tortoise: a wheeled shed roofed in planks and raw hides, the beam and its bronze head out in front (+x)
    boxr(DARKWOOD, WOOD, 0, 0, 7.6, 3.6, .5, .78)
    for sx in (-1, 1):
        face(HIDE, [(-3.9, sx * 2.0, .9), (3.9, sx * 2.0, .9), (3.9, 0, 3.5), (-3.9, 0, 3.5)][::sx]); face(WOOD, [(-3.9, sx * 1.8, .78), (3.9, sx * 1.8, .78), (3.9, sx * 2.0, .92), (-3.9, sx * 2.0, .92)][::sx])
        for x in (-2.7, 2.7): beam(DARKWOOD, (x, sx * 1.75, .5), (x, sx * 2.05, .5), .5, 10)
    for x, sg in ((-3.9, -1), (3.9, 1)): face(DARKWOOD, [(x, -2.0, .9), (x, 2.0, .9), (x, 0, 3.5)][::sg])
    beam(DARKWOOD, (-4.6, 0, 1.7), (5.3, 0, 1.7), .28, 8); beam("bronze", (5.3, 0, 1.7), (6.0, 0, 1.7), .34, 8)
RAM = part("ram", _ram)
def _helepolis():
    """The 'taker of cities': a timber tower on wheels, tapering through six storeys, its front and flanks plated and hung with
    hides, shuttered ports for its engines, a boarding bridge; open behind, where the ladders are. It faces +x."""
    lv = [(0.9, 4.0), (4.4, 3.7), (7.8, 3.4), (11.2, 3.1), (14.6, 2.8), (18.0, 2.5), (21.2, 2.3)]
    for i, ((z0, h0), (z1, h1)) in enumerate(zip(lv, lv[1:])):
        for (a, b), key in ((((1, -1), (1, 1)), "flat:#4d473e"), (((1, 1), (-1, 1)), "canvas:#5a4a3a"), (((-1, -1), (1, -1)), "canvas:#544536")):
            face(key, [(a[0] * h0, a[1] * h0, z0), (b[0] * h0, b[1] * h0, z0), (b[0] * h1, b[1] * h1, z1), (a[0] * h1, a[1] * h1, z1)])
        for ax, ay in ((-1, -1), (1, -1), (1, 1), (-1, 1)): bar(DARKWOOD, (ax * h0, ay * h0, z0), (ax * h1, ay * h1, z1), .3, .3)
        boxr(DARKWOOD, "wood:#8a7050", 0, 0, 2 * h0, 2 * h0, z0 - .22, z0)
        bar(WOOD, (-h0, -h0, z0), (-h1, h1, z1), .14, .14)                                    # the open back: braces and ladders from floor to floor
        for k in range(7): bar(WOOD, (-h0 + .05, .4, z0 + .2 + k * .45), (-h0 + .05, 1.1, z0 + .2 + k * .45), .06, .06)
        for s in (-.5, .5):
            panel("dark:#17130f", ((h0 + h1) / 2 + .05, -h0), ((h0 + h1) / 2 + .05, h0), h0 + s * 1.7, .9, z0 + 1.2, z0 + 2.3, .04)
    boxr(DARKWOOD, "wood:#8a7050", 0, 0, 2 * lv[-1][1], 2 * lv[-1][1], lv[-1][0] - .2, lv[-1][0])
    for a, b in (((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1)), ((-1, -1), (1, -1))): wall("wood:#5a4630", (a[0] * 2.3, a[1] * 2.3), (b[0] * 2.3, b[1] * 2.3), 21.2, 22.3)
    face("wood:#6a5239", [(2.7, -1.5, 17.9), (2.7, 1.5, 17.9), (6.2, 1.5, 19.6), (6.2, -1.5, 19.6)][::-1]); bar(DARKWOOD, (2.5, -1.5, 21.2), (6.2, -1.5, 19.6), .06, .06); bar(DARKWOOD, (2.5, 1.5, 21.2), (6.2, 1.5, 19.6), .06, .06)
    boxr(DARKWOOD, DARKWOOD, 0, 0, 9.0, 8.6, .55, .95)
    for x in (-3.3, -1.1, 1.1, 3.3):
        for s in (-1, 1): beam("wood:#3a2b1e", (x, s * 4.0, .9), (x, s * 4.5, .9), .9, 12)
HELEPOLIS = part("helepolis", _helepolis)
def _mantlet():                                                                           # a wicker screen propped on its stays
    face("straw:#8c7850", [(0, -1.3, 0), (0, 1.3, 0), (.5, 1.3, 2.2), (.5, -1.3, 2.2)]); face("straw:#7a6844", [(0, -1.3, 0), (0, 1.3, 0), (.5, 1.3, 2.2), (.5, -1.3, 2.2)][::-1])
    for y in (-1.1, 1.1): bar(DARKWOOD, (.5, y, 2.1), (-1.0, y, 0), .07, .07)
MANTLET = part("mantlet", _mantlet)
def _shed():                                                                              # a length of covered gallery: posts, a pitched roof of planks under hides
    for x in (-1.9, 1.9):
        for y in (-1.2, 1.2): bar(DARKWOOD, (x, y, 0), (x, y, 2.0), .14, .14)
    for s in (-1, 1): face(HIDE, [(-2.2, s * 1.5, 1.95), (2.2, s * 1.5, 1.95), (2.2, 0, 2.9), (-2.2, 0, 2.9)][::s])
SHED = part("gallery", _shed)
def _shot():                                                                              # dressed stone shot, heaped
    for k in range(10):
        x, y, z = (.42 * math.cos(k * .9), .42 * math.sin(k * .9), 0) if k < 7 else (.2 * math.cos(k * 2.1), .2 * math.sin(k * 2.1), .3)
        lathe("rubble:#a39e92", x, y, [(.03, z), (.17, z + .08), (.2, z + .2), (.17, z + .32), (.03, z + .4)], 7)
SHOT = part("shot", _shot)
STUMP = part("stump", lambda: (lathe("bark:#5d5043", 0, 0, [(.34, 0), (.24, .2), (.22, .42)], 8, cap_top=False), face("wood:#b99a6a", core.ring(0, 0, .22, .42, 8))))
LOGS = part("logs", lambda: [beam("bark:#5d5043", (-2.6, -.8 + j * .42 + (k % 2) * .2, .2 + k * .36), (2.6, -.8 + j * .42 + (k % 2) * .2, .2 + k * .36), .2, 7) for k in range(3) for j in range(4 - k)])

def light(x, y, z, watts, kind="fire"): LIGHTS.append((*core.to_world(x, y, z), watts, kind))
def fire(x, y, z, watts=1100): inst(FIRE, x, y, z); light(x, y, z + .9, watts)
def torch(x, y, z, watts=170): inst(TORCH, x, y, z); light(x, y, z + 2.9, watts, "torch")

# ---------------------------------------------------------------- the lines
def stockade(P, closed=True, gaps=()):
    """A palisade of sharpened stakes along a line, a panel at a time, left open at the gaps and wherever a road crosses."""
    g = random.Random(int(P[0][0] * 7 + P[0][1])); pts = list(P) + ([P[0]] if closed else [])
    for x, y, ux, uy, d in along(pts, 2.4):
        if land.road_dist(x, y) < 1.6 or any(math.hypot(x - gx, y - gy) < gr for gx, gy, gr in gaps): continue
        inst(g.choice(PANELS), x, y, land.zt(x, y), math.atan2(uy, ux) + (math.pi if g.random() < .5 else 0)); land.take_disc(x, y, 1.4)
def lines(g):
    inner, outer, road = grow(OCT, D_IN), grow(OCT, D_OUT), grow(OCT, D_ROAD)
    land.paint("earth", road + [road[0]], .5, 5.0, closed=False, width=D_OUT - D_IN)
    land.paint("earth", grow(OCT, 14) + [grow(OCT, 14)[0]], .42, 6.0, closed=False, width=18)        # the ground before the walls: trampled, burnt over, cut up by sorties
    gaps_in = [(84.6, -84.6, 9.5), (105.5, 19.0, 5.5), (-22.0, -105.5, 3.5)]
    land.earthwork(inner, [(0, 2.2, 1.1), (-4.6, 2.3, -1.8)]); land.earthwork(outer, [(0, 2.2, 1.1), (4.6, 2.3, -1.8)])
    stockade(inner, True, gaps_in); stockade(outer, True, ())
    for P, sign, step, off in ((inner, 1, 30.5, 2.6), (outer, -1, 44.0, 2.6)):               # watch-towers behind the palisades, a torch on each
        k = 0
        for x, y, ux, uy, d in along(list(P) + [P[0]], step):
            px, py = x + uy * off * sign, y - ux * off * sign                               # a little off the line, toward the road
            if land.road_dist(px, py) < 5 or any(math.hypot(x - gx, y - gy) < gr + 4 for gx, gy, gr in gaps_in): continue
            z = land.zt(px, py); inst(WATCH, px, py, z, math.atan2(uy, ux)); land.take_disc(px, py, 3.0); k += 1
            if k % 2 == 0 or sign > 0: inst(TORCH, px + ux * 1.2, py + uy * 1.2, z + 6.7, 0, .8); light(px + ux * 1.2, py + uy * 1.2, z + 9.2, 150, "torch")
    for name, (at, door) in S["camps"].items():                                            # where each camp's road passes the outer palisade: a gate between two towers
        dx, dy = at[0] - door[0], at[1] - door[1]; L = math.hypot(dx, dy); dx, dy = dx / L, dy / L; gx, gy = door[0] - dx * 13.5, door[1] - dy * 13.5
        for s in (-1, 1):
            px, py = gx - dy * s * 7.8, gy + dx * s * 7.8; z = land.zt(px, py); inst(WATCH, px, py, z, math.atan2(dy, dx), (1, 1, .7)); land.take_disc(px, py, 3.0)
            inst(TORCH, px + dy * s * 2.7, py - dx * s * 2.7, land.zt(px, py), 0); light(px + dy * s * 2.7, py - dx * s * 2.7, z + 2.9, 220, "torch")
    CLEAR.append(grow(OCT, D_OUT + 7))

# ---------------------------------------------------------------- the camps
def camp(name, at, door, r, g):
    cx, cy = at; dx, dy = door[0] - cx, door[1] - cy; L = math.hypot(dx, dy); dx, dy = dx / L, dy / L
    circ = [(cx + r * math.cos(2 * math.pi * k / 40), cy + r * math.sin(2 * math.pi * k / 40)) for k in range(40)]
    z = land.pad(circ, None, blend=6.0, lock=False, grow_by=0); land.paint("earth", grow(circ, 3), 1.0, 4.0)
    land.earthwork(circ, [(0, 2.0, .9), (4.0, 2.1, -1.6)]); stockade(circ, True, [(cx + dx * r, cy + dy * r, 3.4)])
    rot = math.degrees(math.atan2(dx, -dy)); chief = name.startswith("commander")
    with placed(cx, cy, rot, z):                                                          # local: the gate at (0, -r), the camp's street running in along +y
        for s in (-1, 1):
            inst(WATCH, s * 7.6, -r + 3.2, 0, 0, (1, 1, .7)); torch(s * 3.4, -r + 1.0, 0, 240)
        rows = [(-7.6, -r + 9), (7.6, -r + 9), (-7.6, -r + 17.5), (7.6, -r + 17.5), (-14.2, -r + 15), (14.2, -r + 15)]
        if chief: rows += [(-15.5, -r + 25), (15.5, -r + 25), (-8.6, -r + 34.5), (8.6, -r + 34.5)]
        else: rows += [(-12.5, -r + 25.5), (12.5, -r + 25.5)]
        for x, y in rows:                                                                 # the men's tents, doors to the street; arms stacked before them
            inst(g.choice(TENTS), x, y, 0, math.pi / 2 * (1 if x < 0 else -1) + g.uniform(-.08, .08), g.uniform(.95, 1.08))
            sx = x - (4.6 if x > 0 else -4.6); inst(ARMS, sx, y + g.uniform(-1.2, 1.2), 0, g.uniform(0, 6))
        hy = -r + (27.5 if chief else 26.5)                                               # the commander's tent at the head of the street, his standard before it
        inst(PAVILION if chief else OFFICER, 0, hy + (3.5 if chief else 1.5), 0, 0); inst(STANDARD, 2.6 if chief else 2.0, hy - 4.6, 0, 0)
        if chief: inst(STANDARD, -2.6, hy - 4.6, 0, 0); inst(props.HOUSE_ALTAR, 0, hy - 8.0, 0, 0, 1.5); torch(-4.8, hy - 3.2, 0, 200); torch(4.8, hy - 3.2, 0, 200)
        fire(0, -r + 12.5, 0, 1300); fire(g.choice((-1, 1)) * 2.0, hy - (12.5 if chief else 6.5), 0, 900)
        inst(props.CART, -4.6, -r + 4.6, 0, .4); inst(LOGS, 5.4, -r + 5.0, 0, 1.4, .7)
        for k in range(6): inst(g.choice((props.AMPH, props.PITHOS, props.SACK, props.BASKET)), 3.2 + (k % 3) * .7, -r + 15.5 + (k // 3) * .7, 0, g.uniform(0, 6))
        if name.endswith("A"):                                                            # the engineers' camp: stone-throwers under repair, shot dressed and heaped
            inst(CATAPULT, -3.5, hy + 8.6, 0, 2.0, .9); inst(CATAPULT, 5.5, hy + 7.4, 0, .6, .9)
            for k in range(3): inst(SHOT, -9 + k * 1.8, hy + 6.5, 0, k)
        elif name.endswith("B"):                                                          # the timber yard: baulks and logs for the works
            for k in range(3): inst(LOGS, -7.5 + k * 6.5, hy + 8.2, 0, g.uniform(-.2, .2), 1.0)
            inst(SHED, 8.5, hy + 2.0, 0, 0)
        elif name.endswith("C"):                                                          # fodder and stores
            for k in range(3): inst(props.HAY, -8 + k * 7.0, hy + 8.0, 0, k, g.uniform(.55, .7))
            props.jar_rows(-11, hy + 1.5, -6.5, hy + 3.4, 0, g, .6)
    land.take(grow(circ, 5)); CLEAR.append(grow(circ, 9))

# ---------------------------------------------------------------- the works against the walls
def mound(g):
    """The mound: earth and timber heaped against the south-east wall until a ram can be brought to bear on its upper courses."""
    import numpy as np
    M = S["mound"]; mc = M["mc"]; d = M["dir"]; out = M["out"] - 1.0; h = 5.9; P = [tuple(p) for p in M["poly"]]
    x0, y0, x1, y1 = core.bbox(P); sub = land.win(x0, y0, x1, y1, 3); xs, ys = land.X[sub], land.Y[sub]
    t = ((xs - mc[0]) * d[0] + (ys - mc[1]) * d[1]) / out; m = land.np_inpoly(grow(P, .4), xs, ys) & (t > .04)
    top = np.clip((1 - t) / .7, 0, 1) * h; base = land.Z[sub].copy()
    land.Z[sub] = np.where(m, np.maximum(base, base * 0 + land.zt(*mc) + top), base); land.LOCK[sub] |= m
    land.paint("earth", grow(P, 2.5), 1.0, 2.0); land.take(grow(P, 2))
    zf = lambda x, y: land.zt(mc[0], mc[1]) + max(0, min(1, (1 - ((x - mc[0]) * d[0] + (y - mc[1]) * d[1]) / out) / .7)) * h
    for a, b in ((P[1], P[2]), (P[3], P[0])):                                               # its flanks shored with logs
        for k in range(12):
            p, q = (lerp(a[0], b[0], k / 12), lerp(a[1], b[1], k / 12)), (lerp(a[0], b[0], (k + 1) / 12), lerp(a[1], b[1], (k + 1) / 12))
            wall("wood:#5a4630", p, q, (land.zt(mc[0], mc[1]) - .5,) * 2, (zf(*p) + .25, zf(*q) + .25)); wall("wood:#5a4630", q, p, (land.zt(mc[0], mc[1]) - .5,) * 2, (zf(*p) + .25, zf(*q) + .25))
    ang = math.atan2(-d[1], -d[0]); zt_ = land.zt(*mc) + h; rx, ry = mc[0] + d[0] * 6.2, mc[1] + d[1] * 6.2
    inst(RAM, rx, ry, zt_, ang)
    tx, ty = -d[1], d[0]
    for s in (-1, 1):
        inst(MANTLET, rx + tx * s * 5.5 - d[0] * 3, ry + ty * s * 5.5 - d[1] * 3, zt_, ang); inst(SHOT, rx + tx * s * 4.2 + d[0] * 5, ry + ty * s * 4.2 + d[1] * 5, zf(rx + d[0] * 5, ry + d[1] * 5), s)
    for k in range(3): inst(SHED, mc[0] + d[0] * (24.5 + k * 4.6), mc[1] + d[1] * (24.5 + k * 4.6), land.zt(mc[0] + d[0] * (24.5 + k * 4.6), mc[1] + d[1] * (24.5 + k * 4.6)), ang)
    fx, fy = mc[0] + d[0] * 30 + tx * 9, mc[1] + d[1] * 30 + ty * 9; fire(fx, fy, land.zt(fx, fy), 800)
    # the defenders' answer above it: a screen of timber and hides raised on the wall, to take the stones and hide the men
    zw = walls.q(land.zt(*mc) + walls.H_WALL) + 1.7
    a, b = (mc[0] - tx * 11 - d[0] * .9, mc[1] - ty * 11 - d[1] * .9), (mc[0] + tx * 11 - d[0] * .9, mc[1] + ty * 11 - d[1] * .9)
    wall(HIDE, a, b, zw, zw + 3.0); wall(HIDE, b, a, zw, zw + 3.0)
    for k in range(8): p = (lerp(a[0], b[0], k / 7), lerp(a[1], b[1], k / 7)); bar(DARKWOOD, (p[0], p[1], zw - 1.6), (p[0], p[1], zw + 3.2), .16, .16)
def tower_attack(g):
    """The helepolis, brought up over a filled ditch on a road of planks toward the east wall; bolt-shooters cover it."""
    R = box(84.0, 14.5, 106.5, 23.5); z = land.pad(R, None, blend=2.5); land.paint("earth", grow(R, 1.5), 1.0, 1.5); land.take(R, 1)
    for k in range(18): boxr(WOOD if k % 3 else DARKWOOD, WOOD if k % 3 else DARKWOOD, 93.0 + k * .72, 19.0, .62, 8.0 + (k % 2) * .4, z - .05, z + .09)
    inst(HELEPOLIS, 87.6, 19.0, z, math.pi)
    for k in range(3): inst(SHED, 96.5 + k * 4.6, 26.6, land.zt(96.5 + k * 4.6, 26.6), 0)
    for x, y in ((95.5, 6.5), (96.5, 33.5)):
        zz = land.zt(x, y); inst(CATAPULT, x, y, zz, math.pi, .6); inst(MANTLET, x - 3.0, y - 1.5, zz, math.pi); inst(MANTLET, x - 3.0, y + 1.5, zz, math.pi); land.take_disc(x, y, 4)
    fire(101.0, 11.5, land.zt(101, 11.5), 700); fire(93.5, 27.5, land.zt(93.5, 27.5), 600); torch(90.5, 13.0, z, 200)
def battery(g):
    """Three stone-throwers on the south side, behind a line of mantlets, their shot piled beside them."""
    for k, x in enumerate((-34.0, -22.0, -10.0)):
        y = -96.8; z = land.pad(rect(x, y, 8, 7), None, blend=2.0); inst(CATAPULT, x, y, z, math.pi / 2 + (k - 1) * .12)
        for s in (-1, 0, 1): inst(MANTLET, x + s * 2.8, y + 4.6, land.zt(x + s * 2.8, y + 4.6), math.pi / 2)
        inst(SHOT, x + 3.2, y - 1.5, z, k); inst(SHOT, x - 3.3, y - .5, z, k + 2); land.take(rect(x, y, 9, 10))
    land.paint("earth", box(-41, -103, -3, -90), 1.0, 2.0); fire(-28.0, -100.2, land.zt(-28, -100.2), 700); torch(-16.0, -100.0, land.zt(-16, -100), 160)

# ---------------------------------------------------------------- the town under siege
def town_defence(g):
    """A second wall, half built, behind the corner the mound threatens (as the Plataians and the Rhodians built theirs),
    the stone for it taken from the houses pulled down in its way; fires on the towers, a watch-fire in the agora."""
    a, b = (76.6, -31.0), (31.0, -76.6); L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; n = 14
    for k in range(n):
        p, q = (a[0] + ux * L * k / n, a[1] + uy * L * k / n), (a[0] + ux * L * (k + 1) / n, a[1] + uy * L * (k + 1) / n); m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        if land.road_dist(*m) < 2.6 and k not in (0, n - 1): continue                      # the streets through it are the last to be closed
        hh = 2.2 + 2.6 * abs(math.sin(k * 1.3 + .6)); seg = [(p[0] - uy * 1.0, p[1] + ux * 1.0), (q[0] - uy * 1.0, q[1] + ux * 1.0), (q[0] + uy * 1.0, q[1] - ux * 1.0), (p[0] + uy * 1.0, p[1] - ux * 1.0)]
        prism("rubble:#b3a78e", "paving:#bdb29a", seg, land.zmin(seg) - .5, land.zt(*m) + hh); land.take(seg, .5)
        if k % 3 == 1: inst(SHOT, m[0] - uy * 3.0, m[1] + ux * 3.0, land.zt(m[0] - uy * 3.0, m[1] + ux * 3.0), k, 1.6)
        if k % 4 == 2: inst(LOGS, m[0] - uy * 4.0, m[1] + ux * 4.0, land.zt(m[0] - uy * 4, m[1] + ux * 4), math.atan2(uy, ux), .6)
    land.paint("earth", [(a[0] + 2, a[1]), (b[0], b[1] - 2), (56, -70), (70, -56)], .9, 2.0)
    for i, (x, y, ze) in enumerate(walls.TOWERS):                                         # watch-fires in iron baskets by every other tower
        if i % 2 == 0:
            r = math.hypot(x, y); px, py = x * (1 - 1.7 / r) - y / r * 4.7, y * (1 - 1.7 / r) + x / r * 4.7; zz = walls.q(land.zt(px, py) + walls.H_WALL) + 1.3
            lathe("flat:#2a2622", px, py, [(.1, zz - 1.3), (.1, zz - .5), (.3, zz - .3), (.34, zz - .1)], 6); lathe("fire", px, py, [(.3, zz - .1), (.2, zz + .3), (.03, zz + .7)], 6, cap_top=False); light(px, py, zz + .8, 260, "torch")
    for x, y in ((-17.0, -12.0), (12.0, -20.0)): fire(x, y, land.zt(x, y), 600)

def build():
    g = random.Random(13)
    lines(g)
    for name, (at, door) in S["camps"].items(): camp(name, at, door, S["camp_r"][name], g)
    if not core.flag("--no-engines"): mound(g); tower_attack(g); battery(g)
    town_defence(g)
    for x, y, z, w, kind in LIGHTS:
        L = bpy.data.lights.new(kind, "POINT"); L.energy = w * float(core.opt("--lamps", 1.0)); L.color = (1.0, .42, .13) if kind == "fire" else (1.0, .55, .22); L.shadow_soft_size = .35 if kind == "fire" else .15
        o = bpy.data.objects.new(kind, L); ROOT.objects.link(o); o.location = (x, y, z)
    print("SIEGE: %d lights" % len(LIGHTS))
