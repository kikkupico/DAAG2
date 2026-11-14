"""The acropolis: the broad stair up from the town, the propylon at its head, and on the summit a sanctuary on the pattern of
Athens, Delphi, and Priene: an east-facing Ionic temple standing in free space on a stepped terrace, its monumental stepped
altar before its eastern pronaos, a circular tholos in the south-eastern court, a Doric treasury along the Sacred Way, the
library stoa in the south-west, a walled sacred olive enclosure (Pandroseion) in the western terrace, and along the northern
terrace a sequence of Hellenistic ornamental monuments—a heroic statuary bathron, a choragic tripod monument (on the pattern of
Lysikrates), a tall pillar monument, semicircular exedrae, bronze tripods, and a colossal bronze Athena."""
import math, random
import numpy as np
from . import core, land, arch, props, houses, civic
from .core import S, face, wall, walls, cap, prism, boxr, box, rect, grow, inst, lerp, placed, cyl, lathe, beam, bar
from .arch import colonnade, entablature, gable, panel, column, ridge, tiles

STONE = civic.STONE; STEPK = "marble:#d9d2c0"; MARBLE = "marble:#e8e1d0"; PAVE = "paving:#dcd3be"
GROVE = []

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
                px = sx * (hw + .35); bz = min(land.zt(px, yb), zb_) - .8
                boxr(STONE, "paving:#cfc6b0", px, yb, 1.35, 1.35, bz, zb_ + 1.5, zb=0, vb=zb_ - 3)
                boxr(MARBLE, MARBLE, px, yb, 1.55, 1.55, zb_ + 1.5, zb_ + 1.66)
                votive = random.Random(k * 7 + sx).choice((props.STATUE_M, props.STATUE_B, props.TRIPOD, props.STELE))
                inst(votive, px, yb, zb_ + 1.66, 0 if sx < 0 else math.pi, .82)
        # monumental entrance piers with bronze tripods at the foot and head of the stair
        for yy, zz in ((y0 + .6, z0), (y1 - .6, z1)):
            px = sx * (hw + .65)
            boxr(STONE, STEPK, px, yy, 1.5, 1.5, min(land.zt(px, yy), zz) - .8, zz + 1.55, zb=0, vb=zz - 2)
            boxr(MARBLE, MARBLE, px, yy, 1.7, 1.7, zz + 1.55, zz + 1.72)
            inst(props.TRIPOD, px, yy, zz + 1.72, 0 if sx < 0 else math.pi, .85)
    land.take(box(-hw - 1.5, y0, hw + 1.5, y1))

def west_stair():
    segs = [gq for gq in land.GRADED if gq[5] == "stair" and abs(gq[0][1] - 114) < .1]
    x1 = max(max(a[0], b[0]) for a, b, *_ in segs); x0 = min(min(a[0], b[0]) for a, b, *_ in segs); x = x1
    while x > x0 + .2:
        xa = x - .42; z = land.zroute((x + xa) / 2, 114.0)[0]
        if not (abs((x + xa) / 2 - land.POSTERN[0]) < 1.4):
            prism(STONE, STEPK, box(xa, 112.5, x, 115.5), min(land.zt(xa, 112.5), land.zt(xa, 115.5), z) - .8, z + .06, zb=0, vb=z - 2)
            for yy in (112.3, 115.7): prism(STONE, "paving:#cfc6b0", box(xa, yy - .22, x, yy + .22), min(land.zt(xa, yy), z) - .8, z + .8, zb=0, vb=z - 2)
        x = xa
    for sy in (-1, 1):
        inst(props.HERM, -46.2, 114.0 + sy * 2.1, land.TOP, math.pi / 2)
    land.take(box(x0, 111.8, x1, 116.2))

