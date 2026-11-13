// ---------- filing ----------
const CHAPTERS = [
  ["Order without a clock", ["clocks", "snapshot", "cops"]],
  ["Agreeing on one thing", ["flp", "suspect", "benor", "commit", "paxos", "vr"]],
  ["Agreeing among liars", ["liars", "pbft"]],
  ["Answering without waiting", ["linear", "cap", "quorum", "merge", "bayou"]],
];
const HAZARDS = [["lost", "messages lost", "couriers lost"], ["reorder", "messages out of order", "couriers out of order"], ["stop", "a node stops for good", "someone is gone for good"],
  ["replace", "a node is replaced", "someone is replaced"], ["lie", "nodes lie", "some are traitors"], ["noclock", "no clocks", "no clocks"]];
const PAPER_TAGS = {
  clocks: "lost reorder noclock", snapshot: "noclock", flp: "reorder stop noclock", paxos: "lost reorder replace noclock",
  vr: "lost reorder replace", benor: "reorder stop noclock", commit: "lost stop replace", linear: "", liars: "lie", cap: "lost", merge: "lost reorder replace", suspect: "reorder stop",
  pbft: "lost reorder lie", quorum: "lost reorder replace", cops: "reorder noclock", bayou: "reorder replace",
};
const OUTCOME = {
  wrong: "snapshot-naive flp-slow paxos-broken liars-sender cap-stale merge-total quorum-one cops-eager commit-giveup linear-newold",
  stuck: "flp-wait cap-wait commit-wait",
};
const VERDICT = { works: "It works.", wrong: "It goes wrong.", stuck: "It never finishes." };
// One sentence per scene: what to take away from it, in plain terms.
const TAKE = {
  "clocks-jump": "Receiving a stamp pushes the counter past it, so an effect is always numbered after its cause.",
  "clocks-ties": "Equal stamps are ordered by node name, so every node lists events in the same order.",
  "clocks-vector": "One count per node can show that two events are unrelated. A single counter cannot.",
  "snapshot-markers": "A node copies at its first marker and records each stream until that stream's marker, so every unit in transit is counted exactly once.",
  "snapshot-naive": "Without markers, a node cannot tell which arrivals belong to the snapshot, and units in transit end up in no copy.",
  "flp-stopped": "A rule that stops waiting can decide without a silent node. Here that happens to be safe.",
  "flp-slow": "The same rule takes the same steps when the silent node is only slow, and two nodes decide differently.",
  "flp-wait": "A rule that waits for everyone is never wrong, and never finishes once one node has stopped.",
  "suspect-forgive": "A suspicion can be withdrawn, and each mistake lengthens the wait, so the mistakes eventually stop.",
  "suspect-stopped": "Suspecting a silent coordinator lets the round move on, and the next coordinator finishes.",
  "suspect-slow": "A wrong suspicion costs a round, never agreement: the locked value is carried into the next round.",
  "paxos-round": "A proposer needs a majority twice: once to claim a round, once to have its value accepted.",
  "paxos-voter": "A voter reports its last vote with every promise, which forces later proposers to keep the old value.",
  "paxos-survive": "Any two majorities share a voter, so a later round always hears about a value already chosen.",
  "paxos-broken": "If a voter forgets its promises, the overlap breaks and a second value gets chosen.",
  "vr-force": "An event is safe once a majority of nodes know it. The primary does the work, and the backups only need to be told.",
  "vr-cutoff": "A cut-off primary can keep running calls, but nothing it does reaches a majority, and the next view starts without it.",
  "vr-form": "The new primary is the node that knows the most, so everything a majority knew is carried into the new view.",
  "benor-coin": "When no value has a majority, each node flips a coin. Sooner or later the coins agree, and nothing was assumed about timing.",
  "benor-spread": "A node that sees even one proposal adopts it without a coin, so a decision made anywhere is soon made everywhere.",
  "commit-agree": "A node that agrees gives up the right to back out. Only then can the coordinator decide for everyone.",
  "commit-veto": "Any one participant can refuse, and then all abort, including those that agreed.",
  "commit-wait": "A participant that has agreed and hears nothing can neither finish nor undo. It waits for the coordinator, however long.",
  "commit-giveup": "Deciding alone after agreeing can leave one participant committed and another undone.",
  "linear-underway": "Operations that overlap may take effect in either order. Every answer here fits one copy that changed once.",
  "linear-newold": "Once any reader has been given the new value, a read that begins later must not be given the old one.",
  "liars-sender": "With three nodes, a receiver that hears two stories cannot tell which of the other two is lying.",
  "liars-relay": "Trusting the sender is right here, and the receiver cannot tell this case from the one where it is wrong.",
  "liars-four": "With four nodes, the honest receivers outvote one liar, even when the liar is the sender.",
  "liars-fourrelay": "A lying receiver is outvoted as well, and the sender's value stands.",
  "pbft-order": "A backup acts only after two rounds of matching messages from three of the four nodes.",
  "pbft-liar": "A lying primary can stall a request but cannot split the honest nodes. A view change replaces it.",
  "cap-fresh": "Answering without hearing from the other side is right when nothing was written there.",
  "cap-stale": "The same answer is stale when the other side took a write, and the node cannot tell which case it is in.",
  "cap-wait": "Refusing to answer without the other side is always correct, and gives no answer while messages are lost.",
  "quorum-overlap": "When read and write groups must overlap, every read meets a copy that holds the latest write.",
  "quorum-one": "Reading a single copy is faster, and can miss a write that was already reported done.",
  "quorum-siblings": "When neither version is newer, both are kept and the client combines them.",
  "merge-counter": "State that only grows, merged by keeping the larger part, needs no waiting and shrugs off loss and repeats.",
  "merge-total": "A single total cannot tell a repeat from a separate add, so it either loses counts or doubles them.",
  "merge-set": "Giving every add its own tag lets a remove delete only what it saw.",
  "cops-wait": "A message that arrives before its cause is held back, so no reader sees an effect without its cause.",
  "cops-eager": "Applying messages in the order they arrive can show an effect whose cause has not arrived.",
  "bayou-moved": "A tentative write shows at once, and may be replayed in a different final order using its fallback.",
};
// What each scene is based on: the concept in the literature's terms, then which of its result's sources (lines of `cite`) it follows.
const BASIS = {
  "clocks-jump": ["Logical clocks: a receiver sets its clock past the timestamp on the message", [0]],
  "clocks-ties": ["A total order of events: equal timestamps are ordered by process name", [0]],
  "clocks-vector": ["Vector clocks: telling concurrent events from causally ordered ones", [2, 1]],
  "snapshot-markers": ["The marker algorithm for recording a consistent global state", [0]],
  "snapshot-naive": ["An inconsistent global state: copies taken without markers miss messages in transit", [0]],
  "cops-wait": ["Causal delivery: a message is delayed until everything it depends on has been delivered", [0]],
  "cops-eager": ["A causality violation: delivering messages in the order they arrive", [0]],
  "flp-stopped": ["Deciding by timeout in an asynchronous system, when the silent process has crashed", [0]],
  "flp-slow": ["A slow process cannot be told from a crashed one, so deciding by timeout can break agreement", [0]],
  "flp-wait": ["Waiting for every process keeps agreement, and loses termination after one crash", [0]],
  "suspect-forgive": ["An unreliable failure detector that is eventually accurate: suspicions are withdrawn and timeouts grow", [1, 0]],
  "suspect-stopped": ["Rotating-coordinator consensus: a suspected coordinator is passed over", [1]],
  "suspect-slow": ["A false suspicion is harmless: the locked estimate carries into the next round", [1]],
  "benor-coin": ["Randomized consensus: a coin flip when no value has a majority", [0]],
  "benor-spread": ["Randomized consensus: a single proposal is adopted without a coin, so a decision spreads", [0]],
  "commit-agree": ["Two-phase commit: every participant agrees, then the coordinator commits", [0]],
  "commit-veto": ["Two-phase commit: one refusal aborts the transaction everywhere", [0]],
  "commit-wait": ["Blocking: a participant that has agreed must wait for a stopped coordinator", [0, 1]],
  "commit-giveup": ["Why a participant that has agreed may not decide alone: atomicity is lost", [0]],
  "paxos-round": ["Single-decree Paxos, the proposer: one ballot in two phases, each needing a majority", [0, 1]],
  "paxos-voter": ["Single-decree Paxos, the acceptor: every promise reports the last vote cast", [0, 1]],
  "paxos-survive": ["Paxos safety: majorities overlap, and a voter's ledger outlasts the voter", [0]],
  "paxos-broken": ["Why Paxos needs stable storage: a forgotten promise lets a second value be chosen", [0]],
  "vr-force": ["Primary copy replication: an event record is forced to a majority before it counts", [0]],
  "vr-cutoff": ["A partitioned primary: its work reaches no majority, and a new view forms without it", [0]],
  "vr-form": ["View change: the cohort with the latest viewstamp becomes the new primary", [0]],
  "liars-sender": ["Impossibility with three generals: a traitorous commander", [1, 0]],
  "liars-relay": ["Impossibility with three generals: a traitorous lieutenant looks just the same", [1, 0]],
  "liars-four": ["The oral-messages algorithm OM(1) with four generals: a traitorous commander", [1]],
  "liars-fourrelay": ["The oral-messages algorithm OM(1) with four generals: a traitorous lieutenant", [1]],
  "pbft-order": ["Normal-case operation: pre-prepare, prepare and commit, as a backup sees them", [0]],
  "pbft-liar": ["A faulty primary that equivocates, and the view change that replaces it", [0]],
  "linear-underway": ["Linearizability: operations that overlap may take effect in either order", [0]],
  "linear-newold": ["Linearizability: an operation that ended before another began must take effect first", [0]],
  "cap-fresh": ["Availability during a partition: answering from the local copy", [0, 1]],
  "cap-stale": ["The CAP argument: an available node cannot know of a write on the far side of a partition", [1]],
  "cap-wait": ["Consistency during a partition: refusing to answer gives up availability", [0, 1]],
  "quorum-overlap": ["Quorum intersection: read and write quorums with r + w greater than N", [0]],
  "quorum-one": ["A read quorum too small to overlap the write quorum can miss a finished write", [0]],
  "quorum-siblings": ["Version vectors: detecting updates made apart, where neither version is newer", [2]],
  "merge-counter": ["A state-based replicated data type: the grow-only counter, spread by anti-entropy", [1, 0]],
  "merge-total": ["Why a merge must be idempotent: a single total cannot tell a repeat from a new add", [1]],
  "merge-set": ["A replicated set with removal: every add is tagged, so a remove deletes only what it observed", [1]],
  "bayou-moved": ["Tentative and committed writes: a dependency check and a merge procedure let a write be replayed in the final order", [0]],
};
// What a result's scenes add up to. `steps` gives each scene's part in the argument, in words that hold in both registers, and `end` where
// the argument lands; together they make the thread shown on every scene. `sum` is the whole idea, [in plain terms, as told on the island],
// shown once the last scene has been read. A result with a single scene has neither.
const ARC = {
  clocks: { steps: { jump: "a count that jumps past each message", ties: "names settle the ties", vector: "one count each shows what is unrelated" }, end: "order without a clock",
    sum: ["No node has a clock the others can read, yet all of them can agree on what came first. Counting events, and carrying the count on every message, puts each cause before its effect. Names settle the ties, so everyone lists events in the same order. And one count per node shows which events had nothing to do with each other.",
      "No house has a clock the others can read, yet all three can agree on what came first. Numbering ledger lines, and writing the number on every order, puts each cause before its effect. Names settle the ties, so everyone lists the day in the same order. And one count per business shows which lines had nothing to do with each other."] },
  snapshot: { steps: { markers: "markers close each stream, and everything is counted once", naive: "without them, what is in transit is counted nowhere" }, end: "a true picture, taken without stopping",
    sum: ["Nobody can read every node at the same instant, and nothing stops to be read. Without markers the copies are taken at moments that do not fit together, and units on the way fall between them. A marker on each stream tells the receiver exactly which arrivals belong to the snapshot, so the pieces add up to a state the system could really have been in.",
      "Nobody can count every storeroom at the same instant, and no business stops trading to be counted. Without the notes the tallies are taken at moments that do not fit together, and amphorae on the road fall between them. A note on each road tells the receiver exactly which deliveries belong to the count, so the tallies add up to a stock Paxos could really have held."] },
  cops: { steps: { wait: "hold an effect back until its cause has come", eager: "apply on arrival, and an effect shows without its cause" }, end: "answer at once, causes first",
    sum: ["Each site answers at once, and hears of the other's writes late and in any order. Applied as they arrive, an effect can show before its cause. Held back until what it depends on has come, it never does, and nobody waits for anything except the missing cause.",
      "Each library answers its own visitors at once, and hears of the other's notes late and in any order. Entered as they arrive, an effect can show before its cause. Held back until the earlier notes have come, it never does, and nobody waits for anything except the missing cause."] },
  flp: { steps: { stopped: "deciding without the silent one can be right", slow: "by the same steps, it can be wrong", wait: "waiting is never wrong, and may never end" }, end: "no rule escapes both",
    sum: ["From inside, the three scenes are the same silence: a node that hears nothing cannot tell a stopped peer from a slow one. A rule that stops waiting is right in one world and wrong in the other, and a rule that keeps waiting never finishes. The paper proves this is no weakness of these particular rules. If even one node may stop, every rule has some run in which it never decides.",
      "From inside, the three scenes are the same silence: a legislator who hears nothing cannot tell a colleague who is gone from one whose couriers are slow. A rule that stops waiting is right in one world and wrong in the other, and a rule that keeps waiting never finishes. The paper proves this is no weakness of these particular rules. If even one legislator may be gone for good, every rule has some run in which it never decides."] },
  suspect: { steps: { forgive: "a suspicion can be taken back", stopped: "a right one moves the round on", slow: "a wrong one costs a round, never agreement" }, end: "guessing is safe",
    sum: ["Nobody can know whether a silent node has stopped, so the nodes guess, and are allowed to be wrong. The guess only decides when to stop waiting and try the next coordinator. What gets decided is protected separately: a value locked by a majority is found by every later coordinator. So a right suspicion saves the round, a wrong one wastes it, and neither can split the decision.",
      "Nobody can know whether a silent colleague is gone, so the legislators guess, and are allowed to be wrong. The guess only decides when to stop waiting and turn to the next president. The colour is protected separately: once a majority has said yes to it, every later president finds it. So a right suspicion saves the round, a wrong one wastes it, and neither can split the decision."] },
  benor: { steps: { coin: "no majority, so toss a coin", spread: "one proposal seen, so adopt it without a coin" }, end: "agreement, sooner or later",
    sum: ["A fixed rule can be held off forever, so this one leaves something to chance. The coin is tossed only when no value has a majority, where either outcome is safe, and a node that sees a proposal never tosses at all. So chance can only break ties, and with probability 1 the coins eventually agree and everyone decides.",
      "A fixed rule can be held off forever, so this one leaves something to chance. The coin is tossed only when no colour has a majority, where either outcome is safe, and a legislator who sees a proposal never tosses at all. So chance can only end ties, and sooner or later the coins agree and everyone decides the same colour."] },
  commit: { steps: { agree: "all say yes, and it is done", veto: "one no undoes it for all", wait: "yes, then silence: stuck", giveup: "deciding alone splits the outcome" }, end: "all or nothing, at the price of waiting",
    sum: ["All-or-nothing is bought with a promise. A participant that agrees gives up the right to back out, which is what lets the coordinator decide for everyone, and lets any one refusal abort for everyone. The price shows when the coordinator falls silent: a participant that has agreed can neither finish nor undo, and if it decides alone the outcome can split. So it must wait.",
      "All-or-nothing is bought with a promise. A business that says yes gives up the right to back out, which is what lets the notary settle the swap for both, and lets either one's no call it off for both. The price shows when the notary falls silent: a business that has said yes can neither hand its goods over nor put them back, and if it settles the matter alone the swap can go through on one side only. So it must wait."] },
  paxos: { steps: { round: "a proposer needs a majority twice", voter: "every promise reports the last vote", survive: "so a chosen value outlives its voters", broken: "unless a promise is forgotten" }, end: "one value, never changed",
    sum: ["One value is chosen and never changed, though proposers compete, messages are lost and nodes are replaced. A proposer must win a majority twice, and each promise it collects reports that voter's last vote. Any two majorities share a voter, so a later round always hears of a value already chosen and must propose it again. All of this rests on voters keeping promises and votes in permanent state. Let one forget, and a second value can be chosen.",
      "One colour is chosen and never changed, though proposers compete, couriers are lost and legislators are replaced. A proposer must win a majority twice, and each promise it collects reports that legislator's last vote. Any two majorities share a legislator, so a later round always hears of a colour already chosen and must propose it again. All of this rests on promises and votes being written in the ledger. Put them on the slate, and a second colour can be chosen."] },
  vr: { steps: { force: "safe once a majority knows it", cutoff: "cut off from the majority, nothing lasts", form: "whoever knows the most leads the new view" }, end: "the work outlives whoever leads it",
    sum: ["One node does the work and the rest are told, and an event counts only once a majority know it. That one test does everything. A primary that is cut off reaches no majority, so nothing it does survives. A new view takes as its primary the node that knows the most, so everything a majority knew is carried over. The copies go on behaving as one, whichever node is in charge.",
      "One legislator presides and the rest are told, and a decree counts only once a majority know it. That one test does everything. A president who is cut off reaches no majority, so nothing done alone survives. A new view is presided over by whoever knows the most, so every decree a majority knew is carried over. The legislators go on acting as one, whoever presides."] },
  liars: { steps: { sender: "three: the sender lies", relay: "three: a receiver lies, and it looks the same", four: "four: a lying sender is outvoted", fourrelay: "four: so is a lying receiver" }, end: "3m + 1 to survive m liars",
    sum: ["With three nodes, a receiver that hears two stories is in the same position whether the sender lied or the other receiver did, so no rule is right in both cases. A fourth node breaks the symmetry: the honest receivers compare what they were told and outvote one liar, whoever it is. In general it takes 3m + 1 nodes to survive m liars.",
      "With three officers, a lieutenant who hears two stories is in the same position whether the commander lied or the other lieutenant did, so no rule is right in both cases. A fourth officer breaks the symmetry: the loyal lieutenants compare what they were told and outvote one traitor, whoever it is. In general it takes 3m + 1 officers to survive m traitors."] },
  pbft: { steps: { order: "act only on three matching voices, twice over", liar: "so a lying leader can stall, not split" }, end: "one order, even among liars",
    sum: ["What worked for one value among liars is made to work for a stream of requests. A node acts on a request only after two rounds of matching messages from three of the four. Any two such groups share an honest node, so no two honest nodes can run different requests in the same slot. A lying primary can therefore only stall, and a stall is answered by changing the view.",
      "What worked for one order among traitors is made to work for a stream of requests. An officer acts on a request only after two rounds of matching messages from three of the four. Any two such groups share a loyal officer, so no two loyal officers can run different requests in the same slot. A lying commanding officer can therefore only stall, and a stall is answered by changing the view."] },
  linear: { steps: { underway: "answers that overlap a change may go either way", newold: "but never the new one and then the old" }, end: "answers a single copy could have given",
    sum: ["This result is a test, not a method. Many copies behave as one if every answer could have come from a single copy that changed at one moment. While a write is under way, old and new answers are both acceptable. Once anyone has been given the new value, the old one is ruled out for every later read. No node can check this alone, because the test needs every answer and when it was given.",
      "This result is a test, not a method. Two scholars are as good as one if every answer could have come from a single scholar who changed the figure once. While the new figure is on its way, old and new answers are both acceptable. Once any student has been told the new figure, the old one is ruled out for every student who asks later. No scholar can check this alone, because the test needs every answer and when it was given."] },
  cap: { steps: { fresh: "answer alone, and be right", stale: "answer alone, by the same steps, and be out of date", wait: "refuse, and be correct but silent" }, end: "the latest, or an answer, never both",
    sum: ["Cut off from the other side, a node cannot tell a write it missed from no write at all. If it answers, the answer is right in one world and stale in the other, by exactly the same steps. If it refuses, it is never wrong, and gives no answer for as long as messages are lost. So while messages are lost a system can promise the latest value or an answer to every request, and never both.",
      "Cut off from the other, a scholar cannot tell a correction that never arrived from no correction at all. A scholar who answers is right in one world and out of date in the other, by exactly the same steps. A scholar who refuses is never wrong, and gives no answer for as long as couriers are lost. So while couriers are lost the scholars can promise the latest figure or an answer to every student, and never both."] },
  quorum: { steps: { overlap: "groups that overlap always find the latest write", one: "a smaller group answers sooner, and can miss it", siblings: "changes made apart are kept side by side" }, end: "wait for some, not all",
    sum: ["Waiting for every copy stops the moment one is out of reach, so wait for some. If the group a read waits for must share a node with the group a write waited for, the read always meets the latest finished write. Shrink the groups and answers come sooner, but can miss it. And when two writes are made apart, neither is newer: the counts on each version show it, and both are kept for the client to combine.",
      "Waiting for every librarian stops the moment one is out of reach, so wait for some. If the librarians a read waits for must include one of those a write waited for, the read always meets the latest finished write. Ask fewer and the answer comes sooner, but can miss it. And when two changes are made apart, neither is newer: the counts on each version show it, and both are kept for the reader to combine."] },
  merge: { steps: { counter: "what only grows can merge without waiting", total: "a single total cannot", set: "tags make removal safe as well" }, end: "never wait, and still end up equal",
    sum: ["Nobody waits for anybody, and the copies still end up equal, provided the state is shaped for it. It must only grow, and merging must give the same result however often and in whatever order copies arrive. One count per node has that shape. A single total does not, because it cannot tell a repeat from a new add. Tagging every add extends the same idea to sets with removal.",
      "No scholar waits for another, and the copies still end up equal, provided what they keep is shaped for it. It must only grow, and merging must give the same result however often and in whatever order couriers arrive. One count per scholar has that shape. A single total does not, because it cannot tell a repeat from a new addition. Tagging every addition extends the same idea to lists with removal."] },
};
// Scenes worth reading side by side.
const PAIR = { "flp-wait": "flp-stopped", "cap-wait": "cap-stale", "liars-four": "liars-sender", "liars-fourrelay": "liars-relay" };
[["snapshot-markers", "snapshot-naive"], ["flp-stopped", "flp-slow"], ["suspect-stopped", "suspect-slow"], ["paxos-survive", "paxos-broken"], ["liars-sender", "liars-relay"],
  ["cap-fresh", "cap-stale"], ["commit-agree", "commit-veto"], ["commit-wait", "commit-giveup"], ["linear-underway", "linear-newold"], ["benor-coin", "benor-spread"], ["quorum-overlap", "quorum-one"], ["merge-counter", "merge-total"], ["cops-wait", "cops-eager"]].forEach(([a, b]) => { PAIR[a] = b; PAIR[b] = a; });

const outcomeOf = key => Object.keys(OUTCOME).find(o => OUTCOME[o].split(" ").includes(key)) || "works";
const ALL = CHAPTERS.flatMap(([chapter, ids]) => ids.flatMap(id => {
  const p = PAPERS.find(x => x.id === id);
  return p.scenes.map(s => ({ p, s, chapter, key: `${p.id}-${s.id}`, oc: outcomeOf(`${p.id}-${s.id}`) }));
}));
const byKey = k => ALL.find(x => x.key === k);
const twinOf = it => it.s.twin ? byKey(`${it.p.id}-${it.s.twin}`) : ALL.find(x => x.p === it.p && x.s.twin === it.s.id);
// The first step at which two scenes look different from inside (0 is the starting state); -1 if they never do.
const sig = (s, i) => { const r = i ? s.rows[i - 1] : s.init; return r ? JSON.stringify([r.perm || {}, r.temp || {}, i ? r.recv || [] : [], i ? (r.sent || []).map(m => m.slice(0, 2)) : []]) : null; };
function firstDiff(a, b) {
  for (let i = 0; i <= Math.max(a.rows.length, b.rows.length); i++) if (sig(a, i) !== sig(b, i)) return i;
  return -1;
}

