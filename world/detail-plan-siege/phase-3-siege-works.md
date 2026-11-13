# Phase 3: the siege works

File: `world/polis/siege.py` (functions `mound`, `tower_attack`, `battery`, and new parts).

Everything in this phase must stay inside the `if not core.flag("--no-engines")` branch of `build()`. Put new works in new functions called from that branch.

## What is there now

| Work | Where | What it has |
|---|---|---|
| Mound | Against the south-east wall. Centre line from (65, −65) outward along (0.71, −0.71) for about 30 m; about 26 m wide at the wall, 14 m at the tail; 5.9 m high at the wall | Log-shored flanks, the ram in its wheeled shed on top, two mantlets, shot, three lengths of covered gallery behind, one fire |
| Siege tower | (87.6, 19), facing west at the east wall | Six-storey wheeled tower on a plank road, three gallery lengths, two small catapults behind mantlets, two fires, one torch |
| Battery | (−34, −96.8), (−22, −96.8), (−10, −96.8), facing north at the south wall | Three stone-throwers, a line of mantlets, shot piles, one fire, one torch |

## Add to the mound

1. **Earth-carriers' gear.** Along both flanks at the tail: two rows of baskets full of earth (`props.BASKET` at 1.3 scale with a dark earth disc on top, ten per row), and bundles of brushwood (new part `FASCINE`: a bundle 2 m long, 0.5 m across, `bark:#6a5a44`), fifteen stacked in two heaps. Mounds were built of earth, timber and brushwood in layers.
2. **A longer covered approach.** Extend the line of `SHED` gallery lengths from three to seven, running back from the mound's tail toward the gap in the inner palisade at (84.6, −84.6).
3. **Screens at the head.** Raise the number of mantlets on the mound's top from two to six, in a line either side of the ram.
4. **Two torches** on the mound's flanks, halfway up: `torch(x, y, z, 180)`.

## Add to the siege tower

5. **Hauling gear.** Behind the tower (east of it) on the plank road: two capstans (new part `CAPSTAN`: a vertical drum 0.6 m across and 1.2 m high with four horizontal bars 2 m long through its head, on a timber frame), and two thick ropes lying on the planks from the capstans to the tower's base (dark beams 0.08 m thick).
6. **A ditch-filling shed.** In front of the tower (west of it, toward the wall), one wheeled shed with a low sloping roof of hides (reuse `RAM` without its beam: make a variant part `TORTOISE`), with a heap of rubble and brushwood spilling from its front. Greek engineers describe such sheds for filling ditches under cover.
7. **Lamps in the tower.** Give two of the tower's dark ports on its east and south faces a `glow` panel in place of `dark`, and add one real lamp of 200 inside the open back at mid height.

## Add to the battery

8. **Proper emplacements.** Round each stone-thrower, on the side toward the town, a low bank of earth-filled baskets in an arc (twelve baskets at 1.3 scale, two high), in place of nothing; keep the mantlets.
9. **Ammunition.** Behind the battery, a rack of dressed shot sorted by size: three rows of ten stone balls (`lathe` spheres 0.25, 0.3 and 0.4 m across, `rubble:#a39e92`) laid in a shallow timber frame.
10. **Spare parts.** One spare throwing arm and one coil of rope by each engine.

## New works

11. **A mine.** Mining under walls is well attested (Philip V at Prinassos, the Romans at Ambracia in 189 BC). Near (−100, 30), between the inner palisade and the west wall but at least 6 m from the palisade: a pit head under a low shed (`SHED`), a sloping trench 2 m wide running 8 m toward the wall and ending under a hide-covered frame, two spoil heaps of pale earth beside it (mounds of radius 3 and height 1.5 at most, `flat:#9a8c72`), a stack of pit props (short logs), and a torch. Paint the ground round it with `land.paint(..."earth"...)`.
12. **A burnt shed.** The one sign of a sortie. Near (20, −100), east of the battery: a length of gallery burnt out. Build it as four charred posts leaning at different angles (`wood:#1f1a16`), a collapsed roof lying on the ground (two dark faces), `land.paint_disc("wet", ...)` radius 4 for the scorched ground, and embers: six small `fire`-material patches 0.2 to 0.4 m across lying on the ground among the wreck, with one real lamp of 120 at 0.5 m height. No flames.
13. **Scaling ladders made ready.** At two places just inside the inner palisade on the north and west sides: six ladders (7 m long, from phase 1) laid side by side on the ground, with a guard fire (prop only) beside them.

Done when: a crop of each of the three existing works shows the new things clearly in firelight, the mine and the burnt shed can each be found in the full picture, and `--no-engines` still builds without errors.
