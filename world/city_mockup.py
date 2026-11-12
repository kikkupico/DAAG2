"""SVG mockup of the walled city: a top-down plan (north up) and the same plan seen from the southeast, as in the concept.
Plan coordinates are metres, x east, y north, origin at the crossroads.
Run: python3 world/city_mockup.py world/plan/city-plan.svg [--app app/js/data/city.js]
     python3 world/city_mockup.py --siege world/plan/siege-plan.svg [--app app/js/data/siege.js]
--siege draws the soldiers' world instead: the same land, a flat walled town with its gates shut, and four camps round it
(the commander's to the north, A, B and C to the east, south and west), linked only by the road round the walls.
With --app it also writes the page's city stage: the southeast picture alone (baked to app/img/<view>-<width>.webp, which needs
Google Chrome and cwebp), where each place is in it, and the road route between every pair of places, lifted onto the stairs and
terraces, all in the picture's own pixels. The page's city is made with --detail; the siege with --siege --night --detail."""
import math, sys, heapq, random

R2 = math.sqrt(2)
ELEV = math.asin(0.75)            # camera height above the horizon: makes the axes run along a 4:3 frame's diagonals
CAM = (1 / R2, -1 / R2)          # where the camera stands, seen from the crossroads: the southeast
UP = (-CAM[0], -CAM[1]); RIGHT = (UP[1], -UP[0])   # the picture's up and right, on the ground
L = 215                           # the four axis ends (N, E, S, W) sit at the overview's corners, this far from the crossroads
random.seed(3)
SIEGE = "--siege" in sys.argv
if SIEGE: sys.argv.remove("--siege")
DETAIL = "--detail" in sys.argv                                           # the detail pass, so far only in the acropolis corner
if DETAIL: sys.argv.remove("--detail")
def detailed(x, y): return DETAIL
NIGHT = "--night" in sys.argv                                             # a moonlit night: every colour is cooled and darkened, then lights are added
if NIGHT: sys.argv.remove("--night")
LIGHTS = {"#fff1c4", "#ffb347", "#ffcf6e", "#cfe3ff", "#ff8c2a"}           # colours that are light sources: the night leaves them alone
GLOWS = []
GROUND = "#b4bf88" if SIEGE else "#cfd8a4"                                # rough meadow round the siege; greener fields round the city                                                                # (x, y, z, radius in metres, kind): warm light spilling on whatever is near
SUN = (0.958, 0.287)                                                      # the way shadows fall: the sun is low in the west-southwest
SHADOWS = "--no-shadows" not in sys.argv                                  # cast shadows, on by default: side by side they look better than without
if not SHADOWS: sys.argv.remove("--no-shadows")

def shade(hex_, f):
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))
def depth(x, y): return x * UP[0] + y * UP[1]                               # larger is further from the camera
def inpoly(x, y, P):
    c = False
    for (ax, ay), (bx, by) in zip(P, P[1:] + P[:1]):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay): c = not c
    return c

# ------------------------------------------------------------------ the city
W, C = 78, 26                     # wall half-width (flat to flat) and corner chamfer
A, B = W, 2 * W - C               # octagon: |x| <= A, |y| <= A, |x| + |y| <= B
def octagon(d=0):
    a, b = A + d, B + d * R2
    return [(a, -(b - a)), (a, b - a), (b - a, a), (-(b - a), a), (-a, b - a), (-a, -(b - a)), (-(b - a), -a), (b - a, -a)]

def shore(x):                     # the south coast; it turns north past the pottery and falls away to the southeast
    y = -140 + 5 * math.sin(x / 23)
    if x < -40: y += 0.32 * (-40 - x)
    if x > 40: y -= 0.004 * (x - 40) ** 2
    return y

# ------------------------------------------------------------------ the acropolis
# Five terraces of rock, 3 m each, and a dressed-stone summit 20 m up. The lower terraces run into the north quarters,
# so the town climbs the hill; the city wall leaves the octagon and wraps the hill, standing on the lowest terrace's edge.
TOP = 20
HILL_C = (0, 122)
PRECINCT = [(24, 104), (46, 112), (44, 152), (-44, 152), (-46, 112), (-24, 104)]
_ph = [random.Random(7).uniform(0, 6.3) for _ in range(3)]
def hill_f(a): return 1 + .04 * math.sin(3 * a + _ph[0]) + .025 * math.sin(7 * a + _ph[1]) + .015 * math.sin(13 * a + _ph[2])
def outline(rx, rys, ryn, a0=0, a1=360, n=90):
    """A rough ellipse round the hill: south radius rys, north radius ryn; every outline shares the same wobble, so they nest."""
    pts = []
    for i in range(n + (0 if a1 - a0 == 360 else 1)):
        a = math.radians(a0 + (a1 - a0) * i / n); f = hill_f(a); ry = ryn if math.sin(a) > 0 else rys
        pts.append((HILL_C[0] + rx * f * math.cos(a), HILL_C[1] + ry * f * math.sin(a)))
    return pts
ROCK = ["#bdb194", "#c3b79b", "#c9bea2", "#cfc4a9", "#d4cab0"]
TIERS = []                                                                # outline, base, height, top colour
for k in range(5):
    t = k / 4
    TIERS.append((outline(90 - 24 * t, 76 - 30 * t, 64 - 18 * t), 3 * k, 3, ROCK[k]))
WALL_N = outline(86, 72, 60, -25, 205, 64)                                # the wall, 4 m inside the lowest terrace's edge
RING_N = outline(102, 88, 76, -25, 205, 64)                               # the road outside it, 12 m beyond the edge
STAIR = dict(w=7, y0=40, y1=104)                                          # the broad stair, up the line of the main street
POSTERN = min(WALL_N, key=lambda p: math.hypot(p[0] + 90, p[1] - 114))    # a small gate in the west wall
WEST_STAIR = dict(y=114, x0=-46, x1=POSTERN[0])                          # a narrow stair down the far side to it
if SIEGE: TIERS, PRECINCT = [], []                                        # the besieged town is flat
CAMPS = {"commander's camp": ((0, 158), (0, 144)), "camp A": ((158, 0), (144, 0)), "camp B": ((0, -116), (0, -104)), "camp C": ((-158, 0), (-144, 0))}   # centre, gate

def zat(x, y):
    """Ground height: only the acropolis stands up."""
    if PRECINCT and inpoly(x, y, PRECINCT): return TOP
    for p, z0, h, _ in TIERS[::-1]:
        if inpoly(x, y, p): return z0 + h
    return 0

# ------------------------------------------------------------------ places
GROUP = {"merchants": "#c0602a", "legislators": "#2f62b8", "scholars": "#25875c", "common": "#555"}
PLACES = {   # label position, door on the road network, group, second line (role)
    "temple":     dict(at=(8, 146), door=(0, 114), group="legislators", sub=None),
    "library T":  dict(at=(-30, 112), door=(-32, 114), group="scholars", sub="library in the precinct", name="temple library"),
    "granary":    dict(at=(160, 0), door=(150, 0), group="merchants", sub="legislator B"),
    "winery":     dict(at=(-158, 4), door=(-148, 0), group="merchants", sub="legislator C"),
    "fishery":    dict(at=(-8, -120), door=(0, -114), group="merchants", sub="legislator A"),
    "pottery":    dict(at=(-88, -88), door=(-80, -80), group="merchants", sub=None),
    "library NW": dict(at=(-106, 64), door=(-99, 64), group="scholars", sub=None, name="northwest library"),
    "library SE": dict(at=(88, -88), door=(80, -80), group="scholars", sub=None, name="southeast library"),
    "proposer P": dict(at=(-47.5, 28.5), door=(-38, 28.5), group="legislators", sub=None),
    "proposer Q": dict(at=(47.5, -28.5), door=(38, -28.5), group="legislators", sub=None),
}
if SIEGE:
    GROUP["soldiers"] = "#a23b2a"
    PLACES = {k: dict(at=c, door=g, group="soldiers", sub=None) for k, (c, g) in CAMPS.items()}
    PLACES["enemy city"] = dict(at=(0, 30), door=(0, 0), group="common", sub=None)

# ------------------------------------------------------------------ roads: (width, kind, points)
ROADS = []
def road(w, kind, *pts): ROADS.append((w, kind, list(pts)))
if SIEGE:      # streets inside the walls go nowhere outside them: the gates are shut, so camps can only go round
    road(8, "street", (0, -W), (0, W)); road(8, "street", (-W, 0), (W, 0))
    for s_ in (-38, 38): road(5, "street", (s_, -W + 4), (s_, W - 4)); road(5, "street", (-W + 4, s_), (W - 4, s_))
    oc5 = octagon(-5); road(3.5, "street", *oc5, oc5[0])
    ring = octagon(12)
    road(6, "road", (90, 0), ring[1], ring[2], (0, 90), ring[3], ring[4], (-90, 0), ring[5], ring[6], (0, -90), ring[7], ring[0], (90, 0))
    road(6, "road", (0, 90), CAMPS["commander's camp"][1]); road(6, "road", (90, 0), CAMPS["camp A"][1])
    road(6, "road", (0, -90), CAMPS["camp B"][1]); road(6, "road", (-90, 0), CAMPS["camp C"][1])
