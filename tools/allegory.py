"""The allegory tool: checks a world's transport network, draws it, prepares and checks its picture, and builds the page's stage data.

An allegory is a folder under allegories/ holding allegory.json (its name and words) and one network file per stage (city.json,
siege.json): the places of the stage, each with its label and position, and the roads between them. Everything a messenger does on
the page is worked out from those files. See skills/build-allegory/SKILL.md for the whole procedure and references/format.md for the files.

  python3 tools/allegory.py new <id> [--from greece]          # start allegories/<id>/ from a copy of another allegory's files
  python3 tools/allegory.py check <dir>                       # every rule a network must keep; exit 1 if one is broken
  python3 tools/allegory.py diagram <dir>                     # <dir>/work/<stage>-diagram.svg (and .png): zones, roads, junctions, places
  python3 tools/allegory.py xy <m2px|px2m> x y [z]            # one point between plan units and picture pixels
  python3 tools/allegory.py plate <dir> <stage>               # work/<stage>-plate.png, -guide.png, -mask.png: what an image generator is given
  python3 tools/allegory.py prompts <dir> <stage>             # the two prompts, for pasting into a generator by hand
  python3 tools/allegory.py paint <dir> <stage>               # both passes through the Gemini API (GEMINI_API_KEY), into work/ and the stage's picture
  python3 tools/allegory.py mark <dir> <stage> <image>        # <image>-marked.png: the numbered discs over a pass-1 painting
  python3 tools/allegory.py lock <dir> <stage> <image> <ground>   # <image>-locked.png: pass 1's routes pasted back over a finished picture
  python3 tools/allegory.py overlay <dir> <stage> [image]     # work/<stage>-overlay.png: routes, doors and places drawn over the picture
  python3 tools/allegory.py trace <dir> <stage> [image]       # for a painted picture: how much of each road has a visible road under it
  python3 tools/allegory.py build <dir> [--default]           # check, bake the pictures into site/img, add the allegory to the page (site/allegories/<id>.js)
  python3 tools/allegory.py default <id>                      # make an allegory on the page the one it opens with
  python3 tools/allegory.py remove <id>                       # take an allegory off the page (its source in allegories/<id>/ stays)
  python3 tools/allegory.py list                              # the allegories on the page
  python3 tools/allegory.py shot <dir> [scene ...]            # screenshots of the built page (needs Chrome, Chromium or Edge), into work/

<dir> is an allegory's folder, or just its id. The frame is fixed: 1600 x 1200 picture pixels, 4:3, seen from the south-east
in parallel projection (see CAMERA below). Only check, diagram, xy, prompts and build work without Pillow."""
import base64, heapq, json, math, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
W, H = 1600, 1200                         # the picture's own pixels; every stage is this frame
WIDTHS = (800, 1200, 1800)                # the widths a picture is baked at for the page
MODEL = "gemini-nano-banana-2.1"          # the only image model to use: it edits in place. gemini-3-pro-image repaints the whole picture

# ------------------------------------------------------------------ the camera: fixed, the same for every world
# Plan units ("m") are x east, y north, z up, origin at the middle of the frame. The camera stands to the south-east, 48.59 degrees
# above the horizon (asin 0.75), in parallel projection: north is the upper right corner, east the lower right, and a circle on the
# ground is an ellipse three quarters as tall as wide. The frame shows a ground square 304 units on a side, standing on its corner.
R2 = math.sqrt(2); SPAN = 215 * R2; K = W / SPAN; SIN, COS = .75, math.sqrt(1 - .75 ** 2)
def m2px(x, y, z=0.0, elev=None):
    """elev: the camera's height above the horizon in degrees, for a stage that sets its own; otherwise the standard asin 0.75."""
    sn, cs = (SIN, COS) if elev is None else (math.sin(math.radians(elev)), math.cos(math.radians(elev)))
    return (W / 2 + K * (x + y) / R2, H / 2 - K * (sn * (y - x) / R2 + cs * z))
def px2m(u, v):        # the point of the ground (z = 0) under a pixel
    a, b = (u - W / 2) * R2 / K, (H / 2 - v) * R2 / (K * SIN); return ((a - b) / 2, (a + b) / 2)

# ------------------------------------------------------------------ the stages: their places (role ids are fixed), and where a place may stand
# kind: what an image generator is told to put there when the network gives the place no "landmark" of its own.
ROLES = {
    "city": {
        "winery": "a place where goods are produced: a working estate of its own",
        "northwest library": "a place where knowledge or records are kept",
        "temple library": "a place where knowledge or records are kept, close to the seat of power",
        "temple": "the seat of power: the grandest place in the picture",
        "proposer P": "a prosperous household, marked by one strong blue feature",
        "crossroads": "an open public space where the routes cross, with one centrepiece standing beside the crossing; travellers arrive here",
        "pottery": "a workshop where something is made by hand",
        "proposer Q": "a rival household, the same size and style as the blue one, marked by one strong red feature",
        "fishery": "a place where goods are produced: a working estate of its own",
        "southeast library": "a place where knowledge or records are kept",
        "granary": "a place where goods are produced: a working estate of its own"},
    "siege": {
        "camp C": "a compact camp of the besieging force, lit from within",
        "commander's camp": "the headquarters of the besieging force: the best appointed of the four camps, lit from within",
        "enemy city": "the besieged stronghold: a large, dense, fortified place, shut tight, with no way in from any route",
        "camp B": "a compact camp of the besieging force, lit from within",
        "camp A": "a compact camp of the besieging force, lit from within"},
}
# Places that are on the picture together in some scene: no two of one cast may share a zone (the three at the centre excepted).
CASTS = {"city": [["fishery", "granary", "winery", "temple", "pottery", "crossroads"], ["northwest library", "temple library", "southeast library", "crossroads"]],
         "siege": [["commander's camp", "camp A", "camp B", "camp C", "enemy city"]]}
CENTRE = {"city": ["crossroads", "proposer P", "proposer Q"], "siege": ["enemy city"]}
# The frame in thirds. A place stands in a corner, the middle of the top edge, the middle of the left edge, or the centre. The middle
# of the right edge is kept clear for the replay and theater buttons, and the middle of the bottom edge is not used.
COLS, ROWS = ("left", "middle", "right"), ("top", "middle", "bottom")
ZONES = {"top left": (0, 0), "top": (1, 0), "top right": (2, 0), "left": (0, 1), "centre": (1, 1), "bottom left": (0, 2), "bottom right": (2, 2)}
BARRED = {(2, 1): "the middle of the right edge (the replay and theater buttons are there)", (1, 2): "the middle of the bottom edge"}
SLACK = 15                                # pixels a place may stand over a zone's line
def in_zone(p, name):
    c, r = ZONES[name]; return c * W / 3 - SLACK <= p[0] <= (c + 1) * W / 3 + SLACK and r * H / 3 - SLACK <= p[1] <= (r + 1) * H / 3 + SLACK
