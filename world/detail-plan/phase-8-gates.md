# Phase 8: making the town gates stand out

Files: `world/polis/walls.py` (functions `gate`, `tower`, `build`), `world/polis/props.py`.

## The problem

The three town gates are hard to find in the picture. Each is a round arch 4.8 m wide in the wall, between two towers that look almost the same as every other tower.

| Gate | At | Road runs | Outer face looks |
|---|---|---|---|
| East | (78, 0) | east–west | east (seen by the camera) |
| South | (0, −78) | north–south | south (seen by the camera) |
| West | (−78, 0) | east–west | west (hidden; the camera sees its town-side face) |

## What is right for the period

Free-standing gate posts are not a Greek form. What Greek and Hellenistic gates did have:

- a gate building taller than the wall beside it, between two towers larger than the ordinary ones;
- a framed opening: dressed jambs or flat pilasters either side of the arch, a ring of wedge stones, a cornice above (the gates of Thasos have large carved pillars at the jambs; Priene's east gate has a stone arch);
- statues, herms and small altars just outside (Hermes as guardian of gates is well attested);
- tombs along the road outside (already there).

Do the items below in order. **Run the route check after each one.** The gate passage is on every messenger's route, so this phase is the one most likely to hide a walker. If an item raises the "hidden" count, reduce it or drop it.

## Add

A trial showed that fine framing alone does not make a gate visible at this scale. **Mass comes first**: items 1 and 2 matter most.

1. **A taller gate building.** Raise the top of the wall over the passage (the `ztop` in `gate()`) by 3.0 m for the three town gates, with battlements on top as now, and close the two short side faces this exposes. Add a string course 0.3 m high at the old wall-top level.
2. **Larger gate towers.** In `walls.build`, the gate towers are made with `w=7.2, d=7.6, out=1.8, h=14.3`. Try `w=8.4, d=8.8, out=3.0, h=17.0`. If the hidden count rises, keep the larger plan and step the height down (16, 15, then 14.3) until it does not.
3. **A framed opening, in pale stone.** In `gate()`, for the round-arched gates only (not `lintel=True`), on **both** faces of the wall:
   - a pilaster either side of the arch: 1.4 m wide, standing 0.6 m proud of the wall, from the ground to the top of the raised gate building, in `marble:#e6dfcf`; a capital block on top 1.8 m wide and 0.5 m high;
   - a cornice across both pilasters: a band 0.6 m high standing 0.7 m proud, same stone;
   - make the existing ring of wedge stones the same pale stone, 0.8 m deep in place of 0.55 and 0.15 m proud in place of 0.05.
   The pilasters stand outside the passage width. Nothing may narrow the opening.
4. **A pale apron.** Paint paving for 8 m outside and 6 m inside each gate, as wide as the gate building: `land.paint("pave", ...)`. This changes the ground's look only, not its height.
5. **Guardians outside (optional).** New prop `GATE_PILLAR`: a square stone pier 1.2 x 1.2 x 4 m on a stepped base, with a bronze statue (use `_figure("bronze", 2.4)`) on top. Outside each gate, one each side of the road, 9 m out from the wall and 5 m from the road's centre line. `land.take_disc` each. Drop these if they do not read in a crop.
6. **Do not** add ivy, banners, flags, torches by day, portcullises or drawbridges.

The siege scene builds the same gates shut and barred (`shut=True`). Build it with `--no-render` and then render a crop of one siege gate to check the frame does not cut through the closed leaves.

Done when: in the full picture at 1800 px all three gates can be found at a glance, and the route check is unchanged.
