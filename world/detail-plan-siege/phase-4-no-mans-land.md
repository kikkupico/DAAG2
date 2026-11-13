# Phase 4: the ground between the lines and the town wall

Files: `world/polis/siege.py`, `world/polis/plants.py` (the `if core.SIEGE:` parts only).

## What is there now

A belt 27.5 m wide between the town wall and the inner palisade. `lines()` paints a band of trodden earth 18 m wide round the wall. Scrub and shrubs are scattered over the rest by `plants.py`. It reads as ordinary countryside.

In a siege this belt is the killing ground. The defenders clear it so nothing gives cover; the attackers strip it for brushwood. No messenger route crosses it, so this phase is the least risky. Nothing here has its own light: **everything must be pale on dark ground or dark on pale ground to be seen by moonlight.**

## Change

1. **Clear the scrub.** In `plants.py`, find where shrubs and tufts are scattered and, when `core.SIEGE`, skip any point within the belt (inside `grow(siege.OCT, siege.D_IN - 2)` and outside the wall). Leave a thin scatter (about one in eight) of low tufts so it is not perfectly bare.
2. **Stumps.** Scatter `siege.STUMP` through the belt at about one per 60 m², using `Scatter`, as `plants.py` already does beyond the lines.

## Add (in a new function `no_mans_land(g)` in `siege.py`, called from `build()`)

3. **Spent shot.** Stone balls lying where they fell at the foot of the walls opposite the battery (south wall, x −40 to 0) and opposite the siege tower (east wall, y 5 to 35): thirty single balls (`lathe` spheres 0.3 to 0.45 m across, `rubble:#b5b0a4`, half sunk) scattered within 12 m of the wall. Use `Scatter` with three sizes.
4. **Fallen masonry.** At the foot of the same two stretches of wall and of the south-east wall above the mound: heaps of fallen blocks. New part `RUBBLE_HEAP`: twelve squared blocks about 0.9 x 0.5 x 0.45 m (`ashlar:#cdc1a6`) tumbled in a pile 3 m across. Five heaps in all. (The matching broken battlements are made in phase 5.)
5. **Wrecked gear.** Three broken mantlets lying flat (the `MANTLET` part with a tilt), one broken ladder in two pieces, and one overturned cart (`props.CART` with `tilt=(1.4, 0)`), spread round the belt on the south and east sides.
6. **Scorched patches.** Six patches of burnt ground, radius 3 to 5 m, with `land.paint_disc("wet", ...)`, mostly on the south and east sides.
7. **Trodden paths.** From each of the three gaps in the inner palisade to the work it serves, a path of trodden earth 3 m wide: `land.paint("earth", [p, q], 1.0, 1.0, closed=False, width=3)`.

Done when: in the full picture the belt reads as stripped, beaten ground clearly different from the country beyond the lines, with pale shot and rubble visible at the foot of the attacked walls.
