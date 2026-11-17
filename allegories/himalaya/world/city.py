"""The town of the Himalayan allegory: a monastery village on a terraced mountainside, built in Blender through the page's camera.

Run from the repository root:   blender -b --factory-startup -P allegories/himalaya/world/city.py -- [--draft] [--guides]
It writes allegories/himalaya/city.json (the network, at the heights this land gives the paths) and renders city.png beside it
(or work/city-draft.png). Then: python3 tools/allegory.py overlay himalaya city, and build.

The layout is given in picture pixels, so that every place falls in its zone of the frame, and turned into plan points on the
land. A path is only walkable ground: the land is benched along it and worn bare, and nothing more is modelled there."""
import math, os, random, sys
os.environ["HIM_STAGE"] = "city"; os.environ.setdefault("HIM_ELEV", "34")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *
import kit
g = random.Random(11)

# ---------------------------------------------------------------- the land before anyone built on it
S_ = (Y - X) / R2; T_ = (X + Y) / R2                                # up the picture, and across it
def ridged(scale, seed, octaves=5): return (1 - 2 * np.abs(fbm(X, Y, scale, octaves, seed=seed, gain=.55))) ** 2      # sharp crests, 0..1
flank = S_ * .62 - T_ * .78                                           # toward the upper left: the mountain
Z = np.clip(.215 * (S_ + 172), 0, None) + 9.0 * fbm(X, Y, 120, 4, seed=3) + 1.6 * fbm(X, Y, 21, 3, seed=8)
mount = sstep(48, 210, flank) ** 1.15
Z = Z + mount * (58 + 46 * ridged(110, 21) + 12 * ridged(34, 22)) + 20 * sstep(52, 95, flank) * ridged(48, 23)        # the mountain's wall, its crests and buttresses
Z = Z + sstep(112, 215, S_) * (30 + 26 * ridged(80, 31)) + 9 * sstep(60, 120, S_) * ridged(28, 32)                     # the slope steepens above the village into broken rock
Z = Z - 11 * sstep(60, 150, T_) * sstep(-40, -150, S_)                # and falls away toward the valley at the lower right
side = np.exp(-(((T_ - 118) + 26 * np.sin(S_ / 46.0)) / 13.0) ** 2) * sstep(120, 20, S_); Z = Z - 7 * side              # a side ravine on the right
gul_t = -83 - 5 * np.sin(S_ / 40.0)
gdist = np.abs(T_ - gul_t); gdepth = 6 + 9 * sstep(120, -60, S_)       # the river's gorge, deepening as it goes down
gorge = 1 - sstep(3.2, 10.5, gdist); Z = Z - gdepth * gorge - 2.0 * np.exp(-(gdist / 20.0) ** 2)
gully = np.clip(gorge + side, 0, 1)
L.Z[:] = Z
GOMPA = ground_px(1345, 205); gd = np.hypot(X - GOMPA[0], Y - GOMPA[1]); kn = np.exp(-(gd / 44.0) ** 2)
L.Z[:] = L.Z + 13 * kn + 5 * sstep(48, 30, gd) * ridged(26, 41)        # the monastery's crag
core_ = np.exp(-((T_ / 80.0) ** 2 + ((S_ + 8) / 62.0) ** 2))            # the village itself: no fields in its middle
gy_, gx_ = np.gradient(L.Z, kit.STEP); slope0 = np.hypot(gx_, gy_)
fieldm = sstep(-.12, .12, fbm(X, Y, 70, 3, seed=40) + .2 - .6 * sstep(40, 75, flank) - .9 * sstep(45, 95, S_)) * (1 - sstep(.05, .4, np.exp(-(gdist / 16.0) ** 2))) * (1 - sstep(.2, .6, side)) * (1 - sstep(.45, .8, core_)) * (1 - sstep(.3, .7, kn)) * (1 - sstep(.42, .62, slope0))
STEPH = 2.4; lev = np.floor(L.Z / STEPH); fr = L.Z / STEPH - lev
L.Z[:] = L.Z * (1 - fieldm) + (lev * STEPH + STEPH * sstep(.76, 1.0, fr)) * fieldm      # terraces: flat treads, short walls
L.COV["field"][:] = fieldm * (fr < .76)
L.COV["plot"][:] = kit._hash(np.floor((T_ + 7 * fbm(X, Y, 45, 2, seed=9)) / 16.0) + 31 * lev, np.floor((S_ + 5 * fbm(X, Y, 45, 2, seed=10)) / 30.0), 4.0)
L.COV["lush"][:] = np.clip(sstep(.02, .5, np.exp(-(gdist / 18.0) ** 2)) + .8 * side + .5 * sstep(.05, .3, fbm(X, Y, 50, 3, seed=14)), 0, 1)
L.COV["snow"][:] = np.clip(sstep(60, 84, L.Z + 18 * fbm(X, Y, 40, 4, seed=61)), 0, 1) * (.65 + .35 * sstep(-.1, .15, fbm(X, Y, 9, 3, seed=62)))
L.COV["rock"][:] = np.clip((mount + sstep(118, 200, S_)) * (.35 + 1.8 * fbm(X, Y, 24, 4, seed=63)) + sstep(.3, .9, gorge) * .9, 0, 1)
L.COV["scree"][:] = np.clip(sstep(30, 80, flank) * sstep(.0, .25, fbm(X, Y, 33, 3, seed=64)) + .7 * sstep(85, 125, S_), 0, 1) * (1 - fieldm)

