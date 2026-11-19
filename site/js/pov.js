// ---------- whose eyes: a scene told from inside any of its nodes ----------
// A scene is told from inside its narrator (`who`). Where it has a global trace (js/data/traces.js), tabs over the stepper
// tell the same scene from inside any other node it involves: that node's own steps, what reaches it, what it keeps, what
// it sends. Everything else on the page follows: the picture marks that node, the panel and the stepper are its steps.
// Out of its sight, as ever, is the world view in a dashed frame: what the others did between its steps.
// pov is the node chosen, or null for the narrator. It resets when another page opens, and holds across the two tellings.
let pov = null;
const traceOf = it => it && it.s && !it.pov ? TRACES[it.key] || null : null;
// The scene as it is being viewed: the scene itself for its narrator; for another node, a scene of the same shape built
// from the trace. Its key, id and name stay the scene's, so its point, its sources and its title are found as ever.
function viewOf(it) {
  const T = traceOf(it); if (!T || !pov || pov === it.s.who || !T.nodes[pov]) return it;
  const X = pov, s = it.s, I = isleOf(it.p), mine = actSteps(T, s.who), steps = actSteps(T, X), O = ovOf(it);
  const others = traceNodes(T).filter(Y => Y !== X), role = Y => T.nodes[Y].role;
  // the others, by role: "proposer P; voters A, C", or just "B, C" where no node has a role
  const roles = [...new Set(others.map(role))];
  const peers = roles.every(r => !r) ? others.join(", ") : roles.map(r => { const ls = others.filter(Y => role(Y) === r); return (r ? r + (ls.length > 1 ? "s " : " ") : "") + ls.join(", "); }).join("; ");
  // a step's account, as the step panel tells it: the node's own `why`; the narrator's is the scene's prose (the telling's, in the Allegory)
  const told = (Y, k) => {
    if (Y === s.who) { const i = mine.indexOf(k) + 1; return O && O.prose ? mk(O.prose[i] || "") : nodeText(s.prose[i] || "", s); }
    // the Allegory's own account where the trace gives one (with the telling's {places}); else the plain one, with the telling's words swapped in
    const a = T.steps[k].acts && T.steps[k].acts[Y]; if (I && a && a.isle) return mk(ALLEGORY.fill(a.isle));
    return a && a.why ? nodeText(lexT(a.why, I), { who: X, peers }) : "";
  };
  // what the others did out of X's sight, from just after its last step up to this one
  const aside = (from, to) => { const out = []; for (let k = from + 1; k <= to; k++) others.forEach(Y => { if (actAt(T, Y, k)) { const t = told(Y, k); if (t) out.push(t); } }); return out.join(" "); };
  const say = ["", ...steps.map(k => told(X, k))], asides = ["", ...steps.map((k, i) => aside(i ? steps[i - 1] : 0, k))];
  // the scene's phases count the narrator's steps: put them on the global clock, then on X's steps; two that land on the
  // same step of X's keep only the later
  const ph = (s.phases || []).map(([from, name, why], i) => { const g = from === 0 ? 0 : mine[from - 1]; return [g ? steps.filter(k => k < g).length + 1 : 0, name, why, O && O.phases ? O.phases[i] : ""]; })
    .filter(([f], i, all) => f <= steps.length && !(all[i + 1] && all[i + 1][0] === f));
  const v = { ...s, who: X, role: role(X), peers, init: T.nodes[X].init || {}, rows: traceRows(T, X), prose: [], twin: undefined, note: "", outside: "", phases: ph.map(p => p.slice(0, 3)) };
  return { ...it, s: v, pov: X, told: { say, asides, phases: ph }, steps };
}
// Whose eyes the open scene is seen through, for the telling's message words (an order is for the goods of the house it goes to).
const msgMe = () => { const it = byKey(sel); return it ? viewOf(it).s.who : undefined; };
// The global step a view's step t stands for (its own t-th step; 0 the start; past its last, the end of the scene).
const globalStep = (it, T, t) => { const st = actSteps(T, it.s.who); return t <= 0 ? 0 : t > st.length ? traceLen(T) + 1 : st[t - 1]; };
// Switching eyes keeps the moment: the new node's step is its last one at or before that moment.
function setPov(X) {
  const it = byKey(sel), T = traceOf(it); if (!T) return;
  const g = globalStep(viewOf(it), T, stageStep);
  pov = X === it.s.who ? null : X;
  const st = actSteps(T, X);
  stageStep = g > traceLen(T) ? st.length + 1 : st.filter(k => k <= g).length;
  render();
  const b = document.querySelector(`.pov [data-pov="${X}"]`); if (b) b.focus();
}
// The tabs: every node of the trace, the narrator first, each with its role in the current telling.
function povHTML(it) {
  const base = byKey(it.key), T = traceOf(base); if (!T || cmp) return "";      // beside a twin, both scenes are as told
  const I = isleOf(it.p), cur = it.s.who, ids = [base.s.who, ...traceNodes(T).filter(Y => Y !== base.s.who)];
  const name = Y => I ? (nmOf(I, Y) ? esc(nmOf(I, Y)) : esc(roleOf(I, Y))) : esc(T.nodes[Y].role || "node");
  return `<div class="pov" role="tablist" aria-label="Whose eyes">${ids.map(Y => `<button type="button" role="tab" data-pov="${Y}" aria-selected="${Y === cur}"${Y === cur ? "" : ` tabindex="-1"`} title="${Y === base.s.who ? "The scene as told" : "The same scene, from inside " + Y}"><b>${nmOf(I, Y) ? "" : Y}</b><span>${name(Y)}</span>${Y === base.s.who ? `<i class="told" aria-label="the narrator">told</i>` : ""}</button>`).join("")}</div>`;
}
// arrow keys move along the tabs, as tabs do
document.addEventListener("keydown", e => {
  const b = e.target.closest && e.target.closest(".pov [data-pov]"); if (!b || (e.key !== "ArrowLeft" && e.key !== "ArrowRight")) return;
  e.preventDefault(); e.stopPropagation();
  const all = [...b.parentNode.children], n = all[(all.indexOf(b) + (e.key === "ArrowRight" ? 1 : all.length - 1)) % all.length];
  setPov(n.dataset.pov);
}, true);
