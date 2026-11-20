// Global traces for the results added to the second set (scenes-more.js). Same shape as traces.js.
const tgB = { perm: { decision: "none" }, temp: { plan: "none" } };
Object.assign(TRACES, {
// Rule 1: B acts on the plan and replies; A acts only on B's reply. Nothing is lost.
"twogen-plan": {
  nodes: { A: { init: tgInit }, B: { init: tgB } },
  steps: [
    { note: "A means to act at t with B. B knows nothing of the plan yet." },
    { note: "A sends the plan." },
    { note: "The plan reaches B. B decides to act at t, and replies.",
      acts: { B: { perm: { decision: "act at t" }, temp: { plan: "act at t", "A has my reply": "not known" }, why: "The plan arrives. By the rule B acts at t on the plan alone, so it decides now and replies. It will never learn whether the reply arrived." } } },
    { note: "The reply reaches A. Now A knows B will act, and decides to act too.",
      acts: { A: { perm: { decision: "act at t" }, temp: { "B has it": "yes" } } } },
    { note: "Time t. Both act together.",
      acts: { A: { perm: { decision: "acted at t" } },
              B: { perm: { decision: "acted at t" }, why: "Time t comes, and B acts." } } },
  ],
  msgs: [
    ["nothing", "A", "", 0, 1],
    ["A", "B", "act at t?", 1, 2],
    ["B", "A", "agreed", 2, 3],
    ["timer", "A", "time t", 3, 4], ["timer", "B", "time t", 3, 4],
  ],
},
// Rule 1 again; every reply from B is lost. B acts alone.
"twogen-lostreply": {
  nodes: { A: { init: tgInit }, B: { init: tgB } },
  steps: [
    { note: "A means to act at t with B. Every reply B sends will be lost." },
    { note: "A sends the plan." },
    { note: "The plan reaches B. B decides to act at t and replies, but the reply is lost.",
      acts: { B: { perm: { decision: "act at t" }, temp: { plan: "act at t", "A has my reply": "not known" }, why: "The plan arrives. By the rule B acts at t on the plan alone, so it decides now and replies." } } },
    { note: "A's timer fires with no reply. A sends the plan again." },
    { note: "The second copy reaches B, which replies again. That reply is lost too.",
      acts: { B: { why: "The plan arrives a second time, so B's reply must have gone astray. B replies again. It has already decided." } } },
    { note: "Time t. B acts, and A, never having heard back, does not. B acts alone.",
      acts: { A: { perm: { decision: "did not act" } },
              B: { perm: { decision: "acted at t" }, why: "Time t comes, and B acts, as it decided. Nobody acts with it." } } },
  ],
  msgs: [
    ["nothing", "A", "", 0, 1],
    ["A", "B", "act at t?", 1, 2],
    ["B", "A", "agreed", 2, null, "lost"],
    ["timer", "A", "no reply yet", 2, 3],
    ["A", "B", "act at t?", 3, 4],
    ["B", "A", "agreed", 4, null, "lost"],
    ["timer", "A", "time t", 4, 5], ["timer", "B", "time t", 4, 5],
  ],
},
// Rule 2: B waits for A's confirmation. Nothing is lost.
"twogen-confirm": {
  nodes: { A: { init: tgInit }, B: { init: tgB } },
  steps: [
    { note: "A means to act at t with B. B knows nothing of the plan yet." },
    { note: "A sends the plan." },
    { note: "The plan reaches B. B replies, and waits for A to confirm.",
      acts: { B: { temp: { plan: "act at t", "A has my reply": "not known" }, why: "The plan arrives. By this rule B must not act until it knows its reply reached A, so it replies and waits." } } },
    { note: "The reply reaches A. A decides to act at t, and confirms.",
      acts: { A: { perm: { decision: "act at t" }, temp: { "B has it": "yes", "B has my confirmation": "not known" } } } },
    { note: "The confirmation reaches B. B decides to act at t.",
      acts: { B: { perm: { decision: "act at t" }, temp: { "A has my reply": "yes" }, why: "A's confirmation arrives: A has the reply and will act. B decides to act at t." } } },
    { note: "Time t. Both act together.",
      acts: { A: { perm: { decision: "acted at t" } },
              B: { perm: { decision: "acted at t" }, why: "Time t comes, and B acts." } } },
  ],
  msgs: [
    ["nothing", "A", "", 0, 1],
    ["A", "B", "act at t?", 1, 2],
    ["B", "A", "agreed, if confirmed", 2, 3],
    ["A", "B", "confirmed", 3, 4],
    ["timer", "A", "time t", 4, 5], ["timer", "B", "time t", 4, 5],
  ],
},
// Rule 2 again; the confirmation is lost. Identical from inside A; A acts alone.
"twogen-lostconfirm": {
  nodes: { A: { init: tgInit }, B: { init: tgB } },
  steps: [
    { note: "A means to act at t with B. A's confirmation will be lost." },
    { note: "A sends the plan." },
    { note: "The plan reaches B. B replies, and waits for A to confirm.",
      acts: { B: { temp: { plan: "act at t", "A has my reply": "not known" }, why: "The plan arrives. By this rule B must not act until it knows its reply reached A, so it replies and waits." } } },
    { note: "The reply reaches A. A decides to act at t, and confirms. The confirmation is lost.",
      acts: { A: { perm: { decision: "act at t" }, temp: { "B has it": "yes", "B has my confirmation": "not known" } } } },
    { note: "Time t. A acts. B, never confirmed, does not. A acts alone.",
      acts: { A: { perm: { decision: "acted at t" } },
              B: { perm: { decision: "did not act" }, why: "Time t comes with no confirmation. B can't know its reply arrived, so by the rule it does not act." } } },
  ],
  msgs: [
    ["nothing", "A", "", 0, 1],
    ["A", "B", "act at t?", 1, 2],
    ["B", "A", "agreed, if confirmed", 2, 3],
    ["A", "B", "confirmed", 3, null, "lost"],
    ["timer", "A", "time t", 3, 4], ["timer", "B", "time t", 3, 4],
  ],
},
});
Object.assign(TRACES, {
// SM(1): S lies, signing x for A and y for B. Both see both signed values and take the default.
"signed-sender": {
  nodes: {
    S: { role: "sender", init: { perm: {} } },
    A: { role: "receiver", init: { perm: { decided: "none" } } },
    B: { role: "receiver", init: { perm: { decided: "none" } } },
  },
  steps: [
    { note: "A sender, S, and two receivers, A and B. S is the liar. Signatures can't be forged." },
    { note: "S signs x for A and y for B.",
      acts: { S: { temp: { signed: "A=x; B=y" }, why: "S lies, but must sign what it sends: it signs x for A and y for B." } } },
    { note: "A and B each pass on the signed value they got.",
      acts: { A: { temp: { "signed by S": "x" } },
              B: { temp: { "signed by S": "y" }, why: "S sends B the value y, with its signature. B passes the signed value on to A unchanged." } } },
    { note: "Each now holds x and y, both signed by S. S lied, and both take the default, y.",
      acts: { A: { perm: { decided: "y" }, temp: { "signed by S": "x, y" } },
              B: { perm: { decided: "y" }, temp: { "signed by S": "y, x" }, why: "A passes on x, also signed by S. S signed two different values, so S lied. B takes the default, y." } } },
  ],
  msgs: [
    ["S", "A", "value(x, signed S)", 1, 2],
    ["S", "B", "value(y, signed S)", 1, 2],
    ["A", "B", "relayed(x, signed S)", 2, 3],
    ["B", "A", "relayed(y, signed S)", 2, 3],
  ],
},
// SM(1): B lies. It cannot sign y as S, so its claim is a forgery and is discarded.
"signed-relay": {
  nodes: {
    S: { role: "sender", init: { perm: {} } },
    A: { role: "receiver", init: { perm: { decided: "none" } } },
    B: { role: "receiver", init: { perm: { decided: "none" } } },
  },
  steps: [
    { note: "A sender, S, and two receivers, A and B. B is the liar. Signatures can't be forged." },
    { note: "S signs x for both.",
      acts: { S: { temp: { signed: "A=x; B=x" }, why: "S is honest: it signs x for A and x for B." } } },
    { note: "A passes on x, signed by S. B lies, and passes on y with a signature it made up.",
      acts: { A: { temp: { "signed by S": "x" } },
              B: { temp: { "signed by S": "x" }, why: "B lies. It would like A to think S said y, but it can't sign as S, so it makes up the signature." } } },
    { note: "A sees the forgery and discards it. S signed only x, so A decides x.",
      acts: { A: { perm: { decided: "x" }, temp: { discarded: "y: forged" } },
              B: { why: "A's copy of x arrives, signed by S. B is the liar; whatever it decides, it can't change what A decides." } } },
  ],
  msgs: [
    ["S", "A", "value(x, signed S)", 1, 2],
    ["S", "B", "value(x, signed S)", 1, 2],
    ["A", "B", "relayed(x, signed S)", 2, 3],
    ["B", "A", "relayed(y, forged S)", 2, 3],
  ],
},
});
const elB = { perm: { leader: "B (9)" }, temp: { "my number": "9", status: "normal" } }, elC = { perm: { leader: "B (9)" }, temp: { "my number": "3", status: "normal" } };
const elBullySteps = [
  { note: "A has missed its leader. It asks the only higher node, B, whether it is up.", acts: { A: { temp: { status: "election" } } } },
  { note: "No answer within T. A halts the only lower node, C." },
  { note: "C halts, and says so.",
    acts: { C: { temp: { status: "election" }, why: "A, a higher node, says halt. C stops what it was doing and enters the election, and says so." } } },
  { note: "A tells C it is elected, and takes over.", acts: { A: { perm: { leader: "A (5)" }, temp: { status: "normal" } } } },
  { note: "C takes A as its leader.",
    acts: { C: { perm: { leader: "A (5)" }, temp: { status: "normal" }, why: "A says it is elected, and it was A that halted C. C takes A as its leader." } } },
];
const elBullyMsgs = [
  ["timer", "A", "no word from the leader", 0, 1],
  ["timer", "A", "no answer within T", 1, 2],
  ["A", "C", "halt", 2, 3],
  ["C", "A", "halted", 3, 4],
  ["A", "C", "I am elected", 4, 5],
];
Object.assign(TRACES, {
// Chang & Roberts: ring A -> B -> C -> A, numbers 5, 9, 3. A starts; B and C join when the first message reaches them.
"election-ring": {
  nodes: {
    A: { init: { perm: { leader: "none" }, temp: { "my number": "5", "taken part": "no" } } },
    B: { init: { perm: { leader: "none" }, temp: { "my number": "9", "taken part": "no" } } },
    C: { init: { perm: { leader: "none" }, temp: { "my number": "3", "taken part": "no" } } },
  },
  steps: [
    { note: "A ring, A to B to C to A, with numbers 5, 9 and 3. No leader." },
    { note: "A starts an election, sending 5 to B.", acts: { A: { temp: { "taken part": "yes" } } } },
    { note: "B drops 5, smaller than its own 9, and joins in by sending 9.",
      acts: { B: { temp: { "taken part": "yes" }, why: "5 arrives from A. B's own number is larger, so B drops it. B hadn't taken part yet, so it joins in, sending its own 9 on to C." } } },
    { note: "C joins in with 3, and passes on 9, larger than its own.",
      acts: { C: { temp: { "taken part": "yes" }, why: "9 arrives from B. It is larger than C's own 3, so C passes it on. C hadn't taken part yet, so it sends its own 3 on as well." } } },
    { note: "A drops 3 and passes on 9." },
    { note: "9 comes back to B: B is elected, and sends the word round.",
      acts: { B: { perm: { leader: "B (9)" }, temp: { "taken part": "no" }, why: "B's own number, 9, has come back. It met every other node and none was larger, so B is the highest. B sends the word round." } } },
    { note: "C takes B as leader and passes the word on.",
      acts: { C: { perm: { leader: "B (9)" }, temp: { "taken part": "no" }, why: "Word comes that 9 is elected. C takes B as its leader and passes the word on." } } },
    { note: "A takes B as leader and passes the word on.", acts: { A: { perm: { leader: "B (9)" }, temp: { "taken part": "no" } } } },
    { note: "The word is back at B. Everyone has B as leader.",
      acts: { B: { why: "The word has been all the way round: every node knows that B leads." } } },
  ],
  msgs: [
    ["timer", "A", "no leader", 0, 1],
    ["A", "B", "elect(5)", 1, 2],
    ["B", "C", "elect(9)", 2, 3],
    ["C", "A", "elect(3)", 3, 4], ["C", "A", "elect(9)", 3, 4],
    ["A", "B", "elect(9)", 4, 5],
    ["B", "C", "elected(9)", 5, 6],
    ["C", "A", "elected(9)", 6, 7],
    ["A", "B", "elected(9)", 7, 8],
  ],
},
// Garcia-Molina's Bully algorithm: B, the leader, has stopped; A is the highest left.
"election-bully": {
  nodes: { A: { init: elInit }, B: { init: elB }, C: { init: elC } },
  steps: [{ note: "Numbers: A 5, B 9, C 3. B leads, and has stopped for good." }, ...elBullySteps],
  msgs: [["A", "B", "are you up?", 1, null, "lost"], ...elBullyMsgs],
},
// The same, but B had only paused. It wakes still believing it leads.
"election-pause": {
  nodes: { A: { init: elInit }, B: { init: elB }, C: { init: elC } },
  steps: [{ note: "Numbers: A 5, B 9, C 3. B leads, and has paused for longer than T." }, ...elBullySteps,
    { note: "B wakes, still the leader by its own account, and sends C its orders. A's question arrives, long after T.",
      acts: { B: { why: "B carries on, unaware that it paused. By its own state it still leads, so it sends C its orders. A's question turns up too, long late." } } },
    { note: "C, whose leader is A, gets orders from B. Two nodes act as leader.",
      acts: { C: { why: "Orders arrive from B, which says it leads. C's leader is A. Two nodes are acting as leader, and C can't tell which to obey." } } },
  ],
  msgs: [["A", "B", "are you up?", 1, 6], ...elBullyMsgs, ["B", "C", "orders from leader B", 6, 7]],
},
});
const mxB = (n, due) => ({ requesting: `yes, as (${n}, B)`, "highest seen": `${n}`, "replies due": due });
Object.assign(TRACES, {
// Ricart & Agrawala: A and B both ask with number 1; the tie goes to A by name, and A holds its reply to B.
"mutex-tie": {
  nodes: { A: { init: mxInit }, B: { init: mxInit }, C: { init: mxInit } },
  steps: [
    { note: "Three nodes, none asking. A and B are about to need the resource at the same moment." },
    { note: "A and B both ask, each with number 1.",
      acts: { A: mxAsk(1), B: { temp: mxB(1, "2"), why: "B needs the resource. The highest number it has seen is 0, so it asks A and C with request 1." } } },
    { note: "A holds its reply to B: tie, and A's name comes first. B replies to A at once. C replies to B.",
      acts: { A: { temp: { deferred: "B" } },
              B: { why: "A's request arrives, also numbered 1. It's a tie, and A's name comes first, so A's request goes first. B replies at once." },
              C: { temp: { "highest seen": "1" }, why: "B's request arrives. C isn't asking, so it replies at once." } } },
    { note: "A has B's reply. B has C's. C replies to A, whose request reached it late.",
      acts: { A: { temp: { "replies due": "1" } },
              B: { temp: { "replies due": "1" }, why: "C replies. B still waits for A." },
              C: { why: "A's request arrives, late. C isn't asking, so it replies at once." } } },
    { note: "A has every reply, and uses the resource.", acts: { A: { temp: { "replies due": "0", using: "yes" } } } },
    { note: "A is done, and sends B the reply it held.", acts: { A: { temp: { requesting: "no", using: "no", deferred: "none" } } } },
    { note: "B has every reply, and uses the resource. Never at the same time as A.",
      acts: { B: { temp: { "replies due": "0", using: "yes" }, why: "A's reply comes at last: A is done. Every other node has replied, so B uses the resource." } } },
  ],
  msgs: [
    ["outside", "A", "use the resource", 0, 1], ["outside", "B", "use the resource", 0, 1],
    ["A", "B", "request(1, A)", 1, 2], ["A", "C", "request(1, A)", 1, 3],
    ["B", "A", "request(1, B)", 1, 2], ["B", "C", "request(1, B)", 1, 2],
    ["B", "A", "reply", 2, 3], ["C", "B", "reply", 2, 3],
    ["C", "A", "reply", 3, 4],
    ["outside", "A", "done with the resource", 4, 5],
    ["A", "B", "reply", 5, 6],
  ],
},
// B asks first, with 1. A's later request is numbered 2, and B holds its reply until it is done.
"mutex-later": {
  nodes: { A: { init: mxInit }, B: { init: mxInit }, C: { init: mxInit } },
  steps: [
    { note: "Three nodes, none asking. B is about to need the resource, and A shortly after." },
    { note: "B asks with number 1.", acts: { B: { temp: mxB(1, "2"), why: "B needs the resource. The highest number it has seen is 0, so it asks A and C with request 1." } } },
    { note: "A and C are not asking, and reply at once.",
      acts: { A: { temp: { "highest seen": "1" } }, C: { temp: { "highest seen": "1" }, why: "B's request arrives. C isn't asking, so it replies at once." } } },
    { note: "B has both replies and uses the resource. Now A asks, with number 2.",
      acts: { A: mxAsk(2), B: { temp: { "replies due": "0", using: "yes" }, why: "A and C both reply. Every other node has replied, so B uses the resource." } } },
    { note: "B holds its reply: its own request, 1, comes before A's 2. C replies.",
      acts: { B: { temp: { "highest seen": "2", deferred: "A" }, why: "A's request arrives, numbered 2. B's own is 1, so B's goes first. B is using the resource, and holds its reply." },
              C: { temp: { "highest seen": "2" }, why: "A's request arrives. C isn't asking, so it replies at once." } } },
    { note: "A has C's reply. B is done, and sends A the reply it held.",
      acts: { A: { temp: { "replies due": "1" } }, B: { temp: { requesting: "no", using: "no", deferred: "none" }, why: "B is done. It sends A the reply it was holding." } } },
    { note: "A has every reply, and uses the resource.", acts: { A: { temp: { "replies due": "0", using: "yes" } } } },
    { note: "A is done.", acts: { A: { temp: { requesting: "no", using: "no" } } } },
  ],
  msgs: [
    ["outside", "B", "use the resource", 0, 1],
    ["B", "A", "request(1, B)", 1, 2], ["B", "C", "request(1, B)", 1, 2],
    ["A", "B", "reply", 2, 3], ["C", "B", "reply", 2, 3],
    ["outside", "A", "use the resource", 2, 3],
    ["A", "B", "request(2, A)", 3, 4], ["A", "C", "request(2, A)", 3, 4],
    ["C", "A", "reply", 4, 5],
    ["outside", "B", "done with the resource", 4, 5],
    ["B", "A", "reply", 5, 6],
    ["outside", "A", "done with the resource", 6, 7],
  ],
},
// A different rule: nobody holds a reply. A and B both get every reply and use the resource together.
"mutex-nodefer": {
  nodes: { A: { init: mxInit }, B: { init: mxInit }, C: { init: mxInit } },
  steps: [
    { note: "Three nodes, none asking. Under this rule nobody ever holds a reply." },
    { note: "A and B both ask, each with number 1.",
      acts: { A: mxAsk(1), B: { temp: mxB(1, "2"), why: "B needs the resource. The highest number it has seen is 0, so it asks A and C with request 1." } } },
    { note: "A and B each reply to the other at once. C replies to B.",
      acts: { B: { why: "A's request arrives. By this rule B replies at once." },
              C: { temp: { "highest seen": "1" }, why: "B's request arrives. C isn't asking, so it replies at once." } } },
    { note: "A has B's reply. B has every reply and uses the resource. C replies to A.",
      acts: { A: { temp: { "replies due": "1" } },
              B: { temp: { "replies due": "0", using: "yes" }, why: "A and C both reply. Every other node has replied, so B uses the resource." },
              C: { why: "A's request arrives, late. C isn't asking, so it replies at once." } } },
    { note: "A has every reply and uses the resource too. Both are using it.",
      acts: { A: { temp: { "replies due": "0", using: "yes" } } } },
  ],
  msgs: [
    ["outside", "A", "use the resource", 0, 1], ["outside", "B", "use the resource", 0, 1],
    ["A", "B", "request(1, A)", 1, 2], ["A", "C", "request(1, A)", 1, 3],
    ["B", "A", "request(1, B)", 1, 2], ["B", "C", "request(1, B)", 1, 2],
    ["A", "B", "reply", 2, 3], ["B", "A", "reply", 2, 3], ["C", "B", "reply", 2, 3],
    ["C", "A", "reply", 3, 4],
  ],
},
});
const abdC = { temp: { latest: "1: x" } }, abdB = { temp: { latest: "1: x" } };
const abdStart = { note: "B begins writing y, with label 2; its messages are lost on the way. A begins a read.",
  acts: { A: { temp: { answers: "A: 1 x" } }, B: { temp: { latest: "2: y" }, why: "A client asks B to write y. B labels it 2, one past 1, and sends it to A and C. Both messages are lost; B will send them again." } } };
