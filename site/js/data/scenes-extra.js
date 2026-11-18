// ---------- the results added to the first set ----------
// Viewstamped replication, a coin flip, atomic commit and linearizability. Each is written against its paper.
PSEUDO.add("coin");
const both = (text, lost) => [["B", text, lost], ["C", text, lost]].map(m => lost ? m : m.slice(0, 2));

SCENES.benor = [
  { id: "coin", name: "No majority, so flip", who: "A", peers: "B, C",
    note: "The rule, for three nodes of which one may stop: wait for two messages, your own included, and never for the third.",
    outside: "C's node has stopped for good. B starts with y.",
    init: { perm: { decided: "none" }, temp: { round: "1", value: "x" } },
    phases: [[0, "Round 1", "Report your value. Propose a value only if more than half the nodes reported it."], [4, "Round 2", "Both nodes enter with the same value, so it is proposed and then decided."]],
    prose: [
      "Node A starts round 1 with the value x and has decided nothing.",
      "In its first step nothing arrives, yet a step can still act: A reports x to B and C.",
      "B reports y. A now has two reports, x and y. Neither value is on more than half of the three nodes, so A proposes no value.",
      "B proposed no value either. With no value proposed, A flips a coin, and it comes up y. A takes y as its value and starts round 2 by reporting it.",
      "B reports y as well. Two of three is more than half, so A proposes y.",
      "B proposes y too. Two proposals are more than the one node that may have stopped, so A decides y. The decision is written once and never changed.",
    ],
    rows: [
      { temp: { reports: "A=x" }, recv: N, sent: both("report(r1, x)"), out: "C has stopped: it never takes this in" },
      { temp: { reports: "A=x; B=y", proposals: "A=?" }, recv: [["B", "report(r1, y)"]], sent: both("propose(r1, ?)") },
      { temp: { round: "2", value: "y", reports: "A=y", proposals: "none yet" }, recv: [["B", "propose(r1, ?)"], ["coin", "y"]], sent: both("report(r2, y)"),
        out: "B flipped too and also got y. Had the coins differed, round 2 would have gone like round 1, and both would flip again" },
      { temp: { reports: "A=y; B=y", proposals: "A=y" }, recv: [["B", "report(r2, y)"]], sent: both("propose(r2, y)") },
      { perm: { decided: "y" }, temp: { proposals: "A=y; B=y" }, recv: [["B", "propose(r2, y)"]], out: "B is in the same position and decides y too" },
    ] },
  { id: "spread", name: "One proposal is enough", who: "A", peers: "B, C",
    note: "Same rule.",
    outside: "All three nodes are running. B and C both start with y, and C's messages reach A before B's.",
    init: { perm: { decided: "none" }, temp: { round: "1", value: "x" } },
    phases: [[0, "Round 1", "Report your value. Propose a value only if more than half the nodes reported it."], [4, "Round 2", "Every node enters with the same value, so it is proposed and then decided."]],
    prose: [
      "Node A starts round 1 with the value x and has decided nothing.",
      "In its first step nothing arrives, yet a step can still act: A reports x to B and C.",
      "C reports y. A now has two reports, x and y. Neither value is on more than half of the three nodes, so A proposes no value.",
      "B's proposal arrives, and it names y. One proposal is enough to adopt: A takes y as its value, with no coin. One is not enough to decide, so A starts round 2.",
      "B reports y. With A's own report that makes two, so A proposes y.",
      "B proposes y as well. Two proposals: A decides y.",
    ],
    rows: [
      { temp: { reports: "A=x" }, recv: N, sent: both("report(r1, x)") },
      { temp: { reports: "A=x; C=y", proposals: "A=?" }, recv: [["C", "report(r1, y)"]], sent: both("propose(r1, ?)") },
      { temp: { round: "2", value: "y", reports: "A=y", proposals: "none yet" }, recv: [["B", "propose(r1, y)"]], sent: both("report(r2, y)"),
        out: "B and C each saw two reports of y and proposed it. C then saw both proposals and has already decided y. Whoever decides has seen two proposals, so every other node has seen at least one" },
      { temp: { reports: "A=y; B=y", proposals: "A=y" }, recv: [["B", "report(r2, y)"]], sent: both("propose(r2, y)") },
      { perm: { decided: "y" }, temp: { proposals: "A=y; B=y" }, recv: [["B", "propose(r2, y)"]], out: "all three have now decided y" },
    ] },
];