def propylon():
    """The gate-building at the stair's head: Doric porches to the town and to the sanctuary, inner Ionic columns, open
    bronze-studded gate leaves, sculpted pediments, gilded akroteria, and flanking braziers."""
    w, d, hc = 13.6, 8.8, 5.8; cx, cy = 0.0, 105.8; z = land.TOP; kw = dict(va=.2, vb=z)
    with placed(cx, cy, 0):
        # keep the central passage flush with the route at z+.05, with stepped marble stylobates under the flanking porches
        cap("paving:#d5ccb6", box(-w / 2, -d / 2, w / 2, d / 2), z + .05)
        for sx in (-1, 1):
            x0, x1 = (min(sx * w / 2, sx * 2.65), max(sx * w / 2, sx * 2.65))
            prism("marble", STEPK, box(x0, -d / 2 - .35, x1, d / 2 + .35), z, z + .22)
            prism("marble", None, box(min(sx * w / 2, sx * (w / 2 - .75)), -d / 2 + .9, max(sx * w / 2, sx * (w / 2 - .75)), d / 2 - .9), z + .22, z + hc + 1.4, **kw)
            # projecting south antae wings framing the entrance
            prism("marble", None, box(min(sx * w / 2, sx * (w / 2 - .75)), -d / 2 - .25, max(sx * w / 2, sx * (w / 2 - .75)), -d / 2 + .9), z + .22, z + hc + .22, **kw)
            # gate wall with doorway in the middle and folded-back bronze-trimmed gate leaves
            prism("marble", None, box(min(sx * 2.6, sx * (w / 2 - .75)), -.38, max(sx * 2.6, sx * (w / 2 - .75)), .38), z + .22, z + hc + 1.4, **kw)
            boxr("marble:#e2dac8", "marble:#e2dac8", sx * 2.55, 0, .28, .92, z + .05, z + 4.35)
            boxr("wood:#5a4028", "bronze", sx * 2.38, 1.05, .12, 1.6, z + .06, z + 4.1)
        boxr("marble:#e2dac8", "marble:#e2dac8", 0, 0, 5.4, .95, z + 4.35, z + 4.82)    # stone lintel over the gate
        for yy in (-d / 2 + .58, d / 2 - .58):
            for xx in (-5.6, -3.35, 3.35, 5.6): inst(column("doric", hc, .46), xx, yy, z + .22)
        for yy in (-1.85, 1.85):                                                          # inner Ionic columns flanking the Sacred Way
            for xx in (-2.95, 2.95): inst(column("ionic", hc + .15, .34), xx, yy, z + .22)
        zt = entablature(box(-w / 2, -d / 2 + .1, w / 2, d / 2 - .1), z + hc + .22, hc, "doric")
        rise = w / 2 * .25
        gable(-w / 2, -d / 2, w / 2, d / 2, zt, rise, "y", .2, "paint:#354f6b", key="tile:#c79f7c", ov=.45, rake=.4)
        for yy, sgn in ((-d / 2 - .42, -1), (d / 2 + .42, 1)):
            for sx in (-1, 1): bar("marble", (sx * (w / 2 + .42), yy, zt - .05), (0, yy, zt + rise + .1), .45, .28)
            bar("marble", (-w / 2 - .42, yy, zt + .04), (w / 2 + .42, yy, zt + .04), .45, .18)
            for k in range(5):
                t = (k + .5) / 5 * 2 - 1; hh = rise * (1 - abs(t)) * .72
                if hh > .22: boxr("marble:#f3efe5", "marble:#f3efe5", t * (w / 2 - .7), yy - sgn * .22, .38, .2, zt + .14, zt + .14 + hh)
            inst(civic.AKRO, 0, yy, zt + rise + .22, 0, .95)
            inst(civic.AKRO, -w / 2 - .15, yy, zt + .18, 0, .65)
            inst(civic.AKRO, w / 2 + .15, yy, zt + .18, 0, .65)
        for sx in (-1, 1):
            inst(props.BRAZIER, sx * 4.5, -d / 2 - .9, z + .05, 0, 1.05)
    land.take(box(-w / 2 - .5, cy - d / 2 - .5, w / 2 + .5, cy + d / 2 + .5))