else:
    road(8, "street", (0, -W), (0, STAIR["y0"])); road(8, "street", (-W, 0), (W, 0))          # the main cross; north of the cross street it becomes the stair
    for s in (-38, 38):
        road(5, "street", (s, -W + 4), (s, 72)); road(5, "street", (-W + 4, s), (W - 4, s))
    oc5 = octagon(-5); road(3.5, "street", (73, 62), oc5[1], oc5[0], oc5[7], oc5[6], oc5[5], oc5[4], (-73, 62))   # lane inside the wall, as far as the hill
    ring = octagon(12)
    road(6, "road", (90, 0), ring[1], *RING_N, ring[4], (-90, 0), ring[5], (-73.5, -73.5), ring[6], (0, -90), ring[7], (73.5, -73.5), ring[0], (90, 0))
    road(6, "road", (W, 0), (150, 0)); road(6, "road", (-W, 0), (-148, 0)); road(6, "road", (0, -W), (0, -114))
    road(4, "road", (-88, 64), (-99, 64)); road(4, "road", (73.5, -73.5), (80, -80)); road(4, "road", (-73.5, -73.5), (-80, -80))
    road(5, "road", (-80, -80), (-74, -104), (-40, -120), (0, -114))                         # coast path, pottery to fishery
    road(STAIR["w"], "stair", (0, STAIR["y0"]), (0, STAIR["y1"]))                             # up the broad stair
    road(5, "paving", (0, STAIR["y1"]), (0, 114), (WEST_STAIR["x0"], 114))                   # across the summit to its west gate
    road(3, "stair", (WEST_STAIR["x0"], 114), (POSTERN[0] - 24, 114))                         # down the west stair, out the postern, to the ring road

# ------------------------------------------------------------------ solids: footprint, base z, height, colours
SOLIDS, TREES, FLAT = [], [], []
def hall(cx, cy, w, d, z, col_h, roof, ridge="x", cols="all", core=None, steps=True, roof_h=2.6, wall="#f2ece0"):
    """A colonnaded building: steps, a core room, columns on the given sides, a band above them, and a gabled roof."""
    return dict(kind="hall", pts=rect(cx, cy, w, d), z=z, h=(1.5 if steps else 0) + col_h + 1.2 + roof_h, cx=cx, cy=cy, w=w, d=d, col_h=col_h, roof=roof,
                ridge=ridge, cols=cols, core=core, steps=steps, roof_h=roof_h, wall=wall, court=None, shadow=True)
def rect(cx, cy, w, d, rot=0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
def mk(pts, h, roof, z=0, wall="#e9dcc4", court=None): return dict(pts=pts, h=h, z=z, roof=roof, wall=wall, court=court)
def solid(pts, h, roof, z=None, court=None, wall="#e9dcc4"):
    if z is None: z = zat(sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
    SOLIDS.append(mk(pts, h, roof, z, wall, court)); return SOLIDS[-1]
def flat(pts, fill, stroke=None, z=0, rows=None): FLAT.append(dict(pts=pts, fill=fill, stroke=stroke, z=z, rows=rows))

TILE, TILE2 = "#c8673e", "#b5582f"
# houses: four blocks to a quarter, four courtyard houses to a block; the southern corner houses give way to gardens.
# Houses in the north quarters stand on whichever terrace they fall on.
for qx in (-1, 1):
    for qy in (-1, 1):
        for bs in (4, 40.5):
            for bt in (4, 40.5):
                for hx in (7, 24.5):
                    for hy in (7, 24.5):
                        x, y = qx * (bs + hx), qy * (bt + hy)
                        if (y < 0 or SIEGE) and abs(x) + abs(y) > 110: TREES.append((x, y, "olive")); continue
                        if not SIEGE and abs(x) < 12 and y > 40:                                                  # the stair runs up an open court
                            TREES += [(x * 1.05, y - 4, "cypress"), (x * 1.05, y + 4, "cypress")]; continue
                        p = not SIEGE and (x, y) in ((-47.5, 28.5), (47.5, -28.5))      # the proposers' houses
                        hs = solid(rect(x, y, 14, 14), random.choice((6, 6, 7, 8)), "#7f9fdc" if p else random.choice((TILE, TILE2)), court=5)
                        if detailed(x, y): hs.update(hip=True, shadow=True, jar=random.random() < .6, lit=NIGHT and random.random() < .45)

# the wall: the southern five sides of the octagon, then round the hill on the lowest terrace; towers and gates
oct_ = octagon(0)
def wall_run(pts, h=7, z=None, gaps=(), inner=(0, 40), timber=False):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 12))
        for i in range(n):
            a, b = i / n, (i + 1) / n
            p, q = (x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)
            mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if any(math.hypot(mid[0] - g[0], mid[1] - g[1]) < 6 for g in gaps): continue
            dx, dy = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dy); nx, ny = -dy / ln * 1.6, dx / ln * 1.6
            if timber:                                                      # a palisade: thinner, dark wood, no battlements
                k_ = .45 / 1.6; solid([(p[0] + nx * k_, p[1] + ny * k_), (q[0] + nx * k_, q[1] + ny * k_), (q[0] - nx * k_, q[1] - ny * k_), (p[0] - nx * k_, p[1] - ny * k_)], h, "#8a6a48", z=zat(*mid) if z is None else z, wall="#6f5236").update(shadow=DETAIL); continue
            ws = solid([(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)], h, "#d9cdb2", z=zat(*mid) if z is None else z, wall="#cbbd9e")
            if detailed(*mid):
                out = 1 if math.hypot(mid[0] + nx - inner[0], mid[1] + ny - inner[1]) > math.hypot(mid[0] - nx - inner[0], mid[1] - ny - inner[1]) else -1
                k = max(1, int(ln / 2.2)); ang = math.degrees(math.atan2(dy, dx))
                ws.update(shadow=True, merl=[(p[0] + dx * (j + .5) / k + nx * out * .7, p[1] + dy * (j + .5) / k + ny * out * .7, ang) for j in range(k)])
if SIEGE:                                                                # four gates, all shut: the wall runs straight across them
    GATES = [(W, 0), (0, -W), (-W, 0), (0, W)]
    wall_run(oct_ + [oct_[0]], h=8, inner=(0, 0))
    for v in oct_:
        ts = solid(rect(*v, 8, 8, 0), 11, "#d9cdb2", wall="#c4b594")
        if DETAIL: ts.update(shadow=True, merl=[(v[0] + a, v[1] + b, 0) for a in (-3.3, 0, 3.3) for b in (-3.3, 0, 3.3) if a or b])
        GLOWS.append((v[0], v[1], 12, 4.5, "torch"))                         # a torch on every tower
    for gx, gy in GATES: GLOWS.append((gx * .9, gy * .9, 3, 7, "fire"))       # watch fires inside the shut gates
else:
    GATES = [(W, 0), (0, -W), (-W, 0)]
    CIRCUIT = [oct_[4], oct_[5], oct_[6], oct_[7], oct_[0], oct_[1]] + WALL_N + [oct_[4]]
    wall_run(CIRCUIT, gaps=GATES + [POSTERN])
    for v in [oct_[i] for i in (0, 1, 4, 5, 6, 7)] + WALL_N[::8]:
        ts = solid(rect(*v, 8, 8, 0), 10, "#d9cdb2", wall="#c4b594")
        if detailed(*v): ts.update(shadow=True, merl=[(v[0] + a, v[1] + b, 0) for a in (-3.3, 0, 3.3) for b in (-3.3, 0, 3.3) if a or b])
for gx, gy in GATES:
    for s in (-1, 1):
        gt = solid(rect(gx + (s * 8 if gx == 0 else 0), gy + (s * 8 if gy == 0 else 0), 7, 7), 10, "#d9cdb2", wall="#c4b594")
        if detailed(gx, gy): gt.update(shadow=True, merl=[(gt["pts"][0][0] + 3.5 + a, gt["pts"][0][1] + 3.5 + b, 0) for a in (-2.8, 0, 2.8) for b in (-2.8, 0, 2.8) if a or b])
    if detailed(gx, gy) and not SIEGE:                                   # the arch: a lintel across the opening, high enough to walk under
        ar = solid(rect(gx, gy, 9 if gx == 0 else 3.4, 3.4 if gx == 0 else 9), 2.6, "#d9cdb2", z=6.2, wall="#c9bb9c")
        ar.update(merl=[(gx + (a if gx == 0 else 0), gy + (0 if gx == 0 else a), 0) for a in (-3.2, -1, 1, 3.2)])

