// ---------- the results added to the second set ----------
// Each is written against its paper, kept in sources/ (gitignored): see each PAPERS entry's `cite`.

// Two generals. Gray's proof: take the shortest rule that always gets both to act together; its last message may be lost.
const tgNote1 = "Rule: B acts at t if the plan reaches it, and replies. A acts at t only if B's reply reaches it.";
const tgNote2 = "Rule: one more message. B acts at t only if A confirms that B's reply arrived. A acts once the reply arrives, and confirms it.";
const tgInit = { perm: { decision: "none" }, temp: { plan: "act at t", "B has it": "not known" } };
const tg0 = "Node A means to act at time t, together with B. Either one acting alone fails. A has decided nothing yet.";
const tg1 = "In its first step nothing arrives, yet a step can still act: A sends the plan to B.";
const tgSend = { recv: N, sent: [["B", "act at t?"]] };
const tgConfirmProse = [tg0, tg1,
  "B's reply arrives: it has the plan, and will act if A confirms. A decides to act at t, and confirms.",
  "Time t comes, and A acts. It never learns whether its confirmation arrived: under this rule nobody replies to a confirmation.",
];
const tgConfirmRows = (lost, o2, o3) => [tgSend,
  { perm: { decision: "act at t" }, temp: { "B has it": "yes", "B has my confirmation": "not known" }, recv: [["B", "agreed, if confirmed"]],
    sent: [lost ? ["B", "confirmed", "lost"] : ["B", "confirmed"]], out: o2 },
  { perm: { decision: "acted at t" }, recv: T("time t"), out: o3 },
];
SCENES.twogen = [
  { id: "plan", name: "A plan and a reply", who: "A", peers: "B", note: tgNote1, init: tgInit,
    prose: [tg0, tg1,
      "B's reply arrives: it has the plan and will act. A now knows that B will act, and decides to act at t.",
      "Time t comes, and A acts."],
    rows: [tgSend,
      { perm: { decision: "act at t" }, temp: { "B has it": "yes" }, recv: [["B", "agreed"]],
        out: "B decided to act as soon as the plan reached it. It cannot know whether its reply arrived; under this rule it does not need to" },
      { perm: { decision: "acted at t" }, recv: T("time t"), out: "B acts at t as well. Both acted together" },
    ] },
  { id: "lostreply", name: "The reply is lost", who: "A", peers: "B", note: "Same rule.", outside: "Every reply B sends will be lost.", init: tgInit,
    prose: [tg0, tg1,
      "No reply comes before A's timer fires. A can't tell a lost plan from a lost reply, so it sends the plan again.",
      "Still no reply when time t comes. A doesn't know that B has the plan, so it does not act."],
    rows: [tgSend,
      { recv: T("no reply yet"), sent: [["B", "act at t?"]], out: "the plan had arrived, and B decided to act. Its reply was lost. This second copy arrives too, and B replies again" },
      { perm: { decision: "did not act" }, recv: T("time t"), out: "B's second reply was lost as well. B acts at t, alone" },
    ] },
  { id: "confirm", name: "One more message", who: "A", peers: "B", note: tgNote2, init: tgInit, prose: tgConfirmProse,
    rows: tgConfirmRows(false, "B now waits for the confirmation before it decides", "the confirmation arrived, so B acts at t as well") },
  { id: "lostconfirm", name: "The confirmation is lost", who: "A", peers: "B", twin: "confirm", note: tgNote2, outside: "A's confirmation will be lost.", init: tgInit, prose: tgConfirmProse,
    rows: tgConfirmRows(true, "this confirmation is lost. To B, a lost confirmation looks like one still on its way",
      "B never got the confirmation, so it does not act. A acts at t, alone. From inside A nothing differed from the scene before") },
];

PAPERS.push({
  id: "twogen", name: "The last message", year: "1975 / 1978",
  cite: "Akkoyunlu, Ekanadham & Huber 1975 · Some Constraints and Tradeoffs in the Design of Network Communications\nGray 1978 · Notes on Data Base Operating Systems (the generals paradox)",
  idea: "Two nodes must both act at a fixed time, or neither. Any message may be lost. Whatever rule they follow, it has a last message, and the sender of that message cannot know it arrived. If the rule could do without it, a shorter rule would do; if it can't, losing it leaves one node acting alone. So no rule with a fixed end works.",
  names: "node = general (Gray) or IPCM, the communication component at each end (Akkoyunlu et al.) · message = runner, messenger · act at t = march on the objective together · knowing for sure what happened at the other end = complete status (Akkoyunlu et al.) · the rule = a fixed-length protocol · the shortest rule whose last message is lost = Gray's proof",
  frame: {
    goal: "Both nodes act at time t, or neither does, and if no message is lost they both act.",
    shared: "Nothing but the rule. Each node knows only what has reached it.",
    assumes: "Any message may be lost, and a node can't tell lost from slow. Nodes don't stop and nobody lies. The deadline is what makes it impossible: Gray's two-phase commit escapes by allowing an unbounded number of messages, and so a node that may wait without limit." },
  scenes: SCENES.twogen });

// Signed messages: algorithm SM(1) of Lamport, Shostak & Pease, for three nodes and one liar.
const smNote = "Rule: S signs its value. Pass on what S signed, then decide: if S signed one value, take it; if it signed two, S lied, so take the default, y. A signature can't be forged, and anyone can check it.";
const smInit = { perm: { decided: "none" } };
const smRow1 = { temp: { "signed by S": "x" }, recv: [["S", "value(x, signed S)"]], sent: [["B", "relayed(x, signed S)"]] };
SCENES.signed = [
  { id: "sender", name: "Three nodes: the sender lies", who: "A", role: "receiver", peers: "sender S; receiver B", note: smNote,
    outside: "S is the liar: it signed x for A and y for B.", init: smInit,
    prose: [
      "A, a receiver, has decided nothing.",
      "S sends A the value x, with its signature. A passes the signed value on to B unchanged.",
      "B passes on y, also signed by S. B could not have made that signature, so S signed two different values: S lied. A takes the default, y."],
    rows: [smRow1,
      { perm: { decided: "y" }, temp: { "signed by S": "x, y" }, recv: [["B", "relayed(y, signed S)"]],
        out: "B holds the same two signed values and decides y too. Without signatures, this is the case that split them" } ] },
  { id: "relay", name: "Three nodes: a receiver lies", who: "A", role: "receiver", peers: "sender S; receiver B", note: smNote,
    outside: "S is honest and signed x for both. B is the liar.", init: smInit,
    prose: [
      "A, a receiver, has decided nothing.",
      "S sends A the value x, with its signature. A passes the signed value on to B unchanged.",
      "B claims that S said y, but S's signature on it doesn't check out. A discards it. S signed only x, so A decides x."],
    rows: [smRow1,
      { perm: { decided: "x" }, temp: { discarded: "y: forged" }, recv: [["B", "relayed(y, forged S)"]],
        out: "B could only lie about S's value by forging S's signature, and a forgery is seen at once. Three nodes are enough" } ] },
];

