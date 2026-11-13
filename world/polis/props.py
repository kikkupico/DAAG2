"""Small things, each made once and instanced: jars, altars, well heads, statues and their bases, stalls, carts, boats."""
import math, random
from . import core, land
from .core import face, mesh, prism, boxr, lathe, cyl, beam, bar, Part, inst, rect, box

def part(name, fn):
    with Part(name) as p: fn()
    return p.mesh
def turned(name, prof, key, n=14):
    return part(name, lambda: lathe(key, 0, 0, prof, n, cap_top=True, cap_bot=False))

AMPH_PROF = [(.02, 0), (.07, .06), (.17, .24), (.2, .42), (.18, .58), (.09, .7), (.055, .74), (.055, .86), (.075, .9)]
AMPH = turned("amphora", AMPH_PROF, "clay:#b4683e", 10)
AMPH_RAW = turned("amphora_unfired", AMPH_PROF, "clay:#b9a58a", 10)
PITHOS = turned("pithos", [(.18, 0), (.42, .25), (.55, .62), (.5, 1.05), (.3, 1.3), (.34, 1.38)], "clay:#a65d38", 12)
HYDRIA_PROF = [(.08, 0), (.16, .12), (.2, .28), (.14, .42), (.07, .5), (.1, .56)]
HYDRIA = turned("hydria", HYDRIA_PROF, "clay:#8c4a2e", 10)
HYDRIA_BLACK = turned("hydria_black", HYDRIA_PROF, "clay:#2a2622", 10)
SACK_PROF = [(.18, 0), (.3, .12), (.32, .4), (.2, .62), (.08, .7)]
SACK = turned("sack", SACK_PROF, "cloth:#c9b68e", 8)
BASKET = turned("basket", [(.22, 0), (.3, .3), (.33, .42)], "straw:#b99a5a", 10)
HAY = turned("hay", [(2.2, 0), (2.4, .6), (2.2, 1.7), (1.5, 2.8), (.6, 3.5), (.05, 3.8)], "straw:#d1b262", 16)
SHEAF = turned("sheaf", [(.25, 0), (.18, .5), (.32, .95), (.05, 1.1)], "straw:#dcbf6c", 7)
BEEHIVE = turned("beehive", [(.3, 0), (.34, .3), (.2, .55), (.05, .62)], "clay:#b08a62", 10)
GRAIN_HEAP = turned("grain_heap", [(1.52, -.04), (1.48, .02), (1.02, .32), (.54, .64), (.05, .90)], "straw:#e0b24a", 16)
CHAFF_HEAP = turned("chaff_heap", [(2.02, -.04), (1.96, .04), (1.42, .23), (.78, .41), (.08, .50)], "straw:#e6d9a8", 16)
MANURE_HEAP = turned("manure_heap", [(2.02, -.05), (1.94, .06), (1.42, .30), (.78, .50), (.10, .60)], "flat:#4a3b2a", 16)
CLAY_HEAP = turned("clay_heap", [(1.54, -.04), (1.48, .04), (1.08, .32), (.58, .56), (.06, .70)], "flat:#8a7a66", 16)
SALT_HEAP = turned("salt_heap", [(.84, -.04), (.80, .02), (.54, .22), (.26, .43), (.04, .60)], "flat:#eeeae0", 16)
SHERD_HEAP = turned("sherd_heap", [(2.55, -.05), (2.48, .05), (1.75, .42), (.92, .75), (.10, .90)], "clay:#9a5a3a", 18)

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
    # stepped, moulded marble pedestal with a bronze inscription plaque
    boxr("marble:#d9d0bd", "marble:#e4dcc9", 0, 0, 4.0, 4.0, 0, .35)
    boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 3.4, 3.4, .35, .7)
    boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, 2.75, 2.75, .7, 3.0)
    boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 3.15, 3.15, 3.0, 3.3)
    boxr("bronze", "bronze", 0, 1.38, 1.6, .08, 1.3, 2.3)
    with core.placed(0, 0, 0, 3.3):
        _figure("bronze", 6.4)
        # Corinthian helmet crest and gilded plume
        boxr("gold", "gold", 0, .05, .24, .95, 6.25, 6.85)
        # aegis collar / breastplate accent
        lathe("gold", 0, 0, [(.88, 4.45), (.96, 4.9), (.62, 5.35)], 10)
    # raised spear with gilded tip, and her round hoplon shield beside her left leg
    beam("bronze", (.98, .25, 3.35), (1.05, .25, 10.6), .065, 6)
    lathe("gold", 1.05, .25, [(.09, 10.6), (.12, 10.75), (.02, 11.15)], 8, cap_top=True)
    cyl("bronze", -1.15, .15, .95, 3.35, 5.15, 16)
    boxr("gold", "gold", -1.15, 1.1, .35, .08, 4.1, 4.45)
