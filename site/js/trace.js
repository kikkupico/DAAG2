// ---------- global traces: a scene seen from any of its nodes ----------
// A scene is told from inside one node, its narrator (`who`). Where the scene has a global trace (js/data/traces.js: every
// node's state at every step, and when each message leaves and arrives), it can be told from inside any of its nodes:
// the trace, projected onto that node, gives that node's own rows, in a scene's shape. Plain functions with no DOM, shared
// by the page and by tools/check-traces.js. Needs applyDelta (rows.js).
const traceLen = T => T.steps.length - 1;                          // steps 1..N; step 0 is the start
const traceNodes = T => Object.keys(T.nodes);
const isLost = m => m[5] === "lost";

// What node X does at global step k: its state deltas, what reaches it and what leaves it (in the order of T.msgs), its account.
function actAt(T, X, k) {
  const a = (T.steps[k] && T.steps[k].acts && T.steps[k].acts[X]) || null;
  const recv = T.msgs.filter(m => m[1] === X && m[4] === k && !isLost(m));
  const sent = T.msgs.filter(m => m[0] === X && m[3] === k);
  if (!a && !recv.length && !sent.length) return null;
  return { perm: (a && a.perm) || null, temp: (a && a.temp) || null, why: (a && a.why) || "", recv, sent };
}
// The global steps at which X acts, in order. The i-th of them is X's own step i+1.
const actSteps = (T, X) => T.steps.map((_, k) => k).filter(k => k > 0 && actAt(T, X, k));

// X's rows: the trace seen from inside X, in the shape of a scene's rows (js/data/scenes.js).
function traceRows(T, X) {
  return actSteps(T, X).map(k => {
    const a = actAt(T, X, k), r = {};
    if (a.perm) r.perm = a.perm;
    if (a.temp) r.temp = a.temp;
    if (a.recv.length) r.recv = a.recv.map(m => [m[0], m[2]]);
    if (a.sent.length) r.sent = a.sent.map(m => isLost(m) ? [m[1], m[2], "lost"] : [m[1], m[2]]);
    return r;
  });
}