PAPERS.push({
  id: "signed", name: "Signed messages", year: "1982",
  cite: "Lamport, Shostak & Pease 1982 · The Byzantine Generals Problem (section 4, Algorithm SM(m))",
  idea: "Liars are hard to beat because they can say anything about what others said. Take that away: the sender signs its value, nobody can forge a signature, and anyone can check one. Each receiver passes the signed value on. If the sender signed two different values, everyone sees both and takes the same default. Then the rule copes with any number of liars among any number of nodes, and three nodes are enough for one.",
  names: "sender = commander, General 0 · receivers = lieutenants · signed by S = v : 0 · relayed = v : 0 : i · the set of values signed by S = Vᵢ · take the default for two values = choice(V), with choice(∅) = RETREAT · liar = traitor · x, y = attack, retreat · signatures that can't be forged = assumption A4",
  frame: {
    goal: "One node sends a value. All honest nodes decide the same value, and if the sender is honest, that is the value it sent.",
    shared: "Up front: the list of nodes, which one sends, the default value, and a way for anyone to check anyone's signature.",
    assumes: "Every message sent arrives, and a missing one can be noticed. An honest node's signature can't be forged and its signed message can't be altered unseen; liars may share each other's. Up to m nodes lie; the rule works whenever there are at least m + 2 nodes, and here m = 1. With one liar, one round of passing on is enough." },
  scenes: SCENES.signed });

// Choosing a leader: Chang & Roberts on a ring; Garcia-Molina's Bully algorithm, and his Theorem 2 when a node only pauses.
const elInit = { perm: { leader: "B (9)" }, temp: { "my number": "5", status: "normal" } };
const elBullyProse = [
  "Node A, number 5, has B, number 9, as its leader. C is number 3.",
  "A hears nothing from B in the time allowed. It starts an election by asking every node with a higher number, here only B, whether it is up.",
  "No answer within T. By the rule's assumption, that means B has stopped, so the leadership is A's. A first tells every lower node to halt, here only C.",
  "C has halted. A tells it that A is elected, and takes over as leader.",
];
const elBullyRows = (lost, o3) => [
  { temp: { status: "election" }, recv: T("no word from the leader"), sent: [lost ? ["B", "are you up?", "lost"] : ["B", "are you up?"]] },
  { recv: T("no answer within T"), sent: [["C", "halt"]] },
  { perm: { leader: "A (5)" }, temp: { status: "normal" }, recv: [["C", "halted"]], sent: [["C", "I am elected"]], out: o3 },
];
SCENES.election = [
  { id: "ring", name: "Around a ring", who: "A", peers: "B, C",
    note: "The nodes form a ring and pass messages one way only: A to B, B to C, C to A. Rule: send your own number on. Pass on a larger number, drop a smaller one. If your own number comes back, you are the highest.",
    init: { perm: { leader: "none" }, temp: { "my number": "5", "taken part": "no" } },
    prose: [
      "Node A, number 5, has no leader. B is number 9 and C number 3, but A does not know that, or even how many nodes there are.",
      "A notices there is no leader and starts an election, sending its own number to B.",
      "Two messages come from C. Its own number, 3, is smaller than 5, so A drops it. The number 9 is larger, so A passes it on.",
      "Word comes round that 9 has been elected: its own number came back to B. A takes B as its leader and passes the word on.",
    ],
    rows: [
      { temp: { "taken part": "yes" }, recv: T("no leader"), sent: [["B", "elect(5)"]] },
      { recv: [["C", "elect(3)"], ["C", "elect(9)"]], sent: [["B", "elect(9)"]], out: "9 is passed by everyone, and every smaller number is dropped by someone larger" },
      { perm: { leader: "B (9)" }, temp: { "taken part": "no" }, recv: [["C", "elected(9)"]], sent: [["B", "elected(9)"]], out: "only the highest number gets all the way round, so only one node can find itself elected" },
    ] },
  { id: "bully", name: "The highest one left", who: "A", peers: "B, C",
    note: "Rule: any message to a running node arrives within a time T, and a node never pauses. A node that misses its leader asks every higher node; if none answers within T, it halts the lower ones and takes over.",
    outside: "B has stopped for good.", init: elInit, prose: elBullyProse,
    rows: elBullyRows(true, "C now has A as its leader. Every node has the same leader, the highest one still running") },
  { id: "pause", name: "The leader only paused", who: "A", peers: "B, C", twin: "bully",
    note: "Same rule, but its assumption fails: B is not stopped, only paused for longer than T.",
    outside: "B has paused, and will carry on later as if nothing had happened.", init: elInit, prose: elBullyProse,
    rows: elBullyRows(false, "B wakes up still the leader, by its own account, and sends C its orders. Two nodes now act as leader. Without a time limit that never fails, no election rule can prevent this") },
];

PAPERS.push({
  id: "election", name: "Choosing a leader", year: "1979 / 1982",
  cite: "Chang & Roberts 1979 · An Improved Algorithm for Decentralized Extrema-Finding in Circular Configurations of Processes\nGarcia-Molina 1982 · Elections in a Distributed Computing System",
  idea: "Nodes with distinct numbers choose the highest as their leader. On a ring, each passes on only numbers larger than its own, so only the highest gets all the way round. With direct messages, a node asks every higher one whether it is up and takes over if none answers in time. That works only if silence for a set time really means stopped. If a node can merely pause, no rule can rule out two leaders.",
  names: "leader = coordinator · number = identification number, used as a priority · elect(n) = a message carrying a process's number, passed to the left · taken part = the process has marked itself · are you up? = node i contacting every node with a higher priority · halt, I am elected = the paper's own messages · status normal, election = S(i).s · a set time T = Assumption 8 · never pauses = Assumption 9 · two leaders = Theorem 2",
  frame: {
    goal: "Every node that is running ends up with the same leader, and it is the running node with the highest number.",
    shared: "Each node knows its own number. On the ring, a node knows only its neighbour and not how many nodes there are; with direct messages, it knows every node's number.",
    assumes: "On the ring, messages arrive and nodes keep running during the election. The second rule allows nodes to stop and restart, but assumes that a message to a running node arrives within a set time and that no node ever pauses. Garcia-Molina proves that without those two assumptions no election rule can keep two nodes from both acting as leader. Nobody lies." },
  scenes: SCENES.election });

