// ---------- the Allegory's telling of the results added to the second set (see scenes-more.js) ----------

const tgaNote1 = "Rule: {B} attacks at dawn if the plan reaches {B}, and sends a courier back. {A} attacks at dawn only if that courier reaches {A}.";
const tgaNote2 = "Rule: one more courier. {B} attacks only if {A} confirms that {B}'s courier arrived. {A} attacks once that courier arrives, and confirms.";
const tga0 = "General {A} means to attack at dawn together with {B}, on the far side of the {enemy city}. Either one attacking alone is beaten. {A} has decided nothing yet.";
const tga1 = "No courier has come, yet {A} can still act: {A} sends a courier to {B} with the plan.";
const tgaConfirm = [tga0, tga1,
  "{B}'s courier arrives: {B} has the plan, and will attack if {A} confirms. {A} decides to attack at dawn, and sends a courier to confirm.",
  "Dawn comes, and {A} attacks. {A} never learns whether the confirming courier got through: under this rule nobody answers a confirmation."];
TELL.twogen = { hat: "soldier", role: "general",
  stage: { view: "siege", A: "camp A", B: "camp C", also: ["enemy city"] }, peers: "general {B}",
  lex: [["act at t?", "attack at dawn?"], ["acted at t", "attacked at dawn"], ["act at t", "attack at dawn"], ["did not act", "held back"],
    ["no reply yet", "no courier back yet"], ["time t", "dawn"], ["agreed, if confirmed", "agreed, if you confirm"], [/^B has it$/, "B holds the plan"]],
  tale: "Two generals wait on either side of the {enemy city}. Together they can take it at dawn; either one attacking alone is beaten. Their couriers must pass the {enemy city}, and any courier may be caught. Each answer needs an answer of its own, and whoever sends the last courier can never know it got through. This is Jim Gray's generals paradox, set in front of {town}.",
  frame: {
    goal: "Both generals attack at dawn, or neither does, and if no courier is caught they both attack.",
    shared: "Nothing but the rule. Each general knows only what the couriers have brought.",
    assumes: "Any courier may be caught, and a general can't tell a caught courier from a slow one. No general falls and nobody lies. Dawn is what makes it impossible: the notary's way of settling a swap escapes by letting the messages go on without limit, so a business may wait as long as it takes." },
  gloss: [["general", "node"], ["courier", "message"], ["caught", "lost"], ["attack at dawn", "act at time t"], ["held back", "did not act"]],
  scenes: {
    plan: { name: "A plan and an answer", note: tgaNote1, prose: [tga0, tga1,
      "{B}'s courier arrives: {B} has the plan and will attack. {A} now knows that {B} will attack, and decides to attack at dawn.",
      "Dawn comes, and {A} attacks."],
      out: { 2: "{B} decided to attack as soon as the plan arrived. {B} cannot know whether the answer got through; under this rule {B} does not need to", 3: "{B} attacks at dawn as well. They take the {enemy city}" } },
    lostreply: { name: "The answer is caught", note: "Same rule.", outside: "Every courier {B} sends will be caught on the way.", prose: [tga0, tga1,
      "No courier comes back before {A}'s hourglass runs out. A caught plan and a caught answer look the same from where {A} stands, so {A} sends the plan again.",
      "Still no courier when dawn comes. {A} doesn't know that {B} has the plan, so {A} holds back."],
      out: { 2: "the plan had arrived, and {B} decided to attack. {B}'s answer was caught. This second plan gets through too, and {B} answers again", 3: "{B}'s second courier was caught as well. {B} attacks at dawn, alone" } },
    confirm: { name: "One more courier", note: tgaNote2, prose: tgaConfirm,
      out: { 2: "{B} now waits for the confirmation before deciding", 3: "the confirmation arrived, so {B} attacks at dawn as well" } },
    lostconfirm: { name: "The confirmation is caught", note: tgaNote2, outside: "{A}'s confirming courier will be caught.", prose: tgaConfirm,
      out: { 2: "this courier is caught. To {B}, a caught courier looks like one still on the way", 3: "{B} never got the confirmation and holds back. {A} attacks alone. To {A}, nothing differed from the scene before" } },
  } };