COLOSSUS = part("colossus", _colossus)
STELE = part("stele", lambda: (boxr("marble:#ddd5c2", "marble:#ddd5c2", 0, 0, .7, .34, 0, .16), boxr("marble:#e9e3d4", "marble:#efe9dc", 0, 0, .52, .16, .16, 1.5)))
HERM = part("herm", lambda: (boxr("marble:#e3dccb", "marble:#e3dccb", 0, 0, .3, .26, 0, 1.45), lathe("marble:#ece6d8", 0, 0, [(.1, 1.45), (.14, 1.55), (.13, 1.7), (.05, 1.78)], 8)))
BASE = part("base", lambda: (boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 1.5, 1.5, 0, .25), boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, 1.25, 1.25, .25, 1.0)))
VOTIVE = part("votive_column", lambda: (boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 1.05, 1.05, 0, .3), lathe("marble:#ece6d8", 0, 0, [(.34, .3), (.26, 4.3), (.4, 4.55)], 12),
                                        boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, .86, .86, 4.55, 4.75),
                                        lathe("gold", 0, 0, [(.28, 4.75), (.34, 5.1), (.18, 5.35)], 10, cap_top=True),
                                        beam("bronze", (-.26, -.26, 4.75), (-.14, -.14, 5.25), .03, 5),
                                        beam("bronze", (.26, -.26, 4.75), (.14, -.14, 5.25), .03, 5),
                                        beam("bronze", (0, .32, 4.75), (0, .18, 5.25), .03, 5)))
def _tripod():
    """A bronze Delphic tripod cauldron on a marble plinth."""
    boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 1.15, 1.15, 0, .24)
    boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, .92, .92, .24, .58)
    for k in range(3):
        a = k * 2 * math.pi / 3 + math.pi / 6
        beam("bronze", (.34 * math.cos(a), .34 * math.sin(a), .58), (.24 * math.cos(a), .24 * math.sin(a), 1.48), .035, 6)
    lathe("bronze", 0, 0, [(.08, 1.18), (.34, 1.38), (.38, 1.56), (.34, 1.62)], 12, cap_top=True)
    lathe("gold", 0, 0, [(.36, 1.56), (.4, 1.62), (.36, 1.65)], 12)
    for s in (-1, 1):
        beam("gold", (s * .35, 0, 1.62), (s * .44, 0, 1.88), .025, 5)
TRIPOD = part("tripod", _tripod)
def _basin():
    """A marble perirrhanterion (purification water basin) on a fluted pedestal."""
    boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, .9, .9, 0, .16)
    lathe("marble:#ece6d8", 0, 0, [(.26, .16), (.16, .55), (.18, .92), (.56, 1.06), (.6, 1.18), (.52, 1.18), (.46, 1.08)], 14)
    cyl("pool", 0, 0, .48, 1.11, 1.13, 14)
BASIN = part("basin", _basin)
def _brazier():
    """A bronze tripod brazier with charcoal embers."""
    boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, .75, .75, 0, .14)
    for k in range(3):
        a = k * 2 * math.pi / 3
        beam("bronze", (.24 * math.cos(a), .24 * math.sin(a), .14), (.2 * math.cos(a), .2 * math.sin(a), .92), .028, 6)
    lathe("bronze", 0, 0, [(.06, .74), (.3, .9), (.34, 1.04), (.28, 1.04)], 12, cap_top=True)
    cyl("fire" if core.NIGHT else "paint:#9e3a18", 0, 0, .24, .98, 1.04, 10)