# on the summit: its wall, the temple, the altar, the temple library, the gatehouse at the head of the stair; then the stairs and estates
if not SIEGE:
    wall_run(PRECINCT + [PRECINCT[0]], h=4, z=TOP, gaps=[(0, 104), (WEST_STAIR["x0"], 116)], inner=(0, 128))
    if DETAIL: SOLIDS.append(hall(8, 132, 30, 16, TOP, 7, "#c8673e", ridge="x", cols="all", core=(0, 0, 21, 8)))       # the temple: peristyle round a cella
    else: solid(rect(8, 132, 30, 16), 10, "#d0603a", z=TOP, wall="#f2ece0")
    solid(rect(8, 117, 6, 3), 1.5, "#e8e2d4", z=TOP)
    if DETAIL: SOLIDS.append(hall(-32, 132, 10, 26, TOP, 5, "#5aa37c", ridge="y", cols="e", core=(-2.2, 0, 4.4, 25), steps=False))   # the library: a stoa open to the east
    else: solid(rect(-32, 132, 10, 26), 7, "#5aa37c", z=TOP, wall="#f2ece0")
    if DETAIL: SOLIDS.append(hall(0, 107, 14, 6, TOP, 4.5, "#c8673e", ridge="x", cols="ns", core=None, steps=False, roof_h=1.6))   # gatehouse at the head of the stair
    else: solid(rect(0, 107, 14, 6), 6, "#e8e2d4", z=TOP, wall="#f2ece0")
    # the broad stair, one prism per step from the street, with parapets; it stands in front of the terraces it cuts through
    N_STEPS = 20
    for i in range(N_STEPS):
        y0 = STAIR["y0"] + (STAIR["y1"] - STAIR["y0"]) * i / N_STEPS; y1 = STAIR["y0"] + (STAIR["y1"] - STAIR["y0"]) * (i + 1) / N_STEPS
        zt = TOP * (i + 1) / N_STEPS; hw = STAIR["w"] / 2
        SOLIDS.append(mk([(-hw, y0), (hw, y0), (hw, y1), (-hw, y1)], zt, "#ece6d8", wall="#e2d9c4" if DETAIL else "#cfc5ae"))
        for sx in (-1, 1):
            x = sx * (hw + .5)
            SOLIDS.append(mk([(x - .5, y0), (x + .5, y0), (x + .5, y1), (x - .5, y1)], zt + 1.2, "#d9cdb2", wall="#c4b594"))
    # the west stair: each step stands on whatever terrace is under it, so the terraces in front of it hide it properly
    for i in range(N_STEPS):
        x0 = WEST_STAIR["x0"] + (WEST_STAIR["x1"] - WEST_STAIR["x0"]) * i / N_STEPS; x1 = WEST_STAIR["x0"] + (WEST_STAIR["x1"] - WEST_STAIR["x0"]) * (i + 1) / N_STEPS
        zt = TOP - (TOP - 3) * (i + 1) / N_STEPS; zb = zat((x0 + x1) / 2, WEST_STAIR["y"])
        SOLIDS.append(mk([(x1, WEST_STAIR["y"] - 2), (x0, WEST_STAIR["y"] - 2), (x0, WEST_STAIR["y"] + 2), (x1, WEST_STAIR["y"] + 2)], max(.4, zt - zb), "#ece6d8", z=zb, wall="#cfc5ae"))

    # estates: granary (east), winery (west), fishery (south), pottery (southwest), the two outer libraries
    if DETAIL: SOLIDS.append(hall(168, 0, 16, 14, 0, 7, TILE, ridge="x", cols="", core=(0, 0, 16, 14), steps=False, roof_h=3.2, wall="#e6d6b8"))   # the granary
    else: solid(rect(168, 0, 16, 14), 9, TILE, wall="#e6d6b8")
    for x, y in ((158, 20), (178, 20), (186, -16), (158, -18)): solid(rect(x, y, 9, 8), 5, TILE2).update(hipr=DETAIL, shadow=DETAIL)
    flat([(150, -30), (195, -30), (195, 30), (150, 30)], "none", "#a08a68")
    FLAT.append(dict(circle=(175, -40, 7), fill="#e3cf8e", stroke="#b49a5a", z=0))          # threshing floor
    if DETAIL: SOLIDS.append(hall(-160, -8, 20, 11, 0, 4, TILE, ridge="x", cols="", core=(0, 0, 20, 11), steps=False, roof_h=2.4, wall="#e6d6b8"))   # the winery's press house
    else: solid(rect(-160, -8, 20, 11), 5, TILE, wall="#e6d6b8")
    for x, y in ((-150, 16), (-172, 16), (-178, -14)): solid(rect(x, y, 9, 8), 5, TILE2).update(hipr=DETAIL, shadow=DETAIL)
    flat([(-188, -26), (-140, -26), (-140, 28), (-188, 28)], "none", "#a08a68")
    if DETAIL: SOLIDS.append(hall(-16, -108, 18, 8, 0, 3.4, TILE, ridge="x", cols="", core=(0, 0, 18, 8), steps=False, roof_h=1.8, wall="#e6d6b8"))   # fishery shed
    else: solid(rect(-16, -108, 18, 8), 4.5, TILE, wall="#e6d6b8")
    for i in range(4): FLAT.append(dict(pts=rect(20 + (i % 2) * 9, -104 - (i // 2) * 7, 7, 5), fill="#9fd0d6", stroke="#7f9a94", z=0))   # salting tanks
    for x in (-30, -2, 22): FLAT.append(dict(pts=rect(x, shore(x) - 10, 3, 22), fill="#a7865b", stroke="#7e6240", z=0))                   # jetties
    for x, y in ((-24, -158), (6, -160), (30, -156), (-50, -146)): FLAT.append(dict(pts=rect(x, y, 3, 9, 20), fill="#7a5a3a", stroke=None, z=0))
    for i in range(3): solid(rect(-34 + i * 5, -112, 0.8, 7), 2.4, "#8a6a48", wall="#8a6a48")   # fish racks
    for x, y in ((-88, -77), (-77, -88)): solid(rect(x, y, 6, 6) if DETAIL else rect(x, y, 7, 7, 45), 3.2 if DETAIL else 5, "#b98a62", wall="#a9774e").update(hipr=DETAIL, shadow=DETAIL)   # kilns, domed                                  # kilns
    if DETAIL: SOLIDS.append(hall(-96, -88, 11, 6, 0, 2.6, "#a7865b", ridge="x", cols="all", core=None, steps=False, roof_h=1.4))   # drying shed, open on all sides
    else: solid(rect(-91, -91, 12, 6, -45), 3.5, "#a7865b", wall="#d8c8a8")
    FLAT.append(dict(pts=[(-112, -86), (-102, -92), (-100, -100), (-112, -98)], fill="#b79d78", stroke="#8c7352", z=0))               # clay pit
    if DETAIL:                                                             # the outer libraries: stoas, open towards the road
        SOLIDS.append(hall(-106, 64, 11, 24, 0, 5, "#5aa37c", ridge="y", cols="e", core=(-2.4, 0, 4.6, 23)))
        SOLIDS.append(hall(92, -92, 24, 11, 0, 5, "#5aa37c", ridge="x", cols="n", core=(0, -2.4, 23, 4.6)))
    else:
        solid(rect(-106, 64, 11, 24), 7, "#5aa37c", wall="#f2ece0")                           # northwest library, by the west wall's ring road
        solid(rect(88, -88, 24, 11, 45), 7, "#5aa37c", wall="#f2ece0")

# the camps: a palisade, rows of tents, the commander's larger tent and standard, cooking fires, on trampled ground
if SIEGE:
    for k, ((cx, cy), (gx, gy)) in CAMPS.items():
        big = k == "commander's camp"; hw, hd = (24, 18) if big else (20, 15)
        FLAT.append(dict(pts=[(cx - hw - 6, cy - hd - 6), (cx + hw + 6, cy - hd - 6), (cx + hw + 6, cy + hd + 6), (cx - hw - 6, cy + hd + 6)], fill="#d6c79c", stroke=None, z=0))
        gate = (gx, gy); fence = [(cx - hw, cy - hd), (cx + hw, cy - hd), (cx + hw, cy + hd), (cx - hw, cy + hd), (cx - hw, cy - hd)]
        wall_run(fence, h=2.6, z=0, gaps=[gate], inner=(cx, cy), timber=True)
        GLOWS.append((gx, gy, 3, 3.5, "torch"))                             # a torch at the camp gate
        for v in fence[:4]: solid(rect(*v, 2.4, 2.4), 3.6, "#7a5a3a", wall="#6b4f33")
        for i in range(-2, 3):
            for j in range(-1, 2):
                x, y = cx + i * 7.5, cy + j * 9
                if abs(i) < 1 and abs(j) < 1: continue
                if DETAIL: SOLIDS.append(hall(x, y, 4.6, 3.4, 0, .9, "#efe4cc", ridge="x", cols="", core=(0, 0, 4.6, 3.4), steps=False, roof_h=1.7, wall="#e2d6bb"))
                else: solid(rect(x, y, 4.6, 3.4), 2.4, "#f1e8d4", wall="#d7cbb0")
        if DETAIL: SOLIDS.append(hall(cx, cy, 8 if big else 6, 6 if big else 4.6, 0, 1.4, "#b5452f", ridge="x", cols="", core=(0, 0, 8 if big else 6, 6 if big else 4.6), steps=False, roof_h=2.4, wall="#e6d8bb"))
        else: solid(rect(cx, cy, 8 if big else 6, 6 if big else 4.6), 3.6 if big else 3, "#b5452f", wall="#e6d8bb")       # the officer's tent
        solid(rect(cx + 6, cy + 4, .6, .6), 9, "#7a5a3a", wall="#6b4f33"); solid(rect(cx + 7.6, cy + 4, 3, .4), 2, "#c0281c", z=7, wall="#a8231a")   # standard
        for fx_, fy_ in ((cx - hw + 6, cy + hd - 5), (cx + hw - 6, cy - hd + 5)):
            FLAT.append(dict(circle=(fx_, fy_, 1.6), fill="#ffb347" if NIGHT else "#e8792c", stroke="#5a3a1e", z=0))
            if NIGHT: FLAT.append(dict(circle=(fx_, fy_, .7), fill="#fff1c4", stroke="#ffb347", z=0)); GLOWS.append((fx_, fy_, 1, 8, "fire"))

# fields, groves, scrub (flat), then trees
if not SIEGE:
    WHEAT = [((104, 32), (146, 120)), ((150, 34), (240, 120)), ((198, -30), (240, 30)), ((104, -120), (150, -34)), ((150, -110), (240, -34))]
    for i, ((x0, y0), (x1, y1)) in enumerate(WHEAT):
        flat([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ("#e6cf7a", "#d9bf62", "#ead98f")[i % 3], "#bfa457", rows=("x" if i % 2 else "y", 3.2) if DETAIL else None)
    VINES = [((-240, -60), (-196, 40)), ((-196, 32), (-120, 50)), ((-140, -66), (-118, 26)), ((-196, -66), (-144, -32)), ((-240, 46), (-200, 110))]
    for (x0, y0), (x1, y1) in VINES:
        flat([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "#c9cf8a", "#9aa35c", rows=("y", 5))
    for _ in range(240):                                                                     # olives on the slopes north of the fields
        x, y = random.uniform(-240, 240), random.uniform(56, 240)
        if (inpoly(x, y, octagon(30)) or any(abs(x - c[0]) < 40 and abs(y - c[1]) < 32 for c, _ in CAMPS.values())) if SIEGE else inpoly(x, y, outline(112, 98, 86)) or (x > 96 and y < 124) or (x < -96 and y < 112 and not (x < -118 and y > 54)): continue
        TREES.append((x, y, "olive"))
    for x, y in ((104, -76), (76, -104), (-84, -64), (64, -88), (30, -96), (-30, -94), (-114, 46), (-114, 82)) if SIEGE else ((104, -76), (76, -104), (-84, -64), (64, -88), (30, -96), (-30, -94), (-114, 46), (-114, 82),     # outside the walls
                 (52, 92), (66, 116), (70, 142), (-60, 86), (-66, 108), (30, 86), (-28, 84), (40, 160), (-40, 162)):  # on the terraces
        TREES.append((x, y, "cypress"))
    for _ in range(60):                                                                      # scrub between the city and the shore
        x, y = random.uniform(40, 240), random.uniform(-200, -100)
        if y > shore(x) + 6 and math.hypot(x - 88, y + 88) > 18 and not (SIEGE and abs(x - 158) < 40 and abs(y) < 32): TREES.append((x, y, "olive"))
else:      # the siege: wilderness all round, scrub and dry grass, woods of round trees and dark pines, boulders; nothing tilled, no sea
    g = random.Random(21)
    def clear(x, y, pad=0):
        if inpoly(x, y, octagon(26 + pad)): return False                                       # the walls and the road round them
        if any(abs(x - c[0]) < 40 + pad and abs(y - c[1]) < 32 + pad for c, _ in CAMPS.values()): return False
        if (abs(x) < 8 + pad and 88 < abs(y) < 150) or (abs(y) < 8 + pad and 88 < abs(x) < 150): return False   # the roads out to the camps
        return abs(x) + abs(y) < 232                                                            # what the overview frame shows, and a little more
    def anywhere():                                                                             # a point in the frame's diamond
        while True:
            x, y = g.uniform(-235, 235), g.uniform(-235, 235)
            if abs(x) + abs(y) < 232: return x, y
    def blob(cx, cy, r, n=14):
        ph = [g.uniform(0, 6.3) for _ in range(3)]
        return [(cx + r * (1 + .22 * math.sin(3 * a + ph[0]) + .12 * math.sin(5 * a + ph[1])) * math.cos(a), cy + r * .8 * (1 + .2 * math.sin(4 * a + ph[2])) * math.sin(a))
                for a in (k / n * 2 * math.pi for k in range(n))]
    for _ in range(110):                                                                        # patches of scrub and dry grass
        x, y = anywhere()
        if clear(x, y, 6): flat(blob(x, y, g.uniform(10, 30)), g.choice(("#8a9d63", "#7f935b", "#cbb97c", "#a9a56c", "#96a468")))
    for _ in range(30):                                                                         # woods in the wild quarters between the camps
        while True:
            wx, wy = anywhere()
            if clear(wx, wy, 14): break
        for _ in range(g.randint(18, 40)):
            x, y = wx + g.gauss(0, 15), wy + g.gauss(0, 12)
            if clear(x, y): TREES.append((x, y, "pine" if g.random() < .65 else "olive"))
    for _ in range(140):                                                                        # lone trees
        x, y = anywhere()
        if clear(x, y): TREES.append((x, y, g.choice(("pine", "olive", "cypress"))))
    for _ in range(80):                                                                         # boulders
        x, y = anywhere()
        if clear(x, y, 2):
            r = g.uniform(1.2, 3.2); solid([(x + r * math.cos(a) * g.uniform(.7, 1.1), y + r * math.sin(a) * g.uniform(.7, 1.1)) for a in (k / 6 * 2 * math.pi for k in range(6))],
                                          r * g.uniform(.5, .9), "#b2ada0", wall="#9a9486").update(shadow=DETAIL)

# ------------------------------------------------------------------ distances along the roads
def segs():
    out = []
    for w, k, pts in ROADS: out += [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    for pl in PLACES.values():                                     # a short cross-piece at each door splits its road there
        (x, y) = pl["door"]; out.append(((x - 1, y - .3), (x + 1, y + .3)))
    return out
def graph():
    S = segs(); cuts = [{0.0, 1.0} for _ in S]
    for i, (p, q) in enumerate(S):
        for j, (r, s) in enumerate(S):
            if j <= i: continue
            d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
            if abs(d) < 1e-9: continue
            t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
            u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
            if -2e-3 <= t <= 1 + 2e-3 and -2e-3 <= u <= 1 + 2e-3: cuts[i].add(min(1, max(0, t))); cuts[j].add(min(1, max(0, u)))
    G = {}
    key = lambda p: (round(p[0], 1), round(p[1], 1))
    for (p, q), c in zip(S, cuts):
        c = sorted(c); pts = [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t) for t in c]
        for a, b in zip(pts, pts[1:]):
            ka, kb, d = key(a), key(b), math.hypot(b[0] - a[0], b[1] - a[1])
            G.setdefault(ka, {})[kb] = d; G.setdefault(kb, {})[ka] = d
    return G, key
def route(G, key, a, b):
    """The shortest way by road from a to b, as a list of plan points."""
    nodes = list(G); snap = lambda p: min(nodes, key=lambda n: math.hypot(n[0] - p[0], n[1] - p[1]))
    s, t = snap(a), snap(b); D, prev, Q = {s: 0}, {}, [(0, s)]
    while Q:
        d, n = heapq.heappop(Q)
        if n == t: break
        if d > D.get(n, 1e18): continue
        for m, w in G[n].items():
            if d + w < D.get(m, 1e18): D[m] = d + w; prev[m] = n; heapq.heappush(Q, (d + w, m))
    path = [t]
    while path[-1] != s: path.append(prev[path[-1]])
    return path[::-1]
def dist(G, key, a, b):
    nodes = list(G); snap = lambda p: min(nodes, key=lambda n: math.hypot(n[0] - p[0], n[1] - p[1]))
    s, t = snap(a), snap(b); D = {s: 0}; Q = [(0, s)]
    while Q:
        d, n = heapq.heappop(Q)
        if n == t: return d
        if d > D.get(n, 1e18): continue
        for m, w in G[n].items():
            if d + w < D.get(m, 1e18): D[m] = d + w; heapq.heappush(Q, (d + w, m))

# ------------------------------------------------------------------ drawing
class View:
    def __init__(s, ox, oy, scale, iso): s.ox, s.oy, s.k, s.iso = ox, oy, scale, iso
    def p(s, x, y, z=0):
        if not s.iso: return (s.ox + s.k * x, s.oy - s.k * y)
        u = x * RIGHT[0] + y * RIGHT[1]; v = math.sin(ELEV) * (x * UP[0] + y * UP[1]) + math.cos(ELEV) * z
        return (s.ox + s.k * u, s.oy - s.k * v)
    def poly(s, pts, z=0): return " ".join("%.1f,%.1f" % s.p(x, y, z) for x, y in pts)

def area(pts): return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1])) / 2
def centre(pts): return (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))

def draw_solid(V, s, o):
    pts = s["pts"] if area(s["pts"]) > 0 else s["pts"][::-1]; z0, h = s["z"], s["h"]
    if V.iso:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            nx, ny = (y2 - y1), -(x2 - x1)                                     # outward normal of a counter-clockwise outline
            if nx * CAM[0] + ny * CAM[1] <= 0: continue                        # faces away from the camera
            f = 0.92 if (nx * RIGHT[0] + ny * RIGHT[1]) < 0 else 0.74          # sun from the left of the picture
            o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width=".5"/>' % (V.poly([(x1, y1), (x2, y2)], z0) + " " + V.poly([(x2, y2), (x1, y1)], z0 + h), shade(s["wall"], f), shade(s["wall"], .6)))
        top = z0 + h
    else: top = 0
    o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width=".6"/>' % (V.poly(pts, top), s["roof"], shade(s["roof"], .7)))
    for mxx, myy, ang in (sorted(s.get("merl", []), key=lambda q: -depth(q[0], q[1])) if V.iso else s.get("merl", [])):
        draw_solid(V, mk(rect(mxx, myy, 1.2, .9, ang), .9, s["roof"], z=top if V.iso else 0, wall=s["wall"]), o)
    if s["court"]:
        cx, cy = centre(pts)
        o.append('<polygon points="%s" fill="%s"/>' % (V.poly(rect(cx, cy, s["court"], s["court"]), top), "#e9dcc4"))

def hull(pts):
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) > 1 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) > 1 and cross(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]
def draw_shadow(V, s, o):
    """The shadow a block casts on the ground it stands on: its outline, and its top swept away from the sun."""
    d = s["h"] * 1.05
    if s.get("tier"):                                                       # a terrace's own outline, shifted: it falls only on the terrace below
        o.append('<polygon points="%s" fill="#3a2a14" opacity=".13"/>' % V.poly([(x + SUN[0] * d, y + SUN[1] * d) for x, y in s["pts"]], s["z"] if V.iso else 0)); return
    sh = hull(s["pts"] + [(x + SUN[0] * d, y + SUN[1] * d) for x, y in s["pts"]])
    o.append('<polygon points="%s" fill="#3a2a14" opacity=".2"/>' % " ".join("%.1f,%.1f" % V.p(x, y, min(s["z"], zat(x, y)) if V.iso else 0) for x, y in sh))
