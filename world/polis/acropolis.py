"""The acropolis: the broad stair up from the town, the propylon at its head, and on the summit a sanctuary on the pattern of
Priene's and Pergamon's: an Ionic temple with its monumental stepped altar to the south-east, a circular tholos in the
eastern court, stoas along the precinct's edges (the library's rooms behind one of them, as at Pergamon), a treasury,
a colossal bronze Athena, bronze tripods, purification basins, exedrae, and votives along the paved Sacred Way."""
import math, random
import numpy as np
from . import core, land, arch, props, houses, civic
from .core import S, face, wall, walls, cap, prism, boxr, box, rect, grow, inst, lerp, placed, cyl, lathe, beam, bar
from .arch import colonnade, entablature, gable, panel, column, ridge, tiles

STONE = civic.STONE; STEPK = "marble:#d9d2c0"; MARBLE = "marble:#e8e1d0"; PAVE = "paving:#dcd3be"

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

def great_altar(cx, cy, z):
    """A Pergamene-style monumental stepped altar before the temple: broad south steps, sculpted podium, U-shaped Ionic
    colonnade framing the upper sacrificial court, central volute altar with fire, and flanking bronze braziers."""
    w, d = 8.4, 5.4; hw, hd = w / 2, d / 2; zp = z + .96
    with placed(cx, cy, 0):
        # 4 broad marble steps along the south front rising to the altar platform
        for i in range(4):
            y0 = -hd - .9 + i * .32; zz = z + (i + 1) * .24
            prism("marble:#e0d8c6", STEPK, box(-hw + .3, y0, hw - .3, hd), z, zz)
        # raised podium and U-shaped wings (west, north, east)
        prism("marble:#e8e1d0", "paving:#e4dcc9", box(-hw, -hd + .4, hw, hd), z, zp)
        # dark/painted frieze band on the podium's east, west, and north flanks
        for x0, y0, x1, y1 in ((-hw - .03, -hd + .5, -hw + .02, hd + .03), (hw - .02, -hd + .5, hw + .03, hd + .03), (-hw - .03, hd - .02, hw + .03, hd + .03)):
            prism("frieze", None, box(x0, y0, x1, y1), z + .38, z + .82)
        # U-shaped Ionic colonnade & parapet around the upper court
        hc = 2.35; r = .17
        colonnade((-hw + .55, -hd + .8), (-hw + .55, hd - .55), 4, "ionic", hc, r, zp, rot=0)
        colonnade((hw - .55, -hd + .8), (hw - .55, hd - .55), 4, "ionic", hc, r, zp, rot=0)
        colonnade((-hw + .55, hd - .55), (hw - .55, hd - .55), 6, "ionic", hc, r, zp, ends=False, rot=0)
        # U-shaped marble entablature and cornice over the wings
        for pts in (box(-hw + .15, -hd + .5, -hw + .95, hd - .15), box(hw - .95, -hd + .5, hw - .15, hd - .15), box(-hw + .15, hd - .95, hw - .15, hd - .15)):
            entablature(pts, zp + hc, hc, "ionic")
        for sx in (-1, 1):
            inst(civic.AKRO, sx * (hw - .55), -hd + .5, zp + hc + hc * .27, 0, .55)
        # central sacrificial altar table with wind-guards and glowing fire
        boxr("marble:#e2dbc9", "marble:#e9e3d4", 0, .2, 3.6, 1.9, zp, zp + .22)
        boxr("marble:#ece6d8", "marble:#f0ebdf", 0, .2, 3.1, 1.45, zp + .22, zp + 1.05)
        boxr("marble:#e2dbc9", "marble:#e9e3d4", 0, .2, 3.35, 1.65, zp + 1.05, zp + 1.18)
        for sx in (-1, 1): boxr("marble:#ece6d8", "marble:#f0ebdf", sx * 1.45, .2, .32, 1.6, zp + 1.18, zp + 1.62)
        cyl("dark:#3a302a", 0, .2, .52, zp + 1.18, zp + 1.24, 12)
        cyl("fire" if core.NIGHT else "paint:#a83e19", 0, .2, .36, zp + 1.22, zp + 1.30, 10)
        for sx in (-1, 1):
            inst(props.BRAZIER, sx * 2.55, -hd + 1.1, zp, 0, .9)
    land.take(rect(cx, cy, w + 1.5, d + 2.0))

