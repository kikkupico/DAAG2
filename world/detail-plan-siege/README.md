# Siege detail pass: brief for the implementing agent

You are adding detail to an existing Blender model of a Hellenistic siege at night, built entirely by Python scripts. A walled town sits inside a ring of siege lines; four army camps lie outside. The model follows Polybius' account of Philip V at Phthiotic Thebes (217 BC).

**How to use this folder.** Read this file once. Then do **one phase file at a time**, in order. Do not read ahead: each phase file contains everything that phase needs. Finish a phase, run its checks, report, and only then open the next file.

| Order | File | Work |
|---|---|---|
| 0 | `phase-0-baseline.md` | Record the starting state |
| 1 | `phase-1-camps.md` | The four army camps |
| 2 | `phase-2-lines.md` | The ground between the two palisades |
| 3 | `phase-3-siege-works.md` | Mound, siege tower, artillery, mine |
| 4 | `phase-4-no-mans-land.md` | The ground between the lines and the town wall |
| 5 | `phase-5-wall-defence.md` | The town wall and its defenders' works |
| 6 | `phase-6-town-under-siege.md` | Inside the town |
| 7 | `phase-7-optional.md` | Sutlers' market, town ditch (only if all else is done) |
| 8 | `phase-8-final.md` | Final render and report |

## 1. Goal and mood

The current render is accurate but empty: large areas of bare ground, few fires, little sign of an army of thousands or a town shut in for weeks. The goal is a picture **full of readable, period-correct signs of a siege in progress**, for about 220–190 BC.

**The mood is a quiet night watch, not an assault.** Nothing is in flight, nothing is burning down, no wall is falling. The story is told by what has been built, stacked, damaged and left lit.

Where accuracy and looks pull apart, these choices have been made. Follow them:

| Question | Decision |
|---|---|
| Many small lights, or a few | **Many, and all of them still.** An army at night shows dozens of points of light. Here they are banked hearths of glowing coals, lamps inside tents, cressets and braziers, oven mouths, a forge. This is both accurate and the best source of beauty in the scene |
| Open flames | **None.** The picture is looked at for a long time as a living place, not as a frame cut from a film. A leaping flame looks frozen. No standing flame anywhere is taller than 0.2 m |
| Bright coloured tents and banners | **No.** Soldiers' tents are hide and undyed cloth. Only the commander's pavilion has colour. A few standards, no flags or pennants |
| Burning buildings | **No.** One burnt-out siege shed with glowing embers is allowed (phase 3). Sorties that burned engines are well attested; a town on fire is a different story from ours |
| Anything caught in motion | **No.** Nothing falling, swinging, flying, spilling or half-collapsed in a way that could not stay so. Things lie, stand, hang or lean at rest |
| Visible damage to the town | **Yes, moderate.** Broken battlements, a few holed roofs, shot lying in the streets near the attacked corner |
| Smoke and mist | **No.** They are costly to render and hide the roads |
| Things too small to see at night | **Leave them out**, however correct |

**Lighting, colour grading, the brightness and colour of lamps, and the colours of existing materials are out of scope.** They are being handled separately. Do not edit `render.py`. Do not change the light colours or the default wattages in `siege.py`. You may add new fires and torches with the existing helpers.

## 2. How the build works

Run from the repository root (Blender 5.1 is installed as `blender`):

```
blender -b --factory-startup -P world/build_polis.py -- --scene world/build3d/siege.json --out world/build3d/polis-siege.png
    [--width 2400] [--samples 96] [--border x0,y0,x1,y1] [--no-render] [--no-engines]
```

- `--no-render` builds everything and runs the route check without rendering. Use it as the fast test.
- `--border x0,y0,x1,y1` renders only a crop. The numbers are fractions of the frame, 0 to 1, with y measured from the top.
- To find where a world point lands in the picture: `core.project(x, y, z)` returns pixels in a 1600 x 1200 frame. Divide by 1600 and 1200 to get `--border` fractions.
- Quick preview: `--width 1600 --samples 32` with a `--border` crop. Final: `--width 2400 --samples 96`.
- `world/build3d/` is ignored by git; renders there are scratch output.

Modules in `world/polis/`:

