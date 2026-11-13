# Phase 7: wells, kitchen gardens, orchard trees

Files: `world/polis/props.py`, `world/polis/country.py`, `world/polis/plants.py`.

Background: wells were common in the Greek countryside, but they belong to **farmsteads and garden plots, not to grain fields**, which were never watered. Water was lifted with a counterweighted pole (Greek *kelon*), which is attested in classical sources. Gardens were small walled plots of vegetables and fruit trees, watered from the well by small earth ditches.

## New props (`props.py`)

- `SWAPE_WELL`: thin posts do not read at this scale, so build it bold. A stone kerb ring 2 m across and 0.7 m high with a dark disc inside (see the existing `_well`). Beside it a forked wooden post 4 m tall and 0.25 m thick. Across the fork, a pole 7 m long and 0.2 m thick, tilted, in pale wood (`wood:#b59a6a`), with a stone counterweight (a 0.7 m block) at the short end and a rope and bucket hanging from the long end over the well.
- `TROUGH`: a stone trough 2.2 x 0.6 x 0.5 m with a `pool` top face just below the rim (reuse the part if the granary phase made it).

## Wells

Place five or six `SWAPE_WELL` in all:

- one just outside the winery yard, on its south or east side by the vines;
- one in the open ground of the potters' quarter, near (−95, −104), in the circle the pottery phase left clear;
- one in each garden below;
- one at the roadside outside the east gate, about 5 m off the road, with a `TROUGH`.

Round each: `land.paint_disc("lush", x, y, 3.0, ...)` and `land.paint_disc("wet", x, y, 1.2, ...)`, then `land.take_disc(x, y, 3)`.

## Gardens (`country.py`)

Write `garden(x0, y0, x1, y1, g)`:

- a plot about 14 x 18 m, bounded by `drystone(..., closed=True)` with one gap for a gate;
- six to ten narrow beds: rectangles about 1.6 m wide with 0.6 m earth paths between, each drawn with `land.field(bed, "green", angle)`;
- a `SWAPE_WELL` at one corner;
- a thin line of `"wet"` cover from the well along the ends of the beds (the ditch): `land.paint("wet", [p, q], 1.0, .3, closed=False, width=.4)`;
- append the plot's outline to `GROVES` with the new kind `"orchard"` and a wide spacing, so three or four fruit trees are planted on its border, and `land.take` the beds so nothing wild grows in them;
- append the plot polygon (grown by 2 m) to `KEEP_CLEAR`.

Build three gardens. Call them in `country.build()` **before** `fields(...)`, so no field is laid over them. Sites (check each with `land.free` and move if not free):

- beside the granary yard, to its south: about x 152–170, y −52 to −36;
- beside the winery yard, to its south-east: about x −146 to −130, y −30 to −12;
- outside the south gate, east of the fishery road: about x 8–24, y −98 to −84.

## Orchard trees (`plants.py`)

Copy the pattern of `_fig`:

- `pomegranate`: 3 m tall, leaf colour `#4f7a34`, plus about 25 small cards in `paint:#b3261e` (the fruit).
- `almond`: 4 m tall, open crown, leaf colour `#6f8a4a`.

Register both with `make(...)` where the other species are made. In the loop over `country.GROVES`, add a branch for kind `"orchard"` that plants a random choice of fig, pomegranate, almond and olive.

In `country.fields`, plots with no crop become olive groves (`GROVES.append((Q, "olive", 8.5))`). Make about one in three of those `"orchard"` instead.

Done when: three walled gardens with striped green beds and a well are clearly visible, and at least five lifting poles can be seen in the full picture.
