# Distributed Algorithms of Ancient Greece

A static page (`app/`, no build step: open `app/index.html` or serve the folder) that tells sixteen results of distributed
computing twice, as an Allegory and as an Abstraction.

- `app/js/data/scenes*.js`, `papers.js`: the steps of every scene. Plain data, shared by both tellings.
- `app/js/data/telling.js`: the Allegory's prose. Place names are tokens (`{fishery}`) filled from the current allegory.
- `allegories/<id>/`: an allegory's source: its name and words, and the road network of its city and its siege.
- `tools/allegory.py`: checks a network, draws it, prepares and checks its picture, and builds it into the page.
- `app/allegories/<id>.js`, `app/js/data/allegories.js`: the allegories the page holds and the one it opens with; a menu in the drawer switches. Written by the tool.
- `app/js/data/plain.js`: the Abstraction's own roads and positions. Fixed; no allegory changes it.
- `world/`: the Blender build of the original Greek town and siege.

## Skills

- **Building a new allegory** (another setting, another road layout, new pictures, renamed places): follow
  `skills/build-allegory/SKILL.md`.

## Checks

- `python3 tools/allegory.py check <id>`: an allegory's networks keep every rule.
- `node app/tools/check-leaks.js`: the Abstraction's text uses none of the telling's own vocabulary (run it after editing scenes or the telling).