| File | What it holds |
|---|---|
| `siege.py` | **Most of your work.** Palisades, watch-towers, tents, engines, camps, the mound, the siege tower, the battery, the town's second wall, and every fire and torch |
| `core.py` | Arguments, camera, geometry primitives (`face`, `wall`, `prism`, `boxr`, `lathe`, `cyl`, `beam`, `bar`), `Part` + `inst` for reusable meshes, `Scatter` for thousands of instances |
| `mats.py` | Materials, chosen by key: `"kind"` or `"kind:#rrggbb"`. Kinds include wood, canvas, straw, rubble, ashlar, paving, clay, cloth, bronze, dark, flat/paint, and for light `fire` (flame), `glow` (lamplight) |
| `land.py` | Terrain, roads, ground covers (`paint`, `paint_disc`), occupancy (`free`, `take`, `take_disc`), `zt(x, y)` ground height, `road_dist(x, y)`, `earthwork` |
| `props.py` | Shared small objects: jars, sacks, baskets, hay, carts, stalls, statues |
| `town.py`, `houses.py`, `civic.py`, `walls.py` | The town. **These are shared with the daytime scene**: guard every change with `if core.SIEGE:` |
| `plants.py` | Trees and scrub; in the siege, woods beyond the lines and stumps near them |

### Layout

Coordinates are metres: x east, y north, town centre at (0, 0). The camera is orthographic, looking from the south-east, about 49° above the horizon. In the picture, south is bottom-left, east is bottom-right, north is top-right, west is top-left. The camera sees the **south and east** sides of things.

| Thing | Where |
|---|---|
| Town wall | An octagon: straight sides at x = ±78 and y = ±78, cut corners between (78, ±52) and (52, ±78) and so on. `S["octagon"]` |
| Town gates (shut and barred) | (78, 0), (0, −78), (−78, 0), (0, 78) |
| Inner palisade | 27.5 m outside the wall line (`D_IN`) |
| **Ring road** (messengers walk it) | 40 m outside the wall line (`D_ROAD`), 5 m wide |
| Outer palisade | 52.5 m outside the wall line (`D_OUT`) |
| Spur roads to the camps | from the ring road straight out to each camp's door |
| Commander's camp | centre (0, 165), radius 23, door (0, 144) |
| Camp A (engineers) | centre (162, 0), radius 19, door (144, 0) |
| Camp B (timber yard) | centre (0, −162), radius 19, door (0, −144) |
| Camp C (stores) | centre (−162, 0), radius 19, door (−144, 0) |
| Mound with the ram | against the south-east wall, centre line from (65, −65) outward along (0.71, −0.71) for 30 m. `S["mound"]` |
| Siege tower (helepolis) | (87.6, 19), facing the east wall, on a plank road x 84–106.5, y 14.5–23.5 |
| Battery of three stone-throwers | (−34, −96.8), (−22, −96.8), (−10, −96.8), facing the south wall |
| Defenders' second wall | inside the south-east corner, from (76.6, −31) to (31, −76.6) |

Inside a camp, `camp()` works in local coordinates: the gate is at (0, −r), the camp's street runs in along +y, the commander's or officer's tent is at the head of the street.

The four camps sit at the four corners of the picture. There is almost no ground in view beyond the outer palisade except round the camps.

### Seeing things at night

- Scale is about 8 pixels per metre at 2400 px and 6 at the 1800 px delivery size. Anything under about 0.5 m is invisible alone.
- **Darkness hides detail.** A new thing is seen only if it is (a) within about 8 m of a fire or torch, (b) lit itself (`fire` or `glow` material), or (c) large and pale on open moonlit ground. Plan every addition round one of these.
- **What "fire" and "torch" mean in these files.** The `FIRE` part is a hearth: a ring of stones round a low bed of glowing coals, with no flame. The `TORCH` part is a cresset on a pole: a small iron cup of glowing coals. Wherever a phase file says "fire", "cooking fire", "watch-fire" or "torch", it means these. Never model a standing flame.
- Use the helpers `fire(x, y, z, watts)` and `torch(x, y, z, watts)`: each makes the prop and a real lamp. Real lamps cost render time. **Budget: at most 60 new real lamps in the whole pass.** The build prints `SIEGE: N lights`; record it in phase 0.
- For a hearth that only needs to be seen, not to light anything, place the prop alone: `inst(FIRE, x, y, z, 0, scale)`. Its coals are emissive and cost almost nothing. Most of the new cooking hearths should be this kind.
- **Lit tents** are the other still light. A tent with a lamp inside shows a warm door: make variants of the tent parts whose dark door face uses the `glow` material in place of `dark`. Use them freely; they need no lamp.

