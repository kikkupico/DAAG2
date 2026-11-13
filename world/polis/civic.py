"""Public buildings: stoas, temples, halls, the theatre, the palaistra; and the town's civic centre built from them.

The models are Priene's: an agora closed by stoas on three sides, the main street running along its north side past a long
two-aisled stoa with the council house and a small sanctuary behind it; a theatre whose seats lie on the acropolis' slope."""
import math, random
import numpy as np
from . import core, land, arch, props, houses
from .core import S, face, wall, walls, cap, prism, boxr, box, rect, grow, inst, lerp, placed, oriented, centre
from .arch import shed, gable, hip, door, window, panel, wface, column, colonnade, entablature, krepis
from .houses import ROT, EDGE

STONE = "ashlar:#d8cdb4"; MARBLE = "marble"; FLOOR = "paving:#d5ccb6"; STEP = "marble:#ddd5c2"

def stoa(x0, y0, x1, y1, front, hc=4.2, aisles=1, rooms=0.0, wk=STONE, z=None, va=.3, tk="tile:#b8754f", order="doric", ends=True, steps=True, blend=1.0):
    """A stoa: a long roofed colonnade open on one side ('n', 's', 'e' or 'w'), a wall behind, sometimes a row of rooms in the back."""
    R = box(x0, y0, x1, y1); z0 = land.pad(R, z, blend=blend); land.take(R, .8); cx, cy = centre(R)
    L, Dp = (x1 - x0, y1 - y0) if front in "ns" else (y1 - y0, x1 - x0); zf = z0 + .45; hl, hd = L / 2, Dp / 2; t = .55; kw = dict(va=va, vb=zf)
    with placed(cx, cy, math.degrees(ROT[front])):
        prism(STEP, FLOOR, box(-hl, -hd, hl, hd), z0 - 1.2, zf)
        if steps:
            for g_, zz in ((.8, zf - .3), (.4, zf - .15)): prism(STEP, STEP, box(-hl, -hd - g_, hl, -hd), z0 - 1.2, zz)
        zt = zf + hc; n = max(2, round((L - 1.2) / 2.35)) + 1
        colonnade((-hl + .6, -hd + .55), (hl - .6, -hd + .55), n, order, hc, hc * .08, zf)
        ztop = entablature(box(-hl, -hd + .1, hl, -hd + 1.0), zt, hc, order)
        prism(wk, None, box(-hl, hd - t, hl, hd), zf, ztop, zb=zf, **kw)
        if ends:
            for sx in (-1, 1): prism(wk, None, box(min(sx * hl, sx * (hl - t)), -hd + .15, max(sx * hl, sx * (hl - t)), hd - t), zf, ztop, zb=zf, **kw)
        if rooms:
            yr = hd - rooms; prism(wk, None, box(-hl + t, yr - .4, hl - t, yr), zf, ztop, zb=zf, **kw); m = max(1, int(L / 4.6))
            for i in range(m): panel("dark", (hl - t, yr - .4), (-hl + t, yr - .4), (L - 2 * t) * (i + .5) / m, 1.3, zf, zf + 2.5, .04)
        if aisles == 2:
            ym = (-hd + (hd - rooms)) / 2; colonnade((-hl + .6 + (L - 1.2) / (n - 1), ym), (hl - .6 - (L - 1.2) / (n - 1), ym), max(2, (n - 1) // 2), "ionic", hc + hc * .2, hc * .065, zf)
        gable(-hl, -hd, hl, hd, ztop, Dp / 2 * .3, "x", va, wk, kw, zb=zf, key=tk, ov=.45, rake=.3)
    return zf

def temple(cx, cy, rot, w, l, hc, nf, ns, order="ionic", z=None, key=MARBLE, tk="tile:#c79f7c", peripteral=True, va=.2, steps=3, blend=1.5):
    """A temple, its front toward local -y (turned `rot` degrees): columns all round (or only a porch), a walled cella with its
    porch and great door, entablature, pediments with a painted field, a tiled roof with ridge and corner ornaments."""
    R = rect(cx, cy, w + 2.4, l + 2.4, rot); z0 = land.pad(R, z, blend=blend); land.take(R, 1.0); hw, hl = w / 2, l / 2; zs = z0 + .3 * steps
    r = hc * (.062 if order == "ionic" else .085); m = r * 1.35 + .12
    with placed(cx, cy, rot):
        krepis(-hw, -hl, hw, hl, z0, zs, steps)
        bx, by = (w - 2 * m) / (nf - 1), (l - 2 * m) / (ns - 1); e = r * 1.25
        E = box(-hw + m - e, -hl + m - e, hw - m + e, hl - m + e)
        colonnade((-hw + m, -hl + m), (hw - m, -hl + m), nf, order, hc, r, zs, key, rot=0)
        if peripteral:
            colonnade((-hw + m, hl - m), (hw - m, hl - m), nf, order, hc, r, zs, key, rot=0)
            for sx in (-1, 1): colonnade((sx * (hw - m), -hl + m), (sx * (hw - m), hl - m), ns, order, hc, r, zs, key, ends=False, rot=0)
            c = (-hw + m + bx, -hl + m + by * 1.0, hw - m - bx, hl - m - by * 1.0); yf = c[1] + by * 1.6
        else:
            c = (-hw + .25, -hl + m + by * 1.2, hw - .25, hl - .25); yf = c[1] + .01
        ztop = entablature(E, zs + hc, hc, order, key)
        for a, b in (((c[0], yf), (c[2], yf)),):                                           # the cella: side and back walls, antae, the door wall
            prism(key, None, box(c[0], yf, c[2], c[3]), zs, ztop, va=va)
            prism(key, None, box(c[0], c[1], c[0] + .5, yf), zs, ztop, va=va); prism(key, None, box(c[2] - .5, c[1], c[2], yf), zs, ztop, va=va)
            panel("dark:#241b14", (c[0], yf), (c[2], yf), (c[2] - c[0]) / 2, min(2.4, (c[2] - c[0]) * .32), zs, zs + hc * .68, .05)
            panel("bronze", (c[0], yf), (c[2], yf), (c[2] - c[0]) / 2 - min(2.4, (c[2] - c[0]) * .32) * .26, min(2.4, (c[2] - c[0]) * .32) * .46, zs, zs + hc * .66, .08)
            if peripteral: colonnade((c[0] + (c[2] - c[0]) * .33, c[1] + .4), (c[0] + (c[2] - c[0]) * .67, c[1] + .4), 2, order, hc, r, zs, key, rot=0)
        rise = (E[2][0] - E[0][0]) / 2 * .26
        gable(E[0][0], E[0][1], E[2][0], E[2][1], ztop, rise, "y", va, "paint:#354f6b", None, zb=zs, key=tk, ov=.5, rake=.45)
        for yy, sgn in ((E[0][1] - .46, -1), (E[2][1] + .46, 1)):                         # the raking cornice and the figures in the pediment
            for sx in (-1, 1):
                core.bar(key, (sx * (E[2][0] + .5), yy, ztop - .05), (0, yy, ztop + rise + .12), .5, .3)
            core.bar(key, (E[0][0] - .5, yy, ztop + .04), (E[2][0] + .5, yy, ztop + .04), .5, .2)
            for k in range(7):
                t = (k + .5) / 7 * 2 - 1; hh = rise * (1 - abs(t)) * .75
                if hh > .22:
                    xx = t * (E[2][0] - .7)
                    boxr("marble:#f3efe5", "marble:#f3efe5", xx, yy - sgn * .24, .38, .22, ztop + .15, ztop + .15 + hh * .78)
                    core.cyl("marble:#f3efe5", xx, yy - sgn * .24, .13, ztop + .15 + hh * .78, ztop + .15 + hh, 8)
            inst(AKRO, 0, yy, ztop + rise + .25, 0); inst(AKRO, E[0][0] - .2, yy, ztop + .2, 0, .7); inst(AKRO, E[2][0] + .2, yy, ztop + .2, 0, .7)
        if peripteral:
            # marble antefixes along the eaves and gilded votive shields on the front and side architrave
            for sx in (-1, 1):
                for k in range(ns * 2 - 1):
                    yy = lerp(E[0][1] + .2, E[2][1] - .2, k / max(1, ns * 2 - 2))
                    boxr("marble:#efe9dc", "gold", sx * (E[2][0] + .42), yy, .16, .26, ztop - .04, ztop + .28)
            for k in range(nf - 1):
                xx = lerp(E[0][0] + bx * .5, E[2][0] - bx * .5, k / max(1, nf - 2))
                core.cyl("gold", xx, E[0][1] - .06, .34, zs + hc + hc * .02, zs + hc + hc * .16, 12)
    return zs
def _akro():
    boxr("marble:#e8e1d0", "marble:#efe9dc", 0, 0, .55, .45, 0, .22)
    core.lathe("gold", 0, 0, [(.18, .22), (.32, .55), (.44, .88), (.22, 1.2), (.04, 1.45)], 8, cap_top=True)
    for sx in (-1, 1):
        core.beam("gold", (sx * .14, 0, .35), (sx * .52, 0, .95), .07, 6)
AKRO = props.part("akroterion", _akro)

def hall(x0, y0, x1, y1, h, axis, wk=STONE, tk="tile:#b8754f", z=None, door_side="s", windows=True, va=.4, porch=0, blend=1.0, g=None):
    """A plain public hall under a gabled roof: a council house, a store, a shed."""
    R = box(x0, y0, x1, y1); z0 = land.pad(R, z, blend=blend); land.take(R, .6); kw = dict(va=va, vb=z0)
    walls(wk, R, z0 - 1.0, z0 + h, zb=z0, **kw)
    d = (y1 - y0) if axis == "x" else (x1 - x0)
    gable(x0, y0, x1, y1, z0 + h, d / 2 * .3, axis, va, wk, kw, zb=z0, key=tk, ov=.5, rake=.3)
    if door_side:
        p, q = EDGE[door_side](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1]); door(p, q, L / 2, z0, 1.8, 3.0, frame=STEP)
    if windows:
        for sd in "nsew":
            p, q = EDGE[sd](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1]); n = max(2, int(L / 3.4))
            for i in range(n): panel("dark", p, q, L * (i + .5) / n, .8, z0 + h - 2.0, z0 + h - .8, .04)
    return z0

