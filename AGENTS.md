# Distributed Algorithms of Ancient Greece

A static page (`site/`, no build step: open `site/index.html` or serve the folder) that tells sixteen results of distributed
computing twice, as an Allegory and as an Abstraction.

- `site/js/data/scenes*.js`, `papers.js`: the steps of every scene. Plain data, shared by both tellings.
- `site/js/home.js`, `site/css/home.css`: the front page, shown at the bare address (no hash). It plays Paxos's first scene in both tellings and wipes between them. `site/js/intro.js` (`#intro`) is the how-to-use page.
- `site/js/data/telling.js`: the Allegory's prose. Place names are tokens (`{fishery}`) filled from the current allegory.
- `allegories/<id>/`: an allegory's source: its name and words, and the road network of its city and its siege.
- `tools/allegory.py`: checks a network, draws it, prepares and checks its picture, and builds it into the page.
- `site/allegories/<id>.js`, `site/js/data/allegories.js`: the allegories the page holds and the one it opens with; a menu in the drawer switches. Written by the tool.
- `site/js/data/plain.js`: the Abstraction's own roads and positions. Fixed; no allegory changes it.
- `world/`: the Blender build of the original Greek town and siege.
- `viz/`: Distributed Computing Papers Visualised, a three.js app on the same data (serve the repo root, open `/viz/`).
  It plays a scene's global trace (`viz/data/traces.js`: every node's state and every message's send and arrival),
  from behind any node or from above the whole system. Abstraction first; the Allegory waits for a 3D world (`viz/js/worlds.js`).

## Skills

- **Building a new allegory** (another setting, another road layout, new pictures, renamed places): follow
  `skills/build-allegory/SKILL.md`.

## Checks

- `python3 tools/allegory.py check <id>`: an allegory's networks keep every rule.
- `node viz/tools/check-traces.js`: every global trace, projected onto its scene's narrator, gives back the scene's rows exactly.
- `node site/tools/check-leaks.js`: the Abstraction's text uses none of the telling's own vocabulary (run it after editing scenes or the telling).