# ---------------------------------------------------------------- the layout, in picture pixels
PLACES = {      # role: (label, at, door)
    "winery": ("brewery", (240, 195), (285, 285)),
    "northwest library": ("printing house", (800, 150), (800, 240)),
    "temple library": ("scripture hall", (1095, 290), (1095, 385)),
    "temple": ("gompa", (1345, 205), (1262, 335)),
    "proposer P": ("manor", (622, 520), (622, 656)),
    "crossroads": ("chorten square", (800, 585), (800, 656)),
    "pottery": ("pottery", (180, 575), (242, 660)),
    "proposer Q": ("manor", (975, 762), (972, 652)),
    "fishery": ("dairy", (235, 1010), (292, 940)),
    "southeast library": ("hermitage library", (488, 945), (488, 852)),
    "granary": ("granary", (1365, 1010), (1318, 930)),
}
ROADS_PX = [
    [(242, 660), (470, 652), (600, 656), (622, 656), (800, 656), (972, 652), (1010, 650), (1185, 610)],      # the main lane, over the gorge by the great bridge
    [(1185, 610), (1205, 490), (1095, 385), (1180, 345), (1262, 335)],                                     # up to the scripture hall and the gompa
    [(800, 656), (715, 500), (720, 350), (800, 240)],                                                      # up to the printing house
    [(292, 940), (255, 800), (242, 660), (255, 470), (285, 285)],                                          # along the far bank: dairy, pottery, brewery
    [(285, 285), (520, 262), (800, 240), (960, 300), (1095, 385)],                                         # the upper lane, over the gorge near its head
    [(600, 656), (565, 780), (488, 852), (400, 905), (292, 940)],                                          # down to the hermitage, and over the lower bridge to the dairy
    [(1010, 650), (1120, 800), (1240, 890), (1318, 930)],                                                  # down to the granary
    [(488, 852), (700, 900), (960, 915), (1120, 800)],                                                     # the lower lane, through the fields
]
def bend(pts):      # a little wander between the fixed points, so no lane is ruled straight
    out = []
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        Lg = math.dist(a, b); n = max(2, int(Lg / 9)); amp = min(3.2, Lg * .05) * (1 if (i + len(pts)) % 2 else -1); nx, ny = -(b[1] - a[1]) / Lg, (b[0] - a[0]) / Lg
        out += [(a[0] + (b[0] - a[0]) * k / n + nx * amp * math.sin(math.pi * k / n), a[1] + (b[1] - a[1]) * k / n + ny * amp * math.sin(math.pi * k / n)) for k in range(n)]
    return out + [pts[-1]]
AT = {k: ground_px(*v[1]) for k, v in PLACES.items()}; DOOR = {k: ground_px(*v[2]) for k, v in PLACES.items()}
roads = [dict(kind="road", width=3, pts=bend([ground_px(*p) for p in r])) for r in ROADS_PX]

# the landmarks' own ground, levelled before the paths are cut (the paths win where they meet)
ROT = 45.0                                                             # a front turned this way faces the camera
LEVEL = {}
def site(k, w, d, rot=ROT, **kw): LEVEL[k] = pad(AT[k][0], AT[k][1], w * U, d * U, rot, **kw); claim(AT[k][0], AT[k][1], math.hypot(w, d) / 2 * U * .8, 9 * U); return LEVEL[k]
site("temple", 40, 34, 40, blend=7); site("temple library", 19, 15, 52, blend=4); site("northwest library", 24, 13, 38, blend=4); site("winery", 20, 16, 50, blend=4)
site("pottery", 18, 15, 40, blend=4); site("crossroads", 15, 15, 45, blend=5); site("proposer P", 16, 14, 48, blend=3.5); site("proposer Q", 16, 14, 42, blend=3.5)
site("fishery", 24, 19, 44, blend=4); site("southeast library", 15, 13, 50, blend=3.5); site("granary", 21, 17, 40, blend=4)
roads = carve(roads, skip=(gorge > .12).astype(np.float32))
for sp in L.SPANS: bridge(sp)
for k in PLACES: paint_disc("bare", DOOR[k][0], DOOR[k][1], 3.5, .9, 3)

# ---------------------------------------------------------------- the landmarks
def gold_roof(cx, cy, w, d, z, rise, rot, over=.9):
    """A gilded pagoda roof: four slopes sweeping out over the walls, a ridge, and the finial at its middle."""
    B = rect(cx, cy, w + 2 * over, d + 2 * over, rot); E = rect(cx, cy, w + 2 * over + .7, d + 2 * over + .7, rot); Tt = rect(cx, cy, w * .34, d * .1, rot)
    for i in range(4):
        j = (i + 1) % 4; face("gold", [P3(E[i], z + .18), P3(E[j], z + .18), P3(B[j], z), P3(B[i], z)]); face("gold", [P3(B[i], z), P3(B[j], z), P3(Tt[j], z + rise), P3(Tt[i], z + rise)], va=.5)
    cap("gold", Tt, z + rise); walls("paint:#7a2a22", rect(cx, cy, w + over, d + over, rot), z - .5, z)
    lathe("gold", cx, cy, [(.5, z + rise), (.62, z + rise + .5), (.3, z + rise + .9), (.42, z + rise + 1.3), (.05, z + rise + 2.2)], 10)
    for c in Tt: lathe("gold", c[0], c[1], [(.2, z + rise), (.26, z + rise + .5), (.03, z + rise + 1.0)], 8)
def finials(T, z, n=4):
    for c in T[:n]: lathe("gold", c[0] * .97 + sum(p[0] for p in T) / len(T) * .03, c[1] * .97 + sum(p[1] for p in T) / len(T) * .03, [(.28, z), (.34, z + .9), (.2, z + 1.05), (.03, z + 1.5)], 8)
def rows_of_windows(cx, cy, w, d, rot, z, floors, sides=(0, 1, 2, 3), every=2.4, trim=None, ww=1.0, hh=1.4, lit=0.0, bt=.05, skip0=True):
    for side in sides:
        Lg = w if side % 2 == 0 else d; n = max(1, int(Lg / every))
        for fl in range(1 if skip0 else 0, floors):
            for k in range(n): window(cx, cy, w, d, rot, side, (k + .5) / n, z + fl * 3.0 + 1.2, ww, hh, lit=g.random() < lit, trim=trim, batter_in=bt * (fl * 3.0 + 3.4))

