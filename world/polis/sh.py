"""A small vocabulary for building shader node trees in a few lines each."""
import bpy, os
import numpy as np
from .core import ASSETS

IMAGES = {}
def image(path, cs="sRGB"):
    if path not in IMAGES:
        im = bpy.data.images.load(path); im.colorspace_settings.name = cs; IMAGES[path] = im
    return IMAGES[path]
AVG = {}
def avg_colour(name):
    """A downloaded texture's mean colour (linear), so its light and dark can be laid over another colour."""
    if name not in AVG:
        im = image(os.path.join(ASSETS, name, "Diffuse.jpg")); a = np.empty(len(im.pixels), dtype=np.float32); im.pixels.foreach_get(a)
        a = a.reshape(-1, 4)[::11, :3]; a = np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)      # the file's values are sRGB; the shader's are linear
        AVG[name] = tuple(float(c) for c in a.mean(0))
    return AVG[name]

class Sh:
    def __init__(s, name):
        s.m = bpy.data.materials.new(name); s.m.use_nodes = True; s.nt = s.m.node_tree
        for n in list(s.nt.nodes): s.nt.nodes.remove(n)
        s.out = s.nt.nodes.new("ShaderNodeOutputMaterial"); s._pos = s._uv = None
    # -- plumbing
    def node(s, t, **kw):
        n = s.nt.nodes.new(t)
        for k, v in kw.items(): setattr(n, k, v)
        return n
    def set(s, inp, v):
        if v is None: return
        if isinstance(v, bpy.types.NodeSocket): s.nt.links.new(v, inp); return
        dv = inp.default_value
        if hasattr(dv, "__len__"):
            if not hasattr(v, "__len__"): v = (v,) * len(dv)
            elif len(v) == 3 and len(dv) == 4: v = (*v, 1.0)
        inp.default_value = v
    # -- inputs
    @property
    def pos(s):
        if s._pos is None: s._pos = s.node("ShaderNodeNewGeometry").outputs["Position"]
        return s._pos
    @property
    def uv(s):
        if s._uv is None: s._uv = s.node("ShaderNodeUVMap").outputs[0]
        return s._uv
    def attr(s, name, out="Fac"): return s.node("ShaderNodeAttribute", attribute_name=name).outputs[out]
    def geo(s, out): return s.node("ShaderNodeNewGeometry").outputs[out]
    def objinfo(s, out="Random"): return s.node("ShaderNodeObjectInfo").outputs[out]
    # -- vectors
    def xyz(s, v):
        n = s.node("ShaderNodeSeparateXYZ"); s.set(n.inputs[0], v); return n.outputs
    def vec(s, x=0.0, y=0.0, z=0.0):
        n = s.node("ShaderNodeCombineXYZ")
        for i, v in zip(n.inputs, (x, y, z)): s.set(i, v)
        return n.outputs[0]
    def mapping(s, v, scale=1.0, loc=(0, 0, 0), rot=(0, 0, 0)):
        n = s.node("ShaderNodeMapping"); s.set(n.inputs["Vector"], v); s.set(n.inputs["Scale"], scale); s.set(n.inputs["Location"], loc); s.set(n.inputs["Rotation"], rot)
        return n.outputs[0]
    def vmath(s, op, a, b=None):
        n = s.node("ShaderNodeVectorMath", operation=op); s.set(n.inputs[0], a)
        if b is not None: s.set(n.inputs[1], b)
        return n.outputs["Value" if op in ("LENGTH", "DOT_PRODUCT", "DISTANCE") else "Vector"]
    # -- numbers
    def math(s, op, a, b=None, c=None, clamp=False):
        n = s.node("ShaderNodeMath", operation=op, use_clamp=clamp); s.set(n.inputs[0], a)
        if b is not None: s.set(n.inputs[1], b)
        if c is not None: s.set(n.inputs[2], c)
        return n.outputs[0]
    def add(s, a, b): return s.math("ADD", a, b)
    def sub(s, a, b): return s.math("SUBTRACT", a, b)
    def mul(s, a, b): return s.math("MULTIPLY", a, b)
    def madd(s, a, k, b): return s.math("MULTIPLY_ADD", a, k, b)
    def sat(s, a): return s.math("ADD", a, 0.0, clamp=True)
    def maxf(s, a, b): return s.math("MAXIMUM", a, b)
    def minf(s, a, b): return s.math("MINIMUM", a, b)
    def rng(s, v, a, b, lo=0.0, hi=1.0, smooth=False):
        """v mapped from a..b to lo..hi, clamped."""
        n = s.node("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP" if smooth else "LINEAR")
        s.set(n.inputs[0], v)
        for i, x in zip(n.inputs[1:5], (a, b, lo, hi)): s.set(i, x)
        return n.outputs[0]
    def lum(s, c):
        n = s.node("ShaderNodeRGBToBW"); s.set(n.inputs[0], c); return n.outputs[0]
    # -- colours
    def mix(s, f, a, b, blend="MIX", clamp=True):
        n = s.node("ShaderNodeMix", data_type="RGBA", blend_type=blend, clamp_result=clamp, clamp_factor=True)
        s.set(n.inputs[0], f); s.set(n.inputs[6], a); s.set(n.inputs[7], b); return n.outputs[2]
    def mixf(s, f, a, b):
        n = s.node("ShaderNodeMix", data_type="FLOAT"); s.set(n.inputs[0], f); s.set(n.inputs[2], a); s.set(n.inputs[3], b); return n.outputs[0]
    def mixv(s, f, a, b):
        n = s.node("ShaderNodeMix", data_type="VECTOR"); s.set(n.inputs[0], f); s.set(n.inputs[4], a); s.set(n.inputs[5], b); return n.outputs[1]
    def ramp(s, v, stops, interp="LINEAR"):
        """A colour ramp: stops are (position, colour) pairs; colours are 3-tuples or greys."""
        n = s.node("ShaderNodeValToRGB"); cr = n.color_ramp; cr.interpolation = interp
        while len(cr.elements) < len(stops): cr.elements.new(.5)
        for e, (p, c) in zip(cr.elements, stops):
            e.position = p; e.color = (c, c, c, 1) if not hasattr(c, "__len__") else (*c[:3], 1)
        s.set(n.inputs[0], v); return n.outputs[0]
    def hsv(s, c, h=.5, sat=1.0, val=1.0):
        n = s.node("ShaderNodeHueSaturation"); s.set(n.inputs["Color"], c); s.set(n.inputs["Hue"], h); s.set(n.inputs["Saturation"], sat); s.set(n.inputs["Value"], val)
        return n.outputs[0]
    def bright(s, c, k):
        """A colour times a number."""
        n = s.node("ShaderNodeVectorMath", operation="SCALE"); s.set(n.inputs[0], c); s.set(n.inputs["Scale"], k); return n.outputs[0]
    # -- textures
    def noise(s, scale, detail=4.0, rough=.6, vec=None, w=None, out="Factor", distort=0.0, lac=2.0):
        n = s.node("ShaderNodeTexNoise", noise_dimensions="4D" if w is not None else "3D")
        s.set(n.inputs["Vector"], s.pos if vec is None else vec); s.set(n.inputs["Scale"], scale); s.set(n.inputs["Detail"], detail)
        s.set(n.inputs["Roughness"], rough); s.set(n.inputs["Distortion"], distort); s.set(n.inputs["Lacunarity"], lac)
        if w is not None: s.set(n.inputs["W"], w)
        return n.outputs[out]
    def voronoi(s, scale, vec=None, out="Distance", feature="F1", rand=1.0, dims="3D"):
        n = s.node("ShaderNodeTexVoronoi", feature=feature, voronoi_dimensions=dims)
        s.set(n.inputs["Vector"], s.pos if vec is None else vec); s.set(n.inputs["Scale"], scale); s.set(n.inputs["Randomness"], rand); return n.outputs[out]
    def white(s, vec):
        n = s.node("ShaderNodeTexWhiteNoise", noise_dimensions="3D"); s.set(n.inputs["Vector"], vec); return n.outputs
    def brick(s, vec, w, h, mortar=.02, c1=(.8, .8, .8), c2=(.4, .4, .4), cm=(0, 0, 0), offset=.5, bias=0.0, smooth=.1, squash=1.0, freq=2):
        """A wall of blocks w x h (in the vector's units): returns (colour, mortar factor)."""
        n = s.node("ShaderNodeTexBrick", offset=offset, squash=squash, squash_frequency=freq); s.set(n.inputs["Vector"], vec)
        s.set(n.inputs["Color1"], c1); s.set(n.inputs["Color2"], c2); s.set(n.inputs["Mortar"], cm); s.set(n.inputs["Scale"], 1.0)
        s.set(n.inputs["Mortar Size"], mortar); s.set(n.inputs["Mortar Smooth"], smooth); s.set(n.inputs["Bias"], bias)
        s.set(n.inputs["Brick Width"], w); s.set(n.inputs["Row Height"], h); return n.outputs["Color"], n.outputs["Factor"]
    def wave(s, vec, scale, distortion=0.0, detail=2.0, dscale=1.0, kind="BANDS", direction="X", profile="SIN"):
        n = s.node("ShaderNodeTexWave", wave_type=kind, wave_profile=profile)
        if kind == "BANDS": n.bands_direction = direction
        s.set(n.inputs["Vector"], vec); s.set(n.inputs["Scale"], scale); s.set(n.inputs["Distortion"], distortion); s.set(n.inputs["Detail"], detail)
        s.set(n.inputs["Detail Scale"], dscale); return n.outputs["Fac"] if "Fac" in n.outputs else n.outputs[1]
    def img(s, im, vec, box=False, interp="Linear", ext="REPEAT"):
        n = s.node("ShaderNodeTexImage", image=im, interpolation=interp, extension=ext)
        if box: n.projection = "BOX"; n.projection_blend = .25
        s.set(n.inputs["Vector"], vec); return n.outputs["Color"]
    def tex(s, name, scale, vec=None, box=False, key="Diffuse", rot=0.0, loc=(.37, .71, .13)):
        """A downloaded texture laid over the world at `scale` metres a tile (flat from above, or box-projected for walls)."""
        cs = "sRGB" if key == "Diffuse" else "Non-Color"
        v = s.mapping(s.pos if vec is None else vec, 1 / scale, loc, (0, 0, rot))
        return s.img(image(os.path.join(ASSETS, name, key + ".jpg"), cs), v, box)
    def tex2(s, name, scale, box=False, vec=None):
        """The same, sampled twice at different scales and turns and mixed in patches, so its tiling does not show."""
        a = s.tex(name, scale, vec, box); b = s.tex(name, scale * 1.83, vec, box, rot=.9, loc=(.11, .53, .29))
        m = s.rng(s.noise(.9 / scale, 2.0, .5, vec=vec), .42, .58)
        return s.mix(m, a, b)
    def tint(s, col, name, rgb, raw=0.0, gain=1.0):
        """A texture's light and dark laid over a chosen colour (raw: how much of its own colour is kept)."""
        av = avg_colour(name); k = 1 / max(1e-3, .2126 * av[0] + .7152 * av[1] + .0722 * av[2])
        l = s.math("POWER", s.mul(s.lum(col), k), gain) if gain != 1.0 else s.mul(s.lum(col), k)
        t = s.mix(1.0, rgb, l, "MULTIPLY", clamp=False)
        return s.mix(raw, t, col) if raw else t
    def bump(s, h, strength=.5, dist=.1, normal=None):
        n = s.node("ShaderNodeBump"); s.set(n.inputs["Height"], h); s.set(n.inputs["Strength"], strength); s.set(n.inputs["Distance"], dist)
        if normal is not None: s.set(n.inputs["Normal"], normal)
        return n.outputs[0]
    # -- surfaces
    def bsdf(s, col, rough=.8, normal=None, **kw):
        b = s.node("ShaderNodeBsdfPrincipled"); s.set(b.inputs["Base Color"], col); s.set(b.inputs["Roughness"], rough)
        if normal is not None: s.set(b.inputs["Normal"], normal)
        for k, v in kw.items(): s.set(b.inputs[k.replace("_", " ")], v)
        return b.outputs[0]
    def emission(s, col, strength):
        n = s.node("ShaderNodeEmission"); s.set(n.inputs[0], col); s.set(n.inputs[1], strength); return n.outputs[0]
    def transparent(s): return s.node("ShaderNodeBsdfTransparent").outputs[0]
    def mix_shader(s, f, a, b):
        n = s.node("ShaderNodeMixShader"); s.set(n.inputs[0], f); s.nt.links.new(a, n.inputs[1]); s.nt.links.new(b, n.inputs[2]); return n.outputs[0]
    def surface(s, shader): s.nt.links.new(shader, s.out.inputs["Surface"]); return s.m