// Taking turns: Ricart & Agrawala. Ask everyone; a node that is asking with priority holds its reply until it is done.
const mxInit = { temp: { requesting: "no", "highest seen": "0", "replies due": "0", deferred: "none", using: "no" } };
const mxNote = "Rule: to use the resource, ask every other node, numbering the request one past the highest number seen, and wait for every reply. Reply at once unless you are asking too and your request comes first: lower number first, and on a tie, the earlier name. Then hold the reply until you are done.";
const mxAsk = (n, s) => ({ temp: { requesting: `yes, as (${n}, A)`, "highest seen": `${n}`, "replies due": "2" }, recv: O("use the resource"), sent: [["B", `request(${n}, A)`], ["C", `request(${n}, A)`]], ...s });
SCENES.mutex = [
  { id: "tie", name: "Asking at the same time", who: "A", peers: "B, C", note: mxNote, init: mxInit,
    prose: [
      "Node A has not asked for the resource, and has seen no request.",
      "A needs the resource. The highest number it has seen is 0, so it asks B and C with request 1.",
      "B's request arrives, also numbered 1. It's a tie, and A's name comes first, so A's request goes first. A holds its reply to B.",
      "B replies: it sees the same tie, settled the same way.",
      "C replies too. Every other node has replied, so A uses the resource.",
      "A is done. It sends B the reply it was holding.",
    ],
    rows: [mxAsk(1),
      { temp: { deferred: "B" }, recv: [["B", "request(1, B)"]] },
      { temp: { "replies due": "1" }, recv: [["B", "reply"]] },
      { temp: { "replies due": "0", using: "yes" }, recv: [["C", "reply"]] },
      { temp: { requesting: "no", using: "no", deferred: "none" }, recv: O("done with the resource"), sent: [["B", "reply"]], out: "B now has both replies and uses the resource, never at the same time as A" },
    ] },
  { id: "later", name: "Asking second", who: "A", peers: "B, C", note: mxNote, init: mxInit,
    prose: [
      "Node A has not asked for the resource, and has seen no request.",
      "B's request arrives, numbered 1. A isn't asking, so it replies at once, and notes the number.",
      "Now A needs the resource. The highest number it has seen is 1, so it asks with request 2.",
      "C replies. B does not, yet.",
      "B's reply comes. Every other node has replied, so A uses the resource.",
      "A is done, and has no replies to send.",
    ],
    rows: [
      { temp: { "highest seen": "1" }, recv: [["B", "request(1, B)"]], sent: [["B", "reply"]] },
      mxAsk(2, { recv: O("use the resource") }),
      { temp: { "replies due": "1" }, recv: [["C", "reply"]] },
      { temp: { "replies due": "0", using: "yes" }, recv: [["B", "reply"]], out: "B was using the resource and held its reply until it was done. B asked first, so B went first, though A's name comes earlier" },
      { temp: { requesting: "no", using: "no" }, recv: O("done with the resource") },
    ] },
  { id: "nodefer", name: "If nobody held a reply", who: "A", peers: "B, C",
    note: "A different rule: reply to every request at once, and use the resource once everyone has replied.", init: mxInit,
    prose: [
      "Node A has not asked for the resource, and has seen no request.",
      "A needs the resource. The highest number it has seen is 0, so it asks B and C with request 1.",
      "B's request arrives, also numbered 1. By this rule A replies at once.",
      "B replies.",
      "C replies too. Every other node has replied, so A uses the resource.",
    ],
    rows: [mxAsk(1),
      { recv: [["B", "request(1, B)"]], sent: [["B", "reply"]] },
      { temp: { "replies due": "1" }, recv: [["B", "reply"]] },
      { temp: { "replies due": "0", using: "yes" }, recv: [["C", "reply"]], out: "B has A's reply and C's as well, and is using the resource at this very moment" },
    ] },
];

PAPERS.push({
  id: "mutex", name: "Taking turns", year: "1981",
  cite: "Ricart & Agrawala 1981 · An Optimal Algorithm for Mutual Exclusion in Computer Networks\nRelated: Lamport 1978 · Time, Clocks, and the Ordering of Events, whose rule needs a third message",
  idea: "One resource, and no node in charge of it. To use it, a node asks every other node and waits until all have replied. Requests carry a number one past the highest seen, so an earlier request carries a smaller number. A node asking at the same time replies at once if the other request comes first, and holds its reply until it is done if its own does. Two requests are never both first, so two nodes never hold the resource together.",
  names: "the resource = the critical section · request(n, A) = REQUEST(Our_Sequence_Number, me) · reply = REPLY · highest seen = Highest_Sequence_Number · replies due = Outstanding_Reply_Count · holding a reply = Reply_Deferred[j] · requesting = Requesting_Critical_Section",
  frame: {
    goal: "At most one node uses the resource at a time, every node that asks eventually gets it, and no node waits for ever.",
    shared: "Nothing. Up front, each node knows the others and its own unique name.",
    assumes: "Every message arrives, in any order and after any delay. No clocks. Nodes don't fail; the paper discusses how a failed node rejoins. Each use takes 2(N − 1) messages: the paper shows no rule in which every node acts alike and handles requests concurrently can use fewer." },
  scenes: SCENES.mutex });