def gompa():
    """The monastery: the assembly hall with its red upper storey and gilded roof, monks' quarters to either side, a paved court
    with tall flag masts and an incense burner in front."""
    (x, y), z = AT["temple"], LEVEL["temple"]; rot = 40.0
    paint("pave", x, y, 36 * U, 30 * U, rot, 1.0, 2.0)
    with placed_s(x, y, rot, z):
        T = battered("wash:" + WHITE, 0, 4, 22, 15, -2, 8.2, 0, .045, va=.2); walls("ashlar", grow(rect(0, 4, 22, 15), .08), -2, .7)
        I = parapet(T, 8.2, MAROON, .9, .2)
        rows_of_windows(0, 4, 22, 15, 0, 0, 3, sides=(1, 2, 3), every=3.0, trim="#c2352b", ww=1.2, hh=1.7)
        rows_of_windows(0, 4, 22, 15, 0, 0, 3, sides=(0,), every=3.6, trim="#c2352b", ww=1.4, hh=1.9, skip0=True)
        # the porch: four red columns under a painted beam
        for cxx in (-4.5, -1.5, 1.5, 4.5): cyl("paint:#9a2b22", cxx, -5.2, .32, 0, 3.6, 8); boxr("paint:#e2b53a", "paint:#e2b53a", cxx, -5.2, .9, .9, 3.6, 3.85)
        boxr("paint:#2f63b5", "paint:#7a2a22", 0, -5.0, 11.5, 1.9, 3.85, 4.5); boxr("paint:" + MAROON, "earth:#93846c", 0, -4.6, 12.2, 2.8, 4.5, 4.85)
        prism("paving", "paving", rect(0, -5.4, 13, 3.4), -.6, .35)
        door(0, 4, 22, 15, 0, 0, .5, .35, 2.4, 3.0, "#e2b53a")
        # the upper storey, red, and the golden roof
        T2 = battered("paint:" + MAROON, 0, 5.5, 13, 9, 7.9, 12.0, 0, .03); I2 = parapet(T2, 12.0, "#3a1512", .5, .16, white_top=False)
        rows_of_windows(0, 5.5, 13, 9, 0, 6.6, 2, every=2.6, trim="#e2b53a", ww=1.0, hh=1.5, bt=.03)
        gold_roof(0, 5.5, 8.5, 5.2, 12.4, 2.6, 0); boxr("paint:" + MAROON, "paint:" + MAROON, 0, 5.5, 8.0, 4.8, 11.7, 12.4)
        finials(I, 8.4)
        # monks' quarters
        for sx in (-1, 1):
            Tq = battered("wash:" + WHITE, sx * 16.2, 3, 7.5, 17, -2, 5.8, 0, .05, va=.6 + sx * .1); parapet(Tq, 5.8, MAROON, .55)
            rows_of_windows(sx * 16.2, 3, 7.5, 17, 0, 0, 2, every=2.5, trim="#8a2f24", skip0=False)
        # the court: masts, the burner, a low wall with its gate
        for sx in (-7.5, 7.5):
            beam("wood:#6b5846", (sx, -11.5, 0), (sx, -11.5, 11.5), .12, 6); face("paint:" + FLAGS[0 if sx < 0 else 2], [(sx, -11.5, 2.5), (sx + .7, -11.5, 2.5), (sx + .7, -11.5, 11.2), (sx, -11.5, 11.2)])
            lathe("gold", sx, -11.5, [(.25, 11.5), (.3, 11.9), (.03, 12.4)], 8)
        boxr("wash:" + WHITE, "wash:" + WHITE, 0, -11, 1.8, 1.8, -.5, 1.0, 45); lathe("wash:" + WHITE, 0, -11, [(.7, 1.0), (.95, 1.7), (.4, 2.5), (.3, 2.9)], 10)
        for (a, b) in (((-20.5, -14.5), (-3, -14.5)), ((3, -14.5), (20.5, -14.5)), ((-20.5, -14.5), (-20.5, -6)), ((20.5, -14.5), (20.5, -6))):
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); boxr("wash:" + WHITE, "paint:" + MAROON, m[0], m[1], abs(b[0] - a[0]) + .6, abs(b[1] - a[1]) + .6, -1.5, 1.5)
    top = z + 15.0 * U
    for a in (205, 250, 295):
        r = 30 * U; ex, ey = x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))
        if path_dist(ex, ey) > 2.5: beam("wood:#6b5846", (ex, ey, zt(ex, ey) - .3), (ex, ey, zt(ex, ey) + 2.4), .05, 5); flag_line((*loc(x, y, rot, 0, 5.5), top), (ex, ey, zt(ex, ey) + 2.4))

def scripture_hall():
    (x, y), z = AT["temple library"], LEVEL["temple library"]; rot = 52.0; paint("pave", x, y, 17 * U, 13 * U, rot, .9, 2.0)
    with placed_s(x, y, rot, z):
        T = battered("paint:#b5562c", 0, 0, 13, 9.5, -2, 7.0, 0, .04, va=.4); walls("ashlar", grow(rect(0, 0, 13, 9.5), .08), -2, .6); I = parapet(T, 7.0, "#3a1512", .7, .18)
        boxr("wash:" + WHITE, None, 0, 0, 12.8, 9.3, 3.2, 3.6)
        rows_of_windows(0, 0, 13, 9.5, 0, 0, 2, every=2.6, trim="#e2b53a", skip0=False, ww=1.0, hh=1.5, bt=.04); door(0, 0, 13, 9.5, 0, 0, .5, 0, 1.6, 2.3, "#e2b53a", out=.12)
        finials(I, 7.2); gold_roof(0, 0, 4.2, 3.0, 7.0, 1.5, 0, .5)
        for k in range(5): cyl("bronze", -6.9, -3.2 + k * 1.6, .32, .9, 1.9, 8); cyl("wood:#6b5846", -6.9, -3.2 + k * 1.6, .05, 0, 2.2, 4)      # prayer wheels along the west wall
        boxr("wood:#5a4030", "earth:#93846c", -6.9, 0, 1.1, 8.6, 2.2, 2.4)

