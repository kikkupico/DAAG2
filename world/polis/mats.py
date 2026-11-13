"""The materials, made the first time each is asked for. A key is "kind" or "kind:#rrggbb" (the same kind in another colour).

What the faces carry for them: UVs in metres (along a wall and up it; along a roof's eave and up its slope), `va` (a random
number per building or part) and `vb` (a kind-specific amount: how decayed a wall is, whether a roof face is a cover tile)."""
import bpy
from . import core
from .core import lin
from .sh import Sh

MATS = {}
def mat(key):
    if key in MATS: return MATS[key]
    kind, _, par = key.partition(":")
    MATS[key] = MAKERS.get(kind, m_flat)(key, par); return MATS[key]
core.MATERIAL[0] = mat
def col_of(par, default): return lin(par if par.startswith("#") else default)

def m_flat(key, par):
    s = Sh(key); c = col_of(par, "#808080")
    n = s.noise(9, 4, .6)
    return s.surface(s.bsdf(s.mix(s.rng(n, .3, .7, 0, .25), c, tuple(x * .7 for x in c)), .8, s.bump(n, .2, .05)))

def m_plaster(key, par):
    """Lime plaster over mud brick on a rubble footing: whitewash gone patchy, splashed and stained low down, streaked under
    the eaves, fallen away in places to show the brick."""
    s = Sh(key); base = col_of(par, "#e8dfca"); va = s.attr("va"); vb = s.attr("vb"); u, v, _ = s.xyz(s.uv)
    tone = s.ramp(va, [(0, tuple(c * .86 for c in base)), (.35, base), (.7, tuple(min(1, c * 1.06) for c in base)), (1, (base[0] * .97, base[1] * .9, base[2] * .78))])
    tx = s.tex2("white_plaster_rough_01", 2.6, box=True)
    col = s.tint(tx, "white_plaster_rough_01", (1, 1, 1)); col = s.mix(1.0, tone, col, "MULTIPLY", clamp=False)
    blotch = s.noise(.55, 5, .65, w=s.mul(va, 31.0))
    col = s.mix(s.rng(blotch, .5, .8, 0, .22), col, s.mix(1.0, col, (.82, .76, .64), "MULTIPLY"))                       # old repairs and sun-yellowed patches
    streak = s.noise(1.0, 4, .7, vec=s.mapping(s.pos, (2.8, 2.8, .16)))
    col = s.mix(s.mul(s.rng(streak, .5, .8), .2), col, s.mix(1.0, col, (.6, .55, .47), "MULTIPLY"))                    # rain streaks
    splash = s.mul(s.rng(s.madd(s.sub(s.noise(1.6, 3, .6, w=2.0), .5), 1.0, v), 1.5, .25), .42)
    col = s.mix(splash, col, s.mix(1.0, col, (.74, .62, .46), "MULTIPLY"))                                             # mud splashed up from the street
    brick_c, brick_f = s.brick(s.uv, .5, .12, .012, lin("#a37c58"), lin("#8a6546"), lin("#6f5440"))
    gone = s.rng(s.madd(vb, .55, s.madd(s.rng(v, 2.2, .3), .16, s.noise(.42, 5, .7, w=s.mul(va, 17.0), distort=.6))), .73, .77)
    col = s.mix(gone, col, brick_c)
    foot = s.rng(s.madd(s.sub(s.noise(2.2, 3, .6, w=7.0), .5), .5, v), .62, .54)                                         # the stone footing
    rub = s.tint(s.tex("old_stone_wall", 2.4, box=True), "old_stone_wall", lin("#a89d86"), raw=.3)
    col = s.mix(foot, col, rub)
    h = s.add(s.mul(s.lum(tx), .6), s.mul(s.maxf(gone, foot), -.5))
    return s.surface(s.bsdf(col, .9, s.bump(h, .35, .06)))

