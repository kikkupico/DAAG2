# Phase 8: final render and report

1. Full siege render at `--width 2400 --samples 96` to `world/build3d/polis-siege.png`. Note the build and render times and the `SIEGE: N lights` line.
2. Run `python3 world/polis_overlay.py world/build3d/polis-siege.png` and open the overlay image. Every node must sit on its road and no node may be covered. (If the overlay script needs the scene named, read its first lines for the argument.)
3. Run the siege check script. Heights unchanged; `0 not on the ground`, `0 hidden`.
4. Build once with `--no-engines --no-render` and confirm it finishes without errors.
5. Run the daytime build with `--no-render`; its `ROUTE CHECK` line must match the one saved in phase 0. Then render the daytime scene once at `--width 1600 --samples 32`, open it, and confirm nothing from the siege work has leaked into it (no shelters in the agora, no broken battlements, no barricades).
6. Look over the whole siege picture once more for anything in the "never add" list in `README.md`, and for anything standing on the ring road or a spur road.
7. Write the report:
   - `polis-siege-before.png` and the new `polis-siege.png`;
   - baseline and final `ROUTE CHECK` lines for both scenes;
   - baseline and final light counts, and build and render times;
   - what was added, phase by phase;
   - what was skipped or removed, and why;
   - anything you were unsure was right for the period.

Do not copy the render into `app/img/` and do not commit. The user decides both.