def poly3(V, pts, fill, stroke=None, sw=.5):
    return '<polygon points="%s" fill="%s"%s/>' % (" ".join("%.1f,%.1f" % V.p(x, y, z if V.iso else 0) for x, y, z in pts), fill, ' stroke="%s" stroke-width="%s" stroke-linejoin="round"' % (stroke, sw) if stroke else "")
def lit(nx, ny, base=.84, k=.2): return base + k * (-nx * SUN[0] - ny * SUN[1])            # a face turned to the sun is lighter
def draw_any(V, s, o):
    if s.get("shadow") and SHADOWS: draw_shadow(V, s, o)
    if s.get("kind") == "hall": draw_hall(V, s, o)
    elif s.get("hip"): draw_house(V, s, o)
    elif s.get("hipr"): draw_hipped(V, s, o)
    else: draw_solid(V, s, o)
def draw_house(V, s, o):
    """A courtyard house: walls, then the open court with its far inner walls, then a tiled roof sloping out and in from a ridge ring."""
    z0, h = s["z"], s["h"]; top = z0 + h; cx, cy = centre(s["pts"]); a, c = 7.5, 2.5; m, r = 4.9, 1.7
    draw_solid(V, dict(s, roof="#000000", court=None), o) if V.iso else None
    if V.iso: o[-1] = ""                                                    # walls only: the flat top is replaced by the roof
    sq = lambda e, zz: [(cx - e, cy - e, zz), (cx + e, cy - e, zz), (cx + e, cy + e, zz), (cx - e, cy + e, zz)]
    o.append(poly3(V, sq(c, z0), "#f0e7d2"))
    if s.get("jar"): o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#a85a32"/>' % (*V.p(cx - c + 1, cy + c - 1, z0 + .4 if V.iso else 0), .7 * V.k))
    if V.iso:
        C = sq(c, z0)
        for i in range(4):                                                  # the court's far walls, seen through the opening
            (x1, y1, _), (x2, y2, _) = C[i], C[(i + 1) % 4]; nx, ny = (y2 - y1), -(x2 - x1)
            if nx * CAM[0] + ny * CAM[1] < 0: o.append(poly3(V, [(x1, y1, z0), (x2, y2, z0), (x2, y2, top), (x1, y1, top)], shade(s["wall"], .9), shade(s["wall"], .66)))
    if V.iso and s.get("lit"):
        rnd = random.Random(int(cx * 7 + cy * 13))
        for (wx, wy), (ux, uy) in (((cx + 7, cy), (0, 1)), ((cx, cy - 7), (1, 0))):    # the east and south walls
            for off in rnd.sample((-3.5, 0, 3.5), rnd.choice((1, 1, 2))):
                px_, py_ = wx + ux * off, wy + uy * off; zw = z0 + h * .45
                o.append(poly3(V, [(px_ - ux * .6, py_ - uy * .6, zw), (px_ + ux * .6, py_ + uy * .6, zw), (px_ + ux * .6, py_ + uy * .6, zw + 1.5), (px_ - ux * .6, py_ - uy * .6, zw + 1.5)], "#ffcf6e"))
    O, R, I = sq(a, top), sq(m, top + r), sq(c, top); N = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    panels = []
    for i in range(4):
        j = (i + 1) % 4; nx, ny = N[i]
        panels.append(([O[i], O[j], R[j], R[i]], lit(nx, ny), True)); panels.append(([R[i], R[j], I[j], I[i]], lit(-nx, -ny), False))
    if V.iso: panels.sort(key=lambda q: -sum(depth(x, y) for x, y, _ in q[0]))
    for pts, f, outer in panels:
        o.append(poly3(V, pts, shade(s["roof"], f), shade(s["roof"], .62), .45))
        if outer:                                                           # rows of tiles, parallel to the eave
            for t in (.36, .7):
                e1 = [pts[0][k] + (pts[3][k] - pts[0][k]) * t for k in range(3)]; e2 = [pts[1][k] + (pts[2][k] - pts[1][k]) * t for k in range(3)]
                o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width=".7" opacity=".55"/>' % (" ".join("%.1f,%.1f" % V.p(q[0], q[1], q[2] if V.iso else 0) for q in (e1, e2)), shade(s["roof"], .6)))