def m_ashlar(key, par):
    """Coursed blocks of local limestone: each block its own shade, drafted joints, stained under the wall-head, lichen."""
    s = Sh(key); base = col_of(par, "#cfc4a8"); va = s.attr("va"); u, v, _ = s.xyz(s.uv); v = s.sub(v, s.attr("vb"))
    c1 = tuple(c * 1.1 for c in base); c2 = (base[0] * .8, base[1] * .78, base[2] * .74)
    bc, bf = s.brick(s.uv, 1.15, .46, .018, c1, c2, tuple(c * .42 for c in base), smooth=.3)
    grain = s.tex2("marble_cliff_05", 6, box=True); col = s.mix(1.0, bc, s.tint(grain, "marble_cliff_05", (1, 1, 1)), "MULTIPLY", clamp=False)
    col = s.mix(s.rng(s.noise(.12, 4, .6, w=s.mul(va, 9.0)), .45, .75, 0, .3), col, s.mix(1.0, col, (.95, .82, .62), "MULTIPLY"))   # ochre weathering in broad washes
    streak = s.noise(.9, 4, .7, vec=s.mapping(s.pos, (2.2, 2.2, .12)))
    col = s.mix(s.mul(s.rng(streak, .48, .78), .3), col, s.mix(1.0, col, (.5, .48, .44), "MULTIPLY"))
    lichen = s.rng(s.noise(2.6, 3, .7, w=4.2), .68, .8)
    col = s.mix(s.mul(lichen, .35), col, lin("#8d8a6a"))
    col = s.mix(s.rng(v, 1.1, .0, 0, .3), col, s.mix(1.0, col, (.66, .6, .5), "MULTIPLY"))                              # damp and dirt at the foot
    return s.surface(s.bsdf(col, .88, s.bump(s.add(s.mul(bf, -1.0), s.mul(s.lum(grain), .5)), .5, .05)))

def m_rubble(key, par):
    """Field stone laid in clay: terrace and yard walls, footings."""
    s = Sh(key); base = col_of(par, "#b3a78e")
    tx = s.tex2("old_stone_wall", 2.6, box=True); col = s.tint(tx, "old_stone_wall", base, raw=.3)
    col = s.mix(s.rng(s.noise(.2, 4, .6), .45, .75, 0, .25), col, s.mix(1.0, col, (.8, .74, .62), "MULTIPLY"))
    return s.surface(s.bsdf(col, .92, s.bump(s.lum(tx), .7, .08)))

def m_drystone(key, par):
    s = Sh(key); base = col_of(par, "#b9b1a0")
    tx = s.tex2("stacked_stone_wall", 1.8, box=True); col = s.tint(tx, "stacked_stone_wall", base, raw=.15, gain=.7)
    return s.surface(s.bsdf(col, .95, s.bump(s.lum(tx), .9, .08)))

def m_marble(key, par):
    """Dressed marble (or fine stucco over limestone): warm white, faintly veined, weathered in soft streaks."""
    s = Sh(key); base = col_of(par, "#efe9dc"); va = s.attr("va")
    vein = s.noise(1.1, 6, .7, distort=1.8); col = s.mix(s.rng(vein, .52, .62, 0, .16), base, tuple(c * .8 for c in base))
    streak = s.noise(.8, 4, .7, vec=s.mapping(s.pos, (2.4, 2.4, .14)))
    col = s.mix(s.mul(s.rng(streak, .5, .8), .16), col, s.mix(1.0, col, (.72, .66, .55), "MULTIPLY"))
    col = s.mix(s.rng(s.noise(.1, 3, .6, w=s.mul(va, 5.0)), .4, .8, 0, .14), col, s.mix(1.0, col, (.97, .9, .76), "MULTIPLY"))
    return s.surface(s.bsdf(col, .5, s.bump(s.noise(22, 3, .6), .08, .02)))

