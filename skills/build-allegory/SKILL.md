---
name: build-allegory
description: Build a new allegory for Distributed Algorithms of Ancient Greece from a setting the user names (a Mars colony, a Tamil river town, a monastery): a new picture of the town and/or the siege, a road network that suits the setting, the couriers' animation following those roads, and the telling renamed to match. Use when asked to add, build, change or reskin the allegory, the world, the town, the siege, or its roads and landmarks.
---

# Build an allegory

The page tells sixteen results of distributed computing twice: as an **Allegory** (people in a town and in a siege, sending
couriers along roads) and as an **Abstraction** (nodes A, B, C). This skill replaces the Allegory's world with one in a
setting the user chooses. You produce, per world, three things: a **picture**, the **network** of roads in it, and the
**names** of the places on it. Everything else follows from those: the couriers walk the routes worked out from your network,
and the telling takes its place names from it.

All commands run from the repository root. `python3 tools/allegory.py` with no arguments lists them.

## 1. Settle four things first

You need four answers. Take any the user has already given; ask for the rest in one go. If you cannot ask (you are running
without a user to answer), use the default and say in your report that you did.

1. **The setting.** A phrase: "a research colony on Mars", "a river town of the Tamil Sangam age". No default: without one, stop.
2. **How the picture is made.** *Image generation* (an image model paints it from a plate of your roads; minutes) or a
   *3D world* (you model it in Blender and render it; hours, and much more control). Default: image generation.
3. **Which worlds.** There are two, and they are different places: the **city** (a town at peace, eleven places) and the
   **siege** (a stronghold shut in by four camps, by night). Build both, or only the one the user picks; the other then
   stays as it is. Default: both. The siege wants a siege from the setting's own history or lore; ask or choose one and say which.
4. **Add or replace.** The page can hold several allegories; the reader picks one from a menu, and the page opens with
   the default one. *Add*: the new allegory joins the menu and the page still opens with the one it opened with before.
   *Replace*: the new allegory becomes the one the page opens with; the others stay in the menu unless the user also asks
   for them to be taken off. Default: add.

## 2. What is fixed, and what is yours

Fixed. Do not change these, and do not edit the files that hold them:

- **The frame and the camera.** Every picture is 4:3, and stands for 1600 x 1200 picture pixels. The camera is a parallel
  projection from the south-east, about 49 degrees above the horizon: north is the upper right corner, east the lower
  right. Never another angle, never perspective, never a straight-down plan.
- **The places.** Each world has a fixed set of places, known by role ids (`fishery`, `temple`, `camp A`, ...). You decide
  what each one *is* in your setting and what it is called, never which ones exist. See `references/telling.md`.
- **Where places may stand.** Cut the frame in thirds each way. A place stands in one of seven zones: the four **corners**,
  the **middle of the top edge**, the **middle of the left edge**, or the **centre**. Nothing stands in the middle of the
  right edge (the replay and theater buttons are there) or the middle of the bottom edge. This spreads the landmarks
  evenly over the picture. The checker enforces it.
- **The Abstraction.** It keeps its own roads and positions whatever you build. Never edit `app/js/data/plain.js`,
  `scenes.js`, `scenes-extra.js`, `papers.js` or `app/js/rows.js`.
- **Generated files.** `app/allegories/<id>.js` and `app/js/data/allegories.js` are written by the tool. Never edit them by hand.

Yours:

- **The road layout.** Anything that suits the setting: a river with two bridges, terraces up a mountainside, the
  corridors of a station, causeways between islands. Do not copy the Greek town's grid and ring. The only demands are
  that it is one network joining every place a courier reaches, and that it can be seen from the camera.
- **The geography, the architecture, the weather, the light,** and what each landmark is.
- **The names**: of each place, of the town, of the allegory.

## 3. Start the allegory

```sh
python3 tools/allegory.py new <id>        # allegories/<id>/: allegory.json, and city.json and siege.json as examples of the format
```

`<id>` is a short lower-case name (`mars`, `sangam`). The two network files are copies of the Greek ones, there to show
the format; `allegory.json` still points both stages at Greece's own. For each world you are building you will rewrite
its network file and then point `"stages"` at it. A world you are not building keeps pointing at Greece's, and you can
delete your copy of its file. The files are described in `references/format.md`.

## 4. Decide the places and lay out the network

Read `references/telling.md` for what each role does in the stories and the few rules its name must keep. Then, for each
world you are building, write its network file: every place with its `label`, where it stands (`at`), where its door meets
the road (`door`), and the roads.

Work in the units that suit the method: **picture pixels** (`"units": "px"`) for image generation, **plan units**
(`"units": "m"`, x east, y north, z up) for a 3D world. `python3 tools/allegory.py xy m2px 150 0` converts a point.

Placing the city's eleven places in seven zones means some zones hold two. A layout that always passes:

| Zone | City | Siege |
|---|---|---|
| top left | winery | camp C |
| top (middle) | northwest library | |
| top right | temple, temple library | commander's camp |
| left (middle) | pottery | |
| centre | crossroads, with proposer P and proposer Q on either side of it | enemy city |
| bottom left | fishery, southeast library | camp B |
| bottom right | granary | camp A |

