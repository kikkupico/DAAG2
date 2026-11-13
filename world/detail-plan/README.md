# Polis detail pass: brief for the implementing agent

You are adding historically correct detail to an existing Blender model of a small Hellenistic Greek town ("Paxos"), built entirely by Python scripts.

**How to use this folder.** Read this file once. Then do **one phase file at a time**, in order. Do not read ahead: each phase file contains everything that phase needs. Finish a phase, run its checks, report, and only then open the next file.

| Order | File | Work |
|---|---|---|
| 0 | `phase-0-baseline.md` | Record the starting state |
| 1 | `phase-1-roofs-and-trees.md` | Roof tile relief, fuller tree crowns |
| 2 | `phase-2-town.md` | Agora market, palaistra |
| 3 | `phase-3-harbour.md` | Shore and harbour |
| 4 | `phase-4-granary.md` | The granary farm |
| 5 | `phase-5-pottery.md` | The potters' quarter |
| 6 | `phase-6-winery.md` | The winery and vineyards |
| 7 | `phase-7-wells-and-gardens.md` | Wells, kitchen gardens, orchard trees |
| 8 | `phase-8-gates.md` | Making the town gates stand out |
| 9 | `phase-9-optional.md` | Dry stream bed, salt works (only if all else is done) |
| 10 | `phase-10-final.md` | Final render and report |

## 1. Goal

The current render is accurate but sparse. The goal is a picture **densely filled with readable, period-correct things** for a Greek town of about 300–150 BC.

`world/reference/target-style.webp` is an AI repaint of our render. Use it **only** as a guide to how full the yards, shore and fields should feel. **Do not copy its layout or its objects**: it redrew the town and contains things that are wrong for the period (section 4).

**Lighting, colour grading and the colours of existing materials are out of scope.** They are being handled separately. Do not edit `render.py`, and do not retune the colours in `mats.py`, the ground, sea or leaf materials. Colours given in the phase files for **new** objects are part of the work.

The phases are ordered by how much each adds to the picture. A trial with an image generator showed what reads at this scale: **market stalls, sails and boats, heaps of grain, groups of pots, and strokes of strong colour** (dyed cloth, golden grain, orange and black pottery). Thin or small things (single posts, shrubs, boundary stones) did not read at all. When in doubt, make fewer, larger, more colourful groups.

**Loaded carts** appear in several phases. Carts stand **unhitched** (no animals): the pole resting on the ground or on a short prop. Build them once in `props.py` from the existing `_cart`: `CART_AMPH` (twelve amphorae standing upright in the bed, packed in a layer of straw), `CART_SACKS` (eight sacks, two high), `CART_HAY` (a rounded load of straw). Use them at 1.3 times the size so the load reads. A cart never stands on a road: put it in a yard or at least 3.5 m from a road's centre line.

## 2. How the build works

Run from the repository root (Blender 5.1 is installed as `blender`):

```
blender -b --factory-startup -P world/build_polis.py -- --scene world/build3d/city.json --out world/build3d/polis.png
    [--width 2400] [--samples 96] [--only a,b] [--skip plants] [--border x0,y0,x1,y1] [--no-render] [--save]
```

- `--no-render` builds everything and runs the route check without rendering. Use it as the fast test.
- `--border x0,y0,x1,y1` renders only a crop. The numbers are fractions of the frame, 0 to 1, with y measured from the top.
- To find where a world point lands in the picture: `core.project(x, y, z)` returns pixels in a 1600 x 1200 frame. Divide by 1600 and 1200 to get `--border` fractions.
- Quick preview: `--width 1600 --samples 24` with a `--border` crop. Final: `--width 2400 --samples 96`.
- `world/build3d/` is ignored by git; renders there are scratch output.

Modules in `world/polis/` (work only here; ignore the older `build_world*.py`):

| File | What it holds |
|---|---|
| `core.py` | Arguments, camera, geometry primitives (`face`, `wall`, `prism`, `boxr`, `lathe`, `cyl`, `beam`, `bar`), `Part` + `inst` for reusable meshes, `Scatter` for thousands of instances |
| `mats.py` | Materials, chosen by key: `"kind"` or `"kind:#rrggbb"`. Kinds: plaster, ashlar, rubble, drystone, marble, paving, tile, wood, clay, cloth, straw, bronze, gold, pool, dark, earth, net, leaf, bark, canvas, flat/paint |
| `land.py` | Terrain, roads, ground covers (`paint`, `paint_disc`, `field`), occupancy (`free`, `take`, `take_disc`), `zt(x, y)` ground height, `road_dist(x, y)`, `sd_at(x, y)` distance inland from the shore |
| `props.py` | Small instanced objects: jars, sacks, baskets, hay, carts, boats, ship, wells, statues, stalls, awnings, press, racks, nets |
| `country.py` | Outside the walls: `granary`, `winery`, `fishery`, `pottery`, two schools, tombs, fields. Lists `GROVES`, `VINEYARDS`, `KEEP_CLEAR`, `FIELDS` feed `plants.py` |
| `plants.py` | Trees built as leaf-card clouds (`make`, `cards`, `limb`), shrubs and rocks from downloaded assets, all planting |
| `town.py`, `houses.py`, `civic.py`, `acropolis.py`, `walls.py` | Inside the walls and on the hill |
| `siege.py` | The night siege scene. It shares all the modules above |

