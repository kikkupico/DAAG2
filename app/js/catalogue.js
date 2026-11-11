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