def printing_house():
    """Where the woodblocks are kept and the pages printed: a long hall, sheets drying on racks before it."""
    (x, y), z = AT["northwest library"], LEVEL["northwest library"]; rot = 38.0
    with placed_s(x, y, rot, z):
        T = battered("wash:" + WHITE, 0, 1, 19, 8.5, -2, 6.4, 0, .05, va=.7); walls("rubble", grow(rect(0, 1, 19, 8.5), .08), -2, .6); I = parapet(T, 6.4, MAROON, .7, .16)
        rows_of_windows(0, 1, 19, 8.5, 0, 0, 2, every=2.3, trim="#2f63b5", skip0=False, ww=.9, hh=1.3); door(0, 1, 19, 8.5, 0, 0, .5, 0, 1.5, 2.2, "#2f63b5", out=.12)
        finials(I, 6.6, 2)
        for k in range(6):      # paper drying on frames
            px_ = -7 + k * 2.8; bar("wood:#6b5846", (px_, -5.6, 0), (px_, -5.6, 1.7), .08, .08); bar("wood:#6b5846", (px_ + 2, -5.6, 0), (px_ + 2, -5.6, 1.7), .08, .08)
            face("paint:#efe6cf", [(px_ + .1, -5.6, .5), (px_ + 1.9, -5.6, .5), (px_ + 1.9, -5.9, 1.65), (px_ + .1, -5.9, 1.65)])
        boxr("wood:#5a4030", "wood:#5a4030", 7.5, -5.6, 2.2, 1.2, 0, .9); boxr("paint:#efe6cf", "paint:#efe6cf", 7.5, -5.6, 1.8, .9, .9, 1.25)

BARREL = None
def yard_parts():
    global BARREL, POT, CHURN, SACK
    with Part("barrel") as BARREL: lathe("wood:#7a5f44", 0, 0, [(.36, 0), (.45, .45), (.36, .9)], 10); lathe("paint:#3a2c22", 0, 0, [(.42, .2), (.43, .26)], 10, cap_top=False); lathe("paint:#3a2c22", 0, 0, [(.43, .64), (.42, .7)], 10, cap_top=False)
    with Part("pot") as POT: lathe("clay", 0, 0, [(.14, 0), (.3, .22), (.26, .45), (.14, .55), (.18, .62)], 9)
    with Part("churn") as CHURN: lathe("wood:#6b5846", 0, 0, [(.2, 0), (.17, 1.25)], 8); lathe("bronze", 0, 0, [(.21, .3), (.21, .36)], 8, cap_top=False); lathe("bronze", 0, 0, [(.19, .95), (.19, 1.0)], 8, cap_top=False); cyl("wood:#4d3d2e", 0, 0, .03, 1.25, 1.75, 4)
    with Part("sack") as SACK: lathe("cloth:#b9a47e", 0, 0, [(.3, 0), (.36, .25), (.3, .6), (.12, .72)], 8)

def brewery():
    """Where the barley beer is made: the house, a lean-to over three copper vats, barrels in the yard."""
    (x, y), z = AT["winery"], LEVEL["winery"]; rot = 50.0; paint("bare", x, y, 20 * U, 16 * U, rot, 1.0, 2.5)
    house(*loc(x, y, rot, 2.6, 2.6), 11, 8.5, rot, 2, z=z, g=g, door_side=0, trim="#3f8a4a", claim_it=False)
    with placed_s(x, y, rot, z):
        for k in range(3): lathe("bronze", -6.2 + k * 2.3, -4.6, [(.85, 0), (1.0, .7), (.9, 1.35), (.55, 1.55)], 12); cyl("rubble", -6.2 + k * 2.3, -4.6, 1.15, -.5, .25, 10)
        for px_, py_ in ((-7.6, -6.2), (-7.6, -3.0), (-.3, -6.2), (-.3, -3.0)): bar("wood:#5a4030", (px_, py_, 0), (px_, py_, 2.6 if py_ > -4 else 2.2), .16, .16)
        face("wood:#6b5846", [(-8.1, -6.7, 2.15), (.2, -6.7, 2.15), (.2, -2.6, 2.7), (-8.1, -2.6, 2.7)])
        for k, (bx, by) in enumerate(((2.2, -5.2), (3.2, -5.4), (2.7, -4.4), (4.3, -5.0), (5.2, -5.6), (5.0, -4.3), (6.3, -5.1))): inst(BARREL.mesh, bx, by, 0, rot=k, sc=U)
        inst(BARREL.mesh, 2.7, -5.0, .9, sc=U); boxr("wood:#4d3d2e", "wood:#4d3d2e", 8.2, -1.5, 1.2, 5.5, 0, 1.3)

def dairy():
    """The yak dairy: the house, a round stone corral, churns by the door, hay for the winter."""
    (x, y), z = AT["fishery"], LEVEL["fishery"]; rot = 44.0; paint("bare", x, y, 25 * U, 20 * U, rot, 1.0, 2.5)
    house(*loc(x, y, rot, -4.0, 3.6), 10.5, 8, rot, 2, z=z, g=g, door_side=0, trim="#2f63b5", claim_it=False)
    to = lambda lx, ly: loc(x, y, rot, lx, ly)
    ring_ = [to(7.0 + 5.6 * math.cos(a), -1.0 + 4.8 * math.sin(a)) for a in [math.radians(t) for t in range(20, 361, 20)]]; stone_wall(ring_, 1.25, .7)
    with placed_s(x, y, rot, z):
        for k in range(4): inst(CHURN.mesh, -6.0 + k * .7, -2.2, 0, sc=U)
        lathe("straw", 0.5, -6.2, [(1.9, 0), (2.1, 1.0), (1.2, 2.4), (.15, 3.1)], 12); lathe("straw", -3.6, -6.6, [(1.4, 0), (1.5, .8), (.8, 1.8), (.1, 2.3)], 10)
        boxr("wood:#5a4030", "straw", 7.0, 5.6, 4.2, 2.2, 0, 1.9)

