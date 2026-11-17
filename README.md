# Distributed Algorithms of Ancient Greece

**[kikkupico.github.io/DAAG2](https://kikkupico.github.io/DAAG2/)**

Sixteen results from distributed computing, each told as a few short scenes from inside one
participant: logical and vector clocks, Chandy–Lamport snapshots, causal multicast, FLP, failure
detectors, Ben-Or, two-phase commit, Paxos, Viewstamped Replication, the Byzantine generals,
PBFT, linearizability, CAP, quorums, gossip and CRDTs, and Bayou.

Every scene is told twice, with the same steps:

- **Allegory**: merchants, part-time legislators, soldiers and scholars in a walled Greek town.
  Nobody shares a room. Every message is a courier who walks the town's roads, and can be slow,
  lost or overtaken.
- **Abstraction**: nodes A, B and C, messages and logs.

Lamport started this: the Byzantine generals (1982) and the part-time parliament of Paxos (1998).
This project takes both stories at their word and puts them in one town.

## Running it

It's a static page with no build step. Open `app/index.html`, or serve the folder:

```sh
python3 -m http.server -d app
```

## How it is made

- `app/js/data/`: the steps of every scene, as plain data shared by both tellings, and the
  Allegory's prose.
- `world/`: the Greek town and its siege, modelled and rendered in Blender (Python scripts).
  Textures, scanned rocks, trees and skies come from [Poly Haven](https://polyhaven.com) (CC0);
  `world/fetch_assets.py` downloads them. The `.blend` files and renders aren't in the repo.
- `allegories/<id>/`: other settings for the same scenes. The drawer has a menu to switch between
  them: a Himalayan dzong, built in Blender like the Greek town, and a Venetian lagoon, painted by
  an image model (Gemini). Each one's road network is hand-made JSON.
  `tools/allegory.py` checks a network, draws it and builds it into the page.
- `skills/build-allegory/`: instructions an AI coding agent follows to build a new setting
  (pictures, roads, renamed places) end to end.

Checks:

```sh
node app/tools/check-leaks.js          # the Abstraction uses none of the Allegory's words
python3 tools/allegory.py check greece # a setting's road network keeps every rule
```

## Earlier versions

- [Paxos Illustrated](https://kikkupico.github.io/paxos-illustrated/): Lamport's paper, word
  for word, among illustrations.
- [Distributed Algorithms of Ancient Greece, v1](https://kikkupico.github.io/DAAG/).

## License

Code: [MIT](LICENSE). Text and images: [CC BY 4.0](LICENSE-CONTENT). The papers belong to their
authors and are linked, not reproduced.