const commitNote = "Node A is one of two participants in a transfer of 5 units from A to B. K coordinates.";
const commit0 = "Node A holds 20 units. The transfer of 5 to B is worked out but not final, and A could still drop it.";
const commit1 = "K asks whether A can commit. A writes down enough to either finish the transfer or undo it, whatever happens next, and agrees. From here on A may not back out by itself.";
const commitAsk = { perm: { transfer: "agreed (can finish or undo)" }, recv: [["K", "request commit"]], sent: [["K", "agree"]] };
SCENES.commit = [
  { id: "agree", name: "Everyone agrees", who: "A", role: "participant", peers: "coordinator K; participant B", note: commitNote,
    init: { perm: { units: "20", transfer: "working" } },
    prose: [commit0, commit1, "K says commit. A finishes the transfer, which leaves it 15 units, and acknowledges."],
    rows: [commitAsk,
      { perm: { units: "15", transfer: "committed" }, recv: [["K", "commit"]], sent: [["K", "ack"]], out: "B agreed as well. K recorded the decision to commit before telling anyone" },
    ] },
  { id: "veto", name: "One participant refuses", who: "A", role: "participant", peers: "coordinator K; participant B", note: commitNote,
    init: { perm: { units: "20", transfer: "working" } },
    prose: [commit0, commit1, "K says abort. A undoes the transfer and acknowledges. Its own agreement made no difference."],
    rows: [commitAsk,
      { perm: { transfer: "undone" }, recv: [["K", "abort"]], sent: [["K", "ack"]], out: "B replied abort, and one refusal is enough" },
    ] },
  { id: "wait", name: "Agreed, then silence", who: "A", role: "participant", peers: "coordinator K; participant B", note: commitNote,
    outside: "K's node stops after collecting the replies. Whether it recorded a decision first, only its own log can say.",
    init: { perm: { units: "20", transfer: "working" } },
    prose: [commit0, commit1,
      "No verdict comes before the timer fires. A asks K for it.",
      "Still nothing, and A asks again. It cannot finish, because K may have decided abort. It cannot undo, because K may have decided commit and told B.",
    ],
    rows: [commitAsk,
      { recv: T("no verdict yet"), sent: [["K", "verdict?", "lost"]] },
      { recv: T("no verdict yet"), sent: [["K", "verdict?", "lost"]], out: "until K's node is back, A waits, holding 5 units it can neither send nor use" },
    ] },
  { id: "giveup", name: "If A gave up waiting", who: "A", role: "participant", peers: "coordinator K; participant B",
    note: "A different rule: after waiting through two timers with no verdict, undo.",
    outside: "K recorded commit and told B, then its node stopped before telling A.",
    init: { perm: { units: "20", transfer: "working" } },
    prose: [commit0, commit1,
      "No verdict comes before the timer fires. A asks K for it.",
      "Still nothing. By this rule A stops waiting and undoes the transfer.",
    ],
    rows: [commitAsk,
      { recv: T("no verdict yet"), sent: [["K", "verdict?", "lost"]] },
      { perm: { transfer: "undone" }, recv: T("no verdict yet"), out: "B was told commit and has added 5 units. A has kept its 5. Those 5 units now exist twice" },
    ] },
];