### Size limits

A trial with an image generator showed which things get blown up out of scale, and that small unlit things inside the dark town do not read. Keep to these limits:

| Thing | Limit |
|---|---|
| Clay oven | at most 1.8 m across, 1.1 m high |
| Spoil heap, clay or earth mound | at most 3 m radius, 1.5 m high |
| Stake belt | stakes at most 1.5 m long; belt at most 3 m wide; **within 6 m of the inner palisade, never touching the town wall** |
| Bed of coals | at most 0.25 m high and 1.2 m across; the one beacon basket 1.6 m across. No standing flames |
| New tents | no larger than the existing `TENTS`; no new pavilions outside a camp |
| Forge shed, shelters | at most 4 x 4 m |
| Anything new | at most 5 m tall, except gate posts and hoists |

**Do not move, remove, shrink or add a camp.** The four camps stay where they are.

**Inside the town walls, add nothing that is not lit.** Every addition there must lie within 8 m of a real lamp (an existing one or one you add) or be emissive itself. If it cannot be lit within the lamp budget, leave it out.

## 3. Rules that must not be broken

1. **Camera, every place, every door and the plan of every road stay exactly as they are.** Do not edit `world/build3d/siege.json`.
2. **Nothing may stand on or hide a road.** Before placing anything, require `land.free(x, y, r)` and `land.road_dist(x, y) > 3.5` (use 5 for anything taller than 2 m). After placing, call `land.take(...)` or `land.take_disc(...)`.
3. **No terrain change within 8 m of a road.**
4. **The route check must stay perfect.** The baseline is `0 not on the ground` and `0 hidden from the camera`. After every phase, run with `--no-render`: both must still be 0, and the `heights` in `polis-siege-heights.json` must be unchanged (to 0.02 m).
5. **No people, no animals, no bodies.** The world is static.
6. **Do not break the daytime scene.** After each phase run `--scene world/build3d/city.json --out world/build3d/polis.png --no-render` and confirm it finishes without errors and its `ROUTE CHECK` line has not changed.
7. **Do not touch `app/` or `render.py`.** Do not commit or push unless the user tells you to.
8. **Performance.** `inst()` creates one Blender object each time. For more than about 200 copies of one thing, use `Scatter.add(collection_of(mesh, name), x, y, z, rot, scale)`.
9. `--no-engines` must still work: anything that belongs to the mound, the siege tower or the battery stays inside the `if not core.flag("--no-engines")` branch.

## 4. Period rules

**Never add these:**

- Trebuchets or any counterweight engine, cannon, crossbows, one-armed catapults. Artillery here is two-armed torsion engines only: stone-throwers and smaller bolt-shooters.
- Timber galleries hung on the outside of stone walls, drawbridges, portcullises, water-filled moats, round towers with conical slate roofs.
- A camp laid out as a rigid square grid with rounded corners (that is Roman). Greek camps followed the ground.
- Rows of pits with stakes, or other works known from Caesar's sieges.
- Flags, pennants, heraldic shields, striped pavilions. A few plain standards exist already; add no more than two.
- Barrels (use amphorae, pithoi, sacks, baskets, skins). Wheelbarrows. Rectangular hay bales.
- Open flames, bonfires, projectiles in the air, flaming arrows, smoke plumes, explosions.

If unsure whether something is right for the period, leave it out.

## 5. The loop for every phase

1. Read the phase file and the code it names.
2. Make the changes.
3. Run the siege build with `--no-render`; apply rule 4.
4. Render a crop of every area you changed. **Open the image and look at it.** Fix what looks wrong or cannot be seen.
5. Run the daytime build with `--no-render` (rule 6).
6. Write a short report: what was added, what was skipped and why, the `ROUTE CHECK` line, the `SIEGE: N lights` line. Then stop or open the next phase file.

## 6. If something goes wrong

- A change makes the route check worse and you cannot fix it in two tries: remove that item, note it in the report, continue.
- A prop cannot be seen in the render: move it nearer a fire, enlarge it (up to 1.5x), or group more of them. If it still does not read, delete it.
- Render time more than doubles against the baseline: turn real lamps into prop-only fires first.