def peristyle(x0, y0, x1, y1, depths, h, hc, wk="plaster:#ece5d5", tk="tile:#b8754f", z=None, va=.3, floor="earth:#d6c7a2", door_side="w", door_at=None, order="doric", exedra=None, blend=0.5):
    """A building round a colonnaded court (a palaistra, a prytaneion): ranges of rooms `depths` = (n, e, s, w) deep, porticoes
    on all four sides of the court. `exedra` names a side whose range opens to the court through columns."""
    R = box(x0, y0, x1, y1); z0 = land.pad(R, z, blend=blend); land.take(R, .6); kw = dict(va=va, vb=.05); dn, de, ds, dw = depths
    cap(floor, R, z0 + .02); walls("rubble", grow(R, .06), z0 - 1.2, z0 + .08)
    cx0, cy0, cx1, cy1 = x0 + dw, y0 + ds, x1 - de, y1 - dn
    for bx, low in (((x0, y1 - dn, x1, y1), "s"), ((x0, y0, x0 + dw, y1 - dn), "e"), ((x1 - de, y0, x1, y1 - dn), "w"), ((x0 + dw, y0, x1 - de, y0 + ds), "n")):
        dd = {"s": dn, "e": dw, "w": de, "n": ds}[low]
        if exedra == {"s": "n", "e": "w", "w": "e", "n": "s"}[low]:                       # open to the court between columns
            a, b = (bx[0] + (bx[2] - bx[0]) * .3, bx[1]), (bx[0] + (bx[2] - bx[0]) * .7, bx[1])
            houses.room(wk, bx[0], bx[1], bx[0] + (bx[2] - bx[0]) * .3, bx[3], z0, z0 + h, kw); houses.room(wk, bx[0] + (bx[2] - bx[0]) * .7, bx[1], bx[2], bx[3], z0, z0 + h, kw)
            wall(wk, (bx[0], bx[3]), (bx[2], bx[3]), z0 - 1, z0 + h, 0, z0, **kw); wall(wk, (bx[2], bx[3]), (bx[0], bx[3]), z0 - 1, z0 + h, 0, z0, **kw)
            colonnade((a[0] + .4, a[1] + .3), (b[0] - .4, b[1] + .3), 4, "ionic", h - .5, .22, z0); prism(wk, None, box(a[0], a[1], b[0], a[1] + .6), z0 + h - .5, z0 + h, zb=z0, **kw)
        else:
            houses.room(wk, *bx, z0, z0 + h, kw)
            houses.openings(*bx, low, z0, random.Random(int(bx[0] * 7 + bx[1])), max(1, int(max(bx[2] - bx[0], bx[3] - bx[1]) / 5)), "door", w=1.2, h=2.3, margin=max(dn, dw) + 1)
        shed(*bx, z0 + h, dd * .26, low, va, wk, kw, zb=z0, key=tk)
    pd = max(2.2, hc * .75); zp = z0 + hc + .35
    for bx, low in (((cx0, cy1 - pd, cx1, cy1), "s"), ((cx0, cy0, cx0 + pd, cy1), "e"), ((cx1 - pd, cy0, cx1, cy1), "w"), ((cx0, cy0, cx1, cy0 + pd), "n")):
        shed(*bx, zp, pd * .2, low, va, key=tk, ov=.2, side=0, back=0)
    a, b = (cx0 + pd - .3, cy0 + pd - .3), (cx1 - pd + .3, cy1 - pd + .3); n = max(3, round((b[0] - a[0]) / 2.3) + 1); n2 = max(3, round((b[1] - a[1]) / 2.3) + 1)
    for p, q, k in (((a[0], a[1]), (b[0], a[1]), n), ((b[0], a[1]), (b[0], b[1]), n2), ((b[0], b[1]), (a[0], b[1]), n), ((a[0], b[1]), (a[0], a[1]), n2)):
        colonnade(p, q, k, order, hc, hc * .085, z0, "marble:#ebe5d8"); L = math.hypot(q[0] - p[0], q[1] - p[1]); ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        core.bar("marble:#e6dfcf", (p[0], p[1], z0 + hc + .17), (q[0], q[1], z0 + hc + .17), .5, .34)
    p, q = EDGE[door_side](x0, y0, x1, y1); L = math.hypot(q[0] - p[0], q[1] - p[1]); t = L / 2 if door_at is None else door_at
    door(p, q, t, z0, 2.0, 2.9, frame=STEP)
    ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L; ox, oy = uy, -ux                    # a porch of two columns before the door
    for s in (-1, 1): inst(column("doric", 3.2, .26), p[0] + ux * (t + s * 1.5) + ox * 1.6, p[1] + uy * (t + s * 1.5) + oy * 1.6, z0)
    with placed(p[0] + ux * t + ox * .9, p[1] + uy * t + oy * .9, math.degrees(math.atan2(uy, ux))):
        prism("marble:#e6dfcf", None, box(-2.0, -1.1, 2.0, .9), z0 + 3.2, z0 + 3.75); gable(-2.0, -1.1, 2.0, .9, z0 + 3.75, .55, "y", va, "marble:#e6dfcf", key=tk, ov=.2, rake=.15)
    return z0, (a[0], a[1], b[0], b[1])