BRAZIER = part("brazier", _brazier)
def _equestrian():
    """An honorific bronze equestrian monument on a high stepped marble pedestal."""
    boxr("marble:#d9d0bd", "marble:#e4dcc9", 0, 0, 1.8, 3.0, 0, .3)
    boxr("marble:#e6dfcf", "marble:#ece6d8", 0, 0, 1.35, 2.4, .3, 1.95)
    boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, 1.55, 2.65, 1.95, 2.15)
    # horse body, neck, head, four legs, and rider
    beam("bronze", (0, -.65, 3.05), (0, .65, 3.12), .28, 8)
    beam("bronze", (0, .55, 3.15), (0, .95, 3.85), .16, 7)
    beam("bronze", (0, .92, 3.82), (0, 1.25, 3.65), .11, 6)
    for sx, sy in ((-.18, -.58), (.18, -.58), (-.18, .55)): beam("bronze", (sx, sy, 2.15), (sx, sy, 3.0), .06, 6)
    beam("bronze", (.18, .55, 3.0), (.18, .85, 2.55), .055, 6)
    with core.placed(0, -.05, 0, 3.2): _figure("bronze", 1.55)
EQUESTRIAN = part("equestrian", _equestrian)
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
STALLS = [part("stall%d" % i, _stall(c)) for i, c in enumerate(("#d9ceb4", "#cfc3a4", "#b0563a", "#d4c9ad", "#7d8fa0", "#c8b98f", "#a9553c", "#5f7896", "#c9a544", "#8a4a3a"))]
def _sundial():
    """A marble column 1.5 m tall carrying a dial block cut with a concave hollow on its south face."""
    boxr("marble:#ddd5c2", "marble:#e6dfcf", 0, 0, .74, .74, 0, .18)
    lathe("marble:#ece6d8", 0, 0, [(.24, .18), (.21, .28), (.17, 1.38), (.24, 1.50)], 12)
    boxr("marble:#e6dfcf", "marble:#ece6d8", 0, .06, .58, .36, 1.50, 2.02)
    for sx in (-1, 1): boxr("marble:#e6dfcf", "marble:#ece6d8", sx * .23, -.19, .12, .14, 1.50, 2.02)
    boxr("marble:#e6dfcf", "marble:#ece6d8", 0, -.19, .34, .14, 1.50, 1.60)
    boxr("marble:#e6dfcf", "marble:#ece6d8", 0, -.19, .34, .14, 1.92, 2.02)
    n = 6
    for k in range(n):
        t0, t1 = -1 + 2 * k / n, -1 + 2 * (k + 1) / n
        x0, x1 = .17 * t0, .17 * t1; y0, y1 = -.20 + .15 * (1 - t0 * t0), -.20 + .15 * (1 - t1 * t1)
        face("marble:#9c927d", [(x0, y0, 1.60), (x1, y1, 1.60), (x1, y1 + .03, 1.92), (x0, y0 + .03, 1.92)])
    beam("bronze", (0, -.06, 1.90), (0, -.29, 1.76), .016, 5)
SUNDIAL = part("sundial", _sundial)
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
def _cart_amph():
    _cart()
    boxr("straw:#d1b262", "straw:#dcbf6c", 0, 0, 2.28, 1.24, .90, 1.08)
    for x in (-.81, -.27, .27, .81):
        for y in (-.40, 0.0, .40):
            lathe("clay:#b4683e", x, y, [(r, z + .98) for r, z in AMPH_PROF], 10, cap_top=True, cap_bot=False)
def _cart_sacks():
    _cart()
    prof = [(r * 1.15, z * .9) for r, z in SACK_PROF]
    for k, z0 in enumerate((.90, 1.44)):
        for i, x in enumerate((-.54, .54)):
            for j, y in enumerate((-.30, .30)):
                key = "cloth:#c9b68e" if (i + j + k) % 2 == 0 else "cloth:#baa57a"
                lathe(key, x * (1 - k * .08), y * (1 - k * .08), [(r, z + z0) for r, z in prof], 8, cap_top=True, cap_bot=False)