def draw_hipped(V, s, o):
    """A small house: walls, then a hipped roof whose ridge runs along its longer side."""
    if V.iso: draw_solid(V, dict(s, roof="#000000"), o); o[-1] = ""
    xs, ys = [x for x, _ in s["pts"]], [y for _, y in s["pts"]]; ov = .5
    x0, x1, y0, y1 = min(xs) - ov, max(xs) + ov, min(ys) - ov, max(ys) + ov; zt = s["z"] + s["h"]; zr = zt + 1.8
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if x1 - x0 >= y1 - y0:
        hd = (y1 - y0) / 2; ra, rb = (x0 + hd, cy, zr), (x1 - hd, cy, zr)
        faces = [([(x0, y1, zt), (x1, y1, zt), rb, ra], lit(0, 1)), ([(x0, y0, zt), ra, (x0, y1, zt)], lit(-1, 0)), ([(x0, y0, zt), (x1, y0, zt), rb, ra], lit(0, -1)), ([(x1, y0, zt), (x1, y1, zt), rb], lit(1, 0))]
    else:
        hw = (x1 - x0) / 2; ra, rb = (cx, y0 + hw, zr), (cx, y1 - hw, zr)
        faces = [([(x0, y0, zt), ra, rb, (x0, y1, zt)], lit(-1, 0)), ([(x0, y1, zt), (x1, y1, zt), rb], lit(0, 1)), ([(x1, y0, zt), ra, rb, (x1, y1, zt)], lit(1, 0)), ([(x0, y0, zt), (x1, y0, zt), ra], lit(0, -1))]
    if V.iso: faces.sort(key=lambda q: -sum(depth(x, y) for x, y, _ in q[0]) / len(q[0]))
    for pts, f in faces: o.append(poly3(V, pts, shade(s["roof"], f), shade(s["roof"], .62), .45))
