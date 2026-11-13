# Phase 2: the ground between the two palisades

File: `world/polis/siege.py` (function `lines`, and new parts).

## What is there now

Two palisades run right round the town, 27.5 m and 52.5 m out from the wall line, each with a ditch and bank. The ring road runs midway between them (40 m out), 5 m wide. Timber watch-towers stand behind each palisade, most with a torch. Where each camp's road passes the outer palisade there are two towers and two torches. The inner palisade has three gaps, at (84.6, −84.6), (105.5, 19) and (−22, −105.5), where the siege works pass through.

The strip between the palisades is 25 m wide and about 800 m round, and apart from the towers it is empty. In a real siege this strip was where the watch lived.

**The ring road is the messengers' route. Everything here must be at least 3.5 m from the road's centre line (5 m if taller than 2 m), and nothing may stand between the road and the camera within 6 m of the road.** That means: put tall things on the **north or west** side of the road (the far side from the camera) and only low things (under 1.2 m) on the south or east side.

Useful: `grow(OCT, d)` gives the octagon pushed out by d metres; `along(points, step)` walks a line and returns `(x, y, ux, uy, distance)` at each step.

## Add

1. **Guard posts.** Every 60 m or so along the ring road, on the side toward the town (between the road and the inner palisade), a picket: one small tent (`TENTS` at 0.8 scale), a small fire (`inst(FIRE, ..., .6)`), a stack of arms (`ARMS`), two log seats. Give every second picket's fire a real lamp of 300. About twelve pickets in all. Skip any that would fall within 12 m of a gap in the inner palisade or of a spur road.
2. **Gates in the outer palisade.** Where each of the four spur roads passes the outer palisade, add gate posts: two squared timbers 4.5 m tall, 3 m either side of the road's centre line, with a lintel beam across the top at 4.3 m. Leave the opening clear. Lay the two gate leaves (hurdles of poles, 3 x 3 m) swung back flat against the palisade.
3. **Sally gaps in the inner palisade.** At the three existing gaps, add a movable barrier drawn aside: new part `CHEVAL`, a 4 m log on two X-shaped feet with sharpened stakes through it, lying beside the gap, not across it.
4. **Sharpened stakes before the inner palisade.** On the town side of the inner ditch, within 6 m of the palisade and nowhere near the town wall, a low belt 3 m wide of stakes leaning toward the town (felled branches and stakes set against a sortie). New part `STAKES_BELT`: a 2.4 m length holding eight stakes 1.5 m long at about 45°. Place along the whole inner line with `Scatter`, following how `stockade` walks the line; skip the gaps and anywhere `land.road_dist < 3`.
5. **Supply dumps along the road.** At four places, on the far side of the road from the camera: a `STAKE_STACK` (from phase 1), a heap of earth-filled baskets (twelve `props.BASKET` at 1.3 scale in a block), and a `props.CART`.
6. **An artillery park.** In the strip on the east side, near (118, −35) but clear of the road: two bolt-shooters waiting (use `CATAPULT` at 0.6 scale), a pile of shot, a mantlet leaning on a rack.
7. **Torches at the tower feet.** At every third watch-tower, a ground torch beside the ladder: `inst(TORCH, ...)` with no lamp.

Done when: looking at the full picture, the strip between the palisades shows a fire or a lit tent every 60 m or so all the way round, the four gates read as gates, and the route check still shows 0 hidden.