// A register from majorities: Attiya, Bar-Noy & Dolev. A read takes the highest label a majority reports, and announces it before answering.
const abdNote = "Writes go to B, which labels each value one higher and sends it to everyone. To read, ask every node for its latest labelled value, take the highest among a majority's answers, your own included, then announce it and wait until a majority have it before answering.";
const abdInit = { temp: { latest: "1: x" } };
const abdAsk = { temp: { answers: "A: 1 x" }, recv: O("read the value"), sent: [["B", "latest?"], ["C", "latest?", "lost"]] };
SCENES.abd = [
  { id: "announce", name: "Announce, then answer", who: "A", role: "reader", peers: "B, the writer; C", note: abdNote,
    outside: "B has just begun writing y, with label 2. Its messages to A and C are lost on the way, so it will send them again.", init: abdInit,
    prose: [
      "Node A holds x, with label 1.",
      "A client asks A for the value. A asks B and C for their latest, counting its own answer.",
      "B answers y, with label 2. With A's own, that is a majority, and the highest label is 2. A takes y, and before answering, announces it.",
      "B says it has y. A and B are a majority holding y, so A answers y.",
      "C, now reading, asks A for its latest. A answers y.",
    ],
    rows: [abdAsk,
      { temp: { latest: "2: y", answers: "A: 1 x; B: 2 y" }, recv: [["B", "latest(2, y)"]], sent: [["B", "announce(2, y)"], ["C", "announce(2, y)", "lost"]] },
      { recv: [["B", "have it"]], sent: [["outside", "answer(y)"]], out: "y was given out only once a majority held it" },
      { recv: [["C", "latest?"]], sent: [["C", "latest(2, y)"]], out: "every majority C can ask includes A or B, so C finds y too. Once y was given out, nobody gets x again" },
    ] },
  { id: "noannounce", name: "Answer at once", who: "A", role: "reader", peers: "B, the writer; C",
    note: "A different rule: to read, take the highest among a majority's answers, and answer at once.",
    outside: "B has just begun writing y, with label 2. Its messages to A and C are lost on the way, so it will send them again.", init: abdInit,
    prose: [
      "Node A holds x, with label 1.",
      "A client asks A for the value. A asks B and C for their latest, counting its own answer.",
      "B answers y, with label 2. With A's own, that is a majority, and the highest label is 2. A answers y at once.",
      "C, now reading, asks A for its latest. A still holds x, and answers that.",
    ],
    rows: [abdAsk,
      { temp: { answers: "A: 1 x; B: 2 y" }, recv: [["B", "latest(2, y)"]], sent: [["outside", "answer(y)"]] },
      { recv: [["C", "latest?"]], sent: [["C", "latest(1, x)"]], out: "C hears x from A and from itself, a majority, and answers x. The read that began after y was given out returns x: new, then old" },
    ] },
];

PAPERS.push({
  id: "abd", name: "A register from majorities", year: "1990 / 1995",
  cite: "Attiya, Bar-Noy & Dolev 1990 · Sharing Memory Robustly in Message-Passing Systems (MIT TM-423; JACM 1995)",
  idea: "Keep a copy of one value at every node and make it behave as one copy, though messages are lost and up to half the nodes may stop. A write labels its value one higher and waits until a majority have it. A read asks everyone, takes the highest label among a majority's answers, and before answering makes sure a majority have that value too. Any two majorities share a node, so a read that starts after another has finished always finds a label at least as high.",
  names: "labelled value = the writer's value with its label, an integer in the unbounded version · B, the writer = the single writer of a single-writer multi-reader register · latest? = the first read message, latest(n, v) its acknowledgement · announce = the second read message (R, val) · noted = its acknowledgement, ACK-R · waiting for a majority = the communicate procedure · behaves as one copy = atomic, i.e. linearizable",
  frame: {
    goal: "Reads and writes of one value, at any node, behave as if there were a single copy, and every operation at a node that keeps running finishes.",
    shared: "One value, a copy at every node. Only B writes it; any node may read.",
    assumes: "Messages can be lost, delayed and reordered; what keeps being sent eventually reaches a majority. Fewer than half the nodes stop. No clocks: nobody ever waits for any particular node. The paper also removes the unbounded labels. Nobody lies." },
  scenes: SCENES.abd });

// Leases: Gray & Cheriton (wait for approval or for the lease to run out; clocks must behave), and Chubby's sequencers.
const lsNote = "Rule: A keeps the value and lends B a copy under a lease: until 12:10 B may answer reads from its copy without asking. A write must wait until every leaseholder approves, or until its lease has run out.";
const lsInit = { perm: { value: "x" }, temp: { leases: "B until 12:10" } };
const lsProse = [
  "Node A keeps the value, x. B holds a copy under a lease that runs until 12:10.",
  "C asks A to write y. B's lease is still running, so A asks B to approve.",
  "No approval comes, and at 12:10 by A's clock B's lease is over. A writes y and tells C.",
];
const lsRows = o2 => [
  { temp: { waiting: "y, for B" }, recv: [["C", "write y"]], sent: [["B", "may I write?", "lost"]] },
  { perm: { value: "y" }, temp: { leases: "none", waiting: "none" }, recv: T("12:10: B's lease is over"), sent: [["C", "written"]], out: o2 },
];
const sqInit = { perm: { value: "x" }, temp: { "highest lock seen": "1" } };
SCENES.leases = [
  { id: "expire", name: "Wait out the lease", who: "A", role: "server", peers: "B, holding a lease; C", note: lsNote,
    outside: "B is cut off: messages to it are lost.", init: lsInit, prose: lsProse,
    rows: lsRows("B's lease ran out at 12:10 by its own clock too, and it stopped answering from its copy. Nobody read x after y was written. Had B answered, A could have written at once") },
  { id: "fastclock", name: "A clock that runs fast", who: "A", role: "server", peers: "B, holding a lease; C", twin: "expire", note: lsNote,
    outside: "B is cut off. A's clock runs fast: when it shows 12:10, it is really 12:06.", init: lsInit, prose: lsProse,
    rows: lsRows("B's clock is right, and its lease has four minutes left. B answers a client x from its copy, after y was written. A lease is only as good as the clocks") },
  { id: "late", name: "A write that arrives late", who: "A", role: "server", peers: "lock service K; clients B, C",
    note: "Rule: a client writes only while it holds the lock, which K grants for a limited time. A applies every write that reaches it.",
    outside: "B held the lock and sent a write, then paused. The lock ran out, and K gave it to C.", init: { perm: { value: "x" } },
    prose: ["Node A keeps the value, x.", "C, holding the lock, writes z. A applies it.", "B's write of y arrives. A applies it."],
    rows: [
      { perm: { value: "z" }, recv: [["C", "write(z)"]] },
      { perm: { value: "y" }, recv: [["B", "write(y)"]], out: "B sent this while it held the lock, but it arrived after the lock had passed to C. It overwrote C's write with nobody holding the lock" },
    ] },
  { id: "sequencer", name: "Numbered locks", who: "A", role: "server", peers: "lock service K; clients B, C",
    note: "Rule: each time K grants the lock it numbers it one higher, and a write carries its lock's number. A refuses a write whose number is lower than the highest it has seen.",
    outside: "B held lock 1 and sent a write, then paused. The lock ran out, and K gave lock 2 to C.", init: sqInit,
    prose: ["Node A keeps the value, x. The highest lock number it has seen is 1.", "C writes z under lock 2. A applies it and notes the number.", "B's write of y arrives, under lock 1. That is lower than 2, so A refuses it."],
    rows: [
      { perm: { value: "z" }, temp: { "highest lock seen": "2" }, recv: [["C", "write(z, lock 2)"]] },
      { temp: { refused: "y, lock 1" }, recv: [["B", "write(y, lock 1)"]], sent: [["B", "refused: lock 1 is over"]], out: "the late write can't undo C's. B learns its lock is gone" },
    ] },
];

