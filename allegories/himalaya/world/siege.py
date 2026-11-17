"""The siege of the Himalayan allegory: a dzong on its crag, shut in by four camps in the snow, on a winter night.

Run from the repository root:   blender -b --factory-startup -P allegories/himalaya/world/siege.py -- [--draft] [--guides]
It writes allegories/himalaya/siege.json and renders siege.png beside it (or work/siege-draft.png).

The besiegers' way round the fortress is a track trodden in the snow, out of bowshot of the walls, with a spur to each camp.
Nothing leads into the dzong."""
import math, os, random, sys
os.environ["HIM_STAGE"] = "siege"; os.environ["HIM_NIGHT"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *
import kit
g = random.Random(23)

# ---------------------------------------------------------------- the land
S_ = (Y - X) / R2; T_ = (X + Y) / R2
def ridged(scale, seed, octaves=5): return (1 - 2 * np.abs(fbm(X, Y, scale, octaves, seed=seed, gain=.55))) ** 2
flank = S_ * .62 - T_ * .78
Z = np.clip(.075 * (S_ + 175), 0, None) + 11 * fbm(X, Y, 120, 4, seed=5) + 3.2 * fbm(X, Y, 34, 3, seed=6) + 1.0 * ridged(16, 7)
Z = Z + sstep(128, 240, S_) * (30 + 36 * ridged(90, 11)) + sstep(150, 240, flank) * (26 + 30 * ridged(70, 12)) + sstep(150, 230, -flank) * (10 + 16 * ridged(60, 13))      # the valley's walls, beyond the camps
gul_t = -72 - 8 * np.sin(S_ / 45.0); gdist = np.abs(T_ - gul_t); gorge = 1 - sstep(2.6, 8.0, gdist); Z = Z - 5.5 * gorge - 1.5 * np.exp(-(gdist / 16.0) ** 2)      # a frozen stream under the crag
L.Z[:] = Z
C0 = ground_px(800, 652); rc = np.hypot(X - C0[0], Y - C0[1]) * (1 + .16 * fbm(X, Y, 30, 3, seed=31))                # the crag: a flat head, broken cliffs all round
HC = 33.0; L.Z[:] = L.Z + HC * sstep(60, 31, rc) ** .8 + 7 * sstep(66, 42, rc) * sstep(28, 44, rc) * ridged(20, 33)
crag = sstep(64, 50, rc) * sstep(24, 34, rc)
L.COV["rock"][:] = np.clip(crag * 1.4 + sstep(.3, .9, gorge) * .6 + (sstep(128, 220, S_) + sstep(150, 235, flank) + sstep(150, 230, -flank)) * (.3 + 1.6 * fbm(X, Y, 24, 4, seed=63)), 0, 1)
L.COV["snow"][:] = 1.0

# ---------------------------------------------------------------- the layout, in picture pixels
PLACES = {
    "camp C": ("camp", (205, 195), (300, 288)),
    "commander's camp": ("general's camp", (1395, 195), (1300, 288)),
    "enemy city": ("dzong", (800, 590), (800, 590)),
    "camp B": ("camp", (205, 1005), (300, 912)),
    "camp A": ("camp", (1395, 1005), (1300, 912)),
}
RING = [(335, 335), (560, 250), (800, 222), (1040, 250), (1265, 335), (1338, 600), (1265, 865), (1040, 955), (800, 982), (560, 955), (335, 865), (262, 600), (335, 335)]
ROADS_PX = [RING, [(335, 335), (300, 288)], [(1265, 335), (1300, 288)], [(335, 865), (300, 912)], [(1265, 865), (1300, 912)]]
def bend(pts):
    out = []
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        Lg = math.dist(a, b); n = max(2, int(Lg / 9)); amp = min(3.0, Lg * .04) * (1 if i % 2 else -1); nx, ny = -(b[1] - a[1]) / Lg, (b[0] - a[0]) / Lg
        out += [(a[0] + (b[0] - a[0]) * k / n + nx * amp * math.sin(math.pi * k / n), a[1] + (b[1] - a[1]) * k / n + ny * amp * math.sin(math.pi * k / n)) for k in range(n)]
    return out + [pts[-1]]
AT = {k: ground_px(*v[1]) for k, v in PLACES.items()}; DOOR = {k: ground_px(*v[2]) for k, v in PLACES.items()}
roads = [dict(kind="road", width=3, pts=bend([ground_px(*p) for p in r])) for r in ROADS_PX]
LEVEL = {}
for k in PLACES:
    if k == "enemy city": LEVEL[k] = pad(AT[k][0], AT[k][1], 62, 48, 45, blend=4, how="mean"); claim(AT[k][0], AT[k][1], 42, 40)
    else: LEVEL[k] = pad(AT[k][0], AT[k][1], 46, 40, 45, blend=10); claim(AT[k][0], AT[k][1], 8, 6)
# the dzong's own ways, which no besieger walks: the stair that climbs the crag to its gate in three turns, the old road
# from the valley (snowed over now, and barred), and the covered stair down to the stream that waters the garrison
DZ = AT["enemy city"]; SKIP = (gorge > .12).astype(np.float32)
def dl(lx, ly): return loc(DZ[0], DZ[1], 45, lx, ly, 1.3)
RB = ground_px(800, 982); vx, vy = RB[0] - DZ[0], RB[1] - DZ[1]; vl = math.hypot(vx, vy)
STAIR = trail([dl(0, -20), dl(0, -24), dl(11, -27), dl(13, -31), dl(-9, -34), dl(-11, -38), dl(5, -41), dl(3, -45)], hw=1.5, shoulder=2.2, ease=5, cover="pave", v=1.0)
OLD = trail([STAIR[-1][:2], (DZ[0] + vx * .82, DZ[1] + vy * .82), (RB[0] - vx / vl * 7, RB[1] - vy / vl * 7)], hw=1.6, shoulder=3.0, ease=10, cover=None)
wx_, wy_ = (-72 - 8 * math.sin(0)), 0.0
def near_stream(p):      # the point of the stream nearest a place
    best = None
    for sv in np.arange(-120, 120, 2.0):
        tv = -72 - 8 * math.sin(sv / 45.0); q = ((tv - sv) / R2, (tv + sv) / R2); d_ = math.dist(p, q)
        if best is None or d_ < best[0]: best = (d_, q)
    return best[1]
W0 = dl(-23, 2); WS = near_stream(W0); wl = math.dist(W0, WS); WEND = (W0[0] + (WS[0] - W0[0]) * (wl - 9) / wl, W0[1] + (WS[1] - W0[1]) * (wl - 9) / wl)
WATER = trail([W0, ((W0[0] + WEND[0]) / 2 + 3, (W0[1] + WEND[1]) / 2 - 3), WEND], hw=1.6, shoulder=2.0, ease=4, cover=None)
roads = carve(roads, skip=SKIP, hw=1.7)
for sp in L.SPANS: bridge(sp)

# ---------------------------------------------------------------- the dzong
def lit_rows(cx, cy, w, d, z, floors, every=2.8, p=.55, trim="#8a2f24", ww=1.0, hh=1.4, sides=(0, 1, 2, 3), bt=.045, first=0):
    for side in sides:
        Lg = w if side % 2 == 0 else d; n = max(1, int(Lg / every))
        for fl in range(first, floors):
            for k in range(n): window(cx, cy, w, d, 0, side, (k + .5) / n, z + fl * 3.0 + 1.2, ww, hh, lit=g.random() < p, trim=trim, batter_in=bt * (fl * 3.0 + 3.4))
def gold_roof(cx, cy, w, d, z, rise, over=.9):
    B = rect(cx, cy, w + 2 * over, d + 2 * over); E = rect(cx, cy, w + 2 * over + .7, d + 2 * over + .7); Tt = rect(cx, cy, w * .34, d * .1)
    for i in range(4):
        j = (i + 1) % 4; face("gold", [P3(E[i], z + .18), P3(E[j], z + .18), P3(B[j], z), P3(B[i], z)]); face("gold", [P3(B[i], z), P3(B[j], z), P3(Tt[j], z + rise), P3(Tt[i], z + rise)], va=.5)
    cap("gold", Tt, z + rise); walls("paint:#7a2a22", rect(cx, cy, w + over, d + over), z - .5, z)
    lathe("gold", cx, cy, [(.5, z + rise), (.62, z + rise + .5), (.3, z + rise + .9), (.42, z + rise + 1.3), (.05, z + rise + 2.2)], 10)
def block(cx, cy, w, d, z0, z1, wash=WHITE, band=MAROON, bh=.9, floors=None, p=.5, first=0, va=.3, trim="#8a2f24"):
    T = battered("wash:" + wash if wash in (WHITE, CREAM) else "paint:" + wash, cx, cy, w, d, z0, z1, 0, .045, va=va); I = parapet(T, z1, band, bh, .2, va=va)
    if floors: lit_rows(cx, cy, w, d, z1 - floors * 3.0 - .6, floors, p=p, first=first, trim=trim)
    return I
def dzong():
    """The fortress-monastery: a great white wall leaning in as it rises, towers at its corners, the red-topped keep and its
    golden roof standing over the courts, lamps in its windows, its one gate shut."""
    (x, y), z = AT["enemy city"], LEVEL["enemy city"]
    with placed_s(x, y, 45, z, 1.3):
        block(0, 0, 44, 33, -9, 11.5, floors=2, p=.45, va=.2)                                      # the outer range, its upper floors only pierced
        for sx in (-1, 1):
            for sy in (-1, 1): I = block(sx * 21, sy * 15.5, 8.5, 8.5, -9, 15.5, floors=2, p=.5, va=.5); lathe("gold", sx * 21, sy * 15.5, [(.5, 15.3), (.6, 16.4), (.05, 17.4)], 8)
        block(-11, 4.5, 13, 11, 11.2, 18.0, floors=2, p=.6, va=.7); block(12, 5.5, 11, 10, 11.2, 17.0, floors=2, p=.6, va=.8)      # halls within
        block(0, 2, 14.5, 13, 11.2, 26.5, floors=4, p=.7, va=.1)                                   # the keep
        block(0, 2, 10.5, 9.5, 26.2, 30.5, wash=MAROON, band="#3a1512", bh=.5, floors=1, p=.9, trim="#e2b53a"); gold_roof(0, 2, 7.5, 6.5, 30.9, 2.8)
        gold_roof(-11, 4.5, 5, 4, 18.2, 1.6, .5); gold_roof(12, 5.5, 4.5, 3.6, 17.2, 1.5, .5)
        door(0, 0, 44, 33, 0, 0, .5, 0, 3.0, 3.8, "#e2b53a", out=.5)
        for k in range(7): boxr("ashlar", "ashlar", 0, -17.5 - k * 1.1, 6.5, 1.2, -9, -.3 - k * .75)   # the steps down from the gate, to nowhere
        for sx in (-9, 9): beam("wood:#6b5846", (sx, -17.6, 0), (sx, -17.6, 12), .14, 6); face("paint:" + FLAGS[2], [(sx, -17.6, 3), (sx + .9, -17.6, 3), (sx + .9, -17.6, 11.6), (sx, -17.6, 11.6)])
        for (a, b) in (((-21, -15.5, 16.4), (0, 2, 31.5)), ((21, -15.5, 16.4), (0, 2, 31.5)), ((-21, 15.5, 16.4), (0, 2, 31.5)), ((21, 15.5, 16.4), (0, 2, 31.5))): flag_line(a, b, sag=.04, size=.7)
        for (fx, fy) in ((-16, -12), (15, -11), (-4, -9)): fire(fx, fy, 11.6, .45, 120.0)           # watch fires on the wall-walk
dzong()
def approach():
    """What makes the fortress a place people lived in and held: the gate stair with its parapet and its barbican, the road
    below barred by the besiegers, and the walled stair down to the water with its tower at the stream."""
    steps(STAIR, 2.6)
    for a, b in zip(STAIR[::3], STAIR[3::3]):      # a parapet on the stair's outer side
        dx, dy = b[0] - a[0], b[1] - a[1]; Lg = math.hypot(dx, dy)
        if Lg < .5: continue
        ox, oy = -dy / Lg, dx / Lg
        if (a[0] + ox - DZ[0]) ** 2 + (a[1] + oy - DZ[1]) ** 2 < (a[0] - ox - DZ[0]) ** 2 + (a[1] - oy - DZ[1]) ** 2: ox, oy = -ox, -oy
        m = ((a[0] + b[0]) / 2 + ox * 1.9, (a[1] + b[1]) / 2 + oy * 1.9); boxr("wash:" + WHITE, "paint:" + MAROON, m[0], m[1], Lg + .3, .6, min(a[2], b[2]) - 1.5, max(a[2], b[2]) + 1.1, math.degrees(math.atan2(dy, dx)), va=.6)
    gx, gy, gz = STAIR[-1]                                             # the barbican at the stair's foot: a small gate tower, shut
    with placed_s(gx, gy, 45, gz, 1.2):
        T = battered("wash:" + WHITE, 0, 0, 7.5, 6, -3, 7.5, 0, .05, va=.5); parapet(T, 7.5, MAROON, .7, .18); door(0, 0, 7.5, 6, 0, 0, .5, 0, 2.2, 3.0, "#e2b53a", out=.3)
        for sx in (-2.2, 2.2): window(0, 0, 7.5, 6, 0, 0, .5 + sx / 7.5, 4.6, .8, 1.1, lit=True)
        lathe("gold", 0, 0, [(.35, 7.3), (.45, 8.2), (.05, 9.0)], 8)
    claim(gx, gy, 6, 9); fire(*loc(gx, gy, 45, 5.5, -1.5, 1.2), gz, .4, 110.0)
    for k in range(0, len(OLD) - 6, 7):                                # the old road: cairns along it under the snow
        x, y, z = OLD[k]; dx, dy = OLD[k + 3][0] - x, OLD[k + 3][1] - y; Lg = math.hypot(dx, dy) or 1
        for sd in (-1, 1): lathe("rubble", x - dy / Lg * 2.6 * sd, y + dx / Lg * 2.6 * sd, [(.55, z - .3), (.4, z + .5), (.1, z + .9)], 6, va=.5)
    x, y, z = OLD[-1]; dx, dy = OLD[-1][0] - OLD[-6][0], OLD[-1][1] - OLD[-6][1]; Lg = math.hypot(dx, dy); px_, py_ = -dy / Lg, dx / Lg      # barred where it meets the besiegers' track
    stone_wall([(x - px_ * 7, y - py_ * 7), (x + px_ * 7, y + py_ * 7)], 1.5, .9); stakes(x - px_ * 9 - dx / Lg * 2.5, y - py_ * 9 - dy / Lg * 2.5, x + px_ * 9 - dx / Lg * 2.5, y + py_ * 9 - dy / Lg * 2.5)
    for a, b in zip(WATER[::4], WATER[4::4]):                          # the water stair: walled on both sides and roofed, stepping down the crag
        dx, dy = b[0] - a[0], b[1] - a[1]; Lg = math.hypot(dx, dy)
        if Lg < .5: continue
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); zlo, zhi = min(a[2], b[2]), max(a[2], b[2]); boxr("wash:" + WHITE, "roof", m[0], m[1], Lg + .5, 3.6, zlo - 2, zhi + 3.2, math.degrees(math.atan2(dy, dx)), va=.7)
        boxr("paint:" + MAROON, None, m[0], m[1], Lg + .6, 3.8, zhi + 2.7, zhi + 3.2, math.degrees(math.atan2(dy, dx)))
    x, y, z = WATER[-1]
    with placed_s(x, y, math.degrees(math.atan2(WS[1] - W0[1], WS[0] - W0[0])), z, 1.2):      # the water tower, on the bank
        T = battered("wash:" + WHITE, 0, 0, 6.5, 6.5, -4, 10, 0, .05, va=.3); parapet(T, 10, MAROON, .7, .18)
        for side in range(4): window(0, 0, 6.5, 6.5, 0, side, .5, 6.5, .8, 1.1, lit=side < 2)
    claim(x, y, 6, 12)