def m_paving(key, par):
    """Weathered stone flags: uneven joints, swept dust, lichen, and worn relief across courts and stylobates."""
    s = Sh(key); base = col_of(par, "#cdc3ac")
    tx = s.tex2("stone_tiles_02", 7.0); tx2 = s.tex2("large_floor_tiles_02", 6.8)
    c_poly = s.tint(tx, "stone_tiles_02", base, raw=.3, gain=1.7)
    c_slab = s.tint(tx2, "large_floor_tiles_02", base, raw=.25, gain=1.45)
    col = s.mix(s.rng(s.noise(.22, 3, .6, w=2.3), .35, .65), c_poly, c_slab)
    p_warp = s.mixv(.12, s.pos, s.noise(1.1, 3, .6, out="Color"))
    bc, bf = s.brick(p_warp, 2.4, 1.8, .065, tuple(min(1, c * 1.08) for c in base), tuple(c * .84 for c in base), tuple(c * .58 for c in base), smooth=.35)
    col = s.mix(.48, col, s.mix(1.0, col, bc, "MULTIPLY", clamp=False))
    dust = s.tint(s.tex2("dry_ground_rocks", 7.5), "dry_ground_rocks", tuple(c * .86 for c in base), raw=.4)
    col = s.mix(s.rng(s.noise(.18, 4, .65, w=3.1), .45, .72, 0, .55), col, dust)
    col = s.mix(s.rng(s.noise(.25, 4, .6), .42, .74, 0, .35), col, s.mix(1.0, col, (.76, .7, .58), "MULTIPLY"))
    moss = s.rng(s.noise(1.2, 4, .7, w=7.2), .60, .78, 0, .35)
    col = s.mix(moss, col, lin("#878664"))
    h = s.add(s.add(s.mul(s.lum(tx), .45), s.mul(s.lum(tx2), .35)), s.add(s.mul(bf, -.6), s.add(s.mul(s.noise(.55, 4, .7), .45), s.mul(s.noise(1.8, 4, .75), .35))))
    return s.surface(s.bsdf(col, .9, s.bump(h, .95, .24)))

def m_tile(key, par):
    """Fired clay roof tiles: every tile its own colour from the kiln, courses lapping, older roofs paler and greyer,
    patches of newer tiles, lichen and soot. UV: metres along the eave and up the slope; vb = 1 on the cover tiles."""
    s = Sh(key); base = col_of(par, "#ad7550"); va = s.attr("va"); vb = s.attr("vb"); u, v, _ = s.xyz(s.uv)
    c1 = (base[0] * 1.22, base[1] * 1.2, base[2] * 1.12); c2 = (base[0] * .66, base[1] * .62, base[2] * .62)
    bc, bf = s.brick(s.uv, .88, .5, .0, c1, c2, c2, offset=0.0, bias=-.1)
    age = s.ramp(va, [(0, (1.1, .98, .86)), (.25, (1, 1, 1)), (.5, (.94, .97, 1.0)), (.75, (.84, .87, .88)), (1, (.7, .72, .72))])       # from new-fired to old and grey
    col = s.mix(1.0, bc, age, "MULTIPLY", clamp=False)
    col = s.hsv(col, s.rng(s.math("FRACT", s.mul(va, 7.31)), 0, 1, .492, .512), s.rng(s.math("FRACT", s.mul(va, 3.77)), 0, 1, .8, 1.08), 1.0)
    pale = tuple(min(1, c) for c in (base[0] * 1.22, base[1] * 1.32, base[2] * 1.3))
    col = s.mix(s.rng(s.madd(va, .3, s.noise(.4, 4, .65, w=s.mul(va, 23.0))), .6, .92, 0, .55), col, pale)                    # sun-bleached stretches
    col = s.mix(s.rng(s.noise(.8, 3, .7, w=s.mul(va, 13.0)), .66, .76, 0, .55), col, tuple(c * 1.1 for c in c1))               # a patch of new tiles
    grime = s.noise(1.1, 5, .7, w=3.1)
    col = s.mix(s.rng(grime, .52, .8, 0, .5), col, lin("#6b6252"))                                                             # lichen and soot
    col = s.mix(s.rng(s.noise(.07, 3, .6, w=1.0), .4, .7, 0, .18), col, lin("#7d7466"))
    lap = s.rng(s.math("FRACT", s.mul(v, 2.0)), .0, .16, .5, 1.0)                                                              # the shadow where a course laps the one below
    col = s.mix(s.mul(s.sub(1.0, lap), s.sub(1.0, vb)), col, s.mix(1.0, col, (.45, .4, .38), "MULTIPLY"))
    col = s.mix(s.mul(vb, .16), col, s.mix(1.0, col, (1.2, 1.18, 1.14), "MULTIPLY", clamp=False))
    return s.surface(s.bsdf(col, .85, s.bump(s.add(s.mul(lap, .6), s.mul(s.noise(14, 2, .5), .4)), .3, .04)))