def fountain_house(cx, cy, front, z=None):
    """A spring house: a basin behind a row of columns, under a tiled roof, where the town draws its water."""
    w, d, hc = 7.0, 4.4, 2.9; R = rect(cx, cy, w, d, math.degrees(ROT[front])); z0 = land.pad(R, z, blend=.8); land.take(R, .8); kw = dict(va=.5, vb=z0)
    with placed(cx, cy, math.degrees(ROT[front])):
        prism(STEP, FLOOR, box(-w / 2, -d / 2, w / 2, d / 2), z0 - 1, z0 + .3)
        prism(STONE, None, box(-w / 2, d / 2 - .5, w / 2, d / 2), z0 + .3, z0 + .3 + hc + .7, zb=z0, **kw)
        for sx in (-1, 1): prism(STONE, None, box(min(sx * w / 2, sx * (w / 2 - .5)), -d / 2 + .2, max(sx * w / 2, sx * (w / 2 - .5)), d / 2 - .5), z0 + .3, z0 + .3 + hc + .7, zb=z0, **kw)
        prism(STEP, None, box(-w / 2 + .5, -.2, w / 2 - .5, d / 2 - .5), z0 + .3, z0 + 1.1); cap("pool", box(-w / 2 + .7, 0, w / 2 - .7, d / 2 - .7), z0 + 1.0)
        colonnade((-w / 2 + .5, -d / 2 + .45), (w / 2 - .5, -d / 2 + .45), 4, "doric", hc, .22, z0 + .3)
        zt = entablature(box(-w / 2, -d / 2 + .1, w / 2, -d / 2 + .8), z0 + .3 + hc, hc * .9)
        gable(-w / 2, -d / 2, w / 2, d / 2, z0 + .3 + hc + .7, d / 2 * .3, "x", .3, STONE, kw, zb=z0, key="tile:#b8754f", ov=.35)