def granary():
    """The village's grain store: a tall storehouse, sheaves drying on its roof, the threshing floor and its heap before it."""
    (x, y), z = AT["granary"], LEVEL["granary"]; rot = 40.0; paint("bare", x, y, 22 * U, 18 * U, rot, 1.0, 2.5)
    with placed_s(x, y, rot, z):
        T = battered("wash:" + CREAM, -3, 3, 10.5, 9, -2, 9.2, 0, .055, va=.35); walls("rubble", grow(rect(-3, 3, 10.5, 9), .08), -2, 1.2); I = parapet(T, 9.2, "#4a2a1c", .6)
        for side in (0, 1, 2, 3):
            for fl in (1, 2): window(-3, 3, 10.5, 9, 0, side, .5, fl * 3.0 + .6, .55, .6, batter_in=.055 * (fl * 3 + 2.6))
        door(-3, 3, 10.5, 9, 0, 0, .5, 0, 1.3, 2.0, "#e2b53a", out=.15)
        for k in range(7): boxr("straw", "straw", -6.2 + k * 1.05, 3 + (k % 2) * 1.4 - .7, .8, 1.6, 9.0, 9.9 + (k % 3) * .2, k * 13)
        bar("wood:#6b5846", (2.6, -1.4, 0), (2.4, -1.2, 9.4), .1, .1); bar("wood:#6b5846", (3.2, -1.4, 0), (3.0, -1.2, 9.4), .1, .1)
        for k in range(11): bar("wood:#6b5846", (2.58 - k * .018, -1.38 + k * .018, .7 + k * .8), (3.18 - k * .018, -1.38 + k * .018, .7 + k * .8), .07, .07)
        lathe("paving", 5.0, -4.2, [(4.2, -.5), (4.2, .08), (0.01, .1)], 20); lathe("straw", 5.0, -4.2, [(1.8, .08), (1.2, .7), (.1, 1.25)], 12)
        for k, (bx, by) in enumerate(((-7.4, -3.6), (-6.7, -3.9), (-7.0, -3.0), (-6.0, -3.4), (-5.4, -3.9))): inst(SACK.mesh, bx, by, 0, rot=k * 1.3, sc=U)
        boxr("wood:#5a4030", "straw", 7.8, 4.0, 3.2, 4.6, 0, 2.2)

def pottery():
    (x, y), z = AT["pottery"], LEVEL["pottery"]; rot = 40.0; paint("bare", x, y, 19 * U, 16 * U, rot, 1.0, 2.5)
    house(*loc(x, y, rot, -1.5, 3.2), 9.5, 7, rot, 1, z=z, g=g, door_side=0, trim="#c2352b", claim_it=False, flags=False)
    with placed_s(x, y, rot, z):
        lathe("clay", 5.0, -1.0, [(2.0, -.5), (2.15, .9), (1.6, 2.0), (.7, 2.7), (.45, 2.9), (.45, 3.3)], 14); face("dark", [(4.4, -3.1, 0), (5.6, -3.1, 0), (5.6, -3.0, 1.0), (4.4, -3.0, 1.0)])
        for i in range(5):
            for j in range(4): inst(POT.mesh, -5.6 + i * .75, -4.2 - j * .7, 0, rot=i + j, sc=U * g.uniform(.8, 1.25))
        for i in range(3): inst(POT.mesh, 1.2 + i * .8, -4.9, 0, sc=U * 1.5)
        boxr("wood:#4d3d2e", "wood:#4d3d2e", 7.6, 3.5, 1.4, 4.0, 0, 1.2)

def hermitage():
    """The hermitage library: a small red-banded house of books inside its own wall, a chorten at the gate."""
    (x, y), z = AT["southeast library"], LEVEL["southeast library"]; rot = 50.0; paint("bare", x, y, 15 * U, 13 * U, rot, 1.0, 2.5)
    with placed_s(x, y, rot, z):
        T = battered("wash:" + WHITE, 0, 1.2, 9, 7.2, -2, 6.0, 0, .05, va=.9); walls("rubble", grow(rect(0, 1.2, 9, 7.2), .08), -2, .6); I = parapet(T, 6.0, MAROON, .9, .18)
        rows_of_windows(0, 1.2, 9, 7.2, 0, 0, 2, every=2.3, trim="#e2b53a", skip0=False, ww=.9, hh=1.3); door(0, 1.2, 9, 7.2, 0, 0, .5, 0, 1.2, 2.0, "#e2b53a", out=.12); finials(I, 6.2)
        for (a, b) in (((-7, -5.6), (-1.6, -5.6)), ((1.6, -5.6), (7, -5.6)), ((-7, -5.6), (-7, 5.4)), ((7, -5.6), (7, 5.4))):
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); boxr("wash:" + WHITE, "paint:" + MAROON, m[0], m[1], abs(b[0] - a[0]) + .5, abs(b[1] - a[1]) + .5, -1.5, 1.3)
    little_chorten(*loc(x, y, rot, 4.6, -3.4), z, .62 * U)