PAPERS.push({
  id: "leases", name: "Leases", year: "1989 / 2006",
  cite: "Gray & Cheriton 1989 · Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency\nBurrows 2006 · The Chubby Lock Service for Loosely-Coupled Distributed Systems (locks and sequencers)",
  idea: "A promise that runs out on its own. A node holding a lease may use its copy without asking until the lease ends; a write must wait until every leaseholder approves or its lease has run out. So a node that is cut off or stopped delays a write only until its lease ends, and silence never needs to be explained. The price is clocks: a lease is safe only if clocks drift by a known amount. And a request sent under a lease can arrive after it ends, so numbered leases let the receiver refuse it.",
  names: "lease = a lease, with a term · may I write? = a request for approval · waiting for approval or expiry = the server defers the write · a clock that runs fast = a server clock that advances too quickly · lock = a Chubby lock, held under a lease · lock number = the sequencer, with its lock generation number · refused = the server rejects a request whose sequencer is no longer valid",
  frame: {
    goal: "Every read, from the value or from a copy, sees the latest write, though messages are lost and nodes stop.",
    shared: "The value, kept at one node, and copies lent out under leases with a fixed end.",
    assumes: "Messages can be lost, and nodes can stop and restart; a restarted server waits out the longest lease it might have granted. Clocks drift from one another by no more than a known amount: Gray and Cheriton call a clock that fails this a Byzantine failure, outside what leases protect against. Nobody lies." },
  scenes: SCENES.leases });

// Longest chain: Nakamoto. Blocks take luck to make; everyone works on the longest chain, and a write is safe to act on only once it is deep.
const nkNote = "Rule: making a block takes long, random work. Build on the longest chain you know. If two are equally long, keep building on the one you heard of first, but keep the other: if it grows longer, switch to it.";
const nkPayInit = { perm: { "acted on x": "no" }, temp: { chain: "1", x: "not in a block yet" } };
SCENES.nakamoto = [
  { id: "fork", name: "Two blocks at once", who: "A", peers: "B, C", note: nkNote,
    init: { temp: { chain: "1", "also kept": "none" } },
    prose: [
      "Node A's chain is one block long.",
      "A's work pays off: it makes block 2a on top of 1, and sends it to B and C.",
      "Block 2b arrives from B, also on top of 1. The two chains are the same length. A heard of its own first, so it keeps building on 2a, and keeps 2b.",
      "Block 3 arrives from C, built on 2b. That chain is now the longest, so A switches to it. 2a drops out of A's chain.",
    ],
    rows: [
      { temp: { chain: "1 2a" }, recv: [["coin", "made block 2a"]], sent: [["B", "block(2a on 1)"], ["C", "block(2a on 1)"]] },
      { temp: { "also kept": "1 2b" }, recv: [["B", "block(2b on 1)"]] },
      { temp: { chain: "1 2b 3", "also kept": "1 2a" }, recv: [["C", "block(3 on 2b)"]], out: "B switches too. Every node builds on 2b now. Anything that was only in 2a goes back to waiting for a block" },
    ] },
  { id: "shallow", name: "Acted on one block deep", who: "A", peers: "B; M, who writes x",
    note: "Rule: act on x, in a way that can't be undone, once x is in a block on your longest chain.",
    outside: "M writes x, and meanwhile works in secret on a chain in which x was never written. M is lucky.", init: nkPayInit,
    prose: [
      "Node A's chain is one block long. M is about to write x, and A will act on it once x is in a block.",
      "Block 2 arrives from B, with x in it. A acts on x.",
      "Two blocks arrive from M, 2′ and 3′, on top of 1. That chain is longer, so A switches to it. x is not in it.",
    ],
    rows: [
      { perm: { "acted on x": "yes" }, temp: { chain: "1 2", x: "in block 2" }, recv: [["B", "block(2 on 1, holds x)"]] },
      { temp: { chain: "1 2′ 3′", x: "gone" }, recv: [["M", "blocks(2′ 3′ on 1)"]], out: "A has acted on x, and now no chain holds x. Every honest node switched to the longer chain, as the rule says" },
    ] },
  { id: "deep", name: "Acted on three blocks deep", who: "A", peers: "B; M, who writes x",
    note: "Rule: act on x, in a way that can't be undone, once x has two more blocks on top of it, three deep in all.",
    outside: "M writes x, and meanwhile works in secret on a chain in which x was never written. The honest nodes make blocks faster than M.", init: nkPayInit,
    prose: [
      "Node A's chain is one block long. M is about to write x, and A will act on it once x is three blocks deep.",
      "Block 2 arrives from B, with x in it. One deep: A waits.",
      "Block 3 arrives on top of it. Two deep.",
      "Two blocks arrive from M, 2′ and 3′, on top of 1. That chain is no longer than A's, so A stays where it is.",
      "Block 4 arrives. x is three deep, and A acts on it.",
    ],
    rows: [
      { temp: { chain: "1 2", x: "in block 2, 1 deep" }, recv: [["B", "block(2 on 1, holds x)"]] },
      { temp: { chain: "1 2 3", x: "2 deep" }, recv: [["B", "block(3 on 2)"]] },
      { temp: { "also kept": "1 2′ 3′" }, recv: [["M", "blocks(2′ 3′ on 1)"]] },
      { perm: { "acted on x": "yes" }, temp: { chain: "1 2 3 4", x: "3 deep" }, recv: [["B", "block(4 on 3)"]],
        out: "M's chain is a block behind and would have to outgrow the honest one. While the honest nodes are faster, the chance of that shrinks with every block it falls behind" },
    ] },
];

