"""Outside the walls: the farm with its granary and tower, the winery among terraced vines, the fishery and the harbour mole,
the potters' quarter, two schools in their groves (the libraries), tombs along the roads out of the gates, and small tilled
plots divided by dry-stone walls. What grows on all this is planted afterwards by plants.py from the lists gathered here."""
import math, random
from . import core, land, arch, props, houses, civic
from .core import S, face, mesh, wall, walls, cap, prism, boxr, box, rect, grow, inst, lerp, placed, in_view, centre, Scatter
from .arch import shed, gable, hip, door, panel, colonnade

GROVES = []        # (polygon, kind, spacing): orchards and sacred groves for plants.py
VINEYARDS = []     # (polygon, angle)
KEEP_CLEAR = []    # polygons nothing wild grows in
STREAMS = []       # (centerline_pts, gravel_bed_poly) for plants.py
PL = S["places"]

def drystone(pts, closed=False, h=.95, gaps=(), keep_clear=False):
    """A dry-stone field wall along a line, following the ground."""
    P = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / 2.5)); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = -uy * .32, ux * .32
        for k in range(n):
            p, q = (a[0] + ux * L * k / n, a[1] + uy * L * k / n), (a[0] + ux * L * (k + 1) / n, a[1] + uy * L * (k + 1) / n); m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if land.road_dist(*m) < 1.2 or any(math.hypot(m[0] - gx, m[1] - gy) < gr for gx, gy, gr in gaps) or not land.free(*m): continue
            if keep_clear and any(core.inpoly(*m, K) for K in KEEP_CLEAR): continue
            seg = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]; z = land.zt(*m)
            prism("drystone", "drystone", seg, land.zmin(seg) - .3, z + h + .12 * math.sin(k * 1.7 + a[0]))
def compound(R, gate, h=1.9, key="rubble:#b9ad94"):
    """A yard wall round an estate, with a gap for its gate at `gate` (x, y)."""
    P = box(*R)
    for a, b in zip(P, P[1:] + P[:1]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; n = max(1, int(L / 3))
        for k in range(n):
            p, q = (a[0] + ux * L * k / n, a[1] + uy * L * k / n), (a[0] + ux * L * (k + 1) / n, a[1] + uy * L * (k + 1) / n); m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if math.hypot(m[0] - gate[0], m[1] - gate[1]) < 2.6: continue
            seg = [(p[0] + uy * .3, p[1] - ux * .3), (q[0] + uy * .3, q[1] - ux * .3), (q[0] - uy * .3, q[1] + ux * .3), (p[0] - uy * .3, p[1] + ux * .3)]
            prism(key, "paving:#c4b89e", seg, land.zmin(seg) - .4, land.zt(*m) + h)
    for s in (-1, 1):
        d = (0, 1) if abs(gate[0] - R[0]) < .5 or abs(gate[0] - R[2]) < .5 else (1, 0)
        boxr(key, "paving:#c4b89e", gate[0] + d[0] * s * 2.4, gate[1] + d[1] * s * 2.4, .9, .9, land.zt(*gate) - .4, land.zt(*gate) + h + .5)
def pyrgos(x0, y0, x1, y1, h=10.5, z=None, va=.4):
    """A farm tower in squared stone: store below, refuge above, a tiled roof. Such towers stood on Hellenistic farms all over Greece."""
    R = box(x0, y0, x1, y1); z0 = land.pad(R, z, blend=1.0); land.take(R, .5); kw = dict(va=va, vb=z0)
    walls("ashlar:#cdc1a6", R, z0 - 1, z0 + h, zb=0, **kw); hip(x0, y0, x1, y1, z0 + h, 1.2, va, ov=.45)
    door(*houses.EDGE["s"](x0, y0, x1, y1), (x1 - x0) / 2, z0, 1.1, 2.1)
    for sd in "nsew":
        p, q = houses.EDGE[sd](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1])
        panel("dark", p, q, L / 2, .7, z0 + h - 2.2, z0 + h - 1.2, .04); panel("dark", p, q, L / 2, .14, z0 + 4.5, z0 + 5.5, .04)
    return z0