const abdWriteMsgs = [["outside", "B", "write y", 0, 1], ["B", "A", "write(2, y)", 1, null, "lost"], ["B", "C", "write(2, y)", 1, null, "lost"],
  ["outside", "A", "read the value", 0, 1], ["A", "B", "latest?", 1, 2], ["A", "C", "latest?", 1, null, "lost"], ["B", "A", "latest(2, y)", 2, 3]];
const abdBAnswers = { note: "B answers with its latest: y, label 2.", acts: { B: { why: "A asks for B's latest. B answers y, with label 2." } } };
Object.assign(TRACES, {
"abd-announce": {
  nodes: { A: { role: "reader", init: abdInit }, B: { role: "writer", init: abdB }, C: { init: abdC } },
  steps: [
    { note: "Every node holds x, label 1. B is the writer." }, abdStart, abdBAnswers,
    { note: "A takes y, the highest label in a majority's answers, and announces it.", acts: { A: { temp: { latest: "2: y", answers: "A: 1 x; B: 2 y" } } } },
    { note: "B notes y.", acts: { B: { why: "A announces y, label 2. B already has it, and says so." } } },
    { note: "A majority holds y. A answers y." },
    { note: "C begins a read, asking A and B.", acts: { C: { temp: { answers: "C: 1 x" }, why: "A client asks C for the value. C asks A and B for their latest, counting its own." } } },
    { note: "A answers C with y." },
    { note: "C takes y, the highest label among C's and A's answers, and announces it before answering.",
      acts: { C: { temp: { latest: "2: y", answers: "C: 1 x; A: 2 y" }, why: "A answers y, label 2. With C's own that is a majority, and the highest label is 2. C takes y and announces it; it will answer once a majority have it." } } },
  ],
  msgs: [...abdWriteMsgs,
    ["A", "B", "announce(2, y)", 3, 4], ["A", "C", "announce(2, y)", 3, null, "lost"],
    ["B", "A", "have it", 4, 5], ["A", "outside", "answer(y)", 5, 5],
    ["outside", "C", "read the value", 5, 6], ["C", "A", "latest?", 6, 7], ["C", "B", "latest?", 6, null],
    ["A", "C", "latest(2, y)", 7, 8],
    ["C", "A", "announce(2, y)", 8, null], ["C", "B", "announce(2, y)", 8, null],
  ],
},
"abd-noannounce": {
  nodes: { A: { role: "reader", init: abdInit }, B: { role: "writer", init: abdB }, C: { init: abdC } },
  steps: [
    { note: "Every node holds x, label 1. B is the writer. Under this rule a reader answers as soon as a majority has answered it." }, abdStart, abdBAnswers,
    { note: "A answers y at once. Only B holds y.", acts: { A: { temp: { answers: "A: 1 x; B: 2 y" } } } },
    { note: "C begins a read, asking A and B.", acts: { C: { temp: { answers: "C: 1 x" }, why: "A client asks C for the value. C asks A and B for their latest, counting its own." } } },
    { note: "A answers C with x." },
    { note: "C hears x from A and from itself, a majority, and answers x, after y was given out.",
      acts: { C: { temp: { answers: "C: 1 x; A: 1 x" }, why: "A answers x, label 1. With C's own that is a majority, and the highest label is 1. C answers x." } } },
  ],
  msgs: [...abdWriteMsgs,
    ["A", "outside", "answer(y)", 3, 3],
    ["outside", "C", "read the value", 3, 4], ["C", "A", "latest?", 4, 5], ["C", "B", "latest?", 4, null],
    ["A", "C", "latest(1, x)", 5, 6], ["C", "outside", "answer(x)", 6, 6],
  ],
},
});
const lsB = { temp: { copy: "x", "lease until": "12:10" } }, lsC = { temp: {} };
const lsStart = [
  { note: "C asks A to write y.", acts: { C: { why: "A client asks C to write y. C passes it to A, which keeps the value." } } },
  { note: "B's lease is running, so A asks B to approve. B is cut off, and the message is lost.", acts: { A: { temp: { waiting: "y, for B" } } } },
];
const lsMsgs0 = [["outside", "C", "write y", 0, 1], ["C", "A", "write y", 1, 2], ["A", "B", "may I write?", 2, null, "lost"]];
const sqK = { temp: { "lock held by": "B (1)" } }, sqB = { temp: { lock: "1" } }, sqC = { temp: { lock: "none" } };
const sqSteps = (seq) => [
  { note: "B, holding the lock, sends a write of y, then pauses. The message is slow.",
    acts: { B: { why: seq ? "B holds lock 1 and sends A a write of y under it. Then B pauses." : "B holds the lock and sends A a write of y. Then B pauses." },
            C: { why: "C needs to write, and asks K for the lock. B holds it, so C waits." } } },
  { note: "B's hold on the lock runs out. K gives the lock to C.",
    acts: { K: { temp: { "lock held by": seq ? "C (2)" : "C" }, why: seq ? "B's hold on the lock has run out with no word from B. K gives the lock to C, numbering it 2." : "B's hold on the lock has run out with no word from B. K gives the lock to C." } } },
  { note: "C, now holding the lock, writes z.",
    acts: { C: { temp: { lock: seq ? "2" : "held" }, why: seq ? "C is granted lock 2, and writes z under it." : "C is granted the lock, and writes z." } } },
];
Object.assign(TRACES, {
"leases-expire": {
  nodes: { A: { role: "server", init: lsInit }, B: { init: lsB }, C: { init: lsC } },
  steps: [{ note: "A keeps x; B holds a copy under a lease until 12:10. B is cut off. Clocks are right." }, ...lsStart,
    { note: "12:05. A client asks B; its lease is running, so B answers x from its copy.", acts: { B: { why: "A client asks B for the value. B's lease runs until 12:10, so B answers from its copy: x. Nothing has been written yet." } } },
    { note: "12:10 by B's clock: B's lease is over, and B drops its copy.", acts: { B: { temp: { copy: "none", "lease until": "none" }, why: "12:10 by B's clock. Its lease is over, so B drops its copy and will ask A before answering again." } } },
    { note: "12:10 by A's clock. A writes y and tells C.", acts: { A: { perm: { value: "y" }, temp: { leases: "none", waiting: "none" } } } },
    { note: "C reports the write done.", acts: { C: { why: "A says y is written. C tells its client." } } },
  ],
  msgs: [...lsMsgs0, ["outside", "B", "read the value", 2, 3], ["B", "outside", "answer(x)", 3, 3], ["timer", "B", "12:10: my lease is over", 3, 4],
    ["timer", "A", "12:10: B's lease is over", 4, 5], ["A", "C", "written", 5, 6], ["C", "outside", "done(y)", 6, 6]],
},
"leases-fastclock": {
  nodes: { A: { role: "server", init: lsInit }, B: { init: lsB }, C: { init: lsC } },
  steps: [{ note: "A keeps x; B holds a copy under a lease until 12:10. B is cut off. A's clock runs four minutes fast." }, ...lsStart,
    { note: "Really 12:06, but A's clock shows 12:10. A writes y and tells C.", acts: { A: { perm: { value: "y" }, temp: { leases: "none", waiting: "none" } } } },
    { note: "C reports the write done. Meanwhile a client asks B, whose lease runs to 12:10 by a correct clock, and B answers x.",
      acts: { B: { why: "A client asks B for the value. It is 12:07 and B's lease runs until 12:10, so B answers from its copy: x." },
              C: { why: "A says y is written. C tells its client." } } },
    { note: "12:10 by B's clock: B drops its copy. It answered x after y was written.", acts: { B: { temp: { copy: "none", "lease until": "none" }, why: "12:10 by B's clock. Its lease is over, so B drops its copy." } } },
  ],
  msgs: [...lsMsgs0, ["timer", "A", "12:10: B's lease is over", 2, 3], ["A", "C", "written", 3, 4], ["C", "outside", "done(y)", 4, 4],
    ["outside", "B", "read the value", 3, 4], ["B", "outside", "answer(x)", 4, 4], ["timer", "B", "12:10: my lease is over", 4, 5]],
},
"leases-late": {
  nodes: { A: { role: "server", init: { perm: { value: "x" } } }, K: { role: "lock service", init: { temp: { "lock held by": "B" } } }, B: { init: { temp: { lock: "held" } } }, C: { init: sqC } },
  steps: [{ note: "A keeps x. B holds the lock, granted by K for a limited time." }, ...sqSteps(false),
    { note: "C's write reaches A, which applies it.", acts: { A: { perm: { value: "z" } } } },
    { note: "B's old write finally reaches A, which applies it, over C's.", acts: { A: { perm: { value: "y" } } } },
  ],
  msgs: [["B", "A", "write(y)", 1, 5], ["timer", "K", "B's hold has run out", 1, 2], ["C", "K", "lock please", 1, 2], ["K", "C", "lock granted", 2, 3], ["C", "A", "write(z)", 3, 4]],
},
"leases-sequencer": {
  nodes: { A: { role: "server", init: sqInit }, K: { role: "lock service", init: sqK }, B: { init: sqB }, C: { init: sqC } },
  steps: [{ note: "A keeps x. B holds lock 1, granted by K for a limited time." }, ...sqSteps(true),
    { note: "C's write, under lock 2, reaches A, which applies it.", acts: { A: { perm: { value: "z" }, temp: { "highest lock seen": "2" } } } },
    { note: "B's old write, under lock 1, reaches A, which refuses it.", acts: { A: { temp: { refused: "y, lock 1" } } } },
  ],
  msgs: [["B", "A", "write(y, lock 1)", 1, 5], ["timer", "K", "B's hold has run out", 1, 2], ["C", "K", "lock please", 1, 2], ["K", "C", "lock 2", 2, 3], ["C", "A", "write(z, lock 2)", 3, 4],
    ["A", "B", "refused: lock 1 is over", 5, null]],
},
});
const nkM = { temp: { chain: "1", "secret chain": "none" } }, nkB = { temp: { chain: "1" } };
const nkPayMsgs = [["outside", "M", "write x", 0, 1], ["M", "B", "write(x)", 1, 2], ["coin", "B", "made block 2", 1, 2]];
const nkPay1 = { note: "M writes x, and sends it out. In secret it starts a chain without x.",
  acts: { M: { temp: { "secret chain": "1" }, why: "M writes x and sends it out, while secretly working on a chain from block 1 in which x was never written.",
    isle: "The {pottery} pays the {fishery} and sends the payment out, while secretly working on a payment book from page 1 in which the coins stay with the {pottery}." } } };