def m_wood(key, par):
    s = Sh(key); base = col_of(par, "#7d5d3c")
    tx = s.tex("brown_planks_09", 1.6, box=True); col = s.tint(tx, "brown_planks_09", base, raw=.2)
    col = s.mix(s.rng(s.noise(.6, 3, .6), .4, .8, 0, .3), col, s.mix(1.0, col, (.72, .72, .7), "MULTIPLY"))
    return s.surface(s.bsdf(col, .85, s.bump(s.lum(tx), .5, .03)))

def m_clay(key, par):
    s = Sh(key); base = col_of(par, "#b06a42"); n = s.noise(5, 4, .6); r = s.objinfo()
    col = s.mix(s.rng(n, .3, .7, 0, .3), base, tuple(c * .72 for c in base)); col = s.hsv(col, s.rng(r, 0, 1, .485, .515), 1.0, s.rng(r, 0, 1, .8, 1.15))
    return s.surface(s.bsdf(col, .7, s.bump(n, .2, .03)))

def m_cloth(key, par):
    """Awnings and sails: undyed or madder- and woad-dyed wool and linen, sun-faded, faintly striped."""
    s = Sh(key); base = col_of(par, "#d8cdb2"); u, v, _ = s.xyz(s.uv)
    stripe = s.rng(s.math("SINE", s.mul(u, 9.0)), .7, .9, 0, .18)
    col = s.mix(stripe, base, tuple(c * .7 for c in base)); n = s.noise(3, 4, .6)
    col = s.mix(s.rng(n, .35, .75, 0, .22), col, tuple(min(1, c * 1.15 + .05) for c in base))
    return s.surface(s.bsdf(col, .95, s.bump(s.noise(60, 2, .5), .15, .01), Sheen_Weight=.3))

def m_straw(key, par):
    s = Sh(key); base = col_of(par, "#cdb168"); n = s.noise(6, 5, .7, vec=s.mapping(s.pos, (1, 1, .25)))
    col = s.mix(s.rng(n, .3, .75), tuple(c * .62 for c in base), tuple(min(1, c * 1.12) for c in base))
    return s.surface(s.bsdf(col, .95, s.bump(n, .7, .1)))

def m_bronze(key, par):
    s = Sh(key); n = s.noise(4, 4, .6)
    col = s.mix(s.rng(n, .4, .7), lin("#6a5536"), lin("#4f6a55"))
    return s.surface(s.bsdf(col, .45, None, Metallic=.85))

def m_gold(key, par):
    """Gilded bronze: warm gold leaf for akroteria, finials, and votive shields."""
    s = Sh(key); c = col_of(par, "#d4a843"); n = s.noise(6, 3, .5)
    col = s.mix(s.rng(n, .35, .65, 0, .2), c, tuple(x * .78 for x in c))
    return s.surface(s.bsdf(col, .28, None, Metallic=.95))

def m_pool(key, par):
    """Still water in a tank, a cistern mouth, a fountain basin."""
    s = Sh(key); c = col_of(par, "#39686a")
    return s.surface(s.bsdf(c, .06, s.bump(s.noise(3, 3, .5), .05, .05)))

def m_dark(key, par):
    """The dark of a doorway or a window."""
    s = Sh(key); return s.surface(s.bsdf(col_of(par, "#1c1712"), .9))

def m_earth(key, par):
    """Packed earth: house courts, yards."""
    s = Sh(key); base = col_of(par, "#c0a57c")
    tx = s.tex2("dirt_aerial_03", 9); col = s.tint(tx, "dirt_aerial_03", base, raw=.2)
    return s.surface(s.bsdf(col, .95, s.bump(s.lum(tx), .4, .05)))