def draw_hall(V, s, o):
    cx, cy, w, d, z = s["cx"], s["cy"], s["w"], s["d"], s["z"]
    if s["steps"]:
        for i, g in enumerate((2, 1, 0)): draw_solid(V, mk(rect(cx, cy, w + g, d + g), .5, "#ece5d6", z=z + .5 * i, wall="#d6ccb8"), o)
        z += 1.5
    parts = []
    if s["core"]: ox, oy, cw, cd = s["core"]; parts.append(mk(rect(cx + ox, cy + oy, cw, cd), s["col_h"], "#ece3cf", z=z, wall=s["wall"] if s["wall"] != "#f2ece0" else "#efe6d3"))
    def run(x0, y0, x1, y1):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2.4) + 1)
        return [(x0 + (x1 - x0) * k / (n - 1), y0 + (y1 - y0) * k / (n - 1)) for k in range(n)]
    hw, hd = w / 2 - .7, d / 2 - .7; spots = []
    if s["cols"] == "all": spots = run(-hw, -hd, hw, -hd) + run(-hw, hd, hw, hd) + run(-hw, -hd, -hw, hd)[1:-1] + run(hw, -hd, hw, hd)[1:-1]
    else:
        side = {"n": run(-hw, hd, hw, hd), "s": run(-hw, -hd, hw, -hd), "e": run(hw, -hd, hw, hd), "w": run(-hw, -hd, -hw, hd)}
        spots = [q for k in s["cols"] for q in side[k]]
    parts += [mk(rect(cx + a, cy + b, .9, .9), s["col_h"], "#f7f2e6", z=z, wall="#f4eee0") for a, b in spots]
    for q in (sorted(parts, key=lambda q: -sum(depth(x, y) for x, y in q["pts"]) / 4) if V.iso else parts): draw_solid(V, q, o)
    zt = z + s["col_h"]; draw_solid(V, mk(rect(cx, cy, w, d), 1.2, "#efe6d2", z=zt, wall="#ebe1cc"), o); zt += 1.2
    zr, ov = zt + s["roof_h"], .5; x0, x1, y0, y1 = cx - w / 2 - ov, cx + w / 2 + ov, cy - d / 2 - ov, cy + d / 2 + ov
    if s["ridge"] == "x":
        panels = [([(x0, cy, zr), (x1, cy, zr), (x1, y1, zt), (x0, y1, zt)], lit(0, 1)), ([(x0, y0, zt), (x1, y0, zt), (x1, cy, zr), (x0, cy, zr)], lit(0, -1))]
        gable = [(x1, y0, zt), (x1, y1, zt), (x1, cy, zr)]
        rows = lambda pts, t: [[pts[0][k] + (pts[3][k] - pts[0][k]) * t for k in range(3)], [pts[1][k] + (pts[2][k] - pts[1][k]) * t for k in range(3)]]
    else:
        panels = [([(x0, y0, zt), (cx, y0, zr), (cx, y1, zr), (x0, y1, zt)], lit(-1, 0)), ([(cx, y0, zr), (x1, y0, zt), (x1, y1, zt), (cx, y1, zr)], lit(1, 0))]
        gable = [(x0, y0, zt), (x1, y0, zt), (cx, y0, zr)]
        rows = lambda pts, t: [[pts[0][k] + (pts[1][k] - pts[0][k]) * t for k in range(3)], [pts[3][k] + (pts[2][k] - pts[3][k]) * t for k in range(3)]]
    for pts, f in panels:
        o.append(poly3(V, pts, shade(s["roof"], f), shade(s["roof"], .62), .5))
        for t in (.25, .5, .75):
            o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width=".7" opacity=".5"/>' % (" ".join("%.1f,%.1f" % V.p(q[0], q[1], q[2] if V.iso else 0) for q in rows(pts, t)), shade(s["roof"], .6)))
    if V.iso: o.append(poly3(V, gable, "#f1eadb", "#b9ad94", .6))                                  # the pediment that faces us

def draw_tree(V, t, z, o):
    x, y, sp = t
    if detailed(x, y) and SHADOWS:                                          # a shadow on the ground, away from the sun
        if sp in ("cypress", "pine"):
            L = 11 if sp == "cypress" else 9; o.append('<polygon points="%s" fill="#3a2a14" opacity=".2"/>' % V.poly(hull([(x - .9 * SUN[1], y + .9 * SUN[0]), (x + .9 * SUN[1], y - .9 * SUN[0]), (x + SUN[0] * L, y + SUN[1] * L)]), z if V.iso else 0))
        else:
            o.append('<polygon points="%s" fill="#3a2a14" opacity=".2"/>' % V.poly([(x + SUN[0] * 3 + 2.6 * math.cos(a / 5 * math.pi), y + SUN[1] * 3 + 2.6 * math.sin(a / 5 * math.pi)) for a in range(10)], z if V.iso else 0))
    if sp == "pine":
        if V.iso:
            bx, by = V.p(x, y, z); tx, ty = V.p(x, y, z + 9)
            o.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#2f5a3c" stroke="#22432c" stroke-width=".6" stroke-linejoin="round"/>' % (bx - 2.6 * V.k, by - .8 * V.k, bx + 2.6 * V.k, by - .8 * V.k, tx, ty))
            o.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#3b6e49" opacity=".8"/>' % (bx - 2.6 * V.k, by - .8 * V.k, bx, by - .5 * V.k, tx, ty))
        else: o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#2f5a3c"/>' % (*V.p(x, y), 2.4 * V.k))
        return
    if sp == "cypress":
        if V.iso:
            bx, by = V.p(x, y, z); tx, ty = V.p(x, y, z + 11)
            o.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#3f6b3a" stroke="#2c4f2a" stroke-width=".6"/>' % ((bx + tx) / 2, (by + ty) / 2, 1.6 * V.k, (by - ty) / 2 + .8))
        else: o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#3f6b3a"/>' % (*V.p(x, y), 1.8 * V.k))
    else:
        cx, cy = V.p(x, y, z + (3 if V.iso else 0))
        o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#8aa26a" stroke="#64804a" stroke-width=".6"/>' % (cx, cy, 2.6 * V.k))

ROAD_COL = {"road": "#cfae86", "street": "#e8dcc6"}
def draw_roads(V, o, z=0):
    for w, k, pts in ROADS:
        if k in ROAD_COL:
            o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round" stroke-linecap="round"/>' % (V.poly(pts, z), ROAD_COL[k], w * V.k * (0.87 if V.iso else 1)))

HILL = [mk(p, h, col, z=z0, wall=shade(col, .8)) for p, z0, h, col in TIERS] + ([mk(PRECINCT, 5, "#e4ddcc", z=TOP - 5, wall="#d2c8b2")] if PRECINCT else [])
TOPS = [s["z"] + s["h"] for s in HILL]

def draw(V, cid):
    o = []
    # sea and beach (the siege has neither)
    xs = [x for x in range(-300, 301, 6)] if not SIEGE else []
    if xs: o.append('<polygon points="%s" fill="#8ec3d4"/>' % V.poly([(x, shore(x)) for x in xs] + [(300, -400), (-300, -400)]))
    if NIGHT and xs:                                                               # moonlight glinting on the water, in short broken strokes
        g = random.Random(5)
        for _ in range(70):
            x = g.uniform(-260, 160); y = shore(x) - g.uniform(14, 120); L = g.uniform(3, 9)
            o.append('<polyline points="%s" fill="none" stroke="#cfe3ff" stroke-width="%.1f" stroke-linecap="round" opacity="%.2f"/>' % (V.poly([(x, y), (x + L * .8, y + L * .25)]), .45 * V.k, g.uniform(.25, .7)))
    if xs: o.append('<polyline points="%s" fill="none" stroke="#efe0b8" stroke-width="%.1f"/>' % (V.poly([(x, shore(x) + 3) for x in xs]), 7 * V.k))
    if xs: o.append('<polyline points="%s" fill="none" stroke="#6aaac0" stroke-width="%.1f" stroke-dasharray="%.1f %.1f"/>' % (V.poly([(x, shore(x) - 8) for x in xs]), .6 * V.k, 4 * V.k, 3 * V.k))
    if DETAIL and xs:
        for off, dash, gap in ((18, 7, 9), (30, 5, 13), (44, 9, 17)):
            o.append('<polyline points="%s" fill="none" stroke="#7fb6c8" stroke-width="%.1f" stroke-dasharray="%.1f %.1f" stroke-linecap="round" opacity=".8"/>' % (V.poly([(x + off * .7, shore(x) - off) for x in xs]), .5 * V.k, dash * V.k, gap * V.k))
    for f in FLAT:
        if "circle" in f:
            cx, cy, r = f["circle"]; rg = [(cx + r * math.cos(a / 12 * math.pi), cy + r * math.sin(a / 12 * math.pi)) for a in range(24)]
            o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (V.poly(rg), f["fill"], f["stroke"])); continue
        o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (V.poly(f["pts"], f["z"]), f["fill"], f["stroke"] or "none", 1 if f["stroke"] else 0))
        if f.get("rows"):
            (x0, y0), _, (x1, y1), _ = f["pts"]; y = y0 + 2.5
            if f["fill"] != "#c9cf8a":                                     # wheat: fine furrows, across or along
                ax, step = f["rows"]; t = (x0 if ax == "x" else y0) + step
                while t < (x1 if ax == "x" else y1):
                    seg = [(t, y0 + 1), (t, y1 - 1)] if ax == "x" else [(x0 + 1, t), (x1 - 1, t)]
                    o.append('<polyline points="%s" stroke="%s" stroke-width="%.2f" opacity=".5"/>' % (V.poly(seg), shade(f["fill"], .82), .45 * V.k)); t += step
                continue
            while y < y1: o.append('<polyline points="%s" stroke="#6f8a3e" stroke-width="%.2f" stroke-dasharray="%.1f %.1f"/>' % (V.poly([(x0 + 2, y), (x1 - 2, y)]), .9 * V.k, 1.2 * V.k, .8 * V.k)); y += f["rows"][1]
    draw_roads(V, o)
    # Sort everything into: ground things behind the hill; the hill, terrace by terrace, each followed by what stands on its far
    # side; then everything in front, back to front. Things on the near slopes are drawn after the whole hill, which is in front of nothing.
    things = [("solid", s, centre(s["pts"]), s["z"]) for s in SOLIDS] + [("tree", t, t[:2], zat(*t[:2])) for t in TREES]
    DH = depth(*HILL_C)
    before, after, on = [], [], [[] for _ in HILL]
    for th in things:
        (x, y), z = th[2], th[3]
        lvl = max([i for i, t in enumerate(TOPS) if t <= z + .01], default=None)
        if lvl is None: (before if V.iso and depth(x, y) > DH and (y > 150 or x < -95) else after).append(th)
        elif V.iso and depth(x, y) <= DH and lvl < len(HILL) - 1: after.append(th)
        else: on[lvl].append(th)
    put = lambda th: draw_tree(V, th[1], th[3], o) if th[0] == "tree" else draw_any(V, th[1], o)
    far = lambda th: -depth(*th[2])
    for th in sorted(before, key=far): put(th)
    for i, h in enumerate(HILL):
        draw_any(V, dict(h, shadow=DETAIL, tier=True), o)
        z = TOPS[i]
        o.append('<clipPath id="%s-h%d"><polygon points="%s"/></clipPath><g clip-path="url(#%s-h%d)">' % (cid, i, V.poly(h["pts"], z if V.iso else 0), cid, i))
        draw_roads(V, o, z if V.iso else 0)                                    # streets carry on across the terrace
        o.append('</g>')
        if i == len(HILL) - 1:
            pv = ROADS[[k for _, k, _ in ROADS].index("paving")][2]
            o.append('<polyline points="%s" fill="none" stroke="#f3eee2" stroke-width="%.1f" stroke-linejoin="round"/>' % (V.poly(pv, z if V.iso else 0), 5 * V.k * (.87 if V.iso else 1)))
        for th in sorted(on[i], key=far) if V.iso else on[i]: put(th)
    for th in sorted(after, key=far) if V.iso else after: put(th)
    return o