# ---------------------------------------------------------------- the theatre
TH = dict(cx=38.5, cy=58.0, r_orch=6.2, r0=7.6, rise=.40, depth=.80, rows=22, diazoma=11, a0=-14.0, a1=194.0)
def _theatre_radii():
    out = []; r = TH["r0"]; z = 0.0
    for k in range(TH["rows"]):
        if k == TH["diazoma"]: r += 1.7; z += .55
        out.append((r, z + TH["rise"])); r += TH["depth"]; z += TH["rise"]
    return out, r
def theatre_cut(zo):
    """Shape the slope for the theatre: a level orchestra and stage yard, and the hollow of the seats above it."""
    rows, r1 = _theatre_radii(); cx, cy = TH["cx"], TH["cy"]; sub = land.win(cx - r1 - 6, cy - 22, cx + r1 + 6, cy + r1 + 6); xs, ys = land.X[sub], land.Y[sub]
    r = np.hypot(xs - cx, ys - cy); ang = np.degrees(np.arctan2(ys - cy, xs - cx)); ang = np.where(ang < -90, ang + 360, ang)
    rr = np.array([p[0] for p in rows] + [r1 + 2]); zz = np.array([p[1] - TH["rise"] for p in rows] + [rows[-1][1]]) + zo - .3
    cone = np.interp(r, rr, zz, left=zo)
    sector = (ang >= TH["a0"]) & (ang <= TH["a1"]) & (r <= r1 + .7)
    yard = (~sector) & (ys < cy + 2) & (ys > cy - 20.5) & (np.abs(xs - cx) < r1 + 3) & (r > 0)
    Zs = land.Z[sub]; fr = ~land.LOCK[sub]
    Zs[sector & fr] = cone[sector & fr]; Zs[yard & fr] = zo
    land.LOCK[sub] |= sector | yard; land.OCC[sub] |= sector | yard
