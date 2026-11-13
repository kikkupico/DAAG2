# Phase 1: roof relief and fuller trees

Geometry only. Do not change any colours.

Files: `world/polis/arch.py`, `world/polis/plants.py`.

## Roofs

Roofs are the largest area of the picture, and their tile rows are too fine to see: rows are 0.56 m apart, about 3 pixels.

1. In `arch.py`, raise `TILE_W` from 0.56 to about 0.85.
2. In `arch.tiles`, the cover-tile ribs are built from `hw, hh, tw = .105, .085, .045` (half-width at the base, height, half-width at the top). Raise them to about `.14, .12, .06` so each rib casts a visible shadow.
3. `mats.m_tile` draws a tile pattern with `s.brick(s.uv, .56, .5, ...)`. Change only the first number so the drawn tile width matches the new `TILE_W`. Change nothing else in that material.
4. Check `arch.ridge` and the hips: ridges should still sit on top of the ribs, and no gaps should open where roof faces meet.
5. Render a crop of the town centre and of one farm. Tile rows must be countable on a house roof.

## Trees

1. In `plants.py`, raise the leaf-card count by about 30% for olive (`_olive`, 950 cards) and plane (`_plane`, 1900 cards). Leave the other species alone.
2. Render a crop of an olive grove. Crowns should look solid from above, with no trunk or ground showing through the middle.
3. If the build or render time rises by more than a quarter, use 15% instead.

Done when: tile rows are visible on house roofs at 1800 px width, and olive and plane crowns look full.