const vrLog2 = ["v1.1 a=1", "v1.2 b=2"];
SCENES.vr = [
  { id: "force", name: "Making an event safe", who: "B", role: "primary", peers: "backups A, C",
    note: "Event “v1.2 b=2” means view 1, event 2, the call b=2.",
    init: { perm: { view: "v1" }, temp: { status: "running, primary", events: ["v1.1 a=1"], "known to a majority": "v1.1" } },
    phases: [[0, "Making an event safe", "An event survives once a majority of nodes know it."], [4, "Signs of life", "Silence from the primary is what starts a change of view."]],
    prose: [
      "B is the primary of view 1. One event, a=1, is known to a majority.",
      "Asked from outside to run b=2, B does, numbers the event v1.2, and sends a record of it to A and C.",
      "A reports that it has the record. B and A are two of three, so a majority know the event and it will survive any change of view. B tells the client it is done.",
      "C has it too.",
      "B's timer fires. It tells A and C that it is still there.",
    ],
    rows: [
      { temp: { "events+": ["v1.2 b=2"] }, recv: O("run b=2"), sent: [["A", "record(v1.2, b=2)"], ["C", "record(v1.2, b=2)"]] },
      { temp: { "known to a majority": "v1.2" }, recv: [["A", "have(v1.2)"]], sent: [["outside", "done(b=2)"]] },
      { recv: [["C", "have(v1.2)"]] },
      { recv: T("time to show signs of life"), sent: [["A", "alive(v1)"], ["C", "alive(v1)"]] },
    ] },
  { id: "cutoff", name: "The primary is cut off", who: "B", role: "primary", peers: "backups A, C",
    note: "B is the primary of view 1.",
    outside: "B's messages are about to stop getting through. B will not be told.",
    init: { perm: { view: "v1" }, temp: { status: "running, primary", events: vrLog2, "known to a majority": "v1.2", "highest view seen": "v1" } },
    phases: [[0, "Unanswered", "Without replies, B can't tell lost from slow, and its new event is known only to itself."], [4, "A new view", "A higher view wins at once, and it starts from what a majority knew."]],
    prose: [
      "B is the primary of view 1, with two events known to a majority.",
      "Asked to run x=9, B does, numbers it v1.3, and sends the record to A and C.",
      "Nothing comes back. When its timer fires, B sends the record again.",
      "Still nothing, so B tries once more.",
      "An invitation to view 3 arrives from A. It is higher than any view B has seen, so B accepts, reporting the last event it knows and that it was a primary. It stops acting as one and waits.",
      "A, the primary of view 3, sends the state the new view starts from. It ends at v2.1 and has no x=9. B replaces what it held with this, and writes down that it is now in view 3.",
    ],
    rows: [
      { temp: { "events+": ["v1.3 x=9"] }, recv: O("run x=9"), sent: [["A", "record(v1.3, x=9)", "lost"], ["C", "record(v1.3, x=9)", "lost"]], out: "neither message arrives, and B can't tell" },
      { recv: T("time to resend"), sent: [["A", "record(v1.3, x=9)", "lost"], ["C", "record(v1.3, x=9)", "lost"]], out: "lost again" },
      { recv: T("time to resend"), sent: [["A", "record(v1.3, x=9)", "lost"], ["C", "record(v1.3, x=9)", "lost"]], out: "A and C have meanwhile formed view 2 without B, and run y=5 in it" },
      { temp: { status: "waiting for the view", "highest view seen": "v3", "known to a majority": null }, recv: [["A", "invite(v3)"]], sent: [["A", "accept(v3, last v1.3, was primary)"]], out: "messages get through again. A noticed, and starts view 3 to take B back in" },
      { perm: { view: "v3" }, temp: { status: "running, backup", events: ["v1.1 a=1", "v1.2 b=2", "v2.1 y=5"] }, recv: [["A", "newview(v3, primary A, events up to v2.1)"]], out: "x=9 never reached a majority, so it did not survive the change of view" },
    ] },
  { id: "form", name: "Forming a new view", who: "C", role: "backup", peers: "A, B",
    note: "B is the primary of view 1.",
    outside: "B's node has stopped. Just before, it ran c=3 and sent the record to A, but not yet to C.",
    init: { perm: { view: "v1" }, temp: { status: "running, backup", events: vrLog2, "highest view seen": "v1" } },
    phases: [[0, "Forming a view", "Whoever notices the silence invites the others to a higher view."], [3, "Choosing the primary", "The node with the latest event knows everything a majority knew."]],
    prose: [
      "C is a backup in view 1 and knows two events.",
      "C's timer fires with nothing heard from the primary. C sets out to form a new view. It picks a number higher than any it has seen, 2, and invites A and B.",
      "A accepts, reporting that its last event is v1.3. That is one more than C knows. C waits a while longer for B.",
      "B does not answer. A and C are a majority, so the view can be formed. A knows the most, so C names A the primary and tells it so.",
      "A sends the state view 2 starts from, which includes c=3. C takes it over and writes down that it is now in view 2.",
    ],
    rows: [
      { temp: { status: "forming a view", "highest view seen": "v2", replies: "C: last v1.2" }, recv: T("nothing from the primary"), sent: [["A", "invite(v2)"], ["B", "invite(v2)", "lost"]], out: "B has stopped: it never takes this in" },
      { temp: { replies: "C: last v1.2; A: last v1.3" }, recv: [["A", "accept(v2, last v1.3)"]] },
      { temp: { status: "waiting for the view", replies: null }, recv: T("no answer from B"), sent: [["A", "init-view(v2, primary A, backup C)"]], out: "c=3 was known to B and A, a majority. Choosing A keeps it" },
      { perm: { view: "v2" }, temp: { status: "running, backup", "events+": ["v1.3 c=3"] }, recv: [["A", "newview(v2, primary A, events up to v1.3)"]] },
    ] },
];