def _cart_hay():
    _cart()
    rings = [(1.18, .65, .90), (1.26, .78, 1.32), (1.16, .74, 1.72), (.84, .54, 2.04), (.36, .24, 2.22), (.05, .04, 2.28)]
    n = 14; V = []; Fc = []
    for rx, ry, z in rings:
        V += [(rx * math.cos(2 * math.pi * i / n), ry * math.sin(2 * math.pi * i / n), z) for i in range(n)]
    for k in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n; Fc.append((k * n + i, k * n + j, (k + 1) * n + j, (k + 1) * n + i))
    mesh("straw:#d1b262", V, Fc, smooth=True)
    face("straw:#d1b262", V[-n:])
CART_AMPH = part("cart_amph", _cart_amph)
CART_SACKS = part("cart_sacks", _cart_sacks)
CART_HAY = part("cart_hay", _cart_hay)
def _hull(L, B, D, secs, outer, inner, deck_z, rocker=.25, stern=0.0, upper=None, band_t=.5):
    prev = None; prev_d = None
    for i in range(secs + 1):
        t = i / secs; x = (t - .5) * L; hw = B / 2 * math.sin(math.pi * min(1, t * 1.03)) ** .6 + .03; sh = rocker * (2 * t - 1) ** 2 + (stern * max(0, t - .85) / .15) ** 2
        p0, p1, p2, p3, p4 = (x, -hw, D + sh), (x, -hw * .88, D * .42), (x, 0, 0), (x, hw * .88, D * .42), (x, hw, D + sh)
        if upper:
            q0 = (x, p1[1] + (p0[1] - p1[1]) * band_t, p1[2] + (p0[2] - p1[2]) * band_t)
            q4 = (x, p3[1] + (p4[1] - p3[1]) * band_t, p3[2] + (p4[2] - p3[2]) * band_t)
            sec = [p0, q0, p1, p2, p3, q4, p4]
        else:
            sec = [p0, p1, p2, p3, p4]
        if prev:
            for k in range(len(sec) - 1):
                key = upper if (upper and k in (0, len(sec) - 2)) else outer
                face(key, [prev[k], sec[k], sec[k + 1], prev[k + 1]][::-1])
            face(inner, [(prev_d[0][0], prev_d[0][1] * 1.08, deck_z), (p1[0], p1[1] * 1.08, deck_z), (p3[0], p3[1] * 1.08, deck_z), (prev_d[1][0], prev_d[1][1] * 1.08, deck_z)])
        prev = sec; prev_d = (p1, p3)
def _boat(lower="wood:#5f4129", upper=None):                                              # a fishing boat: planked hull, thwarts, a short mast with its yard lowered
    _hull(6.5, 1.9, .8, 14, lower, "wood:#a08257", .45, upper=upper, band_t=0.0)
    for xx in (-1.2, .3, 1.6): boxr("wood:#8a6a44", "wood:#8a6a44", xx, 0, .2, 1.5, .62, .7)
    beam("wood:#6b5032", (.2, 0, .5), (.2, 0, 3.4), .06); beam("wood:#6b5032", (-1.9, .25, .95), (2.2, .25, 1.1), .05)
    beam("cloth:#d8cdb2", (-1.6, .32, 1.05), (1.9, .32, 1.2), .12, 6)