PAPERS.push({
  id: "nakamoto", name: "Longest chain", year: "2008",
  cite: "Nakamoto 2008 · Bitcoin: A Peer-to-Peer Electronic Cash System",
  idea: "Agreement among nodes that anyone may join, so nobody can count votes. Instead, adding a block to the shared chain takes long, random work, and everyone builds on the longest chain they know. Two blocks made at once make a fork, and the next block settles it. A liar can rewrite history only by out-working everyone else, and if the honest nodes work faster, its chance of catching up falls with every block it is behind. So agreement is never certain, only ever likelier.",
  names: "block = a block of transactions · making a block = finding a proof-of-work · longest chain = the chain with the most proof-of-work · keeping the other branch = saving it in case it becomes longer · M = the attacker · x = a transaction, M's payment to A · acting on x = handing over what was paid for · three deep = waiting until z blocks have been linked after the transaction · faster = p > q, honest nodes have more CPU power than the attacker",
  frame: {
    goal: "Every honest node agrees on one order of the blocks, and a block deep in the chain is unlikely ever to be replaced.",
    shared: "The chain, a copy at every node, and the rule. Nobody needs to know how many nodes there are or who they are.",
    assumes: "Messages are broadcast, and some may be lost; a node that misses a block asks for it when the next arrives. Nodes come and go. Some may lie, as long as the honest ones together can make blocks faster. No clocks, but the time a block takes is random." },
  scenes: SCENES.nakamoto });

// Consistent hashing: Karger et al., in Chord's form (a key belongs to the first node at or after it on a circle); Dynamo's hinted handoff.
SCENES.chash = [
  { id: "join", name: "A node joins the circle", who: "C", peers: "A, B; D, joining",
    note: "Keys and nodes have places on a circle numbered 0 to 99: A at 20, B at 50, C at 80. A key belongs to the first node at or after its place, going round. So C holds the keys from 51 to 80.",
    init: { temp: { place: "80", keys: "58, 72" } },
    prose: [
      "Node C, at 80 on the circle, holds keys 58 and 72.",
      "D joins at 65. Keys from 51 to 65 are now D's, so C hands over 58 and keeps 72.",
      "A client asks C for key 58. C tells it to ask D.",
    ],
    rows: [
      { temp: { keys: "72" }, recv: [["D", "joining at 65"]], sent: [["D", "keys(58)"]], out: "A and B are not touched: no key moves between the nodes that were there before" },
      { recv: O("read key 58"), sent: [["outside", "ask D"]] },
    ] },
  { id: "modulo", name: "If keys were dealt by count", who: "C", peers: "A, B; D, joining",
    note: "A different rule: number the nodes 0, 1, 2 and give a key to the node numbered by the remainder when the key is divided by the count of nodes. C is node 2 of three.",
    init: { temp: { "my number": "2 of 3", keys: "17, 41, 59" } },
    prose: [
      "Node C, number 2 of three, holds keys 17, 41 and 59: each leaves remainder 2 when divided by 3.",
      "D joins as number 3. Now keys are divided by 4: 17 and 41 leave 1, and go to B; 59 leaves 3, and goes to D. C keeps none of its keys.",
      "Keys 90 and 58 arrive from A and B: divided by 4, each leaves 2, so now they are C's.",
    ],
    rows: [
      { temp: { "my number": "2 of 4", keys: "none" }, recv: [["D", "joining as number 3"]], sent: [["B", "keys(17, 41)"], ["D", "keys(59)"]] },
      { temp: { keys: "90, 58" }, recv: [["A", "keys(90)"], ["B", "keys(58)"]],
        out: "every node reshuffled the same way. Six of the eight keys changed hands, where one new node needed only about a quarter of them" },
    ] },
  { id: "handoff", name: "Keeping a key for a node that is down", who: "C", peers: "A, B",
    note: "Each key is kept on the first two healthy nodes at or after its place on the circle: A at 20, B at 50, C at 80. Key 13 belongs to A and B. A copy held for a node that is down carries a note saying whose it is.",
    outside: "A is down for a while.",
    init: { temp: { keys: "58, 72", "kept for others": "none" } },
    prose: [
      "Node C, at 80, holds keys 58 and 72, and nothing for anyone else.",
      "A write of key 13 comes from B. Its owner A is down, so C is the next healthy node: C keeps the copy, noting that it is A's, and confirms.",
      "C checks, and A is answering again. C sends it the copy.",
      "A has it. C drops its own copy.",
    ],
    rows: [
      { temp: { "kept for others": "13=y, for A" }, recv: [["B", "store(13=y, for A)"]], sent: [["B", "stored"]], out: "B already had its own copy, so the write was on two nodes and could be confirmed while A was down" },
      { recv: T("A answers again"), sent: [["A", "store(13=y)"]] },
      { temp: { "kept for others": "none" }, recv: [["A", "stored"]], out: "key 13 is back on A and B, its own two nodes, and was on two nodes all along" },
    ] },
];

PAPERS.push({
  id: "chash", name: "Keys on a circle", year: "1997 / 2001 / 2007",
  cite: "Karger, Lehman, Leighton, Panigrahy, Levine & Lewin 1997 · Consistent Hashing and Random Trees\nStoica, Morris, Karger, Kaashoek & Balakrishnan 2001 · Chord: A Scalable Peer-to-peer Lookup Service for Internet Applications\nDeCandia et al. 2007 · Dynamo: Amazon's Highly Available Key-value Store (sloppy quorum and hinted handoff)",
  idea: "Spread keys over nodes so that when a node joins or leaves, only the keys it takes or gives up move. Place keys and nodes on a circle; a key belongs to the first node at or after it. A new node takes keys only from its neighbour, and nobody else is touched. Dealing keys by a count of nodes moves nearly all of them instead. And when a key's node is down, the next one round can keep it for a while, and hand it back.",
  names: "the circle = the unit interval, hashed (Karger), the identifier circle modulo 2ᵐ (Chord) · a key's place = its hash · first node at or after it = successor(k) · moving only what must = monotonicity, smoothness · dealt by count = hashing modulo the number of buckets · first two healthy nodes = a sloppy quorum over the preference list, here with N = 2 · kept for A = a hinted replica · handing it back = hinted handoff",
  frame: {
    goal: "Every key has an owner everyone can work out, and when a node joins or leaves, as few keys as possible move.",
    shared: "The rule for placing keys and nodes on the circle, and who is currently on it.",
    assumes: "Each node knows the others' places; Chord shows how to find a key's owner when each knows only a few. Places are spread at random; the papers give each node several places to even out the load. Keys are moved over messages that arrive. Nobody lies." },
  scenes: SCENES.chash });