def manor(k, colour):
    """A headman's house, three floors high, its woodwork, parapet and great banner all in the household's colour."""
    (x, y), z = AT[k], LEVEL[k]; rot = 48.0 if k.endswith("P") else 42.0
    with placed_s(x, y, rot, z):
        T = battered("wash:" + WHITE, 0, 0, 13, 10.5, -2, 9.4, 0, .05, va=.15); walls("ashlar", grow(rect(0, 0, 13, 10.5), .08), -2, .7); I = parapet(T, 9.4, colour, 1.0, .2)
        boxr("paint:" + colour, None, 0, 0, 12.5, 10.0, 6.0, 6.35)
        rows_of_windows(0, 0, 13, 10.5, 0, 0, 3, every=2.5, trim=colour, ww=1.15, hh=1.55); door(0, 0, 13, 10.5, 0, 0, .5, 0, 1.7, 2.3, colour, out=.14)
        face("paint:" + colour, [(-2.4, -5.4, 2.5), (2.4, -5.4, 2.5), (2.4, -7.2, 2.2), (-2.4, -7.2, 2.2)])        # the awning over the door
        for sx in (-2.3, 2.3): bar("wood:#5a4030", (sx, -7.1, 0), (sx, -7.1, 2.2), .1, .1)
        beam("wood:#6b5846", (4.6, -3.6, 9.2), (4.6, -3.6, 17.5), .1, 6); face("paint:" + colour, [(4.6, -3.6, 11.0), (5.9, -3.6, 11.0), (5.9, -3.6, 17.3), (4.6, -3.6, 17.3)]); lathe("gold", 4.6, -3.6, [(.2, 17.5), (.26, 17.9), (.03, 18.4)], 8)
        for c_ in I: face("paint:" + colour, [P3(c_, 9.2), (c_[0] * .93, c_[1] * .93, 9.2), (c_[0] * .93, c_[1] * .93, 10.4), P3(c_, 10.4)])
        boxr("wood:#4d3d2e", "wood:#4d3d2e", 0, 4.4, 9.0, .6, 9.15, 9.8)

def square():
    (x, y), z = AT["crossroads"], LEVEL["crossroads"]; paint_disc("pave", x, y, 12.5, 1.0, 2.0)
    chorten(x, y, z, 2.3, 45, lines=7, g=g)
    c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
    for k in range(6):
        lx, ly = -11.0, -4.6 + k * 1.85; wx, wy = x + lx * c - ly * s, y + lx * s + ly * c; cyl("bronze", wx, wy, .48, zt(wx, wy) + 1.2, zt(wx, wy) + 2.7, 8); cyl("wood:#6b5846", wx, wy, .07, zt(wx, wy) - .2, zt(wx, wy) + 3.2, 4)

yard_parts(); gompa(); scripture_hall(); printing_house(); brewery(); dairy(); granary(); pottery(); hermitage(); manor("proposer P", "#2f63b5"); manor("proposer Q", "#c2352b"); square()

# ---------------------------------------------------------------- the village
def in_frame(x, y, m=20): u, v = m2px(x, y, zt(x, y)); return -m < u < 1600 + m and -m < v < 1200 + m
count = 0
for rnd in range(4):
    for r in roads:
        pts = [(p[0], p[1]) for p in r["pts"]]
        for (x, y, ux, uy, dd) in along(pts, 6.0):
            for sd in (1, -1):
                for row in (0, 1, 2):
                    w, d = g.uniform(6.0, 8.5), g.uniform(5.2, 7.0); W_, D_ = (w + 4.5) * U, d * U; off = D_ / 2 + g.uniform(2.2, 3.2) + row * g.uniform(10, 13)
                    cx, cy = x - uy * off * sd + g.uniform(-1.5, 1.5), y + ux * off * sd + g.uniform(-1.5, 1.5)
                    near = math.hypot(*[a_ - b_ for a_, b_ in zip(m2px(cx, cy, zt(cx, cy)), (800, 610))]) / 560.0
                    if g.random() < near * .95 - .25 + row * .1 or not in_frame(cx, cy): continue
                    rad = math.hypot(W_, D_) / 2; fl = 3 if g.random() < .25 else 2; h = (fl * 2.75 + .5) * U; ang = math.degrees(math.atan2(uy, ux)) + g.uniform(-7, 7)
                    if min([path_dist(cx, cy)] + [path_dist(*p) for p in rect(cx, cy, W_ + 1.2, D_ + 1.2, ang)]) < 2.1: continue
                    if not free(cx, cy, rad * .9, .9) or hides(cx, cy, rad * .8, h + 1.2) or bil(gdist, cx, cy) < 17 or bil(side, cx, cy) > .25 or bil(L.COV["snow"], cx, cy) > .3 or bil(slope0, cx, cy) > .5: continue
                    house(cx, cy, w, d, ang, fl, g=g, door_side=0 if sd > 0 else 2, wash=g.choice((WHITE, WHITE, WHITE, CREAM)), trim=g.choice(("#8a2f24", "#8a2f24", "#7a3a24", "#3f6a8a", "#b0772e")), blend=2.2); count += 1
for _ in range(2600):      # and houses set back from the lanes, filling the village out
    u_, v_ = g.gauss(800, 300), g.gauss(610, 210)
    if not (60 < u_ < 1540 and 60 < v_ < 1140): continue
    cx, cy = ground_px(u_, v_); w, d = g.uniform(5.6, 8.0), g.uniform(5.0, 6.6); W_, D_ = (w + 2.5) * U, d * U; rad = math.hypot(W_, D_) / 2; fl = 3 if g.random() < .2 else 2; h = (fl * 2.75 + .5) * U; ang = 45 + g.uniform(-28, 28)
    if min([path_dist(cx, cy)] + [path_dist(*p_) for p_ in rect(cx, cy, W_ + 1.2, D_ + 1.2, ang)]) < 2.1: continue
    if not free(cx, cy, rad * .9, .9) or hides(cx, cy, rad * .8, h + 1.2) or bil(gdist, cx, cy) < 17 or bil(side, cx, cy) > .25 or bil(L.COV["snow"], cx, cy) > .3 or bil(slope0, cx, cy) > .5: continue
    house(cx, cy, w, d, ang, fl, g=g, door_side=0, wash=g.choice((WHITE, WHITE, WHITE, CREAM)), trim=g.choice(("#8a2f24", "#8a2f24", "#7a3a24", "#3f6a8a", "#b0772e")), blend=2.2); count += 1
