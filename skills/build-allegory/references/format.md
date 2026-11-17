# The files of an allegory

```
allegories/<id>/
  allegory.json      its name and words, and which network file each stage uses
  city.json          the city's network        (only if you build the city)
  siege.json         the siege's network       (only if you build the siege)
  city.png           the pictures, 4:3         (named by "picture" in the network file)
  siege.png
  work/              plates, diagrams, overlays, intermediate paintings; not committed
```

`allegories/greece/` is the original and a working example of everything below.

## allegory.json

```json
{
 "id": "mars",
 "name": "A colony on Mars",
 "title": "Distributed Algorithms of the Red Planet",
 "town": "Ares Base",
 "people": "the growers, part-time councillors, soldiers and archivists of a colony on Mars",
 "hero": { "alt": "what the city picture shows, for someone who cannot see it", "caption": "one line under it on the landing page" },
 "stages": { "city": "city.json", "siege": "../greece/siege.json" },
 "words": []
}
```

`stages` names the network file of each stage, relative to this folder. A stage you did not build points at another
allegory's file, as the siege does above; its picture and names come along with it.

## A network file

```json
{
 "stage": "city",
 "units": "px",
 "night": false,
 "setting": "a research colony on Mars",
 "picture": "city.png",
 "places": {
  "fishery": { "label": "algae farm", "at": [300, 980], "door": [352, 930], "landmark": "an algae farm under a long glass roof" }
 },
 "roads": [
  { "kind": "road", "width": 6, "pts": [[352, 930], [520, 800], [800, 600]] }
 ]
}
```

| Field | Meaning |
|---|---|
| `units` | `"px"`: points are `[x, y]` in the 1600 x 1200 picture, y down. `"m"`: points are `[east, north]` or `[east, north, up]` in plan units, origin at the middle of the frame; the tool projects them through the fixed camera. Use `px` for a painted picture, `m` for a world built in Blender. |
| `night` | `true` gives the page its night styling over a dark picture. |
| `setting` | The phrase the image prompts are written around. For the siege, name the siege. |
| `picture` | The finished picture, beside this file. 4:3, 1800 px wide or more. |
| `camera` | Optional, for `"units": "m"` only: `{"elev": 34}` sets the camera's height above the horizon in degrees (the standard is 48.6). A lower camera shows more of the walls and of rising ground and makes the picture look more three-dimensional; it also lets tall things hide more of the ground behind them. The direction (from the south-east), the parallel projection and the 4:3 frame never change. |
| `places` | One entry for every role id of the stage, no more and no fewer. |
| `places.*.label` | The place's name in this world: a bare common noun with no article ("algae farm"). |
| `places.*.at` | Where the landmark stands: the centre of its footprint. Must be in one of the seven zones. |
| `places.*.door` | Where its couriers join the road. Must lie on a road (within 8 px, or 2 plan units). |
| `places.*.landmark` | Optional. What an image generator is told to put there, in place of the role's general description. |
| `places.*.reach` | `false` for a place no courier goes to (the siege's `enemy city`). |
| `roads` | Lines of points. `kind` is `road` or `street` (a lesser way; drawn lighter in diagrams). `width` is in the file's units and is used only by the Blender helper. Roads join where they touch or cross. |
| `ground`, `fill`, `route`, `what`, `build` | Optional sentences for the image prompts, replacing the stage's defaults: what the bare ground is like, what fills the gaps, what a road is here (`route`: "Each dark band becomes ...", for a setting whose ways are not walked, such as channels between ships), and what the two passes are asked to paint. Run `prompts` to read the result. |
| `lock` | Optional. `true` pastes the roads of the first painting pass back over the second (default for the siege). |

Role ids of the city: `fishery`, `granary`, `winery`, `pottery`, `temple`, `temple library`, `northwest library`,
`southeast library`, `proposer P`, `proposer Q`, `crossroads`. Of the siege: `commander's camp`, `camp A`, `camp B`,
`camp C`, `enemy city`. The ids are only keys: a `northwest library` need not be in the north-west.

With `"units": "m"`, the frame shows a square of ground 304 units on a side standing on its corner: `[0, 215]` (north) is
the upper right corner of the picture, `[215, 0]` (east) the lower right, `[0, -215]` the lower left, `[-215, 0]` the upper
left, and `[0, 0]` the centre. A height `z` lifts a point up the picture by 3.48 px per unit.

## What `check` enforces

- every role id present, each with a label, `at` and `door`;
- labels: no article, 22 characters or fewer (warning), and the two rules in `telling.md`;
- every place in a zone, none in the middle of the right or bottom edge, the centre trio in the centre;
- places that share a scene in different zones; every zone used; no two places within 110 px;
- every reachable place's door on a road, and a way by road between every two of them;
- the picture 4:3.

## What `build` writes

`app/allegories/<id>.js` (the allegory's name and words and, for each stage, the picture's files, the labels, each place
and door in pixels, and the route between every two places), the pictures as `app/img/<id>-<stage>-<width>.webp`, and
the allegory's entry in `app/js/data/allegories.js`, the list of allegories the page holds and which one it opens with.
These are the only files of the page that change.

The page holds every allegory that has been built. With more than one, a menu in the side drawer lets the reader choose;
`?allegory=<id>` in the address chooses one for a link. `default <id>` sets the one the page opens with, `remove <id>`
takes one off the page (its source folder stays), `list` shows them.
