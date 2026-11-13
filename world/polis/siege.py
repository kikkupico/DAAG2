"""The siege, by night. The model is Philip V before Phthiotic Thebes (Polybius 5.99): the army in separate camps round the
town, "the ground between the camps secured by a trench and a double palisade, with wooden towers at every hundred feet".
The messengers' ring road runs between the two palisades. Against the walls stand the engines of a Hellenistic siege: a wheeled
tower (helepolis), a battery of torsion stone-throwers behind wicker mantlets, and a mound with a ram under its tortoise
(as Polybius describes at Echinous, 9.41). Inside, the gates are barred and the defenders are raising a second wall behind
the threatened corner. No people: banked hearths of glowing coals, cressets and a few lamps stand in for them.
Nothing is caught in motion: no standing flames, no smoke; the picture must hold as a still, living place."""
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
def tent(name, w, l, wall_h, ridge, col, porch=0.0, trim=None, lit=False):
    """A ridge tent, its length along y and its door at the -y end."""
    def f():
        x0, x1, y0, y1 = -w / 2, w / 2, -l / 2, l / 2; k = "canvas:" + col
        for sx in (-1, 1):
            face(k, [(sx * x1, y0, 0), (sx * x1, y1, 0), (sx * x1, y1, wall_h), (sx * x1, y0, wall_h)][::sx])
            face(k, [(sx * (x1 + .12), y0 - .1, wall_h - .05), (sx * (x1 + .12), y1 + .1, wall_h - .05), (0, y1 + .1, ridge), (0, y0 - .1, ridge)][::sx])
            if trim: face("canvas:" + trim, [(sx * (x1 + .14), y0 - .12, wall_h - .08), (sx * (x1 + .14), y1 + .12, wall_h - .08), (sx * (x1 * .8), y1 + .12, wall_h + (ridge - wall_h) * .22), (sx * (x1 * .8), y0 - .12, wall_h + (ridge - wall_h) * .22)][::sx])
        for yy, sg in ((y0, -1), (y1, 1)): face(k, [(x0, yy, 0), (x1, yy, 0), (x1, yy, wall_h), (0, yy, ridge), (x0, yy, wall_h)][::-sg])
        face("glow" if lit else "dark:#1d1712", [(-w * .16, y0 - .02, 0), (w * .16, y0 - .02, 0), (w * .16, y0 - .02, wall_h * 1.15), (0, y0 - .02, ridge * .8), (-w * .16, y0 - .02, wall_h * 1.15)])
        for yy in (y0 - .15, y1 + .15): beam(DARKWOOD, (0, yy, 0), (0, yy, ridge + .3), .05, 5)
        if porch:
            face(k, [(x0 * .8, y0, ridge * .8), (x1 * .8, y0, ridge * .8), (x1 * .8, y0 - porch, wall_h + .2), (x0 * .8, y0 - porch, wall_h + .2)][::-1])
            for sx in (x0 * .8, x1 * .8): beam(DARKWOOD, (sx, y0 - porch, 0), (sx, y0 - porch, wall_h + .25), .05, 5)
    return part(name, f)
TENT_SPECS = ((4.6, 6.0, 1.0, 2.7, "#c9bb9b"), (4.2, 5.4, .9, 2.5, "#b9a888"), (5.0, 6.4, 1.1, 2.9, "#a8946f"), (4.4, 5.8, 1.0, 2.6, "#8d7a5e"))
TENTS = [tent("tent%d" % i, w, l, wh, r, c) for i, (w, l, wh, r, c) in enumerate(TENT_SPECS)]
TENTS_LIT = [tent("tent%d_lit" % i, w, l, wh, r, c, lit=True) for i, (w, l, wh, r, c) in enumerate(TENT_SPECS)]
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
    for k in range(5): beam("wood:#2e2218", (.7 * math.cos(k * 1.26), .7 * math.sin(k * 1.26), .1), (.15 * math.cos(k * 1.26 + .5), .15 * math.sin(k * 1.26 + .5), .2), .07, 5)
    lathe("fire", 0, 0, [(.6, .06), (.5, .17), (.22, .24)], 10)                             # a banked hearth: a bed of glowing coals, no standing flame
FIRE = part("campfire", _fire)
def _torch():
    beam(DARKWOOD, (0, 0, 0), (0, 0, 2.3), .05, 5); lathe("flat:#2a2622", 0, 0, [(.1, 2.3), (.17, 2.5)], 6); lathe("fire", 0, 0, [(.16, 2.5), (.15, 2.6), (.06, 2.68)], 6)
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
def _tortoise():
    boxr(DARKWOOD, WOOD, 0, 0, 6.2, 3.4, .5, .75)
    for sx in (-1, 1):
        face(HIDE, [(-3.2, sx * 1.8, .85), (3.2, sx * 1.8, .85), (3.2, 0, 2.8), (-3.2, 0, 2.8)][::sx])
        for x in (-2.1, 2.1): beam(DARKWOOD, (x, sx * 1.65, .5), (x, sx * 1.95, .5), .45, 10)
    for x, sg in ((-3.2, -1), (3.2, 1)): face(DARKWOOD, [(x, -1.8, .85), (x, 1.8, .85), (x, 0, 2.8)][::sg])
TORTOISE = part("tortoise", _tortoise)
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
            if i in (2, 4) and s > 0:
                panel("glow", (-h0, -h0), (h0, -h0), h0, .9, z0 + 1.2, z0 + 2.3, .05)
                panel("glow", ((h0 + h1) / 2 + .06, -h0), ((h0 + h1) / 2 + .06, h0), h0 + s * 1.7, .9, z0 + 1.2, z0 + 2.3, .05)
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

def _cookpot():
    for k in range(3):
        a = k * 2 * math.pi / 3
        beam(DARKWOOD, (.55 * math.cos(a), .55 * math.sin(a), 0), (0, 0, 1.35), .035, 5)
    beam("flat:#2a2622", (0, 0, 1.35), (0, 0, .64), .015, 4)
    lathe("flat:#241e1a", 0, 0, [(.08, .35), (.20, .48), (.20, .62), (.16, .66)], 8, cap_top=True)
COOKPOT = part("cookpot", _cookpot)

def _rack_arms():
    for sx in (-2.0, 2.0): beam(DARKWOOD, (sx, 0, 0), (sx, 0, 1.8), .07, 6)
    bar(WOOD, (-2.1, 0, 1.45), (2.1, 0, 1.45), .10, .10)
    for k in range(6):
        cx = -1.6 + k * .64
        pts = [(cx + .35 * math.cos(t), -.12, 1.05 + .35 * math.sin(t)) for t in [i * .785 for i in range(8)]]
        face("bronze", pts)
    for k in range(8):
        px = -1.7 + k * .48
        beam("wood:#8a744e", (px, .9, 0), (px, -.12, 4.9), .032, 4)
RACK_ARMS = part("rack_arms", _rack_arms)

def _picket():
    for sx in (-5.0, 5.0): beam(DARKWOOD, (sx, 0, 0), (sx, 0, 1.5), .08, 6)
    beam("straw:#a89468", (-5.0, 0, 1.25), (5.0, 0, 1.25), .03, 5)
    boxr(DARKWOOD, WOOD, 0, 0, 7.6, .65, 0, .42)
    for hx in (-3.2, 0.0, 3.2):
        lathe("straw:#d1b262", hx, .75, [(.85, 0), (.75, .35), (.4, .65), (.05, .82)], 10)
PICKET = part("picket", _picket)

