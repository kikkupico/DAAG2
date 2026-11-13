# Phase 6: inside the town

Files: `world/polis/siege.py` (new function `town_life(g)` called from `build()`), and, **only inside `if core.SIEGE:`**, `world/polis/houses.py` and `world/polis/civic.py`.

## What is there now

The town is the daytime town without its hill: sixteen blocks on a grid, with houses in the northern blocks where the daytime town has its acropolis slope. Streets: the two main streets along x = 0 and y = 0 (8 m wide), four lesser ones along x = ±38 and y = ±38 (5 m wide), and a lane just inside the wall. In the middle are the agora (open square x −35.5 to 35.5, y −35.5 to −4), stoas round it, the council house and a small sanctuary north of the main street (temple at (−24.5, 26.6), altar at (−11.5, 26.6)), and the palaistra (x 4.6–35, y −70.6 to −41.2). About a third of windows and a fifth of doors glow at night. Two watch-fires burn in the agora.

The town looks asleep, not besieged. No messenger route runs inside the walls, but keep the streets passable all the same: nothing in the middle 4 m of any street.

## Add

**Everything here must be lit** (see "Size limits" in `README.md`): the town is dark, and a trial showed that unlit additions inside the walls cannot be seen. Each item below names its light. Lamp cost of this phase: about 13.

1. **Country people sheltering in the town.** When Athens was shut up in 431 BC, Thucydides says the country people camped in the sanctuaries and open spaces. Four clusters of shelters, three or four shelters in each, set in a ring round one hearth of coals: two clusters in the agora's west half, one in the small sanctuary's precinct, one in the open ground by the palaistra. New part `SHELTER`: a lean-to 3 x 2.5 m, two poles 1.8 m tall at the front, a pale cloth roof sloping to the ground behind (`canvas:#c4b594`, so it reads by firelight), its open side facing the fire. Each cluster's fire is a `fire(x, y, z, 350)` with a real lamp. A few jars and bundles by each shelter.
2. **The agora as an arms depot.** Round the two existing watch-fires in the agora (at (−17, −12) and (12, −20)), within 7 m of each: four `ARMS` stacks, three piles of shot, a row of twelve shields leaning on a rail (the `RACK_ARMS` from the camps phase, or build it here), and a cart. Raise those two fires from 600 to 900 watts.
3. **A sacrifice at the altar.** On the altar before the small temple (altar at (−11.5, 26.6)), a bed of glowing coals: a `fire`-material slab covering most of the altar top, 0.12 m high, no flame, and a real lamp of 600 just above it. Two `torch` props (no lamp) flanking the temple steps. This should be the brightest point inside the walls.
4. **Damage, only where it is lit.** Phase 5 puts a torch-lit artillery platform behind the south wall near (−22, −66) and one behind the east wall near (66, 19). Within 10 m of each of those torches only:
   - two roofs with holes: on each, a dark irregular patch about 2 m across lying 2 cm above the roof surface (`dark:#15110e`), with a ring of pale broken edge round it (`clay:#c9a078`, 0.25 m wide) and loose tiles scattered;
   - eight stone balls (0.4 m, pale) lying in the lane and courts.
   Place these from `siege.py` after the town is built, using `scene.ray_cast` downward to find the roof height (see how `render.check` uses it). If phase 5's platforms were skipped, skip this item.
5. **Houses pulled down for the second wall.** The ground between the half-built wall and the south-east corner is already kept clear, and phase 5 lights it with two torches. Fill it with the remains: six low wall stubs (rubble walls 0.6 to 1.2 m high tracing three house plans about 9 x 8 m), heaps of roof tiles (blocks in `clay:#a8674a`), and stacked timbers. If phase 5's torches were skipped, add two here (`torch(x, y, z, 200)`).
6. **Barricades.** Aeneas advises blocking streets inside the gates. Behind each of the four gates, 14 m in, a barricade across **half** the street's width only, leaving the other half open: two carts on their sides and a row of eight pithoi, with one `torch(x, y, z, 180)` beside it. Alternate which half is blocked.
7. **Darker windows near the walls, brighter at the centre.** In `houses.openings`, when `core.SIEGE`, make a window's chance of being lit depend on distance from the centre: about 0.45 within 40 m of (0, 0), falling to 0.12 at the walls. The function may need the position passed in; if that is awkward, skip this item and say so.

Done when: the agora is plainly crowded and lit, the altar fire is the brightest point inside the walls, every new thing in a crop can be seen by its own light, and the daytime build is unchanged.