// Flexible Paxos: Howard, Malkhi & Spiegelman. Four voters; only a phase-1 group and a phase-2 group must overlap.
const fpOut = "In round 1, P got x accepted by A and B. Under these group sizes that is a phase-2 group, so x is chosen. Nobody has told Q.";
const fpInit = { perm: { "tried up to": "0" } };
SCENES.fpaxos = [
  { id: "overlap", name: "Three to claim, two to accept", who: "Q", role: "proposer", peers: "voters A, B, C, D",
    note: "Four voters. Phase 1 needs promises from any three; phase 2 needs any two to accept. Every three and every two share a voter, though two twos need not.",
    outside: fpOut, init: fpInit,
    phases: [[0, "Phase 1: three promises", "A group of three always meets any group of two that accepted."], [4, "Phase 2: two accept", "Two is enough, because every later phase 1 will meet them."]],
    prose: [
      "Q, a proposer, has tried no round yet.",
      "Asked to get y chosen, Q claims round 2 and asks B, C and D to promise. Any three will do.",
      "B promises, reporting that it accepted x in round 1.",
      "C promises, having accepted nothing.",
      "D promises, having accepted nothing. Three promises: phase 1 is done. B's report means x may have been chosen, so Q must propose x, not y. It asks C and D to accept.",
      "C and D accept. Two acceptances in round 2: x is chosen, again, and Q writes it down.",
    ],
    rows: [
      { perm: { "tried up to": "2" }, temp: { wants: "y" }, recv: O("get y chosen"), sent: [["B", "claim(r2)"], ["C", "claim(r2)"], ["D", "claim(r2)"]] },
      { temp: { "last votes": "B=r1 x" }, recv: [["B", "promise(r2, accepted (r1, x))"]] },
      { temp: { "last votes": "B=r1 x; C=none" }, recv: [["C", "promise(r2, accepted none)"]] },
      { temp: { "last votes": "B=r1 x; C=none; D=none", proposing: "x" }, recv: [["D", "promise(r2, accepted none)"]], sent: [["C", "propose(r2, x)"], ["D", "propose(r2, x)"]] },
      { perm: { chosen: "x" }, temp: { "accepted by": "C D" }, recv: [["C", "accepted(r2)"], ["D", "accepted(r2)"]],
        out: "C and D share no voter with A and B. That is safe: what has to overlap is each round's three with every earlier round's two" },
    ] },
  { id: "disjoint", name: "Two to claim, two to accept", who: "Q", role: "proposer", peers: "voters A, B, C, D",
    note: "A different setting: any two promises for phase 1, any two acceptances for phase 2. Two twos can miss each other.",
    outside: fpOut, init: fpInit,
    phases: [[0, "Phase 1: two promises", "Two can miss the two that accepted."], [2, "Phase 2: two accept", ""]],
    prose: [
      "Q, a proposer, has tried no round yet.",
      "Asked to get y chosen, Q claims round 2 and asks C and D to promise. Any two will do.",
      "C and D promise, neither having accepted anything. Phase 1 is done and nobody has reported a vote, so Q proposes its own y.",
      "C and D accept. Two acceptances in round 2: Q takes y as chosen.",
    ],
    rows: [
      { perm: { "tried up to": "2" }, temp: { wants: "y" }, recv: O("get y chosen"), sent: [["C", "claim(r2)"], ["D", "claim(r2)"]] },
      { temp: { "last votes": "C=none; D=none", proposing: "y" }, recv: [["C", "promise(r2, accepted none)"], ["D", "promise(r2, accepted none)"]], sent: [["C", "propose(r2, y)"], ["D", "propose(r2, y)"]] },
      { perm: { chosen: "y" }, temp: { "accepted by": "C D" }, recv: [["C", "accepted(r2)"], ["D", "accepted(r2)"]], out: "x was chosen in round 1 by A and B, whom Q's phase 1 never asked. Two values are chosen" },
    ] },
];

PAPERS.splice(PAPERS.findIndex(p => p.id === "paxos") + 1, 0, {
  id: "fpaxos", name: "Flexible Paxos", year: "2016",
  cite: "Howard, Malkhi & Spiegelman 2016 · Flexible Paxos: Quorum Intersection Revisited",
  idea: "Paxos waits for a majority in both of its phases, but a majority is more than it needs. What keeps a chosen value safe is that a later round's phase 1 hears from someone who accepted it in phase 2. So only those two groups must overlap: a phase-1 group and a phase-2 group. Two phase-2 groups may miss each other entirely. With four nodes, phase 2 can wait for two instead of three, if phase 1 waits for three.",
  names: "group = quorum · three to claim = a phase-1 quorum, Q1 · two to accept = a phase-2 quorum, Q2 · must overlap = Q1 and Q2 intersect, |Q1| + |Q2| > N · claim, promise, propose, accepted = prepare, promise, propose, accept · last votes = the values reported in phase-1 promises",
  frame: {
    goal: "Choose exactly one value, and never change it once chosen, as in Paxos, but with smaller groups in phase 2.",
    shared: "As in Paxos, the chosen value is whatever a phase-2 group accepted in one round. Up front, everyone knows the voters and the sizes of the two kinds of group.",
    assumes: "As in Paxos: nodes run at any speed and may stop, and a replacement starts from permanent state; messages can be delayed, repeated or lost, but not altered. Nobody lies. The price of small phase-2 groups is paid in phase 1, which must wait for more nodes." },
  scenes: SCENES.fpaxos });

// Chain replication: van Renesse & Schneider. Updates enter at the head and pass down; only the tail answers.
const crNote = "The nodes form a chain: A, the head, then B, then C, the tail. Updates enter at the head and pass down the chain in order. Reads go to the tail, and only the tail answers anyone.";
SCENES.chain = [
  { id: "tail", name: "Only the tail answers", who: "C", role: "tail", peers: "A, the head; B", note: crNote,
    outside: "A client has asked A, the head, to write y.", init: { perm: { value: "x" } },
    prose: [
      "Node C, the tail, holds x.",
      "The update to y comes down the chain from B. C applies it, tells the client the write is done, and acknowledges it back up the chain.",
      "A client asks C for the value. C answers y.",
    ],
    rows: [
      { perm: { value: "y" }, recv: [["B", "update(1: y)"]], sent: [["outside", "done(y)"], ["B", "ack(1)"]], out: "A and B applied y before C, but answered nobody. Since only the tail answers, nobody hears of y until every node has it" },
      { recv: O("read the value"), sent: [["outside", "answer(y)"]], out: "anything the tail gives out is already at every node, so a node failing can't take it back" },
    ] },
  { id: "anynode", name: "If any node answered", who: "A", role: "head", peers: "B; C, the tail",
    note: "A different rule: updates still enter at the head and pass down, but any node answers reads from its own copy.", init: { perm: { value: "x" }, temp: { "sent, not yet acked": "none" } },
    prose: [
      "Node A, the head, holds x.",
      "A client asks A to write y. A applies it and passes it down to B.",
      "A client asks A for the value. A answers y.",
    ],
    rows: [
      { perm: { value: "y" }, temp: { "sent, not yet acked": "1: y" }, recv: O("write y"), sent: [["B", "update(1: y)"]] },
      { recv: O("read the value"), sent: [["outside", "answer(y)"]], out: "a moment later another client asks C, which hasn't got the update yet, and is told x. New, then old" },
    ] },
  { id: "middle", name: "A node in the middle fails", who: "A", role: "head", peers: "B; C, the tail; M, which keeps the chain's list",
    note: "Each node keeps a list of the updates it has passed on that the tail hasn't yet acknowledged. When the node after it changes, it first resends that list.",
    outside: "A passed update 2, z, to B. B's node stopped before passing it on.", init: { perm: { value: "z" }, temp: { next: "B", "sent, not yet acked": "2: z" } },
    prose: [
      "Node A, the head, has applied z and passed it to B. The tail hasn't acknowledged it yet.",
      "M says B is gone and the node after A is now C. Before anything else, A resends everything on its list to C.",
      "C acknowledges update 2. A strikes it from the list.",
    ],
    rows: [
      { temp: { next: "C" }, recv: [["M", "your next node is now C"]], sent: [["C", "update(2: z)"]] },
      { temp: { "sent, not yet acked": "none" }, recv: [["C", "ack(2)"]], out: "C applied z and told the client it was done. Nothing B held was lost, because A kept everything the tail hadn't yet confirmed" },
    ] },
];