You may arrange them otherwise, as long as the checker passes: places that appear together in a scene never share a zone
(the three at the centre excepted), every zone is used, and no two places stand closer than 110 px. Put each place well
inside its zone, 80 px or more from the frame's edge, so its name plate has room.

Roads:

- A road is a line of points. Roads join wherever they touch or cross; there are no bridges over one another.
- Every place a courier reaches needs its `door` on a road. In the siege the `enemy city` has `"reach": false`: no road
  enters it, and the camps reach one another only by going round it.
- Keep the roads inside the frame, and give the place where they meet the door a short stub if the landmark stands back.
- Give the network the character of the setting, and some choice of ways: two places should not always meet at one hub.
- Leave room for the landmarks: a road should pass beside a place, never through its `at` point.

Then check it and look at it. Repeat until it passes and looks like a place:

```sh
python3 tools/allegory.py check <id>      # every rule; fix each ERROR, weigh each warn
python3 tools/allegory.py diagram <id>    # allegories/<id>/work/<stage>-diagram.png: open it and look
```

## 5. Make the picture

Follow one of these, per the user's choice. Both end with a 4:3 picture named by `"picture"` in the network file, and an
overlay you have looked at.

- **Image generation:** `references/image.md`
- **3D world in Blender:** `references/blender.md`

Whichever you use, the test is the same:

```sh
python3 tools/allegory.py overlay <id> <stage>     # work/<stage>-overlay.png
```

Open the overlay. Every magenta route must lie on ground a courier could walk and that the camera can see, every yellow
door must touch its landmark, and every red ring must sit on its landmark. For a painted picture, where every route must
also look like a road, measure it:

```sh
python3 tools/allegory.py trace <id> <stage>       # the share of each road with a painted road under it; exit 1 if any is BARE
```

`trace` is rough (a shadow reads as bare, sand-coloured ground as road), so use it to find where to look on the overlay.
A road it calls BARE, or a bare stretch it lists, is settled by looking, and then by fixing one side or the other:

- **A route off its road:** move the network's points onto the painted road, `check`, and look again. This is free.
- **No road painted there at all:** remake the picture, or take that road out of the network if every place is still joined without it.
- **A landmark painted outside its zone,** or not painted at all: remake the picture (for a painted one, run pass 2
  again). Never re-point the place at some other building that happens to stand in the right zone: the place's
  landmark is what was asked for there (the red household for `proposer Q`, a library for a library).

Do not go on to step 6 while a route crosses open ground or a building, or a place has no landmark of its own. If you
have run out of attempts, stop and report exactly which routes and places are wrong.

## 6. Name the allegory

Fill in `allegories/<id>/allegory.json`: `name`, `title`, `town`, `people`, `hero`, and point `stages` at your network
files. `references/telling.md` explains each and the optional `words`, which carry the setting further into the prose.

## 7. Build and verify

```sh
python3 tools/allegory.py build <id>      # checks, bakes the pictures into app/img, and adds the allegory to the page
python3 tools/allegory.py shot <id>       # screenshots of the built page into allegories/<id>/work/page-*.png
```

`shot` needs no browser driven by hand: it finds Chrome, Chromium or Edge on the machine, serves the page, and writes one
picture per scene, each at its third step, plus the first scene again in the Abstraction. By default it takes a
merchants' scene (`clocks-jump`), a legislators' (`paxos-round`), a scholars' (`quorum-overlap`) and the siege
(`liars-four`); name others after the id (`shot <id> snapshot-markers cap-stale`). **Open every picture it wrote** and check:

- the couriers' trails run along roads of the picture, and start and end at their landmarks;
- the name plates read well, sit clear of one another, and nothing sits under the two buttons at the middle of the right edge;
- the prose under the picture reads as natural sentences with your place names and words in it;
- the Abstraction's picture (`page-clocks-jump-plain.png`) is the plain diagram it always was, with none of your names in it.

To look at the page yourself: `python3 -m http.server 8000 -d app`, then http://localhost:8000. A scene's address takes
`?reg=plain` for the Abstraction and `?step=3` for a step, before the `#`.

If `shot` finds no browser and you have no other way to see the page, say so in your report; do not claim it was checked.

`build` only ever adds: the allegory joins the page's menu, and the page goes on opening with the one it opened with
before. If the user chose **replace**, also run:

```sh
python3 tools/allegory.py default <id>    # the page now opens with this one
python3 tools/allegory.py remove <other>  # only if the user asked for another allegory to be taken off the page
python3 tools/allegory.py list            # what the page holds, and which is the default
```

`remove` takes an allegory off the page only; its source in `allegories/` stays, and `build` brings it back. Never
delete another allegory's folder.

## 8. Report

Say what you built and by which method, whether it was added or made the default, which defaults you assumed, where the files are, what you looked at to verify
it, and anything that is not right yet (a route that drifts, a label that reads oddly). Do not commit unless asked.