const nkPay2 = { note: "B makes block 2, with x in it, and sends it out.",
  acts: { B: { temp: { chain: "1 2" }, why: "x arrives, and B's work pays off: block 2, with x in it, on top of 1. B sends it out.",
    isle: "The payment arrives, and the {granary} finishes the sum: page 2, with the payment on it, after page 1. The {granary} sends it out." } } };
Object.assign(TRACES, {
"nakamoto-fork": {
  nodes: { A: { init: { temp: { chain: "1", "also kept": "none" } } }, B: { init: { temp: { chain: "1", "also kept": "none" } } }, C: { init: { temp: { chain: "1", "also kept": "none" } } } },
  steps: [
    { note: "Every node's chain is one block long." },
    { note: "A and B each make a block at the same moment, 2a and 2b, and send it out.",
      acts: { A: { temp: { chain: "1 2a" } }, B: { temp: { chain: "1 2b" }, why: "B's work pays off: block 2b on top of 1. B sends it out." } } },
    { note: "A and B each hear of the other's block; each keeps its own, heard of first. C hears of 2b first.",
      acts: { A: { temp: { "also kept": "1 2b" } }, B: { temp: { "also kept": "1 2a" }, why: "Block 2a arrives from A. It is no longer than B's own chain, which B heard of first, so B keeps building on 2b and keeps 2a." },
              C: { temp: { chain: "1 2b" }, why: "Block 2b arrives from B. It is longer than C's chain, so C builds on it." } } },
    { note: "C hears of 2a, and keeps it. C's work pays off: block 3, on 2b.",
      acts: { C: { temp: { chain: "1 2b 3", "also kept": "1 2a" }, why: "Block 2a arrives, as long as 2b, which C heard of first; C keeps it. Then C's work pays off: block 3 on top of 2b. C sends it out." } } },
    { note: "Block 3 makes the 2b chain the longest. A switches to it; B was already on it.",
      acts: { A: { temp: { chain: "1 2b 3", "also kept": "1 2a" } }, B: { temp: { chain: "1 2b 3" }, why: "Block 3 arrives, on top of 2b. B's chain is now three long." } } },
  ],
  msgs: [
    ["coin", "A", "made block 2a", 0, 1], ["coin", "B", "made block 2b", 0, 1],
    ["A", "B", "block(2a on 1)", 1, 2], ["A", "C", "block(2a on 1)", 1, 3],
    ["B", "A", "block(2b on 1)", 1, 2], ["B", "C", "block(2b on 1)", 1, 2],
    ["coin", "C", "made block 3", 2, 3],
    ["C", "A", "block(3 on 2b)", 3, 4], ["C", "B", "block(3 on 2b)", 3, 4],
  ],
},
"nakamoto-shallow": {
  nodes: { A: { init: nkPayInit }, B: { init: nkB }, M: { init: nkM } },
  steps: [{ note: "Every chain is one block long. M is about to write x." }, nkPay1, nkPay2,
    { note: "A acts on x. M is lucky and makes 2′ in secret.", acts: { A: { perm: { "acted on x": "yes" }, temp: { chain: "1 2", x: "in block 2" } },
      M: { temp: { "secret chain": "1 2′" }, why: "Block 2 arrives with x in it. M ignores it and keeps working in secret. Its work pays off: 2′, on top of 1.",
        isle: "Page 2 arrives with the {pottery}'s payment. The {pottery} ignores it and keeps working in secret. It finishes the sum: page 2′, after page 1." } } },
    { note: "M makes 3′. Its chain is now longer, and it sends both blocks out.", acts: { M: { temp: { chain: "1 2′ 3′", "secret chain": "none" }, why: "M is lucky again: 3′. Its secret chain is now longer than the honest one, so M sends out both blocks." } } },
    { note: "A and B switch to the longer chain. x is gone; what A did on the strength of it is not.",
      acts: { A: { temp: { chain: "1 2′ 3′", x: "gone" } }, B: { temp: { chain: "1 2′ 3′" }, why: "Blocks 2′ and 3′ arrive. That chain is longer, so B switches to it, as the rule says." } } },
  ],
  msgs: [...nkPayMsgs, ["B", "A", "block(2 on 1, holds x)", 2, 3], ["B", "M", "block(2 on 1, holds x)", 2, 3],
    ["coin", "M", "made block 2′", 2, 3], ["coin", "M", "made block 3′", 3, 4],
    ["M", "A", "blocks(2′ 3′ on 1)", 4, 5], ["M", "B", "blocks(2′ 3′ on 1)", 4, 5]],
},
"nakamoto-deep": {
  nodes: { A: { init: nkPayInit }, B: { init: nkB }, M: { init: nkM } },
  steps: [{ note: "Every chain is one block long. M is about to write x." }, nkPay1, nkPay2,
    { note: "A sees x one deep and waits. B makes block 3; M makes 2′ in secret.",
      acts: { A: { temp: { chain: "1 2", x: "in block 2, 1 deep" } }, B: { temp: { chain: "1 2 3" }, why: "B's work pays off again: block 3, on top of 2. B sends it out." },
              M: { temp: { "secret chain": "1 2′" }, why: "Block 2 arrives with x in it. M ignores it and keeps working in secret. Its work pays off: 2′, on top of 1.",
                isle: "Page 2 arrives with the {pottery}'s payment. The {pottery} ignores it and keeps working in secret. It finishes the sum: page 2′, after page 1." } } },
    { note: "A sees x two deep. M makes 3′ and sends its chain out, hoping to overtake.",
      acts: { A: { temp: { chain: "1 2 3", x: "2 deep" } }, M: { temp: { chain: "1 2′ 3′", "secret chain": "none" }, why: "M makes 3′. Its chain is as long as the honest one, and A is about to act on x, so M sends both blocks out, hoping to win the tie.",
                isle: "The {pottery} finishes page 3′. Its payment book is as long as the honest one, and the {fishery} is about to hand over the amphorae, so the {pottery} sends both pages out, hoping to win the tie." } } },
    { note: "M's chain is no longer than the one A and B already have, so they stay. B makes block 4.",
      acts: { A: { temp: { "also kept": "1 2′ 3′" } }, B: { temp: { chain: "1 2 3 4" }, why: "Blocks 2′ and 3′ arrive. That chain is no longer than B's, which it heard of first, so B stays. Its work pays off: block 4." } } },
    { note: "x is three deep. A acts on it.", acts: { A: { perm: { "acted on x": "yes" }, temp: { chain: "1 2 3 4", x: "3 deep" } } } },
  ],
  msgs: [...nkPayMsgs, ["B", "A", "block(2 on 1, holds x)", 2, 3], ["B", "M", "block(2 on 1, holds x)", 2, 3],
    ["coin", "B", "made block 3", 2, 3], ["coin", "M", "made block 2′", 2, 3],
    ["B", "A", "block(3 on 2)", 3, 4], ["coin", "M", "made block 3′", 3, 4],
    ["M", "A", "blocks(2′ 3′ on 1)", 4, 5], ["M", "B", "blocks(2′ 3′ on 1)", 4, 5], ["coin", "B", "made block 4", 4, 5],
    ["B", "A", "block(4 on 3)", 5, 6]],
},
});
Object.assign(TRACES, {
"chash-join": {
  nodes: { A: { init: { temp: { place: "20", keys: "13, 90" } } }, B: { init: { temp: { place: "50", keys: "33" } } }, C: { init: { temp: { place: "80", keys: "58, 72" } } }, D: { init: { temp: { place: "none", keys: "none" } } } },
  steps: [
    { note: "A at 20 holds 13 and 90 (going round past 99); B at 50 holds 33; C at 80 holds 58 and 72. D is about to join at 65." },
    { note: "D joins at 65, and tells the node after it, C.", acts: { D: { temp: { place: "65" }, why: "D joins the circle at 65. The node after it is C, which holds everything from 51 to 80; D tells C." } } },
    { note: "C hands D the keys from 51 to 65: just 58.", acts: { C: { temp: { keys: "72" } } } },
    { note: "D takes 58. A client asks C for 58, and is sent to D.",
      acts: { D: { temp: { keys: "58" }, why: "C hands over key 58, which now belongs to D." } } },
  ],
  msgs: [["D", "C", "joining at 65", 1, 2], ["C", "D", "keys(58)", 2, 3], ["outside", "C", "read key 58", 2, 3], ["C", "outside", "ask D", 3, 3]],
},
"chash-modulo": {
  nodes: { A: { init: { temp: { "my number": "0 of 3", keys: "33, 72, 90" } } }, B: { init: { temp: { "my number": "1 of 3", keys: "13, 58" } } }, C: { init: { temp: { "my number": "2 of 3", keys: "17, 41, 59" } } }, D: { init: { temp: { "my number": "none", keys: "none" } } } },
  steps: [
    { note: "Keys by remainder after dividing by 3: A has 33, 72, 90; B has 13, 58; C has 17, 41, 59. D is about to join." },
    { note: "D joins as number 3, and tells everyone.", acts: { D: { temp: { "my number": "3 of 4" }, why: "D joins as node number 3. Now keys are divided by 4, and D tells every node." } } },
    { note: "Everyone recounts by 4 and sends away what is no longer theirs.",
      acts: { A: { temp: { "my number": "0 of 4", keys: "72" }, why: "Divided by 4, 72 leaves 0 and stays; 33 leaves 1, for B; 90 leaves 2, for C." },
              B: { temp: { "my number": "1 of 4", keys: "13" }, why: "Divided by 4, 13 leaves 1 and stays; 58 leaves 2, for C." },
              C: { temp: { "my number": "2 of 4", keys: "none" } } } },
    { note: "The keys arrive. Of eight keys, six changed hands.",
      acts: { B: { temp: { keys: "13, 17, 41, 33" }, why: "Keys 17 and 41 arrive from C, and 33 from A. B now holds 13, 17, 33 and 41." },
              C: { temp: { keys: "90, 58" }, why: "Keys 90 from A and 58 from B arrive: under the new count they are C's." },
              D: { temp: { keys: "59" }, why: "Key 59 arrives from C: divided by 4 it leaves 3." } } },
  ],
  msgs: [["D", "A", "joining as number 3", 1, 2], ["D", "B", "joining as number 3", 1, 2], ["D", "C", "joining as number 3", 1, 2],
    ["A", "B", "keys(33)", 2, 3], ["A", "C", "keys(90)", 2, 3], ["B", "C", "keys(58)", 2, 3],
    ["C", "B", "keys(17, 41)", 2, 3], ["C", "D", "keys(59)", 2, 3]],
},
"chash-handoff": {
  nodes: { A: { init: { temp: { status: "down", keys: "13=x, 90" } } }, B: { init: { temp: { keys: "13=x, 33" } } }, C: { init: { temp: { keys: "58, 72", "kept for others": "none" } } } },
  steps: [
    { note: "Key 13 lives on A and B. A is down." },
    { note: "B takes a write of 13=y, stores it, and sends it to A. A is down; the message is lost.",
      acts: { B: { temp: { keys: "13=y, 33" }, why: "A client asks B to write 13=y. B stores it and sends a copy to A, the key's other node." } } },
    { note: "No answer from A. B sends the copy to the next healthy node, C, noting that it is A's.",
      acts: { B: { why: "A doesn't answer. The next healthy node round the circle is C, so B sends it the copy, with a note that it is A's." } } },
    { note: "C keeps it for A, and confirms.", acts: { C: { temp: { "kept for others": "13=y, for A" } } } },
    { note: "Two copies: B confirms the write. A comes back.",
      acts: { B: { why: "C confirms. With B's own, the write is on two nodes, so B tells the client it is done." }, A: { temp: { status: "up" }, why: "A is back up, with key 13 still at x." } } },
    { note: "C sees A answering, and sends it the copy." },
    { note: "A stores 13=y and confirms.", acts: { A: { temp: { keys: "13=y, 90" }, why: "C hands over the copy it kept: 13=y. A stores it and confirms." } } },
    { note: "C drops its copy. 13=y is on A and B.", acts: { C: { temp: { "kept for others": "none" } } } },
  ],
  msgs: [["outside", "B", "write 13=y", 0, 1], ["B", "A", "store(13=y)", 1, null, "lost"], ["timer", "B", "no answer from A", 1, 2],
    ["B", "C", "store(13=y, for A)", 2, 3], ["C", "B", "stored", 3, 4], ["B", "outside", "done(13=y)", 4, 4],
    ["timer", "C", "A answers again", 4, 5], ["C", "A", "store(13=y)", 5, 6], ["A", "C", "stored", 6, 7]],
},
});
const fpV = (acc) => ({ role: "voter", init: { perm: { promised: "1", accepted: acc } } });
const fpNodes = { Q: { role: "proposer", init: fpInit }, P: { role: "proposer", init: { perm: { "tried up to": "1", chosen: "x" } } }, A: fpV("(r1, x)"), B: fpV("(r1, x)"), C: fpV("none"), D: fpV("none") };
const fpWhy = { claim: v => `Q claims round 2, higher than any round ${v} has promised. ${v} promises to ignore older rounds, writes that down, and reports what it last accepted.`,
  accept: v => `Q proposes in round 2, and ${v} has promised nothing higher. ${v} accepts and writes it down.` };
