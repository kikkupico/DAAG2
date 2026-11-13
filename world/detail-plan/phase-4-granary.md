# Phase 4: the granary farm

Files: `world/polis/props.py`, `world/polis/country.py` (function `granary`).

## What is there now

Door at (150, 0). Walled yard x 150–196, y −31 to 31 (its north-east corner is outside the picture).

| Thing | Where |
|---|---|
| Grain store | x 159–186, y 9–20 |
| Farmhouse | x 156–172, y −27 to −11.5 |
| Tower | x 173.5–180.5, y −24 to −17 |
| Threshing floor | centre (183, −3.5), radius 6.8 |
| Hay stacks | (189, 17), (191, 9) |
| Well | (167, −5) |
| Store jars | round (175, −9) |
| Beehives | x 187–191, y −26.5 |
| Carts | (156, 5.5), (176, 3.5) |

Keep the gate at (150, 0) and a clear lane from it into the yard.

## Add

1. **Grain and chaff heaps.** `GRAIN_HEAP`: a cone, radius 1.5, height 0.9, `straw:#e0b24a`. `CHAFF_HEAP`: wider and flatter, radius 2, height 0.5, `straw:#e6d9a8`. Two of each, on and just beside the threshing floor.
2. **Bread oven.** `OVEN`: a clay dome, radius 0.9, height 1.1 (`clay:#b89a78`), on a rubble base 0.4 m high, with a dark mouth on the south side. One, a few metres from the farmhouse door.
3. **Correct the beehives.** Greek hives were horizontal clay tubes, not upright domes. New `HIVE`: a clay cylinder 0.6 m long and 0.3 m across lying on its side, one end dark. Build a rubble wall 4 m long and 0.5 m high where the hives are now and lay twelve hives on it in two stacked rows. Remove the old `BEEHIVE` instances (leave the old part defined if the siege scene uses it; check with grep).
4. **Olive mill.** `OLIVE_MILL`: a round stone basin 1.8 m across and 0.5 m high (`rubble` side, `paving` rim), a short stone post in the middle, two half-round crushing stones (0.5 m radius) either side of it joined by a wooden bar. This crusher type is attested at Olynthus. Put it under an open shed about 5 x 4 m (four wooden posts and `arch.shed` or `arch.gable`, as the winery's press shed is built) with one `props.PRESS` beside it and six `PITHOS`.
5. **Empty animal pen.** A fold about 8 x 6 m of `drystone(..., closed=True)` with a gate gap, a lean-to roof along its north side (`arch.shed` on three posts, 2.2 m high), a `TROUGH` inside (new part: a stone trough 2.2 x 0.6 x 0.5 m with a `pool` top face just below the rim), and `land.paint("earth", ...)` over its floor. In the south-east part of the yard.
6. **Manure heap.** `MANURE_HEAP`: a low mound, radius 2, height 0.6, `flat:#4a3b2a`. Next to the pen.
7. **Pergola.** Against the south wall of the farmhouse: six wooden posts 2.4 m tall in two rows, rails across the top, and vine leaf cards over it covering about 4 x 7 m. For the leaves, build a Part with `plants.cards("leaf:#62803a", [...], n, .2, g)` over a flat ellipsoid, or reuse the vine part from `plants.py`.
8. **Loaded carts.** Replace the two empty carts with loaded ones (see `README.md`; build the parts if an earlier phase did not): a `CART_SACKS` by the grain store door, a `CART_HAY` by the hay stacks, and a `CART_AMPH` (oil) beside the olive mill.
9. **More working clutter.** A second block of sacks by the store door (twenty, stacked two high), a stack of ten baskets, one wood pile.

After placing, `land.take` each footprint.

Done when: a crop of the farm at 2400 px shows at least six new kinds of thing that can be told apart, and the lane from the gate is still clear.
