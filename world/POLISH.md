# Polish list

Known shortcomings, recorded on 10 November 2026 and deliberately left until the high-level design is settled.
Nothing here blocks the island plan or the remaining districts.

## Render speed

The three speed-ups are now in `build_world.py` (11 November 2026): ground relief from one noise texture instead of the whole blend,
4000 px overviews and 1500 px close views (`--width`, `--close`), and 64 samples. A full render of all 25 views took 19 minutes,
against about 2 hours before. Render only the views that changed (`--views a,b,c`) when possible: partial renders are safe, because
`world.json` keeps the other views' entries and planting is seeded by position.

## The rendered world (`build_world.py`)

- **Vines** are thin twigs on posts, not leafy rows. A denser plant or a purpose-built vine is needed, with rails between posts.
- **Camps are small and plain**: tents in a grid, no people, horses, palisade or siege engines. The cooking fires read as black dots.
- **The enemy city's wall** is a plain block texture with no wall-walk detail; the three roofs that show above it are ordinary houses.
- **Library colonnades** are mostly hidden under the roof from this camera angle, so the libraries read as plain halls.
- **Trees**: no olives yet; the downloaded species look alike from above.
- **Town has no streets or yard walls**, only houses on a grid.
- **Roof tiles lack relief** in the close views.
- **Water surface** is plain; no shore foam or wave pattern.
- **The cut wheat field** still reads pale at overview size.
- **One shrub variant is skipped** at build time (`shrub_01_f`), because it is tiny and would need an extreme scale.
- **Fish racks** read as racks of hanging fish in the close view, but are still only a few pixels in the overview.
- **Ground at close range** still has a faint unevenness where the patches of texture meet.

## Additions, not defects (need a go-ahead)

- People, animals and carts.
- A night render for dark mode.

## The stage on the page (`explainer-isles`)

- The page is about 3 MB, because it carries four pictures. Each further picture adds about half a megabyte; a shared, smaller set or lazy loading may be needed.
- The temple pictures with red and with blue columns are rendered but not yet used on the page.
- Requests from a citizen are not drawn on the legislators' stage, because no place stands for the citizen.
- A legislator's home is marked only by a small blue pennant, which is invisible in the overview.
- Not yet clicked through in a live browser; checked in screenshots only.
- The amphora counts and the tally are not drawn on the picture, only in the timeline.

## The page content

- PBFT and Bayou have not been cut down to their conceptual parts.
- The one-line takeaways stay in abstract terms in the telling.
- Commit or abort is told with merchants inside the legislators' chapter, and causes first with scholars inside the merchants' chapter.
- Bracha 1987 and Ahamad et al. 1995 are not in `sources/` (publisher pages refuse scripted downloads).

## Done in the first polish pass (10–11 November 2026)

- Ground material rebuilt as one blended surface; Blender's "Maximum number of closures exceeded" warning is gone.
- Texture repetition broken up at both scales: each ground texture is laid down in patches about one tile across, each taken from a random place in the texture, with a coarser sample over it and slow variation in brightness on top. The ground's relief now comes from the texture's own light and dark, not from normal maps, which went wrong on ground with no UV layout. The regular scalloped bands round camp A are gone.
- Hay and lean-to roofs: a straw-gold material in place of the grey thatch photo.
- Fish racks: two rails hung with rows of salted fish, in place of a picket-fence look.
- Dark rings round levelled sites removed: the rock texture now follows the land's own slope, not the ramp made by levelling. Vineyard terraces keep their edges.
- Standing wheat: rows of stalk clumps in every field but the cut one; darker stubble and sheaves in the cut field.
- Cypresses added along roads and beside buildings.
- Agora paved.
- Planting is seeded by position, so a change in one place only changes the planting there, and partial renders stay consistent.
- On the page: courier labels no longer overlap each other or place names; liars messages say "commander said"; on phones the picture starts scrolled to your own place.
- Each result's picture is cropped to its own places (about 1.4× larger for snapshots, 1.04–1.14× for the other three, because their places are spread wide), with a close-up of your own place in a corner clear of the scene, or below the picture when no corner is clear and on phones.
- Every result in the telling now has a stage (16 results, 44 scenes), sharing 9 pictures and 9 close-ups.
- The step strip is now the stepper: it sits under the picture, pins to the top of the screen while the timeline is read, brings each step's card in under it, and follows the reader's own scrolling. The picture's caption is gone.
- The inside view no longer darkens the picture; world view (global view in the Abstraction register) is a single on/off switch.
- The Abstraction register shows the same layout as a diagram: lettered nodes where the places are, straight links, messages with their plain names, no picture or close-up.
- The granary and the winery each stand in a small estate: five and four workers' houses, walled yards and a well.