print("houses:", count)
# chortens and mani walls by the ways, flags over the lanes
for (u, v) in ((520, 300), (1050, 470), (330, 760), (850, 860), (1180, 780), (640, 240)):
    x, y = ground_px(u, v)
    if path_dist(x, y) > 3 and free(x, y, 2.5) and not hides(x, y, 1.2, 3): little_chorten(x, y, zt(x, y), .8); claim(x, y, 2, 3)
for (u0, v0, u1, v1) in ((900, 700, 985, 690), (560, 610, 640, 615)):
    a, b = ground_px(u0, v0), ground_px(u1, v1)
    if path_dist(*a) > 2.2 and path_dist(*b) > 2.2: mani_wall(a[0], a[1], b[0], b[1])

# a walled yard beside some houses, where there is room
for (hx, hy, hz, hr) in list(kit.ROOFS):
    if g.random() < .6:
        a = g.uniform(0, 6.28); yx, yy = hx + (hr + 4.5) * math.cos(a), hy + (hr + 4.5) * math.sin(a)
        if path_dist(yx, yy) > 6 and free(yx, yy, 4.2, .3) and bil(gdist, yx, yy) > 16:
            rr = [(yx + 4 * math.cos(t) * g.uniform(.85, 1.1), yy + 3.4 * math.sin(t) * g.uniform(.85, 1.1)) for t in [math.radians(q) for q in range(0, 331, 30)]]
            stone_wall(rr + rr[:1], .95, .55); claim(yx, yy, 4.0, 1.2); paint_disc("bare", yx, yy, 3.2, .8, 1.5)
            if g.random() < .5: lathe("straw", yx, yy, [(1.3, zt(yx, yy) - .3), (1.45, zt(yx, yy) + .8), (.8, zt(yx, yy) + 1.9), (.08, zt(yx, yy) + 2.5)], 10, va=g.random())
# a worn path from every house to the nearest lane
for (hx, hy, hz, hr) in kit.ROOFS:
    d_ = np.hypot(L.PS[:, 0] - hx, L.PS[:, 1] - hy); i = int(np.argmin(d_))
    if d_[i] < 34: footpath((hx, hy), (float(L.PS[i, 0]), float(L.PS[i, 1])), .9, .75)
# the gompa's kora: the path the pilgrims walk round it, a row of eight chortens beside the court, a mani wall on the way up
(gx_, gy_), gz_ = AT["temple"], LEVEL["temple"]
for k in range(8):
    cx_, cy_ = loc(gx_, gy_, 40, -15.5 + k * 3.0, -19.0)
    if path_dist(cx_, cy_) > 2.6: little_chorten(cx_, cy_, zt(cx_, cy_), .78)
ring_ = [loc(gx_, gy_, 40, 25 * math.cos(math.radians(t)), 4 + 20.5 * math.sin(math.radians(t))) for t in range(0, 361, 15)]
for a, b in zip(ring_, ring_[1:]): footpath(a, b, 1.1, .8)
for k in range(10):      # prayer wheels along the kora's east side
    wx, wy = loc(gx_, gy_, 40, 22.2, -6 + k * 2.0)
    if path_dist(wx, wy) > 2.2: cyl("bronze", wx, wy, .45, zt(wx, wy) + 1.1, zt(wx, wy) + 2.5, 8); cyl("wood:#6b5846", wx, wy, .07, zt(wx, wy) - .2, zt(wx, wy) + 3.0, 4)
ma, mb = ground_px(1215, 420), ground_px(1232, 362)
if path_dist(*ma) > 2.4 and path_dist(*mb) > 2.4: mani_wall(ma[0], ma[1], mb[0], mb[1])
# water-turned prayer wheels in little stone houses by the river, below each bridge
for sp in L.SPANS:
    ex, ey, ez = sp[0]; dx, dy = sp[-1][0] - ex, sp[-1][1] - ey; Lg = math.hypot(dx, dy); hx_, hy_ = ex - dx / Lg * 4.5 + dy / Lg * 7, ey - dy / Lg * 4.5 - dx / Lg * 7
    if path_dist(hx_, hy_) > 3.5 and free(hx_, hy_, 3, .5) and not hides(hx_, hy_, 2.5, 4):
        z_ = pad(hx_, hy_, 5, 5, 45, blend=2)
        with placed_s(hx_, hy_, 45, z_): T = battered("rubble", 0, 0, 3.2, 3.2, -2, 2.6, 0, .04); cap("roof", grow(T, .3), 2.6); cyl("bronze", 0, -1.75, .5, .6, 1.9, 8)
        claim(hx_, hy_, 3, 4)

# strings of prayer flags from roof to roof across the lanes
nf = 0
for i, (ax, ay, az, ar) in enumerate(kit.ROOFS):
    for (bx, by, bz, br) in kit.ROOFS[i + 1:]:
        dd = math.hypot(ax - bx, ay - by)
        if 13 < dd < 26 and g.random() < .16 and nf < 46: flag_line((ax, ay, az + .5), (bx, by, bz + .5), size=.6); nf += 1
