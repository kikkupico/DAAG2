const PAPERS = [
{
  id: "clocks", name: "Logical clocks", year: "1978 / 1988",
  cite: "Lamport 1978 · Time, Clocks, and the Ordering of Events in a Distributed System\nFidge 1988 · Timestamps in Message-Passing Systems That Preserve the Partial Ordering\nMattern 1988 · Virtual Time and Global States of Distributed Systems",
  idea: "No shared clock, so count instead. Each event adds one, each message carries the count, and a receiver jumps past it. A cause always gets a smaller number than its effect. Keeping one count per node also shows when two events are unrelated.",
  names: "counter = clock C\u1d62 · @n = timestamp T\u2098 (Lamport) · seen = vector time (Mattern), timestamp array (Fidge)",
  frame: {
    goal: "Number every event so a cause always gets a smaller number than its effect, and all nodes can list events in one agreed order. With one count per node, also tell when neither of two events caused the other.",
    shared: "Nothing is stored in common. The order emerges from the numbers stamped on messages. Up front, nodes share only the counting rule and each other's names, for breaking ties.",
    assumes: "No shared clock. Messages may be slow or lost: counting needs no reply. The paper never considers a node being replaced." },
  scenes: SCENES.clocks },
{
  id: "snapshot", name: "Snapshots", year: "1985",
  cite: "Chandy & Lamport 1985 · Distributed Snapshots: Determining Global States",
  idea: "When its first marker arrives, a node reads its own value and writes a copy. Until a marker arrives on each incoming stream, it also writes down every message that stream delivers. The copies plus the written-down messages add up to a state the system could have been in.",
  names: "units copy = the process's recorded state · copied from B = recorded state of the channel from B",
  frame: {
    goal: "Read every node's value, plus the messages in transit, so the results form a state the system could actually have been in, without stopping anyone from writing.",
    shared: "The snapshot, in pieces: each node holds a copy of its own value plus the messages it wrote down from each incoming stream.",
    assumes: "Messages between two nodes are never lost and arrive in the order sent, after a delay that is arbitrary but finite. Every node can be reached, directly or through others. No node is replaced during a snapshot." },
  scenes: SCENES.snapshot },
{
  id: "flp", name: "Slow or stopped", year: "1985",
  cite: "Fischer, Lynch & Paterson 1985 · Impossibility of Distributed Consensus with One Faulty Process",
  idea: "A node that hears nothing cannot tell whether a peer has stopped or is only slow. A rule that decides without that peer can be wrong; a rule that waits for it can wait forever. The paper proves every rule has some run that never decides, if just one node may stop.",
  names: "input = input register x\u209a · decided = output register y\u209a, written once · nothing = the null marker \u2205 · x, y = 0, 1 · stopped = faulty",
  frame: {
    goal: "Each node starts with x or y. Every node that decides must pick the same value, and some node must decide. Both values must be possible outcomes.",
    shared: "Only the rule. Each node holds its own input, and writes its decision once, in permanent state.",
    assumes: "Messages take any finite time and arrive in any order, but are never lost or altered. No clocks: in each step a node receives one message or nothing. At most one node stops for good, with no replacement. Nodes follow the rule exactly, with no randomness." },
  scenes: SCENES.flp },
{
  id: "suspect", name: "Suspecting", year: "1988 / 1996",
  cite: "Dwork, Lynch & Stockmeyer 1988 · Consensus in the Presence of Partial Synchrony\nChandra & Toueg 1996 · Unreliable Failure Detectors for Reliable Distributed Systems",
  idea: "A node may suspect a silent peer of having stopped, and may be wrong. Suspicion only decides when to move on, never what to decide: a value is locked once a majority says yes to one coordinator, and every later coordinator finds it. So wrong suspicions cost time, never agreement.",
  names: "suspects = the failure detector's output Dₚ · waiting longer after a mistake = increasing the timeout · estimate, adopted in = estimateₚ, tsₚ · coordinator of round r = (r mod n) + 1 · yes, no = ack, nack · decide, passed on = Reliable Broadcast · delays that settle eventually = partial synchrony (Dwork, Lynch & Stockmeyer)",
  frame: {
    goal: "Each node starts with a value. Every node that decides picks the same one, it is one of the starting values, and every node that keeps running decides.",
    shared: "Up front, the list of nodes and the order in which they take turns coordinating rounds.",
    assumes: "Messages are never lost, but can take any time. Fewer than half the nodes may stop, for good. Each node keeps a list of suspects that can be wrong. Agreement never depends on that list. Finishing needs a time after which some running node is no longer suspected by anyone, which waiting longer after each mistake gives once delays settle." },
  scenes: SCENES.suspect },
{
  id: "paxos", name: "Paxos", year: "1998 / 2001",
  cite: "Lamport 1998 · The Part-Time Parliament\nLamport 2001 · Paxos Made Simple",
  idea: "Voters promise to ignore older rounds and accept proposals, and keep both permanently. Once a majority accepts a value in one round, every later round must propose that same value.",
  names: "claim = NextBallot · promise = LastVote · propose = BeginBallot · accepted = Voted · tried up to = lastTried · promised = nextBal · accepted (state) = prevVote · chosen = the decree in the ledger · chosen(v) = Success · last votes = the slip of paper",
  frame: {
    goal: "Choose exactly one value, and never change it once chosen.",
    shared: "The chosen value, though no node stores it as such: it is whatever a majority of voters accepted in the same round. Up front, everyone knows the list of voters, so “majority” means the same to all.",
    assumes: "Nodes run at any speed and may end; a replacement starts from the old node's permanent state. Messages can be delayed, repeated or lost, but never altered. Nobody lies." },
  scenes: SCENES.paxos },
{
  id: "raft", name: "Raft", year: "2014",
  cite: "Ongaro & Ousterhout 2014 · In Search of an Understandable Consensus Algorithm\nRelated: Oki & Liskov 1988, Liskov & Cowling 2012 · Viewstamped Replication, a close relative: rounds are views, and VR Revisited keeps nothing permanent, rebuilding state from peers instead",
  idea: "One coordinator per round appends entries to every log, and an entry is agreed once a majority has it. Round, vote and log are permanent. Everything else can be rebuilt.",
  names: "round = currentTerm · voted for = votedFor · agreed up to = commitIndex · applied up to = lastApplied · claim = RequestVote · append = AppendEntries",
  frame: {
    goal: "Keep the same log on every node, so all of them apply the same entries in the same order.",
    shared: "The log up to the agreed position. Entries past it are not yet shared and can still be replaced. Up front, everyone knows the list of nodes.",
    assumes: "Messages can be delayed, lost, repeated or reordered. A node may end and be replaced by one starting from its permanent state. Nobody lies. Correctness never depends on timing, but progress needs a reachable majority and messages that arrive before timers run out." },
  scenes: SCENES.raft },
{
  id: "liars", name: "Liars", year: "1980 / 1982",
  cite: "Pease, Shostak & Lamport 1980 · Reaching Agreement in the Presence of Faults\nLamport, Shostak & Pease 1982 · The Byzantine Generals Problem",
  idea: "Some nodes may lie, telling different nodes different things. Honest nodes pass on what they were told and take the majority. With three nodes and one liar no rule works: it takes 3m + 1 nodes to survive m liars.",
  names: "sender = commander · receivers = lieutenants · liar = traitor · x, y = attack, retreat · pass on, then majority = algorithm OM(1)",
  frame: {
    goal: "One node sends a value. All honest nodes decide the same value, and if the sender is honest, that is the value it sent.",
    shared: "Up front: the list of nodes, which one sends, and a default value. Each receiver knows who sent each message it gets.",
    assumes: "Every message sent arrives unchanged, and a missing one can be noticed; it then counts as the default. Up to m nodes lie and may send anything; the rest follow the rule. Nodes are not replaced." },
  scenes: SCENES.liars },
{
  id: "pbft", name: "Ordering with liars", year: "1999",
  cite: "Castro & Liskov 1999 · Practical Byzantine Fault Tolerance",
  idea: "With 3f + 1 nodes, up to f may lie. One node orders each request; the others check with each other before acting. Two rounds of matching messages from 2f + 1 nodes mean any two such groups share an honest node, so no two honest nodes run different requests in the same slot.",
  names: "order = PRE-PREPARE · agree = PREPARE · commit = COMMIT · ready to run (two matching agrees) = prepared · run after three commits = committed-local · view, primary = v mod n · change view = VIEW-CHANGE · new view = NEW-VIEW · done = REPLY; the client waits for f + 1 matching replies · f = 1, n = 4",
  frame: {
    goal: "Every honest node runs the same requests in the same order, and each client gets a correct answer, even if some nodes lie.",
    shared: "Up front, the list of nodes and which one orders requests in each view. Messages are signed, so a node can't pretend to be another or alter what another said.",
    assumes: "Messages can be lost, delayed, repeated or reordered. Up to f of 3f + 1 nodes lie, and may send anything. Correctness never depends on timing; progress needs delays that don't keep growing faster than the timers." },
  scenes: SCENES.pbft },
{
  id: "cap", name: "CAP", year: "2000 / 2002",
  cite: "Brewer 2000 · Towards Robust Distributed Systems\nGilbert & Lynch 2002 · Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services\nRelated: Herlihy & Wing 1990 · Linearizability, the precise meaning of “always the latest value”",
  idea: "When every message between two groups of nodes may be lost, a node asked for the value must answer without hearing from the other group, perhaps with an old value, or not answer at all. It can't tell a write it missed from no write.",
  names: "always the latest value = atomic consistency, also called linearizability (Herlihy & Wing) · every request answered = availability · messages lost between groups = a partition · outside = a client",
  frame: {
    goal: "Every read returns the latest value written, and every request to a running node gets an answer, even while messages between groups are lost.",
    shared: "One value that clients read and write, with a copy on each node.",
    assumes: "Any message can be lost, and a node can't tell lost from slow. The paper proves the result both without clocks and with timers. Nodes don't stop and nobody lies." },
  scenes: SCENES.cap },
{
  id: "quorum", name: "Quorums", year: "2007 / 2012",
  cite: "DeCandia et al. 2007 · Dynamo: Amazon's Highly Available Key-value Store\nBailis et al. 2012 · Probabilistically Bounded Staleness for Practical Partial Quorums",
  idea: "Keep N copies. A write waits for W of them, a read for R. If R + W is more than N, every read group shares a node with every write group, so a read finds the latest write. Smaller groups answer faster, and are only sometimes stale.",
  names: "copies = N replicas · two for a write = W · two for a read = R · overlapping groups = R + W > N (strict quorum) · reading one copy = a partial quorum, measured by PBS · the list on each version = vector clock · catching up after a read = read repair · two versions returned = divergent versions, reconciled by the client · cart = Dynamo's shopping cart",
  frame: {
    goal: "Always accept writes and answer reads quickly. With overlapping groups, a read sees the latest finished write. Concurrent writes are kept side by side for the client to combine.",
    shared: "Up front, the number of copies and the group sizes. Each node holds full versions, each carrying a list of counts, one per node.",
    assumes: "Messages can be lost, delayed or reordered. Copies are stored durably, so a node can be replaced. Dynamo itself lets a stand-in node hold a copy while one is down, which can break the overlap. Nobody lies." },
  scenes: SCENES.quorum },
{
  id: "merge", name: "Merging copies", year: "1987 / 2011",
  cite: "Demers et al. 1987 · Epidemic Algorithms for Replicated Database Maintenance\nShapiro, Preguiça, Baquero & Zawirski 2011 · A Comprehensive Study of Convergent and Commutative Replicated Data Types\nHellerstein & Alvaro 2020 · Keeping CALM: When Distributed Consistency Is Easy",
  idea: "If a node's state only grows, and two copies combine by keeping the larger part of each, nodes never need to wait for one another. Messages can be lost, repeated or reordered: once every node has heard, directly or through others, everything the others added, all copies are equal.",
  names: "counts = the G-Counter's payload P · keep the larger of each = merge, the least upper bound · added / removed = the 2P-Set's A and R (R is the tombstone set) · x:A1 = an element with a unique tag, as in the OR-Set · resending on a timer = anti-entropy (Demers) · only grows = monotonic (CALM)",
  frame: {
    goal: "Every node answers at once, without asking anyone, and all copies end up equal once messages stop changing them.",
    shared: "Up front, only the list of nodes and the merge rule. Each node holds a full copy and sends all of it.",
    assumes: "Messages can be lost, repeated, delayed or reordered, as long as some keep getting through. Copies are kept in permanent state. Nobody lies." },
  scenes: SCENES.merge },
{
  id: "bayou", name: "Tentative writes", year: "1995",
  cite: "Terry, Theimer, Petersen, Demers, Spreitzer & Hauser 1995 · Managing Update Conflicts in Bayou, a Weakly Connected Replicated Storage System",
  idea: "Accept writes anywhere and show them at once, but mark them tentative. Each write carries its own check and fallback, so it can be replayed in any order. One server fixes the final order, and every server replays its writes to match.",
  names: "booking = a Write · first choice and fallback = dependency check and merge procedure · tentative = not yet stable · final order = commit sequence, set by the primary · A1, B1 = accept stamps · passing bookings on = anti-entropy",
  frame: {
    goal: "Let anyone write at any server, even when cut off, and have every server end up with the same bookings in the same order.",
    shared: "The log of writes, held by every server. Up front, which server is the primary.",
    assumes: "Servers connect only now and then, so writes travel slowly and in any order, but each one eventually reaches every server. Logs are kept durably. Nobody lies." },
  scenes: SCENES.bayou },
{
  id: "cops", name: "Causes first", year: "2011",
  cite: "Lloyd, Freedman, Kaminsky & Andersen 2011 · Don't Settle for Eventual: Scalable Causal Consistency for Wide-Area Storage with COPS",
  idea: "Each write names the writes it depends on. A site holds back an arriving write until those are present. Readers at any site then never see an effect without its cause, while every site still answers at once.",
  names: "site = cluster (datacenter) · after photo v1 = the write's nearest dependency · holding = waiting for dep_check to succeed · write(…, after …) = put_after · Alice and Bob = the paper's photo example",
  frame: {
    goal: "Answer every read and write at the local site at once, and never show an effect before its cause.",
    shared: "Each site holds a full copy. Each write carries the versions it depends on.",
    assumes: "Sites copy writes to each other in the background, in any order and with any delay, but every write eventually arrives. Within a site, operations are quick and in order. Nobody lies." },
  scenes: SCENES.cops },
];

