"""The acropolis: the broad stair up from the town, the propylon at its head, and on the summit a sanctuary on the pattern of
Priene's and Pergamon's: an Ionic temple with its altar to the east, stoas along the precinct's edges (the library's rooms
behind one of them, as at Pergamon), a treasury, a colossal bronze, votives along the ways. The west stair goes down to the postern."""
import math, random
from . import core, land, arch, props, houses, civic
from .core import S, face, wall, walls, cap, prism, boxr, box, rect, grow, inst, lerp, placed
from .arch import colonnade, entablature, gable, panel, column

STONE = civic.STONE; STEPK = "marble:#d9d2c0"
def broad_stair():
    y0, y1, hw = land.STAIR_Y0, land.STAIR_Y1, 3.5; z0, z1 = land.Z40, land.TOP; n = round((z1 - z0) / .165)
    for i in range(n):
        ya, yb = lerp(y0, y1, i / n), lerp(y0, y1, (i + 1) / n); zt_ = lerp(z0, z1, (i + .6) / n)
        prism(STONE, STEPK, box(-hw, ya, hw, yb + .02), min(land.zt(-hw, ya), land.zt(hw, ya), zt_ - .3) - .6, zt_, zb=0, vb=zt_ - 2)
    for sx in (-1, 1):                                                                    # parapets stepping up with the flights, a pier at every landing
        m = 20
        for k in range(m):
            ya, yb = lerp(y0, y1, k / m), lerp(y0, y1, (k + 1) / m); zb_ = lerp(z0, z1, (k + 1) / m)
            seg = box(min(sx * hw, sx * (hw + .7)), ya, max(sx * hw, sx * (hw + .7)), yb)
            prism(STONE, "paving:#cfc6b0", seg, land.zmin(seg) - .8, zb_ + .95, zb=0, vb=zb_ - 3)
            if k % 4 == 3:
                boxr(STONE, "paving:#cfc6b0", sx * (hw + .35), yb, 1.3, 1.3, min(land.zt(sx * (hw + .35), yb), zb_) - .8, zb_ + 1.5, zb=0, vb=zb_ - 3)
                inst(random.Random(k * 7 + sx).choice((props.STATUE_M, props.STATUE_B, props.STELE)), sx * (hw + .35), yb, zb_ + 1.5, 0 if sx < 0 else math.pi, .8)
    land.take(box(-hw - 1.2, y0, hw + 1.2, y1))
def west_stair():
    segs = [gq for gq in land.GRADED if gq[5] == "stair" and abs(gq[0][1] - 114) < .1]
    x1 = max(max(a[0], b[0]) for a, b, *_ in segs); x0 = min(min(a[0], b[0]) for a, b, *_ in segs); x = x1
    while x > x0 + .2:
        xa = x - .42; z = land.zroute((x + xa) / 2, 114.0)[0]
        if not (abs((x + xa) / 2 - land.POSTERN[0]) < 1.4):
            prism(STONE, STEPK, box(xa, 112.5, x, 115.5), min(land.zt(xa, 112.5), land.zt(xa, 115.5), z) - .8, z + .06, zb=0, vb=z - 2)
            for yy in (112.3, 115.7): prism(STONE, "paving:#cfc6b0", box(xa, yy - .22, x, yy + .22), min(land.zt(xa, yy), z) - .8, z + .8, zb=0, vb=z - 2)
        x = xa
    land.take(box(x0, 111.8, x1, 116.2))

def propylon():
    """The gate-building at the stair's head: Doric porches to the town and to the sanctuary, the way passing between."""
    w, d, hc = 13.0, 8.4, 5.6; cx, cy = 0.0, 105.8; z = land.TOP; kw = dict(va=.2, vb=z)
    with placed(cx, cy, 0):
        cap("paving:#d5ccb6", box(-w / 2, -d / 2, w / 2, d / 2), z + .05)
        for sx in (-1, 1):
            prism("marble", None, box(min(sx * w / 2, sx * (w / 2 - .7)), -d / 2 + .9, max(sx * w / 2, sx * (w / 2 - .7)), d / 2 - .9), z, z + hc + 1.4, **kw)
            prism("marble", None, box(min(sx * 2.6, sx * (w / 2 - .7)), -.35, max(sx * 2.6, sx * (w / 2 - .7)), .35), z, z + hc + 1.4, **kw)       # the gate wall, its doorway in the middle
        for yy in (-d / 2 + .6, d / 2 - .6):
            for xx in (-5.4, -3.2, 3.2, 5.4): inst(column("doric", hc, .46), xx, yy, z)
        zt = entablature(box(-w / 2, -d / 2 + .1, w / 2, d / 2 - .1), z + hc, hc, "doric")
        gable(-w / 2, -d / 2, w / 2, d / 2, zt, w / 2 * .25, "y", .2, "paint:#8fa3b8", key="tile:#c79f7c", ov=.45, rake=.4)
        for yy in (-d / 2 - .4, d / 2 + .4): inst(civic.AKRO, 0, yy, zt + w / 2 * .25 + .2)
    land.take(box(-w / 2, cy - d / 2, w / 2, cy + d / 2))