# haystacks on the terraces
for _ in range(400):
    x, y = g.uniform(-300, 300), g.uniform(-300, 300)
    if in_frame(x, y) and bil(L.COV["field"], x, y) > .8 and path_dist(x, y) > 4 and free(x, y, 2.5, 1) and g.random() < .14:
        z = zt(x, y); sc = g.uniform(1.4, 2.1); lathe("straw", x, y, [(1.0 * sc, z - .3), (1.15 * sc, z + .6 * sc), (.7 * sc, z + 1.5 * sc), (.08 * sc, z + 2.0 * sc)], 10, va=g.random()); claim(x, y, 1.8, 2)

# ---------------------------------------------------------------- what grows and lies about
pines = load("pine_tree_01", lods=("LOD1", "LOD0", "LOD2")); small = load("tree_small_02"); shrubs = load("shrub_01") + load("shrub_02") + load("shrub_04"); bush = load("wild_rooibos_bush")
rocks = load("namaqualand_boulder_02") + load("namaqualand_boulder_03") + load("namaqualand_boulder_05") + load("boulder_01"); stones = load("namaqualand_stones_01"); moss = load("rock_moss_set_01")
cliffs = load("namaqualand_cliff_02") + load("rock_face_01") + load("rock_face_02") + load("coastal_cliff_02") + load("namaqualand_cliff_01")
gy2, gx2 = np.gradient(L.Z, kit.STEP); slope2 = np.hypot(gx2, gy2); nc = 0
for _ in range(2600):
    x, y = g.uniform(-340, 340), g.uniform(-340, 340)
    if not in_frame(x, y, 120) or path_dist(x, y) < 9 or not free(x, y, 5, 2): continue
    sl = bil(slope2, x, y); mt = bil(mount, x, y); go = bil(gorge, x, y); up = sstep(110, 190, (y - x) / R2)
    if cliffs and g.random() < (.5 * sl + .6 * mt + .5 * up) * .55 + (.5 if .15 < go < .8 else 0) and bil(fieldm, x, y) < .2:
        h = g.uniform(5, 11) * (1 + 1.3 * mt + .8 * up) * (.55 if go > .1 else 1)
        if not hides(x, y, h * .6, h): strew(cliffs, x, y, g, h=h, sink=.28, tilt=.25); claim(x, y, h * .35, h); nc += 1
print("crags:", nc)
def ok(x, y, r, h): return in_frame(x, y, 80) and path_dist(x, y) > r + 1.8 and free(x, y, r, .6) and not hides(x, y, r, h)
n = 0
for _ in range(70000):
    x, y = g.uniform(-330, 330), g.uniform(-330, 330); fl = bil(flank, x, y); sn = bil(L.COV["snow"], x, y); fi = bil(fieldm, x, y); ss = (y - x) / R2
    grove = sstep(.02, .22, float(fbm(np.array(x), np.array(y), 55, 3, seed=90)))
    wood_ = (1.2 * sstep(10, 70, fl) + 1.6 * sstep(62, 100, ss) + .6 * bil(gully, x, y) + .45 * grove) * (1 - sn * .7)
    if pines and g.random() < wood_ * .9 and fi < .3:
        h = g.uniform(12, 21)
        if ok(x, y, 2.0, h): strew(pines, x, y, g, h=h); claim(x, y, .9, h); n += 1
    elif small and g.random() < .10 + .6 * bil(gully, x, y) + .2 * grove + .5 * (bil(L.COV["bare"], x, y) > .2) and fi < .5 and sn < .2 and ss < 70:
        h = g.uniform(6.5, 10.5)
        if ok(x, y, 2.6, h): strew(small, x, y, g, h=h); claim(x, y, 1.5, h); n += 1
print("trees:", n)
for _ in range(14000):
    x, y = g.uniform(-330, 330), g.uniform(-330, 330)
    if not in_frame(x, y, 60) or path_dist(x, y) < 2.4 or not free(x, y, .8, .2): continue
    fi = bil(fieldm, x, y); sn = bil(L.COV["snow"], x, y); fl = bil(flank, x, y)
    if fi > .35 or sn > .75: continue
    t = g.random()
    if t < .45 and shrubs and sn < .3: strew(shrubs + bush, x, y, g, h=g.uniform(.9, 2.2))
    elif t < .7 and stones: strew(stones, x, y, g, scale=g.uniform(1.2, 3.0), sink=.2)
    elif rocks and g.random() < .2 + .8 * sstep(40, 120, fl): strew(rocks, x, y, g, h=g.uniform(1.2, 3.5) * (1 + 1.6 * sstep(60, 140, fl)), sink=.3, tilt=.3)

# the river in its gorge
wv = []
for sv in np.arange(-260, 215, 1.5):
    tv = -83 - 5 * math.sin(sv / 40.0); wv.append(((tv - sv) / R2, (tv + sv) / R2))
for (a, b) in zip(wv, wv[1:]):
    dx, dy = b[0] - a[0], b[1] - a[1]; Lg = math.hypot(dx, dy); nx, ny = -dy / Lg * 4.2, dx / Lg * 4.2
    face("water", [(a[0] - nx, a[1] - ny, zt(a[0], a[1]) + .5), (a[0] + nx, a[1] + ny, zt(a[0], a[1]) + .5), (b[0] + nx, b[1] + ny, zt(b[0], b[1]) + .5), (b[0] - nx, b[1] - ny, zt(b[0], b[1]) + .5)])
mats.MATS["water"] = water_material()

# ---------------------------------------------------------------- the network, the light, the picture
places = {k: dict(label=v[0], at=[round(AT[k][0], 2), round(AT[k][1], 2), round(zt(*AT[k]), 2)], door=[round(DOOR[k][0], 2), round(DOOR[k][1], 2), round(zt(*DOOR[k]), 2)]) for k, v in PLACES.items()}
net = write_network(os.path.join(kit.ALLEGORY, "city.json"), "city", places, roads, setting="a Buddhist monastery village high in the Himalaya")
light(sun_el=37, sun_az=104, sun=5.6, sky=.5, exposure=.4)
finish(net)
