"""Light, sky, the renderer's settings, and the check that every walker stands on the ground and can be seen."""
import bpy, json, math, os
from mathutils import Vector
from . import core, land
from .core import S, scene, ROOT, opt, flag, ASSETS, OUT, TOWARD

def setup():
    el = math.radians(float(opt("--sun-el", 34))); az = math.radians(float(opt("--sun-az", 56.5)))    # light travels toward this bearing (degrees from east): from the south-west
    sx, sy = math.cos(az), math.sin(az)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); ROOT.objects.link(sun)
    sun.rotation_euler = Vector((sx * math.cos(el), sy * math.cos(el), -math.sin(el))).to_track_quat("-Z", "Y").to_euler()
    sun.data.energy = float(opt("--sun", 6.0)); sun.data.color = tuple(float(c) for c in opt("--sun-col", "1,.91,.77").split(",")); sun.data.angle = math.radians(1.2)
    if core.NIGHT:                                                                        # a clear night under the moon: blue light, soft-edged shadows
        sun.data.energy = float(opt("--moon", 2.4)); sun.data.color = tuple(float(c) for c in opt("--moon-col", ".22,.42,1.0").split(",")); sun.data.angle = math.radians(2.0)
    world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True; wt = world.node_tree; bg = wt.nodes["Background"]
    name = opt("--hdri", "kloofendal_48d_partly_cloudy_puresky"); hdr = os.path.join(ASSETS, name, name + "_2k.hdr")
    env = wt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(hdr)
    # The sky image has its own sun, 145.8 degrees round from east; it is turned to stand where the lamp's sun stands, then clipped
    # out of the picture (the lamp is the sun), leaving the sky's glow brightest on the sun's side.
    mp = wt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(float(opt("--hdri-rot", (math.degrees(az) + 180) - 145.8)))); tc = wt.nodes.new("ShaderNodeTexCoord")
    wt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); wt.links.new(mp.outputs[0], env.inputs["Vector"])
    cl = wt.nodes.new("ShaderNodeVectorMath"); cl.operation = "MINIMUM"; cl.inputs[1].default_value = (float(opt("--sky-clip", 6)),) * 3
    wt.links.new(env.outputs["Color"], cl.inputs[0]); wt.links.new(cl.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = float(opt("--sky", .45))
    if core.NIGHT:
        nb = wt.nodes.new("ShaderNodeMix"); nb.data_type = "RGBA"; nb.blend_type = "MULTIPLY"; nb.inputs[0].default_value = 1; nb.inputs[7].default_value = (.24, .40, 1.0, 1)
        wt.links.new(cl.outputs[0], nb.inputs[6]); wt.links.new(nb.outputs[2], bg.inputs[0]); bg.inputs[1].default_value = float(opt("--sky", .2))
    scene.render.engine = "CYCLES"; scene.cycles.samples = core.SAMPLES; scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6; scene.cycles.transparent_max_bounces = 24; scene.cycles.diffuse_bounces = 3
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences; prefs.compute_device_type = "METAL"; prefs.get_devices()
        for dev in prefs.devices: dev.use = True
        scene.cycles.device = "GPU"
    except Exception as ex: print("GPU not enabled:", ex)
    scene.view_settings.view_transform = opt("--view", "AgX")
    try: scene.view_settings.look = opt("--look", "AgX - Punchy")
    except Exception as ex: print("look not set:", ex)
    scene.view_settings.exposure = float(opt("--exposure", 1.3 if core.NIGHT else .7))
    if not flag("--no-grade"): grade()
    if flag("--border"):
        x0, y0, x1, y1 = map(float, opt("--border").split(",")); r = scene.render
        r.use_border = True; r.use_crop_to_border = True; r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = x0, x1, 1 - y1, 1 - y0
    scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"; scene.render.filepath = OUT

def grade():
    """The picture's finish: shade gathered where things meet (the occlusion pass, multiplied in), richer colour, and a gentle
    S-curve on the finished tones."""
    N_ = core.NIGHT; ao, sat, con = float(opt("--ao", .5 if N_ else .45)), float(opt("--sat", 1.3 if N_ else 1.15)), float(opt("--contrast", .6 if N_ else .5))
    bloom = float(opt("--bloom", 1.0 if N_ else 0))                                         # by night, a soft halo round every flame and lamp
    ng = bpy.data.node_groups.new("grade", "CompositorNodeTree"); ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    N, L = ng.nodes.new, ng.links.new; rl = N("CompositorNodeRLayers"); out = N("NodeGroupOutput"); img = rl.outputs["Image"]
    if ao > 0:
        bpy.context.view_layer.use_pass_ambient_occlusion = True; scene.world.light_settings.distance = float(opt("--ao-dist", 2.5))
        dn = N("CompositorNodeDenoise"); L(rl.outputs["Ambient Occlusion"], dn.inputs["Image"])
        mx = N("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = ao
        L(img, mx.inputs[6]); L(dn.outputs["Image"], mx.inputs[7]); img = mx.outputs[2]
    hs = N("CompositorNodeHueSat"); hs.inputs["Saturation"].default_value = sat; L(img, hs.inputs["Image"]); img = hs.outputs["Image"]
    if bloom > 0:
        gl = N("CompositorNodeGlare"); gl.inputs["Type"].default_value = "Bloom"; gl.inputs["Threshold"].default_value = float(opt("--bloom-at", 1.5))
        gl.inputs["Strength"].default_value = bloom; gl.inputs["Size"].default_value = float(opt("--bloom-size", .45)); L(img, gl.inputs["Image"]); img = gl.outputs["Image"]
    L(img, out.inputs[0])
    scene.compositing_node_group = ng; scene.render.use_compositing = True
    if con > 0:                                                                           # on the displayed tones: darks a little deeper, lights a little brighter
        vs = scene.view_settings; vs.use_curve_mapping = True; c = vs.curve_mapping.curves[3]
        c.points.new(.25, .25 - .07 * con); c.points.new(.75, .75 + .06 * con); vs.curve_mapping.update()

def check():
    """Every route sample, at this build's own height: is the ground there, and can the camera see a walker on it?"""
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    pts = sorted({(p[0], p[1]) for r in S["routes"] for p in r}); heights = {}; off, hidden = [], []
    for x, y in pts:
        z, d = land.zroute(x, y); heights["%g,%g" % (x, y)] = round(z, 3)
        if d > .6: off.append((x, y, "no road within %.1f m" % d)); continue
        hit, loc, *_ = scene.ray_cast(dg, Vector((x, y, z + 1.9)), Vector((0, 0, -1)))
        if not hit or abs(loc.z - z) > .3: off.append((x, y, round(z, 2), round(loc.z, 2) if hit else None, _[2].name if hit else None))
        p = Vector((x, y, z + .9)); hit, loc, *_ = scene.ray_cast(dg, p + TOWARD * 500, -TOWARD)
        if hit and (loc - p).length > 1.6: hidden.append((x, y, round(z, 2), _[2].name))
    print("ROUTE CHECK: %d samples; %d not on the ground at their height; %d hidden from the camera" % (len(pts), len(off), len(hidden)))
    for b in off[:20]: print("  off the ground:", b)
    by = {}
    for h in hidden: by[h[3]] = by.get(h[3], 0) + 1
    print("  hidden by:", sorted(by.items(), key=lambda kv: -kv[1])[:12])
    base = OUT.rsplit(".", 1)[0]
    places = {k: dict(at=v["at"], door=v["door"], zdoor=round(land.zroute(*v["door"])[0], 3)) for k, v in S["places"].items()}
    json.dump(dict(top=land.TOP, heights=heights, places=places, off=off, hidden=hidden), open(base + "-heights.json", "w"))

def render():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if flag("--save"): bpy.ops.wm.save_as_mainfile(filepath=OUT.rsplit(".", 1)[0] + ".blend")
    if not flag("--no-render"): bpy.ops.render.render(write_still=True); print("WROTE", OUT)