const sgaNote = "Rule: the commander seals the order. Pass on the sealed order, then decide: if {S} sealed one order, obey it; if two, {S} is a traitor, so retreat. A seal can't be forged, and every officer knows it on sight.";
const sga1 = "{S} sends {A} the order to attack, under {S}'s seal. {A} passes the sealed order on to {B} unchanged.";
TELL.signed = { hat: "soldier", role: "lieutenant", roles: { S: "commander" },
  stage: { view: "siege", S: "commander's camp", A: "camp A", B: "camp B", also: ["enemy city"] }, peers: "the commander {S} and lieutenant {B}",
  lex: [["y: forged", "retreat: the seal is forged"], ["signed S", "sealed by the commander"], ["forged S", "a forged seal"],
    [/^signed by S$/, "orders under the commander's seal"], [/\bx\b/g, "attack"], [/\by\b/g, "retreat"], [/^value\(/, "order("]],
  tale: "The commander and two lieutenants again, but now the commander seals every order with a ring nobody else can copy. A lieutenant passes the sealed order on as it came. A traitor can still say anything, but can't put the commander's seal on it. So a commander who seals two different orders is caught, and a lieutenant who invents one is caught too. Three officers are now enough to outlast one traitor.",
  frame: {
    goal: "The commander sends an order. All loyal lieutenants decide the same order, and if the commander is loyal, it is the order the commander sent.",
    shared: "Up front: the roll of officers, which one commands, the default order, retreat, and a seal every officer knows on sight.",
    assumes: "Every courier arrives, and a missing one can be noticed. A loyal officer's seal can't be forged, and a sealed order can't be altered unseen; traitors may lend each other theirs. Up to m officers are traitors; with one traitor, one round of passing on is enough." },
  gloss: [["commander", "sender"], ["lieutenant", "receiver"], ["seal", "signature"], ["traitor", "a node that lies"], ["attack, retreat", "the two values, x and y"]],
  scenes: {
    sender: { name: "Three officers: the commander lies", note: sgaNote, outside: "{S} is the traitor: {S} sealed attack for {A} and retreat for {B}.", prose: [
      "Lieutenant {A} has decided nothing.", sga1,
      "{B} passes on an order to retreat, also under {S}'s seal. {B} could not have made that seal, so {S} sealed two different orders: {S} is a traitor. {A} retreats, the default."],
      out: { 2: "{B} holds the same two sealed orders and retreats too. Without seals, this is the case that split them" } },
    relay: { name: "Three officers: a lieutenant lies", note: sgaNote, outside: "{S} is loyal and sealed attack for both. {B} is the traitor.", prose: [
      "Lieutenant {A} has decided nothing.", sga1,
      "{B} claims {S} ordered a retreat, but the seal on it is a forgery. {A} throws it away. {S} sealed only attack, so {A} decides to attack."],
      out: { 2: "{B} could only lie about {S}'s order by forging {S}'s seal, and a forgery is seen at once. Three officers are enough" } },
  } };

const elaBully = [
  "Legislator {A}, of seniority 5, has {B}, of seniority 9, in the chair. {C} has seniority 3.",
  "{A} hears nothing from the chair in the time allowed. {A} calls an election by asking every more senior legislator, here only {B}, whether they are there.",
  "No answer within the hour. By the rule, that means {B} is gone, so the chair is {A}'s. {A} first tells every junior legislator to halt, here only {C}.",
  "{C} has halted. {A} tells {C} that {A} is elected, and takes the chair.",
];
TELL.election = { hat: "legislator", role: "legislator",
  stage: { view: "city", A: "fishery", B: "granary", C: "winery", also: ["temple"] },
  lex: [[/^elect\((\d+)\)$/, "seniority $1"], [/^elected\((\d+)\)$/, "in the chair: seniority $1"], [/^leader$/, "chair"], [/^my number$/, "my seniority"],
    [/\((\d+)\)$/, ", seniority $1"], ["no word from the leader", "no word from the chair"], ["no leader", "the chair is empty"], ["no answer within T", "no answer within the hour"], ["orders from leader B", "instructions from the chair, B"]],
  tale: "The legislators always give the chair to the most senior of them. When it falls empty, they choose again, with no one to count heads. Passed hand to hand round a circle, only the highest seniority comes back to its owner. Sent directly, a legislator asks everyone more senior whether they are there, and takes the chair if nobody answers within the hour. That is only safe if an hour's silence truly means gone. These are Chang and Roberts's ring and Garcia-Molina's bully.",
  frame: {
    goal: "Every legislator still at work ends up with the same chair, and it is the most senior one still at work.",
    shared: "Each legislator knows their own seniority. Round the circle, each knows only who comes next; sent directly, each knows everyone's seniority.",
    assumes: "Round the circle, couriers arrive and nobody leaves during the election. The second rule allows legislators to be gone and come back, but assumes a courier to anyone at work arrives within the hour and that nobody ever dozes off. Without those two, no rule can keep two legislators from both acting as chair. Nobody lies." },
  gloss: [["legislator", "node"], ["seniority", "the node's number"], ["the chair", "the leader"], ["the hour", "the time limit T"], ["dozing off", "pausing"]],
  scenes: {
    ring: { name: "Round the circle", note: "The legislators pass couriers round a circle, one way only: {A} to {B}, {B} to {C}, {C} to {A}. Rule: send your own seniority on. Pass on a higher one, drop a lower one. If your own comes back, you are the most senior.", prose: [
      "Legislator {A}, of seniority 5, sees the chair empty. {B} has seniority 9 and {C} 3, but {A} does not know that, or even how many legislators there are.",
      "{A} calls an election, sending its own seniority, 5, on to {B}.",
      "Two couriers come from {C}. {C}'s own seniority, 3, is lower than 5, so {A} drops it. Seniority 9 is higher, so {A} passes it on.",
      "Word comes round that 9 is in the chair: {B}'s own seniority came back to {B}. {A} takes {B} as chair and passes the word on."],
      out: { 2: "9 is passed by everyone, and every lower seniority is dropped by someone more senior", 3: "only the highest seniority gets all the way round, so only one legislator can find themselves elected" } },
    bully: { name: "The most senior one left", note: "Rule: a courier to anyone at work arrives within the hour, and nobody ever dozes off. A legislator who misses the chair asks everyone more senior; if nobody answers within the hour, they halt the juniors and take the chair.",
      outside: "{B} is gone for good.", prose: elaBully,
      out: { 3: "{C} now has {A} in the chair. Everyone has the same chair, the most senior legislator still at work" } },
    pause: { name: "The chair only dozed off", note: "Same rule, but its assumption fails: {B} is not gone, only dozing, for longer than the hour.",
      outside: "{B} has dozed off, and will carry on later as if nothing had happened.", prose: elaBully,
      out: { 3: "{B} wakes still in the chair, by {B}'s own account, and sends {C} instructions. Two legislators now act as chair. Without an hour that never lies, no rule can prevent this" } },
  } };

const mxaNote = "Rule: to book the ox-cart, ask both other businesses, numbering the booking one past the highest seen, and wait for both to say go ahead. Say go ahead at once, unless you are booking too and your booking comes first: lower number first, and on a tie, the name earlier in the alphabet. Then hold your answer until the cart is back.";
const mxa0 = "The {fishery} has not booked the ox-cart, and has seen no booking.";
TELL.mutex = { hat: "merchant", role: "merchant",
  stage: { view: "city", A: "fishery", B: "granary", C: "winery", client: "crossroads", labels: { crossroads: "the harbour" } }, client: "harbour",
  names: { A: "{fishery}", B: "{granary}", C: "{winery}" },
  lex: [[/^request\(/, "may I have the ox-cart? ("], [/\((\d+), A\)/g, "(booking $1, {fishery})"], [/\((\d+), B\)/g, "(booking $1, {granary})"], [/\((\d+), C\)/g, "(booking $1, {winery})"],
    [/^reply$/, "go ahead"], ["use the resource", "the catch must go to market"], ["done with the resource", "the ox-cart is back"],
    [/^using$/, "has the ox-cart"], [/^requesting$/, "asking for the cart"], ["highest seen", "highest booking seen"], [/^deferred$/, "answer held for"], ["replies due", "answers still due"],
    [/^A$/, "{fishery}"], [/^B$/, "{granary}"], [/^C$/, "{winery}"]],
  tale: "{town} has one ox-cart, and nobody is in charge of it. A business that needs it asks the other two and waits until both say go ahead. Every booking carries a number one past the highest the business has seen, so an earlier booking has a smaller number. A business that is booking too says go ahead at once if the other booking comes first, and otherwise holds its answer until the cart is back. Two bookings can never both come first, so the cart is never promised twice. This is Ricart and Agrawala's rule, which saves a courier on the one in the ledgers of {town}.",
  frame: {
    goal: "Only one business has the ox-cart at a time, every business that books it gets it in the end, and nobody waits for ever.",
    shared: "Nothing. Beforehand the businesses know each other's names.",
    assumes: "Every courier arrives, in any order and after any delay. No town clock. No business shuts; the paper discusses how one that did would come back. Each booking takes four couriers, two out and two back: no rule in which every business acts alike, and answers bookings as they come, can use fewer." },
  gloss: [["the ox-cart", "the shared resource"], ["a booking", "a request"], ["go ahead", "a reply"], ["holding an answer", "deferring a reply"], ["the booking number", "the sequence number"]],
  scenes: {
    tie: { name: "Booking at the same time", note: mxaNote, prose: [mxa0,
      "The catch must go to market. The highest booking the {fishery} has seen is 0, so it asks the {granary} and the {winery} for the cart with booking 1.",
      "The {granary}'s booking arrives, also numbered 1. It's a tie, and {fishery} comes before {granary} in the alphabet, so the {fishery}'s booking goes first. It holds its answer.",
      "The {granary} says go ahead: it sees the same tie, settled the same way.",
      "The {winery} says go ahead too. Both have answered, so the {fishery} takes the ox-cart.",
      "The cart is back. The {fishery} sends the {granary} the go-ahead it was holding."],
      out: { 5: "now the {granary} has both answers and takes the cart. Never at the same time as the {fishery}" } },
    later: { name: "Booking second", note: mxaNote, prose: [mxa0,
      "The {granary}'s booking arrives, numbered 1. The {fishery} isn't booking, so it says go ahead at once, and notes the number.",
      "Now the catch must go to market. The highest booking the {fishery} has seen is 1, so it books with 2.",
      "The {winery} says go ahead. The {granary} does not, yet.",
      "The {granary}'s go-ahead comes. Both have answered, so the {fishery} takes the ox-cart.",
      "The cart is back, and no answers are being held."],
      out: { 4: "the {granary} had the cart and held its answer until it was back. The {granary} booked first, so it went first, though {fishery} comes earlier in the alphabet" } },
    nodefer: { name: "If nobody held an answer", note: "A different rule: say go ahead to every booking at once, and take the cart once both have answered.", prose: [mxa0,
      "The catch must go to market. The highest booking the {fishery} has seen is 0, so it asks the {granary} and the {winery} for the cart with booking 1.",
      "The {granary}'s booking arrives, also numbered 1. By this rule the {fishery} says go ahead at once.",
      "The {granary} says go ahead.",
      "The {winery} says go ahead too. Both have answered, so the {fishery} takes the ox-cart."],
      out: { 4: "the {granary} has both go-aheads as well, and is loading the same ox-cart at this very moment" } },
  } };

const abdaNote = "New measurements go to {B}, who numbers each one higher than the last and sends it to everyone. To answer a student, ask every scholar for their latest figure, take the highest-numbered among a majority's answers, your own included, then send it round and wait until a majority have it before answering.";
const abdaOut = "{B} has just been brought a new measurement, 252,000, numbered 2. {B}'s couriers to {A} and {C} are lost on the way, so {B} will send them again.";
const abda12 = ["Scholar {A} holds 250,000 stadia round the Earth, measurement 1.",
  "A student asks {A} how many stadia it is round the Earth. {A} asks {B} and {C} for their latest figure, counting {A}'s own."];
TELL.abd = { hat: "scholar", role: "scholar",
  stage: { view: "city", A: "northwest library", B: "temple library", C: "southeast library", labels: { crossroads: "a student" }, client: "crossroads" }, client: "student",
  lex: [[/^latest\?$/, "your latest figure?"], [/^latest\((\d+), ([xy])\)$/, "latest: $2, measurement $1"], [/^announce\((\d+), ([xy])\)$/, "I am giving out $2, measurement $1"],
    [/^write\((\d+), ([xy])\)$/, "new figure: $2, measurement $1"], ["write y", "a new measurement: y"], ["read the value", "how many stadia round the Earth?"],
    [/^latest$/, "latest figure"], [/^(\d+): ([xy])$/, "$2, measurement $1"], [/\bx\b/g, "250,000"], [/\by\b/g, "252,000"]],
  tale: "Three scholars each keep the figure for the distance round the Earth. Only {B} takes in new measurements, numbering each one higher than the last. Couriers get lost and a scholar may be gone, so nobody waits for everyone: a scholar answering a student asks the others, takes the highest-numbered figure that a majority report, and makes sure a majority have it before giving it out. Any two majorities share a scholar, so once a figure has been given out, no later student hears an older one. This is the register of Attiya, Bar-Noy and Dolev.",
  frame: {
    goal: "Students asking any scholar hear answers a single scholar could have given, and every question to a scholar still at work gets an answer.",
    shared: "One figure, a copy at every library. Only {B} takes in new measurements; any scholar may answer.",
    assumes: "Couriers can be lost, slow or overtaken; what keeps being sent eventually reaches a majority. Fewer than half the scholars are gone. No clocks: nobody ever waits for any particular scholar. Nobody lies." },
  gloss: [["scholar", "node"], ["{B}, who takes in measurements", "the writer"], ["the measurement number", "the label"], ["giving a figure out", "answering a read"], ["sending it round", "the read's second phase, announcing the value"]],
  scenes: {
    announce: { name: "Send it round, then answer", note: abdaNote, outside: abdaOut, prose: [...abda12,
      "{B} answers 252,000, measurement 2. With {A}'s own, that is a majority, and the highest number is 2. {A} takes 252,000, and before answering, sends it round.",
      "{B} has noted 252,000. {A} and {B} are a majority holding it, so {A} answers 252,000.",
      "{C}, asked by another student, asks {A} for the latest figure. {A} answers 252,000."],
      out: { 3: "252,000 was given out only once a majority held it", 4: "every majority {C} can ask includes {A} or {B}, so {C} finds 252,000 too. Once it was given out, no student hears 250,000 again" } },
    noannounce: { name: "Answer at once", note: "A different rule: take the highest-numbered among a majority's answers, and answer at once.", outside: abdaOut, prose: [...abda12,
      "{B} answers 252,000, measurement 2. With {A}'s own, that is a majority, and the highest number is 2. {A} answers 252,000 at once.",
      "{C}, asked by another student, asks {A} for the latest figure. {A} still holds 250,000, and answers that."],
      out: { 3: "{C} hears 250,000 from {A} and from {C}'s own copy, a majority, and answers 250,000. A student who asked after 252,000 was given out is told 250,000: new, then old" } },
  } };

const lsaNote = "Rule: {A} keeps the figure and lends {B} a copy until 12:10: until then {B} may answer students from the copy without asking. A new figure must wait until every borrower agrees, or until the loan has run out.";
const lsaProse = ["Scholar {A} keeps the figure, 250,000 stadia round the Earth. {B} has a copy on loan until 12:10.",
  "{C} brings {A} a new measurement, 252,000. {B}'s loan is still running, so {A} asks {B} to agree to the change.",
  "No answer comes, and at 12:10 by {A}'s water clock {B}'s loan is over. {A} changes the figure to 252,000 and tells {C}."];
TELL.leases = { hat: "scholar", role: "scholar", roles: { K: "registrar" },
  stage: { view: "city", A: "temple library", B: "northwest library", C: "southeast library", K: "temple", labels: { crossroads: "a student" }, client: "crossroads" }, client: "student",
  lex: [[/\block\b/g, "warrant"], ["may I warrante?", "may I change the figure?"], [/^warrantten$/, "the figure is changed"], [/^warrante y$/, "a new measurement: y"],
    [/^warrante\(([xyz])/, "change the figure to $1"], [/lease/g, "loan"], [/^leases$/, "copies on loan"], [/\bx\b/g, "250,000"], [/\by\b/g, "252,000"], [/\bz\b/g, "251,000"]],
  tale: "The {temple library} keeps the true figure for the distance round the Earth, and lends other libraries a copy for a fixed time. Until the loan runs out, the borrower answers students from the copy without asking. A new figure must wait until every borrower agrees, or until their loans run out, so a library that can't be reached only holds things up until then. All of it rests on the water clocks keeping time together. A warrant to change the figure, granted by the registrar for a fixed time, is numbered, so that a change sent under an old warrant can be turned away. These are the leases of Gray and Cheriton, and the numbered locks of Chubby.",
  frame: {
    goal: "Every student, asking the {temple library} or a borrower, hears the latest figure, though couriers are lost and scholars are gone.",
    shared: "The figure, kept at the {temple library}, and copies lent out until a fixed time.",
    assumes: "Couriers can be lost, and scholars can be gone and come back; the keeper, coming back, waits out the longest loan it might have made. Water clocks drift apart by no more than a known amount. Nobody lies." },
  gloss: [["a loan", "a lease"], ["the water clock", "a node's clock"], ["a warrant", "a lock"], ["the warrant's number", "a sequencer"], ["the registrar", "the lock service, K"]],
  scenes: {
    expire: { name: "Wait out the loan", note: lsaNote, outside: "{B} is cut off: couriers to {B} are lost.", prose: lsaProse,
      out: { 2: "{B}'s loan ran out at 12:10 by {B}'s own clock too, and {B} stopped answering from the copy. No student heard 250,000 after the change. Had {B} answered, {A} could have changed it at once" } },
    fastclock: { name: "A water clock that runs fast", note: lsaNote, outside: "{B} is cut off. {A}'s water clock runs fast: when it shows 12:10, it is really 12:06.", prose: lsaProse,
      out: { 2: "{B}'s clock is right, and the loan has four minutes left. {B} tells a student 250,000 after the figure was changed. A loan is only as good as the clocks" } },
    late: { name: "A change that arrives late", note: "Rule: a scholar changes the figure only while holding the warrant, which the registrar grants for a fixed time. {A} makes every change that reaches it.",
      outside: "{B} held the warrant and sent a change, then dozed off. The warrant ran out, and the registrar gave it to {C}.",
      prose: ["Scholar {A} keeps the figure, 250,000.", "{C}, holding the warrant, changes the figure to 251,000. {A} makes the change.", "{B}'s change to 252,000 arrives. {A} makes it."],
      out: { 2: "{B} sent this while holding the warrant, but it arrived after the warrant had passed to {C}. It undid {C}'s change with nobody holding the warrant" } },
    sequencer: { name: "Numbered warrants", note: "Rule: each time the registrar grants the warrant, it is numbered one higher, and a change carries its warrant's number. {A} turns away a change whose number is lower than the highest seen.",
      outside: "{B} held warrant 1 and sent a change, then dozed off. The warrant ran out, and the registrar gave warrant 2 to {C}.",
      prose: ["Scholar {A} keeps the figure, 250,000. The highest warrant number seen is 1.", "{C} changes the figure to 251,000 under warrant 2. {A} makes the change and notes the number.", "{B}'s change to 252,000 arrives, under warrant 1. That is lower than 2, so {A} turns it away."],
      out: { 2: "the late change can't undo {C}'s. {B} learns the warrant is gone" } },
  } };

const nkaNote = "Rule: a page may be added to the payment book only by whoever finishes a long sum that takes luck as well as time. Copy pages onto the longest payment book you know. If two are equally long, keep adding to the one you heard of first, but keep the other: if it grows longer, switch to it.";
TELL.nakamoto = { hat: "merchant", role: "merchant",
  stage: { view: "city", A: "fishery", B: "granary", C: "winery", M: "pottery", also: ["crossroads"] },
  names: { A: "{fishery}", B: "{granary}", C: "{winery}", M: "{pottery}" },
  lex: [[/^made block (\S+)$/, "finished the sum for page $1"], [/^blocks\(/, "pages("], [/^block\(/, "page("], [/holds x\)/, "the {fishery} is paid)"],
    [/^write\(x\)$/, "payment to the {fishery}"], [/^write x$/, "pay the {fishery}"], [/^x$/, "payment"], [/block (\d)/, "page $1"], [/^chain$/, "payment book"], ["secret chain", "hidden payment book"],
    ["also kept", "other payment book kept"], ["acted on x", "amphorae handed over"]],
  tale: "Every business in {town} keeps a copy of one public payment book of payments, and anyone may set up shop and join. A page can be added only by whoever finishes a long sum that takes luck as well as patience, and every page names the page before it. Everyone copies onto the longest payment book they know. Two pages finished at once make two payment books, and the next page settles which is longer. A cheat can rewrite the payment book only by out-summing everyone else together, and with every page it falls behind, its chances shrink. So a payment is never certain, only ever likelier, the deeper it lies. This is Satoshi Nakamoto's chain, kept on parchment.",
  frame: {
    goal: "Every honest business agrees on one payment book, page by page, and a page deep in it is unlikely ever to be replaced.",
    shared: "The payment book, copied at every business, and the rule. Nobody needs to know how many businesses there are, or who they are.",
    assumes: "News of a page goes to everyone, and some couriers may be lost; a business that misses a page asks for it when the next arrives. Businesses open and close. Some may cheat, as long as the honest ones together finish sums faster. No town clock, but how long a sum takes is down to luck." },
  gloss: [["a page", "a block"], ["the long sum", "the work that makes a block"], ["the longest payment book", "the longest chain"], ["the {pottery}", "M, a node that lies"], ["three pages deep", "two more blocks on top"]],
  scenes: {
    fork: { name: "Two pages at once", note: nkaNote, prose: [
      "The {fishery}'s payment book is one page long.",
      "The {fishery} finishes the sum: it adds page 2a after page 1, and sends it to the {granary} and the {winery}.",
      "Page 2b arrives from the {granary}, also after page 1. The two payment books are the same length. The {fishery} heard of its own first, so it keeps adding to 2a, and keeps 2b too.",
      "Page 3 arrives from the {winery}, written after 2b. That payment book is now the longest, so the {fishery} switches to it. 2a is set aside."],
      out: { 3: "the {granary} switches too. Every business now adds to 2b. Payments only on page 2a go back to waiting for a page" } },
    shallow: { name: "Paid one page deep", note: "Rule: hand over the goods once the payment is on a page of your longest payment book.",
      outside: "The {pottery} pays the {fishery}, and meanwhile works in secret on a payment book in which it never paid. The {pottery} is lucky.", prose: [
      "The {fishery}'s payment book is one page long. The {pottery} has promised to pay for 20 amphorae, which the {fishery} will hand over once the payment is on a page.",
      "Page 2 arrives from the {granary}, with the {pottery}'s payment on it. The {fishery} hands over the amphorae.",
      "Two pages arrive from the {pottery}, 2′ and 3′, after page 1. That payment book is longer, so the {fishery} switches to it. The payment is not in it."],
      out: { 2: "the {pottery} has the amphorae and its coins. Every honest business switched to the longer payment book, as the rule says" } },
    deep: { name: "Paid three pages deep", note: "Rule: hand over the goods once the payment has two more pages after it, three deep in all.",
      outside: "The {pottery} pays the {fishery}, and meanwhile works in secret on a payment book in which it never paid. The honest businesses finish sums faster than the {pottery}.", prose: [
      "The {fishery}'s payment book is one page long. The {pottery} has promised to pay for 20 amphorae, which the {fishery} will hand over once the payment is three pages deep.",
      "Page 2 arrives from the {granary}, with the {pottery}'s payment on it. One deep: the {fishery} waits.",
      "Page 3 arrives after it. Two deep.",
      "Two pages arrive from the {pottery}, 2′ and 3′, after page 1. That payment book is no longer than the {fishery}'s, so the {fishery} stays where it is.",
      "Page 4 arrives. The payment is three deep, and the {fishery} hands over the amphorae."],
      out: { 4: "the {pottery}'s payment book is a page behind and would have to outgrow the honest one. While the honest businesses are faster, the chance of that shrinks with every page it falls behind" } },
  } };

TELL.chash = { hat: "scholar", role: "librarian",
  stage: { view: "city", A: "northwest library", B: "temple library", C: "southeast library", D: "temple", labels: { crossroads: "a reader" }, client: "crossroads" }, client: "reader",
  lex: [[/^keys\(/, "scrolls("], [/^keys$/, "scrolls held"], [/^place$/, "place on the dial"], ["joining at 65", "opening at 65 on the dial"], ["joining as number 3", "opening as library number 3"],
    [/^read key (\d+)$/, "fetch scroll $1"], [/^ask D$/, "try the new library"], [/^store\((\d+)=(\w), for (\w)\)$/, "keep scroll $1 ($2) for $3"], [/^store\((\d+)=(\w)\)$/, "keep scroll $1 ($2)"],
    [/^stored$/, "shelved"], ["kept for others", "shelved for other libraries"], ["A answers again", "A is open again"], [/^write 13=y$/, "a new copy of scroll 13"], [/^my number$/, "library number"]],
  tale: "The libraries share out the scrolls by a dial numbered 0 to 99. Every scroll and every library has a place on it, and a scroll belongs to the first library at or after its place, going round. When a new library opens, it takes scrolls only from the library after it, and nobody else moves a thing. Shared out by counting libraries instead, nearly every scroll would change shelves. And when a library is closed for a while, the next one round keeps its scrolls with a note, and carries them back when it opens. This is the consistent hashing of Karger and his colleagues, as Chord and Dynamo use it.",
  frame: {
    goal: "Every scroll has a library everyone can work out, and when a library opens or closes, as few scrolls as possible change shelves.",
    shared: "The dial, the rule, and which libraries are open.",
    assumes: "Each library knows the others' places on the dial. Places are spread at random; the papers give each library several, to even out the load. Couriers carrying scrolls arrive. Nobody lies." },
  gloss: [["librarian", "node"], ["a scroll", "a key"], ["the dial", "the circle of hashed places"], ["the first library at or after a scroll", "the key's successor"], ["a scroll kept with a note", "a hinted replica"]],
  scenes: {
    join: { name: "A new library opens", note: "Scrolls and libraries have places on a dial numbered 0 to 99: {A} at 20, {B} at 50, {C} at 80. A scroll belongs to the first library at or after its place, going round. So {C} holds the scrolls from 51 to 80.", prose: [
      "Librarian {C}, at 80 on the dial, holds scrolls 58 and 72.",
      "A new library, {D}, opens at 65. Scrolls from 51 to 65 are now {D}'s, so {C} sends over 58 and keeps 72.",
      "A reader asks {C} for scroll 58. {C} sends them to the new library."],
      out: { 1: "{A} and {B} move nothing: no scroll changes between the libraries that were open before" } },
    modulo: { name: "If scrolls were dealt by count", note: "A different rule: number the libraries 0, 1, 2 and give a scroll to the library numbered by the remainder when the scroll's number is divided by the count of libraries. {C} is number 2 of three.", prose: [
      "Librarian {C}, number 2 of three, holds scrolls 17, 41 and 59: each leaves 2 when divided by 3.",
      "{D} opens as number 3. Now numbers are divided by 4: 17 and 41 leave 1, and go to {B}; 59 leaves 3, and goes to {D}. {C} keeps none of its scrolls.",
      "Scrolls 90 and 58 arrive from {A} and {B}: divided by 4, each leaves 2, so now they are {C}'s."],
      out: { 2: "every library reshuffled the same way. Six of the eight scrolls changed shelves, where one new library needed only about a quarter of them" } },
    handoff: { name: "Keeping scrolls for a closed library", note: "Each scroll is kept at the first two open libraries at or after its place on the dial: {A} at 20, {B} at 50, {C} at 80. Scroll 13 belongs to {A} and {B}. A copy kept for a closed library carries a note saying whose it is.",
      outside: "{A} is closed for a while.", prose: [
      "Librarian {C}, at 80, holds scrolls 58 and 72, and nothing for anyone else.",
      "A new copy of scroll 13 comes from {B}. Its home, {A}, is closed, so {C} is the next library open: {C} keeps the copy, with a note that it is {A}'s, and says so.",
      "{C} checks, and {A} is open again. {C} sends the copy over.",
      "{A} has it. {C} takes its own copy off the shelf."],
      out: { 1: "{B} had kept its own copy, so the scroll was in two libraries and the copyist could be told it was done while {A} was closed", 3: "scroll 13 is back at {A} and {B}, its own two libraries, and was in two libraries all along" } },
  } };

const fpaOut = "In round 1, {P} got red accepted by {A} and {B}. Under these rules that is enough to settle it, so the columns are red. Nobody has told {Q}.";
TELL.fpaxos = { hat: "legislator", role: "legislator", roles: { P: "proposer", Q: "proposer" },
  stage: { view: "city", A: "fishery", B: "granary", C: "winery", D: "pottery", P: "proposer P", Q: "proposer Q", also: ["temple"], client: "crossroads", labels: { crossroads: "a citizen" } }, client: "citizen",
  peers: "legislators {A}, {B}, {C} and {D}",
  lex: [[/\bx\b/g, "red"], [/\by\b/g, "blue"], ["get red chosen", "paint the columns red"], ["get blue chosen", "paint the columns blue"]],
  tale: "The columns again, red or blue, but now with four legislators, and a rule that asks less of the second half of each round. Promises must come from three; acceptances need only two. Every three and every two share a legislator, so a later round always hears of a colour already settled. Two pairs may share nobody, and that is fine. Shrink the promises to two as well, and a round can miss the pair that settled it. This is the Flexible Paxos of Howard, Malkhi and Spiegelman.",
  frame: {
    goal: "Choose exactly one colour for the columns and never change it, as before, but with fewer acceptances needed in each round.",
    shared: "The chosen colour, as before: whatever enough legislators accepted in one round. Up front, everyone knows the roll and how many promises and acceptances a round needs.",
    assumes: "As before: legislators work at any pace and may leave office, a successor starting from the ledger; couriers can be delayed, sent twice or lost, but never altered. Nobody lies. Needing fewer acceptances is paid for by needing more promises." },
  gloss: [["legislator", "voter"], ["red, blue", "the two values, x and y"], ["three promising legislators", "a phase-1 quorum"], ["two accepting legislators", "a phase-2 quorum"]],
  scenes: {
    overlap: { name: "Three to promise, two to accept", note: "Four legislators. A round needs promises from any three, and acceptances from any two. Every three and every two share a legislator, though two pairs need not.", outside: fpaOut,
      phases: ["Three promises", "Two acceptances"], prose: [
      "{Q}, a proposer, has tried no round yet.",
      "A citizen asks {Q} to have the columns painted blue. {Q} claims round 2 and asks {B}, {C} and {D} to promise. Any three will do.",
      "{B} promises, reporting a vote for red in round 1.",
      "{C} promises, having accepted nothing.",
      "{D} promises, having accepted nothing. Three promises. {B}'s report means red may already be settled, so {Q} must propose red, not blue, and asks {C} and {D}.",
      "{C} and {D} accept. Two acceptances in round 2: red is settled, again, and {Q} writes it in the ledger."],
      out: { 5: "{C} and {D} share no legislator with {A} and {B}. That is safe: what must overlap is each round's three with every earlier round's two" } },
    disjoint: { name: "Two to promise, two to accept", note: "A different rule: promises from any two, acceptances from any two. Two pairs can miss each other.", outside: fpaOut,
      phases: ["Two promises", "Two acceptances"], prose: [
      "{Q}, a proposer, has tried no round yet.",
      "A citizen asks {Q} to have the columns painted blue. {Q} claims round 2 and asks {C} and {D} to promise. Any two will do.",
      "{C} and {D} promise, neither having accepted anything. Nobody reports a vote, so {Q} proposes blue.",
      "{C} and {D} accept. Two acceptances in round 2: {Q} takes blue as settled."],
      out: { 3: "red was settled in round 1 by {A} and {B}, whom {Q} never asked. The columns are both red and blue" } },
  } };

const craNote = "The libraries form a line: {A} first, then {B}, then {C}, the last. New figures are brought to the first and passed down the line in order. Students ask the last, and only the last answers anyone.";
TELL.chain = { hat: "scholar", role: "scholar", roles: { M: "registrar" },
  stage: { view: "city", A: "northwest library", B: "temple library", C: "southeast library", M: "temple", labels: { crossroads: "a student" }, client: "crossroads" }, client: "student",
  lex: [[/^update\((\d+): ([xyz])\)$/, "new figure $1: $2"], [/^ack\((\d+)\)$/, "figure $1 is in at the end of the line"], ["sent, not yet acked", "passed on, not yet confirmed"],
    ["your next node is now C", "pass figures to C from now on"], ["the node before you is now A", "take figures from A from now on"], [/^next$/, "passing figures to"], [/^before$/, "taking figures from"], [/^write y$/, "a new measurement: y"],
    ["read the value", "how many stadia round the Earth?"], ["no word from B", "no word from B's library"], [/^chain$/, "the line"],
    [/(\d+): ([xyz])$/, "figure $1: $2"], [/\bx\b/g, "250,000"], [/\by\b/g, "252,000"], [/\bz\b/g, "251,000"]],
  tale: "Three libraries stand in a line. A new measurement is brought to the first, which copies it and passes it to the next, and so down to the last. Students ask only the last library, and only the last answers anyone, so no figure is given out until every library has it. If a library in the middle closes, the registrar closes up the line, and the library before it sends on again everything the end of the line has not yet confirmed. This is the chain replication of van Renesse and Schneider.",
  frame: {
    goal: "Students hear answers a single library could have given, while libraries close and the line closes up around them.",
    shared: "The figure, a copy at every library in the line. The registrar keeps the list of who is in the line, and tells the libraries when it changes.",
    assumes: "Couriers between neighbours in the line arrive, and in order. Libraries close but nobody lies, and a closed library is noticed; the registrar keeps its list safe by a vote of its own. Not every library closes at once." },
  gloss: [["the first library", "the head"], ["the last library", "the tail"], ["the registrar", "M, the master"], ["passed on, not yet confirmed", "Sentᵢ, updates not yet acknowledged by the tail"]],
  scenes: {
    tail: { name: "Only the last answers", note: craNote, outside: "A copyist has brought {A}, the first library, a new figure: 252,000.", prose: [
      "Scholar {C}, at the last library, holds 250,000 stadia round the Earth.",
      "The new figure, 252,000, comes down the line from {B}. {C} copies it, tells the copyist it is in, and sends word back up the line.",
      "A student asks {C} how many stadia it is round the Earth. {C} answers 252,000."],
      out: { 1: "{A} and {B} copied 252,000 before {C}, but answered nobody. Since only the last answers, nobody hears it until every library has it", 2: "anything the last library gives out is already in every library, so a library closing can't take it back" } },
    anynode: { name: "If any library answered", note: "A different rule: new figures still enter at the first library and pass down the line, but any library answers students from its own copy.", prose: [
      "Scholar {A}, at the first library, holds 250,000.",
      "A copyist brings {A} a new figure, 252,000. {A} copies it and passes it to {B}.",
      "A student asks {A}. {A} answers 252,000."],
      out: { 2: "a moment later another student asks {C}, which hasn't got the new figure yet, and is told 250,000. New, then old" } },
    middle: { name: "A library in the middle closes", note: "Each library keeps a list of the figures it has passed on that the end of the line hasn't confirmed. When the library after it changes, it first sends that list on again.",
      outside: "{A} passed figure 2, 251,000, to {B}. {B}'s library closed before passing it on.", prose: [
      "Scholar {A}, at the first library, has copied 251,000 and passed it to {B}. The end of the line hasn't confirmed it.",
      "The registrar says {B}'s library is closed and {A} should pass figures to {C} from now on. Before anything else, {A} sends {C} everything on its list.",
      "{C} confirms figure 2. {A} strikes it from the list."],
      out: { 2: "{C} copied 251,000 and told the copyist it was in. Nothing {B} held was lost, because {A} kept everything the end of the line hadn't confirmed" } },
  } };

const ttaNote = "The {fishery} posts the price of fish, and the {granary} the price of grain. Every new price is posted with a time, and anyone asking for prices “as of” a time is told the prices posted no later. Each water clock may be off by up to 5, and its keeper knows it: it gives the earliest and the latest the true time could be.";
TELL.truetime = { hat: "merchant", role: "merchant",
  stage: { view: "city", A: "fishery", B: "granary", client: "crossroads", labels: { crossroads: "a customer" } }, client: "customer",
  names: { A: "{fishery}", B: "{granary}" },
  lex: [["write a=y", "post fish at 3 obols"], ["write b=z", "post grain at 5 obols"], [/^read a as of (\d+)$/, "the fish price as of $1"], [/^read b as of (\d+)$/, "the grain price as of $1"],
    [/a=y/g, "fish at 3 obols"], [/b=z/g, "grain at 5 obols"], [/a=x/g, "fish at the old price"], [/^a$/, "fish price"], [/^b$/, "grain price"],
    [/^y @/, "3 obols @"], [/^z @/, "5 obols @"], [/^x$/, "the old price"], [/^clock reads (\d+)$/, "the water clock reads $1"], [/^pending$/, "waiting to post"]],
  tale: "No two water clocks in {town} agree, but each keeper knows how far off theirs might be. That is enough to post prices in the right order. A business stamps a new price with the latest the time could be, and doesn't put it up until the earliest the time could be is past that stamp. Then anything that happens after the price goes up is stamped later, wherever it happens, so prices asked for as of any time are ones that were really up together. This is Spanner's TrueTime, with water clocks.",
  frame: {
    goal: "If one price goes up before another is posted, the first carries the earlier time, so prices asked for as of any time are ones that were really up together.",
    shared: "Each business's own prices. Up front, a water clock at each, with a known limit on how far off it can be.",
    assumes: "No water clock is ever further off than its keeper believes. The wait costs about twice that limit on every new price. Lost couriers and businesses that shut are left aside here. Nobody lies." },
  gloss: [["a posted price", "a write"], ["the time on it", "its timestamp"], ["earliest and latest the time could be", "TrueTime's interval"], ["waiting before posting", "commit wait"]],
  scenes: {
    wait: { name: "Wait out the doubt", note: ttaNote + " Rule: stamp a price with the latest the time could be, and don't put it up until the earliest the time could be has passed the stamp.",
      outside: "At true time 20, the {fishery}'s water clock reads 24.", prose: [
      "The {fishery} has fish at the old price.",
      "A customer asks for fish at 3 obols. The water clock reads 24, so the true time is somewhere from 19 to 29. The {fishery} stamps the new price 29, the latest it could be, and waits.",
      "The water clock reads 35: the true time is at least 30, so 29 is surely past. The {fishery} puts the price up and says so."],
      out: { 2: "the customer then has grain posted at 5 obols at the {granary}. Whatever its clock says, the true time is now past 30, so its stamp is at least 30: after the fish. Effects are stamped after their causes" } },
    nowait: { name: "Trust the water clock", note: ttaNote + " A different rule: stamp a price with what your water clock reads, and put it up at once.",
      outside: "At true time 20, the {fishery}'s water clock reads 24, four ahead. The {granary}'s is four behind.", prose: [
      "The {fishery} has fish at the old price.",
      "A customer asks for fish at 3 obols. The water clock reads 24, so the {fishery} stamps the price 24 and puts it up at once.",
      "Someone asks for the fish price as of 20. The new price is stamped 24, later than 20, so the {fishery} gives the old price."],
      out: { 2: "the customer, told fish was up at 3 obols, then had grain posted at the {granary}, whose clock read 17, so it is stamped 17. Asking as of 20, one sees the new grain price and the old fish price: the effect without its cause" } },
  } };