def labels(V, box=None):
    o = []
    for key, pl in PLACES.items():
        x, y = pl["at"]; z = zat(x, y) + (14 if V.iso else 0)
        px, py = V.p(x, y, z)
        if box: px = min(max(px, box[0] + 62), box[1] - 62)
        colr = GROUP[pl["group"]]; name = pl.get("name", key)
        if key.startswith("proposer"):
            o.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s" stroke="#fff" stroke-width="1"/>' % (*V.p(x, y, zat(x, y) + 8 if V.iso else 0), colr)); py -= 10
        o.append('<text x="%.1f" y="%.1f" class="lb" fill="%s">%s</text>' % (px, py - 4, colr, name))
        if pl["sub"]: o.append('<text x="%.1f" y="%.1f" class="sub" fill="%s">%s</text>' % (px, py + 9, GROUP["legislators"] if "legislator" in pl["sub"] else colr, pl["sub"]))
    return o

def svg():
    G, key = graph()
    WD, HT = 1560, 900
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="-apple-system, Helvetica, Arial, sans-serif">' % (WD, HT, WD, HT),
           '<style>.lb{font-size:13px;font-weight:600;text-anchor:middle;paint-order:stroke;stroke:#fffdf6;stroke-width:3.5px}'
           '.sub{font-size:10.5px;text-anchor:middle;paint-order:stroke;stroke:#fffdf6;stroke-width:3px}'
           '.h{font-size:17px;font-weight:700;fill:#2a2a2a}.c{font-size:12px;fill:#555}.t{font-size:11.5px;fill:#333}</style>',
           '<rect width="100%" height="100%" fill="#fbf8f1"/>']
    # panel 1: plan, north up
    P = 640; s1 = P / (2 * (L + 20)); ox, oy = 20 + P / 2, 70 + P / 2
    out.append('<text x="20" y="40" class="h">Plan, north up</text><text x="20" y="58" class="c">metres from the crossroads; the dashed diamond is what the overview shows</text>')
    out.append('<clipPath id="c1"><rect x="20" y="70" width="%d" height="%d"/></clipPath><g clip-path="url(#c1)"><rect x="20" y="70" width="%d" height="%d" fill="#cfd8a4"/>' % (P, P, P, P))
    V1 = View(ox, oy, s1, False); d1 = '<rect x="20" y="70" width="%d" height="%d" fill="%s"/>' % (P, P, GROUND) + "".join(draw(V1, "c1")); out.append(night(d1, V1) if NIGHT else d1)
    out.append('<polygon points="%s" fill="none" stroke="#333" stroke-width="1.2" stroke-dasharray="6 5"/>' % V1.poly([(0, L), (L, 0), (0, -L), (-L, 0)]))
    out += labels(V1)
    out.append('</g><rect x="20" y="70" width="%d" height="%d" fill="none" stroke="#999"/>' % (P, P))
    nx, ny = 20 + P - 30, 100
    out.append('<path d="M%d %d l-7 18 l7 -5 l7 5z" fill="#333"/><text x="%d" y="%d" class="c" text-anchor="middle">N</text>' % (nx, ny, nx, ny - 6))
    sb = 50 * s1; out.append('<path d="M40 %d h%.1f" stroke="#333" stroke-width="2"/><text x="40" y="%d" class="c">50 m</text>' % (70 + P - 20, sb, 70 + P - 26))
    # panel 2: the southeast view in a 4:3 frame whose diagonals are the main axes
    FW = 840; k2 = FW / (R2 * L); FH = FW * 3 / 4; fx, fy = 700, 70
    out.append('<text x="%d" y="40" class="h">Seen from the southeast, 4:3</text><text x="%d" y="58" class="c">orthographic, camera %.1f° above the horizon, so the main streets run corner to corner</text>' % (fx, fx, math.degrees(ELEV)))
    out.append('<clipPath id="c2"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath><g clip-path="url(#c2)"><rect x="%d" y="%d" width="%d" height="%d" fill="#cfd8a4"/>' % (fx, fy, FW, FH, fx, fy, FW, FH))
    V2 = View(fx + FW / 2, fy + FH / 2, k2, True); d2 = '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (fx, fy, FW, FH, GROUND) + "".join(draw(V2, "c2")); out.append(night(d2, V2) if NIGHT else d2)
    out.append('<path d="M%d %d L%d %d M%d %d L%d %d" stroke="#333" stroke-width="1" stroke-dasharray="6 5" opacity=".55"/>' % (fx, fy, fx + FW, fy + FH, fx + FW, fy, fx, fy + FH))
    out += labels(V2, (fx, fx + FW))
    out.append('</g><rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#999"/>' % (fx, fy, FW, FH))
    # distances
    pairs = [(a, b) for i, a in enumerate(CAMPS) for b in list(CAMPS)[i + 1:]] if SIEGE else [("fishery", "granary"), ("fishery", "winery"), ("granary", "winery"), ("pottery", "fishery"), ("pottery", "winery"), ("pottery", "granary"),
             ("proposer P", "winery"), ("proposer P", "granary"), ("proposer P", "fishery"), ("proposer Q", "winery"), ("proposer Q", "granary"), ("proposer Q", "fishery"),
             ("library T", "library NW"), ("library T", "library SE"), ("library NW", "library SE")]
    ty = fy + FH + 34
    out.append('<text x="%d" y="%d" class="h" style="font-size:14px">Walking distances along the roads (m)</text>' % (fx, ty))
    for i, (a, b) in enumerate(pairs):
        d = dist(G, key, PLACES[a]["door"], PLACES[b]["door"]); na, nb = PLACES[a].get("name", a), PLACES[b].get("name", b)
        out.append('<text x="%d" y="%d" class="t">%s – %s: <tspan font-weight="700">%d</tspan></text>' % (fx + (i // 5) * 290, ty + 22 + (i % 5) * 17, na, nb, round(d)))
        print("%-20s %-20s %4d" % (na, nb, round(d)))
    lx, ly = 20, 70 + P + 40
    for i, (g, c) in enumerate((("soldiers", GROUP["soldiers"]),) if SIEGE else (("merchants", GROUP["merchants"]), ("legislators", GROUP["legislators"]), ("scholars", GROUP["scholars"]))):
        out.append('<circle cx="%d" cy="%d" r="5" fill="%s"/><text x="%d" y="%d" class="t">%s</text>' % (lx + i * 130 + 6, ly, c, lx + i * 130 + 16, ly + 4, g))
    notes = ("The enemy town: walls %d m across, four gates, all shut. The camps lie north (the commander's), east, south and west," % (2 * W),
             "joined only by the road round the walls, so every message between camps goes the long way round.") if SIEGE else None
    for i, line in enumerate(notes or ("Walls %d m across at the south: 4 quarters × 4 blocks × 4 courtyard houses. No agora: the cross meets at a crossroads." % (2 * W),
                              "The acropolis rises in five 3 m terraces to a summit 20 m up; the north quarters climb its lower terraces,",
                              "and the city wall leaves the octagon to wrap the hill along its rock edge. A broad stair continues the main street",
                              "up to the temple; a narrow stair runs down the far side to a postern. A road hugs the outside of the whole circuit.")):
        out.append('<text x="%d" y="%d" class="c">%s</text>' % (lx, ly + 28 + 17 * i, line))
    out.append('</svg>')
    return "\n".join(out)

# ------------------------------------------------------------------ the page's city stage
APP_PLACES = {pl.get("name", k): (pl["at"], pl["door"]) for k, pl in PLACES.items()}
if not SIEGE: APP_PLACES["crossroads"] = ((0, 6), (0, 0))                     # where people from outside come from

def zroute(x, y):
    """Height of a walker on the roads: the stairs climb evenly; elsewhere the ground or terrace underfoot."""
    if SIEGE: return 0
    if abs(x) <= STAIR["w"] / 2 + .01 and STAIR["y0"] <= y <= STAIR["y1"]: return TOP * (y - STAIR["y0"]) / (STAIR["y1"] - STAIR["y0"])
    if abs(y - WEST_STAIR["y"]) < .6 and WEST_STAIR["x1"] <= x <= WEST_STAIR["x0"]:
        return TOP - (TOP - 3) * (WEST_STAIR["x0"] - x) / (WEST_STAIR["x0"] - WEST_STAIR["x1"])
    return zat(x, y)

def night(body, V):
    """Moonlight: every colour that is not a light source is darkened and cooled; then the glows are laid over it all."""
    import re
    def cool(m):
        h = "#" + m.group(1).lower()
        if h in LIGHTS: return h
        r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5)); l = .3 * r + .59 * g + .11 * b
        mix = lambda c: c * .68 + l * .32                                  # keep most of each colour's own hue, so roofs stay roofs
        return "#%02x%02x%02x" % (int(mix(r) * .40 + 10), int(mix(g) * .44 + 16), min(255, int(mix(b) * .56 + 38)))
    body = re.sub(r"#([0-9a-fA-F]{6})\b", cool, body)
    defs = ('<defs><radialGradient id="glow-fire"><stop offset="0" stop-color="#ffcf6e" stop-opacity=".95"/><stop offset=".3" stop-color="#ff8c2a" stop-opacity=".5"/>'
            '<stop offset="1" stop-color="#ff8c2a" stop-opacity="0"/></radialGradient><radialGradient id="glow-torch"><stop offset="0" stop-color="#fff1c4" stop-opacity="1"/>'
            '<stop offset=".25" stop-color="#ffb347" stop-opacity=".6"/><stop offset="1" stop-color="#ffb347" stop-opacity="0"/></radialGradient></defs>')
    lights = ""
    for x, y, z, r, kind in GLOWS:
        px, py = V.p(x, y, z if V.iso else 0); rx = r * V.k
        lights += '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#glow-%s)"/>' % (px, py, rx, rx * (.75 if V.iso and kind == "fire" else 1), kind)
        if kind == "torch": lights += '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff1c4"/>' % (px, py, .5 * V.k)
    return defs + body + '<g style="mix-blend-mode:screen">' + lights + "</g>"

def app_js():
    AW, AH = 1600, 1200; V = View(AW / 2, AH / 2, AW / (R2 * L), True)
    body = '<rect width="%d" height="%d" fill="%s"/>' % (AW, AH, GROUND) + "".join(draw(V, "city"))
    if NIGHT: body = night(body, V)
    G, key = graph(); r1 = lambda p: [round(p[0], 1), round(p[1], 1)]
    places = {n: r1(V.p(*at, zat(*at))) for n, (at, door) in APP_PLACES.items()}
    doors = {n: r1(V.p(*door, zroute(*door))) for n, (at, door) in APP_PLACES.items()}
    routes = {}
    names = sorted(APP_PLACES)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            try: path = route(G, key, APP_PLACES[a][1], APP_PLACES[b][1])
            except KeyError: continue                                              # no road between them (the shut town); nobody walks it
            pts = []
            for (x1, y1), (x2, y2) in zip(path, path[1:]):
                n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 3))                # every 3 m, so the stairs climb smoothly
                for j in range(n):
                    x, y = x1 + (x2 - x1) * j / n, y1 + (y2 - y1) * j / n
                    pts.append(r1(V.p(x, y, zroute(x, y))))
            pts.append(r1(V.p(*path[-1], zroute(*path[-1]))))
            routes[a + "|" + b] = [p for k, p in enumerate(pts) if k == 0 or p != pts[k - 1]]
    # the Abstraction register's background: only the roads, as plain lines in two weights, and the projection, for drawing node blocks
    plain = {"road": [], "street": []}
    for w, k, pts in ROADS:
        line = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 3))
            line += [V.p(x1 + (x2 - x1) * j / n, y1 + (y2 - y1) * j / n, zroute(x1 + (x2 - x1) * j / n, y1 + (y2 - y1) * j / n)) for j in range(n)]
        line.append(V.p(*pts[-1], zroute(*pts[-1])))
        plain["street" if k == "street" else "road"].append("M" + "L".join("%.1f,%.1f" % q for q in line))
    o = V.p(0, 0, 0); vec = lambda q: [round(q[0] - o[0], 4), round(q[1] - o[1], 4)]
    iso = dict(e=vec(V.p(1, 0, 0)), n=vec(V.p(0, 1, 0)), u=vec(V.p(0, 0, 1)))       # pixels per metre east, north and up
    import json
    name, view = ("SIEGE", "siege") if SIEGE else ("CITY", "city")
    img = bake(body, AW, AH, view)                                                 # the picture itself goes to the page as an image, not as markup
    city = dict(w=AW, h=AH, night=NIGHT, img=img, plain={k: "".join(v) for k, v in plain.items()}, iso=iso, places=places, doors=doors, routes=routes)
    frac = {n: [round(p[0] / AW, 4), round(p[1] / AH, 4)] for n, p in places.items()}
    head = "// The %s stage, written by world/city_mockup.py%s --app: the southeast picture, its places and the road routes between them.\n" % (view, " --siege" if SIEGE else "")
    data = "const %s = %s;\n" % (name, json.dumps(city, separators=(",", ":")))
    diag = "STAGES.%s = { w: %s.w, h: %s.h, places: %s, roads: {}, label: {}, inset: {}, img: null };   // for the Abstraction register\n" % (view, name, name, json.dumps(frac))
    return head + data + diag

