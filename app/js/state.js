// ---------- state, and the two registers ----------
let sel = "map", lens = "inside", cmp = false, reg = "isle";
const haz = new Set();
let bg = "rendered";            // the Allegory's background: the frame rendered in Blender (or ?bg=drawn for the drawn city)
try { if (localStorage.getItem("lens") === "outside") lens = "outside"; if (localStorage.getItem("reg") === "plain") reg = "plain"; } catch (e) {}
{ const q = new URLSearchParams(location.search).get("bg"); if (q === "rendered" || q === "3d") bg = "rendered"; else if (q === "drawn") bg = "drawn"; }

const UI = {
  plain: {
    thesis: "Sixteen results from distributed computing, each told from inside a single node. A node knows what it holds and what arrives. Everything else is a guess.",
    title: "Distributed Algorithms, One Node at a Time",
    map: "Overview", arrives: "Arrives", leaves: "Leaves", perm: "permanent", temp: "temporary",
    permL: "permanent: handed to a replacement", tempL: "temporary: ends with the node",
    outBtn: "Global view", goOut: "Turn on global view", goIn: "Turn it off", seen: "Global view", point: "The point",
    endStep: "The end: what the node could know, and what happened",
    kept: "State", noneIn: "nothing arrives", noneOut: "nothing leaves",
    client: "client", timer: "timer", nothing: "no message", coin: "coin", inplay: "In play", pick: "pick any to find scenes that share them", unit: ["paper", "papers", "in"],
    strip: ["permanent state changes", "temporary only", "no change", "something arrives", "something leaves"],
    same: "From inside, the two scenes are identical at every step. Turn on global view to see what separates them.",
    differ0: "The two scenes differ from the start: the node keeps different things.", until: d => `The two scenes are identical from inside until step ${d}.`,
  },
  isle: {
    thesis: "Paxos has no assembly hall. Its merchants, part-time legislators, soldiers and scholars each work from their own place, and all they know of one another comes by courier.",
    title: "Distributed Algorithms of Ancient Greece",
    map: "Bird's Eye View", arrives: "Arrives", leaves: "Leaves", perm: "in the ledger", temp: "on the slate",
    permL: "ledger: passes to a successor", tempL: "slate: wiped when its owner goes",
    outBtn: "World view", goOut: "Turn on world view", goIn: "Turn it off", seen: "World view", point: "The point",
    endStep: "The end: what could be known, and what happened",
    kept: "Ledger and slate", noneIn: "no courier arrives", noneOut: "no courier leaves",
    client: "citizen", timer: "hourglass", nothing: "no courier", coin: "tossed coin", inplay: "In play", pick: "pick any to find scenes that share them", unit: ["result", "results", "in"],
    strip: ["the ledger changes", "slate only", "no change", "a courier arrives", "a courier leaves"],
    same: "From inside, the two scenes are identical at every step. Turn on world view to see what separates them.",
    differ0: "The two scenes differ from the start: different things are kept.", until: d => `The two scenes are identical from inside until step ${d}.`,
  },
};
const U = () => UI[reg];
const isleOf = p => reg === "isle" ? TELL[p.id] : null;
const ovOf = it => { const I = isleOf(it.p); return I ? I.scenes[it.s.id] : null; };
const nameOf = it => { const O = ovOf(it); return (O && O.name) || it.s.name; };
const paperName = p => p.name;
const roleOf = (I, l) => (I.roles && I.roles[l]) || I.role;
const cap = t => t.charAt(0).toUpperCase() + t.slice(1);
const ND = l => `<span class="nd">${l}</span>`;
// Where the telling names the nodes (the merchants' three businesses), the name stands in for the letter.
const nmOf = (I, l) => (I && I.names && I.names[l]) || null;
const clientOf = (I, text) => ((I.clientFor || []).find(([re]) => re.test(text)) || [0, I.client])[1];
// Message and state text, with the telling's few nouns for things swapped in.
function lexT(text, I) {
  if (!I) return text;
  let t = text;
  for (const [a, b] of I.lex) t = typeof a === "string" ? t.split(a).join(b) : t.replace(a, b);
  return t;
}