# ---------------------------------------------------------------- the camps
def tent(x, y, rot, Lg=5.0, w=3.6, h=2.4, cloth="canvas:#d6cdb8", trim=None, lit=False):
    """A ridge tent of heavy cloth, pegged out, snow lying along its ridge."""
    z = zt(x, y)
    with placed_s(x, y, rot, z, 1.75):
        a, b = -Lg / 2, Lg / 2
        face(cloth, [(a, -w / 2, 0), (b, -w / 2, 0), (b, 0, h), (a, 0, h)], va=g.random()); face(cloth, [(b, w / 2, 0), (a, w / 2, 0), (a, 0, h), (b, 0, h)], va=g.random())
        face(cloth, [(a, w / 2, 0), (a, -w / 2, 0), (a, 0, h)]); face("glow" if lit else "dark", [(b, -w / 4, 0), (b, w / 4, 0), (b, 0, h * .7)]); face(cloth, [(b, -w / 2, 0), (b, -w / 4, 0), (b, 0, h * .7), (b, 0, h)]); face(cloth, [(b, w / 4, 0), (b, w / 2, 0), (b, 0, h), (b, 0, h * .7)])
        face("paint:#dfe6f2", [(a, -w * .12, h * .78), (b, -w * .12, h * .78), (b, 0, h + .04), (a, 0, h + .04)]); face("paint:#dfe6f2", [(b, w * .12, h * .78), (a, w * .12, h * .78), (a, 0, h + .04), (b, 0, h + .04)])
        if trim: face("paint:" + trim, [(a, -w / 2 - .02, .5), (b, -w / 2 - .02, .5), (b, -w * .4 - .02, .5 + h * .2), (a, -w * .4 - .02, .5 + h * .2)])
    claim(x, y, 5.0, 4.5)