def theatre(g):
    zo = land.zt(TH["cx"], 41.5) + .25; theatre_cut(zo); cx, cy = TH["cx"], TH["cy"]; rows, r1 = _theatre_radii(); seat = "marble:#dcd4c2"
    a0, a1 = math.radians(TH["a0"]), math.radians(TH["a1"]); n = 52; A = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
    P = lambda r, a, z: (cx + r * math.cos(a), cy + r * math.sin(a), z)
    for k, (r, zt_) in enumerate(rows):                                                   # the seats: a riser and a tread for every row, ring by ring
        zt_ += zo; r2 = r + TH["depth"]; zb = zo + (rows[k - 1][1] if k else 0.0)
        for a, b in zip(A, A[1:]):
            face(seat, [P(r, b, zb), P(r, a, zb), P(r, a, zt_), P(r, b, zt_)], [(0, 0), (1, 0), (1, .4), (0, .4)], va=k / 30)
            face(seat, [P(r, a, zt_), P(r2, a, zt_), P(r2, b, zt_), P(r, b, zt_)][::-1], va=k / 30)
        if k == TH["diazoma"]:
            ri = r - 1.7
            for a, b in zip(A, A[1:]): face("paving:#cfc6b0", [P(ri - .02, a, zb + .01), P(r, a, zb + .01), P(r, b, zb + .01), P(ri - .02, b, zb + .01)][::-1])
    ztop = zo + rows[-1][1]; lo, hi = rows[:TH["diazoma"]], rows[TH["diazoma"]:]
    def stairs(rs, angles):                                                              # stairways: strips lying on the seats' edges
        for a in angles:
            w = .5; ra, rb = rs[0][0] - .05, rs[-1][0] + TH["depth"]; za, zb_ = zo + rs[0][1] - TH["rise"] + .06, zo + rs[-1][1] + .06
            ux, uy = math.cos(a), math.sin(a); px, py = -uy * w, ux * w
            Q = lambda r_, s, z: (cx + r_ * ux + s * px, cy + r_ * uy + s * py, z)
            face("paving:#b9b09b", [Q(ra, -1, za), Q(rb, -1, zb_), Q(rb, 1, zb_), Q(ra, 1, za)][::-1])
    stairs(lo, [a0 + (a1 - a0) * i / 7 for i in range(8)]); stairs(hi, [a0 + (a1 - a0) * i / 14 for i in range(15)])
    for a, sg in ((a0, -1), (a1, 1)):                                                     # the analemmata: the end walls that hold up the seats' wings
        ux, uy = math.cos(a), math.sin(a); nx, ny = (uy * sg * -1, -ux * sg * -1)
        nx, ny = (math.sin(a), -math.cos(a)) if sg < 0 else (-math.sin(a), math.cos(a))    # away from the seats
        ra, rb = TH["r0"] - .2, r1 + .8
        for off in (0.0, 1.1):
            pts = [(cx + ra * ux + nx * off, cy + ra * uy + ny * off, zo - 1), (cx + rb * ux + nx * off, cy + rb * uy + ny * off, zo - 1),
                   (cx + rb * ux + nx * off, cy + rb * uy + ny * off, ztop + .9), (cx + ra * ux + nx * off, cy + ra * uy + ny * off, zo + 1.1)]
            oriented(STONE, pts, (nx, ny, 0) if off else (-nx, -ny, 0), uv=[(0, zo - 1), (rb - ra, zo - 1), (rb - ra, ztop + .9), (0, zo + 1.1)], vb=zo)
        face("paving:#cfc6b0", [(cx + ra * ux, cy + ra * uy, zo + 1.1), (cx + rb * ux, cy + rb * uy, ztop + .9), (cx + rb * ux + nx * 1.1, cy + rb * uy + ny * 1.1, ztop + .9), (cx + ra * ux + nx * 1.1, cy + ra * uy + ny * 1.1, zo + 1.1)][::-sg])
        oriented(STONE, [(cx + ra * ux, cy + ra * uy, zo - 1), (cx + ra * ux + nx * 1.1, cy + ra * uy + ny * 1.1, zo - 1), (cx + ra * ux + nx * 1.1, cy + ra * uy + ny * 1.1, zo + 1.1), (cx + ra * ux, cy + ra * uy, zo + 1.1)], (-ux, -uy, 0), vb=zo)
        oriented(STONE, [(cx + rb * ux, cy + rb * uy, zo - 3), (cx + rb * ux + nx * 1.1, cy + rb * uy + ny * 1.1, zo - 3), (cx + rb * ux + nx * 1.1, cy + rb * uy + ny * 1.1, ztop + .9), (cx + rb * ux, cy + rb * uy, ztop + .9)], (ux, uy, 0), vb=zo)
    for a, b in zip(A, A[1:]):                                                            # the rim: a wall round the back of the top row, down to the ground outside
        for rr_, inw in ((r1 + .8, False), (r1 + .25, True)):
            p_, q_ = (cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)), (cx + rr_ * math.cos(b), cy + rr_ * math.sin(b))
            zb = min(land.zt(cx + (r1 + 2) * math.cos(a), cy + (r1 + 2) * math.sin(a)), ztop) - 1.2
            if inw: wall(STONE, q_, p_, ztop - .1, ztop + .9, 0, 0, vb=zo)
            else: wall(STONE, p_, q_, zb, ztop + .9, rr_ * a, 0, vb=zb + 1)
        face("paving:#cfc6b0", [P(r1 + .25, a, ztop + .9), P(r1 + .8, a, ztop + .9), P(r1 + .8, b, ztop + .9), P(r1 + .25, b, ztop + .9)][::-1])
    # the orchestra: beaten earth in a stone kerb, the altar at its centre; a drain between it and the front row
    N = 36; ro = TH["r_orch"]
    face("earth:#cdb994", [(cx + ro * math.cos(2 * math.pi * i / N), cy + ro * math.sin(2 * math.pi * i / N), zo + .04) for i in range(N)])
    for i in range(N):
        t0, t1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1) / N
        face("marble:#e6dfcf", [P(ro, t0, zo + .07), P(ro + .4, t0, zo + .07), P(ro + .4, t1, zo + .07), P(ro, t1, zo + .07)][::-1])
    cap("paving:#c9c0aa", box(cx - 28, cy - 20, cx + 28, cy + 1.5), zo + .02)
    inst(props.HOUSE_ALTAR, cx, cy, zo + .04, 0, 1.3)
    # the stage building: a long two-storey skene, the columned proskenion before it, and the gateways of the two side entrances
    sy = cy - TH["r0"] - 8.4; sx0, sx1 = cx - 12, cx + 12; hs = 7.2; kw = dict(va=.5, vb=zo)
    walls(STONE, box(sx0, sy, sx1, sy + 5.6), zo - 1, zo + hs, zb=zo, **kw); hip(sx0, sy, sx1, sy + 5.6, zo + hs, 1.2, .35, key="tile:#b8754f")
    p, q = (sx0, sy), (sx1, sy)
    for t in (4, 12, 20): door(p, q, t, zo, 1.6, 2.6, frame=STEP)
    for t in (2, 7, 12, 17, 22): panel("dark", p, q, t, .8, zo + 4.6, zo + 5.8, .04); panel("dark", (sx1, sy + 5.6), (sx0, sy + 5.6), t, 2.2, zo + 3.4, zo + 6.0, .04)
    py0, py1 = sy + 5.6, sy + 8.3; colonnade((sx0 + 1.5, py1 - .25), (sx1 - 1.5, py1 - .25), 11, "doric", 2.7, .2, zo + .1)
    prism("marble:#e6dfcf", "wood:#8a6a44", box(sx0 + 1.2, py0, sx1 - 1.2, py1), zo + 2.8, zo + 3.2)
    for s in (-1, 1):
        gx = cx + s * 16.5
        for yy in (sy + 3.0, sy + 6.6): boxr("marble:#e6dfcf", "marble:#e6dfcf", gx, yy, .7, .7, zo, zo + 3.6)
        prism("marble:#e6dfcf", "marble:#e6dfcf", box(gx - .45, sy + 2.6, gx + .45, sy + 7.0), zo + 3.6, zo + 4.2)
        walls(STONE, box(min(gx, cx + s * 12), sy, max(gx, cx + s * 12), sy + .7), zo - 1, zo + 2.6, zb=zo, **kw)
    land.paint("pave", box(cx - 28, cy - 20, cx + 28, cy + 1), 1.0, 1.0)