def tholos(cx, cy, z):
    """A circular Ionic tholos in the eastern sanctuary court: 3-stepped marble krepis, 10 columns, circular cella with
    bronze doorway facing the temple, conical tiled roof, and gilded bronze finial."""
    n_col = 10; r_col = 3.45; hc = 4.6; rc = .27
    with placed(cx, cy, 0):
        # 3-stepped circular marble krepis
        for k, (rad, zz) in enumerate(((4.55, z + .22), (4.2, z + .44), (3.85, z + .66))):
            cyl(MARBLE, 0, 0, rad, z, zz, 24)
        zs = z + .66
        # ring of 10 slender Ionic columns
        col_mesh = column("ionic", hc, rc)
        for i in range(n_col):
            a = 2 * math.pi * i / n_col
            inst(col_mesh, r_col * math.cos(a), r_col * math.sin(a), zs, a + math.pi / 2)
        # circular marble cella with a bronze-framed doorway facing west (-x) toward the temple
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
    subm = land.win(-54, 100, 56, 172, 0, land.MRES, land.NM)
    xm, ym = land.XM[subm], land.YM[subm]
    in_su = np.array([core.inpoly(float(x), float(y), SU) for x, y in zip(xm.ravel(), ym.ravel())]).reshape(xm.shape)
    in_court = (np.abs(xm) < 11.8) & (ym > 114.5) & (ym < 158.5)
    n_earth = land.fbm(xm, ym, 11.0, 4, seed=41) + .5 * land.fbm(xm, ym, 3.8, 3, seed=73)
    n_rock = land.fbm(xm, ym, 8.5, 4, seed=97)
    grove = np.maximum(np.exp(-(((xm - 43.5) / 5.5) ** 2 + ((ym - 157.5) / 5.5) ** 2)),
                       np.exp(-(((xm + 33.0) / 5.0) ** 2 + ((ym - 153.0) / 5.0) ** 2))) * .65
    wear = np.clip((n_earth + grove - .05) * 1.8, 0, 1) * in_su * (~in_court)
    rock = np.clip((n_rock - .22) * 2.2, 0, 1) * in_su * (~in_court)
    land.COV["earth"][subm] = np.maximum(land.COV["earth"][subm], wear)
    land.COV["pave"][subm] = np.clip(land.COV["pave"][subm] * (1.0 - wear * .85 - rock), 0, 1)
    land.COV["rock"][subm] = np.maximum(land.COV["rock"][subm], rock)
    broad_stair(); west_stair(); propylon()

    # formal dressed stone flagging only on the Sacred Way and central Temple & Altar court, plus paved stone walkways
    cap("paving:#d2c8b0", box(-3.4, 104.0, 3.4, 115.0), z + .03)                        # Sacred Way from propylon
    cap(PAVE, box(-11.5, 115.0, 11.5, 158.0), z + .04)                                    # main temple & altar court
    cap("paving:#cfc5ad", box(-45.5, 112.2, -3.4, 115.8), z + .025)                       # west path to library & postern
    # inlaid marble stone paths & border curbs linking the temple court to the treasury and tholos
    for bx in (box(-11.5, 124.8, 11.5, 125.25), box(-11.5, 114.3, 28.0, 114.8), box(11.5, 142.5, 29.5, 143.5),
               box(-3.6, 104.0, -3.2, 114.5), box(3.2, 104.0, 3.6, 114.5)):
        cap("marble:#dfd7c4", bx, z + .046)
    for pts in (box(-11.7, 116.5, -11.4, 158.0), box(-11.7, 157.8, 11.5, 158.1), box(11.4, 116.5, 11.7, 158.0)):
        prism(MARBLE, MARBLE, pts, z, z + .14)

    # the main Ionic peripteral temple aligned with the stairway and propylon, its stepped altar, and the circular Tholos
    civic.temple(0.0, 140.5, 0, 15.4, 30.5, 8.4, 6, 11, "ionic", z, peripteral=True, blend=0)
    great_altar(0.0, 119.6, z)
    tholos(34.0, 143.0, z)

    # bronze tripods and purification basins flanking the temple pronaos and propylon exit
    for sx in (-1, 1):
        inst(props.BASIN, sx * 3.1, 110.6, z, 0, 1.0)
        inst(props.TRIPOD, sx * 5.2, 124.2, z, 0, 1.05)
        inst(props.BASIN, sx * 3.6, 124.5, z, 0, .95)

    # stoas on the west, south-west (trimmed to give the temple breathing room), and a shorter north stoa behind the temple
    civic.stoa(-45.5, 117.6, -17.5, 128.2, "s", 4.6, rooms=4.2, z=z, va=.35, blend=0)
    civic.stoa(-49.6, 129.4, -40.4, 157.5, "e", 4.2, z=z, va=.5, blend=0)
    civic.stoa(-18.0, 162.2, 20.0, 168.6, "s", 4.6, aisles=1, z=z, va=.45, blend=0)
    for k in range(4): inst(props.BENCH, -41.5 + k * 6.8, 115.9, z, 0)
    for k in range(4): inst(props.BENCH, -13.5 + k * 9.0, 160.8, z, 0)
    for k in range(3): inst(g.choice((props.STATUE_M, props.STATUE_B)), -9.0 + k * 9.0, 161.0, z, 0)

    # treasury east of the forecourt with flanking tripods, plus the colossal bronze Athena & equestrian monument
    civic.temple(34.0, 115.0, -90, 6.4, 10.5, 4.2, 2, 4, "doric", z, peripteral=False, steps=2, blend=0)
    for sy in (-1, 1): inst(props.TRIPOD, 27.6, 115.0 + sy * 2.3, z, -math.pi / 2, .95)
    inst(props.COLOSSUS, -13.5, 122.8, z, math.pi); land.take(rect(-13.5, 122.8, 5.5, 5.5))
    inst(props.EQUESTRIAN, 16.5, 118.2, z, -math.pi * .75); land.take(rect(16.5, 118.2, 3.0, 3.8))

    # cistern wellhead
    inst(props.WELL, 40.5, 121.0, z, 0, 1.6)

    # votives: statues, stelai, and tripods along the Sacred Way, exedrae, herms by the library, votive columns round the temple
    for k in range(6):
        y = 109.5 + k * 1.3
        for sx in (-1, 1):
            if g.random() < .85 and not (111.5 < y < 116.5 and sx < 0):
                inst(g.choice((props.STATUE_M, props.STATUE_B, props.STELE, props.TRIPOD)), sx * (3.4 + g.uniform(0, .25)), y, z, math.pi / 2 * -sx)
    for k in range(12): inst(g.choice((props.STELE, props.HERM, props.STATUE_M)), -44 + k * 2.4, 111.2 + g.uniform(-.25, .25), z, 0)
    inst(props.EXEDRA, 19.5, 128.0, z, math.pi)
    inst(props.EXEDRA, -15.5, 146.0, z, -math.pi / 2)
    inst(props.EXEDRA, 28.0, 152.5, z, -math.pi * .75)
    for x, y in ((12.5, 132), (12.5, 142), (12.5, 152), (39.5, 130.0), (39.5, 149.0), (-11.5, 132), (-11.5, 142), (-11.5, 152), (-26, 138), (27.5, 135.5)):
        inst(g.choice((props.STATUE_B, props.STATUE_M, props.VOTIVE, props.TRIPOD, props.BASE)), x, y, z, g.uniform(0, 6.3))

    for x, y, kind in ((43.5, 156.5, "olive"), (45.5, 159.0, "cypress"), (26.0, 154.0, "cypress"), (-33.5, 152.5, "olive"),
                       (-35.5, 154.5, "cypress"), (46.0, 135.0, "cypress"), (-24.0, 155.5, "olive"), (40.0, 162.5, "cypress"),
                       (46.0, 145.0, "olive"), (-18.5, 132.5, "cypress"), (25.0, 108.5, "cypress")):
        houses.TREES.append((x, y, z, kind))
    land.take(SU)
