# Phase 5: the town wall and the defenders' works

Files: `world/polis/siege.py` (function `town_defence` and new functions), `world/polis/walls.py` (only inside `if core.SIEGE:`).

## What is there now

The wall is an octagon with a tiled tower at every corner and two at each of the four gates. The gates are shut and barred. At night about a third of the tower windows glow, and a watch-fire in an iron basket burns on the wall-walk beside every other tower. Above the mound, the defenders have raised a screen of timber and hides on the wall. Inside the south-east corner a second wall of rubble is half built, from (76.6, −31) to (31, −76.6).

Helpers: `walls.H_WALL` is the wall's height; `walls.q(z)` rounds a height to a stone course; the wall-walk is at `walls.q(land.zt(x, y) + walls.H_WALL)`; `walls.TOWERS` lists every tower as (x, y, eaves height).

The measures below come from Greek writers on defending towns, chiefly Aeneas Tacticus (4th century BC) and Philo of Byzantium (3rd century BC).

## Add

1. **Padding against the ram.** Aeneas describes lowering sacks of chaff and wool to cushion the wall where a ram strikes. On the outer face of the south-east wall where the mound meets it (the stretch 8 m either side of (65, −65), projected onto the wall), hang ten large sacks from the battlements on ropes: each a pale bag 1.2 m across and 1.8 m long (`canvas:#b8a888`), its top 1 m below the wall-walk, with a thin dark rope up to the parapet. Place them just outside the existing hide screen so they are not hidden by it.
2. **Swing-beams.** At Plataea the defenders dropped heavy beams on chains to break the ram's head. Two beams over the same stretch: each a squared timber 5 m long lying across the parapet and reaching 2 m out beyond the wall, with a stone block 0.8 m across hanging from its outer end on a chain (a thin dark bar), and a timber A-frame 2.5 m tall on the wall-walk holding it.
3. **Broken battlements.** Opposite the battery (south wall, x −40 to 0) and opposite the siege tower (east wall, y 5 to 35), knock out the parapet: in `walls.parapet` (or wherever merlons are placed), when `core.SIEGE`, skip the merlons that fall in those two stretches at random (about half), and add two notches 1.5 m wide and 1 m deep in the wall top, each patched with a timber frame and hides (`HIDE`).
4. **Defenders' artillery.** Philo advises placing stone-throwers behind the wall to answer the attackers'. Inside the wall, on two timber platforms 5 x 5 m and 3 m high (four posts, a plank deck, a ladder): one behind the south wall near (−22, −66) and one behind the east wall near (66, 19), each with a `CATAPULT` at 0.8 scale pointing outward, a pile of shot, and a `torch`. Check they stand in the lane behind the wall, not on a house; move along the wall if needed.
5. **A lit wall-walk.** Between every pair of towers, one torch on the wall-walk at the midpoint (prop only, no lamp, at 0.8 scale), on the inner edge of the walk. About sixteen. Then give four of them, evenly spread, a real lamp of 150.
6. **A signal beacon.** Signalling by fire is described at length by Polybius and Aeneas. On the wall-walk beside the north gate's west tower, a beacon: an iron basket 1.6 m across on a 3 m post, heaped with glowing coals (a low dome of `fire` material, 0.25 m high, no flame) and a real lamp of 700 just above it. This should be the brightest single point on the walls.
7. **Fire-fighting and stores on the wall.** At the foot of the wall inside, behind each of the three attacked stretches: a row of ten `props.PITHOS` (water against fire), a stack of shot, and a pile of long poles.
8. **Finish the story of the second wall.** Beside the half-built wall: a timber hoist (two 5 m spars lashed at the top with a rope and a block of stone hanging), three more heaps of squared blocks (`RUBBLE_HEAP` from phase 4, or build it here if phase 4 was skipped), a mortar trough, and two torches with real lamps of 200.

Do **not** add timber galleries projecting from the top of the walls, boiling oil, or banners.

Done when: the wall above the mound clearly shows the sacks and the two beams, the two attacked stretches show ragged tops, the beacon is the brightest point on the wall, and the daytime build is unchanged.