BAKE_WIDTHS = (800, 1200, 1800)           # the stage is about 360 css px on a phone (720 px at 2x, 1080 at 3x) and at most about 900 on a desktop (1800 at 2x)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
def bake(body, AW, AH, view):
    """Render the stage picture to WebP beside the page (app/img), once per width, with headless Chrome (the only renderer
    that draws the night's screen-blended lights as the browser does) and cwebp. Returns {width: path from the page}."""
    import os, subprocess, tempfile
    app_dir = os.path.normpath(os.path.join(os.path.dirname(sys.argv[sys.argv.index("--app") + 1]), "..", ".."))
    os.makedirs(os.path.join(app_dir, "img"), exist_ok=True)
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, view + ".svg")
        open(src, "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>' % (AW, AH, AW, AH, body))
        for w in BAKE_WIDTHS:
            png, rel = os.path.join(tmp, "%s-%d.png" % (view, w)), "img/%s-%d.webp" % (view, w)
            subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=%d,%d" % (AW, AH),
                            "--force-device-scale-factor=%g" % (w / AW), "--screenshot=" + png, "file://" + src], check=True, capture_output=True)
            subprocess.run(["cwebp", "-quiet", "-q", "82", "-m", "6", png, "-o", os.path.join(app_dir, rel)], check=True)
            out[w] = rel
    return out

def crop_svg(x0, x1, y0, y1):
    AW, AH = 1600, 1200; V = View(AW / 2, AH / 2, AW / (R2 * L), True)
    pts = [V.p(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (0, 34)]
    bx0, bx1, by0, by1 = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
    body = '<rect x="-2000" y="-2000" width="6000" height="6000" fill="%s"/>' % GROUND + "".join(draw(V, "crop"))
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%.1f %.1f %.1f %.1f">%s</svg>' % ((bx1 - bx0) * 1.6, (by1 - by0) * 1.6, bx0, by0, bx1 - bx0, by1 - by0, body)

if "--crop" in sys.argv: open(sys.argv[sys.argv.index("--crop") + 1], "w").write(crop_svg(-70, 120, 25, 205))
open(sys.argv[1], "w").write(svg())
if "--app" in sys.argv: open(sys.argv[sys.argv.index("--app") + 1], "w").write(app_js())
