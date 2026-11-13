# Phase 7 (optional): sutlers' market and the town ditch

Do this phase only if phases 1 to 6 are finished and their checks pass. Each part stands alone. Drop a part if its checks fail twice.

File: `world/polis/siege.py`.

## A. A sutlers' market

Hellenistic armies were followed by traders, and a market outside the camp is mentioned often. It gives the only civilian colour in the besiegers' half of the picture.

1. Site: outside camp C (the stores camp, centre (−162, 0), radius 19), on open ground beside its spur road, on the far side of the road from the camera, between the camp's palisade and the outer siege palisade. Confirm with `core.in_view` and `land.free`; if camp C has no room in view, try camp B.
2. Eight stalls in a loose row facing the road, 5 m back from its centre line: use `props.STALLS`. Goods at each: amphorae, sacks, baskets, six to ten per stall.
3. Three small tents behind the stalls (`TENTS` at 0.8 scale), two carts, a fire (real lamp of 400) and two prop-only torches.
4. `land.paint("earth", ...)` over the market ground, and add the area to `CLEAR` so no trees are planted there.

## B. The town ditch

Philo advises three ditches before a town wall, and most Hellenistic towns had at least one. The model has none, although `tower_attack` already speaks of a "filled ditch". This part is the riskiest in the whole plan because it changes terrain. Skip it at the first sign of trouble.

1. One dry ditch, 6 m wide and 2.5 m deep, with its centre line 11 m outside the wall line: `land.earthwork(grow(OCT, 11), [(0, 3.0, -2.5)])`. Read `land.earthwork` first to confirm what its arguments mean; the palisade ditches in `lines()` are made the same way.
2. The ditch must be **interrupted** (left as level ground) in four kinds of place. Build it as separate open stretches (`closed=False`) that stop short:
   - 9 m either side of each of the four gates;
   - across the whole width of the mound (it is filled there);
   - across the siege tower's plank road, x 84–106.5, y 12–26 (filled there too);
   - anywhere within 8 m of something already placed (`land.free` false).
3. Call it in `build()` **before** `mound`, `tower_attack` and `battery`, so their own levelling wins.
4. At the two filled crossings, show the fill: pale earth (`land.paint("earth", ...)`), brushwood bundles (`FASCINE`) and rubble at both edges.
5. Check: the route check is unchanged (no road is nearer than 29 m, so it should be), the wall's foot is not undercut (render a crop of a wall stretch and of each gate), and the daytime build is unchanged.

Done when: each part you kept is visible in a crop and all checks pass.