BOAT = part("boat", _boat)
BOAT_BLACK = part("boat_black", lambda: _boat("wood:#2a2420"))
BOAT_RED = part("boat_red", lambda: _boat("wood:#5f4129", "wood:#8a3a26"))
BOATS = (BOAT, BOAT_BLACK, BOAT_RED)
def _ship(lower="wood:#4a321f", upper=None):                                              # a round merchantman, sail furled on its yard, steering oars at the stern
    D = 2.3; _hull(16, 5.0, D, 22, lower, "wood:#a98860", D - .15, .8, 1.5, upper=upper, band_t=.5)
    boxr("wood:#7a5a38", "wood:#8f6a42", -5.3, 0, 2.8, 3.0, D - .15, D + 1.0)
    beam("wood:#5b4128", (.8, 0, D), (.8, 0, D + 9.5), .17); beam("wood:#5b4128", (.8, -5.0, D + 8.8), (.8, 5.0, D + 8.8), .1)
    beam("cloth:#d9ceb4", (.95, -4.6, D + 8.55), (.95, 4.6, D + 8.55), .28, 7)
    for s in (-1, 1): beam("wood:#6b4a2c", (-6.6, s * 2.0, D + .6), (-8.2, s * 2.6, -.9), .07); beam("wood:#3a2a1e", (.8, 0, D + 9.3), (7.4 , s * .2, D + 1.0), .02, 4); beam("wood:#3a2a1e", (.8, 0, D + 9.3), (-7.2, s * .2, D + 1.6), .02, 4)
SHIP = part("ship", _ship)
SHIP_RED = part("ship_red", lambda: _ship("wood:#2a2420", "wood:#8a3a26"))
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
def _timber():
    for k, n in enumerate((4, 3, 1)):
        for j in range(n): beam("wood:#9a7c54", (-3.0, (j - (n - 1) / 2) * .28, .125 + k * .23), (3.0, (j - (n - 1) / 2) * .28, .125 + k * .23), .125, 7)
TIMBER = part("timber", _timber)
def _cauldron():
    for k in range(3):
        a = k * 2 * math.pi / 3
        lathe("rubble:#7a7468", .33 * math.cos(a), .33 * math.sin(a), [(.14, -.04), (.16, .12), (.11, .26)], 7)
    lathe("dark:#25201c", 0, 0, [(.18, .18), (.38, .32), (.40, .52), (.34, .68), (.38, .72)], 12, cap_top=False)
    cyl("dark:#14110f", 0, 0, .33, .58, .61, 12)
CAULDRON = part("cauldron", _cauldron)
def _anchor():
    n = 8; ri = .12; hx, hy = 0.0, .12
    out = [(.42 * (1 - .22 * math.sin(2 * math.pi * k / n)) * math.cos(2 * math.pi * k / n),
            .42 * (1 - .22 * math.sin(2 * math.pi * k / n)) * math.sin(2 * math.pi * k / n)) for k in range(n)]
    inn = [(hx + ri * math.cos(2 * math.pi * k / n), hy + ri * math.sin(2 * math.pi * k / n)) for k in range(n)]
    for k in range(n):
        j = (k + 1) % n
        face("rubble:#9b9483", [(out[k][0], out[k][1], .18), (out[j][0], out[j][1], .18), (inn[j][0], inn[j][1], .18), (inn[k][0], inn[k][1], .18)])
        face("rubble:#9b9483", [(out[k][0], out[k][1], -.02), (out[j][0], out[j][1], -.02), (out[j][0], out[j][1], .18), (out[k][0], out[k][1], .18)])
        face("rubble:#8a8373", [(inn[k][0], inn[k][1], .18), (inn[j][0], inn[j][1], .18), (inn[j][0], inn[j][1], -.02), (inn[k][0], inn[k][1], -.02)])
ANCHOR = part("anchor", _anchor)
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
def _hive():
    """A horizontal terracotta tube hive (0.6 m long, 0.3 m across), one end dark."""
    beam("clay:#b4683e", (0, -.3, .15), (0, .3, .15), .15, 10)
    pts = [(.115 * math.cos(2 * math.pi * k / 10), -.304, .15 + .115 * math.sin(2 * math.pi * k / 10)) for k in range(10)]
    core.oriented("dark:#1c1712", pts, (0, -1, 0))
HIVE = part("hive", _hive)
def _oven():
    """A domed clay bread oven on a rubble base, with a dark mouth on the south side."""
    lathe("rubble:#b9ad94", 0, 0, [(.96, -.08), (.96, .40)], 14, smooth=False, cap_top=True, cap_bot=False)
    prof = [(.90 * math.cos(t), .40 + 1.10 * math.sin(t)) for t in (0.0, .26, .52, .78, 1.04, 1.30, 1.50)] + [(.04, 1.50)]
    lathe("clay:#b89a78", 0, 0, prof, 16, smooth=True, cap_top=True, cap_bot=False)
    boxr("clay:#a88968", "clay:#a88968", 0, -.86, .66, .22, .40, .96)
    face("dark:#1c1712", [(-.24, -.98, .42), (.24, -.98, .42), (.20, -.98, .86), (-.20, -.98, .86)])
