"""SVG mockup of the walled city: a top-down plan (north up) and the same plan seen from the southeast, as in the concept.
Plan coordinates are metres, x east, y north, origin at the crossroads. Run: python3 world/city_mockup.py world/plan/city-plan.svg"""
import math, sys, heapq, random

R2 = math.sqrt(2)
ELEV = math.asin(0.75)            # camera height above the horizon: makes the axes run along a 4:3 frame's diagonals
CAM = (1 / R2, -1 / R2)          # where the camera stands, seen from the crossroads: the southeast
UP = (-CAM[0], -CAM[1]); RIGHT = (UP[1], -UP[0])   # the picture's up and right, on the ground
L = 215                           # the four axis ends (N, E, S, W) sit at the overview's corners, this far from the crossroads
random.seed(3)

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

def zat(x, y):
    """Ground height: only the acropolis stands up."""
    if inpoly(x, y, PRECINCT): return TOP
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

# ------------------------------------------------------------------ roads: (width, kind, points)
ROADS = []
def road(w, kind, *pts): ROADS.append((w, kind, list(pts)))
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
def rect(cx, cy, w, d, rot=0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
def mk(pts, h, roof, z=0, wall="#e9dcc4", court=None): return dict(pts=pts, h=h, z=z, roof=roof, wall=wall, court=court)
def solid(pts, h, roof, z=None, court=None, wall="#e9dcc4"):
    if z is None: z = zat(sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
    SOLIDS.append(mk(pts, h, roof, z, wall, court))
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
                        if y < 0 and abs(x) + abs(y) > 110: TREES.append((x, y, "olive")); continue
                        if abs(x) < 12 and y > 40:                                                  # the stair runs up an open court
                            TREES += [(x * 1.05, y - 4, "cypress"), (x * 1.05, y + 4, "cypress")]; continue
                        p = (x, y) in ((-47.5, 28.5), (47.5, -28.5))
                        solid(rect(x, y, 14, 14), random.choice((6, 6, 7, 8)), "#7f9fdc" if p else random.choice((TILE, TILE2)), court=5)

# the wall: the southern five sides of the octagon, then round the hill on the lowest terrace; towers and gates
oct_ = octagon(0)
def wall_run(pts, h=7, z=None, gaps=()):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 12))
        for i in range(n):
            a, b = i / n, (i + 1) / n
            p, q = (x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)
            mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if any(math.hypot(mid[0] - g[0], mid[1] - g[1]) < 6 for g in gaps): continue
            dx, dy = q[0] - p[0], q[1] - p[1]; ln = math.hypot(dx, dy); nx, ny = -dy / ln * 1.6, dx / ln * 1.6
            solid([(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)], h, "#d9cdb2", z=zat(*mid) if z is None else z, wall="#cbbd9e")
GATES = [(W, 0), (0, -W), (-W, 0)]
CIRCUIT = [oct_[4], oct_[5], oct_[6], oct_[7], oct_[0], oct_[1]] + WALL_N + [oct_[4]]
wall_run(CIRCUIT, gaps=GATES + [POSTERN])
for v in [oct_[i] for i in (0, 1, 4, 5, 6, 7)] + WALL_N[::8]: solid(rect(*v, 8, 8, 0), 10, "#d9cdb2", wall="#c4b594")
for gx, gy in GATES:
    for s in (-1, 1): solid(rect(gx + (s * 8 if gx == 0 else 0), gy + (s * 8 if gy == 0 else 0), 7, 7), 10, "#d9cdb2", wall="#c4b594")