def m_emit(key, par):
    s = Sh(key); return s.surface(s.emission(col_of(par, "#ffbe5c"), float(core.opt("--glow", 9))))

def m_frieze(key, par):
    """A Doric frieze: triglyphs painted blue-black between pale metopes, a red band below."""
    s = Sh(key); u, v, _ = s.xyz(s.uv)
    tri = s.rng(s.math("ABSOLUTE", s.sub(s.math("FRACT", s.mul(u, 1 / 1.1)), .5)), .17, .2)
    col = s.mix(tri, lin("#2b3c5c"), lin("#ebe4d4"))
    return s.surface(s.bsdf(col, .6))

def m_net(key, par):
    """A net hung to dry: a dark mesh you half see through."""
    s = Sh(key); return s.surface(s.bsdf(col_of(par, "#4a3a2a"), .9, None, Alpha=.5))

def m_leaf(key, par):
    """Foliage: every leaf card its own shade, darker inside the crown, light passing through at the edges."""
    s = Sh(key); base = col_of(par, "#5f7a38"); va = s.attr("va"); vb = s.attr("vb")
    col = s.ramp(va, [(0, tuple(c * .55 for c in base)), (.5, base), (1, (min(1, base[0] * 1.35), min(1, base[1] * 1.28), base[2] * 1.05))])
    col = s.mix(s.rng(vb, .95, .35, 0, .45), col, tuple(c * .45 for c in base))
    d = s.bsdf(col, .55, None, Specular_IOR_Level=.3); t = s.node("ShaderNodeBsdfTranslucent"); s.set(t.inputs[0], s.mix(1.0, col, (1.3, 1.25, .7), "MULTIPLY", clamp=False))
    return s.surface(s.mix_shader(.28, d, t.outputs[0]))
def m_bark(key, par):
    s = Sh(key); base = col_of(par, "#6a5a48"); n = s.noise(9, 5, .7, vec=s.mapping(s.pos, (1, 1, .2)))
    return s.surface(s.bsdf(s.mix(s.rng(n, .3, .7), tuple(c * .6 for c in base), tuple(min(1, c * 1.2) for c in base)), .9, s.bump(n, .6, .03)))

def m_glow(key, par):
    """Lamplight seen through a window or a doorway."""
    s = Sh(key); return s.surface(s.emission(col_of(par, "#ffb055"), float(core.opt("--lamp", 5))))
def m_fire(key, par):
    """Flame: brightest at its heart."""
    s = Sh(key); n = s.noise(3.5, 3, .6)
    return s.surface(s.emission(s.mix(s.rng(n, .35, .7), lin("#ff6a1a"), lin("#ffd27a")), float(core.opt("--glow", 40))))

def m_canvas(key, par):
    """Tent cloth and raw hides: weathered, stained, lighter along the folds."""
    s = Sh(key); base = col_of(par, "#c9bb9b"); n = s.noise(1.6, 5, .65); f = s.noise(7, 3, .6)
    col = s.mix(s.rng(n, .3, .75), tuple(c * .7 for c in base), tuple(min(1, c * 1.12) for c in base)); col = s.mix(s.rng(f, .5, .8, 0, .2), col, tuple(c * .55 for c in base))
    return s.surface(s.bsdf(col, .92, s.bump(s.add(n, s.mul(f, .4)), .35, .05)))

MAKERS = dict(canvas=m_canvas, glow=m_glow, fire=m_fire, frieze=m_frieze, net=m_net, leaf=m_leaf, bark=m_bark, flat=m_flat, plaster=m_plaster, ashlar=m_ashlar, rubble=m_rubble, drystone=m_drystone, marble=m_marble, paving=m_paving,
              tile=m_tile, wood=m_wood, clay=m_clay, cloth=m_cloth, straw=m_straw, bronze=m_bronze, gold=m_gold, pool=m_pool, dark=m_dark, earth=m_earth,
              emit=m_emit, paint=m_flat)
