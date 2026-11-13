# Phase 2: agora market and palaistra

Files: `world/polis/civic.py` (`agora`, `gymnasium`), `world/polis/props.py`.

**Routes cross the agora and run along every street.** Apply rule 2 strictly here, and run the route check after each numbered item, not only at the end.

Streets inside the walls: the two main streets along x = 0 and y = 0 (8 m wide), and four lesser ones along x = ±38 and y = ±38 (5 m wide).

## Agora

The open square is x −35.5 to 35.5, y −35.5 to −4, south of the main east–west street. The north–south main street crosses it along x = 0. It already has an altar at (−17, −17), statues along y = −6.2 and x = ±6.2, two exedrae, a fountain house at (22.5, −9.2), six stalls round (12–22, −15 to −21), and two plane trees.

1. **More stalls. This is the most important item in the whole plan.** Raise the number from six to about fourteen: keep the east group and add a west group round x −28 to −22, y −12 to −24, clear of the altar. Put six to ten goods at each stall (amphorae, sacks, baskets), not three, some on the counter and some on the ground in front. The stall cloths in `props.STALLS` are mostly cream; add four more variants so that about half the stalls are coloured: `#a9553c` (madder red), `#5f7896` (woad blue), `#c9a544` (weld yellow), `#8a4a3a`.
1a. **Loaded carts.** Build the three loaded-cart parts described in `README.md`. Stand one `CART_AMPH` and one `CART_SACKS` at the edges of the agora, behind the stall rows, at least 6 m from both main streets.
2. **Speakers' platform.** A stone block 3 x 2 x 1 m (`ashlar` sides, `paving` top) with two steps on one side. Near (−8, −30).
3. **Sundial.** A marble column 1.5 m tall with a small block on top cut with a hollow on its south face. Hellenistic sundials of this kind are common finds. Near (10, −27).
4. **Measures table.** One `props.TABLE` at 1.3 times the size with five small dark discs on its top (the standard measures), by the east stalls.
5. **Shade.** Two more plane trees (`houses.TREES.append((x, y, z, "plane"))`) with a `props.BENCH` under each, at least 6 m from both main streets.

## Palaistra

Its court is inside x 4.6–35, y −70.6 to −41.2 (`gymnasium` gets the court rectangle back from `peristyle`).

6. A sand pit for jumping and wrestling: `land.paint("sand", ...)` over about 6 x 3 m in the court. Two `props.BASIN` near one colonnade. A row of four herms along another side.

No flower beds or lawns anywhere in the town. House courts are left as they are.

Done when: the agora reads as a busy, colourful market from the full picture, and the route check is unchanged.
