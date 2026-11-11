// ---------- the telling ----------
// One island, Paxos, with no assembly hall: everyone works from their own place and hears from the rest by courier.
// Four hats, one per chapter. People are anonymous: a role and the same letter the plain register uses.
// The merchants are the exception: `names` gives A, B and C a business each, and the name replaces the letter.
// The steps are the same in both registers. `lex` (and `msg`, which also knows the peer and the direction)
// make what is asked, sent and held specific: a colour for the temple columns, an order for grain.
// In the prose, {A} marks a person's letter, so a sentence can still begin with the article "A".
const HAT = {
  merchant: ["Merchants", "Trade needs to know what came first and what is in stock."],
  legislator: ["Legislators", "A law must be one law, though legislators come and go."],
  soldier: ["Soldiers", "Every loyal officer must act alike, though some are traitors."],
  scholar: ["Scholars", "Knowledge can be answered now and reconciled later."],
};
const flpP = [
  "Legislator {A} favours red and has decided nothing.",
  "In the first step no courier comes, yet a step can still act: {A} sends a vote, red, to {B} and {C}.",
  "{B}'s vote arrives: blue. One vote is still missing, so {A} waits.",
  "No courier comes.",
  "None again.",
  "A third empty step. By the rule {A} now decides with the votes in hand, red and blue, and a tie goes to red. The decision goes in the ledger once and is never changed.",
];
const susP = [
  "Legislator {A} favours red, and that is {A}'s estimate so far. Nothing is decided.",
  "A citizen asks the legislators to settle the colour. Round 1 is {B}'s to preside over, so {A} sends {B} the estimate: red, held since the start.",
  "The hourglass runs out with nothing from {B}, so {A} suspects {B}. {A} sends {B} a no for round 1 and moves to round 2, sending the estimate to {C}, the next president.",
  "{C} proposes blue. {A} takes blue as the estimate, notes that it was adopted in round 2, and says yes.",
  "{C} tells {A} to decide blue. {A} writes blue in the ledger, and passes the decision on to both colleagues in case {C} is gone before telling them.",
];
const liar3 = [
  "Lieutenant {A} has decided nothing.",
  "The commander, {S}, orders {A} to attack, and {A} passes on to {B} what {S} said.",
  "{B} reports that {S} said retreat. {A} has no way to tell which of them lied. The rule breaks the tie in favour of {S}, so {A} decides to attack.",
];
const liar4 = [
  "Lieutenant {A} has decided nothing.",
  "The commander, {S}, orders {A} to attack, and {A} passes it on to {B} and {C}.",
  "{B} reports that {S} said retreat. {A} waits for {C}.",
];
const capP = [
  "Scholar {A} holds the figure: 250,000 stadia round the Earth.",
  "A student asks how many stadia it is round the Earth. {A} asks {B} whether there is anything newer.",
  "The hourglass runs out with no reply. By the rule {A} answers with what {A} holds: 250,000.",
];
const pax0 = "Proposer {Q} has tried no round yet.";
const pax1 = "A citizen wants the columns painted blue. {Q} claims round 2 and asks all three legislators to promise.";
const pbft0 = "Officer {B} is in view 0, where {A} commands. The count stands at 0 spears, and nothing has run yet.";
const quorumOut = "{B} handled a write of “Homer, Hesiod”: {B} and {A} stored it, so the reader was told it was done. The courier to {C} was lost.";
const quorum0 = "Librarian {C}'s copy of the list holds Homer, with counts showing one change, made through {A}.";
const copsOut = "At {B}'s library, a scholar shelved a scroll, then added it to the catalogue. The two writes travel separately, and the catalogue's arrives first. A visitor reads at {A}'s library.";
const cops0 = "Scholar {A} has no scroll on record, and the catalogue is empty.";