const linNote = "One value, copied at A and at B. Writes go to B, which passes them on. Either node answers reads from its own copy.";
const linProse = [
  "Node A holds the value x.",
  "A client asks A to read the value. A answers x at once, from its own copy.",
  "B passes on a write of y. A stores it and confirms.",
  "A client asks again, and A answers y.",
];
const linRows = (o1, o2) => [
  { recv: O("read the value"), sent: [["outside", "answer(x)"]], out: o1 },
  o2 ? { perm: { value: "y" }, recv: [["B", "store(y)"]], sent: [["B", "stored"]], out: o2 } : { perm: { value: "y" }, recv: [["B", "store(y)"]], sent: [["B", "stored"]] },
  { recv: O("read the value"), sent: [["outside", "answer(y)"]] },
];
SCENES.linear = [
  { id: "underway", name: "While the write is under way", who: "A", peers: "B", note: linNote,
    outside: "A client has asked B to write y. B has not yet applied it or answered anyone.",
    init: { perm: { value: "x" } }, prose: linProse,
    rows: linRows("this read overlaps the write, so x is a fair answer: it is as if the read came just before the write", "B now applies y and reports the write done") },
  { id: "newold", name: "After another reader saw y", who: "A", peers: "B", twin: "underway", note: linNote,
    outside: "A client has asked B to write y. B applied it at once, and has already answered another reader with y.",
    init: { perm: { value: "x" } }, prose: linProse,
    rows: linRows("another read was answered y before this one began, and this one is answered x. No single copy answers y and then x") },
];

PAPERS.splice(PAPERS.findIndex(p => p.id === "paxos") + 1, 0, {
  id: "vr", name: "Primary and backups", year: "1988 / 1990",
  cite: "Oki & Liskov 1988 · Viewstamped Replication: A New Primary Copy Method to Support Highly-Available Distributed Systems\nSchneider 1990 · Implementing Fault-Tolerant Services Using the State Machine Approach: A Tutorial\nRelated: Liskov & Cowling 2012 · Viewstamped Replication Revisited, and Ongaro & Ousterhout 2014 · Raft, later retellings of the same design",
  idea: "One node, the primary, does the work and sends a record of each event to the backups. An event is safe once a majority know it. When the primary is lost, the nodes still in touch form a new view, and the one that knows the most becomes its primary, so everything a majority knew is carried over.",
  names: "node = cohort · view = the cohorts in touch with one another, one of them the primary · v2 = viewid · v1.3 = viewstamp: view 1, timestamp 3 · record = an event record, sent through the communication buffer · known to a majority = forced to a sub-majority of backups · forming a view = status “view manager” · waiting for the view = status “underling” · invite, accept, init-view, newview = the paper's own names",
  frame: {
    goal: "Keep a service running and its state intact when nodes crash or are cut off, with the copies behaving as one.",
    shared: "The events known to a majority. Up front, everyone knows the list of nodes.",
    assumes: "Messages can be lost, delayed or reordered, and the network can split. A node that crashes loses everything but the number of its current view, and says so when it rejoins. If a majority crash at once, what they knew may be gone, and then no new view ever forms. Nobody lies." },
  scenes: SCENES.vr });