def build():
    if not land.HILL: return
    g = random.Random(41); z = land.TOP; SU = land.SUMMIT
    land.paint("earth", SU, .8, 2.0)
    for _ in range(46):                                                                   # the summit is living rock: it breaks through the trodden earth, and dry grass holds on between
        x, y = g.uniform(-50, 52), g.uniform(102, 170)
        if core.inpoly(x, y, SU) and land.road_dist(x, y) > 1.5:
            r = g.uniform(1.5, 5.5); land.paint_disc("rock", x, y, r, g.uniform(.6, 1.0), r * .8); land.clear_disc("earth", x, y, r * .7, r * .6)
    broad_stair(); west_stair(); propylon()
    # the temple, facing south over the town to the sea; the great altar before it; the precinct paved round both
    tz = civic.temple(8.0, 140.5, 0, 15.4, 30.5, 8.4, 6, 11, "ionic", z, peripteral=True, blend=0)
    land.paint("pave", box(-3.5, 114.5, 19.5, 158.5), 1.0, 1.5); land.paint("pave", box(-3, 104, 3, 128), 1.0, 1.0)
    inst(props.ALTAR, 8.0, 119.6, z, 0, 1.2); land.take(rect(8.0, 119.6, 9.5, 5.5))
    # stoas on the west and south-west: the library's reading rooms open off the long one's back wall
    civic.stoa(-45.5, 117.6, -15.0, 128.2, "s", 4.6, rooms=4.2, z=z, va=.35, blend=0)
    civic.stoa(-49.6, 129.4, -40.4, 157.5, "e", 4.2, z=z, va=.5, blend=0)
    for k in range(4): inst(props.BENCH, -41 + k * 7, 115.9, z, 0)
    # a treasury east of the forecourt, the colossal bronze, and a long stoa closing the north side
    civic.temple(34.0, 115.0, -90, 6.4, 10.5, 4.2, 2, 4, "doric", z, peripteral=False, steps=2, blend=0)
    inst(props.COLOSSUS, -8.5, 122.5, z, math.pi); land.take(rect(-8.5, 122.5, 5, 5))
    civic.stoa(-30.0, 160.0, 34.0, 167.8, "s", 4.4, z=z, va=.45, blend=0)
    # votives: statues and stelai along the processional way, exedrae, herms by the library, monuments round the temple
    for k in range(6):
        y = 109.5 + k * 1.3
        for sx in (-1, 1):
            if g.random() < .8 and not (111.5 < y < 116.5 and sx < 0): inst(g.choice((props.STATUE_M, props.STATUE_B, props.STELE, props.STELE)), sx * (3.3 + g.uniform(0, .3)), y, z, math.pi / 2 * -sx)
    for k in range(12): inst(g.choice((props.STELE, props.HERM, props.STATUE_M)), -44 + k * 2.4, 111.2 + g.uniform(-.3, .3), z, 0)
    inst(props.EXEDRA, 24, 124.0, z, math.pi); inst(props.EXEDRA, -10, 147.0, z, -math.pi / 2)
    for x, y in ((21, 131), (21, 142), (21, 152), (38, 128.5), (38, 145.5), (-4, 131), (-4, 141), (-22, 136), (-30, 152), (44, 150), (27, 118)): inst(g.choice((props.STATUE_B, props.STATUE_M, props.VOTIVE, props.BASE)), x, y, z, g.uniform(0, 6.3))
    inst(props.WELL, 40, 120, z, 0, 1.6)                                                  # the cistern's mouth
    for x, y, kind in ((43, 156, "olive"), (26, 152, "cypress"), (-34, 152, "cypress"), (46, 137, "cypress"), (-10, 155, "olive"), (40, 162, "cypress")): houses.TREES.append((x, y, z, kind))
    land.take(SU)