def temple_terrace(x0, y0, x1, y1, z, h=.36):
    """A stepped marble sanctuary terrace supporting the east-facing temple, with ceremonial steps along the east front and south flank."""
    for k, (g, zz) in enumerate(((.45, z + h * .5), (0.0, z + h))):
        prism("marble:#dfd7c4", PAVE if k == 1 else STEPK, box(x0 - g, y0 - g, x1 + g, y1 + g), z - .2, zz)
    for pts in (box(x0 + .35, y0 + .35, x1 - .35, y0 + .75), box(x0 + .35, y1 - .75, x1 - .35, y1 - .35),
                box(x0 + .35, y0 + .35, x0 + .75, y1 - .35), box(x1 - .75, y0 + .35, x1 - .35, y1 - .35)):
        cap("marble:#eae3d2", pts, z + h + .01)
    return z + h

def olive_enclosure(cx, cy, z):
    """A walled marble peribolos enclosure in the west court (on the pattern of the Pandroseion at Athens) housing the sacred
    olive tree and an archaic hero altar."""
    hw, hd = 3.6, 3.4
    with placed(cx, cy, 0):
        prism("marble:#dfd7c4", "earth:#8b7858", box(-hw, -hd, hw, hd), z - .1, z + .14)
        for pts in (box(-hw, -hd, hw, -hd + .32), box(-hw, hd - .32, hw, hd), box(-hw, -hd + .32, -hw + .32, hd - .32),
                    box(hw - .32, -hd + .32, hw, -1.1), box(hw - .32, 1.1, hw, hd - .32)):
            prism(MARBLE, STEPK, pts, z + .14, z + .92)
        for xx, yy in ((-hw + .16, -hd + .16), (-hw + .16, hd - .16), (hw - .16, -hd + .16), (hw - .16, hd - .16), (hw - .16, -1.1), (hw - .16, 1.1)):
            boxr(MARBLE, MARBLE, xx, yy, .48, .48, z + .14, z + 1.15)
        inst(props.ALTAR, 1.4, 0.0, z + .14, math.pi / 2, .50)
    houses.TREES.append((cx - .7, cy + .2, z + .14, "olive"))
    land.take(box(cx - hw - .6, cy - hd - .6, cx + hw + .6, cy + hd + .6))

def statue_bathron(cx, cy, z, rot=0):
    """A Hellenistic stepped marble statuary podium (on the pattern of the Monument of the Eponymous Heroes / Daochos Base at
    Delphi): a 3-stepped marble krepis, moulded orthostate backdrop parapet with anta piers, bronze tripods at the ends, and five
    honorific bronze and marble statues facing the temple court."""
    hw, hd = 4.8, 1.35
    with placed(cx, cy, rot):
        for k, (g, zz) in enumerate(((.44, z + .20), (.22, z + .40), (0.0, z + .62))):
            prism("marble:#dfd7c4", STEPK if k < 2 else MARBLE, box(-hw - g, -hd - g, hw + g, hd + g), z - .1, zz)
        zp = z + .62
        # low moulded orthostate backdrop wall along the north edge and short returning antae at the ends
        prism(MARBLE, "marble:#f0ebdf", box(-hw + .15, hd - .42, hw - .15, hd), zp, zp + 1.35)
        prism("marble:#dcd3be", "marble:#f2ece0", box(-hw + .08, hd - .48, hw - .08, hd + .06), zp + 1.35, zp + 1.50)
        for sx in (-1, 1):
            boxr(MARBLE, "marble:#f2ece0", sx * (hw - .38), 0.0, .68, 2.2, zp, zp + 1.05)
            inst(props.TRIPOD, sx * (hw - .38), -.25, zp + 1.05, math.pi, .82)
        for k in range(5):
            xx = lerp(-hw + 1.45, hw - 1.45, k / 4)
            st = props.STATUE_B if k % 2 == 0 else props.STATUE_M
            inst(st, xx, -.15, zp, math.pi, .95)
    land.take(rect(cx, cy, hw * 2 + 1.8, hd * 2 + 1.8, rot))