PAPERS.push({
  id: "benor", name: "Flipping a coin", year: "1983",
  cite: "Ben-Or 1983 · Another Advantage of Free Choice: Completely Asynchronous Agreement Protocols",
  idea: "No fixed rule can always decide when one node may stop. A rule with a coin can, with probability 1. In each round nodes report their values, and propose a value only if more than half reported it. A node that sees a proposal adopts it. A node that sees none flips a coin. Two values can never both be proposed in one round, so the coin never risks a wrong decision. It only breaks ties, and sooner or later the coins agree.",
  names: "report = the message (1, r, v) · propose = the message (2, r, v, D) · propose ? = the message (2, r, ?) · value = xₚ · coin = set xₚ to 1 or 0, each with probability ½ · decided = the write-once output register · x, y = 0, 1",
  frame: {
    goal: "Agree on one of two values with no assumption about timing at all, deciding with probability 1 as long as a majority of nodes keep running.",
    shared: "Only the rule and the number of nodes. Each node has its own coin.",
    assumes: "Messages take any length of time and arrive in any order, but do arrive. Fewer than half the nodes stop. Nobody lies here; the paper gives a second rule for liars, which needs more than five nodes for each liar. Even a scheduler that sees everything cannot hold off a decision forever, except with probability 0." },
  scenes: SCENES.benor }, {
  id: "commit", name: "Commit or abort", year: "1978 / 1981",
  cite: "Gray 1978 · Notes on Data Base Operating Systems (the two-phase commit protocol)\nSkeen 1981 · Nonblocking Commit Protocols",
  idea: "Several nodes must all do a thing or all not do it. A coordinator asks each whether it can. A node that agrees gives up the right to back out. If all agree, the coordinator records commit and tells everyone; otherwise it says abort. A node that has agreed and then hears nothing cannot safely do either.",
  names: "request commit, agree, commit, abort, ack = REQUEST_COMMIT, AGREE, COMMIT, ABORT, ACKNOWLEDGE (Gray) · agreed (can finish or undo) = the undo and redo log forced to nonvolatile storage · the coordinator's record = the commit record, written before any commit message is sent · waiting for a stopped coordinator = blocking (Skeen)",
  frame: {
    goal: "Either every participant commits or none does, though messages are lost and nodes crash and restart.",
    shared: "The decision, which is held in one place: the coordinator's log.",
    assumes: "Messages can be lost and are sent again. A node can crash and restart from what it wrote down. Any participant may refuse until it has agreed. A participant that has agreed waits for the coordinator; Skeen calls this blocking and gives the conditions under which a protocol avoids it. Nobody lies." },
  scenes: SCENES.commit }, {
  id: "linear", name: "As if one copy", year: "1990",
  cite: "Herlihy & Wing 1990 · Linearizability: A Correctness Condition for Concurrent Objects",
  idea: "An operation takes time: it begins when it is asked and ends when it is answered. Copies behave as one if each operation can be given a single moment between its beginning and its end, so that the answers are what one copy would give in that order. Operations that overlap may go either way round. One that ended before another began must come first.",
  names: "begins, ends = invocation, response · a single moment = “takes effect instantaneously at some point between its invocation and its response” · the order of moments = a legal sequential history · must come first = the precedence order on operations · the value = a register object",
  frame: {
    goal: "Say exactly when the answers given by many nodes, to many clients, at overlapping times, are answers a single copy could have given.",
    shared: "Nothing is prescribed. This is a test applied to what happened, not a way of making it happen.",
    assumes: "Every operation has a beginning and an end that an outside observer can put in order. The paper is about objects shared by processes on one machine; the same test is applied to copies on many nodes. It shows two properties: each object can be checked by itself, and no operation is ever forced to wait." },
  scenes: SCENES.linear });
