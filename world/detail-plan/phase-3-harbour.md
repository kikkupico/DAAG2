# Phase 3: shore and harbour

Files: `world/polis/props.py`, `world/polis/country.py` (function `fishery`).

## What is there now

The fishery's door is at (0, −114). The sea is to the south; `land.sd_at(x, y)` gives the distance inland from the waterline (it is small on the beach and negative in the water).

| Thing | Where |
|---|---|
| Fish shed | x −25 to −7, y −130 to −122.5 |
| House | x −23.5 to −9.5, y −112 to −99.5 |
| Six salting vats | round x 13–26, y −110 to −104 |
| Jar store | x 34.5–45, y −113.5 to −105.5 |
| Drying racks, nets | along the beach west of the shed |
| Six boats on the sand | x −60 to 30, y about −131 to −139 |
| Stone mole | from (18, −136) south to (20, −156), then south-west to (4, −168); top at z 1.15 |
| Merchant ship | (6.5, −151.5), in the lee of the mole |
| Three boats afloat | (13, −146), (9.5, −161.5), (−18, −150) |

## Add

1. **A second ship, sail furled on its yard like the first.** Give `_ship` parameters for the two hull colours, keeping today's colours as defaults. Make a second part with a black lower hull (`wood:#2a2420`) and a red-ochre upper band (`wood:#8a3a26`). Anchor it off the end of the mole, about (−8, −172), turned at a different angle from the first. Check it is in the picture with `core.in_view`.
2. **Painted boats.** Make two more variants of `_boat`: one pitch-black (`wood:#2a2420`), one with a red upper edge. Use the three variants at random for the boats on the sand and afloat.
3. **A boat under repair.** One boat at 1.5 times the size on the upper beach, level, held up by four short timbers each side. Beside it: `TIMBER`, a stack of eight logs 6 m long and 0.25 m thick (`wood:#9a7c54`); a pitch cauldron (a dark pot 0.8 m across on three stones); and a pale patch of wood chips (`land.paint_disc("sand", ...)`, radius 2.5).
4. **Sails drying.** Two cloth faces lying on the sand above the waterline, each about 5 x 7 m, 5 cm above the ground, cut into four strips with small height differences so they do not look like one flat card. One `cloth:#d9ceb4` (undyed), one `cloth:#a9553c` (madder red).
5. **Cargo on the mole.** Along the landward stretch of the mole, on its top (z 1.17): two blocks of about forty amphorae with `jar_rows`, a block of twenty sacks, baskets. Leave a clear strip down the middle.
6. **Stone anchors.** Three flat pierced stones about 0.8 m across (`rubble`), lying at the foot of the mole on the beach.
7. **Loaded carts.** One `CART_AMPH` (see `README.md`; build it if the agora phase did not) at the landward foot of the mole, and one beside the jar store, both clear of the fishery road.
8. **Lifting frame (optional).** Two 6 m spars leaning together and lashed at the top, a rope hanging from the apex, standing on the mole near the ship. Keep it slight. Do not build a crane with a jib or a wheel.

`land.take_disc` each thing on the beach. The beach here is already inside a `KEEP_CLEAR` box.

Done when: a crop of the harbour at 2400 px shows two ships, boats in at least two colours, the boat under repair with its timber, the sails, and cargo on the mole.