def choragic_monument(cx, cy, z):
    """A circular marble choragic tripod monument (on the pattern of the Monument of Lysikrates in Athens, 334 BC): a high square
    stepped marble podium supporting a slender circular colonnaded tholos-drum, conical monolithic marble roof, and crowning
    gilded bronze tripod."""
    with placed(cx, cy, 0):
        for k, (w, zz) in enumerate(((4.2, z + .24), (3.8, z + .48), (3.4, z + .72))):
            boxr("marble:#dfd7c4", STEPK, 0, 0, w, w, z - .1, zz)
        # high square marble podium with base and cornice mouldings
        boxr(MARBLE, MARBLE, 0, 0, 2.95, 2.95, z + .72, z + 2.75)
        boxr("frieze", None, 0, 0, 3.0, 3.0, z + 2.25, z + 2.65)
        boxr("marble:#f0ebdf", STEPK, 0, 0, 3.25, 3.25, z + 2.75, z + 2.98)
        zs = z + 2.98; hc = 3.1; r_col = 1.28
        cyl(MARBLE, 0, 0, 1.48, zs, zs + .20, 20)
        cyl("marble:#eae3d2", 0, 0, 1.18, zs + .20, zs + .20 + hc, 20)
        col_me = column("ionic", hc, .14)
        for i in range(6):
            a = 2 * math.pi * i / 6 + math.pi / 6
            inst(col_me, r_col * math.cos(a), r_col * math.sin(a), zs + .20, a + math.pi / 2)
        zt = zs + .20 + hc
        cyl("marble:#f0ebdf", 0, 0, 1.46, zt, zt + .30, 20)
        cyl("frieze", 0, 0, 1.48, zt + .30, zt + .54, 20)
        cyl("marble:#f3efe5", 0, 0, 1.62, zt + .54, zt + .70, 20)
        # low conical marble roof with acanthus pedestal and crowning gilded tripod
        lathe("marble:#f0ebdf", 0, 0, [(1.64, zt + .70), (1.15, zt + 1.15), (.48, zt + 1.55), (.32, zt + 2.05), (.46, zt + 2.22)], 16, cap_top=True)
        inst(props.TRIPOD, 0, 0, zt + 2.20, 0, .95)
    land.take(rect(cx, cy, 5.2, 5.2))

def pillar_monument(cx, cy, z, rot=-45):
    """A tall Hellenistic votive pillar monument (on the pattern of the Pillar of Prusias / Eumenes II at Delphi): a stepped
    marble base, tapering rectangular marble shaft with moulded cornice, and crowning bronze equestrian statue high against the sky."""
    with placed(cx, cy, rot):
        boxr("marble:#dfd7c4", STEPK, 0, 0, 2.8, 3.6, z - .1, z + .26)
        boxr("marble:#e4dcc9", STEPK, 0, 0, 2.3, 3.1, z + .26, z + .52)
        boxr(MARBLE, MARBLE, 0, 0, 1.65, 2.45, z + .52, z + 4.35)
        boxr("frieze", None, 0, 0, 1.70, 2.50, z + 3.85, z + 4.20)
        boxr("marble:#f2ece0", "marble:#f2ece0", 0, 0, 1.95, 2.75, z + 4.35, z + 4.62)
        inst(props.EQUESTRIAN, 0, 0, z + 4.60, 0, .92)
    land.take(rect(cx, cy, 4.4, 4.4, rot))

