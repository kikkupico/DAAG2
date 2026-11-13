# Phase 1: the four army camps

File: `world/polis/siege.py` (function `camp`, and new parts above it).

## What is there now

Each camp is a round palisade with a ditch, a gate with two watch-towers and two torches, eight to ten tents either side of a street, a pile of stacked arms by each tent, an officer's tent (a pavilion with two standards and an altar in the commander's camp), **two fires**, a cart, a log pile and six jars. Camp A also has two stone-throwers and shot; camp B three log piles and a shed; camp C three hay stacks and rows of jars.

`camp()` builds in local coordinates: gate at (0, −r), street along +y, officer's tent near (0, −r + 27). r is 23 for the commander's camp and 19 for the others. Much of each camp is bare ground, and two lights are far too few.

## Add to every camp

0. **Lit tents.** Make the lit-door tent variants described in `README.md`. In every camp, about one tent in three (old and new) is a lit one.

1. **Cooking fires.** Soldiers ate in tent groups, each round its own fire. Put one small fire in front of each pair of tents, on the street side, 3 m from the tent doors: use `inst(FIRE, x, y, 0, 0, .6)` **without** a lamp. Give every third one a real lamp with `light(x, y, .6, 350)`. Keep the two existing large fires.
2. **Round each cooking fire**: a tripod with a hanging pot (new part `COOKPOT`: three 1.4 m poles meeting at the top, a dark pot 0.4 m across hanging just above the coals), and three or four low seats (logs 0.8 m long lying on the ground).
3. **More tents.** Fill the empty arcs of each camp with a second ring of smaller tents (use `TENTS` at scale 0.8), six to ten per camp, doors facing the centre, at least 2.5 m inside the palisade. Check each with `land.free`.
4. **Shield and spear racks.** New part `RACK_ARMS`: two posts 1.8 m tall and 4 m apart with a rail between, six round bronze shields (0.7 m across) hung on the rail, and eight long pikes leaning against it (thin poles 5 m long). One per camp near the officer's tent, lit by its torches. Macedonian pikes were about 5 to 6 m long.
5. **Picket line (no animals).** New part `PICKET`: a rope between two posts 10 m apart, a long wooden feeding trough under it, three heaps of hay. One per camp, against the palisade on the side away from the gate.
6. **Water.** A group of eight large jars (`props.PITHOS`) sunk a little into the ground beside two leather buckets, near the camp gate. A second `props.CART` loaded with six amphorae.
7. **A torch at the officer's tent** in camps A, B and C (the commander's camp has two already): `torch(x, y, 0, 180)`.

## Add to one camp each

8. **Commander's camp: the guard and the treasury.** A second small pavilion (use `OFFICER`) beside the main one, with a `torch` each side of its door. Two rows of four `RACK_ARMS`-style shield stands is too much; add one more `RACK_ARMS` only. A table (`props.TABLE`) under the pavilion's porch.
9. **Camp A (engineers): a field forge.** New part `FORGE`: a stone hearth 1.2 m square and 0.8 m high with a glowing top (`fire` material disc 0.6 m across), a bellows (a dark wedge 1 m long) at one side, an anvil (a dark block 0.4 m on a log 0.6 m high), under an open shed (four posts and a hide roof, like `SHED` but 4 x 4 m). Give it a real lamp: `light(x, y, 1.2, 500)`. Beside it: a stack of timber baulks (`LOGS`), coils of rope (dark rings 0.8 m across lying flat, in a stack of three), and a third stone-thrower half built (place `CATAPULT` at 0.9 scale and leave out nothing; then lay two loose arms, bars 2 m long, on the ground beside it).
10. **Camp B (timber yard): the stake-makers.** A saw-trestle (two X-frames 1.2 m high with a log across), a heap of pale wood chips (`land.paint_disc("sand", ...)`, radius 2), three stacks of finished palisade stakes (new part `STAKE_STACK`: twenty pointed poles 3.2 m long lying side by side, 0.6 m high), and two finished ladders lying flat (two rails 7 m long, rungs every 0.4 m).
11. **Camp C (stores): the granary and bakery.** Two domed clay ovens (radius 0.9, height 1.1, no larger, glowing mouth in `glow` material on the south side; one real lamp of 250 between them), a stack of thirty sacks two high (`props.SACK`), and a second block of amphorae with `props.jar_rows`.

Done when: each camp shows at least eight small fires in the full picture, the bare ground is mostly filled, and camps A, B and C can be told apart at a glance by the forge glow, the timber stacks and the ovens.