def pavilion(x, y, r=5.2, h=6.0, cloth="canvas:#e6dcc4", band="#2f63b5"):
    """The general's tent: a great round pavilion, a blue band of appliqué under its eaves, a gilded finial, banners at its door."""
    z = zt(x, y)
    with placed_s(x, y, 0, z, 1.7):
        lathe(cloth, 0, 0, [(r, 0), (r, h * .42)], 16, smooth=False, cap_top=False, va=.3); lathe("paint:" + band, 0, 0, [(r + .03, h * .32), (r + .03, h * .42)], 16, smooth=False, cap_top=False)
        lathe(cloth, 0, 0, [(r + .35, h * .4), (r * .5, h * .78), (.25, h)], 16, smooth=False, va=.6); lathe("paint:#dfe6f2", 0, 0, [(r * .52, h * .775), (.26, h + .01)], 16, smooth=False, cap_top=False)
        lathe("gold", 0, 0, [(.3, h), (.4, h + .6), (.05, h + 1.4)], 8); face("glow", [(r * .7, -1.0, 0), (r * .7 + .5, -1.0, 0), (r * .7 + .5, -.2, h * .36), (r * .7, -.2, h * .36)])
        for sy in (-2.6, 2.6): beam("wood:#6b5846", (r + 2.0, sy, 0), (r + 2.0, sy, 8.5), .1, 6); face("paint:" + ("#c2352b" if sy < 0 else "#e2b53a"), [(r + 2.0, sy, 3.2), (r + 2.0, sy + 1.0, 3.2), (r + 2.0, sy + 1.0, 8.3), (r + 2.0, sy, 8.3)])
    claim(x, y, 11, 10)