def _forge():
    for x in (-1.8, 1.8):
        for y in (-1.8, 1.8): bar(DARKWOOD, (x, y, 0), (x, y, 2.5), .14, .14)
    for s in (-1, 1): face(HIDE, [(-2.0, s * 2.0, 2.4), (2.0, s * 2.0, 2.4), (2.0, 0, 3.3), (-2.0, 0, 3.3)][::s])
    boxr("rubble:#7a7468", "rubble:#8a857a", 0, 0, 1.2, 1.2, 0, .8)
    cyl("fire", 0, 0, .30, .78, .83, 10)
    beam("flat:#2a2420", (-1.5, 0, .45), (-.7, 0, .65), .22, 6)
    cyl("bark:#5d5043", 1.15, -.2, .24, 0, .60, 8)
    boxr("flat:#2e2b28", "flat:#3d3a36", 1.15, -.2, .42, .26, .60, .92)
FORGE = part("forge", _forge)

def _stake_stack():
    rg = random.Random(29)
    for row, n in enumerate((8, 7, 5)):
        z = .08 + row * .16
        for j in range(n):
            y = (j - (n - 1) / 2) * .17 + rg.uniform(-.01, .01)
            x0, x1 = -1.6 + rg.uniform(-.04, .04), 1.6 + rg.uniform(-.04, .04)
            lathe(WOOD if (row + j) % 2 else DARKWOOD, 0, 0, [], 4) if False else None
            beam(WOOD if (row + j) % 2 else DARKWOOD, (x0, y, z), (x1 - .25, y, z), .075, 5)
            beam(WOOD if (row + j) % 2 else DARKWOOD, (x1 - .25, y, z), (x1, y, z), .02, 5)
STAKE_STACK = part("stake_stack", _stake_stack)

def _ladder():
    for sy in (-.35, .35): beam(WOOD, (-3.5, sy, .06), (3.5, sy, .06), .055, 5)
    for k in range(17):
        x = -3.2 + k * .4
        beam(DARKWOOD, (x, -.35, .06), (x, .35, .06), .03, 4)
LADDER = part("ladder", _ladder)

def _saw_trestle():
    for sx in (-1.1, 1.1):
        beam(DARKWOOD, (sx, -.55, 0), (sx, .55, 1.2), .06, 5)
        beam(DARKWOOD, (sx, .55, 0), (sx, -.55, 1.2), .06, 5)
    beam("bark:#5d5043", (-2.0, 0, .95), (2.0, 0, .95), .20, 7)
SAW_TRESTLE = part("saw_trestle", _saw_trestle)

def _coil_rope():
    for k in range(3):
        z = .07 + k * .14; n = 12
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            beam("straw:#8a744e", (.36 * math.cos(a0), .36 * math.sin(a0), z), (.36 * math.cos(a1), .36 * math.sin(a1), z), .065, 5)
COIL_ROPE = part("coil_rope", _coil_rope)

def _clay_oven():
    prof = [(.90 * math.cos(t), 1.08 * math.sin(t)) for t in (0.0, .28, .56, .84, 1.12, 1.40)] + [(.04, 1.08)]
    lathe("clay:#b89a78", 0, 0, prof, 14, smooth=True, cap_top=True, cap_bot=False)
    boxr("clay:#a88968", "clay:#a88968", 0, -.82, .62, .22, 0.0, .58)
    face("glow", [(-.22, -.94, .05), (.22, -.94, .05), (.18, -.94, .48), (-.18, -.94, .48)])
CLAY_OVEN = part("clay_oven", _clay_oven)

def _cheval():
    beam(DARKWOOD, (-2.0, 0, .55), (2.0, 0, .55), .12, 7)
    for sx in (-1.5, 1.5):
        beam(WOOD, (sx, -.5, 0), (sx, .5, 1.0), .06, 5)
        beam(WOOD, (sx, .5, 0), (sx, -.5, 1.0), .06, 5)
    for k in range(7):
        x = -1.5 + k * .5
        s = 1 if k % 2 == 0 else -1
        beam(WOOD, (x, -.65 * s, .05), (x, .65 * s, 1.15), .04, 5)
CHEVAL = part("cheval", _cheval)

def _stakes_belt():
    for k in range(8):
        x = -1.05 + k * .30
        beam(WOOD if k % 2 else DARKWOOD, (x, .55, -.1), (x + (k % 3 - 1) * .06, -.50, .95), .055, 5)
    bar(DARKWOOD, (-1.2, .15, .35), (1.2, .15, .35), .08, .08)
STAKES_BELT = part("stakes_belt", _stakes_belt)

def _earth_basket():
    lathe("straw:#b99a5a", 0, 0, [(.22, 0), (.30, .3), (.33, .42)], 10, cap_top=False)
    lathe("earth:#6b5239", 0, 0, [(.31, .38), (.31, .43), (.15, .49), (.03, .51)], 10, cap_top=True)
EARTH_BASKET = part("earth_basket", _earth_basket)

def _fascine():
    beam("bark:#6a5a44", (-1.0, 0, .24), (1.0, 0, .24), .24, 7)
    for k in (-0.5, 0.5):
        beam("dark:#3a2e20", (k - .04, 0, .24), (k + .04, 0, .24), .255, 8)
FASCINE = part("fascine", _fascine)

def _capstan():
    boxr(DARKWOOD, WOOD, 0, 0, 1.4, 1.4, 0, .14)
    cyl(WOOD, 0, 0, .30, .14, 1.34, 10)
    for k in range(4):
        a = k * math.pi / 4
        bar(DARKWOOD, (-1.0 * math.cos(a), -1.0 * math.sin(a), 1.18), (1.0 * math.cos(a), 1.0 * math.sin(a), 1.18), .09, .09)
CAPSTAN = part("capstan", _capstan)

def _shot_rack():
    boxr(DARKWOOD, WOOD, 0, 0, 4.4, 1.8, 0, .14)
    for row, rad in enumerate((.125, .15, .20)):
        y = -.52 + row * .52
        for k in range(10):
            x = -1.8 + k * .40
            lathe("rubble:#a39e92", x, y, [(.02, .14), (rad * .85, .14 + rad * .4), (rad, .14 + rad), (rad * .85, .14 + rad * 1.6), (.02, .14 + rad * 2)], 7)
SHOT_RACK = part("shot_rack", _shot_rack)

def _rubble_heap():
    rg = random.Random(43)
    for k in range(12):
        r = rg.uniform(0, 1.2); a = rg.uniform(0, 6.28); z = (1 - r / 1.4) * .55
        boxr("ashlar:#cdc1a6", "ashlar:#d8cdb4", r * math.cos(a), r * math.sin(a), .9, .5, z, z + .45, rg.uniform(0, 180))
RUBBLE_HEAP = part("rubble_heap", _rubble_heap)

