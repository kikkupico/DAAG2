# Building the world in Blender

You write a Blender Python script that models the setting and renders it through the page's camera. The network comes
first and the world is built round it: wherever the network has a road, your world must have clear ground a person could
walk, because the couriers are drawn from the network, not from the picture.

A "road" in the network is only a path. It need not be a road in the world: under it put whatever the setting would have
there (a trodden track, a causeway, a strip of bare rock beside a wall, a corridor floor), or nothing but open ground. Do
not model literal roads of the network's shape and width, and do not shape camps, walls or towns to the diagram: make them
as irregular as real ones. The page draws the couriers' trails itself.

Needs `blender` on the path (4.x or 5.x). Write the network in plan units (`"units": "m"`): x east, y north, z up, origin
at the centre of the frame. Give road points a third number where the ground rises.

## The fixed part: `tools/blender_stage.py`

```python
import bpy, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), "tools"))
import blender_stage as stage

bpy.ops.wm.read_factory_settings(use_empty=True)
net = stage.network("allegories/<id>/city.json")
stage.camera(width=2400)                    # the page's camera. Never move, turn or rescale it.
guides = stage.roads(net)                   # a ribbon along every path: a guide for test renders, not part of the world

# ... your world: ground, water, landmarks at net["places"][k]["at"], everything between ...

stage.check(net)                            # which stretches of path can the camera not see?
for g in guides: bpy.data.objects.remove(g) # the final picture has no guide ribbons in it
stage.render("allegories/<id>/city.png")
```

Keep your script in `allegories/<id>/world/` and run it from the repository root:

```sh
blender -b --factory-startup -P allegories/<id>/world/city.py
python3 tools/allegory.py overlay <id> city
```

`trace` does not apply here: it looks for painted roads, and a path in a built world need not be one. `stage.check` and the
overlay are the tests.

`stage.project(x, y, z)` gives the picture pixel of a world point, and `python3 tools/allegory.py xy px2m 800 600` the
ground point under a pixel, for planning what falls where in the frame.

## What the frame shows

A square of ground 304 units on a side, standing on its corner: north `(0, 215)` is the upper right corner of the
picture, east `(215, 0)` the lower right, south `(0, -215)` the lower left, west `(-215, 0)` the upper left. Model the
ground well past that square (500 units each way) so no edge shows. A "unit" is a metre in the original town, which is
about 180 m across; scale your setting to fill the frame the same way, whatever its real size.

## Rules the picture must keep

- **Walkable ground where the network has a path.** Nothing stands on it, and the ground under it is at the path's `z`:
  if your terrain decides the heights, sample it along each path and write the heights back into the network file
  before you build. `stage.roads` draws the paths as ribbons so you can see them in test renders; remove them for the final one.
- **Paths visible.** The camera looks from the south-east and down, so anything tall just south-east of a road hides it.
  Keep tall buildings and trees on the far side (north-west) of a road, or set back by their own height. `stage.check`
  lists what hides what; a courier hidden for a step or two behind a low wall is fine, a hidden street is not.
- **Landmarks at their places.** The centre of each landmark's footprint is the place's `at`; its entrance faces its `door`.
  Make landmarks large and distinct enough to read at a glance at 900 px wide: they are what the name plates point at.
- **Zones.** `at` points still obey the seven zones, in the picture. A tall landmark draws upward from its `at`, so keep
  the top corners' landmarks low enough to stay in the frame.
- **The siege is by night.** Light it by the moon and by fires and lamps, set `"night": true`, and keep the roads readable
  against the dark ground.

## Working method

1. Guide ribbons and a flat ground only, low samples, small width (`stage.camera(width=800)`). Render, `overlay`, and confirm the
   magenta routes lie on the ribbons. This takes seconds and proves the frame.
2. Terrain and water. Fix the paths' heights now.
3. Landmarks, one per place, as simple masses first. Render and overlay again: rings on landmarks, doors touching them.
4. Everything between: lesser buildings, fields, walls, vegetation, props. Run `stage.check` after each addition that is tall.
5. Materials, light, and a final render at 2400 px wide or more, with enough samples to be clean.

Build everything parametrically in the script; nothing is modelled by hand. `world/polis/` is the original town's build
(a large one) if you want to see how far this goes: terrain, walls, houses, plants, a siege. You may borrow from it, but
do not edit it, and do not make your world a variation of it: a different setting wants its own plan.

Render outputs and `.blend` files are not committed. The picture named by `"picture"` is what `build` bakes into the page.