def stakes(x0, y0, x1, y1):
    """A line of sharpened stakes leaning toward the fortress."""
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 1.1))
    for k in range(n + 1):
        x, y = lerp(x0, x1, k / n), lerp(y0, y1, k / n)
        if path_dist(x, y) < 2.4: continue
        z = zt(x, y); dx, dy = AT["enemy city"][0] - x, AT["enemy city"][1] - y; Lg = math.hypot(dx, dy); beam("wood:#4d3d2e", (x, y, z - .3), (x + dx / Lg * .9, y + dy / Lg * .9, z + 1.7), .09, 5)
def camp(k, chief=False):
    (x, y), z = AT[k], LEVEL[k]; paint_disc("bare", x, y, 24, .8, 9)
    dx, dy = AT["enemy city"][0] - x, AT["enemy city"][1] - y; Lg = math.hypot(dx, dy); fx, fy = dx / Lg, dy / Lg; sx, sy = -fy, fx      # toward the fortress, and across
    spots = []
    if chief: pavilion(x, y); spots.append((x, y, 12))
    else: tent(x, y, math.degrees(math.atan2(fy, fx)), 6.5, 4.6, 3.0, trim="#2f63b5", lit=True); spots.append((x, y, 6))
    n = 0
    for _ in range(400):
        if n >= (13 if chief else 11): break
        a = g.uniform(0, 6.28); r = g.uniform(13 if chief else 9, 30); tx, ty = x + r * math.cos(a), y + r * math.sin(a)
        if path_dist(tx, ty) < 4.5 or hides(tx, ty, 2.6, 3.4) or any(math.hypot(tx - px_, ty - py_) < rr + 6.2 for px_, py_, rr in spots): continue
        u_, v_ = m2px(tx, ty, zt(tx, ty))
        if not (25 < u_ < 1575 and 25 < v_ < 1175): continue
        black = g.random() < .45
        tent(tx, ty, math.degrees(math.atan2(y - ty, x - tx)) + g.uniform(-25, 25), g.uniform(4.2, 5.6), g.uniform(3.2, 4.0), g.uniform(2.1, 2.6), cloth="canvas:#2e2823" if black else "canvas:#d6cdb8", lit=g.random() < .35); spots.append((tx, ty, 4)); n += 1
    for (ox, oy) in ((9.5, 7.5), (-10.5, -8.0), (4, -13)) if not chief else ((16.5, -9.0), (-15.0, 11.0), (4.0, 18.0), (-6, -17)):      # the camp's fires
        px_, py_ = x + fx * ox + sx * oy, y + fy * ox + sy * oy
        if path_dist(px_, py_) > 3 and all(math.hypot(px_ - a_, py_ - b_) > rr + 1.6 for a_, b_, rr in spots): fire(px_, py_, zt(px_, py_), .9, 520.0); paint_disc("bare", px_, py_, 2.2, 1, 1.5); spots.append((px_, py_, 1.5))
    stakes(x + fx * 36 + sx * 22, y + fy * 36 + sy * 22, x + fx * 36 - sx * 22, y + fy * 36 - sy * 22)
    for _ in range(3):      # banners
        a = g.uniform(0, 6.28); bx, by = x + 12 * math.cos(a), y + 12 * math.sin(a)
        if path_dist(bx, by) > 3 and all(math.hypot(bx - a_, by - b_) > rr + 1 for a_, b_, rr in spots): pole(bx, by, zt(bx, by), 6.5, g=g)
