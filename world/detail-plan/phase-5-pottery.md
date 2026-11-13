# Phase 5: the potters' quarter

Files: `world/polis/props.py`, `world/polis/country.py` (function `pottery`).

## What is there now

Door at (−80, −80); the quarter is unwalled and lies south-west of it.

| Thing | Where |
|---|---|
| Workshop | x −104 to −91, y −90 to −82.5 |
| Open drying shed with rows of jars | x −103 to −92, y −100.5 to −93.5 |
| Two kilns (stone drum, clay dome, stoke-hole on the south) | (−112, −94) and (−114, −103) |
| Two potters' wheels | (−90, −102), (−87, −97) |
| Clay pit | about x −121 to −110, y −92 to −84 |
| Heaps of jars | round (−96, −105), (−107, −109), (−85, −89) |

A road runs from (−80, −80) south to (−74, −104) and on to the fishery. Keep everything at least 3 m from it.

## Add

1. **Settling tanks.** Clay was mixed with water and left to settle. Three shallow stone tanks, each about 3 x 2.4 m, in a row next to the clay pit, each 0.2 m lower than the last. Copy how the salting vats are built in `fishery` (two `walls` rings, a rim, a `cap` for the liquid). Liquid colours: `pool:#8b7355`, `pool:#a08a6a`, `pool:#b59f80`.
2. **Clay heaps.** `CLAY_HEAP`: a mound, radius 1.5, height 0.7, `flat:#8a7a66`. Three, beside the tanks.
3. **Unfired ware.** A pale version of the amphora part (`clay:#b9a58a`). Lay about sixty in `jar_rows` in open ground south of the drying shed. Seeing pale unfired pots next to orange fired ones is the point.
4. **Black-gloss ware.** A dark version of the hydria part (`clay:#2a2622`). A block of about thirty near the workshop door, on its east side.
5. **Roof tiles.** Potters made the town's tiles. `TILE_STACK`: a block 0.9 x 0.6 x 0.6 m in `clay:#b8754f`, with two or three thin dark lines across its top to suggest stacked tiles. Twelve stacks in two neat rows.
6. **Waster dump.** `SHERD_HEAP`: a mound, radius 2.5, height 0.9, `clay:#9a5a3a`, with about ten ordinary jars half sunk in it at steep tilts (`inst(..., tilt=(a, b))`). At the south-west edge of the quarter.
7. **Brushwood fuel.** `FAGGOTS`: a bundle 1.5 m long and 0.4 m across (`bark:#7a6a50`). A stack of eight by each kiln. Remove one of the two existing wood piles at the kilns.
8. **Kiln detail.** On each kiln: a dark disc 0.5 m across on top of the dome (the vent), and a wider scorched patch at the stoke-hole (`land.paint_disc("wet", ...)` radius 3 in place of 2).
9. **Loaded cart.** One `CART_AMPH` (see `README.md`) standing by the workshop, on the side toward the road but 4 m clear of it: new jars going out to the winery and the fishery.
10. **Leave room for a well.** Keep a clear circle of 4 m radius round (−95, −104); a later phase puts a well there.

Extend the quarter's `KEEP_CLEAR` box if anything lies outside it.

Done when: a crop of the quarter at 2400 px shows pale, orange and black pots as three distinct groups, the tanks, the tile stacks and the waster dump.
