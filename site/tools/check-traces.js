// Checks every global trace (site/js/data/traces.js) against the scene it belongs to.
// Usage: node site/tools/check-traces.js     (exit 1 on any problem)
//
// 1. Projected onto the scene's narrator (`who`), the trace gives back the scene's init and rows exactly:
//    the same state changes, the same arrivals and departures in the same order, the same lost marks.
// 2. Its messages are sound: senders and receivers are nodes of the trace (or outside/timer as senders),
//    nothing arrives before it leaves, and every step number lies inside the trace.
// 3. Every node of the trace has a place on the scene's stage (TELL[paper].stage), so every world can show it.
// 4. Every step of a node other than the narrator has its own account (`why`): it is that node's telling of the step.
const fs = require("fs"), path = require("path"), vm = require("vm");
const root = path.join(__dirname, "..", "..");
const ctx = vm.createContext({ console });
const load = f => vm.runInContext(fs.readFileSync(path.join(root, f), "utf8"), ctx, { filename: f });
["site/js/data/scenes.js", "site/js/rows.js", "site/js/data/papers.js", "site/js/data/telling-text.js", "site/js/data/scenes-extra.js", "site/js/data/scenes-more.js",
 "site/js/data/telling.js", "site/js/data/telling-more.js", "site/js/data/plain.js", "site/js/data/traces.js", "site/js/data/traces-more.js", "site/js/trace.js"].forEach(load);
const get = n => vm.runInContext(n, ctx);
const PAPERS = get("PAPERS"), TELL = get("TELL"), TRACES = get("TRACES"), PLAIN = get("PLAIN");
const project = get("traceRows"), traceLen = get("traceLen"), actSteps = get("actSteps");

const bad = [], PSEUDO = new Set(["outside", "timer", "nothing", "coin"]);
const norm = r => JSON.stringify({ perm: r.perm || {}, temp: r.temp || {}, recv: r.recv || [], sent: (r.sent || []).map(m => m[2] === "lost" ? m.slice(0, 3) : m.slice(0, 2)) });
for (const [key, T] of Object.entries(TRACES)) {
  const p = PAPERS.find(p => key.startsWith(p.id + "-")), s = p && p.scenes.find(s => key === p.id + "-" + s.id);
  if (!s) { bad.push(`${key}: no such scene`); continue; }
  const N = traceLen(T), nodes = Object.keys(T.nodes);
  if (!T.nodes[s.who]) { bad.push(`${key}: the narrator ${s.who} is not among the trace's nodes`); continue; }
  // 1. the narrator's view
  const init = T.nodes[s.who].init || {};
  if (JSON.stringify({ perm: init.perm || {}, temp: init.temp || {} }) !== JSON.stringify({ perm: s.init.perm || {}, temp: s.init.temp || {} }))
    bad.push(`${key}: ${s.who}'s starting state differs from the scene's init`);
  const got = project(T, s.who);
  if (got.length !== s.rows.length) bad.push(`${key}: ${s.who} acts ${got.length} times in the trace, but the scene has ${s.rows.length} rows`);
  for (let i = 0; i < Math.min(got.length, s.rows.length); i++)
    if (norm(got[i]) !== norm(s.rows[i])) bad.push(`${key}: ${s.who}'s step ${i + 1} differs\n    scene: ${norm(s.rows[i])}\n    trace: ${norm(got[i])}`);
  // 2. the messages
  T.msgs.forEach((m, i) => {
    const [from, to, text, sent, arr, flag] = m, at = `${key}: message ${i} (${from}→${to} ${text})`;
    if (!T.nodes[from] && !PSEUDO.has(from)) bad.push(`${at}: unknown sender`);
    if (!T.nodes[to] && to !== "outside") bad.push(`${at}: unknown receiver`);
    if (PSEUDO.has(from) && to === "outside") bad.push(`${at}: nothing goes from outside to outside`);
    if (!(sent >= 0 && sent <= N)) bad.push(`${at}: leaves at step ${sent}, outside 0..${N}`);
    if (arr !== null && to !== "outside" && !(arr > sent && arr <= N)) bad.push(`${at}: arrives at step ${arr}, not after it leaves or past the end`);
    if (flag && flag !== "lost") bad.push(`${at}: unknown flag ${flag}`);
    if (PSEUDO.has(from) && arr === null) bad.push(`${at}: an outside message, a timer, a coin or an empty step must arrive`);
    if (to === "outside" && arr !== sent) bad.push(`${at}: a reply to outside leaves the scene at once: arrives must equal sent`);
  });
  T.steps.forEach((st, k) => Object.keys(st.acts || {}).forEach(X => { if (!T.nodes[X]) bad.push(`${key}: step ${k} has an act for unknown node ${X}`); }));
  if (T.steps[0].acts) bad.push(`${key}: step 0 is the start and has no acts`);
  // 3. the stage
  const S = TELL[p.id] && TELL[p.id].stage, G = S && PLAIN[S.view === "siege" ? "siege" : "city"];
  if (!S) bad.push(`${key}: ${p.id} has no stage`);
  else nodes.forEach(X => { if (!S[X] || !G.places[S[X]]) bad.push(`${key}: node ${X} has no place on the stage`); });
  // (a stage with no client place is fine: the page shows a request from outside at the node it reaches)
  // 4. the other nodes' accounts
  nodes.filter(X => X !== s.who).forEach(X => actSteps(T, X).forEach(k => { const a = T.steps[k].acts && T.steps[k].acts[X];
    if (!a || !a.why) bad.push(`${key}: ${X} acts at step ${k} but has no \`why\` to tell it`); }));
}
if (bad.length) { console.log(bad.join("\n")); process.exit(1); }
console.log(`ok: ${Object.keys(TRACES).length} trace(s) match their scenes`);
