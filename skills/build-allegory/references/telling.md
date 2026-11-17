# The places, and how the telling names them

The prose of the Allegory (`app/js/data/telling.js`) never names a place outright. It writes `{fishery}`, and the page
fills in the `label` you gave that place. So naming the places well is most of retelling the stories.

## The city's places

Four kinds of people live in the town. Each result is told among one kind.

| Role id | Who is there | What it must be in your setting |
|---|---|---|
| `fishery`, `granary`, `winery` | The three **merchants**, who stand for nodes A, B and C. They sell to customers and order from one another. The same three are the **part-time legislators**: they vote from their workplaces. | Three independent working places that produce and store goods, each its own estate, far apart. |
| `pottery` | The maker of the containers the merchants ship goods in, who asks for a count of them all. | A workshop. |
| `temple` | The seat of authority. The notary who oversees a three-way exchange sits here, and the legislators' standing question is what colour to paint its columns, red or blue. | The grandest place, with something that can be painted red or blue (see `words` below). |
| `proposer P`, `proposer Q` | Two rival legislators who each try to get their own colour passed. | Two alike households near the centre, one marked blue (P), one red (Q). |
| `crossroads` | Where people from outside arrive: a customer, a citizen, a student, a reader. | An open public space at the middle of the network. |
| `northwest library`, `temple library`, `southeast library` | The three **scholars** or **librarians**, each keeping a copy of the same records. | Three places where knowledge or records are kept, far apart. The ids' compass words mean nothing. |

Who is on the picture together (and so must be in different zones): the three merchants with the temple, the crossroads
and sometimes the pottery or the two proposers; the three libraries with the crossroads.

## The siege's places

| Role id | Who is there | What it must be |
|---|---|---|
| `commander's camp` | The commander, who sends the order to attack or retreat. | The headquarters of the besieging force. |
| `camp A`, `camp B`, `camp C` | The lieutenants. Some may be traitors. | Three lesser camps. They usually share one label ("camp"): the page adds the letter. |
| `enemy city` | Nobody a courier reaches. | The besieged stronghold at the centre, shut tight. `"reach": false`. |

The camps hear from one another only by courier, and every courier goes round the stronghold. That is the point of the
picture: keep the roads out of it.

## Rules for labels

- A **bare common noun**, lower case, no article: `algae farm`, not `the Algae Farm`. The prose writes "the {fishery}",
  "The {fishery}'s ledger", "an order from the {granary}", so the label must read well after "the".
- **Short**: it is printed on a plate over the picture. Two words is good; 22 characters is the limit.
- The labels of `fishery`, `granary` and `winery` must **start with three different letters**. One scene abbreviates them
  to their initials.
- The `fishery`'s label must come **before the `granary`'s in the alphabet**. One scene settles a tie "by name,
  alphabetically", and the fishery wins it.
- Distinct places get distinct labels, except the camps and the two proposers, which share one each.

`check` enforces the mechanical ones. Read a few scenes on the page for the rest.

## allegory.json

| Field | Used for |
|---|---|
| `name` | The allegory's own name, in tool output. |
| `title` | The page's title in the Allegory register (the original: "Distributed Algorithms of Ancient Greece"). |
| `town` | The town's proper name; the prose's `{town}` (the original: "Paxos"). |
| `people` | Completes "In the Allegory they are ...": the four kinds of people, in your setting's words. |
| `hero` | `alt` and `caption` for the city picture at the top of the landing page. |
| `words` | Optional. See below. |

## Going further with `words`

Place names are filled in everywhere. The things people handle are not: the prose still speaks of amphorae, an ox-cart,
sardines, couriers, ledgers, the temple's columns. Much of that reads fine in any pre-modern setting. Where a word jars,
`words` swaps it throughout the Allegory's text, as a whole word, keeping a leading capital:

```json
"words": [["amphorae", "canisters"], ["amphora", "canister"], ["ox-cart", "rover"], ["columns", "airlock doors"]]
```

- Give plural and singular as separate pairs, the longer first.
- The swap is blind and exact: `["courier", "drone"]` leaves "couriers" alone unless you list that too. Read the result on the page.
- Keep it short. Swap the handful of words that break the setting, and leave the rest of the story alone.
- The words that carry the algorithms (ledger, slate, round, promise, vote, red, blue) should stay, or be swapped only
  for exact equivalents.
- `words` never reaches the Abstraction: its text is not yours to change, by this or any other means.

**Proper names and units are the first things to swap.** They place the story in Greece more firmly than any noun: the
scholars' lists hold Homer, Hesiod and Sappho, the scrolls are the Iliad and the Odyssey, the Earth is measured in stadia, and the soldiers count spears. Search
`app/js/data/telling.js` and `telling-text.js` for capitalised words and for units, and give each an equivalent from
your setting (authors or works its scholars would keep, its own measure of distance). Leave Ann and Bob, who are the
papers' own, and the names of the papers' authors.

To see what else there is to swap, search `app/js/data/telling.js` for the nouns of the results you care about. After
`build`, read at least one scene of each kind of people on the page (`shot`), prose included, and fix what still jars.

## The tokens, if you edit the prose itself

You should rarely need to. If you do: `{fishery}` is the label, `{Fishery}` the label with a capital, `{FISHERY}` its
initial alone, `{town}` the town. `{A}`, a single capital letter, is a person's letter and is not yours to change. Any
role id works as a token. Never write a place's name into the prose as plain text.