Object.assign(TRACES, {
"fpaxos-overlap": {
  nodes: fpNodes,
  steps: [
    { note: "Round 1 is over: A and B accepted x, a phase-2 group of two, so x is chosen. Q knows nothing of it." },
    { note: "Q claims round 2 with B, C and D.", acts: { Q: { perm: { "tried up to": "2" }, temp: { wants: "y" } } } },
    { note: "B, C and D promise. B reports its vote for x.",
      acts: { B: { perm: { promised: "2" }, why: fpWhy.claim("B") }, C: { perm: { promised: "2" }, why: fpWhy.claim("C") }, D: { perm: { promised: "2" }, why: fpWhy.claim("D") } } },
    { note: "B's promise reaches Q.", acts: { Q: { temp: { "last votes": "B=r1 x" } } } },
    { note: "C's promise reaches Q.", acts: { Q: { temp: { "last votes": "B=r1 x; C=none" } } } },
    { note: "D's promise completes phase 1. Q must propose x, and asks C and D.", acts: { Q: { temp: { "last votes": "B=r1 x; C=none; D=none", proposing: "x" } } } },
    { note: "C and D accept x in round 2.",
      acts: { C: { perm: { accepted: "(r2, x)" }, why: fpWhy.accept("C") }, D: { perm: { accepted: "(r2, x)" }, why: fpWhy.accept("D") } } },
    { note: "Q has two acceptances: x is chosen, the same value as before.", acts: { Q: { perm: { chosen: "x" }, temp: { "accepted by": "C D" } } } },
  ],
  msgs: [
    ["outside", "Q", "get y chosen", 0, 1],
    ["Q", "B", "claim(r2)", 1, 2], ["Q", "C", "claim(r2)", 1, 2], ["Q", "D", "claim(r2)", 1, 2],
    ["B", "Q", "promise(r2, accepted (r1, x))", 2, 3], ["C", "Q", "promise(r2, accepted none)", 2, 4], ["D", "Q", "promise(r2, accepted none)", 2, 5],
    ["Q", "C", "propose(r2, x)", 5, 6], ["Q", "D", "propose(r2, x)", 5, 6],
    ["C", "Q", "accepted(r2)", 6, 7], ["D", "Q", "accepted(r2)", 6, 7],
  ],
},
"fpaxos-disjoint": {
  nodes: fpNodes,
  steps: [
    { note: "Round 1 is over: A and B accepted x, a phase-2 group of two, so x is chosen. Q knows nothing of it." },
    { note: "Q claims round 2 with C and D only.", acts: { Q: { perm: { "tried up to": "2" }, temp: { wants: "y" } } } },
    { note: "C and D promise, having accepted nothing.",
      acts: { C: { perm: { promised: "2" }, why: fpWhy.claim("C") }, D: { perm: { promised: "2" }, why: fpWhy.claim("D") } } },
    { note: "Q has two promises and no reported vote. It proposes y.", acts: { Q: { temp: { "last votes": "C=none; D=none", proposing: "y" } } } },
    { note: "C and D accept y in round 2.",
      acts: { C: { perm: { accepted: "(r2, y)" }, why: fpWhy.accept("C") }, D: { perm: { accepted: "(r2, y)" }, why: fpWhy.accept("D") } } },
    { note: "Q takes y as chosen. P took x. Two values are chosen.", acts: { Q: { perm: { chosen: "y" }, temp: { "accepted by": "C D" } } } },
  ],
  msgs: [
    ["outside", "Q", "get y chosen", 0, 1],
    ["Q", "C", "claim(r2)", 1, 2], ["Q", "D", "claim(r2)", 1, 2],
    ["C", "Q", "promise(r2, accepted none)", 2, 3], ["D", "Q", "promise(r2, accepted none)", 2, 3],
    ["Q", "C", "propose(r2, y)", 3, 4], ["Q", "D", "propose(r2, y)", 3, 4],
    ["C", "Q", "accepted(r2)", 4, 5], ["D", "Q", "accepted(r2)", 4, 5],
  ],
},
});
const crHB = { perm: { value: "x" }, temp: { "sent, not yet acked": "none" } };
Object.assign(TRACES, {
"chain-tail": {
  nodes: { A: { role: "head", init: crHB }, B: { init: crHB }, C: { role: "tail", init: { perm: { value: "x" } } } },
  steps: [
    { note: "A chain: A, the head; B; C, the tail. All hold x." },
    { note: "A client asks the head to write y. A applies it and passes it down.",
      acts: { A: { perm: { value: "y" }, temp: { "sent, not yet acked": "1: y" }, why: "A client asks A, the head, to write y. A applies it, notes it as sent, and passes it to B." } } },
    { note: "B applies y and passes it down.",
      acts: { B: { perm: { value: "y" }, temp: { "sent, not yet acked": "1: y" }, why: "Update 1 arrives from A. B applies it, notes it as sent, and passes it to C. It answers nobody." } } },
    { note: "C, the tail, applies y, tells the client it is done, and acknowledges up the chain.", acts: { C: { perm: { value: "y" } } } },
    { note: "B strikes update 1 and passes the acknowledgement up. A client reads at the tail and gets y.",
      acts: { B: { temp: { "sent, not yet acked": "none" }, why: "The tail acknowledges update 1. B strikes it from its list and passes the acknowledgement to A." } } },
    { note: "A strikes update 1.", acts: { A: { temp: { "sent, not yet acked": "none" }, why: "The acknowledgement for update 1 arrives. A strikes it from its list." } } },
  ],
  msgs: [
    ["outside", "A", "write y", 0, 1], ["A", "B", "update(1: y)", 1, 2], ["B", "C", "update(1: y)", 2, 3],
    ["C", "outside", "done(y)", 3, 3], ["C", "B", "ack(1)", 3, 4], ["B", "A", "ack(1)", 4, 5],
    ["outside", "C", "read the value", 3, 4], ["C", "outside", "answer(y)", 4, 4],
  ],
},
"chain-anynode": {
  nodes: { A: { role: "head", init: crHB }, B: { init: crHB }, C: { role: "tail", init: { perm: { value: "x" } } } },
  steps: [
    { note: "A chain: A, the head; B; C, the tail. All hold x. Under this rule any node answers reads." },
    { note: "A client asks the head to write y. A applies it and passes it down.", acts: { A: { perm: { value: "y" }, temp: { "sent, not yet acked": "1: y" } } } },
    { note: "A answers a read with y. B applies y and passes it down; the link to C is slow.",
      acts: { B: { perm: { value: "y" }, temp: { "sent, not yet acked": "1: y" }, why: "Update 1 arrives from A. B applies it, notes it as sent, and passes it to C." } } },
    { note: "Another client reads at C, which still has x.", acts: { C: { why: "A client asks C for the value. The update hasn't reached C yet, so it answers x, after A answered y." } } },
    { note: "The update reaches C at last.", acts: { C: { perm: { value: "y" }, why: "Update 1 arrives from B. C applies it." } } },
  ],
  msgs: [
    ["outside", "A", "write y", 0, 1], ["A", "B", "update(1: y)", 1, 2],
    ["outside", "A", "read the value", 1, 2], ["A", "outside", "answer(y)", 2, 2],
    ["B", "C", "update(1: y)", 2, 4],
    ["outside", "C", "read the value", 2, 3], ["C", "outside", "answer(x)", 3, 3],
  ],
},
"chain-middle": {
  nodes: { A: { role: "head", init: { perm: { value: "z" }, temp: { next: "B", "sent, not yet acked": "2: z" } } },
    B: { init: { perm: { value: "z" }, temp: { status: "stopped" } } }, C: { role: "tail", init: { perm: { value: "y" }, temp: { before: "B" } } },
    M: { role: "keeps the chain's list", init: { temp: { chain: "A B C" } } } },
  steps: [
    { note: "A passed update 2, z, to B, which stopped before passing it on. C, the tail, still holds y." },
    { note: "M notices B is gone. It tells C first, then A.",
      acts: { M: { temp: { chain: "A C" }, why: "B has stopped. M takes it off the list, and tells C, the node after B, before A, the node before it." } } },
    { note: "C takes A as the node before it.", acts: { C: { temp: { before: "A" }, why: "M says the node before C is now A." } } },
    { note: "A takes C as the node after it, and first resends everything on its list.", acts: { A: { temp: { next: "C" } } } },
    { note: "C applies z, tells the client it is done, and acknowledges.", acts: { C: { perm: { value: "z" }, why: "Update 2 arrives from A. C, the tail, applies it, tells the client it is done, and acknowledges." } } },
    { note: "A strikes update 2 from its list.", acts: { A: { temp: { "sent, not yet acked": "none" } } } },
  ],
  msgs: [
    ["timer", "M", "no word from B", 0, 1],
    ["M", "C", "the node before you is now A", 1, 2], ["M", "A", "your next node is now C", 1, 3],
    ["A", "C", "update(2: z)", 3, 4], ["C", "outside", "done(z)", 4, 4], ["C", "A", "ack(2)", 4, 5],
  ],
},
});
Object.assign(TRACES, {
"truetime-wait": {
  nodes: { A: { init: { perm: { a: "x" } } }, B: { init: { perm: { b: "x" } } } },
  steps: [
    { note: "True time 20. A's clock reads 24, four ahead; B's clock is four behind. Each says it may be off by 5." },
    { note: "A stamps a=y with 29, the latest the time could be, and waits.", acts: { A: { temp: { pending: "a=y @29", "true time": "19 to 29" } } } },
    { note: "True time 31: A's clock reads 35, so the time is surely past 29. A applies y and reports it done." , acts: { A: { perm: { a: "y @29" }, temp: { pending: "none", "true time": "30 to 40" } } } },
    { note: "The client then writes b=z at B. B's clock reads 27, so the time could be up to 32. B stamps z with 32, after y's 29.",
      acts: { B: { temp: { pending: "b=z @32", "true time": "22 to 32" }, why: "A client asks B to write b = z. B's clock reads 27, so the true time is somewhere from 22 to 32. B stamps the write 32, the latest it could be, and waits." } } },
    { note: "B's clock passes 37; 32 is surely past. B applies z and reports it done.",
      acts: { B: { perm: { b: "z @32" }, temp: { pending: "none", "true time": "33 to 43" }, why: "B's clock reads 38: the true time is at least 33, so 32 is surely past. B applies the write and reports it done." } } },
  ],
  msgs: [
    ["outside", "A", "write a=y", 0, 1], ["timer", "A", "clock reads 35", 1, 2], ["A", "outside", "done(a=y)", 2, 2],
    ["outside", "B", "write b=z", 2, 3], ["timer", "B", "clock reads 38", 3, 4], ["B", "outside", "done(b=z)", 4, 4],
  ],
},
"truetime-nowait": {
  nodes: { A: { init: { perm: { a: "x" } } }, B: { init: { perm: { b: "x" } } } },
  steps: [
    { note: "True time 20. A's clock reads 24, four ahead; B's clock is four behind." },
    { note: "A stamps a=y with its clock's 24, applies it and reports it done.", acts: { A: { perm: { a: "y @24" } } } },
    { note: "True time 21. The client then writes b=z at B, whose clock reads 17. B stamps it 17 and reports it done.",
      acts: { B: { perm: { b: "z @17" }, why: "A client asks B to write b = z. B's clock reads 17, so B stamps the write 17, applies it and reports it done." } } },
    { note: "A reader asks both for their values as of 20. B has z, stamped 17. A's y is stamped 24, so A answers x.",
      acts: { B: { why: "A reader asks for b as of 20. The write of z is stamped 17, no later than 20, so B answers z." } } },
  ],
  msgs: [
    ["outside", "A", "write a=y", 0, 1], ["A", "outside", "done(a=y)", 1, 1],
    ["outside", "B", "write b=z", 1, 2], ["B", "outside", "done(b=z)", 2, 2],
    ["outside", "A", "read a as of 20", 2, 3], ["A", "outside", "answer(a=x)", 3, 3],
    ["outside", "B", "read b as of 20", 2, 3], ["B", "outside", "answer(b=z)", 3, 3],
  ],
},
});