# ---------------------------------------------------------------- the civic centre
def agora(g):
    """The agora: an open square south of the main street, stoas on its west, south and east; across the street the long
    north stoa. In the square: the altar, lines of statues and stelai, exedrae, a fountain house, a few market stalls."""
    sq = box(-35.5, -35.5, 35.5, -4.0)
    land.paint("earth", sq, 1.0, 1.5); land.take(sq)
    stoa(-35.5, -35.5, -5.2, -29.0, "n", 3.9, va=.35); stoa(5.2, -35.5, 35.5, -29.0, "n", 3.9, va=.5)
    stoa(-35.5, -28.4, -29.3, -5.0, "e", 3.9, va=.6); stoa(29.3, -28.4, 35.5, -5.0, "w", 3.9, va=.25)
    for r in (box(-29.3, -29.0, -5.2, -26.2), box(5.2, -29.0, 29.3, -26.2), box(-29.3, -28.4, -26.4, -5.0), box(26.4, -28.4, 29.3, -5.0)): land.paint("pave", r, 1.0, .8)
    stoa(-35.5, 5.4, -5.2, 16.2, "s", 4.8, aisles=2, rooms=3.6, va=.3); stoa(5.2, 5.4, 35.5, 16.2, "s", 4.8, aisles=2, rooms=3.6, va=.45)
    land.paint("pave", box(-35.5, 4.0, 35.5, 5.6), 1.0, .5)
    z = land.zt
    inst(props.ALTAR, -17, -17, z(-17, -17), 0, .62); land.paint("pave", rect(-17, -17, 8, 6), 1.0, 1.0)
    for i in range(9):                                                                    # honours along the street: bronzes of benefactors on their bases
        x = -27 + i * 2.6
        if abs(x) > 5: inst(g.choice((props.STATUE_B, props.STATUE_B, props.STATUE_M)), x, -6.2, z(x, -6.2), math.pi)
    for i in range(8):
        x = 7.5 + i * 2.7; inst(g.choice((props.STATUE_B, props.STATUE_M, props.STELE, props.STELE)), x, -6.2, z(x, -6.2), math.pi)
    for x in (-6.2, 6.2):
        for i in range(6): y = -10 - i * 3.0; inst(g.choice((props.STELE, props.HERM, props.STATUE_M)), x, y, z(x, y), math.pi / 2 if x < 0 else -math.pi / 2)
    inst(props.EXEDRA, -22, -24.5, z(-22, -24.5), 0); inst(props.EXEDRA, 14, -24.5, z(14, -24.5), 0); inst(props.VOTIVE, -9, -24, z(-9, -24)); inst(props.VOTIVE, 9.5, -9.5, z(9.5, -9.5))
    fountain_house(22.5, -9.2, "s")
    stalls = [
        (12, -15, g.choice((0, math.pi))), (16.5, -15, g.choice((0, math.pi))), (21, -15.5, g.choice((0, math.pi))),
        (12.5, -20.5, g.choice((0, math.pi))), (17, -20, g.choice((0, math.pi))), (22, -21, g.choice((0, math.pi))),
        (-26.2, -11.5, math.pi / 2), (-26.2, -15.5, math.pi / 2), (-26.2, -19.5, math.pi / 2), (-26.2, -23.5, math.pi / 2),
        (-22.5, -11.5, -math.pi / 2), (-22.5, -15.5, -math.pi / 2), (-22.5, -19.5, -math.pi / 2), (-17.5, -22.5, 0.0),
    ]
    cloths = [0, 2, 1, 6, 3, 7, 8, 5, 9, 4, 6, 0, 7, 8]
    g.shuffle(cloths)
    for (x, y, rot), ci in zip(stalls, cloths):
        assert land.road_dist(x, y) > 4, f"stall too close to road at {(x, y)}"
        r = rot + g.uniform(-.08, .08); cr, sr = math.cos(r), math.sin(r)
        inst(props.STALLS[ci], x, y, z(x, y), r)
        for k in range(g.randint(6, 10)):
            on_counter = k % 2 == 0
            lx = g.uniform(-1.05, 1.05) if on_counter else g.uniform(-1.25, 1.25)
            ly = g.uniform(-.72, -.28) if on_counter else g.uniform(-1.45, -1.00)
            gx, gy = x + cr * lx - sr * ly, y + sr * lx + cr * ly
            gz = (z(x, y) + .85) if on_counter else z(gx, gy)
            inst(g.choice((props.AMPH, props.SACK, props.BASKET)), gx, gy, gz, g.uniform(0, 6), g.uniform(.78, .92))
    for part_, cx, cy, ang in ((props.CART_AMPH, 25.2, -15.5, math.radians(-95)), (props.CART_SACKS, -19.5, -9.8, math.radians(-5))):
        assert land.road_dist(cx, cy) > 5.5, f"cart too close to main street at {(cx, cy)}"
        inst(part_, cx, cy, z(cx, cy), ang, 1.3)
    bx, by = -13.5, -24.0; bz = z(bx, by)                                                # speakers' platform (bema) in front of the south stoa
    with placed(bx, by, 0, bz):
        prism(STONE, FLOOR, box(-1.5, -1.0, 1.5, 1.0), -.3, 1.0, zb=0)
        prism(STONE, FLOOR, box(1.5, -.8, 1.9, .8), -.3, .67, zb=0)
        prism(STONE, FLOOR, box(1.9, -.8, 2.3, .8), -.3, .33, zb=0)
    inst(props.SUNDIAL, 10.0, -24.5, z(10.0, -24.5))
    tx, ty, trot = 9.2, -17.5, math.pi / 2; tz = z(tx, ty)                               # standard measures table (sekoma) by the east stalls
    inst(props.TABLE, tx, ty, tz, trot, 1.3)
    with placed(tx, ty, math.degrees(trot), tz):
        for dx, dy, r in ((-.62, .05, .15), (-.31, -.06, .13), (0.0, .06, .115), (.30, -.05, .10), (.58, .04, .09)):
            core.cyl("dark:#221c16", dx, dy, r, 1.04, 1.10, 10)
    houses.TREES.append((-12, -11.5, z(-12, -11.5), "plane")); houses.TREES.append((25, -22.5, z(25, -22.5), "plane"))
    for tx, ty in ((-11.0, -19.5), (14.5, -10.5)):
        assert land.road_dist(tx, ty) >= 6, f"plane tree too close to road at {(tx, ty)}"
        houses.TREES.append((tx, ty, z(tx, ty), "plane"))
        inst(props.BENCH, tx, ty - 1.3, z(tx, ty - 1.3), 0)