def great_altar(cx, cy, z, rot=-90):
    """A Pergamene- and Priene-style monumental stepped altar before the east front of the temple: broad ceremonial steps facing
    the temple on the west, sculpted relief podium, U-shaped Ionic colonnade framing the upper sacrificial court, raised horned
    altar table (bomos) with glowing fire, and flanking bronze braziers."""
    w, d = 9.6, 6.4; hw, hd = w / 2, d / 2; zp = z + .96
    with placed(cx, cy, rot):
        prism("marble:#dfd7c4", STEPK, box(-hw - .45, -hd - .3, hw + .45, hd + .45), z - .2, z + .18)
        # 4 broad marble steps along the front (-y in local coords, west toward the temple when rot=-90)
        for i in range(4):
            y0 = -hd - .95 + i * .34; zz = z + (i + 1) * .24
            prism("marble:#e0d8c6", STEPK, box(-hw + .35, y0, hw - .35, hd), z, zz)
        # raised podium and U-shaped wings
        prism("marble:#e8e1d0", "paving:#e4dcc9", box(-hw, -hd + .4, hw, hd), z + .18, zp)
        # sculpted high-relief frieze band on the podium's three outer flanks, with carved relief figures catching the light
        for x0, y0, x1, y1 in ((-hw - .04, -hd + .5, -hw + .02, hd + .04), (hw - .02, -hd + .5, hw + .04, hd + .04), (-hw - .04, hd - .02, hw + .04, hd + .04)):
            prism("frieze", None, box(x0, y0, x1, y1), z + .34, z + .84)
        for sx in (-1, 1):
            for k in range(5):
                yy = lerp(-hd + 1.0, hd - .4, k / 4)
                boxr("marble:#f2ece0", "marble:#f2ece0", sx * (hw + .06), yy, .10, .32, z + .38, z + .80)
        for k in range(7):
            xx = lerp(-hw + .8, hw - .8, k / 6)
            boxr("marble:#f2ece0", "marble:#f2ece0", xx, hd + .06, .32, .10, z + .38, z + .80)
        # U-shaped Ionic colonnade around the upper court
        hc = 2.35; r = .17
        colonnade((-hw + .58, -hd + .85), (-hw + .58, hd - .58), 4, "ionic", hc, r, zp, rot=0)
        colonnade((hw - .58, -hd + .85), (hw - .58, hd - .58), 4, "ionic", hc, r, zp, rot=0)
        colonnade((-hw + .58, hd - .58), (hw - .58, hd - .58), 6, "ionic", hc, r, zp, ends=False, rot=0)
        # U-shaped marble entablature and cornice over the wings
        for pts in (box(-hw + .15, -hd + .5, -hw + .98, hd - .15), box(hw - .98, -hd + .5, hw - .15, hd - .15), box(-hw + .15, hd - .98, hw - .15, hd - .15)):
            entablature(pts, zp + hc, hc, "ionic")
        for sx in (-1, 1):
            inst(civic.AKRO, sx * (hw - .58), -hd + .5, zp + hc + hc * .27, 0, .55)
            inst(civic.AKRO, sx * (hw - .58), hd - .58, zp + hc + hc * .27, 0, .55)
        # central sacrificial altar table (bomos) on a stepped base with volute wind-guards and glowing fire
        boxr("marble:#dad2bf", "marble:#e4dcc9", 0, .15, 4.2, 2.3, zp, zp + .20)
        boxr("marble:#e2dbc9", "marble:#e9e3d4", 0, .15, 3.7, 1.9, zp + .20, zp + .40)
        boxr("marble:#ece6d8", "marble:#f0ebdf", 0, .15, 3.2, 1.5, zp + .40, zp + 1.25)
        boxr("marble:#e2dbc9", "marble:#e9e3d4", 0, .15, 3.5, 1.75, zp + 1.25, zp + 1.40)
        for sx in (-1, 1): boxr("marble:#ece6d8", "marble:#f0ebdf", sx * 1.52, .15, .36, 1.7, zp + 1.40, zp + 1.88)
        cyl("dark:#3a302a", 0, .15, .62, zp + 1.40, zp + 1.48, 12)
        cyl("fire" if core.NIGHT else "paint:#b8431b", 0, .15, .45, zp + 1.45, zp + 1.58, 10)
        for sx in (-1, 1):
            inst(props.BRAZIER, sx * 2.85, -hd + 1.15, zp, 0, .95)
    land.take(rect(cx, cy, w + 2.0, d + 2.5, rot))

