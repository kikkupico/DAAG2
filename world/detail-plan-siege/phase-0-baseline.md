# Phase 0: baseline

Apart from one small fix, nothing is changed in this phase. It records the state every later phase is checked against.

1. **Make the build repeatable, if it is not already.** Open `world/polis/plants.py` and look at `make()`. If it seeds with `hash(name) % 1000`, replace that with `zlib.crc32(name.encode()) % 1000` (and `import zlib`): Python changes string hashes on every run, so tree shapes would differ between runs. If it already uses `zlib.crc32`, do nothing.
2. Run the full siege build at `--width 2400 --samples 96` and copy the result to `world/build3d/polis-siege-before.png`. Note the build time and the render time.
3. From the output, save the `ROUTE CHECK:` line and the `SIEGE: N lights` line to `world/build3d/baseline-siege.txt`. The route check should read `0 not on the ground` and `0 hidden from the camera`.
4. Copy `world/build3d/polis-siege-heights.json` to `world/build3d/baseline-siege-heights.json`.
5. Run the daytime build with `--no-render` and save its `ROUTE CHECK:` line in the same text file:
   `blender -b --factory-startup -P world/build_polis.py -- --scene world/build3d/city.json --out world/build3d/polis.png --no-render`
6. Write a small script `world/build3d/check-siege.py` (scratch, not committed) that compares the current `polis-siege-heights.json` with the baseline and prints any route height that differs by more than 0.02 m, and the sizes of its `off` and `hidden` lists. You will run it after every phase.
7. Read `world/polis/siege.py` in full. Note the parts that already exist (`PANELS`, `WATCH`, `TENTS`, `OFFICER`, `PAVILION`, `ARMS`, `STANDARD`, `FIRE`, `TORCH`, `CATAPULT`, `RAM`, `HELEPOLIS`, `MANTLET`, `SHED`, `SHOT`, `STUMP`, `LOGS`) and the helpers `light`, `fire`, `torch`, `stockade`.

Done when: the baseline files exist and the check script prints "no differences" on the untouched build.
