# Making the picture with an image generator

The picture is painted in two passes, because one pass cannot both keep the roads where the network has them and build
freely. Pass 1 turns a **plate** (your roads as dark bands on blank ground) into the bare landscape. Pass 2 is given that
painting with a numbered disc on every place, and replaces each disc with a landmark.

Write the network in picture pixels (`"units": "px"`), and give the stage a `setting`. For the siege, the setting names the
siege ("thirteenth-century China, during the Mongol siege of Xiangyang"); it is always painted by night, so set `"night": true`.

## With the Gemini API

```sh
export GEMINI_API_KEY=...
python3 tools/allegory.py paint <id> city
python3 tools/allegory.py paint <id> siege
```

This writes, in `allegories/<id>/work/`: `<stage>-plate.png`, `-ground.png` (pass 1), `-ground-overlay.png`,
`-ground-marked.png` (the input of pass 2), and the result as `allegories/<id>/<stage>.png` with `work/<stage>-overlay.png`.
Name the result in the network file: `"picture": "city.png"`.

The model is `gemini-nano-banana-2.1`, set in the tool. Do not change it: `gemini-3-pro-image` repaints the whole picture in
pass 2, moves the roads and leaves discs in it.

`paint` stretches what the generator returns to exact 4:3 (generators come back a few pixels off) and ends by running
`trace` on the result. Do not resize or crop pictures yourself.

**Look at both overlays.** The ground is the cheap pass to get right. If `-ground-overlay.png` shows a missing or shifted
road, delete `work/<stage>-ground.png` and run again. If only pass 2 disappoints, run again as is: an existing ground is
kept and built on. Expect to run a pass two or three times, but keep the count modest: every run is paid for, and moving
the network's points to fit a good painting is free.

## Without the API

```sh
python3 tools/allegory.py plate <id> city        # work/city-plate.png (and -guide.png, -mask.png)
python3 tools/allegory.py prompts <id> city      # prints both prompts
```

1. Give any image generator that edits images `work/city-plate.png` with the pass 1 prompt, asking for 4:3. Save the
   result as `work/city-ground.png` and run `overlay <id> city work/city-ground.png`. If it is not exactly 4:3, ask again.
2. `python3 tools/allegory.py mark <id> city work/city-ground.png`, then give `city-ground-marked.png` with the pass 2
   prompt. Save the result as `allegories/<id>/city.png` and run `overlay` again.

If you have no image generator at all, say so and stop here: do not ship the plate or a diagram as the picture.

## Steering the result

- **What a landmark is**: give the place a `"landmark"` sentence in the network file. Say what kind of thing it is in
  this setting, and for the two proposers keep "one strong blue feature" and "one strong red feature".
- **The ground and the gaps**: the stage's `"ground"` and `"fill"` sentences replace the defaults in the prompts. Use
  them for relief ("the highest ground is at the upper right"), water, weather.
- **Roads that drifted**: move the network's points to where the painting put the road, if the painting is otherwise
  good; `check`, `overlay`, and look again. Or inpaint with `work/<stage>-mask.png` and "A wide route, clearly different
  from the ground around it, matching the painting's style, light and perspective."
- **Roads that pass 2 bent**: `python3 tools/allegory.py lock <id> <stage> <final> work/<stage>-ground.png` pastes
  pass 1's roads back over the final picture. It is on by default for the siege (`"lock": true`), where nothing tall
  stands by the roads. In a town it can cut a building that stands in front of a road.
- **A landmark in the wrong place**: move its `at` and `door` to where it was painted, if that is still inside its zone.
  Otherwise run pass 2 again, or mask round the disc's position and inpaint that landmark's line from the pass 2 prompt.
  Do not give the place to a different building.

## What was learnt making the first ones

- **The camera is part of the prompt.** Without it the siege came out as a straight-down plan. Both prompts state it; do
  not shorten it away if you edit them.
- **Ground first.** With nothing to place, the bands survive almost exactly. The usual losses are a stretch that runs
  along the top edge of the frame, and a dead end painted on out to the edge: keep roads away from the edges.
- **Discs, not plots.** Larger "building plot" shapes gave landmarks that sat across the roads.
- **Say that routes are walked.** "A route people move along" produced canals in a river town.
- **A painterly setting drifts more** than a photographic one. An ink-and-wash river town let its lanes wander.
- **No horizon.** A pass 1 that painted sky made pass 2 reframe the picture. The ground fills the frame.
- **Keep the roads visible**: strong contrast with the ground, and no people or animals, which would hide the couriers.
- **Simple networks hold best.** A dozen clear roads survive two passes; a dense grid of lanes does not.