SHOT_SINGLE = [part("shot_s%d" % i, lambda rad=r: lathe("rubble:#b5b0a4", 0, 0, [(.02, -rad * .3), (rad * .85, -rad * .1), (rad, rad * .3), (rad * .85, rad * .7), (.02, rad)], 7)) for i, r in enumerate((.15, .185, .225))]

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
            if k % 3 == 0:
                tx, ty = px - uy * 2.2, py + ux * 2.2
                if land.road_dist(tx, ty) > 3.5: inst(TORCH, tx, ty, land.zt(tx, ty), 0)
    for name, (at, door) in S["camps"].items():                                            # where each camp's road passes the outer palisade: a gate between two towers
        dx, dy = at[0] - door[0], at[1] - door[1]; L = math.hypot(dx, dy); dx, dy = dx / L, dy / L; gx, gy = door[0] - dx * 13.5, door[1] - dy * 13.5
        for s in (-1, 1):
            px, py = gx - dy * s * 7.8, gy + dx * s * 7.8; z = land.zt(px, py); inst(WATCH, px, py, z, math.atan2(dy, dx), (1, 1, .7)); land.take_disc(px, py, 3.0)
            inst(TORCH, px + dy * s * 2.7, py - dx * s * 2.7, land.zt(px, py), 0); light(px + dy * s * 2.7, py - dx * s * 2.7, z + 2.9, 220, "torch")
        # gate posts, lintel, and open hurdle leaves
        pL = (gx + dy * 3.0, gy - dx * 3.0); pR = (gx - dy * 3.0, gy + dx * 3.0)
        zL, zR = land.zt(*pL), land.zt(*pR); ztop = max(zL, zR) + 4.3
        bar(DARKWOOD, (pL[0], pL[1], zL - .3), (pL[0], pL[1], ztop + .2), .28, .28)
        bar(DARKWOOD, (pR[0], pR[1], zR - .3), (pR[0], pR[1], ztop + .2), .28, .28)
        bar(DARKWOOD, (pL[0], pL[1], ztop), (pR[0], pR[1], ztop), .26, .26)
        for s in (-1, 1):
            hx, hy = gx - dy * s * 4.5 + dx * .5, gy + dx * s * 4.5 + dy * .5; zh = land.zt(hx, hy)
            for k in range(5):
                zz = zh + .3 + k * .65
                bar(WOOD, (hx - dy * 1.4, hy + dx * 1.4, zz), (hx + dy * 1.4, hy - dx * 1.4, zz), .08, .08)
            for t in (-1.2, 0.0, 1.2):
                bar(DARKWOOD, (hx - dy * t, hy + dx * t, zh), (hx - dy * t, hy + dx * t, zh + 3.0), .08, .08)
    # 1. guard posts along the ring road (inward toward town, clear of road & gaps)
    p_idx = 0
    for x, y, ux, uy, d in along(road + [road[0]], 64.0):
        px, py = x - uy * 6.8, y + ux * 6.8
        if land.road_dist(px, py) < 3.5 or not land.free(px, py, 2.5): continue
        if any(math.hypot(px - gx, py - gy) < 12.0 for gx, gy, _ in gaps_in): continue
        z = land.zt(px, py); ang = math.atan2(uy, ux)
        inst(TENTS_LIT[p_idx % len(TENTS_LIT)] if p_idx % 2 else g.choice(TENTS), px, py, z, ang, .8)
        fx, fy = px + uy * 2.8, py - ux * 2.8; fz = land.zt(fx, fy)
        inst(FIRE, fx, fy, fz, 0, .6)
        if p_idx % 2 == 0: light(fx, fy, fz + .6, 300)
        inst(ARMS, px + ux * 2.4, py + uy * 2.4, land.zt(px + ux * 2.4, py + uy * 2.4), g.uniform(0, 6))
        for s in (-1, 1):
            sx, sy = fx + ux * s * 1.1, fy + uy * s * 1.1; sz = land.zt(sx, sy)
            beam("bark:#5d5043", (sx - uy * .4, sy + ux * .4, sz + .12), (sx + uy * .4, sy - ux * .4, sz + .12), .12, 6)
        land.take_disc(px, py, 3.0); p_idx += 1
    # 3. movable cheval-de-frise drawn aside at the three inner palisade gaps
    for gx, gy, gr in gaps_in:
        cx, cy = gx + (8.5 if gx > 0 else -6.0), gy + (5.5 if gy < 0 else 4.0)
        if land.road_dist(cx, cy) > 3.5 and land.free(cx, cy, 2.0):
            inst(CHEVAL, cx, cy, land.zt(cx, cy), .4); land.take_disc(cx, cy, 2.2)
    # 4. sharpened stakes belt before the inner palisade
    stakes_coll = core.collection_of(STAKES_BELT, "stakes_belt")
    belt_line = grow(OCT, D_IN - 5.5)
    for x, y, ux, uy, d in along(belt_line + [belt_line[0]], 2.4):
        if land.road_dist(x, y) < 3.0 or any(math.hypot(x - gx, y - gy) < gr + 1.5 for gx, gy, gr in gaps_in): continue
        core.Scatter.add(stakes_coll, x, y, land.zt(x, y), math.atan2(uy, ux) + math.pi)
    # 5. supply dumps along the far side of the road (north & west sides, outside the road)
    for sx, sy, rot in ((-65.0, 125.0, .2), (45.0, 125.0, -.1), (-125.0, 45.0, 1.5), (-125.0, -45.0, 1.6)):
        if land.road_dist(sx, sy) > 3.5 and land.free(sx, sy, 3.0):
            z = land.zt(sx, sy)
            inst(STAKE_STACK, sx, sy, z, rot)
            inst(props.CART, sx + 4.2 * math.cos(rot), sy + 4.2 * math.sin(rot), land.zt(sx + 4.2 * math.cos(rot), sy + 4.2 * math.sin(rot)), rot + .3)
            for k in range(12):
                bx, by = sx - 3.0 + (k % 4) * .7, sy - 1.5 + (k // 4) * .7
                inst(props.BASKET, bx, by, land.zt(bx, by), g.uniform(0, 6), 1.3)
            land.take_disc(sx, sy, 4.0)
    # 6. artillery park on the east side, clear of the road
    ax, ay = 111.0, -35.0
    if land.road_dist(ax, ay) > 3.5 and land.free(ax, ay, 3.0):
        inst(CATAPULT, ax, ay - 2.5, land.zt(ax, ay - 2.5), math.pi, .6)
        inst(CATAPULT, ax, ay + 2.5, land.zt(ax, ay + 2.5), math.pi, .6)
        inst(SHOT, ax - 2.2, ay, land.zt(ax - 2.2, ay), 0)
        inst(MANTLET, ax + 1.8, ay, land.zt(ax + 1.8, ay) + .1, math.pi / 2, 1.0, tilt=(1.1, 0))
        land.take_disc(ax, ay, 4.0)
    CLEAR.append(grow(OCT, D_OUT + 7))

# ---------------------------------------------------------------- the camps
def _cooking_fire(x, y, g, lit=False):
    inst(FIRE, x, y, 0, 0, .6); inst(COOKPOT, x, y, 0, g.uniform(0, 6))
    n_seats = g.randint(3, 4); a0 = g.uniform(0, 6.28)
    for k in range(n_seats):
        a = a0 + k * 2 * math.pi / n_seats + g.uniform(-.2, .2)
        sx, sy = x + 1.15 * math.cos(a), y + 1.15 * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        beam("bark:#5d5043", (sx - tx * .4, sy - ty * .4, .12), (sx + tx * .4, sy + ty * .4, .12), .12, 6)
    if lit: light(x, y, .6, 350)

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
        for i, (x, y) in enumerate(rows):                                                  # the men's tents, doors to the street; arms stacked before them
            tlist = TENTS_LIT if i % 3 == 0 else TENTS
            inst(g.choice(tlist), x, y, 0, math.pi / 2 * (1 if x < 0 else -1) + g.uniform(-.08, .08), g.uniform(.95, 1.08))
            sx = x - (4.6 if x > 0 else -4.6); inst(ARMS, sx, y + g.uniform(-1.2, 1.2), 0, g.uniform(0, 6))
        hy = -r + (27.5 if chief else 26.5)                                               # the commander's tent at the head of the street, his standard before it
        inst(PAVILION if chief else OFFICER, 0, hy + (3.5 if chief else 1.5), 0, 0); inst(STANDARD, 2.6 if chief else 2.0, hy - 4.6, 0, 0)
        if chief:
            inst(STANDARD, -2.6, hy - 4.6, 0, 0); inst(props.HOUSE_ALTAR, 0, hy - 8.0, 0, 0, 1.5); torch(-4.8, hy - 3.2, 0, 200); torch(4.8, hy - 3.2, 0, 200)
            inst(props.TABLE, 0, hy - 3.6, 0, 0)
            inst(OFFICER, -9.5, hy + 2.5, 0, 0); torch(-11.8, hy - 1.5, 0, 180); torch(-7.2, hy - 1.5, 0, 180)
            inst(RACK_ARMS, -5.5, hy - 2.5, 0, 0)
        else:
            torch(-3.2, hy - 2.6, 0, 180)
        inst(RACK_ARMS, 5.5, hy - 2.2, 0, 0)
        fire(0, -r + 12.5, 0, 1300); fire(g.choice((-1, 1)) * 2.0, hy - (12.5 if chief else 6.5), 0, 900)
        inst(props.CART, -4.6, -r + 4.6, 0, .4); inst(props.CART_AMPH, 4.4, -r + 5.2, 0, -.5); inst(LOGS, 5.4, -r + 5.0, 0, 1.4, .7)
        for k in range(8):
            px, py = 2.8 + (k % 4) * .85, -r + 2.6 + (k // 4) * .85
            inst(props.PITHOS, px, py, -.15, g.uniform(0, 6))
        for k in range(2):
            cyl("canvas:#4a3828", 1.8 + k * .5, -r + 2.8, .18, 0, .35, 8)
        for k in range(6): inst(g.choice((props.AMPH, props.PITHOS, props.SACK, props.BASKET)), 3.2 + (k % 3) * .7, -r + 15.5 + (k // 3) * .7, 0, g.uniform(0, 6))
        inst(PICKET, 0, r - 3.6, 0, 0)
        # cooking fires in front of pairs of inner tents
        cf_pts = [(-3.8, -r + 9.0), (3.8, -r + 9.0), (-3.8, -r + 17.5), (3.8, -r + 17.5), (-10.4, -r + 15.0), (10.4, -r + 15.0)]
        if chief: cf_pts += [(-11.5, -r + 25.0), (11.5, -r + 25.0)]
        for ci, (fx, fy) in enumerate(cf_pts):
            _cooking_fire(fx, fy, g, lit=(ci % 3 == 0))
        # second ring of smaller tents in open arcs
        taken = list(rows) + [(-7.6, -r + 3.2), (7.6, -r + 3.2), (0, hy + (3.5 if chief else 1.5)), (0, r - 3.6), (5.5, hy - 2.2), (0, -r + 12.5), (-4.6, -r + 4.6), (4.4, -r + 5.2)]
        if chief: taken += [(-9.5, hy + 2.5), (-5.5, hy - 2.5)]
        if name.endswith("A"):
            inst(CATAPULT, -6.2, hy + 4.8, 0, 2.0, .9); inst(CATAPULT, 6.2, hy + 4.8, 0, .6, .9)
            for k in range(3): inst(SHOT, -9 + k * 1.8, hy + 6.5, 0, k)
            inst(FORGE, 9.5, hy - 3.5, 0, 0); light(9.5, hy - 3.5, 1.2, 500)
            inst(LOGS, 13.5, hy - 3.5, 0, 1.5, .8); inst(COIL_ROPE, 9.5, hy - 6.5, 0, 0)
            inst(CATAPULT, 6.0, hy - 8.5, 0, .3, .9)
            bar(WOOD, (4.5, hy - 10.2, .08), (6.5, hy - 10.4, .08), .11, .11)
            bar(WOOD, (4.7, hy - 10.6, .08), (6.7, hy - 10.8, .08), .11, .11)
            taken += [(9.5, hy - 3.5), (13.5, hy - 3.5), (6.0, hy - 8.5), (-6.2, hy + 4.8), (6.2, hy + 4.8)]
        elif name.endswith("B"):
            for k in range(3): inst(LOGS, -7.5 + k * 6.5, hy + 5.2, 0, g.uniform(-.2, .2), 1.0)
            inst(SHED, 8.5, hy + 2.0, 0, 0)
            inst(SAW_TRESTLE, 8.5, hy - 3.5, 0, .3); land.paint_disc("sand", *core.to_world(8.5, hy - 3.5)[:2], 2.0, 1.0, 1.0)
            for sx, sy, sr in ((11.5, hy - 6.0, .2), (11.5, hy - 8.5, .1), (-9.5, hy - 3.5, 1.4)):
                inst(STAKE_STACK, sx, sy, 0, sr)
            inst(LADDER, -8.5, hy - 6.8, 0, .1); inst(LADDER, -8.5, hy - 8.2, 0, .05)
            taken += [(8.5, hy + 2.0), (8.5, hy - 3.5), (11.5, hy - 6.0), (11.5, hy - 8.5), (-9.5, hy - 3.5), (-8.5, hy - 7.5)]
        elif name.endswith("C"):
            for k in range(3): inst(props.HAY, -8 + k * 7.0, hy + 5.0, 0, k, g.uniform(.55, .7))
            props.jar_rows(-11, hy + 1.5, -6.5, hy + 3.4, 0, g, .6)
            inst(CLAY_OVEN, 8.5, hy - 3.5, 0, -math.pi / 2); inst(CLAY_OVEN, 11.5, hy - 3.5, 0, -math.pi / 2)
            light(10.0, hy - 4.5, .8, 250)
            for k in range(30):
                row_i, col_i, layer = (k % 15) // 5, (k % 15) % 5, k // 15
                inst(props.SACK, -11.0 + col_i * .65, hy - 5.0 + row_i * .65, layer * .52, g.uniform(0, 6), .9)
            props.jar_rows(7.0, hy - 8.5, 11.5, hy - 6.5, 0, g, .6)
            taken += [(8.5, hy - 3.5), (11.5, hy - 3.5), (-9.5, hy - 4.5), (9.0, hy - 7.5)]
        n_outer = 0; outer_cands = []
        for ang_deg in range(-75, 256, 18):
            a = math.radians(ang_deg); tx, ty = (r - 4.5) * math.cos(a), (r - 4.5) * math.sin(a)
            if ty < -r + 5.5 or abs(tx) < 4.0 and ty < 0: continue
            if any(math.hypot(tx - ox, ty - oy) < 4.5 for ox, oy in taken): continue
            wx, wy, _ = core.to_world(tx, ty)
            if not land.free(wx, wy, 2.0): continue
            tlist = TENTS_LIT if n_outer % 3 == 1 else TENTS
            inst(g.choice(tlist), tx, ty, 0, math.atan2(-tx, ty), .8)
            taken.append((tx, ty)); outer_cands.append((tx, ty)); n_outer += 1
            if n_outer >= (10 if chief else 7): break
        for oi in range(0, len(outer_cands), 2):
            tx, ty = outer_cands[oi]; L_ = math.hypot(tx, ty) or 1
            fx, fy = tx - tx / L_ * 4.2, ty - ty / L_ * 4.2
            if not any(math.hypot(fx - ox, fy - oy) < 2.2 for ox, oy in taken):
                _cooking_fire(fx, fy, g, lit=(oi % 6 == 0))
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
        for m_k in range(3):
            mx, my = rx + tx * s * (5.2 + m_k * .3) - d[0] * (1.2 + m_k * 2.5), ry + ty * s * (5.2 + m_k * .3) - d[1] * (1.2 + m_k * 2.5)
            inst(MANTLET, mx, my, zf(mx, my), ang)
        inst(SHOT, rx + tx * s * 4.2 + d[0] * 5, ry + ty * s * 4.2 + d[1] * 5, zf(rx + d[0] * 5, ry + d[1] * 5), s)
        # 1. earth-carriers' gear at the tail flanks
        for bk in range(10):
            bx = mc[0] + d[0] * (18.0 + bk * .9) + tx * s * 8.2
            by = mc[1] + d[1] * (18.0 + bk * .9) + ty * s * 8.2
            inst(EARTH_BASKET, bx, by, land.zt(bx, by), g.uniform(0, 6), 1.3)
        fx0, fy0 = mc[0] + d[0] * 24.5 + tx * s * 10.5, mc[1] + d[1] * 24.5 + ty * s * 10.5
        for fk in range(7 if s < 0 else 8):
            row_f, col_f = fk // 4, fk % 4
            inst(FASCINE, fx0 + tx * s * col_f * .5, fy0 + ty * s * col_f * .5, land.zt(fx0, fy0) + row_f * .42, ang + .2)
        # 4. two torches on the mound's flanks, halfway up
        tx_p, ty_p = mc[0] + d[0] * 14.0 + tx * s * 9.5, mc[1] + d[1] * 14.0 + ty * s * 9.5
        torch(tx_p, ty_p, zf(tx_p, ty_p), 180)
    # 2. extend covered approach from 3 to 7 gallery lengths
    for k in range(7): inst(SHED, mc[0] + d[0] * (24.5 + k * 4.6), mc[1] + d[1] * (24.5 + k * 4.6), land.zt(mc[0] + d[0] * (24.5 + k * 4.6), mc[1] + d[1] * (24.5 + k * 4.6)), ang)
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
    # 5. hauling gear: two capstans and thick ropes
    for sy in (17.2, 20.8):
        inst(CAPSTAN, 98.5, sy, z + .09, 0)
        beam("straw:#8a744e", (91.5, sy, z + .20), (98.5, sy, z + .45), .05, 5)
    # 6. ditch-filling tortoise shed in front of the tower, with rubble and brushwood spilling
    inst(TORTOISE, 81.8, 19.0, land.zt(81.8, 19.0), math.pi, .62)
    for fk in range(4):
        inst(FASCINE, 79.8, 18.2 + fk * .5, land.zt(79.8, 18.2 + fk * .5), .2 * fk, .8)
    lathe("rubble:#9b9483", 79.8, 19.0, [(1.1, 0), (.8, .35), (.3, .6), (.05, .7)], 8)
    # 7. lamp inside the tower's open back at mid height
    light(86.5, 19.0, z + 10.0, 200)
    for k in range(3): inst(SHED, 96.5 + k * 4.6, 26.6, land.zt(96.5 + k * 4.6, 26.6), 0)
    for x, y in ((95.5, 6.5), (96.5, 33.5)):
        zz = land.zt(x, y); inst(CATAPULT, x, y, zz, math.pi, .6); inst(MANTLET, x - 3.0, y - 1.5, zz, math.pi); inst(MANTLET, x - 3.0, y + 1.5, zz, math.pi); land.take_disc(x, y, 4)
    fire(101.0, 11.5, land.zt(101, 11.5), 700); fire(93.5, 27.5, land.zt(93.5, 27.5), 600); torch(90.5, 13.0, z, 200)
def battery(g):
    """Three stone-throwers on the south side, behind a line of mantlets, their shot piled beside them."""
    for k, x in enumerate((-34.0, -22.0, -10.0)):
        y = -96.8; z = land.pad(rect(x, y, 8, 7), None, blend=2.0); inst(CATAPULT, x, y, z, math.pi / 2 + (k - 1) * .12)
        for s in (-1, 0, 1): inst(MANTLET, x + s * 2.8, y + 4.6, land.zt(x + s * 2.8, y + 4.6), math.pi / 2)
        # 8. low bank of earth-filled baskets in an arc toward the town
        for bk in range(12):
            a = math.radians(25 + (bk % 6) * 26); layer = bk // 6
            bx, by = x + 4.0 * math.cos(a), y + 1.2 + 3.2 * math.sin(a)
            inst(EARTH_BASKET, bx, by, land.zt(bx, by) + layer * .52, g.uniform(0, 6), 1.3)
        inst(SHOT, x + 3.2, y - 1.5, z, k); inst(SHOT, x - 3.3, y - .5, z, k + 2); land.take(rect(x, y, 9, 10))
        # 10. spare throwing arm and coil of rope
        bar(WOOD, (x - 4.2, y - 2.2, z + .08), (x - 2.2, y - 2.6, z + .08), .11, .11)
        inst(COIL_ROPE, x + 4.2, y - 2.4, z, 0)
    # 9. rack of dressed shot sorted by size behind the battery
    inst(SHOT_RACK, -22.0, -102.0, land.zt(-22.0, -102.0), 0)
    land.paint("earth", box(-41, -103, -3, -90), 1.0, 2.0); fire(-28.0, -100.2, land.zt(-28, -100.2), 700); torch(-16.0, -100.0, land.zt(-16, -100), 160)

def mine(g):
    """A mine driven toward the west wall: pit head under a shed, sloping trench, spoil heaps, pit props, torch."""
    mx, my = -96.0, 30.0
    if land.road_dist(mx, my) < 5.0: return
    land.paint("earth", box(mx - 4, my - 5, mx + 12, my + 5), 1.0, 2.0)
    z = land.zt(mx, my)
    inst(SHED, mx, my, z, 0)
    prism("earth:#6b5239", "earth:#4d3a28", box(mx + 1.5, my - 1.0, mx + 9.5, my + 1.0), z - 1.2, z - .1)
    for tx in (mx + 3.0, mx + 5.5, mx + 8.0):
        for sy in (-1.0, 1.0): bar(DARKWOOD, (tx, my + sy, z - .8), (tx, my + sy, z + 1.1), .12, .12)
        bar(DARKWOOD, (tx, my - 1.1, z + 1.1), (tx, my + 1.1, z + 1.1), .12, .12)
    face(HIDE, [(mx + 1.5, my - 1.2, z + 1.2), (mx + 9.5, my - 1.2, z + 1.2), (mx + 9.5, my + 1.2, z + 1.2), (mx + 1.5, my + 1.2, z + 1.2)])
    for sy in (-3.2, 3.2):
        lathe("flat:#9a8c72", mx + 2.0, my + sy, [(2.6, -.1), (2.2, .45), (1.3, 1.0), (.3, 1.35), (.05, 1.4)], 12, cap_top=True)
    inst(LOGS, mx - 3.2, my + 2.8, land.zt(mx - 3.2, my + 2.8), 1.2, .55)
    torch(mx - 2.5, my - 2.5, land.zt(mx - 2.5, my - 2.5), 180)
    land.take(box(mx - 4, my - 5, mx + 11, my + 5), .5)

def burnt_shed(g):
    """A burnt-out length of gallery east of the battery, with glowing embers."""
    bx, by = 20.0, -100.0
    if land.road_dist(bx, by) < 4.0: return
    z = land.zt(bx, by); land.paint_disc("wet", bx, by, 4.0, 1.0, 1.5)
    for px, py, tx, ty in ((-1.8, -1.1, -.4, .2), (1.8, -1.1, .3, -.3), (-1.8, 1.1, .2, .4), (1.8, 1.1, -.3, -.2)):
        bar("wood:#1f1a16", (bx + px, by + py, z - .1), (bx + px + tx, by + py + ty, z + 1.5), .14, .14)
    face("wood:#1f1a16", [(bx - 2.0, by - 1.3, z + .12), (bx + 2.0, by - 1.3, z + .12), (bx + 1.9, by + .1, z + .35), (bx - 1.9, by + .1, z + .35)])
    face("wood:#1f1a16", [(bx - 2.0, by + 1.3, z + .10), (bx + 2.0, by + 1.3, z + .10), (bx + 1.9, by - .1, z + .35), (bx - 1.9, by - .1, z + .35)][::-1])
    for ex, ey, er in ((-.8, -.4, .18), (.4, .5, .15), (1.1, -.2, .20), (-.3, .8, .14), (.7, -.7, .16), (-1.2, .3, .17)):
        cyl("fire", bx + ex, by + ey, er, z + .02, z + .08, 7)
    light(bx, by, z + .5, 120)
    land.take_disc(bx, by, 4.0)

def ladders_ready(g):
    """Six scaling ladders laid ready at two places just inside the inner palisade on the north and west sides."""
    for lx, ly, rot in ((-25.0, 100.0, 0.0), (-100.0, -25.0, math.pi / 2)):
        if land.road_dist(lx, ly) < 3.5: continue
        for k in range(6):
            px, py = lx + (0 if rot == 0 else (k - 2.5) * 1.1), ly + ((k - 2.5) * 1.1 if rot == 0 else 0)
            inst(LADDER, px, py, land.zt(px, py), rot)
        fx, fy = lx + (4.8 if rot == 0 else 0), ly + (0 if rot == 0 else 4.8)
        inst(FIRE, fx, fy, land.zt(fx, fy), 0, .6)
        land.take_disc(lx, ly, 4.5)

# ---------------------------------------------------------------- the town under siege
def _padding_sack():
    lathe("canvas:#b8a888", 0, 0, [(.15, 0), (.55, .25), (.60, .9), (.52, 1.55), (.20, 1.80)], 10, cap_top=True)
    beam("dark:#2a2218", (0, 0, 1.80), (0, 0, 2.85), .025, 4)
PADDING_SACK = part("padding_sack", _padding_sack)

def _beacon():
    beam("flat:#2a2622", (0, 0, 0), (0, 0, 3.0), .08, 6)
    lathe("flat:#2a2622", 0, 0, [(.25, 2.75), (.78, 3.0), (.80, 3.35)], 10, cap_top=False)
    lathe("fire", 0, 0, [(.74, 3.25), (.65, 3.42), (.30, 3.50)], 10, cap_top=True)
BEACON = part("beacon", _beacon)

def _hoist():
    for sx in (-1.6, 1.6): beam(DARKWOOD, (sx, -.8, 0), (0, .4, 4.8), .10, 6)
    beam("straw:#8a744e", (0, .4, 4.8), (0, .4, 2.2), .03, 5)
    boxr("ashlar:#cdc1a6", "ashlar:#d8cdb4", 0, .4, .8, .6, 1.6, 2.2)
HOIST = part("hoist", _hoist)

def _shelter():
    for sx in (-1.4, 1.4): beam(DARKWOOD, (sx, -1.1, 0), (sx, -1.1, 1.8), .06, 5)
    beam(DARKWOOD, (-1.5, -1.1, 1.8), (1.5, -1.1, 1.8), .05, 5)
    face("canvas:#c4b594", [(-1.5, -1.2, 1.82), (1.5, -1.2, 1.82), (1.5, 1.3, 0.05), (-1.5, 1.3, 0.05)])
    face("canvas:#a89a7a", [(-1.5, -1.2, 1.82), (1.5, -1.2, 1.82), (1.5, 1.3, 0.05), (-1.5, 1.3, 0.05)][::-1])
SHELTER = part("shelter", _shelter)

def _platform():
    for sx in (-2.1, 2.1):
        for sy in (-2.1, 2.1): bar(DARKWOOD, (sx, sy, 0), (sx, sy, 3.0), .18, .18)
    boxr(DARKWOOD, WOOD, 0, 0, 4.6, 4.6, 2.9, 3.1)
    for sx in (-.35, .35): bar(WOOD, (sx, -2.5, 0), (sx, -2.2, 3.0), .07, .07)
    for k in range(7): bar(WOOD, (-.35, -2.45 + k * .04, .3 + k * .4), (.35, -2.45 + k * .04, .3 + k * .4), .05, .05)
PLATFORM = part("platform", _platform)

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
    # 8. hoist, rubble heaps, mortar trough, and two torches by the second wall
    hm = ((a[0] + b[0]) / 2 - uy * 3.5, (a[1] + b[1]) / 2 + ux * 3.5)
    inst(HOIST, hm[0], hm[1], land.zt(*hm), math.atan2(uy, ux))
    boxr(DARKWOOD, "earth:#c9b592", hm[0] + ux * 4.0, hm[1] + uy * 4.0, 1.8, 1.0, land.zt(*hm), land.zt(*hm) + .45, math.degrees(math.atan2(uy, ux)))
    for t in (.22, .50, .78):
        rx, ry = lerp(a[0], b[0], t) - uy * 3.8, lerp(a[1], b[1], t) + ux * 3.8
        inst(RUBBLE_HEAP, rx, ry, land.zt(rx, ry), t * 5)
    for t in (.32, .68):
        tx_, ty_ = lerp(a[0], b[0], t) - uy * 2.5, lerp(a[1], b[1], t) + ux * 2.5
        torch(tx_, ty_, land.zt(tx_, ty_), 200)
    # 1 & 2. padding sacks and swing-beams on the south-east wall above the mound
    mc = S["mound"]["mc"]; d = S["mound"]["dir"]; tx, ty = -d[1], d[0]
    zw_walk = walls.q(land.zt(*mc) + walls.H_WALL)
    for k in range(10):
        off = -7.2 + k * 1.6
        sx, sy = mc[0] + tx * off + d[0] * 1.85, mc[1] + ty * off + d[1] * 1.85
        inst(PADDING_SACK, sx, sy, zw_walk - 2.8, 0)
    for s in (-1, 1):
        bx, by = mc[0] + tx * s * 4.5, mc[1] + ty * s * 4.5
        bar(DARKWOOD, (bx - d[0] * 1.0, by - d[1] * 1.0, zw_walk + 1.1), (bx + d[0] * 4.0, by + d[1] * 4.0, zw_walk + 1.1), .24, .24)
        bar(WOOD, (bx + d[0] * .2 - tx * .9, by + d[1] * .2 - ty * .9, zw_walk), (bx + d[0] * .2, by + d[1] * .2, zw_walk + 2.5), .16, .16)
        bar(WOOD, (bx + d[0] * .2 + tx * .9, by + d[1] * .2 + ty * .9, zw_walk), (bx + d[0] * .2, by + d[1] * .2, zw_walk + 2.5), .16, .16)
        beam("flat:#3a3530", (bx + d[0] * 3.8, by + d[1] * 3.8, zw_walk + 1.0), (bx + d[0] * 3.8, by + d[1] * 3.8, zw_walk - 1.2), .03, 4)
        boxr("ashlar:#cdc1a6", "ashlar:#d8cdb4", bx + d[0] * 3.8, by + d[1] * 3.8, .8, .8, zw_walk - 1.8, zw_walk - 1.0)
    # 3. hide-and-timber patches over the two wall-top notches
    for nx, ny, ux_, uy_ in ((-20.0, -78.0, 1.0, 0.0), (78.0, 20.0, 0.0, 1.0)):
        zn = walls.q(land.zt(nx, ny) + walls.H_WALL)
        pa, pb = (nx - ux_ * 1.2 + uy_ * 1.1, ny - uy_ * 1.2 - ux_ * 1.1), (nx + ux_ * 1.2 + uy_ * 1.1, ny + uy_ * 1.2 - ux_ * 1.1)
        wall(HIDE, pa, pb, zn, zn + 1.2); wall(HIDE, pb, pa, zn, zn + 1.2)
        for p in (pa, pb): bar(DARKWOOD, (p[0], p[1], zn), (p[0], p[1], zn + 1.3), .12, .12)
    # 4. defenders' artillery on timber platforms in the lane behind the south and east walls
    for px, py, ang in ((-22.0, -74.2, -math.pi / 2), (74.2, 19.0, 0.0)):
        pz = land.zt(px, py)
        inst(PLATFORM, px, py, pz, ang)
        inst(CATAPULT, px, py, pz + 3.1, ang, .8)
        inst(SHOT, px - 1.5 * math.sin(ang), py + 1.5 * math.cos(ang), pz + 3.1, 0, .7)
        torch(px + 1.8 * math.sin(ang), py - 1.8 * math.cos(ang), pz + 3.1, 180)
    # 7. fire-fighting and stores at the foot of the wall inside behind the three attacked stretches
    for sx, sy, ux_, uy_ in ((-28.0, -76.0, 1.0, 0.0), (76.0, 12.0, 0.0, 1.0), (54.0, -64.0, .707, -.707)):
        for k in range(10):
            px, py = sx + ux_ * k * .9, sy + uy_ * k * .9
            inst(props.PITHOS, px, py, land.zt(px, py), g.uniform(0, 6))
        inst(SHOT, sx - ux_ * 2.0, sy - uy_ * 2.0, land.zt(sx - ux_ * 2.0, sy - uy_ * 2.0), 0)
        inst(LOGS, sx + ux_ * 10.5, sy + uy_ * 10.5, land.zt(sx + ux_ * 10.5, sy + uy_ * 10.5), math.atan2(uy_, ux_), .5)
    for i, (x, y, ze) in enumerate(walls.TOWERS):                                         # watch-fires in iron baskets by every other tower
        if i % 2 == 0:
            r = math.hypot(x, y); px, py = x * (1 - 1.7 / r) - y / r * 4.7, y * (1 - 1.7 / r) + x / r * 4.7; zz = walls.q(land.zt(px, py) + walls.H_WALL) + 1.3
            lathe("flat:#2a2622", px, py, [(.1, zz - 1.3), (.1, zz - .5), (.3, zz - .3), (.34, zz - .1)], 6); lathe("fire", px, py, [(.33, zz - .12), (.31, zz - .02), (.12, zz + .05)], 8); light(px, py, zz + .8, 260, "torch")
    # 5. lit wall-walk: midpoint torches between pairs of towers (4 with real lamps)
    T = walls.TOWERS; nT = len(T); lit_count = 0
    for i in range(nT):
        x0, y0, _ = T[i]; x1, y1, _ = T[(i + 1) % nT]
        if math.hypot(x1 - x0, y1 - y0) > 45.0: continue
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2; r = math.hypot(mx, my) or 1
        px, py = mx * (1 - 2.2 / r), my * (1 - 2.2 / r); zz = walls.q(land.zt(px, py) + walls.H_WALL)
        inst(TORCH, px, py, zz, 0, .8)
        if i % 4 == 1 and lit_count < 4:
            light(px, py, zz + 2.3, 150, "torch"); lit_count += 1
    # 6. signal beacon beside the north gate's west tower
    bx, by = -13.0, 78.0; bz = walls.q(land.zt(bx, by) + walls.H_WALL)
    inst(BEACON, bx, by, bz, 0); light(bx, by, bz + 3.8, 700, "fire")
    for x, y in ((-17.0, -12.0), (12.0, -20.0)): fire(x, y, land.zt(x, y), 900)

def no_mans_land(g):
    """The cleared killing ground between the inner palisade and the town wall: spent shot, fallen masonry, wrecked gear, scorched patches, trodden paths."""
    shot_colls = [core.collection_of(m, m.name) for m in SHOT_SINGLE]
    for _ in range(15):
        x, y = g.uniform(-40, 0), g.uniform(-90, -79.5)
        if land.free(x, y, .3): core.Scatter.add(g.choice(shot_colls), x, y, land.zt(x, y), g.uniform(0, 6.28))
        x, y = g.uniform(79.5, 90), g.uniform(5, 35)
        if land.free(x, y, .3): core.Scatter.add(g.choice(shot_colls), x, y, land.zt(x, y), g.uniform(0, 6.28))
    for rx, ry in ((-32, -80.2), (-14, -80.2), (80.2, 10), (80.2, 26), (59, -71)):
        if land.free(rx, ry, 1.5):
            inst(RUBBLE_HEAP, rx, ry, land.zt(rx, ry), g.uniform(0, 6.28)); land.take_disc(rx, ry, 1.8)
    for mx, my, mr in ((28, -92, .4), (88, -12, 1.8), (94, 48, 2.5)):
        if land.free(mx, my, 1.2):
            inst(MANTLET, mx, my, land.zt(mx, my) + .2, mr, 1.0, tilt=(1.4, 0)); land.take_disc(mx, my, 1.4)
    for lx, ly, lr in ((88, -28, .6), (91, -26, 1.1)):
        if land.free(lx, ly, 1.5):
            inst(LADDER, lx, ly, land.zt(lx, ly) + .1, lr, .55, tilt=(0, .15)); land.take_disc(lx, ly, 1.8)
    if land.free(15, -90, 1.5):
        inst(props.CART, 15, -90, land.zt(15, -90) + .6, .7, 1.0, tilt=(1.4, 0)); land.take_disc(15, -90, 1.8)
    for sx, sy, sr in ((-25, -88, 3.8), (10, -86, 3.5), (42, -82, 4.2), (86, -42, 3.6), (92, 8, 3.2), (88, 38, 4.0)):
        land.paint_disc("wet", sx, sy, sr, 1.0, 1.5)
    for p, q in (((84.6, -84.6), (72.0, -72.0)), ((105.5, 19.0), (92.0, 19.0)), ((-22.0, -105.5), (-22.0, -96.8))):
        land.paint("earth", [p, q], 1.0, 1.0, closed=False, width=3.0)

ALTAR_COALS = part("altar_coals", lambda: boxr("fire", "fire", 0, 0, .9, .6, 0, .12))
def _roof_hole():
    cyl("dark:#15110e", 0, 0, 1.05, 0, .08, 10)
    lathe("clay:#c9a078", 0, 0, [(1.02, 0), (1.35, .04), (1.28, .15), (1.02, .12)], 10, cap_top=True)
    for k in (0.4, 1.8, 3.3, 4.9):
        boxr("clay:#a8674a", "clay:#a8674a", 1.15 * math.cos(k), 1.15 * math.sin(k), .35, .24, .06, .14, k)
ROOF_HOLE = part("roof_hole", _roof_hole)
STONE_BALL = part("stone_ball_40", lambda: lathe("limestone:#d8cfb8", 0, 0, [(.04, 0), (.18, .08), (.21, .20), (.18, .32), (.04, .40)], 8, cap_top=True))
RUBBLE_STUB = part("rubble_stub", lambda: boxr("rubble:#b3a78e", "paving:#bdb29a", 0, 0, 3.2, .55, 0, .9))
TILE_HEAP = part("tile_heap", lambda: lathe("clay:#a8674a", 0, 0, [(1.1, 0), (.65, .32), (.12, .55)], 8, cap_top=True))

def town_life(g):
    from mathutils import Vector
    core.flush()
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()

    def hit_z(x, y):
        ok, loc, _, _, _, _ = scene.ray_cast(dg, Vector((x, y, 80.0)), Vector((0.0, 0.0, -1.0)))
        return loc.z if ok else land.zt(x, y)

    # 1. Four civilian shelter clusters (agora west x2, sanctuary, palaistra)
    for cx, cy in ((-15.0, -27.2), (-10.5, -14.5), (-18.0, 21.5), (20.0, -55.0)):
        fire(cx, cy, land.zt(cx, cy), 350)
        n_sh = g.choice((3, 4))
        a0 = g.uniform(0, 6.28)
        for i in range(n_sh):
            a = a0 + i * (6.28 / n_sh) + g.uniform(-0.2, 0.2)
            r = g.uniform(2.5, 3.2)
            px, py = cx + r * math.cos(a), cy + r * math.sin(a)
            inst(SHELTER, px, py, land.zt(px, py), a + math.pi)
        for _ in range(5):
            a = g.uniform(0, 6.28); r = g.uniform(1.3, 2.2)
            px, py = cx + r * math.cos(a), cy + r * math.sin(a)
            inst(g.choice((props.PITHOS, props.AMPH, props.SACK, props.BASKET)), px, py, land.zt(px, py), g.uniform(0, 6.28), g.uniform(0.75, 1.0))

    # 2. Agora arms depot around the two watch-fires, keeping streets clear
    depot_pts = []
    for fx, fy in ((-17.0, -12.0), (12.0, -20.0)):
        for _ in range(40):
            px = fx + g.uniform(-6.5, 6.5)
            py = fy + g.uniform(-6.5, 6.5)
            if math.hypot(px - fx, py - fy) > 2.2 and land.road_dist(px, py) > 2.0:
                depot_pts.append((px, py))
                if len(depot_pts) >= 10: break
    for i, (px, py) in enumerate(depot_pts[:10]):
        z = land.zt(px, py)
        if i < 4: inst(ARMS, px, py, z, g.uniform(0, 6.28))
        elif i < 7: inst(SHOT, px, py, z, g.uniform(0, 6.28))
        elif i < 9: inst(RACK_ARMS, px, py, z, g.uniform(0, 6.28))
        else: inst(props.CART, px, py, z, g.uniform(0, 6.28))

    # 3. Sanctuary altar sacrifice + temple step torches
    az = hit_z(-11.5, 26.6)
    inst(ALTAR_COALS, -11.5, 26.6, az, 0.0)
    light(-11.5, 26.6, az + 1.5, 600, "fire")
    for sx, sy in ((-16.5, 24.5), (-16.5, 28.7)):
        inst(TORCH, sx, sy, land.zt(sx, sy), g.uniform(0, 6.28))

    # 4. Artillery damage near the two inner-lane platforms
    for px, py in ((-22.0, -74.2), (74.2, 19.0)):
        roof_hits = []
        for r in (4.5, 6.5, 8.5, 9.5):
            for k in range(16):
                a = k * (6.28 / 16) + g.uniform(-0.1, 0.1)
                rx, ry = px + r * math.cos(a), py + r * math.sin(a)
                rz = hit_z(rx, ry)
                if rz > land.zt(rx, ry) + 2.5 and all(math.hypot(rx - hx, ry - hy) > 3.0 for hx, hy, _ in roof_hits):
                    roof_hits.append((rx, ry, rz))
                    if len(roof_hits) >= 2: break
            if len(roof_hits) >= 2: break
        for rx, ry, rz in roof_hits:
            inst(ROOF_HOLE, rx, ry, rz, g.uniform(0, 6.28))
        placed = 0
        for _ in range(40):
            bx = px + g.uniform(-9.0, 9.0)
            by = py + g.uniform(-9.0, 9.0)
            bz = hit_z(bx, by)
            if bz <= land.zt(bx, by) + 0.5:
                inst(STONE_BALL, bx, by, bz, g.uniform(0, 6.28))
                placed += 1
                if placed >= 8: break

    # 5. Pulled-down houses between second wall and SE corner
    for hx, hy, ha in ((38.0, -62.0, 0.2), (48.0, -56.0, 0.9), (56.0, -44.0, 1.4)):
        z = land.zt(hx, hy)
        inst(RUBBLE_STUB, hx, hy, z, ha)
        inst(RUBBLE_STUB, hx + 2.2 * math.cos(ha + 1.57), hy + 2.2 * math.sin(ha + 1.57), z, ha + 1.57)
        inst(TILE_HEAP, hx + 1.4 * math.cos(ha), hy + 1.4 * math.sin(ha), z, g.uniform(0, 6.28))
        inst(LOGS, hx - 1.8 * math.sin(ha), hy + 1.8 * math.cos(ha), z, ha, 0.5)

    # 6. Four gate barricades 14 m inside each gate, blocking half the street
    barricades = (
        (64.0,  2.2, 0.0),
        (-2.2, -64.0, math.pi / 2),
        (-64.0, -2.2, 0.0),
        (2.2,  64.0, math.pi / 2),
    )
    for bx, by, ba in barricades:
        for d in (-1.2, 1.2):
            cx = bx + d * math.cos(ba)
            cy = by + d * math.sin(ba)
            inst(props.CART, cx, cy, land.zt(cx, cy), ba + (0.4 if d > 0 else -0.4))
        for k in range(8):
            ox = bx + (k - 3.5) * 0.65 * math.cos(ba) + g.uniform(-0.4, 0.4)
            oy = by + (k - 3.5) * 0.65 * math.sin(ba) + g.uniform(-0.4, 0.4)
            inst(props.PITHOS, ox, oy, land.zt(ox, oy), g.uniform(0, 6.28), g.uniform(0.85, 1.05))
        torch(bx, by, land.zt(bx, by), 180)

def sutlers(g):
    """Part A (Phase 7): small sutlers' market outside Camp C or Camp B if in view and clear."""
    for sx, sy, rot in ((-142.0, -26.0, 0.2), (26.0, -142.0, 1.3), (-26.0, -142.0, 1.3)):
        if core.in_view(sx, sy, 0, 0.0) and land.free(sx, sy, 5.5) and land.road_dist(sx, sy) > 4.0:
            land.paint_disc("earth", sx, sy, 6.5, .6, 1.5)
            for dx, dy in ((-2.5, -1.8), (2.2, -1.5), (0.0, 2.5)):
                px, py = sx + dx, sy + dy
                inst(props.STALLS[g.randrange(len(props.STALLS))], px, py, land.zt(px, py), rot + g.uniform(-0.3, 0.3))
            inst(props.CART, sx - 3.5, sy + 2.0, land.zt(sx - 3.5, sy + 2.0), rot + 0.8)
            for _ in range(6):
                px = sx + g.uniform(-4.0, 4.0); py = sy + g.uniform(-4.0, 4.0)
                inst(g.choice((props.PITHOS, props.AMPH, props.SACK)), px, py, land.zt(px, py), g.uniform(0, 6.28))
            torch(sx, sy, land.zt(sx, sy), 180)
            land.take_disc(sx, sy, 6.0)
            break

def town_ditch():
    """Part B (Phase 7): interrupted town ditch along open stretches of grow(OCT, 11) before siege works."""
    ring = grow(OCT, 11)
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(4, int(L / 4.0))
        stretch = []
        for k in range(n + 1):
            t = k / n
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            clear = (land.road_dist(x, y) > 5.0
                     and math.hypot(x - (-22.0), y - (-96.8)) > 12.0
                     and math.hypot(x - 92.0, y - 19.0) > 10.0
                     and math.hypot(x - 68.0, y - (-68.0)) > 14.0)
            if clear:
                stretch.append((x, y))
            else:
                if len(stretch) >= 2:
                    land.earthwork(stretch, [(0, 3.0, -2.5)], closed=False, keep_clear=2.2)
                stretch = []
        if len(stretch) >= 2:
            land.earthwork(stretch, [(0, 3.0, -2.5)], closed=False, keep_clear=2.2)

def build():
    g = random.Random(13)
    lines(g)
    for name, (at, door) in S["camps"].items(): camp(name, at, door, S["camp_r"][name], g)
    town_ditch()
    if not core.flag("--no-engines"): mound(g); tower_attack(g); battery(g); mine(g); burnt_shed(g); ladders_ready(g)
    no_mans_land(g)
    town_defence(g)
    town_life(g)
    sutlers(g)
    for x, y, z, w, kind in LIGHTS:
        L = bpy.data.lights.new(kind, "POINT"); L.energy = w * float(core.opt("--lamps", 2.5)); L.color = (1.0, .42, .13) if kind == "fire" else (1.0, .55, .22); L.shadow_soft_size = .35 if kind == "fire" else .15
        o = bpy.data.objects.new(kind, L); ROOT.objects.link(o); o.location = (x, y, z)
    print("SIEGE: %d lights" % len(LIGHTS))