# on the summit: its wall, the temple, the altar, the temple library, the gatehouse at the head of the stair
wall_run(PRECINCT + [PRECINCT[0]], h=4, z=TOP, gaps=[(0, 104), (WEST_STAIR["x0"], 116)])
solid(rect(8, 132, 30, 16), 10, "#d0603a", z=TOP, wall="#f2ece0")
solid(rect(8, 117, 6, 3), 1.5, "#e8e2d4", z=TOP)
solid(rect(-32, 132, 10, 26), 7, "#5aa37c", z=TOP, wall="#f2ece0")
solid(rect(0, 107, 14, 6), 6, "#e8e2d4", z=TOP, wall="#f2ece0")
# the broad stair, one prism per step from the street, with parapets; it stands in front of the terraces it cuts through
N_STEPS = 20
for i in range(N_STEPS):
    y0 = STAIR["y0"] + (STAIR["y1"] - STAIR["y0"]) * i / N_STEPS; y1 = STAIR["y0"] + (STAIR["y1"] - STAIR["y0"]) * (i + 1) / N_STEPS
    zt = TOP * (i + 1) / N_STEPS; hw = STAIR["w"] / 2
    SOLIDS.append(mk([(-hw, y0), (hw, y0), (hw, y1), (-hw, y1)], zt, "#ece6d8", wall="#cfc5ae"))
    for sx in (-1, 1):
        x = sx * (hw + .5)
        SOLIDS.append(mk([(x - .5, y0), (x + .5, y0), (x + .5, y1), (x - .5, y1)], zt + 1.2, "#d9cdb2", wall="#c4b594"))
# the west stair: each step stands on whatever terrace is under it, so the terraces in front of it hide it properly
for i in range(N_STEPS):
    x0 = WEST_STAIR["x0"] + (WEST_STAIR["x1"] - WEST_STAIR["x0"]) * i / N_STEPS; x1 = WEST_STAIR["x0"] + (WEST_STAIR["x1"] - WEST_STAIR["x0"]) * (i + 1) / N_STEPS
    zt = TOP - (TOP - 3) * (i + 1) / N_STEPS; zb = zat((x0 + x1) / 2, WEST_STAIR["y"])
    SOLIDS.append(mk([(x1, WEST_STAIR["y"] - 2), (x0, WEST_STAIR["y"] - 2), (x0, WEST_STAIR["y"] + 2), (x1, WEST_STAIR["y"] + 2)], max(.4, zt - zb), "#ece6d8", z=zb, wall="#cfc5ae"))