PAPERS.push({
  id: "chain", name: "Chain replication", year: "2004",
  cite: "van Renesse & Schneider 2004 · Chain Replication for Supporting High Throughput and Availability",
  idea: "Arrange the copies in a chain. Updates enter at the head and pass down the chain in order; reads are answered by the tail, and only the tail answers anyone. So a value is given out only once every copy has it, and the copies behave as one. When a node fails, the chain closes up around it, and the node before it resends whatever it passed on that the tail never confirmed.",
  names: "the chain = servers linked by reliable FIFO links · head, tail = the paper's own names · update(n: v) = an update request, forwarded as state changes · ack(n) = ack(r), sent back up from the tail · sent, not yet acked = Sentᵢ · M = the master, a separate service · behaving as one = strong consistency",
  frame: {
    goal: "Reads and writes behave as if there were one copy, while copies fail and the chain closes up around them.",
    shared: "The value, a copy at every node in the chain. M keeps the list of who is in the chain, and tells nodes when it changes.",
    assumes: "Links between neighbours deliver in order and don't lose messages. Nodes stop and don't lie, and a stopped node is noticed; M is itself kept by a consensus service. Fewer than all the nodes stop at once." },
  scenes: SCENES.chain });

// True time: Spanner. A clock that gives an interval; stamp with its latest end, and wait until that stamp is surely past before answering.
const ttNote = "A keeps a, and B keeps b. Every write is stamped with a time, and a read “as of” a time sees the writes stamped no later. Each node's clock may be off by up to 5, and says so: it gives the earliest and latest the true time could be.";
SCENES.truetime = [
  { id: "wait", name: "Wait out the doubt", who: "A", peers: "B", note: ttNote + " Rule: stamp a write with the latest the time could be, and don't report it done until the earliest the time could be has passed the stamp.",
    outside: "At true time 20, A's clock reads 24.", init: { perm: { a: "x" } },
    prose: [
      "Node A holds a = x.",
      "A client asks A to write a = y. A's clock reads 24, so the true time is somewhere from 19 to 29. A stamps the write 29, the latest it could be, and waits.",
      "A's clock reads 35: the true time is at least 30, so 29 is surely past. A applies the write and reports it done.",
    ],
    rows: [
      { temp: { pending: "a=y @29", "true time": "19 to 29" }, recv: O("write a=y") },
      { perm: { a: "y @29" }, temp: { pending: "none", "true time": "30 to 40" }, recv: T("clock reads 35"), sent: [["outside", "done(a=y)"]],
        out: "the client, told it is done, then writes b = z at B. Whatever B's clock says, the true time there is now past 30, so B's stamp is at least 30: after y's. Effects are stamped after their causes" },
    ] },
  { id: "nowait", name: "Trust the clock", who: "A", peers: "B", note: ttNote + " A different rule: stamp a write with what your clock reads, and report it done at once.",
    outside: "At true time 20, A's clock reads 24, four ahead. B's clock is four behind.", init: { perm: { a: "x" } },
    prose: [
      "Node A holds a = x.",
      "A client asks A to write a = y. A's clock reads 24, so A stamps the write 24, applies it and reports it done.",
      "A reader asks for a as of 20. The write of y is stamped 24, later than 20, so A answers x.",
    ],
    rows: [
      { perm: { a: "y @24" }, recv: O("write a=y"), sent: [["outside", "done(a=y)"]] },
      { recv: O("read a as of 20"), sent: [["outside", "answer(a=x)"]],
        out: "the client, told y was done, then wrote b = z at B, whose clock read 17. That write is stamped 17. The same reader, as of 20, gets b = z and a = x: the effect without its cause" },
    ] },
];

PAPERS.push({
  id: "truetime", name: "True time", year: "2012",
  cite: "Corbett et al. 2012 · Spanner: Google's Globally-Distributed Database (TrueTime and commit wait)",
  idea: "Clocks can't agree exactly, but they can say how far off they might be. A clock that gives an interval, the earliest and the latest the true time could be, is enough to order writes by time. Stamp each write with the latest the time could be, then wait until the earliest has passed that stamp before telling anyone it is done. Anything that starts after the write is done gets a later stamp, wherever it runs, so a read as of any time sees causes before their effects.",
  names: "the clock's interval = TT.now(), returning [earliest, latest] · off by up to 5 = the error bound ε · stamp with the latest = the commit timestamp s ≥ TT.now().latest · wait until the earliest has passed it = commit wait, until TT.after(s) · read as of a time = a snapshot read at a timestamp · causes before effects = external consistency",
  frame: {
    goal: "If one write is done before another starts, the first gets the smaller stamp, so any read as of a time sees a state that really existed.",
    shared: "Each node's data. Up front, a clock at every node with a known bound on its error.",
    assumes: "Every clock's error really stays within its bound; Spanner keeps the bound small with GPS and atomic clocks, and the scenes leave that aside. The wait costs about twice the bound on every write. Messages and failures are handled by Paxos groups, also left aside here. Nobody lies." },
  scenes: SCENES.truetime });