OVEN = part("oven", _oven)
def _olive_mill():
    """An Olynthian trapetum: round stone basin, central post, two half-round crushing stones joined by a wooden bar."""
    lathe("rubble:#b9ad94", 0, 0, [(.90, -.05), (.90, .50)], 18, smooth=False, cap_top=False, cap_bot=False)
    lathe("paving:#c4b89e", 0, 0, [(.90, .50), (.74, .50), (.70, .24), (.02, .24)], 18, smooth=False, cap_top=False, cap_bot=False)
    cyl("rubble:#a89c84", 0, 0, .18, .24, .88, 10)
    boxr("wood:#5b3f26", "wood:#5b3f26", 0, 0, .26, .26, .72, .86)
    n = 14; cy_z = .76
    secs = [(.34, .50), (.48, .50), (.58, .33), (.62, .06)]
    for s in (-1, 1):
        rings = [[(s * x, r * math.cos(2 * math.pi * i / n), cy_z + r * math.sin(2 * math.pi * i / n)) for i in range(n)] for x, r in secs]
        core.oriented("ashlar:#b5ab96", rings[0], (-s, 0, 0))
        core.oriented("ashlar:#b5ab96", rings[-1], (s, 0, 0))
        for a, b in zip(rings, rings[1:]):
            for i in range(n):
                j = (i + 1) % n
                q = [a[i], a[j], b[j], b[i]]
                mid = ((a[i][0] + b[i][0]) * .5 - s * .34, (a[i][1] + a[j][1]) * .5, (a[i][2] + a[j][2]) * .5 - cy_z)
                core.oriented("ashlar:#b5ab96", q, mid)
    beam("wood:#6b5032", (-1.35, 0, .76), (1.35, 0, .76), .065, 8)
OLIVE_MILL = part("olive_mill", _olive_mill)
def _trough():
    """A stone water trough (2.2 x 0.6 x 0.5 m) with water just below the rim."""
    boxr("rubble:#b9ad94", "paving:#c4b89e", 0, 0, 2.2, .6, -.05, .14)
    for sy in (-1, 1): boxr("rubble:#b9ad94", "paving:#cfc5ac", 0, sy * .24, 2.2, .12, .14, .50)
    for sx in (-1, 1): boxr("rubble:#b9ad94", "paving:#cfc5ac", sx * 1.04, 0, .12, .36, .14, .50)
    face("pool", [(-.98, -.18, .44), (.98, -.18, .44), (.98, .18, .44), (-.98, .18, .44)])
TROUGH = part("trough", _trough)
def _tile_stack():
    """A neat stack of fired roof tiles (0.9 x 0.6 x 0.6 m) with dark lines across the top."""
    boxr("clay:#b8754f", "clay:#b8754f", 0, 0, .9, .6, 0, .6)
    for x in (-.22, 0.0, .22):
        boxr("dark:#3a2216", "dark:#3a2216", x, 0, .045, .58, .59, .625)
TILE_STACK = part("tile_stack", _tile_stack)
def _faggots():
    """A tied bundle of brushwood (1.5 m long, 0.4 m across) for kiln fuel."""
    beam("bark:#7a6a50", (-.73, 0, .20), (.73, 0, .20), .12, 7)
    for dy, dz, a, b in ((0, .105, -.75, .74), (0, -.105, -.72, .75), (.105, 0, -.74, .72), (-.105, 0, -.75, .75)):
        beam("bark:#7a6a50", (a, dy, .20 + dz), (b, dy * .9, .20 + dz * .9), .095, 6)
    for xb in (-.38, .38):
        beam("dark:#3a2e20", (xb - .03, 0, .20), (xb + .03, 0, .20), .206, 10)