# estates: granary (east), winery (west), fishery (south), pottery (southwest), the two outer libraries
solid(rect(168, 0, 16, 14), 9, TILE, wall="#e6d6b8")
for x, y in ((158, 20), (178, 20), (186, -16), (158, -18)): solid(rect(x, y, 9, 8), 5, TILE2)
flat([(150, -30), (195, -30), (195, 30), (150, 30)], "none", "#a08a68")
FLAT.append(dict(circle=(175, -40, 7), fill="#e3cf8e", stroke="#b49a5a", z=0))          # threshing floor
solid(rect(-160, -8, 20, 11), 5, TILE, wall="#e6d6b8")
for x, y in ((-150, 16), (-172, 16), (-178, -14)): solid(rect(x, y, 9, 8), 5, TILE2)
flat([(-188, -26), (-140, -26), (-140, 28), (-188, 28)], "none", "#a08a68")
solid(rect(-16, -108, 18, 8), 4.5, TILE, wall="#e6d6b8")                                 # fishery shed
for i in range(4): FLAT.append(dict(pts=rect(20 + (i % 2) * 9, -104 - (i // 2) * 7, 7, 5), fill="#9fd0d6", stroke="#7f9a94", z=0))   # salting tanks
for x in (-30, -2, 22): FLAT.append(dict(pts=rect(x, shore(x) - 10, 3, 22), fill="#a7865b", stroke="#7e6240", z=0))                   # jetties
for x, y in ((-24, -158), (6, -160), (30, -156), (-50, -146)): FLAT.append(dict(pts=rect(x, y, 3, 9, 20), fill="#7a5a3a", stroke=None, z=0))
for i in range(3): solid(rect(-34 + i * 5, -112, 0.8, 7), 2.4, "#8a6a48", wall="#8a6a48")   # fish racks
for x, y in ((-88, -77), (-77, -88)): solid(rect(x, y, 7, 7, 45), 5, "#b98a62", wall="#a9774e")                                  # kilns
solid(rect(-91, -91, 12, 6, -45), 3.5, "#a7865b", wall="#d8c8a8")                         # drying shed
FLAT.append(dict(pts=[(-112, -86), (-102, -92), (-100, -100), (-112, -98)], fill="#b79d78", stroke="#8c7352", z=0))               # clay pit
solid(rect(-106, 64, 11, 24), 7, "#5aa37c", wall="#f2ece0")                               # northwest library, by the west wall's ring road
solid(rect(88, -88, 24, 11, 45), 7, "#5aa37c", wall="#f2ece0")

# fields, groves, scrub (flat), then trees
WHEAT = [((104, 32), (146, 120)), ((150, 34), (240, 120)), ((198, -30), (240, 30)), ((104, -120), (150, -34)), ((150, -110), (240, -34))]
for i, ((x0, y0), (x1, y1)) in enumerate(WHEAT):
    flat([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ("#e6cf7a", "#d9bf62", "#ead98f")[i % 3], "#bfa457")
VINES = [((-240, -60), (-196, 40)), ((-196, 32), (-120, 50)), ((-140, -66), (-118, 26)), ((-196, -66), (-144, -32)), ((-240, 46), (-200, 110))]
for (x0, y0), (x1, y1) in VINES:
    flat([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "#c9cf8a", "#9aa35c", rows=("y", 5))
for _ in range(240):                                                                     # olives on the slopes north of the fields
    x, y = random.uniform(-240, 240), random.uniform(56, 240)
    if inpoly(x, y, outline(112, 98, 86)) or (x > 96 and y < 124) or (x < -96 and y < 112 and not (x < -118 and y > 54)): continue
    TREES.append((x, y, "olive"))
for x, y in ((104, -76), (76, -104), (-84, -64), (64, -88), (30, -96), (-30, -94), (-114, 46), (-114, 82),     # outside the walls
             (52, 92), (66, 116), (70, 142), (-60, 86), (-66, 108), (30, 86), (-28, 84), (40, 160), (-40, 162)):  # on the terraces
    TREES.append((x, y, "cypress"))
for _ in range(60):                                                                      # scrub between the city and the shore
    x, y = random.uniform(40, 240), random.uniform(-200, -100)
    if y > shore(x) + 6 and math.hypot(x - 88, y + 88) > 18: TREES.append((x, y, "olive"))

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
    if s["court"]:
        cx, cy = centre(pts)
        o.append('<polygon points="%s" fill="%s"/>' % (V.poly(rect(cx, cy, s["court"], s["court"]), top), "#e9dcc4"))

def draw_tree(V, t, z, o):
    x, y, sp = t
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

HILL = [mk(p, h, col, z=z0, wall=shade(col, .8)) for p, z0, h, col in TIERS] + [mk(PRECINCT, 5, "#e4ddcc", z=TOP - 5, wall="#d2c8b2")]
TOPS = [s["z"] + s["h"] for s in HILL]

def draw(V, cid):
    o = []
    # sea and beach
    xs = [x for x in range(-300, 301, 6)]
    o.append('<polygon points="%s" fill="#8ec3d4"/>' % V.poly([(x, shore(x)) for x in xs] + [(300, -400), (-300, -400)]))
    o.append('<polyline points="%s" fill="none" stroke="#efe0b8" stroke-width="%.1f"/>' % (V.poly([(x, shore(x) + 3) for x in xs]), 7 * V.k))
    o.append('<polyline points="%s" fill="none" stroke="#6aaac0" stroke-width="%.1f" stroke-dasharray="%.1f %.1f"/>' % (V.poly([(x, shore(x) - 8) for x in xs]), .6 * V.k, 4 * V.k, 3 * V.k))
    for f in FLAT:
        if "circle" in f:
            cx, cy, r = f["circle"]; rg = [(cx + r * math.cos(a / 12 * math.pi), cy + r * math.sin(a / 12 * math.pi)) for a in range(24)]
            o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1"/>' % (V.poly(rg), f["fill"], f["stroke"])); continue
        o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (V.poly(f["pts"], f["z"]), f["fill"], f["stroke"] or "none", 1 if f["stroke"] else 0))
        if f.get("rows"):
            (x0, y0), _, (x1, y1), _ = f["pts"]; y = y0 + 2.5
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
    put = lambda th: draw_tree(V, th[1], th[3], o) if th[0] == "tree" else draw_solid(V, th[1], o)
    far = lambda th: -depth(*th[2])
    for th in sorted(before, key=far): put(th)
    for i, h in enumerate(HILL):
        draw_solid(V, h, o)
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
    V1 = View(ox, oy, s1, False); out += draw(V1, "c1")
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
    V2 = View(fx + FW / 2, fy + FH / 2, k2, True); out += draw(V2, "c2")
    out.append('<path d="M%d %d L%d %d M%d %d L%d %d" stroke="#333" stroke-width="1" stroke-dasharray="6 5" opacity=".55"/>' % (fx, fy, fx + FW, fy + FH, fx + FW, fy, fx, fy + FH))
    out += labels(V2, (fx, fx + FW))
    out.append('</g><rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#999"/>' % (fx, fy, FW, FH))
    # distances
    pairs = [("fishery", "granary"), ("fishery", "winery"), ("granary", "winery"), ("pottery", "fishery"), ("pottery", "winery"), ("pottery", "granary"),
             ("proposer P", "winery"), ("proposer P", "granary"), ("proposer P", "fishery"), ("proposer Q", "winery"), ("proposer Q", "granary"), ("proposer Q", "fishery"),
             ("library T", "library NW"), ("library T", "library SE"), ("library NW", "library SE")]
    ty = fy + FH + 34
    out.append('<text x="%d" y="%d" class="h" style="font-size:14px">Walking distances along the roads (m)</text>' % (fx, ty))
    for i, (a, b) in enumerate(pairs):
        d = dist(G, key, PLACES[a]["door"], PLACES[b]["door"]); na, nb = PLACES[a].get("name", a), PLACES[b].get("name", b)
        out.append('<text x="%d" y="%d" class="t">%s – %s: <tspan font-weight="700">%d</tspan></text>' % (fx + (i // 5) * 290, ty + 22 + (i % 5) * 17, na, nb, round(d)))
        print("%-20s %-20s %4d" % (na, nb, round(d)))
    lx, ly = 20, 70 + P + 40
    for i, (g, c) in enumerate((("merchants", GROUP["merchants"]), ("legislators", GROUP["legislators"]), ("scholars", GROUP["scholars"]))):
        out.append('<circle cx="%d" cy="%d" r="5" fill="%s"/><text x="%d" y="%d" class="t">%s</text>' % (lx + i * 130 + 6, ly, c, lx + i * 130 + 16, ly + 4, g))
    for i, line in enumerate(("Walls %d m across at the south: 4 quarters × 4 blocks × 4 courtyard houses. No agora: the cross meets at a crossroads." % (2 * W),
                              "The acropolis rises in five 3 m terraces to a summit 20 m up; the north quarters climb its lower terraces,",
                              "and the city wall leaves the octagon to wrap the hill along its rock edge. A broad stair continues the main street",
                              "up to the temple; a narrow stair runs down the far side to a postern. A road hugs the outside of the whole circuit.")):
        out.append('<text x="%d" y="%d" class="c">%s</text>' % (lx, ly + 28 + 17 * i, line))
    out.append('</svg>')
    return "\n".join(out)

open(sys.argv[1], "w").write(svg())