def zone_of(p, prefer=None):
    """The zone a point stands in: the one it is inside, or failing that one whose line it is just over."""
    if prefer and in_zone(p, prefer): return prefer
    own = next((z for z, v in ZONES.items() if v == cell_of(p)), None)
    return own or next((z for z in ZONES if in_zone(p, z)), None)
def cell_of(p): return (min(2, max(0, int(p[0] // (W / 3)))), min(2, max(0, int(p[1] // (H / 3)))))

# ------------------------------------------------------------------ reading an allegory
def find(d):
    for c in (d, os.path.join(REPO, "allegories", d)):
        if os.path.isfile(os.path.join(c, "allegory.json")): return os.path.abspath(c)
    sys.exit("no allegory.json in %s (nor in allegories/%s)" % (d, d))

class Stage:
    """One network file, with every point also in picture pixels."""
    def __init__(s, path, name):
        s.path, s.dir, s.name = path, os.path.dirname(path), name
        s.d = json.load(open(path)); s.units = s.d.get("units", "px"); s.owner = os.path.basename(s.dir)
        s.places = s.d.get("places", {}); s.roads = s.d.get("roads", [])
        s.work = os.path.join(s.dir, "work")
    def px(s, p):
        if s.units == "m": return m2px(p[0], p[1], p[2] if len(p) > 2 else 0.0, (s.d.get("camera") or {}).get("elev"))
        return (float(p[0]), float(p[1]))
    def at(s, k): return s.px(s.places[k]["at"])
    def door(s, k): return s.px(s.places[k]["door"])
    def reach(s, k): return s.places[k].get("reach", True)
    def tol(s): return 2.0 if s.units == "m" else 8.0                    # how far a door may stand from its road
    def picture(s): return os.path.join(s.dir, s.d["picture"]) if s.d.get("picture") else None
    def out(s, name): os.makedirs(s.work, exist_ok=True); return os.path.join(s.work, "%s-%s" % (s.name, name))

def load(d):
    d = find(d); A = json.load(open(os.path.join(d, "allegory.json"))); A.setdefault("id", os.path.basename(d))
    files = A.get("stages") or {n: n + ".json" for n in ("city", "siege")}
    return d, A, {n: Stage(os.path.normpath(os.path.join(d, f)), n) for n, f in files.items()}

# ------------------------------------------------------------------ the graph: junctions where roads meet, cross or reach a door
def graph(S):
    """Cuts every road wherever another road touches or crosses it, and at the point nearest each door.
    Returns (G, Z, D): G[a][b] = length of the road between junctions a and b (in the file's own units, on the plan),
    Z[a] = the junction's height, D[place] = the junction at its door (None if the door is not on a road)."""
    segs = []                                                            # (p, q) with p, q = (x, y, z)
    for r in S.roads:
        P = [(p[0], p[1], p[2] if len(p) > 2 else 0.0) for p in r["pts"]]
        segs += [(a, b) for a, b in zip(P, P[1:]) if a[:2] != b[:2]]
    cuts = [{0.0, 1.0} for _ in segs]
    for i, (p, q) in enumerate(segs):
        for j in range(i + 1, len(segs)):
            r, s = segs[j]; d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
            if abs(d) < 1e-9: continue
            t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
            u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
            if -2e-3 <= t <= 1 + 2e-3 and -2e-3 <= u <= 1 + 2e-3: cuts[i].add(min(1, max(0, t))); cuts[j].add(min(1, max(0, u)))
    key = lambda p: (round(p[0], 1), round(p[1], 1)); D = {}
    for k, pl in S.places.items():
        x, y = pl["door"][:2]; best = None
        for i, (p, q) in enumerate(segs):
            dx, dy = q[0] - p[0], q[1] - p[1]; t = max(0, min(1, ((x - p[0]) * dx + (y - p[1]) * dy) / (dx * dx + dy * dy)))
            e = math.hypot(x - p[0] - t * dx, y - p[1] - t * dy)
            if not best or e < best[0] - 1e-9: best = (e, i, t)
        if best and best[0] <= S.tol(): cuts[best[1]].add(best[2]); p, q = segs[best[1]]; D[k] = key((p[0] + (q[0] - p[0]) * best[2], p[1] + (q[1] - p[1]) * best[2]))
        else: D[k] = None
    G, Z = {}, {}
    for (p, q), c in zip(segs, cuts):
        c = sorted(c); pts = [tuple(p[n] + (q[n] - p[n]) * t for n in range(3)) for t in c]
        for a, b in zip(pts, pts[1:]):
            ka, kb = key(a), key(b)
            if ka == kb: continue
            G.setdefault(ka, {})[kb] = G.setdefault(kb, {})[ka] = math.hypot(b[0] - a[0], b[1] - a[1]); Z[ka], Z[kb] = a[2], b[2]
    return G, Z, D

def shortest(G, s, t):
    D, prev, Q = {s: 0}, {}, [(0, s)]
    while Q:
        d, n = heapq.heappop(Q)
        if n == t: break
        if d > D.get(n, 1e18): continue
        for m, w in G[n].items():
            if d + w < D.get(m, 1e18): D[m] = d + w; prev[m] = n; heapq.heappush(Q, (d + w, m))
    if t not in D: return None, None
    path = [t]
    while path[-1] != s: path.append(prev[path[-1]])
    return path[::-1], D[t]

def thin(pts, eps=.05):
    """The same line with the points that lie on the straight between their neighbours left out."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]; L = math.hypot(c[0] - a[0], c[1] - a[1])
        if L < 1e-9 or abs((c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])) / L > eps or (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1]) < 0: out.append(b)
    return out + [pts[-1]]

def routes(S):
    """The way by road between every two places a messenger can reach, in picture pixels: {"a|b": [[x, y], ...]} with a < b."""
    G, Z, D = graph(S); out, lens = {}, {}; names = sorted(k for k in S.places if S.reach(k) and D.get(k))
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            path, d = shortest(G, D[a], D[b])
            if not path: continue
            pts = [S.px((x, y, Z[(x, y)])) for x, y in path]
            out[a + "|" + b] = [[round(x, 1), round(y, 1)] for x, y in thin(pts)]; lens[a + "|" + b] = d
    return out, lens

# ------------------------------------------------------------------ check
def check_stage(S, exempt=()):
    E, Wn = [], []; err, warn = E.append, Wn.append; roles = ROLES[S.name]
    if S.units not in ("m", "px"): err('"units" must be "m" (plan units) or "px" (picture pixels)')
    for k in roles:
        if k not in S.places: err("the place %r is missing: a stage needs every one of its places" % k)
    for k in S.places:
        if k not in roles: err("%r is not a place of the %s: the role ids are fixed (%s)" % (k, S.name, ", ".join(roles)))
    if E: return E, Wn
    for k, pl in S.places.items():
        lb = pl.get("label", "")
        if not lb or not isinstance(lb, str): err("%s: no label" % k); continue
        if re.match(r"(the|an?) ", lb, re.I): err("%s: the label %r starts with an article; give the bare noun, the prose adds its own" % (k, lb))
        if re.search(r"[{}<>\"]", lb): err("%s: the label %r has a character the prose cannot carry" % (k, lb))
        if len(lb) > 22: warn("%s: the label %r is long for a plate on the picture (over 22 characters)" % (k, lb))
        for f in ("at", "door"):
            if not (isinstance(pl.get(f), list) and len(pl[f]) >= 2): err("%s: no %r point" % (k, f))
    if E: return E, Wn
    if S.name == "city":
        L = {k: S.places[k]["label"] for k in ("fishery", "granary", "winery")}
        if len({v[0].upper() for v in L.values()}) < 3: err("the labels of fishery, granary and winery (%s) must start with three different letters: one scene shows them by their initials" % ", ".join(L.values()))
        if not L["fishery"].lower() < L["granary"].lower(): err("the fishery's label (%r) must come before the granary's (%r) in the alphabet: one scene settles a tie by name, in the fishery's favour" % (L["fishery"], L["granary"]))
    # where the places stand
    Z = {}
    for k in S.places:
        p = S.at(k)
        if not (40 <= p[0] <= W - 40 and 40 <= p[1] <= H - 40): err("%s stands at (%.0f, %.0f), outside the frame or within 40 px of its edge" % (k, *p)); continue
        z = zone_of(p, "centre" if k in CENTRE[S.name] else None)
        if k in exempt: Z[k] = z or "exempt"; continue
        if not z: c = cell_of(p); err("%s stands at (%.0f, %.0f), in %s. A place stands in a corner, the middle of the top edge, the middle of the left edge, or the centre" % (k, p[0], p[1], BARRED.get(c, "no zone")))
        Z[k] = z
    for k in CENTRE[S.name]:
        if k in Z and Z[k] != "centre" and k not in exempt: err("%s must stand in the centre zone, not %s" % (k, Z[k]))
    for cast in CASTS[S.name]:
        seen = {}
        for k in cast:
            if k in exempt or k not in Z or not Z[k]: continue
            if Z[k] in seen: err("%s and %s share the %s zone, and they are on the picture together in some scenes: move one to another zone" % (seen[Z[k]], k, Z[k]))
            seen[Z[k]] = k
    used = {z for z in Z.values() if z in ZONES}; need = set(ZONES) if S.name == "city" else {"top left", "top right", "bottom left", "bottom right", "centre"}
    for z in sorted(need - used): err("no place stands in the %s zone: the places should be spread over all of %s" % (z, ", ".join(sorted(need))))
    ks = list(S.places)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            d = math.dist(S.at(a), S.at(b))
            if d < 110: err("%s and %s stand %.0f px apart: under 110 px their name plates collide" % (a, b, d))
    # the roads
    if not S.roads: err("no roads"); return E, Wn
    for i, r in enumerate(S.roads):
        if r.get("kind") not in ("road", "street", "stair", "paving"): err('road %d: "kind" must be road, street, stair or paving' % i)
        if len(r.get("pts", [])) < 2: err("road %d: needs at least two points" % i)
    if E: return E, Wn
    G, Zh, D = graph(S)
    for k in S.places:
        if D[k] is None and S.reach(k): err("%s: its door is not on a road (more than %g %s from the nearest one)" % (k, S.tol(), S.units))
        p = S.door(k)
        if S.reach(k) and not (0 <= p[0] <= W and 0 <= p[1] <= H): err("%s: its door (%.0f, %.0f) is outside the frame" % (k, *p))
        if math.dist(p, S.at(k)) > 260: warn("%s: its door is %.0f px from the place itself; messengers will seem to stop short" % (k, math.dist(p, S.at(k))))
    R, _ = routes(S); live = [k for k in S.places if S.reach(k) and D[k]]
    for i, a in enumerate(sorted(live)):
        for b in sorted(live)[i + 1:]:
            if a + "|" + b not in R: err("no way by road from %s to %s: every place a messenger reaches must be joined to the others" % (a, b))
    for key, pts in R.items():
        n, hid = 0, 0
        for a, b in zip(pts, pts[1:]):
            for j in range(11):
                x, y = a[0] + (b[0] - a[0]) * j / 10, a[1] + (b[1] - a[1]) * j / 10; n += 1; hid += not (0 <= x <= W and 0 <= y <= H)
        if hid / n > .4: warn("the way %s runs outside the frame for %d%% of its length" % (key.replace("|", " to "), 100 * hid / n))
    # the picture
    pic = S.picture()
    if pic:
        if not os.path.exists(pic): warn("the picture %s does not exist yet" % os.path.relpath(pic, REPO))
        else:
            try:
                from PIL import Image
                im = Image.open(pic)
                if abs(im.width / im.height - 4 / 3) > .003: err("the picture is %d x %d: it must be 4:3" % im.size)
                if im.width < 1800: warn("the picture is %d px wide; 1800 or more keeps it sharp on large screens" % im.width)
            except ImportError: warn("Pillow is not installed: the picture's shape was not checked")
    elif not S.d.get("baked"): warn('no "picture" is named yet')
    return E, Wn

def check(d, quiet=False):
    d, A, stages = load(d); bad = 0
    for f in ("name", "title", "town", "people"):
        if not A.get(f): print("ERROR allegory.json: %r is missing" % f); bad += 1
    for a, b in A.get("words", []):
        if not (isinstance(a, str) and isinstance(b, str) and a and b): print("ERROR allegory.json: every entry of \"words\" is a pair of strings"); bad += 1
    for n in ("city", "siege"):
        if n not in stages or not os.path.exists(stages[n].path): print("ERROR no network for the %s (%s)" % (n, stages[n].path if n in stages else n + ".json")); bad += 1; continue
        E, Wn = check_stage(stages[n], stages[n].d.get("exempt", ()))
        for m in E: print("ERROR %s: %s" % (n, m))
        for m in Wn: print("warn  %s: %s" % (n, m))
        bad += len(E)
        if not E and not quiet:
            G, _, _ = graph(stages[n]); R, _ = routes(stages[n])
            print("ok    %s: %d places, %d roads, %d junctions, %d routes%s" % (n, len(stages[n].places), len(stages[n].roads), len(G), len(R), "" if stages[n].dir == d else " (shared with " + stages[n].owner + ")"))
    return bad

# ------------------------------------------------------------------ the diagram
def diagram(d):
    d, A, stages = load(d)
    for n, S in stages.items():
        G, Z, D = graph(S); R, lens = routes(S); o = []
        o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-60 -60 %d %d" font-family="Helvetica, Arial, sans-serif" font-size="20">' % (W + 120, H + 120))
        o.append('<rect x="-60" y="-60" width="%d" height="%d" fill="#f4f1ea"/><rect width="%d" height="%d" fill="#fff" stroke="#222" stroke-width="3"/>' % (W + 120, H + 120, W, H))
        for c in range(3):
            for r in range(3):
                name = next((z for z, v in ZONES.items() if v == (c, r)), None); x, y = c * W / 3, r * H / 3
                o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="#bbb" stroke-dasharray="6 6"/>' % (x, y, W / 3, H / 3, "#e9f3e4" if name else "#f6dcdc"))
                o.append('<text x="%.1f" y="%.1f" fill="%s" font-size="17">%s</text>' % (x + 10, y + 24, "#5d8a4c" if name else "#b05555", name or "keep clear"))
        for r in S.roads:
            pts = " ".join("%.1f,%.1f" % S.px(p) for p in r["pts"])
            o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%d" stroke-linejoin="round" stroke-linecap="round"/>' % (pts, "#c9b9a0" if r["kind"] == "street" else "#8a6f4d", 7 if r["kind"] == "street" else 10))
        for (x, y), nb in G.items():
            if len(nb) != 2: u, v = S.px((x, y, Z[(x, y)])); o.append('<circle cx="%.1f" cy="%.1f" r="5" fill="#fff" stroke="#333" stroke-width="2"/>' % (u, v))
        for i, k in enumerate(ROLES[S.name], 1):
            if k not in S.places: continue
            (x, y), (dx, dy) = S.at(k), S.door(k)
            o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#c22" stroke-width="2" stroke-dasharray="4 4"/><circle cx="%.1f" cy="%.1f" r="7" fill="#ffd23c" stroke="#000" stroke-width="2"/>' % (x, y, dx, dy, dx, dy))
            o.append('<circle cx="%.1f" cy="%.1f" r="22" fill="#d62828" stroke="#fff" stroke-width="3"/><text x="%.1f" y="%.1f" fill="#fff" font-weight="bold" text-anchor="middle" dy=".35em">%d</text>' % (x, y, x, y, i))
            o.append('<text x="%.1f" y="%.1f" text-anchor="middle" stroke="#fff" stroke-width="5" paint-order="stroke" font-weight="bold">%s</text><text x="%.1f" y="%.1f" text-anchor="middle" stroke="#fff" stroke-width="5" paint-order="stroke" font-size="15" fill="#555">%s</text>'
                     % (x, y + 46, esc(S.places[k].get("label", "?")), x, y + 64, esc(k)))
        o.append('<text x="0" y="-22" font-size="24" font-weight="bold">%s: the %s</text><text x="%d" y="-22" text-anchor="end" fill="#555">red disc: a place · yellow: its door · white: a junction · camera from the south-east, north to the upper right</text></svg>' % (esc(A.get("name", A["id"])), n, W))
        out = S.out("diagram.svg"); open(out, "w").write("\n".join(o)); print("wrote", os.path.relpath(out))
        png = png_of(S); print("wrote", os.path.relpath(png)) if png else None
        print("  %d junctions; routes, in %s on the plan:" % (len(G), "plan units" if S.units == "m" else "px"))
        for key in sorted(lens): print("    %-44s %6.0f" % (key.replace("|", " to "), lens[key]))
def esc(t): return str(t).replace("&", "&amp;").replace("<", "&lt;")

def png_of(S):
    """The diagram again as a PNG, drawn with Pillow, so an agent that cannot open an SVG can still look at it."""
    try: from PIL import Image, ImageDraw
    except ImportError: return None
    G, Z, D = graph(S); im = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(im); f, fs = font(22), font(16)
    for c in range(3):
        for r in range(3):
            name = next((z for z, v in ZONES.items() if v == (c, r)), None); x, y = c * W / 3, r * H / 3
            d.rectangle((x, y, x + W / 3, y + H / 3), fill=(233, 243, 228) if name else (246, 220, 220), outline=(187, 187, 187)); d.text((x + 10, y + 8), name or "keep clear", fill=(93, 138, 76) if name else (176, 85, 85), font=fs)
    for r in S.roads: d.line([S.px(p) for p in r["pts"]], fill=(201, 185, 160) if r["kind"] == "street" else (138, 111, 77), width=7 if r["kind"] == "street" else 10, joint="curve")
    for (x, y), nb in G.items():
        if len(nb) != 2: u, v = S.px((x, y, Z[(x, y)])); d.ellipse((u - 5, v - 5, u + 5, v + 5), fill=(255, 255, 255), outline=(40, 40, 40), width=2)
    for i, k in enumerate(ROLES[S.name], 1):
        if k not in S.places: continue
        (x, y), (dx, dy) = S.at(k), S.door(k); d.line((x, y, dx, dy), fill=(200, 30, 30), width=2); d.ellipse((dx - 7, dy - 7, dx + 7, dy + 7), fill=(255, 210, 60), outline=(0, 0, 0), width=2)
        d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(214, 40, 40), outline=(255, 255, 255), width=3); d.text((x, y), str(i), fill=(255, 255, 255), font=f, anchor="mm")
        d.text((x, y + 40), "%s (%s)" % (S.places[k].get("label", "?"), k), fill=(0, 0, 0), font=fs, anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
    out = S.out("diagram.png"); im.save(out); return out

# ------------------------------------------------------------------ pictures: the plate an image generator starts from, and the checks on what comes back
def font(size):
    from PIL import ImageFont
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try: return ImageFont.truetype(f, int(size))
        except OSError: pass
    return ImageFont.load_default(size=int(size))

def bands(S, d, ss, width, fill):
    """Every road a messenger can walk, as a band. Roads no route uses (the streets of a shut town) are left to the painter."""
    R, _ = routes(S)
    for pts in R.values():
        q = [(x * ss, y * ss) for x, y in pts]; d.line(q, fill=fill, width=round(width * ss), joint="curve"); r = width * ss / 2
        for x, y in (q[0], q[-1]): d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

def order(S): return [k for k in ROLES[S.name] if k in S.places]         # the reading order of the discs
def discs(S, im, ss=1):
    from PIL import ImageDraw
    d = ImageDraw.Draw(im); f = font(30 * ss)
    for i, k in enumerate(order(S), 1):
        x, y = (c * ss for c in S.at(k)); r = 26 * ss
        d.ellipse((x - r, y - r, x + r, y + r), fill=(214, 40, 40), outline=(255, 255, 255), width=int(4 * ss)); d.text((x, y), str(i), fill=(255, 255, 255), font=f, anchor="mm")
    return im

def plate(S, ss=2):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (W * ss, H * ss), (226, 222, 212))
    if S.d.get("bands") is not False: bands(S, ImageDraw.Draw(im), ss, 22, (60, 52, 44))
    im.resize((W, H), Image.LANCZOS).save(S.out("plate.png")); discs(S, im, ss).resize((W, H), Image.LANCZOS).save(S.out("guide.png"))
    m = Image.new("L", (W, H), 0); bands(S, ImageDraw.Draw(m), 1, 44, 255); m.save(S.out("mask.png"))      # every route widened, for an inpainting pass
    print("wrote", os.path.relpath(S.out("plate.png")), "-guide.png, -mask.png")

def mark(S, path):
    from PIL import Image
    im = Image.open(path).convert("RGB"); discs(S, im, im.width / W); out = path.rsplit(".", 1)[0] + "-marked.png"; im.save(out); print("wrote", os.path.relpath(out)); return out

def lock(S, final, ground, out):
    """Pastes the routes of the pass-1 painting back over the finished one, with soft edges, so a road lies exactly under every
    route whatever pass 2 did to it. Right where nothing tall stands by the roads (a siege's ring); elsewhere a building in
    front of a road would be cut by it."""
    from PIL import Image, ImageDraw, ImageFilter
    f = Image.open(final).convert("RGB"); g = Image.open(ground).convert("RGB").resize(f.size, Image.LANCZOS); ss = f.width / W
    m = Image.new("L", f.size, 0); bands(S, ImageDraw.Draw(m), ss, 34, 255)
    Image.composite(g, f, m.filter(ImageFilter.GaussianBlur(7 * ss))).save(out); print("wrote", os.path.relpath(out))

def overlay(S, path=None):
    """Routes in magenta, doors in yellow, places as red rings, and the zones' lines, over the picture: every route should lie on
    a visible road, every door touch its landmark, every ring sit on its landmark."""
    from PIL import Image, ImageDraw
    path = path or S.picture(); im = Image.open(path).convert("RGB").resize((W, H)); d = ImageDraw.Draw(im); R, _ = routes(S); f = font(16)
    for i in (1, 2): d.line((i * W / 3, 0, i * W / 3, H), fill=(255, 255, 255), width=1); d.line((0, i * H / 3, W, i * H / 3), fill=(255, 255, 255), width=1)
    for pts in R.values(): d.line([tuple(p) for p in pts], fill=(255, 0, 200), width=3)
    for k in S.places:
        x, y = S.door(k); d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 220, 0), outline=(0, 0, 0), width=2)
        x, y = S.at(k); d.ellipse((x - 24, y - 24, x + 24, y + 24), outline=(230, 30, 30), width=4)
        d.text((x, y + 38), "%s (%s)" % (S.places[k]["label"], k), fill=(0, 0, 0), font=f, anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
    out = S.out("overlay.png"); im.save(out); print("wrote", os.path.relpath(out)); return out

def trace(S, path=None, quiet=False):
    """Is there a painted road under every road of the network? Takes the picture's colour every 10 px along every road; the
    commonest of those colours is what a road looks like in this picture. A point reads as road if its colour is near that, and
    nearer to it than the ground 30 px to either side is. Prints the share of each road that reads as road and where its long
    bare stretches are; returns the number of roads under 55%. It is a measure for painted pictures, where a route must look
    like a road, and a rough one: it reads a shadow across a road as bare, and ground of the road's own colour as road.
    Use it to find where to look on the overlay, not in place of looking."""
    from PIL import Image, ImageFilter
    path = path or S.picture(); im = Image.open(path).convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(3)); px = im.load()
    def col(x, y): return px[min(W - 1, max(0, int(x))), min(H - 1, max(0, int(y)))]
    lines = []
    for r in S.roads:
        P = [S.px(p) for p in r["pts"]]; pts = []
        for a, b in zip(P, P[1:]):
            L = math.dist(a, b)
            if L < 1: continue
            ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            for j in range(int(L // 10) + 1):
                x, y = a[0] + ux * j * 10, a[1] + uy * j * 10
                if 35 <= x <= W - 35 and 35 <= y <= H - 35: pts.append((x, y, ux, uy))
        lines.append(pts)
    allc = [col(x, y) for pts in lines for x, y, _, _ in pts]
    if not allc: return 0
    best = max(allc, key=lambda c: sum(math.dist(c, d) < 26 for d in allc[::3])); near = [d for d in allc if math.dist(best, d) < 26]
    road = tuple(sum(c[k] for c in near) / len(near) for k in range(3)); bad, rows = 0, []
    for i, (r, pts) in enumerate(zip(S.roads, lines)):
        if not pts: continue
        on, run, bare = 0, None, []
        for x, y, ux, uy in pts:
            d = math.dist(col(x, y), road); side = max(math.dist(col(x - uy * 30, y + ux * 30), road), math.dist(col(x + uy * 30, y - ux * 30), road))
            ok = d < 34 and side > d + 6; on += ok
            if ok:
                if run and run[2] >= 7: bare.append(run)
                run = None
            else: run = [run[0], (x, y), run[2] + 1] if run else [(x, y), (x, y), 1]
        if run and run[2] >= 7: bare.append(run)
        share = on / len(pts); low = share < .55; bad += low
        rows.append("  %s road %2d (%s) from (%.0f, %.0f) to (%.0f, %.0f): %3.0f%% reads as road%s" % ("BARE" if low else "ok  ", i, r["kind"], *pts[0][:2], *pts[-1][:2], 100 * share,
                    "".join("; bare from (%.0f, %.0f) to (%.0f, %.0f)" % (*a, *b) for a, b, _ in bare)))
    if not quiet:
        print("TRACE %s: %d of %d roads read as bare ground for most of their length" % (os.path.basename(path), bad, len(rows)))
        for row in rows: print(row)
    return bad

CAMERA = ("The camera is fixed: a parallel projection with no perspective and no vanishing point, as in an isometric map, looking "
          "down from the south-east at about 50 degrees above the horizon. North is toward the upper right of the frame and east "
          "toward the lower right. Everything upright rises straight up the frame and shows its top together with its south and "
          "east sides; a circle lying on the ground appears as an ellipse three quarters as tall as it is wide. It is never a "
          "straight-down plan view.")
GROUND = """The attached image is a plate: blank pale ground crossed by dark bands.

Repaint it as {what}, as a detailed, realistic aerial illustration, before anything large has been built there. {camera}

Treat this as an edit: the network of dark bands stays exactly where it is in the frame (every band, bend, junction and dead end, at the same position, shape and width) and only its surface changes.

- {route} This includes the bands that run close to the edges of the frame. Every route is continuous, open to the sky and clearly visible from above along its whole length, in strong contrast with what lies beside it. A route ends where its band ends, short of the frame. No other route of similar width exists anywhere.
- Between the routes, paint only what this setting stands on (land, water, ice, sand, rock, whatever it is here), with its relief, its vegetation, its weather and its light, and make it as particular to this setting as you can. {ground} The view looks down on the ground: it fills the whole frame, with no horizon and no sky. No buildings yet.

Avoid: people, animals, text, labels, extra routes, haze or shadow hiding the routes, a changed framing."""
OPEN = """The attached image is a blank plate, the shape of the picture wanted.

Paint on it {what}, as a detailed, realistic aerial illustration. {camera}

- {ground}
- The view looks down from above: what is painted fills the whole frame, with no horizon and no sky.

Avoid: people, animals, text, labels, lines, lanes, tracks or paths drawn across the picture, a changed framing."""
BUILD = """The attached painting shows {what} with its routes. {count} numbered red discs have been placed on it.

Edit the painting: {build}. {camera}

Change nothing else: same framing and scale, same light, same ground, and every route exactly as painted, at the same position in the frame, with the same shape, width and surface.

- Replace each numbered disc with one landmark of the kind listed below. The landmark stands exactly where its disc is (the disc marks the centre of its footprint), beside the route, never on it, with its entrance at the nearest route end. Choose what each landmark is so that it belongs to this setting. No disc or number is left in the finished painting.
- Fill the remaining gaps between the routes with the smaller structures, working areas and props that only this setting would have, so that it looks lived in. {fill}
- Every route stays open to the sky and visible along its whole length. Nothing stands on, bridges over or overhangs a route.

Landmarks:
{landmarks}

Avoid: people, animals, text, numbers, discs, labels, new routes, moved routes, haze or shadow hiding the routes."""
TELL = {   # what each pass is told, per stage; a network file may replace any of these with its own ("what" may hold {setting})
    "city": dict(what="the empty landscape of {setting}", build="build the settlement into it", ground="", fill="Do not fall back on a generic town with fields."),
    "siege": dict(what="the empty ground on which a stronghold of {setting} will stand and be besieged", build="build a siege into it, by night",
                  ground="The ground inside the routes is open and nearly level. It is a clear night, lit by the moon.",
                  fill="Nothing here is at peace: it is the ground of a siege. The routes keep their exact size and shape, reaching as near the edges of the frame as they do now; the camps stand outside them, the stronghold inside, stopping short of the routes all round."),
}
ROUTE = "Each dark band becomes a route that people in this setting walk along, whatever that is here (never a waterway)."      # a stage's "route" replaces it
COUNT = "zero one two three four five six seven eight nine ten eleven twelve".split()
def prompts(S):
    setting = S.d.get("setting")
    if not setting: sys.exit('%s: give the stage a "setting" (a phrase such as "a research colony on Mars") before asking for prompts' % os.path.relpath(S.path))
    T = {k: S.d.get(k, v) for k, v in TELL[S.name].items()}; what = T["what"].format(setting=setting)
    marks = "\n".join("%d. %s" % (i, S.places[k].get("landmark") or ROLES[S.name][k]) for i, k in enumerate(order(S), 1))
    if S.d.get("bands") is False:        # ways over open ground or water, with nothing to paint under them: no bands on the plate, no routes in the prompts
        b = BUILD.replace(" with its routes", "").replace(", and every route exactly as painted, at the same position in the frame, with the same shape, width and surface", "")
        b = b.replace("beside the route, never on it, with its entrance at the nearest route end. ", "").replace("between the routes ", "").replace("\n- Every route stays open to the sky and visible along its whole length. Nothing stands on, bridges over or overhangs a route.", "").replace("new routes, moved routes, haze or shadow hiding the routes", "lines, lanes or tracks drawn across the picture")
        return (OPEN.format(what=what, camera=CAMERA, ground=T["ground"]),
                b.format(what=what, camera=CAMERA, count=COUNT[len(order(S))].capitalize(), build=T["build"], fill=T["fill"], landmarks=marks))
    return (GROUND.format(what=what, camera=CAMERA, ground=T["ground"], route=S.d.get("route", ROUTE)),
            BUILD.format(what=what, camera=CAMERA, count=COUNT[len(order(S))].capitalize(), build=T["build"], fill=T["fill"], landmarks=marks))

def paint1(prompt, src, out):
    """One edit of the image at src through the Gemini interactions API (key in GEMINI_API_KEY), saved to out."""
    import urllib.request, urllib.error
    if not os.environ.get("GEMINI_API_KEY"): sys.exit("GEMINI_API_KEY is not set. Either set it, or run `prompts` and use any image generator by hand.")
    body = {"model": MODEL, "store": False, "response_format": {"type": "image", "aspect_ratio": "4:3", "image_size": "2K"},
            "input": [{"type": "text", "text": prompt}, {"type": "image", "mime_type": "image/png", "data": base64.b64encode(open(src, "rb").read()).decode()}]}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", json.dumps(body).encode(),
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json", "Api-Revision": "2026-05-20"})
    try: r = json.load(urllib.request.urlopen(req, timeout=600))
    except urllib.error.HTTPError as e: sys.exit("%d: %s" % (e.code, e.read().decode()[:800]))
    data = [c["data"] for s in r.get("steps", []) for c in s.get("content") or [] if c.get("type") == "image" and c.get("data")]
    if not data: sys.exit("no image came back: " + json.dumps(r)[:800])
    open(out, "wb").write(base64.b64decode(data[-1])); print("wrote", os.path.relpath(out)); fit(out)

def fit(path):
    """Generators return frames a few pixels off 4:3 (2400 x 1792). The picture stands for the whole 1600 x 1200 frame, so it is
    stretched to the exact shape, never cropped; a frame more than 3% off is not this frame at all."""
    from PIL import Image
    im = Image.open(path); w, h = im.size; off = abs(w / h - 4 / 3) / (4 / 3)
    if off < 5e-4: return
    if off > .03: sys.exit("%s is %d x %d: not a 4:3 picture. Ask the generator for 4:3 again." % (os.path.relpath(path), w, h))
    im.convert("RGB").resize((w, round(w * 3 / 4)), Image.LANCZOS).save(path); print("  fitted %d x %d to %d x %d (4:3)" % (w, h, w, round(w * 3 / 4)))

def paint(S):
    """Both passes. An existing work/<stage>-ground.png is kept, so a good ground can be built on again after a poor pass 2
    (delete it to repaint the ground). The result is written to the stage's picture."""
    p1, p2 = prompts(S); plate(S); ground = S.out("ground.png"); final = S.picture() or os.path.join(S.dir, S.name + ".png")
    if os.path.exists(ground): print("keeping", os.path.relpath(ground))
    else: paint1(p1, S.out("plate.png"), ground)
    overlay(S, ground); os.replace(S.out("overlay.png"), S.out("ground-overlay.png")); marked = mark(S, ground)
    if S.d.get("lock", S.name == "siege") and S.d.get("bands") is not False: paint1(p2, marked, S.out("raw.png")); lock(S, S.out("raw.png"), ground, final)
    else: paint1(p2, marked, final)
    overlay(S, final)
    if S.d.get("bands") is not False: trace(S, final)
    if not S.d.get("picture"): print('now name it in %s:  "picture": "%s"' % (os.path.relpath(S.path), os.path.basename(final)))

# ------------------------------------------------------------------ build: the page's data
def bake(S):
    """The stage's picture at the page's widths, as WebP in site/img. A stage with "baked" names pictures already there."""
    if S.d.get("baked"): return {k: {str(w): v.replace("{w}", str(w)) for w in WIDTHS} for k, v in S.d["baked"].items()}
    pic = S.picture(); rels = {str(w): "img/%s-%s-%d.webp" % (S.owner, S.name, w) for w in WIDTHS}
    if not pic or not os.path.exists(pic):                                # the source picture is not kept in the repository; the baked ones are
        if all(os.path.exists(os.path.join(REPO, "site", r)) for r in rels.values()): print("%s: no source picture here; keeping the baked ones in site/img" % S.name); return {"img": rels}
        sys.exit("%s: its picture is missing (%s)" % (S.name, pic))
    from PIL import Image
    im = Image.open(pic).convert("RGB"); out = {}
    for w in WIDTHS:
        rel = "img/%s-%s-%d.webp" % (S.owner, S.name, w); im.resize((w, round(w * 3 / 4)), Image.LANCZOS).save(os.path.join(REPO, "site", rel), "WEBP", quality=82, method=6); out[str(w)] = rel
    return {"img": out}

# The page holds every allegory that has been built, one file each in site/allegories/, and the list of them in site/js/data/allegories.js.
# It opens with the default one; the reader can pick another from the menu.
PAGE = os.path.join(REPO, "site", "allegories"); LIST = os.path.join(REPO, "site", "js", "data", "allegories.js")
LOADER = r"""// The allegories the page can tell, and the one it opens with. Written by tools/allegory.py (build, default, remove). Do not edit by hand.
const ALLEGORIES = %s;
// Which one this visit tells: ?allegory=<id> in the address, else the reader's last choice, else the default. Its file defines
// ALLEGORY, CITY and SIEGE, and is loaded here, before the scripts that follow, so the rest of the page finds them in place.
{
  const has = id => ALLEGORIES.list.some(a => a.id === id); let id = new URLSearchParams(location.search).get("allegory");
  if (!has(id)) { try { id = localStorage.getItem("allegory"); } catch (e) {} }
  if (!has(id)) id = ALLEGORIES.default;
  ALLEGORIES.current = id;
  document.write('<script src="allegories/' + id + '.js"></' + 'script>');
}
"""
def listed():
    if not os.path.exists(LIST): return {"default": None, "list": []}
    return json.loads(re.search(r"const ALLEGORIES = (\{.*?\});\n", open(LIST).read(), re.S).group(1))
def write_list(L):
    L["list"] = [a for a in L["list"] if os.path.exists(os.path.join(PAGE, a["id"] + ".js"))]
    if L["list"] and not any(a["id"] == L["default"] for a in L["list"]): L["default"] = L["list"][0]["id"]
    open(LIST, "w").write(LOADER % json.dumps(L, separators=(",", ":"), ensure_ascii=False))
    print("the page holds: " + ", ".join("%s%s" % (a["id"], " (default)" if a["id"] == L["default"] else "") for a in L["list"]))

def build(d, default=False):
    if check(d, quiet=True): sys.exit("not built: fix the errors above first")
    d, A, stages = load(d); js = lambda o: json.dumps(o, separators=(",", ":"), ensure_ascii=False); os.makedirs(PAGE, exist_ok=True)
    out = ["// The allegory %r as the page tells it: its name and words, and for each stage its picture, its places and the way by road\n// between every two of them, in the picture's own pixels. Written by tools/allegory.py build from allegories/%s/. Do not edit by hand.\n" % (A["id"], A["id"])]
    out.append("const ALLEGORY = %s;\n" % js({k: A[k] for k in ("id", "name", "title", "town", "people", "hero", "words") if k in A}))
    for n in ("city", "siege"):
        S = stages[n]; R, _ = routes(S); r1 = lambda p: [round(p[0], 1), round(p[1], 1)]
        o = dict(w=W, h=H, night=bool(S.d.get("night")), **bake(S), label={k: S.places[k]["label"] for k in S.places},
                 places={k: r1(S.at(k)) for k in S.places}, doors={k: r1(S.door(k)) for k in S.places}, routes=R)
        out.append("const %s = %s;\n" % (n.upper(), js(o)))
    open(os.path.join(PAGE, A["id"] + ".js"), "w").write("".join(out)); print("wrote site/allegories/%s.js" % A["id"])
    L = listed(); L["list"] = [a for a in L["list"] if a["id"] != A["id"]] + [{"id": A["id"], "name": A["name"]}]
    if default or not L["default"]: L["default"] = A["id"]
    write_list(L)

def set_default(i):
    L = listed()
    if not any(a["id"] == i for a in L["list"]): sys.exit("%r is not on the page yet: build it first" % i)
    L["default"] = i; write_list(L)

def remove(i):
    """Takes an allegory off the page: its data file and its baked pictures. Its source in allegories/<id>/ stays, so `build` brings it back."""
    L = listed(); f = os.path.join(PAGE, i + ".js")
    if not os.path.exists(f): sys.exit("%r is not on the page" % i)
    if len(L["list"]) < 2: sys.exit("%r is the only allegory on the page: build another before removing it" % i)
    os.remove(f); n = 0
    for g in os.listdir(os.path.join(REPO, "site", "img")):
        if g.startswith(i + "-") and g.endswith(".webp"): os.remove(os.path.join(REPO, "site", "img", g)); n += 1
    print("removed site/allegories/%s.js and %d pictures; allegories/%s/ is kept" % (i, n, i)); write_list(L)

def browser():
    for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"):
        if os.path.exists(c): return c
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"):
        if shutil.which(c): return shutil.which(c)

def shot(d, keys):
    """Screenshots of the page as it is now built, without opening a browser by hand: each scene in the Allegory, and the first
    also in the Abstraction, into <dir>/work/page-<scene>[-plain].png. Serves site/ itself for as long as it takes."""
    import http.server, subprocess, threading
    d = find(d); exe = browser()
    if not os.path.exists(os.path.join(PAGE, os.path.basename(d) + ".js")): sys.exit("%s is not on the page yet: build it first" % os.path.basename(d))
    if not exe: sys.exit("no Chrome, Chromium or Edge found. Serve the page (python3 -m http.server 8000 -d site) and look at it some other way, or say that it was not looked at.")
    keys = keys or ["clocks-jump", "paxos-round", "quorum-overlap", "liars-four"]; work = os.path.join(d, "work"); os.makedirs(work, exist_ok=True)
    class H_(http.server.SimpleHTTPRequestHandler):
        def __init__(s, *a, **k): super().__init__(*a, directory=os.path.join(REPO, "site"), **k)
        def log_message(s, *a): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H_); threading.Thread(target=srv.serve_forever, daemon=True).start()
    for k, reg in [(k, "isle") for k in keys] + [(keys[0], "plain")]:
        out = os.path.join(work, "page-%s%s.png" % (k, "" if reg == "isle" else "-plain"))
        subprocess.run([exe, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=1300,1500", "--virtual-time-budget=9000", "--screenshot=" + out,
                        "http://127.0.0.1:%d/?allegory=%s&reg=%s&step=2#%s" % (srv.server_address[1], os.path.basename(d), reg, k)], capture_output=True)
        print("wrote" if os.path.exists(out) else "FAILED", os.path.relpath(out))
    srv.shutdown()

def new(i, src="greece"):
    dst = os.path.join(REPO, "allegories", i)
    if os.path.exists(dst): sys.exit("allegories/%s already exists" % i)
    if not re.fullmatch(r"[a-z][a-z0-9-]*", i): sys.exit("an id is lower-case letters, digits and hyphens")
    s = find(src); os.makedirs(dst)
    for f in ("allegory.json", "city.json", "siege.json"):
        o = json.load(open(os.path.join(s, f)))
        if f == "allegory.json": o.update(id=i, stages={"city": "../%s/city.json" % os.path.basename(s), "siege": "../%s/siege.json" % os.path.basename(s)}); o.pop("hero", None)
        else: o.pop("baked", None); o.pop("exempt", None); o.pop("picture", None)
        open(os.path.join(dst, f), "w").write(dumps(o))
    print("wrote allegories/%s/: allegory.json, and city.json and siege.json copied from %s as examples of the format.\nBoth stages still point at %s's own. Redraw the network of each stage you are building, then point \"stages\" at your file." % (i, os.path.basename(s), os.path.basename(s)))

def dumps(o):
    """JSON with one point, place or pair to a line, so a network stays readable and its diffs small."""
    s = json.dumps(o, indent=1, ensure_ascii=False)
    s = re.sub(r"\[\s+(-?[\d.eE+-]+),\s+(-?[\d.eE+-]+)(?:,\s+(-?[\d.eE+-]+))?\s+\]", lambda m: "[" + ", ".join(g for g in m.groups() if g is not None) + "]", s)
    s = re.sub(r"\[\s+(\"[^\"\n]*\"),\s+(\"[^\"\n]*\")\s+\]", r"[\1, \2]", s)
    s = re.sub(r"\[\n\s+(\[[^\[\]\n]*\](?:,\n\s+\[[^\[\]\n]*\])*)\n\s+\]", lambda m: "[" + re.sub(r",\n\s+", ", ", m.group(1)) + "]", s)
    return s + "\n"

if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0] if a else ""
    def stage(i=2):
        d, A, st = load(a[1])
        if len(a) <= i or a[i] not in st: sys.exit("name the stage: city or siege")
        return st[a[i]]
    if cmd == "check" and len(a) > 1: sys.exit(1 if check(a[1]) else 0)
    elif cmd == "diagram" and len(a) > 1: diagram(a[1])
    elif cmd == "xy" and len(a) > 3:
        v = [float(x) for x in a[2:]]; print("%.1f %.1f" % m2px(*v) if a[1] == "m2px" else "%.2f %.2f" % px2m(*v[:2]))
    elif cmd == "plate" and len(a) > 2: plate(stage())
    elif cmd == "prompts" and len(a) > 2: print("PASS 1 (give it work/%s-plate.png)\n\n%s\n\n\nPASS 2 (give it the pass-1 painting after `mark`)\n\n%s" % (a[2], *prompts(stage())))
    elif cmd == "paint" and len(a) > 2: paint(stage())
    elif cmd == "mark" and len(a) > 3: mark(stage(), a[3])
    elif cmd == "lock" and len(a) > 4: lock(stage(), a[3], a[4], a[3].rsplit(".", 1)[0] + "-locked.png")
    elif cmd == "overlay" and len(a) > 2: overlay(stage(), a[3] if len(a) > 3 else None)
    elif cmd == "trace" and len(a) > 2: sys.exit(1 if trace(stage(), a[3] if len(a) > 3 else None) else 0)
    elif cmd == "shot" and len(a) > 1: shot(a[1], a[2:])
    elif cmd == "build" and len(a) > 1: build(a[1], "--default" in a)
    elif cmd == "default" and len(a) > 1: set_default(a[1])
    elif cmd == "remove" and len(a) > 1: remove(a[1])
    elif cmd == "list": write_list(listed())
    elif cmd == "new" and len(a) > 1: new(a[1], a[a.index("--from") + 1] if "--from" in a else "greece")
    elif cmd == "fmt" and len(a) > 1:
        o = json.load(open(a[1])); open(a[1], "w").write(dumps(o))
    else: print(__doc__)