def granary(g):
    """The granary's farm: the long grain store on its ventilated floor, the farmhouse and its tower, the threshing floor."""
    dx, dy = PL["granary"]["door"]; R = (dx, -31.0, dx + 46, 31.0); z = land.zt(dx + 12, 0)
    yard = box(*R); land.paint("earth", yard, 1.0, 2.5); KEEP_CLEAR.append(grow(yard, 2)); compound(R, (dx, dy))
    x0 = dx + 9; z0 = civic.hall(x0, 9.0, x0 + 27, 20.0, 5.6, "x", wk="plaster:#e6dcc4", door_side="s", windows=False, va=.55, blend=2.0)
    for k in range(10):                                                                   # buttress piers, and the vents of the raised floor between them
        xx = x0 + 1.4 + k * 2.7; boxr("rubble:#b9ad94", "paving:#c4b89e", xx, 8.75, .8, .6, z0 - .6, z0 + 4.2)
        if k < 9: panel("dark", (x0, 9.0), (x0 + 27, 9.0), 2.75 + k * 2.7, .9, z0 + .25, z0 + .55, .04)
    walls("rubble:#b9ad94", box(x0 - .15, 8.85, x0 + 27.15, 20.15), z0 - .8, z0 + 1.0)
    houses.house(dx + 6, -27.0, dx + 22, -11.5, g, ("n",), door_side="n"); pyrgos(dx + 23.5, -24.0, dx + 30.5, -17.0)
    tx, ty = dx + 33, -3.5; land.pad(rect(tx, ty, 14, 14), None, blend=3)                # the threshing floor: a paved circle open to the wind
    zt_ = land.zt(tx, ty); N = 28
    face("paving:#cdbf9c", [(tx + 6.3 * math.cos(2 * math.pi * i / N), ty + 6.3 * math.sin(2 * math.pi * i / N), zt_ + .06) for i in range(N)])
    for i in range(N):
        a0, a1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1) / N
        prism("rubble:#b9ad94", "rubble:#b9ad94", [(tx + 6.3 * math.cos(a0), ty + 6.3 * math.sin(a0)), (tx + 6.8 * math.cos(a0), ty + 6.8 * math.sin(a0)), (tx + 6.8 * math.cos(a1), ty + 6.8 * math.sin(a1)), (tx + 6.3 * math.cos(a1), ty + 6.3 * math.sin(a1))], zt_ - .3, zt_ + .3)
    land.take(rect(tx, ty, 14, 14)); inst(props.HAY, tx - 1, ty + 1, zt_, 0, .45)
    for k in range(12): inst(props.SHEAF, tx + 5.4 * math.cos(k * .5), ty + 5.4 * math.sin(k * .5), zt_ + .06, k)
    inst(props.GRAIN_HEAP, tx + 2.1, ty - .8, zt_ + .06, .4); inst(props.CHAFF_HEAP, tx - 1.4, ty - 2.2, zt_ + .06, 1.2)
    for m, hx, hy in ((props.GRAIN_HEAP, tx + 8.3, ty + 2.2), (props.CHAFF_HEAP, tx + 6.9, ty - 5.3)):
        inst(m, hx, hy, land.zt(hx, hy), g.uniform(0, 6)); land.take_disc(hx, hy, 2.2)
    for x, y in ((dx + 39, 17), (dx + 41, 9)): inst(props.HAY, x, y, land.zt(x, y), g.uniform(0, 6), g.uniform(.85, 1.05)); land.take(rect(x, y, 6, 6))
    # olive mill under an open shed, lever press, pithoi, and oil cart in the north-west yard
    mill_pad = box(dx + 1.2, 9.5, dx + 8.0, 19.5); z_mill = land.pad(mill_pad, None, blend=1.5)
    mx0, my0, mx1, my1 = dx + 1.3, 14.8, dx + 6.3, 18.8
    for x in (mx0 + .25, mx1 - .25):
        for y in (my0 + .25, my1 - .25): inst(arch.column("post", 3.2, .09, "wood:#6b5032"), x, y, z_mill)
    shed(mx0, my0, mx1, my1, z_mill + 3.2, .8, "n", key="tile:#a8674a", ov=.25)
    inst(props.OLIVE_MILL, dx + 4.2, 16.0, z_mill, .25); inst(props.PRESS, dx + 3.8, 11.2, z_mill, 0)
    for k in range(6):
        px, py = dx + 1.8 + (k % 3) * 1.35, 7.7 + (k // 3) * 1.3
        inst(props.PITHOS, px, py, land.zt(px, py), g.uniform(0, 6)); land.take_disc(px, py, .8)
    land.take(mill_pad)
    # loaded carts (1.3x) replacing the old empty carts
    for m, cx, cy, cr in ((props.CART_AMPH, dx + 6.8, 5.4, .45), (props.CART_SACKS, dx + 22.0, 4.4, 2.85), (props.CART_HAY, dx + 34.5, 5.6, .25)):
        inst(m, cx, cy, land.zt(cx, cy), cr, 1.3); land.take_disc(cx, cy, 2.8)
    # sacks, stacked baskets, bread oven, and woodpile
    for k in range(14): inst(props.SACK, dx + 12 + (k % 5) * .62, 7.6 + (k // 5) * .6, land.zt(dx + 12, 7.6), g.uniform(0, 6))
    for k in range(20):
        sx, sy = dx + 25.0 + (k % 5) * .62, 7.5 + ((k // 5) % 2) * .62
        inst(props.SACK, sx, sy, land.zt(dx + 26.2, 7.8) + (k // 10) * .50, g.uniform(0, 6))
    land.take(box(dx + 24.5, 7.0, dx + 28.2, 8.6))
    for k in range(10):
        bx = dx + 17.0 + (k % 3) * .72; by = 7.5 + ((k // 3) % 2) * .70; bz = land.zt(dx + 17.7, 7.8) + (k // 6) * .36
        inst(props.BASKET, bx, by, bz, g.uniform(0, 6), 1.15)
    land.take(box(dx + 16.5, 7.0, dx + 19.0, 8.7))
    inst(props.OVEN, dx + 7.5, -5.2, land.zt(dx + 7.5, -5.2), 0); land.take_disc(dx + 7.5, -5.2, 1.4)
    inst(props.WOODPILE, dx + 3.5, -6.0, land.zt(dx + 3.5, -6.0), .2); land.take_disc(dx + 3.5, -6.0, 1.8)
    # pergola against the south wall of the farmhouse
    from . import plants
    px0, px1, py0, py1 = dx + 8.5, dx + 15.5, -30.4, -27.1; z_perg = land.zt((px0 + px1) / 2, (py0 + py1) / 2) + 2.4
    for px in (px0 + .3, (px0 + px1) / 2, px1 - .3):
        for py in (py0 + .15, py1 - .15): core.beam("wood:#6b5032", (px, py, land.zt(px, py) - .1), (px, py, z_perg), .085, 6)
    for py in (py0 + .15, py1 - .15): core.beam("wood:#6b5032", (px0, py, z_perg), (px1, py, z_perg), .08, 6)
    for k in range(7):
        px = px0 + (px1 - px0) * k / 6; core.beam("wood:#6b5032", (px, py0 - .1, z_perg + .06), (px, py1 + .1, z_perg + .06), .055, 6)
    for py in (py0 + .6, (py0 + py1) / 2, py1 - .6): core.beam("wood:#7d5d3c", (px0 - .1, py, z_perg + .12), (px1 + .1, py, z_perg + .12), .04, 5)
    for px in (px0 + .3, px1 - .3): core.beam("bark:#5c4a38", (px + .12, py0 + .15, land.zt(px, py0) - .1), (px + .06, py0 + .25, z_perg + .15), .05, 5)
    with core.Part("pergola_vines") as pv: plants.cards("leaf:#62803a", [(0, 0, 0, 3.5, 2.0, .32)], 600, .24, g, inner=.15, up=.5)
    inst(pv.mesh, (px0 + px1) / 2, (py0 + py1) / 2, z_perg + .22, 0); land.take(box(px0 - .2, py0 - .2, px1 + .2, py1 + .2))
    # empty animal pen, trough, and manure heap in the south-east part of the yard
    pen = box(dx + 33.0, -21.5, dx + 41.0, -15.5); z_pen = land.pad(pen, None, blend=1.5); land.paint("earth", pen, 1.0, 1.5)
    drystone(pen, closed=True, h=1.0, gaps=[(dx + 37.0, -21.5, 1.3)])
    for px in (dx + 33.4, dx + 37.0, dx + 40.6): inst(arch.column("post", 2.2, .085, "wood:#6b5032"), px, -17.6, z_pen)
    shed(dx + 33.0, -17.7, dx + 41.0, -15.3, z_pen + 2.2, .55, "s", key="tile:#a8674a", ov=.25)
    inst(props.TROUGH, dx + 38.0, -19.5, z_pen, .15); land.take(pen, .5)
    inst(props.MANURE_HEAP, dx + 43.3, -17.2, land.zt(dx + 43.3, -17.2), .4); land.take_disc(dx + 43.3, -17.2, 2.3)
    props.jars(dx + 25, -9, None, 9, 1.6, g, (props.PITHOS,), check=False); inst(props.WELL, dx + 17, -5, land.zt(dx + 17, -5), 0, 1.3)
    # horizontal terracotta beehives stacked in two rows on a rubble wall
    zh = land.zt(dx + 39.0, -26.5)
    boxr("rubble:#b9ad94", "paving:#c4b89e", dx + 39.0, -26.5, 4.0, .7, zh - .3, zh + .5)
    boxr("wood:#7d5d3c", "wood:#7d5d3c", dx + 39.0, -26.5, 3.3, .62, zh + .80, zh + .85)
    for row, zz in enumerate((zh + .50, zh + .85)):
        for k in range(6): inst(props.HIVE, dx + 37.62 + k * .55, -26.5, zz, 0)
    land.take(box(dx + 36.8, -27.2, dx + 41.2, -25.8))
    land.take(yard)
    return R

def winery(g):
    """The winery: the press-house and its yard of sunk jars, a treading floor, the lever press under a shed; vines on terraces."""
    dx, dy = PL["winery"]["door"]; R = (dx - 42, -26.0, dx, 28.0); yard = box(*R); land.paint("earth", yard, 1.0, 2.5); KEEP_CLEAR.append(grow(yard, 2)); compound(R, (dx, dy))
    rg = random.Random(66)
    z0 = civic.hall(dx - 33, 6.0, dx - 11, 17.0, 4.6, "x", wk="plaster:#e9dfc8", door_side="s", windows=False, va=.3, blend=2.0)
    houses.house(dx - 38, -23.0, dx - 22, -8.0, g, ("n", "e"), door_side="e")
    px, py = dx - 9, -15.5; zp = land.pad(rect(px, py, 11, 9), None, blend=2)             # the press under its open shed
    inst(props.PRESS, px - 1, py, zp, 0)
    for x, y in ((px - 5, py - 3.6), (px + 5, py - 3.6), (px - 5, py + 3.6), (px + 5, py + 3.6)): inst(arch.column("post", 3.0, .1, "wood:#6b5032"), x, y, zp)
    gable(px - 5.3, py - 3.9, px + 5.3, py + 3.9, zp + 3.0, 1.0, "x", .6, key="tile:#a8674a", ov=.3)
    tx, ty = dx - 8, 9.5; zt_ = land.zt(tx, ty)                                           # the treading floor, its spout into a sunk vat
    boxr("rubble:#c2b69a", "paving:#cfc5ac", tx, ty, 4.2, 3.4, zt_ - .3, zt_ + .55); boxr("flat:#4b2a33", "flat:#4b2a33", tx, ty, 3.4, 2.6, zt_ + .5, zt_ + .58)
    inst(props.PITHOS, tx + 2.9, ty, zt_ - .7)
    z_pith = land.zt(dx - 31, -3) - .75
    for i in range(4):                                                                    # the pitheon: store jars sunk to their shoulders, with stone lids
        for j in range(5):
            jx, jy = dx - 31 + i * 1.7, -3.5 + j * 1.6
            inst(props.PITHOS, jx, jy, z_pith, g.uniform(0, 6))
            inst(props.PITHOS_LID, jx, jy, z_pith + 1.375, rg.uniform(0, 6))
    props.jar_rows(dx - 20, 2.0, dx - 14.5, 4.4, land.zt(dx - 17, 3), g)
    # two rows of ~30 empty amphorae against the south wall of the press-house, west of the door
    props.jar_rows(dx - 30.8, 4.95, dx - 24.2, 5.65, None, rg, .46)
    # loaded amphora carts (1.3x): one near the treading floor, one just inside the gate south of the lane
    inst(props.CART_AMPH, dx - 6, 3, land.zt(dx - 6, 3), 2.95, 1.3); land.take_disc(dx - 6, 3, 2.8)
    cx2, cy2 = dx - 5.5, -4.8
    assert land.road_dist(cx2, cy2) > 3.5, f"winery gate cart too close to road at {(cx2, cy2)}"
    inst(props.CART_AMPH, cx2, cy2, land.zt(cx2, cy2), math.radians(-155), 1.3); land.take_disc(cx2, cy2, 2.8)
    inst(props.WOODPILE, dx - 39, 21, land.zt(dx - 39, 21), .3)
    # raisin drying ground in the open north-east yard: 4 x 3 straw mats (1.2 x 3.0 m) topped with black and white grapes
    dry_box = box(dx - 8.5, 13.5, dx - 1.3, 24.3)
    z_dry = land.pad(dry_box, None, blend=1.5)
    for col in range(4):
        for row in range(3):
            mx = dx - 7.8 + col * 1.6; my = 14.0 + row * 3.4 + 1.5
            boxr("straw", "straw", mx + .6, my, 1.2, 3.0, z_dry - .01, z_dry + .03)
            gkey = "flat:#9a7a2e" if (col, row) in ((0, 2), (2, 1), (3, 0)) else "flat:#4a2338"
            boxr(gkey, gkey, mx + .6, my, 1.0, 2.78, z_dry + .025, z_dry + .042)
    land.take(dry_box)
    # two clusters of eight harvest baskets with purple grape tops beside the treading floor
    for bx, by in ((dx - 9.8, 5.5), (dx - 8.7, 5.4), (dx - 7.6, 5.6), (dx - 6.6, 5.9),
                   (dx - 9.5, 6.6), (dx - 8.4, 6.5), (dx - 7.3, 6.7), (dx - 6.4, 6.9),
                   (dx - 3.6, 7.6), (dx - 2.5, 7.8), (dx - 3.4, 8.7), (dx - 2.3, 8.9),
                   (dx - 3.7, 9.8), (dx - 2.6, 10.0), (dx - 3.5, 10.9), (dx - 2.4, 11.1)):
        inst(props.BASKET_GRAPE, bx, by, land.zt(bx, by), rg.uniform(0, 6), rg.uniform(.95, 1.05))
    # two stacks of vine stakes against south-facing walls
    for sx, sy in ((dx - 26.5, -23.8), (dx - 15.0, 27.0)):
        inst(props.STAKES, sx, sy, land.zt(sx, sy), 0.0)
    # pitch hearth for lining jars: cauldron on three stones, scorched ground, and woodpile beside it
    hx, hy = dx - 12.8, -4.5; hz = land.zt(hx, hy)
    land.paint_disc("wet", hx, hy, 1.5)
    core.cyl("flat:#22201e", hx, hy, .75, hz - .02, hz + .018, 16, smooth=False)
    inst(props.CAULDRON, hx, hy, hz, .3, 1.1)
    inst(props.WOODPILE, hx - 2.3, hy - .8, land.zt(hx - 2.3, hy - .8), .25)
    # vine pergola over the ground between the house and the sunk jars, reaching east into sunlight
    from . import plants
    px0, px1, py0, py1 = dx - 28.0, dx - 19.5, -8.0, -4.0
    z_perg = land.zt((px0 + px1) / 2, (py0 + py1) / 2) + 2.4
    for px_ in (px0 + .3, lerp(px0 + .3, px1 - .3, 1 / 3), lerp(px0 + .3, px1 - .3, 2 / 3), px1 - .3):
        for py_ in (py0 + .15, py1 - .15):
            core.beam("wood:#6b5032", (px_, py_, land.zt(px_, py_) - .1), (px_, py_, z_perg), .085, 6)
    for py_ in (py0 + .15, py1 - .15):
        core.beam("wood:#6b5032", (px0, py_, z_perg), (px1, py_, z_perg), .08, 6)
    for k in range(8):
        px_ = px0 + (px1 - px0) * k / 7
        core.beam("wood:#6b5032", (px_, py0 - .1, z_perg + .06), (px_, py1 + .1, z_perg + .06), .055, 6)
    for py_ in (py0 + .65, lerp(py0 + .65, py1 - .65, 1 / 3), lerp(py0 + .65, py1 - .65, 2 / 3), py1 - .65):
        core.beam("wood:#7d5d3c", (px0 - .1, py_, z_perg + .12), (px1 + .1, py_, z_perg + .12), .04, 5)
    for px_ in (px0 + .3, px1 - .3):
        core.beam("bark:#5c4a38", (px_ + .12, py0 + .15, land.zt(px_, py0) - .1), (px_ + .06, py0 + .25, z_perg + .15), .05, 5)
    with core.Part("pergola_vines_winery") as pv:
        plants.cards("leaf:#62803a", [(0, 0, 0, 4.35, 2.2, .42)], 850, .25, rg, inner=.15, up=.5)
    inst(pv.mesh, (px0 + px1) / 2, (py0 + py1) / 2, z_perg + .28, 0)
    land.take(box(px0 - .2, py0 - .2, px1 + .2, py1 + .2))
    land.take(yard)
    for P, ang in ((box(dx - 80, -64, dx - 46, 44), 4), (box(dx - 42, 32, dx + 26, 52), 2), (box(dx - 40, -66, dx + 8, -32), -3), (box(dx + 6, -30, dx + 26, 26), 88), (box(dx - 78, 48, dx - 44, 100), 6)):
        Q = [p for p in P]
        VINEYARDS.append((Q, ang))
    # two vineyard watch huts at vineyard corners, >= 4 m from any road
    for hx, hy, hrot in ((dx + 23.5, 23.5, 0.0), (dx + 4.5, -35.0, math.radians(-15))):
        assert land.road_dist(hx, hy) > 4.0, f"watch hut too close to road at {(hx, hy)}"
        inst(props.WATCH_HUT, hx, hy, land.zt(hx, hy), hrot)
        land.take_disc(hx, hy, 2.4)
        KEEP_CLEAR.append(box(hx - 2.0, hy - 2.0, hx + 2.0, hy + 2.0))
    return R

def fishery(g):
    """The fishery: the shed and its salting vats, racks of drying fish, nets, boats on the sand; and the harbour's stone mole."""
    dx, dy = PL["fishery"]["door"]
    z0 = civic.hall(-25.0, -130.0, -7.0, -122.5, 3.4, "x", wk="plaster:#e4d9c0", door_side="n", windows=False, va=.7, blend=2.0)
    houses.house(-23.5, -112.0, -9.5, -99.5, g, ("e", "s"), door_side="e")
    land.paint("earth", box(-28, -130, 38, -100), 1.0, 3.0)
    for i in range(3):                                                                    # salting vats: stone tanks of brine sunk in the ground
        for j in range(2):
            cx, cy = 13.0 + i * 6.4, -110.0 + j * 5.6; zv = land.pad(rect(cx, cy, 6.0, 5.2), None, blend=1.5)
            walls("rubble:#c2b69a", rect(cx, cy, 5.4, 4.6), zv - .4, zv + .5); walls("rubble:#c2b69a", rect(cx, cy, 4.6, 3.8), zv - .4, zv + .5, inward=True)
            O, I = rect(cx, cy, 5.4, 4.6), rect(cx, cy, 4.6, 3.8)
            for (a, b), (c, d) in zip(zip(O, O[1:] + O[:1]), zip(I, I[1:] + I[:1])): face("paving:#cfc5ac", [(a[0], a[1], zv + .5), (b[0], b[1], zv + .5), (d[0], d[1], zv + .5), (c[0], c[1], zv + .5)])
            cap("pool:#5d7a74" if (i + j) % 3 else "pool:#7a6a58", I, zv + .3); land.take(rect(cx, cy, 6, 5.2))
    civic.hall(34.5, -113.5, 45.0, -105.5, 3.2, "y", wk="plaster:#e4d9c0", door_side="w", windows=False, va=.5, blend=2.0)        # the store for the filled jars
    props.jar_rows(26, -100.6, 33, -98.8, land.zt(29, -100), g)
    for k in range(6):
        x, y = -34 - k * 4.4, -121 + k * 1.2
        if land.free(x, y, 2): inst(props.RACK, x, y, land.zt(x, y), .25); land.take_disc(x, y, 2.4)
    for x, y, r in ((-2, -131.5, .2), (6, -132.5, -.3), (-40, -133, .5)):
        if land.sd_at(x, y) > 2: inst(props.NETS, x, y, land.zt(x, y), r); land.take_disc(x, y, 2.6)
    for x, y, r in ((-14, -137.5, 1.3), (-21, -138.6, 1.5), (-29, -139.5, 1.1), (30, -134.5, 1.9), (-52, -134.5, .9), (-60, -131, 1.2)):   # boats drawn up on the beach
        yy = y
        while land.sd_at(x, yy) < 2.5 and yy < y + 12: yy += .5
        inst(g.choice(props.BOATS), x, yy, land.zt(x, yy) + .05, r, tilt=(g.uniform(-.2, .2), 0)); land.take_disc(x, yy, 3.2)
    # boat under repair on the upper beach: 1.5x, level on short shore timbers, with timber stack, pitch cauldron, and wood chips
    bx, by, brot = 4.5, -124.0, .25; bz = land.zt(bx, by) + .28
    inst(props.BOAT, bx, by, bz, brot, 1.5)
    with placed(bx, by, math.degrees(brot), bz):
        for xx in (-3.0, -1.0, 1.0, 3.0):
            t = xx / 9.75 + .5; hw = 1.425 * math.sin(math.pi * min(1, t * 1.03)) ** .6 + .045
            for s in (-1, 1): core.beam("wood:#7a5a38", (xx, s * (hw + .45), -.45), (xx, s * (hw * .88), .65), .09, 6)
    inst(props.TIMBER, 5.5, -127.6, land.zt(5.5, -127.6), brot)
    inst(props.CAULDRON, 10.5, -125.0, land.zt(10.5, -125.0), .4)
    land.paint_disc("sand", 6.2, -125.5, 2.5)
    land.take_disc(bx, by, 5.5); land.take_disc(5.5, -127.6, 3.6); land.take_disc(10.5, -125.0, 1.5)
    # two sails spread on the sand to dry, cut into four rippled strips with visible seams
    def _dry_sail(sx, sy, srot, key):
        ca, sa = math.cos(srot), math.sin(srot)
        ys = [-3.5 + j * 1.75 for j in range(5)]
        def pt(lx, ly, dz): wx, wy = sx + ca * lx - sa * ly, sy + sa * lx + ca * ly; return (wx, wy, land.zt(wx, wy) + dz)
        for i in range(4):
            x0, x1 = -2.45 + i * 1.24, -2.45 + i * 1.24 + 1.16
            xm = (x0 + x1) * .5; h_edge = .04 + .03 * (i % 2); h_mid = .11 + .05 * (i % 2)
            for j in range(4):
                for xa, xb, ha, hb in ((x0, xm, h_edge, h_mid), (xm, x1, h_mid, h_edge)):
                    p00 = pt(xa, ys[j], ha); p10 = pt(xb, ys[j], hb); p11 = pt(xb, ys[j + 1], hb); p01 = pt(xa, ys[j + 1], ha)
                    face(key, [p00, p10, p11, p01], [(xa + 2.5, ys[j] + 3.5), (xb + 2.5, ys[j] + 3.5), (xb + 2.5, ys[j + 1] + 3.5), (xa + 2.5, ys[j + 1] + 3.5)], va=i * .12)
        land.take_disc(sx, sy, 4.5)
    _dry_sail(25.0, -126.5, .15, "cloth:#d9ceb4"); _dry_sail(39.0, -127.0, -.18, "cloth:#a9553c")
    # the mole: a breakwater of squared blocks run out from the beach and turned along the shore, the harbour in its lee
    M = [(18.0, -136.0), (20.0, -156.0), (4.0, -168.0)]
    for a, b in zip(M, M[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; n = max(1, int(L / 3))
        for k in range(n):
            p, q = (a[0] + ux * L * k / n, a[1] + uy * L * k / n), (a[0] + ux * L * (k + 1) / n, a[1] + uy * L * (k + 1) / n)
            seg = [(p[0] + uy * 2.2, p[1] - ux * 2.2), (q[0] + uy * 2.2, q[1] - ux * 2.2), (q[0] - uy * 2.2, q[1] + ux * 2.2), (p[0] - uy * 2.2, p[1] + ux * 2.2)]
            prism("ashlar:#bdb39c", "paving:#c2b9a4", seg, -6, 1.15 + .04 * (k % 3), zb=0, vb=.2)
            if k % 2 == 0: boxr("ashlar:#bdb39c", "paving:#c2b9a4", p[0] - uy * 1.6, p[1] + ux * 1.6, .5, .5, 1.1, 1.75)
    prism("ashlar:#bdb39c", "paving:#c2b9a4", [(M[1][0] + 2.6 * math.cos(k * math.pi / 5), M[1][1] + 2.6 * math.sin(k * math.pi / 5)) for k in range(10)], -6, 1.2, zb=0, vb=.2)
    ROCKS.append((M, 3.4)); inst(props.SHIP, 6.5, -151.5, -.75, 2.3)
    if in_view(-8.0, -172.0): inst(props.SHIP_RED, -8.0, -172.0, -.75, .55)
    for bx, by, br in ((13, -146, 1.4), (9.5, -161.5, .4), (-18, -150, 2.6)): inst(g.choice(props.BOATS), bx, by, -.28, br)
    with placed(18.0, -136.0, math.degrees(math.atan2(-20.0, 2.0)), 0):                         # cargo stacked along both sides of the landward mole, a clear strip down the middle
        props.jar_rows(1.8, -1.95, 7.6, -.78, 1.21, g, gap=.45)
        props.jar_rows(9.4, -1.95, 15.2, -.78, 1.21, g, gap=.45)
        props.jar_rows(1.4, .75, 6.3, 1.45, 1.21, g, gap=.52, kind=props.SACK)
        props.jar_rows(8.2, .75, 12.2, 1.45, 1.21, g, gap=.65, kind=props.BASKET)
    with placed(19.65, -152.5, math.degrees(math.atan2(-20.0, 2.0)), 1.20):                    # slight two-spar lifting frame on the mole near the ship
        for sx in (-1.1, 1.1): core.beam("wood:#5b4128", (sx, .9, 0), (0, -1.8, 5.6), .11, 6)
        core.beam("wood:#5b4128", (-.26, -1.52, 5.05), (.26, -1.52, 5.05), .05, 5)
        core.beam("wood:#3a2a1e", (0, -1.8, 5.6), (0, -1.8, 2.3), .035, 5)
        boxr("wood:#5b4128", "wood:#6b5032", 0, -1.8, .22, .22, 2.15, 2.40)
    for ax, ay, ar in ((21.0, -133.2, .4), (22.1, -132.3, 1.9), (20.6, -131.8, 3.5)):       # pierced stone anchors at the foot of the mole
        inst(props.ANCHOR, ax, ay, land.zt(ax, ay), ar); land.take_disc(ax, ay, 1.0)
    for cx, cy, cr in ((17.5, -128.5, math.radians(-105)), (38.5, -117.5, math.radians(15))): # loaded amphora carts at the mole foot and beside the jar store
        assert land.road_dist(cx, cy) > 3.5, f"harbour cart too close to road at {(cx, cy)}"
        inst(props.CART_AMPH, cx, cy, land.zt(cx, cy), cr, 1.3); land.take_disc(cx, cy, 4.5)
    KEEP_CLEAR.append(box(-66, -142, 48, -98))
ROCKS = []

def pottery(g):
    """The potters' quarter, outside the walls for the smoke's sake: kilns, a drying shed racked with jars, wheels, the clay pit."""
    dx, dy = PL["pottery"]["door"]; ax, ay = PL["pottery"]["at"]; rg = random.Random(55)
    land.paint("earth", [(dx - 2, dy + 4), (dx - 34, dy + 2), (dx - 36, dy - 24), (dx - 10, dy - 30), (dx + 2, dy - 12)], 1.0, 3.0)
    z0 = civic.hall(ax - 16, ay - 2, ax - 3, ay + 5.5, 3.1, "x", wk="plaster:#e2d6bb", door_side="e", windows=False, va=.75, blend=2.0)
    sx0, sy0, sx1, sy1 = ax - 15, ay - 12.5, ax - 4, ay - 5.5; zs = land.pad(box(sx0, sy0, sx1, sy1), None, blend=2)          # the open drying shed
    for x in (sx0 + .3, (sx0 + sx1) / 2, sx1 - .3):
        for y in (sy0 + .3, sy1 - .3): inst(arch.column("post", 2.6, .09, "wood:#6b5032"), x, y, zs)
    shed(sx0, sy0, sx1, sy1, zs + 2.6, 1.0, "s", .8, key="tile:#a8674a", ov=.3); props.jar_rows(sx0 + .8, sy0 + .9, sx1 - .6, sy1 - .7, zs, g, .52); land.take(box(sx0, sy0, sx1, sy1))
    for idx, (kx, ky) in enumerate(((ax - 24, ay - 6), (ax - 26, ay - 15))):                # updraught kilns: a stone drum under a clay dome, the stoke-hole to the south
        zk = land.pad(rect(kx, ky, 7, 7), None, blend=2)
        core.lathe("rubble:#a99b80", kx, ky, [(3.0, zk - .3), (3.0, zk + 1.3)], 18, smooth=True, cap_top=False)
        core.lathe("clay:#a98463", kx, ky, [(3.0, zk + 1.3)] + [(3.0 * math.cos(t), zk + 1.3 + 2.0 * math.sin(t)) for t in (.3, .6, .9, 1.2, 1.45)], 18)
        core.cyl("dark:#1c1712", kx, ky, .25, zk + 3.26, zk + 3.31, 14)                    # the vent on top of the dome
        boxr("dark:#2b1a12", "dark:#2b1a12", kx, ky - 3.0, 1.0, .25, zk, zk + 1.0)
        wrot = g.uniform(0, 3)
        if idx == 0: inst(props.WOODPILE, kx + 4.6, ky - 2.5, land.zt(kx + 4.6, ky - 2.5), wrot)
        land.take(rect(kx, ky, 8, 8))
        land.paint_disc("wet", kx, ky - 4.5, 3.0, .6, 2.0)
    for fx, fy, frot in ((ax - 19.2, ay - 4.2, .3), (ax - 20.2, ay - 14.0, -.25)):         # brushwood fuel stacks of eight faggot bundles by each kiln
        with placed(fx, fy, math.degrees(frot), land.zt(fx, fy)):
            for by, bz in ((-.60, 0), (-.20, 0), (.20, 0), (.60, 0), (-.40, .34), (0, .34), (.40, .34), (0, .68)):
                inst(props.FAGGOTS, 0, by, bz, 0)
        land.take_disc(fx, fy, 1.8)
    for x, y in ((ax - 2, ay - 14), (ax + 1, ay - 9)): inst(props.POTTERS_WHEEL, x, y, land.zt(x, y))
    pit = [(ax - 33, ay + 2), (ax - 25, ay + 4), (ax - 22, ay - 1), (ax - 30, ay - 4)]; land.pad(pit, land.zt(ax - 28, ay) - .8, blend=2.5, lock=False); land.paint("wet", pit, .9, 1.5); land.paint("plough", pit, 1.0, 1.0)
    zt0 = land.zt(ax - 19.5, ay + 4.5)                                                    # three stepped clay settling tanks next to the clay pit
    for i, pkey in enumerate(("pool:#8b7355", "pool:#a08a6a", "pool:#b59f80")):
        cx, cy = ax - 19.5, ay + 4.5 - i * 2.9; zv = land.pad(rect(cx, cy, 3.4, 2.7), zt0 - i * .2, blend=1.2)
        walls("rubble:#c2b69a", rect(cx, cy, 3.0, 2.4), zv - .4, zv + .45); walls("rubble:#c2b69a", rect(cx, cy, 2.3, 1.7), zv - .4, zv + .45, inward=True)
        O, I = rect(cx, cy, 3.0, 2.4), rect(cx, cy, 2.3, 1.7)
        for (a, b), (c, d) in zip(zip(O, O[1:] + O[:1]), zip(I, I[1:] + I[:1])): face("paving:#cfc5ac", [(a[0], a[1], zv + .45), (b[0], b[1], zv + .45), (d[0], d[1], zv + .45), (c[0], c[1], zv + .45)])
        cap(pkey, I, zv + .28); land.take(rect(cx, cy, 3.4, 2.7))
    for cx, cy in ((ax - 19.5, ay + 7.4), (ax - 23.2, ay + 7.0), (ax - 26.8, ay + 6.4)):  # three clay heaps beside the settling tanks
        inst(props.CLAY_HEAP, cx, cy, land.zt(cx, cy), rg.uniform(0, 6)); land.take_disc(cx, cy, 1.8)
    swape_well(-95.0, -104.0, math.radians(60))
    props.jars(ax - 8, ay - 17, None, 26, 3.4, g); props.jars(ax - 19, ay - 21, None, 18, 2.6, g); props.jars(ax + 3, ay - 1, None, 9, 1.6, g)
    props.jar_rows(ax - 16.4, ay - 16.4, ax - 12.4, ay - 13.5, None, rg, .46, props.AMPH_RAW, 1.08)    # pale unfired ware south of the drying shed
    land.take(box(ax - 16.7, ay - 16.7, ax - 12.1, ay - 13.2))
    props.jar_rows(ax - .2, ay + 1.2, ax + 2.5, ay + 3.4, None, rg, .50, props.HYDRIA_BLACK, 1.3)     # block of black-gloss ware east of the workshop door
    land.take(box(ax - .5, ay + .9, ax + 2.8, ay + 3.7))
    for row in range(2):                                                                  # twelve stacks of roof tiles in two neat rows
        for k in range(6):
            tx, ty = ax - 2.0 + k * 1.15, ay - 18.8 + row * 1.2
            inst(props.TILE_STACK, tx, ty, land.zt(tx, ty), 0)
    land.take(box(ax - 2.7, ay - 19.4, ax + 4.4, ay - 17.0))
    sx, sy = ax - 14.5, ay - 19.8; sz = land.zt(sx, sy)                                   # waster dump at the south-west edge, broken jars half sunk
    inst(props.SHERD_HEAP, sx, sy, sz, rg.uniform(0, 6)); land.take_disc(sx, sy, 2.8)
    for k in range(10):
        a = k * 2 * math.pi / 10 + rg.uniform(-.25, .25); d = rg.uniform(.45, 1.85)
        jx, jy = sx + d * math.cos(a), sy + d * math.sin(a)
        hm = .90 - .15 * min(1, d / .92) if d < .92 else (.75 - .33 * (d - .92) / .83 if d < 1.75 else .42 - .37 * (d - 1.75) / .73)
        inst(rg.choice((props.AMPH, props.AMPH, props.HYDRIA, props.PITHOS)), jx, jy, sz + hm - .16, rg.uniform(0, 6.3), rg.uniform(.9, 1.1), tilt=(rg.uniform(.7, 1.3), rg.uniform(-.4, .4)))
    cx, cy = ax + 2.5, ay - 4.8                                                           # loaded amphora cart on the workshop side toward the road, 4 m clear
    assert land.road_dist(cx, cy) > 4.0, f"pottery cart too close to road at {(cx, cy)}"
    inst(props.CART_AMPH, cx, cy, land.zt(cx, cy), math.radians(-150), 1.3); land.take_disc(cx, cy, 3.0)
    KEEP_CLEAR.append(box(ax - 38, ay - 28, ax + 8, ay + 9))

def school(door, at, side, g, name):
    """A school in its grove, as the Academy and the Lyceum lay outside Athens: a precinct wall, a stoa to walk and talk in,
    the room where the books are kept, an exedra, an altar of the Muses, herms; plane trees and cypresses."""
    dx, dy = door
    if side == "se": R = (dx + 1.5, dy - 24.0, dx + 27.5, dy + 2.0); gate = (dx + 1.5, dy)
    else: R = (dx - 24.0, dy - 13.0, dx - 1.5, dy + 13.0); gate = (dx - 1.5, dy)
    P = box(*R); z = land.pad(P, None, blend=3.0); land.paint("earth", P, .9, 2.0); KEEP_CLEAR.append(grow(P, 1.5)); compound(R, gate, 1.7, "rubble:#c2b69a")
    x0, y0, x1, y1 = R
    if side == "se":
        civic.stoa(x0 + 4.5, y0 + 1.2, x1 - 1.2, y0 + 7.4, "n", 3.7, z=z, va=.3, blend=0)
        civic.hall(x1 - 9.2, y0 + 9.0, x1 - 1.2, y1 - 2.0, 4.6, "y", wk="plaster:#ece5d5", door_side="w", va=.45, z=z, blend=0)
        inst(props.EXEDRA, x0 + 8, y1 - 4.0, z, math.pi); inst(props.HOUSE_ALTAR, x0 + 9.5, y0 + 13, z, 0, 1.5)
        for k in range(5): inst(g.choice((props.HERM, props.STATUE_M, props.STELE)), x0 + 5.5 + k * 2.6, y0 + 9.2, z, math.pi)
        GROVES.append((box(x0 + 2, y0 + 10, x1 - 11, y1 - 1.5), "school", 7.0))
    else:
        civic.stoa(x0 + 1.2, y0 + 1.2, x0 + 7.4, y1 - 1.2, "e", 3.7, z=z, va=.3, blend=0)
        civic.hall(x0 + 9.0, y1 - 9.5, x1 - 4.0, y1 - 1.2, 4.6, "x", wk="plaster:#ece5d5", door_side="s", va=.45, z=z, blend=0)
        inst(props.EXEDRA, x1 - 5.5, y0 + 4.5, z, math.pi / 2); inst(props.HOUSE_ALTAR, x0 + 13, y0 + 9, z, 0, 1.5)
        for k in range(5): inst(g.choice((props.HERM, props.STATUE_M, props.STELE)), x0 + 9.0, y0 + 3 + k * 2.4, z, -math.pi / 2)
        GROVES.append((box(x0 + 9.5, y0 + 1.5, x1 - 1.5, y1 - 11), "school", 7.0))
    land.take(P)
    GROVES.append((grow(P, 9.0), "sacred", 9.0))

def tombs(g):
    """Roadside tombs outside the gates, as along the Street of Tombs at Athens: stelai, small walled plots, a few fine monuments."""
    for x0, x1, y in ((-100, -140, 0.0), (98, 128, 0.0)):
        n = int(abs(x1 - x0) / 3.2)
        for k in range(n):
            for sd in (-1, 1):
                if g.random() < .45: continue
                x = x0 + (x1 - x0) * (k + g.uniform(.2, .8)) / n; yy = y + sd * g.uniform(5.2, 8.5)
                if not land.free(x, yy, 1.0): continue
                zt_ = land.zt(x, yy); kind = g.random()
                if kind < .55: inst(props.STELE, x, yy, zt_, 0 if sd < 0 else math.pi, g.uniform(.8, 1.2))
                elif kind < .75: inst(props.VOTIVE, x, yy, zt_, 0, .6)
                elif kind < .9:                                                           # a family plot: a low wall of squared stone, stelai on it
                    boxr("ashlar:#cfc4a8", "paving:#cfc6b0", x, yy, 4.2, 2.6, zt_ - .3, zt_ + 1.1)
                    for i in (-1, 0, 1): inst(props.STELE, x + i * 1.2, yy, zt_ + 1.1, 0 if sd < 0 else math.pi, .8)
                else: inst(props.STATUE_M, x, yy, zt_, math.pi / 2 * sd)
                land.take_disc(x, yy, 2.6)
        GROVES.append(([(x0, y - 11), (x1, y - 11), (x1, y + 11), (x0, y + 11)], "tombs", 11.0))

def _natural_field(Q, seed):
    """Give an unwalled tilled plot organically wandering borders and rounded turn-corners."""
    rg = random.Random(seed); pts = []; ph1, ph2 = rg.uniform(0, 6.28), rg.uniform(0, 6.28)
    for idx, (a, b) in enumerate(zip(Q, Q[1:] + Q[:1])):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        nx, ny = dy / max(1e-6, L), -dx / max(1e-6, L); steps = max(5, int(L / 2.0))
        for k in range(steps):
            t = k / steps; fade = math.sin(math.pi * t) ** .55
            wob = fade * (1.15 * math.sin(t * 6.28 + ph1 + idx * 1.7) + .55 * math.sin(t * 12.56 + ph2) + rg.uniform(-.45, .45))
            pts.append((a[0] + dx * t + nx * wob, a[1] + dy * t + ny * wob))
    return core.chaikin(pts, 1)

def fields(g, estates):
    """Small tilled plots east of the town and along the coast road: stubble after the harvest, fallow under the plough, a
    few green with pulse or vegetables; each plot ploughed parallel to its own edges, walled plots neat, open ones natural."""
    def plots(x0, y0, x1, y1, w, depth, ang0):
        y = y0
        while y < y1 - 6:
            d = depth * g.uniform(.75, 1.25); x = x0 + g.uniform(-3, 3)
            while x < x1 - 6:
                ww = w * g.uniform(.7, 1.3); P = [(x + g.uniform(-.8, .8), y + g.uniform(-.8, .8)), (min(x + ww, x1) + g.uniform(-.8, .8), y + g.uniform(-.8, .8)), (min(x + ww, x1) + g.uniform(-.8, .8), min(y + d, y1) + g.uniform(-.8, .8)), (x + g.uniform(-.8, .8), min(y + d, y1) + g.uniform(-.8, .8))]
                cx, cy = centre(P); ok = in_view(cx, cy, 0, 30) and all(land.road_dist(*p) > 5 and land.sd_at(*p) > 16 for p in P + [(cx, cy)])
                ok = ok and not any(core.inpoly(px, py, K) for K in KEEP_CLEAR for px, py in P + [(cx, cy)]) and not any(core.inpoly(kx, ky, P) for K in KEEP_CLEAR for kx, ky in K) and not (land.HILL and any(core.inpoly(px, py, land.FOOT) for px, py in P))
                if ok:
                    k = g.random(); kind = "stubble" if k < .5 else "plough" if k < .74 else "green" if k < .86 else None
                    Q = grow(P, -1.3)
                    which = g.choice((0, 0, 1)) if kind else 0
                    if kind: _ = g.uniform(-4, 4)
                    walled = g.random() < .5; wall_h = g.uniform(.7, 1.0) if walled else 0.0
                    ux = ((Q[1][0] - Q[0][0] + Q[2][0] - Q[3][0]) * .5, (Q[1][1] - Q[0][1] + Q[2][1] - Q[3][1]) * .5)
                    uy = ((Q[3][0] - Q[0][0] + Q[2][0] - Q[1][0]) * .5, (Q[3][1] - Q[0][1] + Q[2][1] - Q[1][1]) * .5)
                    dir_v = ux if which == 0 else uy
                    angle = math.degrees(math.atan2(dir_v[1], dir_v[0]))
                    if kind:
                        Fp = Q if walled else _natural_field(Q, int(round(cx * 31 + cy * 97)))
                        land.field(Fp, kind, angle, feather=.8 if walled else 2.8); FIELDS.append((Fp, kind))
                    else: GROVES.append((Q, "orchard" if g.random() < 1 / 3 else "olive", 8.5))
                    if walled: drystone(P, closed=True, h=wall_h)
                    if kind == "stubble" and g.random() < .5:
                        for _ in range(g.randint(4, 10)):
                            px, py = cx + g.uniform(-ww / 3, ww / 3), cy + g.uniform(-d / 3, d / 3)
                            if core.inpoly(px, py, Q): inst(props.SHEAF, px, py, land.zt(px, py), g.uniform(0, 6))
                x += ww + g.uniform(1.5, 3.5)
            y += d + g.uniform(1.5, 4)
    plots(98, 12, 236, 124, 34, 26, 2); plots(98, -130, 236, -12, 32, 24, -5); plots(-66, -128, -34, -96, 16, 14, 8); plots(46, -128, 78, -96, 16, 14, 4)
    plots(-136, 62, -112, 110, 14, 16, 10); plots(-134, -92, -100, -40, 16, 14, 0)
FIELDS = []

def standing_grain(x0, y0, x1, y1, g, wheat, dy=.52, dx=.38):
    """Ripe grain still standing: scattered 3D stalk-and-ear clumps in close east-west rows over warm earth and stubble."""
    P = box(x0, y0, x1, y1)
    land.paint("earth", P, .65, .4)
    land.field(P, "stubble", 0.0, feather=.35)
    y = y0 + dy * .5; row = 0
    while y < y1 - dy * .25:
        x = x0 + dx * .5 + (dx * .5 if row % 2 else 0) + g.uniform(-.06, .06)
        while x < x1 - dx * .25:
            px = x + g.uniform(-.07, .07); py = y + g.uniform(-.08, .08)
            if land.free(px, py, .15):
                Scatter.add(wheat[g.randrange(len(wheat))], px, py, land.zt(px, py) - .03, g.uniform(0, 6.283), g.uniform(.86, 1.16))
            x += dx * g.uniform(.86, 1.14)
        y += dy; row += 1

def granary_fields():
    """The granary's own fields, between the ring road and the farm, on either side of the road out to it: long strips run
    east-west inside dry-stone walls, divided by grass baulks with boundary stones at their ends, plus natural open plots to
    the north and south. It is just after the harvest: one strip still stands in ripe wheat, one is half reaped with the
    sheaves lying in the swath and stooked behind the reapers, one is all stooks, one is half turned by the ard (left in the
    furrow), one green with chickpeas and lentils; north of the road a strip of wheat, a fallow ploughed strip, and an
    open stubble plot; south of the walled block, a natural ploughed plot."""
    from . import plants
    rg = random.Random(410)
    WHEAT = []
    for i in range(5):
        wg = random.Random(4100 + i * 37)
        with core.Part("wheat%d" % i) as wp:
            for s in range(14):
                a = wg.uniform(0, 6.283); r = wg.uniform(0, .17); x, y = r * math.cos(a), r * math.sin(a)
                hh = wg.uniform(.78, 1.08); lx = hh * wg.uniform(-.18, .18); ly = hh * wg.uniform(-.18, .18)
                sk = "straw:#d8bc68" if s % 3 else "straw:#cfb05a"
                ek = "straw:#e0c678" if s % 2 else "straw:#c9a64c"
                core.beam(sk, (x, y, 0.0), (x + lx, y + ly, hh), .014, 3, smooth=False)
                core.beam(ek, (x + lx, y + ly, hh), (x + lx * 1.15, y + ly * 1.15, hh + .16), .028, 4, smooth=False)
        WHEAT.append(core.collection_of(wp.mesh, "wheat%d" % i))
    with core.Part("pulse") as pp: plants.cards("leaf:#6d8a3a", [(0, 0, .2, .3, .3, .17)], 46, .075, rg, .3, .6)
    PULSE = core.collection_of(pp.mesh, "pulse")
    def strip(x0, y0, x1, y1, kind, ang=0.0, feather=.5):
        P = box(x0, y0, x1, y1)
        land.field(P, kind, ang + rg.uniform(-1.5, 1.5), feather=feather); FIELDS.append((P, kind))
    def stooks(x0, y0, x1, y1, dx=4.6, dy=3.4):
        y = y0 + dy / 2
        while y < y1 - 1:
            x = x0 + dx / 2 + rg.uniform(-.6, .6)
            while x < x1 - 1:
                px, py = x + rg.uniform(-.5, .5), y + rg.uniform(-.35, .35)
                if land.free(px, py, .6): inst(props.STOOK, px, py, land.zt(px, py) - .03, rg.uniform(0, 6.3), rg.uniform(.9, 1.1)); land.take_disc(px, py, .8)
                x += dx * rg.uniform(.85, 1.15)
            y += dy
    def horos(x, y):                                                                      # a boundary stone at a baulk's end
        z = land.zt(x, y); boxr("ashlar:#d2c8ae", "ashlar:#ddd4bc", x, y, .32, .22, z - .2, z + .62, rg.uniform(-8, 8)); land.take_disc(x, y, .4)
    # --- south of the road: four strips in one walled block, the farm track down its east side
    S = (101.0, -62.5, 142.5, -12.5)
    track = [(145.4, -3.5), (145.2, -20.0), (145.6, -40.0), (145.0, -61.0)]
    land.paint("earth", track, .85, 1.0, closed=False, width=2.3); KEEP_CLEAR.append(_widen(track, 1.6))
    drystone(box(*S), closed=True, h=.95, gaps=[(142.5, -19.0, 1.6), (142.5, -44.5, 1.6), (101.0, -31.5, 1.4)])
    drystone([(101.0, -37.6), (142.5, -37.6)], h=.85, gaps=[(139.5, -37.6, 1.3)])
    x0, x1 = S[0] + 1.2, S[2] - 1.2
    # S1, half reaped: wheat still standing in the east, stubble in the west with sheaves in the swath and stooks behind
    y0, y1 = -24.2, -13.7; cut = 122.0
    strip(x0, y0, cut, y1, "stubble")
    standing_grain(cut + .2, y0 + .2, x1 - .2, y1 - .2, rg, WHEAT); land.take(box(cut, y0, x1, y1))
    for k in range(14):                                                                   # the swath along the cut edge, sheaves bound and lying
        sx, sy = cut - rg.uniform(.6, 2.6), y0 + .7 + k * (y1 - y0 - 1.4) / 13
        inst(props.SHEAF_LYING, sx, sy, land.zt(sx, sy), rg.uniform(-.5, .5) + (math.pi if k % 3 == 0 else 0)); land.take_disc(sx, sy, .5)
    stooks(x0, y0, cut - 4.5, y1)
    cx, cy = cut - 9.0, -19.0; inst(props.CART_HAY, cx, cy, land.zt(cx, cy), math.radians(4), 1.3); land.take_disc(cx, cy, 3.0)
    for bx, by in ((cut - 3.4, -15.0), (cut - 3.0, -14.4), (x0 + 1.0, -23.3)): inst(props.BASKET, bx, by, land.zt(bx, by), rg.uniform(0, 6), 1.15)
    # S2: all reaped, the stooks standing in rows
    y0, y1 = -36.4, -25.6; strip(x0, y0, x1, y1, "stubble"); stooks(x0, y0, x1, y1, 4.2, 3.6)
    # S3: south half turned by the ard along the strip length, north half still stubble; the ard left in the boundary furrow
    y0, y1 = -50.0, -38.6; mid = -44.2
    strip(x0, y0, x1, mid, "plough", 0.0, .35); strip(x0, mid, x1, y1, "stubble", 0.0, .35)
    ax, ay = 123.5, mid; inst(props.ARD, ax, ay, land.zt(ax, ay) - .02, 0.0, 1.25); land.take_disc(ax + 1.4, ay, 2.8)
    inst(props.AMPH, 127.0, y1 - .9, land.zt(127.0, y1 - .9) + .18, 0, 1.0, tilt=(1.45, 0)); inst(props.BASKET, 127.8, y1 - 1.3, land.zt(127.8, y1 - 1.3), .3)
    for k in range(4):                                                                    # stooks remaining on the unturned north half
        px, py = x1 - 4.0 - k * 6.5, mid + 2.8 + (k % 2 - .5) * 1.1; inst(props.STOOK, px, py, land.zt(px, py) - .03, rg.uniform(0, 6)); land.take_disc(px, py, .8)
    # S4: chickpeas and lentils in rows, green against the stubble
    y0, y1 = -61.3, -51.4; strip(x0, y0, x1, y1, "green", 0.0, .35)
    y = y0 + .6
    while y < y1 - .45:
        x = x0 + .45 + rg.uniform(0, .25)
        while x < x1 - .45:
            if rg.random() < .9: Scatter.add(PULSE, x + rg.uniform(-.08, .08), y + rg.uniform(-.05, .05), land.zt(x, y) - .04, rg.uniform(0, 6.3), rg.uniform(.75, 1.25))
            x += rg.uniform(.42, .62)
        y += .95
    for x in (S[0] + 1.0, S[2] - 1.0):
        for y in (-25.0, -50.8): horos(x, y)
    # --- unwalled natural ploughed plot south of the walled block, between the SE library grove and the kitchen garden
    S_far = _natural_field(box(116.0, -85.0, 143.5, -66.0), 411)
    land.field(S_far, "plough", rg.uniform(-3.0, 3.0), feather=2.4); FIELDS.append((S_far, "plough")); land.take(S_far)
    # --- north of the road: a strip of wheat and a fallow strip, walled, between the tombs and the stream
    N1 = (102.5, 13.5, 142.5, 31.5)
    drystone(box(*N1), closed=True, h=.9, gaps=[(112.0, 13.5, 1.5), (142.5, 18.0, 1.4)])
    x0, x1 = N1[0] + 1.1, N1[2] - 1.1
    y0, y1 = 14.7, 22.0; standing_grain(x0 + .2, y0 + .2, x1 - .2, y1 - .2, rg, WHEAT); FIELDS.append((box(x0, y0, x1, y1), "stubble")); land.take(box(x0, y0, x1, y1))
    y0, y1 = 23.2, 30.3; strip(x0, y0, x1, y1, "plough", 0.0, .45)
    for x in (N1[0] + 1.0, N1[2] - 1.0): horos(x, 22.6)
    # --- unwalled natural stubble plot north of N1, tucked between the ring road and the stream bed
    N2 = _natural_field([(101.0, 34.5), (132.0, 34.5), (123.0, 50.0), (101.0, 54.0)], 412)
    land.field(N2, "stubble", 0.0, feather=2.4); FIELDS.append((N2, "stubble"))
    for px, py in ((106.5, 40.0), (113.0, 39.2), (119.5, 40.5), (108.5, 46.5), (115.8, 45.8), (105.0, 50.5)):
        if core.inpoly(px, py, N2) and land.free(px, py, .6) and land.road_dist(px, py) > 3.0:
            inst(props.STOOK, px, py, land.zt(px, py) - .03, rg.uniform(0, 6.3), rg.uniform(.9, 1.1)); land.take_disc(px, py, .8)
    for sx, sy in ((110.0, 42.5), (122.0, 38.0), (112.5, 48.2), (124.2, 43.0)):
        if core.inpoly(sx, sy, N2) and land.free(sx, sy, .4) and land.road_dist(sx, sy) > 3.0:
            inst(props.SHEAF_LYING, sx, sy, land.zt(sx, sy), rg.uniform(0, 6.3)); land.take_disc(sx, sy, .5)
    land.take(N2)
    # --- the watchman's shelter by the track, his water jar and baskets; field trees at the block corners
    hx, hy = 145.6, 22.5; inst(props.WATCH_HUT, hx, hy, land.zt(hx, hy), math.radians(90)); land.take_disc(hx, hy, 1.8)
    props.jars(hx, hy - .2, None, 3, .5, rg, (props.AMPH, props.HYDRIA), check=False); inst(props.BASKET, hx + .7, hy + .6, land.zt(hx + .7, hy + .6), 0)
    for tx, ty, kind in ((99.2, -14.5, "almond"), (99.0, -60.0, "olive"), (144.0, -64.0, "fig"), (101.0, 32.4, "almond"), (139.0, 33.0, "pomegranate")):
        houses.TREES.append((tx, ty, None, kind))
    for P in (box(*S), box(*N1), S_far, N2): land.take(grow(P, -.6)); KEEP_CLEAR.append(grow(P, 1.0))

def swape_well(x, y, rot=0.0):
    """Place a swape well with lush/wet ground discs and reserve space."""
    assert land.road_dist(x, y) > 4.0, f"swape well too close to road at {(x, y)}"
    land.paint_disc("lush", x, y, 3.0, .85, 1.5); land.paint_disc("wet", x, y, 1.2, 1.0, .6)
    inst(props.SWAPE_WELL, x, y, land.zt(x, y), rot)
    land.take_disc(x, y, 3.0)
    px, py = x - 3.45 * math.cos(rot), y - 3.45 * math.sin(rot)
    cx, cy = x - 5.20 * math.cos(rot), y - 5.20 * math.sin(rot)
    land.take_disc(px, py, 2.0); land.take_disc(cx, cy, 1.8)

def garden(x0, y0, x1, y1, g, gate_side="n"):
    """A walled kitchen garden with narrow green beds, a swape well, an earth ditch, and border fruit trees."""
    P = box(x0, y0, x1, y1)
    land.paint("earth", P, 1.0, .6)
    gate = {"n": ((x0 + x1) / 2, y1, 1.3), "s": ((x0 + x1) / 2, y0, 1.3),
            "e": (x1, (y0 + y1) / 2, 1.3), "w": (x0, (y0 + y1) / 2, 1.3)}[gate_side]
    drystone(P, closed=True, h=.95, gaps=[gate])
    wx, wy = x0 + 3.0, y1 - 2.6
    swape_well(wx, wy, math.pi)
    w = x1 - x0; avail = w - 3.2
    n = max(6, min(10, int((avail + .6) / 2.2)))
    bed_w = min(1.6, (avail - (n - 1) * .6) / n); total = n * bed_w + (n - 1) * .6
    bx0 = (x0 + x1 - total) / 2; by0, by1 = y0 + 3.2, y1 - 4.5
    for k in range(n):
        x_a = bx0 + k * (bed_w + .6); bed = box(x_a, by0, x_a + bed_w, by1)
        land.field(bed, "green", 90.0, feather=.25); land.take(bed)
    land.paint("wet", [(wx + 1.0, y1 - 4.0), (bx0 + total, y1 - 4.0)], 1.0, .3, closed=False, width=.4)
    GROVES.append((grow(P, -.8), "orchard", 4.2)); KEEP_CLEAR.append(grow(P, 2))

def _widen(pts, hw):
    """Widen an open polyline to a closed polygon of half-width hw."""
    left, right, n = [], [], len(pts)
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(0, i - 1)]; bx, by = pts[min(n - 1, i + 1)]
        L = math.hypot(bx - ax, by - ay) or 1.0
        nx, ny = -(by - ay) / L, (bx - ax) / L
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    return left + right[::-1]

def stream_bed():
    """A summer-dry stream bed east of the ring road, made by ground paint and planting only."""
    raw = [
        (112.0, 92.0), (115.0, 78.0), (121.0, 65.0), (128.0, 53.0),
        (138.0, 44.0), (149.0, 39.5), (161.0, 38.5), (173.0, 37.5), (185.0, 35.5),
    ]
    pts = core.chaikin(raw, 2, closed=False)
    for p in pts:
        assert land.road_dist(*p) >= 4.0, f"stream bed too close to road at {p}"
    land.paint("lush", pts, .95, 2.5, closed=False, width=8.0)
    land.paint("gravel", pts, 1.0, .8, closed=False, width=3.0)
    samples = core.along(pts, 1.0)
    for k in range(0, len(samples) - 2, 5):
        seg = [(samples[j][0], samples[j][1]) for j in range(k, min(k + 3, len(samples)))]
        if len(seg) >= 2:
            land.paint("gravel", seg, .65, .35, how="clear", closed=False, width=.65)
            land.paint("earth", seg, .85, .35, closed=False, width=.65)
            land.paint("wet", seg, 1.0, .4, closed=False, width=.7)
    KEEP_CLEAR.append(_widen(pts, 5.0))
    STREAMS.append((pts, _widen(pts, 1.8)))

def salt_works(g):
    """Coastal solar salt pans east of the harbour, with clay banks, drying stages, salt heaps, baskets, and a rake."""
    cx, cy, rot_deg = 61.0, -130.8, -18.0
    ang = math.radians(rot_deg); ca, sa = math.cos(ang), math.sin(ang)
    def wpt(lx, ly): return (cx + ca * lx - sa * ly, cy + sa * lx + ca * ly)
    pans_poly = [wpt(-8.3, -4.6), wpt(8.3, -4.6), wpt(8.3, 4.6), wpt(-8.3, 4.6)]
    area_poly = [wpt(-8.6, -4.8), wpt(13.6, -4.8), wpt(13.6, 4.8), wpt(-8.6, 4.8)]
    for p in pans_poly:
        sd = land.sd_at(*p)
        assert 3.0 < sd < 14.0, f"salt pan corner sd={sd:.2f} out of range at {p}"
        assert land.road_dist(*p) > 5.0 and land.free(*p), f"salt pan blocked at {p}"
    for p in area_poly:
        assert land.road_dist(*p) > 5.0 and land.free(*p), f"salt works blocked at {p}"
    z0 = land.pad(area_poly, None, blend=1.5)
    land.paint("sand", area_poly, .9, 2.5)
    with placed(cx, cy, rot_deg, z0):
        # clay banks 0.25 m high, 0.4 m wide between and around the 3 x 2 grid of 5 x 4 m pans
        for y_w in (-4.4, 0.0, 4.4):
            boxr("flat:#a8977a", "flat:#a8977a", 0.0, y_w, 16.6, .4, -.25, .25)
        for x_w in (-8.1, -2.7, 2.7, 8.1):
            for y_p in (-2.2, 2.2):
                boxr("flat:#a8977a", "flat:#a8977a", x_w, y_p, .4, 4.0, -.25, .25)
        # six pan floors 5 cm below the bank tops (z = 0.20): brine, concentrating, and salt-crust with pink-brown edge
        for col_idx, xc in enumerate((-5.4, 0.0, 5.4)):
            for yc in (-2.2, 2.2):
                x0, x1, y0, y1 = xc - 2.5, xc + 2.5, yc - 2.0, yc + 2.0
                if col_idx == 0:
                    face("pool:#8fa39c", [(x0, y0, .20), (x1, y0, .20), (x1, y1, .20), (x0, y1, .20)])
                elif col_idx == 1:
                    face("flat:#c9c2b4", [(x0, y0, .20), (x1, y0, .20), (x1, y1, .20), (x0, y1, .20)])
                else:
                    b = .45; ix0, ix1, iy0, iy1 = x0 + b, x1 - b, y0 + b, y1 - b
                    face("flat:#e2dcd0", [(ix0, iy0, .20), (ix1, iy0, .20), (ix1, iy1, .20), (ix0, iy1, .20)])
                    edge = "flat:#b07b70"
                    face(edge, [(x0, y0, .20), (x1, y0, .20), (ix1, iy0, .20), (ix0, iy0, .20)])
                    face(edge, [(x1, y0, .20), (x1, y1, .20), (ix1, iy1, .20), (ix1, iy0, .20)])
                    face(edge, [(x1, y1, .20), (x0, y1, .20), (ix0, iy1, .20), (ix1, iy1, .20)])
                    face(edge, [(x0, y1, .20), (x0, y0, .20), (ix0, iy0, .20), (ix0, iy1, .20)])
        # four heaps of salt, baskets, and a wooden rake beside the harvest pans
        for hx, hy in ((10.2, -2.0), (12.2, -1.3), (10.3, 1.7), (12.3, 2.3)):
            inst(props.SALT_HEAP, hx, hy, 0.0, g.uniform(0, 6))
        for bx, by in ((9.4, -3.4), (10.3, -3.6), (9.5, 3.3), (11.7, .4), (12.7, .6)):
            inst(props.BASKET, bx, by, 0.0, g.uniform(0, 6), 1.25)
        inst(props.RAKE, 10.2, -.2, 0.0, .45)
    land.take([wpt(-10.5, -6.5), wpt(15.5, -6.5), wpt(15.5, 6.5), wpt(-10.5, 6.5)])
    KEEP_CLEAR.append([wpt(-11.8, -7.8), wpt(16.8, -7.8), wpt(16.8, 7.8), wpt(-11.8, 7.8)])

def build():
    g = random.Random(77)
    e1 = granary(g); e2 = winery(g); fishery(g); pottery(g)
    swape_well(-162.0, -29.0, 0.0)
    swape_well(99.5, 9.5, math.radians(170))
    inst(props.TROUGH, 100.5, 7.4, land.zt(100.5, 7.4), 0.0); land.take_disc(100.5, 7.4, 1.6)
    garden(148.0, -50.5, 166.0, -33.5, g, "n")
    garden(-146.0, -30.0, -130.0, -12.0, g, "w")
    garden(49.0, -115.0, 67.0, -97.5, g, "n")
    school(PL["southeast library"]["door"], PL["southeast library"]["at"], "se", g, "se"); school(PL["northwest library"]["door"], PL["northwest library"]["at"], "nw", g, "nw")
    stream_bed(); salt_works(g)
    tombs(g); granary_fields(); fields(g, (e1, e2))
