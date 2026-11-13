# Phase 9 (optional): dry stream bed and salt works

Do this phase only if phases 1 to 8 are finished and their checks pass. Each part stands alone. Drop a part if its checks fail twice.

Files: `world/polis/country.py`, `world/polis/plants.py`, `world/polis/props.py`.

## A. Dry stream bed

A summer-dry stream bed with reeds and oleander, made **by paint and planting only**. No terrain change, no bridge, no crossing of any road.

1. Course: a winding line that starts **east of the ring road that runs north from (90, 0)**, for example at (112, 92), and runs east-south-east until it leaves the picture (`core.in_view` turns false). It must stay at least 4 m from every road (`land.road_dist`) and outside the granary yard (x 150–196, y −31 to 31). Build the line from eight to ten points and smooth it with `core.chaikin(pts, 2, closed=False)`.
2. Paint along it: a 3 m band of `"gravel"`, a thin broken line of `"wet"` down the middle, and `"lush"` 4 m either side with a soft edge.
3. Add its outline (the line widened to 10 m) to `KEEP_CLEAR` **before** `fields(...)` runs, so no plot is laid across it.
4. Plants: reeds in the bed (`_reed` exists in `plants.py`); a new bush `oleander` on the banks, 2.5 m tall, leaf colour `#3f6a3a`, with about 15% of its cards in `paint:#d8668c` (the flowers); five or six plane trees along it.

Oleander is native to Greek stream beds and is the correct source of pink flowers. Use it only here and beside wells.

## B. Salt works

Sea salt was made by letting sea water dry in shallow pans on flat shore.

1. Find a flat stretch of beach where `3 < land.sd_at(x, y) < 14`, `land.free` is true, and no road is within 5 m. Look first east of the harbour, round x 50–90.
2. Six pans in two rows, each about 5 x 4 m, with clay banks 0.25 m high and 0.4 m wide between them (`flat:#a8977a`). Pan floors are flat faces 5 cm below the bank tops: two in `pool:#8fa39c` (fresh brine), two in `flat:#c9c2b4`, two in `flat:#e2dcd0` with a pink-brown edge.
3. Four heaps of salt beside the pans: cones, radius 0.8, height 0.6, `flat:#eeeae0`. A few baskets and a wooden rake (a 2 m pole with a short cross-piece) lying by them.
4. Add the area to `KEEP_CLEAR` before `fields(...)` runs.

Done when: each part you kept is visible in a crop, and the route check is unchanged.