Coordinates are metres: x east, y north, town centre at (0, 0). Walls are at about ±78. The sea is south (y below about −135). The acropolis is north (y 100 to 170). The camera is orthographic, looking from the south-east, about 49° above the horizon. So:

- In the picture, south is bottom-left, east is bottom-right, north is top-right, west is top-left.
- The camera sees the **south and east** sides of things. Put new props on the south or east side of a building, or in open yard, or they will be hidden.
- Scale is about 8 pixels per metre at the 2400 px render and 6 at the 1800 px delivery size. **Anything under about 0.5 m is invisible alone.** Small things only read in groups or with strong contrast against the ground. Spend effort on things 1 m and larger, and on clusters. You may enlarge a small prop by up to 1.5x.

New props are built as a `Part` in `props.py` from the existing primitives; copy the style of the props already there. Sizes in the phase files are guides. Coordinates of existing buildings in the phase files were read from the code, not measured: confirm free space with `land.free` and a crop render before placing.

## 3. Rules that must not be broken

1. **Camera, every place, every door and the plan of every road stay exactly as they are.** Messengers on the web page walk these roads. Do not edit `world/build3d/city.json`.
2. **Nothing may stand on or hide a road.** Before placing anything, require `land.free(x, y, r)` and `land.road_dist(x, y) > 3` (use 4 for anything taller than 2 m). After placing, call `land.take(...)` or `land.take_disc(...)` so plants stay off it.
3. **Do not change terrain near roads.** `land.pad` is allowed only inside existing yards or more than 8 m from any road.
4. **The route check must not get worse.** After every phase, run with `--no-render` and compare with the baseline from phase 0: in the `ROUTE CHECK:` line the count "not on the ground" must not rise, the count "hidden from the camera" must not rise, and the `heights` entries in `polis-heights.json` must be unchanged (to 0.02 m).
5. **No people and no animals.** The world is static. Empty pens and troughs are fine.
6. **Do not break the siege scene.** After each phase run `--scene world/build3d/siege.json --out world/build3d/polis-siege.png --no-render` and confirm it finishes without errors.
7. **Do not touch `app/` or `render.py`.** Do not commit or push unless the user tells you to.
8. **Performance.** `inst()` creates one Blender object each time. For more than about 200 copies of one thing, use `Scatter.add(collection_of(mesh, name), x, y, z, rot, scale)` instead.
9. Every new argument must have a default that keeps the build runnable with the command above.

## 4. Period rules

**Never add these** (the reference image has several):

- Bougainvillea, citrus, prickly pear, agave, eucalyptus, jacaranda, maize, tomato, sunflower. (`world/assets/jacaranda_tree` exists; do not use it.)
- Ivy or creepers on the town walls or towers. A working fortification was kept clear.
- Flower beds or lawns in house courtyards. Greek courts were paved or beaten-earth working yards.
- Canals or stone-lined irrigation channels. Greek farming was dry farming; only garden plots were watered, from wells, by small earth ditches.
- Wooden barrels (use amphorae, pithoi, sacks and baskets). Rectangular hay bales (round stacks only).
- Screw presses, rotary animal mills, water wheels, windmills, wheelbarrows.
- Triangular sails (square sails only), lighthouses, large harbour cranes.
- Chimneys, glass windows, domes (the existing round tholos with its conical roof is fine).
- Stone-paved country roads. Outside the walls, roads are earth.

If unsure whether something is right for the period, leave it out.

## 5. The loop for every phase

1. Read the phase file and the code it names.
2. Make the changes.
3. Run the build with `--no-render`; apply rule 4.
4. Render a crop of every area you changed. **Open the image and look at it.** Fix what looks wrong or cannot be seen.
5. Run the siege build with `--no-render` (rule 6).
6. Write a short report: what was added, what was skipped and why, the `ROUTE CHECK` line. Then stop or open the next phase file.

## 6. If something goes wrong

- A change makes the route check worse and you cannot fix it in two tries: remove that item, note it in the report, continue.
- A prop is invisible in the render: enlarge it (up to 1.5x), group more of them, or choose a colour that contrasts with the ground under it. If it still does not read, delete it. Invisible detail only costs render time.
- Build or render time more than doubles against the baseline: cut leaf-card and instance counts first.