def tholos(cx, cy, z, rot=0):
    """A circular Ionic tholos in the south-eastern sanctuary court: 3-stepped marble krepis, 10 columns, circular cella with
    bronze doorway facing the altar court, conical tiled roof, and gilded bronze finial."""
    n_col = 10; r_col = 3.45; hc = 4.6; rc = .27
    with placed(cx, cy, rot):
        # 3-stepped circular marble krepis
        for k, (rad, zz) in enumerate(((4.55, z + .22), (4.2, z + .44), (3.85, z + .66))):
            cyl(MARBLE, 0, 0, rad, z, zz, 24)
        zs = z + .66
        # ring of 10 slender Ionic columns
        col_mesh = column("ionic", hc, rc)
        for i in range(n_col):
            a = 2 * math.pi * i / n_col
            inst(col_mesh, r_col * math.cos(a), r_col * math.sin(a), zs, a + math.pi / 2)
        # circular marble cella with a bronze-framed doorway facing local -x
        cyl(MARBLE, 0, 0, 2.05, zs, zs + hc, 20)
        boxr("marble:#e2dac8", "marble:#e2dac8", -2.02, 0, .22, 1.4, zs, zs + 3.1)
        boxr("dark:#241b14", "dark:#241b14", -2.08, 0, .1, 1.0, zs, zs + 2.85)
        boxr("bronze", "bronze", -2.11, -.24, .06, .46, zs + .02, zs + 2.83)
        boxr("bronze", "bronze", -2.11, .24, .06, .46, zs + .02, zs + 2.83)
        # circular entablature (architrave, frieze, projecting cornice)
        zt = zs + hc
        cyl("marble:#ece6d8", 0, 0, r_col + .38, zt, zt + .38, 24)
        cyl("marble:#e2dac8", 0, 0, r_col + .42, zt + .38, zt + .72, 24)
        cyl("marble:#f0ebdf", 0, 0, r_col + .68, zt + .72, zt + .92, 24)
        # conical terracotta tiled roof in 16 radial facets with raised hip ribs and a gilded bronze finial
        zr = zt + .92; peak = zr + 2.25; re = r_col + 1.05; nf = 16
        apex = (0, 0, peak)
        for i in range(nf):
            a0, a1 = 2 * math.pi * i / nf, 2 * math.pi * (i + 1) / nf
            p0 = (re * math.cos(a0), re * math.sin(a0), zr)
            p1 = (re * math.cos(a1), re * math.sin(a1), zr)
            face("tile:#c79f7c", [p0, p1, apex], [(0, 0), (1.7, 0), (.85, 4.8)], va=.25, vb=0.0)
            ridge(p0, apex, va=.25, key="tile:#c79f7c", r=.09)
        lathe("gold", 0, 0, [(.38, peak - .05), (.28, peak + .25), (.42, peak + .55), (.18, peak + .9), (.04, peak + 1.3)], 10, cap_top=True)
    land.take(rect(cx, cy, 10.5, 10.5))

