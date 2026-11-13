# Phase 10: final render and report

1. Full render at `--width 2400 --samples 96` to `world/build3d/polis.png`. Note the build and render times.
2. Run `python3 world/polis_overlay.py world/build3d/polis.png` and open the overlay image. Every node must sit on its road and no node may be covered.
3. Run the baseline check script. Heights unchanged; "not on the ground" and "hidden" counts not above the baseline.
4. Run the siege build and render it once at `--width 1600 --samples 32`. Open it and confirm nothing from the daytime work looks wrong at night (in particular the gates, and any prop shared by both scenes).
5. Look over the whole daytime picture once more for the things in the "never add" list in `README.md`, and for anything standing on a road.
6. Write the report:
   - `polis-before.png` and the new `polis.png`;
   - the baseline and final `ROUTE CHECK` lines;
   - what was added, phase by phase;
   - what was skipped or removed, and why;
   - baseline and final build and render times;
   - anything you were unsure was right for the period.

Do not copy the render into `app/img/` and do not commit. The user decides both.
