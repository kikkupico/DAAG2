# Distributed Algorithms of Ancient Greece

A static page (`site/`, no build step: open `site/index.html` or serve the folder) that tells sixteen results of distributed
computing twice, as an Allegory and as an Abstraction.

- `site/js/data/scenes*.js`, `papers.js`: the steps of every scene. Plain data, shared by both tellings.
- `site/js/home.js`, `site/css/home.css`: the front page, shown at the bare address (no hash). It plays Paxos's first scene in both tellings and wipes between them. `site/js/intro.js` (`#intro`) is the how-to-use page.
- `site/js/theater.js`, `site/css/theater.css`: the stage. A result's own page (its Introduction, with its picture at rest)
  and every scene with a picture fill the window under one head (menu, result and scene pickers, the tellings, the guide);
  the drawer opens over it. The front page, the guide (`#intro`), the overview (`#map`) and comparisons are ordinary pages.
- `site/js/data/telling.js`: the Allegory's prose. Place names are tokens (`{fishery}`) filled from the current allegory.
- `allegories/<id>/`: an allegory's source: its name and words, and the road network of its city and its siege.
- `tools/allegory.py`: checks a network, draws it, prepares and checks its picture, and builds it into the page.
- `site/allegories/<id>.js`, `site/js/data/allegories.js`: the allegories the page holds and the one it opens with; a menu in the drawer switches. Written by the tool.
- `site/js/data/plain.js`: the Abstraction's own roads and positions. Fixed; no allegory changes it.
- `world/`: the Blender build of the original Greek town and siege.
- `site/js/data/traces.js`, `site/js/trace.js`: global traces, for the scenes that have one: every node's state at
  every step, and when each message leaves and arrives. Projected onto a node, a trace gives that node's rows, so the
  scene can be told from inside any of its nodes (the viewpoint tabs over the stepper). Its narrator's rows must match.
- `viz/`: an archived three.js experiment on the same data, gitignored and kept on disk only.

## Skills

- **Building a new allegory** (another setting, another road layout, new pictures, renamed places): follow
  `skills/build-allegory/SKILL.md`.

## Checks

- `python3 tools/allegory.py check <id>`: an allegory's networks keep every rule.
- `node site/tools/check-traces.js`: every global trace, projected onto its scene's narrator, gives back the scene's rows
  exactly, and every other node's step has its own account (`why`). The checker can't tell whether the other nodes
  follow the algorithm's rules; check that by hand when writing a trace.
- `node site/tools/check-leaks.js`: the Abstraction's text uses none of the telling's own vocabulary (run it after editing scenes or the telling).