def build():
    if not land.HILL: return
    g = random.Random(41); z = land.TOP; SU = land.SUMMIT
    land.paint("earth", SU, .85, 2.0)
    # worn sanctuary paving across the entire summit (to the circuit walls), broken organically by earth, rock, and grove soil
    land.paint("pave", SU, .85, 2.5)
    land.paint("gravel", SU, .45, 3.0)
    subm = land.win(-54, 100, 64, 168, 0, land.MRES, land.NM)
    xm, ym = land.XM[subm], land.YM[subm]
    in_su = np.array([core.inpoly(float(x), float(y), SU) for x, y in zip(xm.ravel(), ym.ravel())]).reshape(xm.shape)
    in_court = (xm > -10.5) & (xm < 44.5) & (ym > 118.5) & (ym < 150.0)
    n_earth = land.fbm(xm, ym, 11.0, 4, seed=41) + .5 * land.fbm(xm, ym, 3.8, 3, seed=73)
    n_rock = land.fbm(xm, ym, 8.5, 4, seed=97)
    grove = np.maximum.reduce([
        np.exp(-(((xm - 49.0) / 6.5) ** 2 + ((ym - 142.0) / 9.0) ** 2)),
        np.exp(-(((xm - 16.0) / 24.0) ** 2 + ((ym - 154.5) / 5.0) ** 2)),
        np.exp(-(((xm + 30.0) / 8.0) ** 2 + ((ym - 134.0) / 6.0) ** 2)),
    ]) * .85
    wear = np.clip((n_earth + grove - .05) * 1.8, 0, 1) * in_su * (~in_court)
    rock = np.clip((n_rock - .22) * 2.2, 0, 1) * in_su * (~in_court)
    land.COV["earth"][subm] = np.maximum(land.COV["earth"][subm], wear)
    land.COV["lush"][subm] = np.maximum(land.COV["lush"][subm], np.clip(grove * .55, 0, .5) * in_su * (~in_court))
    land.COV["pave"][subm] = np.clip(land.COV["pave"][subm] * (1.0 - wear * .85 - rock), 0, 1)
    land.COV["rock"][subm] = np.maximum(land.COV["rock"][subm], rock)
    broad_stair(); west_stair(); propylon()

    # formal dressed stone flagging on the Sacred Way, the West Library Walk, and the Eastern Altar Court
    cap("paving:#d2c8b0", box(-3.5, 104.0, 3.5, 119.5), z + .03)                        # Sacred Way entry from propylon
    cap("paving:#cfc5ad", box(-45.5, 112.2, -3.4, 115.8), z + .025)                     # West path to library & postern
    cap("paving:#d6ccb6", box(-9.5, 119.0, 40.5, 125.4), z + .035)                      # Processional Sacred Way along south flank of temple
    cap(PAVE, box(22.5, 125.0, 44.5, 149.0), z + .04)                                   # Eastern Altar Court before the temple front
    # inlaid pale marble paths & border curbs linking the propylon, library, temple terrace, altar court, northern monuments, treasury, and tholos
    for bx in (box(-45.5, 114.3, -3.5, 114.8), box(-3.6, 104.0, -3.2, 119.2), box(3.2, 104.0, 3.6, 119.2),
               box(-9.5, 119.0, 40.5, 119.45), box(-9.5, 124.95, 23.0, 125.4),
               box(23.0, 137.0, 31.8, 138.0), box(35.5, 119.4, 36.5, 132.0),
               box(35.5, 120.2, 41.0, 121.1), box(-15.5, 137.0, -9.2, 137.8),
               box(-3.0, 149.2, 37.5, 149.8), box(23.5, 147.0, 24.3, 151.0)):
        cap("marble:#dfd7c4", bx, z + .046)
    for pts in (box(22.8, 148.7, 44.5, 149.05), box(44.2, 125.0, 44.55, 149.05), box(22.8, 125.0, 44.5, 125.35)):
        prism(MARBLE, MARBLE, pts, z, z + .14)

    # the main East-Facing Ionic peripteral temple on its stepped sanctuary terrace, well separated from the library
    zt_terr = temple_terrace(-9.6, 127.8, 23.6, 147.2, z, h=.36)
    civic.temple(7.0, 137.5, 90, 15.4, 30.5, 8.4, 6, 11, "ionic", zt_terr, peripteral=True, blend=0)
    great_altar(36.0, 137.5, z, rot=-90)
    tholos(45.0, 120.5, z, rot=-35)

    # Walled Sacred Olive Enclosure (Pandroseion) in the open terrace north of the library
    olive_enclosure(-29.5, 134.5, z)

    # Ornamental Hellenistic monuments along the northern and north-eastern terrace (aligned with the northern wall and in full sunlight):
    # 1. Circular Choragic Tripod Monument (on the pattern of Lysikrates) overlooking the northeast court
    choragic_monument(25.5, 151.0, z)
    # 2. Heroic Statuary Bathron (Monument of the Eponymous Heroes / Daochos Base) north of the Great Altar, aligned with the citadel wall
    statue_bathron(34.8, 151.2, z, rot=-12)
    # 3. Tall Hellenistic Pillar Monument (on the pattern of Eumenes II / Prusias at Delphi) on the east side of the Altar Court
    pillar_monument(44.0, 145.5, z, rot=-45)

    # bronze tripods and purification basins (perirrhanteria) flanking the propylon exit, the eastern temple pronaos, and the altar steps
    for sx in (-1, 1):
        inst(props.BASIN, sx * 3.1, 110.6, z, 0, 1.0)
    for sy in (-1, 1):
        inst(props.TRIPOD, 24.8, 137.5 + sy * 5.0, z, math.pi / 2, 1.1)
        inst(props.BASIN, 24.8, 137.5 + sy * 3.2, z, math.pi / 2, 1.0)
        inst(props.TRIPOD, 30.2, 137.5 + sy * 3.5, z, -math.pi / 2, 1.0)

    # the reshaped Library stoa at its fixed south-west door (-32, 114)
    civic.stoa(-44.5, 117.2, -21.5, 125.8, "s", 4.2, rooms=3.8, z=z, va=.35, blend=0)
    for k in range(3): inst(props.BENCH, -40.0 + k * 7.2, 115.8, z, 0)
    for x_b in (-4.0, 15.2, 31.2): inst(props.BENCH, x_b, 150.5, z, 0)
    inst(props.SUNDIAL, -19.5, 116.2, z, 0, 1.15)

    # Doric treasury (thesauros) along the southern Sacred Way with flanking tripods
    civic.temple(20.0, 111.2, 90, 6.2, 10.0, 4.1, 2, 4, "doric", z, peripteral=False, steps=2, blend=0)
    for sy in (-1, 1): inst(props.TRIPOD, 25.9, 111.2 + sy * 2.2, z, math.pi / 2, .95)

    # Colossal bronze Athena (Athena Promachos) in the open forecourt between the library and the temple, & equestrian monument
    inst(props.COLOSSUS, -13.0, 121.0, z, -math.pi * .75); land.take(rect(-13.0, 121.0, 5.5, 5.5))
    inst(props.EQUESTRIAN, 10.5, 115.8, z, -math.pi * .75); land.take(rect(10.5, 115.8, 3.0, 3.8))

    # sanctuary cistern wellhead
    inst(props.WELL, 33.5, 112.0, z, 0, 1.55)

    # votives: statues, stelai, and tripods along the Sacred Way, exedrae, herms by the library, and votive columns around the Altar Court
    for k in range(5):
        y = 109.5 + k * 1.35
        for sx in (-1, 1):
            if g.random() < .85 and not (111.2 < y < 116.8 and sx < 0):
                inst(g.choice((props.STATUE_M, props.STATUE_B, props.STELE, props.TRIPOD)), sx * (3.5 + g.uniform(0, .2)), y, z, math.pi / 2 * -sx)
    for k in range(11): inst(g.choice((props.STELE, props.HERM, props.STATUE_M)), -44 + k * 2.3, 111.2 + g.uniform(-.25, .25), z, 0)
    inst(props.EXEDRA, 2.5, 125.0, z, math.pi)
    inst(props.EXEDRA, 28.0, 125.0, z, math.pi)
    inst(props.EXEDRA, -20.5, 142.5, z, -math.pi * .25)
    for x, y in ((-5.5, 118.2), (5.5, 118.2), (11.5, 125.8), (19.5, 125.8),
                 (25.5, 128.0), (29.8, 147.8), (42.5, 130.0), (41.0, 147.8),
                 (45.5, 136.5), (-13.5, 131.5), (-13.5, 141.5), (-21.0, 131.5)):
        inst(g.choice((props.VOTIVE, props.STATUE_B, props.STATUE_M, props.TRIPOD, props.BASE)), x, y, z, g.uniform(0, 6.3))

    # sacred grove (alsos) of olives, cypresses, stone pines, and pomegranates framing the northern and eastern ramparts
    for x, y, kind in ((-41.0, 130.5, "olive"), (-9.5, 152.5, "cypress"),
                       (14.5, 154.5, "olive"), (30.5, 156.2, "cypress"), (43.5, 155.0, "olive"),
                       (51.5, 149.5, "cypress"), (50.0, 139.5, "olive"), (53.5, 143.0, "cypress"),
                       (53.0, 131.0, "olive"), (53.5, 117.5, "cypress")):
        houses.TREES.append((x, y, z, kind))
    GROVE.extend([
        (-36.5, 135.5, z, "cypress", .95), (-23.5, 145.5, z, "olive", .98), (-15.5, 148.5, z, "pomegranate", .95),
        (-11.5, 151.0, z, "olive", 1.0), (-4.0, 152.5, z, "stonepine", 1.05), (3.0, 153.2, z, "olive", 1.05),
        (9.5, 153.8, z, "stonepine", 1.02), (18.5, 155.2, z, "cypress", .98), (21.5, 155.8, z, "pomegranate", .95),
        (39.8, 155.8, z, "olive", .95), (42.5, 156.8, z, "cypress", 1.0),
        (47.5, 151.5, z, "pomegranate", .95), (49.0, 145.5, z, "olive", .95), (49.0, 134.5, z, "pomegranate", .92),
    ])
    land.take(SU)