def north_quarter(g):
    """Behind the north stoa: the council house and the prytaneion to the east, a small sanctuary to the west."""
    hall(6.0, 18.4, 21.5, 35.2, 7.4, "y", va=.55, door_side="s")                          # the bouleuterion
    peristyle(23.0, 18.4, 35.4, 35.2, (4.0, 3.0, 3.0, 3.0), 3.6, 2.7, door_side="s", va=.6, floor="paving:#d6cdb8")       # the prytaneion, with the city's hearth
    T = box(-35.3, 18.4, -5.0, 35.3); zt_ = land.pad(T, None, blend=.5); land.take(T); land.paint("earth", T, .9, 1.0)
    for a, b in zip(T, T[1:] + T[:1]):
        if a[0] == b[0] and a[0] > -6:                                                    # the precinct's wall, open to the avenue through a small gate
            houses.court_wall(a, (a[0], 24.5), zt_, 2.4, "plaster:#ece5d5", dict(va=.4, vb=.05), "tile", .3); houses.court_wall((a[0], 28.5), b, zt_, 2.4, "plaster:#ece5d5", dict(va=.4, vb=.05), "tile", .3)
        else: houses.court_wall(a, b, zt_, 2.4, "plaster:#ece5d5", dict(va=.4, vb=.05), "tile", .3)
    for yy in (24.5, 28.5): boxr("marble:#e6dfcf", "marble:#e6dfcf", -5.0, yy, .6, .6, zt_, zt_ + 3.0)
    prism("marble:#e6dfcf", "marble:#e6dfcf", box(-5.4, 24.2, -4.6, 28.8), zt_ + 3.0, zt_ + 3.5)
    temple(-24.5, 26.6, 90, 8.2, 14.5, 5.0, 4, 6, "ionic", zt_, peripteral=False, blend=0)       # prostyle, facing east to its altar
    inst(props.ALTAR, -11.5, 26.6, zt_, math.pi / 2, .5); land.paint("pave", box(-17, 23.5, -5.5, 29.7), 1.0, .8)
    for x, y in ((-9, 21), (-9, 32.5), (-14, 33)): inst(g.choice((props.STATUE_M, props.STELE)), x, y, zt_, -math.pi / 2)
    houses.TREES.append((-30, 21.5, zt_, "cypress")); houses.TREES.append((-18, 33, zt_, "cypress")); houses.TREES.append((-12, 20.5, zt_, "olive"))

def gymnasium(g):
    """The palaistra by the south gate: rooms round a sanded court for wrestling, a washroom, the hall where the young are taught."""
    z0, court = peristyle(4.6, -70.6, 35.0, -41.2, (6.2, 4.4, 4.2, 5.0), 3.9, 3.3, door_side="w", va=.2, exedra="n")
    for x, y in ((court[0] + 2, court[1] + 2), (court[2] - 2, court[3] - 2)): inst(props.HERM, x, y, z0)
    inst(props.BENCH, (court[0] + court[2]) / 2, court[1] + 1.0, z0)
    cx, cy = (court[0] + court[2]) / 2 - .5, (court[1] + court[3]) / 2 + 1.0
    land.paint("sand", box(cx - 3.0, cy - 1.5, cx + 3.0, cy + 1.5), 1.0, .4)
    for y in (-53.0, -55.8): inst(props.BASIN, court[0] + 1.2, y, z0 + .02)
    for k in range(4): inst(props.HERM, 15.0 + k * 2.6, court[3] - 1.7, z0 + .02)

def build(g):
    if land.HILL: theatre(g)
    agora(g); north_quarter(g); gymnasium(g)