def trebuchet(x, y, rot):
    """A counterweight engine: a timber frame on a sledge base, the long arm with its box of stones, the sling laid out behind."""
    z = zt(x, y)
    with placed_s(x, y, rot, z, 1.5):
        for sy in (-1.3, 1.3):
            bar("wood:#5a4636", (-3.2, sy, .15), (3.2, sy, .15), .3, .3); bar("wood:#5a4636", (-1.9, sy, .2), (0, sy, 4.6), .22, .22); bar("wood:#5a4636", (1.9, sy, .2), (0, sy, 4.6), .22, .22)
        for sx in (-3.0, 0, 3.0): bar("wood:#5a4636", (sx, -1.3, .15), (sx, 1.3, .15), .26, .26)
        beam("wood:#4d3d2e", (0, -1.5, 4.6), (0, 1.5, 4.6), .14, 6); bar("wood:#6b5846", (2.2, 0, 6.3), (-5.2, 0, 1.9), .26, .3)
        boxr("wood:#4d3d2e", "rubble", 2.5, 0, 1.6, 1.4, 4.9, 6.3); beam("paint:#2a221c", (-5.2, 0, 1.9), (-6.6, 0, .25), .04, 4)
        for k in range(5): lathe("rubble", -4.2 + (k % 3) * .5, 2.2 + (k // 3) * .5, [(.26, 0), (.3, .22), (.1, .45)], 6)
    claim(x, y, 6, 8)
def stores(x, y):
    z = zt(x, y)
    with placed_s(x, y, g.uniform(0, 90), z, 1.3):
        for k in range(g.randint(4, 7)): boxr("wood:#6b5846", "wood:#7a6248", g.uniform(-1.6, 1.6), g.uniform(-1.2, 1.2), g.uniform(.8, 1.2), g.uniform(.7, 1.0), 0, g.uniform(.6, 1.3), g.uniform(0, 40))
        for k in range(5): lathe("cloth:#b9a47e", 2.4 + (k % 3) * .6, -.5 + (k // 3) * .7, [(.3, 0), (.36, .25), (.3, .6), (.12, .72)], 7)
        bar("wood:#5a4636", (-3.2, -1.6, .25), (-3.2, 1.6, .25), .14, .14); bar("wood:#5a4636", (-4.6, -1.6, .25), (-4.6, 1.6, .25), .14, .14); boxr("wood:#6b5846", "cloth:#b9a47e", -3.9, 0, 1.6, 2.6, .3, .9)      # a sledge, loaded
    claim(x, y, 4.5, 2)
camp("camp A"); camp("camp B"); camp("camp C"); camp("commander's camp", chief=True); approach()
for k in ("camp A", "camp B", "camp C", "commander's camp"):
    (x, y) = AT[k]; dx, dy = DZ[0] - x, DZ[1] - y; Lg = math.hypot(dx, dy); fx, fy = dx / Lg, dy / Lg
    for (o1, o2) in ((44, 20), (44, -20)):
        tx, ty = x + fx * o1 - fy * o2, y + fy * o1 + fx * o2
        if path_dist(tx, ty) > 7 and free(tx, ty, 6, 1) and bil(gdist, tx, ty) > 14 and not hides(tx, ty, 3, 8): trebuchet(tx, ty, math.degrees(math.atan2(fy, fx))); paint_disc("bare", tx, ty, 6, .7, 3); break
    for _ in range(30):
        a = g.uniform(0, 6.28); tx, ty = x + 17 * math.cos(a), y + 17 * math.sin(a)
        if path_dist(tx, ty) > 4 and free(tx, ty, 4.5, .5) and not hides(tx, ty, 3, 2): stores(tx, ty); break
    footpath((x, y), DOOR[k], 1.6, .9)
# watch fires along the ring, on the side away from the fortress, and a breastwork of stones before each
for r in roads[:1]:
    for i, (x, y, ux, uy, dd) in enumerate(along([(p[0], p[1]) for p in r["pts"]], 46.0)):
        ox, oy = -uy, ux
        if (AT["enemy city"][0] - x) * ox + (AT["enemy city"][1] - y) * oy > 0: ox, oy = -ox, -oy
        fx_, fy_ = x + ox * 6.0, y + oy * 6.0
        if bil(gdist, fx_, fy_) < 12 or not free(fx_, fy_, 2.5, 1): continue
        fire(fx_, fy_, zt(fx_, fy_), .75, 300.0); paint_disc("bare", fx_, fy_, 2.0, 1, 1.5); claim(fx_, fy_, 2, 1)
        wx, wy = x - ox * 4.5, y - oy * 4.5; stone_wall([(wx - ux * 4, wy - uy * 4), (wx + ux * 4, wy + uy * 4)], 1.0, .7)

# ---------------------------------------------------------------- what grows and lies about, under snow
pines = load("pine_tree_01", lods=("LOD1", "LOD0", "LOD2")); rocks = load("namaqualand_boulder_02") + load("namaqualand_boulder_03") + load("namaqualand_boulder_05") + load("boulder_01")
cliffs = load("namaqualand_cliff_02") + load("rock_face_01") + load("rock_face_02") + load("coastal_cliff_02"); shrubs = load("shrub_01") + load("shrub_02")
snow_on(pines, .75); snow_on(rocks, .85); snow_on(cliffs, .8); snow_on(shrubs, .7)
def in_frame(x, y, m=20): u, v = m2px(x, y, zt(x, y)); return -m < u < 1600 + m and -m < v < 1200 + m
def ok(x, y, r, h): return in_frame(x, y, 90) and path_dist(x, y) > r + 2.2 and free(x, y, r, .8) and not hides(x, y, r, h)
n = 0
for _ in range(40000):
    x, y = g.uniform(-340, 340), g.uniform(-340, 340); rr = math.hypot(x - C0[0], y - C0[1]); ss = (y - x) / R2
    grove = sstep(.0, .2, float(fbm(np.array(x), np.array(y), 60, 3, seed=90)))
    if rr < 66 or g.random() > .12 + .6 * grove + .6 * sstep(120, 200, ss): continue
    h = g.uniform(11, 20)
    if ok(x, y, 2.0, h): strew(pines, x, y, g, h=h); claim(x, y, 1.0, h); n += 1
print("trees:", n)
for _ in range(2200):
    x, y = g.uniform(-340, 340), g.uniform(-340, 340); rr = bil(rc, x, y)
    if not in_frame(x, y, 100) or path_dist(x, y) < 8 or not free(x, y, 4, 1): continue
    onc = 30 < rr < 64
    if g.random() < (.9 if onc else .03 + .3 * sstep(150, 220, (y - x) / R2)):
        h = g.uniform(6, 13) if onc else g.uniform(4, 9)
        if not hides(x, y, h * .6, h): strew(cliffs, x, y, g, h=h, sink=.3, tilt=.3); claim(x, y, h * .35, h)
for _ in range(7000):
    x, y = g.uniform(-330, 330), g.uniform(-330, 330)
    if not in_frame(x, y, 60) or path_dist(x, y) < 2.6 or not free(x, y, .8, .2): continue
    if g.random() < .5: strew(rocks, x, y, g, h=g.uniform(.8, 2.6), sink=.3, tilt=.3)
    else: strew(shrubs, x, y, g, h=g.uniform(.8, 1.8))
# the frozen stream
def m_ice(key, par):
    s = Sh(key); n = s.noise(.6, 4, .7); col = s.mix(s.rng(n, .35, .7), lin("#8fb1c4"), lin("#d5e2ea")); return s.surface(s.bsdf(col, .18, s.bump(n, .2, .04)))
mats.MAKERS["ice"] = m_ice; wv = []
for sv in np.arange(-260, 215, 1.5):
    tv = -72 - 8 * math.sin(sv / 45.0); wv.append(((tv - sv) / R2, (tv + sv) / R2))
for (a, b) in zip(wv, wv[1:]):
    dx, dy = b[0] - a[0], b[1] - a[1]; Lg = math.hypot(dx, dy); nx, ny = -dy / Lg * 3.4, dx / Lg * 3.4
    face("ice", [(a[0] - nx, a[1] - ny, zt(a[0], a[1]) + .45), (a[0] + nx, a[1] + ny, zt(a[0], a[1]) + .45), (b[0] + nx, b[1] + ny, zt(b[0], b[1]) + .45), (b[0] - nx, b[1] - ny, zt(b[0], b[1]) + .45)])

# ---------------------------------------------------------------- the network, the light, the picture
places = {k: dict(label=v[0], at=[round(AT[k][0], 2), round(AT[k][1], 2), round(zt(*AT[k]), 2)], door=[round(DOOR[k][0], 2), round(DOOR[k][1], 2), round(zt(*DOOR[k]), 2)]) for k, v in PLACES.items()}
places["enemy city"]["reach"] = False
net = write_network(os.path.join(kit.ALLEGORY, "siege.json"), "siege", places, roads, night=True, setting="a dzong in the Himalaya, besieged in winter")
light(sun_el=27, sun_az=112, moon=2.9)
finish(net, winter=True)