FAGGOTS = part("faggots", _faggots)
def _basket_grape():
    """A 1.4x harvest basket heaped with dark purple grapes."""
    k = 1.4
    lathe("straw:#b99a5a", 0, 0, [(.22 * k, 0), (.30 * k, .30 * k), (.33 * k, .42 * k)], 10, cap_top=False, cap_bot=False)
    lathe("flat:#3d1f33", 0, 0, [(.315 * k, .39 * k), (.315 * k, .425 * k), (.19 * k, .465 * k), (.03 * k, .48 * k)], 10, cap_top=True, cap_bot=False)
BASKET_GRAPE = part("basket_grape", _basket_grape)
PITHOS_LID = part("pithos_lid", lambda: cyl("paving:#cfc5ac", 0, 0, .36, 0, .06, 14, smooth=False))
def _stakes():
    """A stack of twenty 2 m vine stakes (0.5 m high)."""
    rg = random.Random(19)
    for row, n in enumerate((6, 5, 5, 4)):
        z = .062 + row * .118
        for j in range(n):
            y = (j - (n - 1) / 2) * .132 + rg.uniform(-.01, .01)
            x0, x1 = -1.0 + rg.uniform(-.05, .05), 1.0 + rg.uniform(-.05, .05)
            beam("wood:#8a7352", (x0, y, z), (x1, y, z), .062, 6)
STAKES = part("stakes", _stakes)
def _watch_hut():
    """A vineyard watchman's shelter: four 2.2 m posts carrying a slightly sloped 2.5 x 2.5 m reed roof."""
    z_lo, z_hi = 2.15, 2.38
    for x in (-1.0, 1.0):
        for y in (-1.0, 1.0):
            beam("wood:#6b5032", (x, y, -.35), (x, y, z_lo if y < 0 else z_hi), .08, 6)
    for y, zh in ((-1.0, z_lo), (1.0, z_hi)):
        beam("wood:#6b5032", (-1.15, y, zh), (1.15, y, zh), .06, 6)
    for x in (-1.0, 0.0, 1.0):
        beam("wood:#7d5d3c", (x, -1.2, z_lo + .05), (x, 1.2, z_hi + .05), .05, 6)
    t = .14
    b = [(-1.25, -1.25, z_lo + .05), (1.25, -1.25, z_lo + .05), (1.25, 1.25, z_hi + .05), (-1.25, 1.25, z_hi + .05)]
    u = [(p[0], p[1], p[2] + t) for p in b]
    face("straw:#b9a56a", u); face("straw:#b9a56a", b[::-1])
    for i in range(4):
        j = (i + 1) % 4; face("straw:#b9a56a", [b[i], b[j], u[j], u[i]])
WATCH_HUT = part("watch_hut", _watch_hut)
def _swape_well():
    """A country well with a counterweighted lifting pole (kelon/shaduf): 2 m stone kerb, 4 m forked post, 7 m tilted pole."""
    lathe("rubble:#c2b69a", 0, 0, [(1.02, -.25), (.96, .54), (1.03, .62), (1.03, .70), (.68, .70), (.68, .60)], 16, smooth=False, cap_top=False, cap_bot=False)
    cyl("dark:#14110f", 0, 0, .70, .60, .64, 14)
    beam("wood:#6b5032", (-3.45, 0, -.35), (-3.45, 0, 3.55), .125, 8)
    for sy in (-1, 1): beam("wood:#6b5032", (-3.45, 0, 3.35), (-3.45, sy * .26, 4.15), .09, 7)
    beam("wood:#b59a6a", (-5.37, 0, 2.19), (0.0, 0, 6.69), .10, 8)
    boxr("rubble:#9b9483", "paving:#c4b89e", -5.20, 0, .70, .70, 1.35, 2.05)
    beam("wood:#5b3f26", (-5.20, 0, 2.05), (-5.20, 0, 2.38), .05, 6)
    beam("straw:#b9a56a", (0, 0, 6.69), (0, 0, 2.05), .04, 6)
    for sx in (-1, 1): beam("wood:#5b3f26", (sx * .22, 0, 1.92), (0, 0, 2.12), .028, 5)
    lathe("wood:#8c6a44", 0, 0, [(.18, 1.45), (.24, 1.95), (.21, 1.95), (.16, 1.50)], 10, cap_top=False, cap_bot=True)
    cyl("pool", 0, 0, .20, 1.80, 1.84, 10)
