# Phase 0: baseline

Apart from one small fix, nothing is changed in this phase. It records the state every later phase is checked against.

1. **First make the build repeatable.** `plants.py` seeds each tree shape with `hash(name)`, and Python changes string hashes on every run, so tree shapes differ between runs and the "hidden" count wobbles (96 to 98 seen on identical code). In `plants.make`, replace `hash(name) % 1000` with `zlib.crc32(name.encode()) % 1000` (and `import zlib`). Run the build twice with `--no-render` and confirm the `ROUTE CHECK` line is identical both times.
2. Run the full build at `--width 2400 --samples 96` and copy the result to `world/build3d/polis-before.png`. Note the build time and the render time.
3. From the output, save the line starting `ROUTE CHECK:` (and the `hidden by:` line after it) to `world/build3d/baseline-route-check.txt`.
4. Copy `world/build3d/polis-heights.json` to `world/build3d/baseline-heights.json`.
5. Run the siege build with `--no-render` and confirm it finishes without errors:
   `blender -b --factory-startup -P world/build_polis.py -- --scene world/build3d/siege.json --out world/build3d/polis-siege.png --no-render`
6. Write a small script `world/build3d/check.py` (scratch, not committed) that compares the current `polis-heights.json` with the baseline and prints any route height that differs by more than 0.02 m, and the two `off` and `hidden` counts. You will run it after every phase.
7. Read `props.py` and `country.py` in full, so you know which props and helpers already exist.

Done when: the four baseline files exist and the check script prints "no differences" on the untouched build.
