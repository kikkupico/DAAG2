# Phase 6: the winery and its vineyards

Files: `world/polis/props.py`, `world/polis/country.py` (function `winery`).

## What is there now

Door at (−148, 0). Walled yard x −190 to −148, y −26 to 28 (its far north-west corner is outside the picture).

| Thing | Where |
|---|---|
| Press-house | x −181 to −159, y 6–17 |
| House | x −186 to −170, y −23 to −8 |
| Lever press under an open shed | centre (−157, −15.5), shed 11 x 8 m |
| Treading floor with a sunk vat | (−156, 9.5) |
| Store jars sunk in the ground (4 x 5) | x −179 to −174, y −3.5 to 3 |
| Rows of amphorae | x −168 to −162.5, y 2–4.4 |
| Cart | (−154, 3) |
| Wood pile | (−187, 21) |
| Vineyards | five blocks all round the yard (`VINEYARDS`) |

Keep the gate at (−148, 0) and a clear lane from it into the yard.

## Add in the yard

1. **Raisin drying ground.** An area about 6 x 10 m in open yard. Lay straw mats in rows: flat `straw` faces 1.2 x 3 m, 3 cm above the ground, with 0.4 m between. On each mat a slightly smaller dark face 1 cm higher: `flat:#4a2338` (black grapes) on most, `flat:#9a7a2e` (white grapes) on a few.
2. **Harvest baskets.** A variant of `BASKET` 1.4 times the size with a dark purple disc (`flat:#3d1f33`) as its top. Two clusters of eight by the treading floor.
3. **Vine stakes.** `STAKES`: about twenty thin poles 2 m long lying side by side in a stack 0.5 m high (`wood:#8a7352`). Two stacks against a wall on its south or east side.
4. **Lids on the sunk jars.** A pale disc (`paving:#cfc5ac`, radius 0.36) on top of each of the twenty sunk pithoi.
5. **Empty amphorae.** Against the south wall of the press-house, two rows of amphorae leaning on the wall (use `jar_rows`, then tilt is optional), about thirty in all.
6. **Pitch hearth.** Jars were lined with pine pitch. Three stones in a ring, a dark cauldron 0.8 m across on them (`flat:#22201e`), `land.paint_disc("wet", ...)` 1.5 m round it for the scorched ground, and a wood pile beside it.
7. **Pergola.** Over the ground between the house and the sunk jars, about 5 x 8 m: eight posts 2.4 m tall, rails on top, vine leaves over it (reuse the pergola Part from the granary phase if it exists).

8a. **Loaded carts.** Replace the empty cart at (−154, 3) with a `CART_AMPH` (see `README.md`), and stand a second `CART_AMPH` just inside the gate, to one side of the lane.

## Add in the vineyards

8. **Guard huts.** `WATCH_HUT`: four posts 2.2 m tall, a flat reed roof 2.5 x 2.5 m (`straw:#b9a56a`) with a slight slope. Two, each at a corner of a vineyard block, at least 4 m from any road. Call `land.take_disc` and add a small polygon to `KEEP_CLEAR` so vines are not planted through them.
Done when: a crop of the winery at 2400 px shows the drying ground, the pergola and at least four other new things that can be told apart.