SWAPE_WELL = part("swape_well", _swape_well)
def _rake():
    """A wooden salt-pan rake (2 m pole with a short cross-piece) lying on the ground."""
    beam("wood:#7a5836", (-1.05, 0, .065), (1.05, 0, .065), .06, 6)
    bar("wood:#5b3f26", (1.0, -.42, .075), (1.0, .42, .075), .10, .11)
RAKE = part("rake", _rake)
def _stook():
    """A stook of eight sheaves stood ears-up and leaning together to dry in the field, a ninth laid over them as a cap."""
    for k in range(8):
        a = 2 * math.pi * k / 8 + (.12 if k % 2 else 0)
        beam("straw:#d6b964", (.46 * math.cos(a), .46 * math.sin(a), -.02), (.09 * math.cos(a), .09 * math.sin(a), 1.02), .12, 6)
    lathe("straw:#c9a956", 0, 0, [(.34, .9), (.27, 1.1), (.14, 1.24), (.03, 1.3)], 9, cap_top=True)
STOOK = part("stook", _stook)
def _sheaf_lying():
    """A bound sheaf laid flat where the reaper dropped it, ears to one end."""
    beam("straw:#d8bc68", (-.55, 0, .13), (.2, 0, .13), .13, 7); beam("straw:#c9aa58", (.2, 0, .14), (.62, 0, .16), .19, 7)
    beam("dark:#4a3b2a", (-.08, 0, .13), (.0, 0, .13), .145, 7)
SHEAF_LYING = part("sheaf_lying", _sheaf_lying)
def _ard():
    """A Greek ard left at the furrow's end: the share-beam on the ground with its iron tip, the stilt and handle, the long pole
    running forward to the yoke, laid on the soil until the oxen come back."""
    bar("wood:#6b5032", (-.55, 0, .08), (.45, 0, .05), .12, .11)
    beam("dark:#3a3631", (.42, 0, .05), (.66, 0, .03), .045, 5)
    beam("wood:#6b5032", (-.45, 0, .1), (-.95, 0, 1.0), .045, 6); beam("wood:#6b5032", (-.98, -.22, 1.0), (-.92, .22, 1.02), .035, 5)
    beam("wood:#7d5d3c", (-.25, 0, .14), (2.95, 0, .12), .055, 6)
    bar("wood:#5b3f26", (2.95, -.78, .09), (2.95, .78, .09), .11, .1)
    for s in (-1, 1): beam("wood:#5b3f26", (2.85, s * .42, .1), (2.85, s * .42, .42), .025, 4); beam("wood:#5b3f26", (3.05, s * .42, .1), (3.05, s * .42, .42), .025, 4)
ARD = part("ard", _ard)

def jars(cx, cy, z, n, r, g, kinds=(AMPH, AMPH, AMPH, PITHOS, HYDRIA), check=True):
    """A cluster of jars on the ground, a few tipped over."""
    for k in range(n):
        a = g.uniform(0, 6.3); d = r * math.sqrt(g.random()); x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        if check and not land.free(x, y): continue
        m = g.choice(kinds); tip = g.random() < .15 and m is not PITHOS
        inst(m, x, y, (land.zt(x, y) if z is None else z) + (.18 if tip else 0), g.uniform(0, 6.3), g.uniform(.9, 1.15), tilt=(g.uniform(1.3, 1.5), 0) if tip else None)
def jar_rows(x0, y0, x1, y1, z, g, gap=.46, kind=AMPH, sc=1.0):
    """Amphorae stood in rows, as in a store or a potter's drying yard."""
    y = y0
    while y < y1:
        x = x0
        while x < x1:
            zz = land.zt(x, y) if z is None else z
            inst(kind, x + g.uniform(-.04, .04), y, zz, g.uniform(0, 6.3), sc * g.uniform(.95, 1.05)); x += gap
        y += gap
