// ---------- comparing two results ----------
// A comparison's key is "cmp" (nothing chosen yet) or "cmp=flp~cap". Two results are set side by side: what each is after and
// assumes, then their scenes in pairs, and for any pair the two timelines lined up by the kind of step, not by its number.
const isVs = k => k === "cmp" || /^cmp=/.test(k);
const vsIds = k => { const [a = "", b = ""] = (k.split("=")[1] || "").split("~"); return [a, b]; };
const vsOf = k => vsIds(k).map(id => PAPERS.find(p => p.id === id) || null);
const vsKey = (a, b) => `cmp=${a || ""}~${b || ""}`;
const vsValid = k => isVs(k) && (k === "cmp" || vsIds(k).every((id, i, ids) => !id || (PAPERS.some(p => p.id === id) && ids.indexOf(id) === i)));
const edgeOf = (a, b) => MAP_EDGES.find(([x, y]) => (x === a && y === b) || (x === b && y === a));
const pById = id => PAPERS.find(p => p.id === id);
const scenesOf = p => p.scenes.map(s => byKey(`${p.id}-${s.id}`));

// Which of B's scenes sits beside each of A's: one with the same outcome if there is one, else the next in order.
// A reader's own choice for a row (vsPick) wins. B's scenes that end up beside nothing get rows of their own.
const vsPick = {}, vsOpen = new Set();
let vsSeen = "";
function pairsOf(pa, pb) {
  const A = scenesOf(pa), B = scenesOf(pb), free = new Set(B), auto = new Map();
  A.forEach(a => { const b = B.find(x => free.has(x) && x.oc === a.oc); if (b) { auto.set(a, b); free.delete(b); } });
  A.forEach(a => { if (!auto.has(a) && free.size) { const b = B.find(x => free.has(x)); auto.set(a, b); free.delete(b); } });
  const pick = vsPick[vsKey(pa.id, pb.id)] || {};
  const rows = A.map(a => [a, a.key in pick ? byKey(pick[a.key]) || null : auto.get(a) || null]);
  const used = new Set(rows.map(r => r[1]));
  return [...rows, ...B.filter(b => !used.has(b)).map(b => [null, b])];
}

// The kinds of thing a step can be, told from inside: what arrived, and what the node did about it.
const KINDS = [
  ["asked", "is asked", "is asked", "A request arrives from outside.", "Someone comes asking."],
  ["hears", "hears from a peer", "a courier arrives", "A message arrives from another node.", "A courier arrives from one of the others."],
  ["silence", "nothing arrives", "no courier comes", "No message arrives: an empty step, or a timer fires.", "No courier comes: an empty step, or the hourglass runs out."],
  ["sends", "sends to peers", "sends couriers", "The node sends a message to another node.", "A courier is sent to one of the others."],
  ["commits", "commits itself", "commits", "The node does something it cannot take back: it writes to permanent state, or gives an answer.", "Something that cannot be taken back: a line in the ledger, or an answer given."],
];
const kindName = k => { const x = KINDS.find(y => y[0] === k); return reg === "isle" ? x[2] : x[1]; };
function kindsOf(r) {
  if (!r.t) return [];
  const k = [], peer = m => !PSEUDO.has(m[0]);
  if (r.recv.some(m => m[0] === "outside")) k.push("asked");
  if (r.recv.some(peer)) k.push("hears");
  if (r.recv.some(m => m[0] === "timer" || m[0] === "nothing")) k.push("silence");
  if (r.sent.some(peer)) k.push("sends");
  if (r.sent.some(m => m[0] === "outside") || JSON.stringify(r.perm) !== JSON.stringify(r.prevPerm)) k.push("commits");
  return k;
}
// Line two scenes' steps up so that as many kinds as possible sit beside the same kind, keeping each scene's order.
// A step beside nothing has no counterpart in the other scene. Returns rows of [step or null, step or null], steps from 1.
function alignSteps(A, B) {
  const n = A.length, m = B.length, S = Array.from({ length: n + 2 }, () => Array(m + 2).fill(0));
  const sc = (i, j) => A[i].filter(k => B[j].includes(k)).length;
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) { const s = sc(i, j); S[i][j] = Math.max(S[i + 1][j], S[i][j + 1], s ? s + S[i + 1][j + 1] : 0); }
  const rows = []; let i = 0, j = 0;
  while (i < n || j < m) {
    const s = i < n && j < m ? sc(i, j) : 0;
    if (s && S[i][j] === s + S[i + 1][j + 1]) rows.push([++i, ++j]);
    else if (i < n && (j >= m || S[i][j] === S[i + 1][j])) rows.push([++i, null]);
    else rows.push([null, ++j]);
  }
  return rows;
}

// One dot per step, as in the stepper, but only to look at.
function miniStrip(it) {
  const rows = buildRows(it.s), chg = (a, b) => JSON.stringify(a) !== JSON.stringify(b);
  const cls = r => (r.t && chg(r.perm, r.prevPerm) ? "p" : r.t && chg(r.temp, r.prevTemp) ? "t" : "n") + (r.recv.some(m => m[0] !== "nothing") ? " r" : "") + (r.sent.length ? " s" : "");
  return `<span class="dots mini" aria-hidden="true">${rows.map(r => `<i class="sd ${cls(r)}">${r.t}</i>`).join("")}<i class="sd fin"><svg width="10" height="10" viewBox="0 0 12 12">${OC[it.oc]}</svg></i></span>`;
}

function pickerHTML(side, cur, other) {
  const opt = p => `<option value="${p.id}"${cur === p ? " selected" : ""}${other === p ? " disabled" : ""}>${esc(paperName(p))}</option>`;
  return `<select class="pick" data-vs="${side}" aria-label="${side === "a" ? "First" : "Second"} result to compare"><option value=""${cur ? "" : " selected"}>Choose a ${U().unit[0]}…</option>${CHAPTERS.map(([name, ids]) => `<optgroup label="${esc(name)}">${ids.map(pById).map(opt).join("")}</optgroup>`).join("")}</select>`;
}
// Pairs the map already joins with an arrow: each comes with a sentence saying how the second answers the first.
function linkedHTML(only) {
  const es = MAP_EDGES.filter(([a, b]) => !only || a === only.id || b === only.id);
  if (!es.length) return "";
  return `<section class="sect"><p class="label">${only ? `Linked to ${esc(paperName(only))} on the map` : "Pairs the map already links"}</p><ul class="vlinks">${es.map(([a, b, l]) =>
    `<li><button type="button" data-key="${vsKey(a, b)}"><span class="t">${esc(paperName(pById(a)))} <span aria-hidden="true">→</span><span class="sr">and</span> ${esc(paperName(pById(b)))}</span><span class="d">${esc(l)}</span></button></li>`).join("")}</ul></section>`;
}

// The two setups, fact by fact.
function castOf(p) {
  const xs = scenesOf(p), lines = xs.map(castHTML), same = lines.every(l => l === lines[0]);
  if (same) return `<p>${lines[0]}</p>`;
  const seen = new Map(); xs.forEach((x, i) => { if (!seen.has(lines[i])) seen.set(lines[i], []); seen.get(lines[i]).push(nameOf(x)); });
  return [...seen].map(([l, names]) => `<p>${l} <span class="in-s">(${esc(names.join("; "))})</span></p>`).join("");
}
function setupHTML(pa, pb) {
  const ps = [pa, pb], Is = ps.map(isleOf), fr = ps.map((p, i) => (Is[i] && Is[i].frame) || p.frame);
  const tags = ps.map(tagsOf), both = h => tags[0].includes(h) && tags[1].includes(h);
  const hz = i => { const mine = HAZARDS.filter(([id]) => tags[i].includes(id));
    return mine.length ? `<ul class="hz">${mine.map(([id, plain, isle]) => `<li${both(id) ? ` class="both"` : ""}>${isle_(plain, isle)}${both(id) ? `<span class="sr"> (in both)</span>` : ""}</li>`).join("")}</ul>` : `<p class="none">none of the six</p>`; };
  const shared = HAZARDS.filter(([id]) => both(id)).length;
  const rows = [
    ...(Is[0] && Is[1] ? [["Told among", i => `<p><b>${HAT[Is[i].hat][0]}.</b> ${esc(HAT[Is[i].hat][1])}</p>`]] : []),
    ["The goal", i => `<p>${esc(fr[i].goal)}</p>`], ["What is shared", i => `<p>${esc(fr[i].shared)}</p>`], ["What it assumes", i => `<p>${esc(fr[i].assumes)}</p>`],
    ["Cast", i => castOf(ps[i])],
    [U().inplay, hz, shared ? "Filled: in play in both." : "Nothing in play in both."],
  ];
  return `<section class="sect"><p class="label">The two setups</p><div class="vt" role="table">
    <div class="vr vh" role="row"><span role="columnheader" class="sr">Fact</span>${ps.map(p => `<div role="columnheader"><button type="button" data-key="${p.id}">${esc(paperName(p))}</button><small>${esc(p.year)}</small></div>`).join("")}</div>
    ${rows.map(([label, f, foot]) => `<div class="vr" role="row"><div class="label" role="rowheader">${label}${foot ? `<small>${foot}</small>` : ""}</div>${[0, 1].map(i => `<div role="cell"><span class="label who-p">${esc(paperName(ps[i]))}</span>${f(i)}</div>`).join("")}</div>`).join("")}
  </div></section>`;
}

// One pair of scenes: what each comes to, then (opened) the two timelines lined up.
let vsCol = 0;
function alignedHTML(a, b) {
  const ra = buildRows(a.s), rb = buildRows(b.s), ka = ra.map(kindsOf), kb = rb.map(kindsOf);
  const rows = alignSteps(ka.slice(1), kb.slice(1)), hits = rows.filter(([i, j]) => i && j), ca = ++vsCol, cb = ++vsCol;
  const chips = (ks, sh) => ks.length ? `<p class="kc">${ks.map(k => `<span${sh.includes(k) ? ` class="sh"` : ""}>${kindName(k)}</span>`).join("")}</p>` : "";
  const cell = (x, col, t, ks, sh) => t === null ? `<div class="al-c none"><span>no counterpart</span></div>`
    : `<div class="al-c"><span class="label who-p">${esc(paperName(x.p))} · ${t === "end" ? "the end" : "step " + t}</span>${chips(ks, sh)}${timelineHTML(x, col, -1, t, true)}</div>`;
  const row = (i, j, label) => { const sh = i !== null && j !== null && i !== "end" ? ka[i].filter(k => kb[j].includes(k)) : [];
    return `<div class="al-r${sh.length ? " hit" : ""}">${label ? `<p class="al-l label">${label}</p>` : sh.length ? `<p class="al-l label">Same kind of step: ${sh.map(kindName).join(", ")}</p>` : ""}${cell(a, ca, i, i === null || i === "end" ? [] : ka[i], sh)}${cell(b, cb, j, j === null || j === "end" ? [] : kb[j], sh)}</div>`; };
  const n = hits.length, note = n ? `${n === 1 ? "One step" : cap(COUNT[n] || String(n)) + " steps"} of “${esc(nameOf(a))}” ${n === 1 ? "sits" : "sit"} beside a step of the same kind in “${esc(nameOf(b))}”. The rest have no counterpart.`
    : "No step of one scene is the same kind of step as any in the other.";
  return `<div class="al"><p class="al-n">${note}</p>
    <div class="al-r al-h">${[a, b].map(x => `<div><button type="button" data-key="${x.key}">${esc(nameOf(x))}</button><small>${esc(paperName(x.p))}</small></div>`).join("")}</div>
    ${row(0, 0, "Where each starts")}${rows.map(([i, j]) => row(i, j)).join("")}${row("end", "end", "Where each ends")}
    <dl class="kkey">${KINDS.map(k => `<div><dt>${reg === "isle" ? k[2] : k[1]}</dt><dd>${reg === "isle" ? k[4] : k[3]}</dd></div>`).join("")}</dl></div>`;
}
function pairHTML(pa, pb, a, b) {
  const id = `${a ? a.key : ""}|${b ? b.key : ""}`, open = a && b && vsOpen.has(id);
  const card = (x, p, side) => {
    if (!x) return `<div class="vp-s none"><span>No scene of ${esc(paperName(p))} beside this one.</span>${side ? repick(null) : ""}</div>`;
    return `<div class="vp-s"><span class="label who-p">${esc(paperName(p))}</span><h3>${ocMark(x.oc)}<button type="button" data-key="${x.key}">${esc(nameOf(x))}</button></h3>
      <p class="vd">${VERDICT[x.oc]}</p><p class="tk">${esc(TAKE[x.key])}</p>${miniStrip(x)}${side ? repick(x) : ""}</div>`;
  };
  const repick = cur => !a ? "" : `<label class="repick"><span>Set beside</span><select data-vs="pair" data-a="${a.key}">${scenesOf(pb).map(x => `<option value="${x.key}"${x === cur ? " selected" : ""}>${esc(nameOf(x))}</option>`).join("")}<option value=""${cur ? "" : " selected"}>nothing</option></select></label>`;
  const sameOc = a && b && a.oc === b.oc;
  return `<section class="vp${open ? " open" : ""}${sameOc ? " same" : ""}">
    ${a && b ? `<p class="vp-oc label">${sameOc ? `Both: ${VERDICT[a.oc].toLowerCase()}` : "Different outcomes"}</p>` : ""}
    <div class="vp-pair">${card(a, pa, 0)}${card(b, pb, 1)}</div>
    ${a && b ? `<button type="button" class="btn sm" data-vsopen="${id}" aria-expanded="${!!open}">${open ? "Hide the steps" : "Line up the steps"}</button>` : ""}
    ${open ? alignedHTML(a, b) : ""}</section>`;
}

function vsHTML(key) {
  const [pa, pb] = vsOf(key), ready = pa && pb;
  const head = `<div class="intro"><h1>Compare</h1>
    <p class="idea">${ready ? "" : `Set two ${U().unit[1]} side by side: what each is after and what it assumes, then their scenes in pairs, with the steps lined up by the kind of step.`}</p>
    <div class="picks">${pickerHTML("a", pa, pb)}<button type="button" class="swap" data-vsswap="1" aria-label="Swap the two"${ready ? "" : " disabled"}><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M3 6h11l-3-3M15 12H4l3 3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>${pickerHTML("b", pb, pa)}</div></div>`;
  if (!ready) return `<div class="map vs">${head}${pa || pb ? linkedHTML(pa || pb) : ""}${linkedHTML()}</div>`;
  const k = vsKey(pa.id, pb.id), pairs = pairsOf(pa, pb);
  if (vsSeen !== k) { vsSeen = k; vsOpen.clear(); const f = pairs.find(([a, b]) => a && b); if (f) vsOpen.add(`${f[0].key}|${f[1].key}`); }   // a new comparison opens on its first pair
  const e = edgeOf(pa.id, pb.id);
  const link = e ? `<p class="vlink"><span class="label">On the map</span>${esc(paperName(pById(e[0])))} <span aria-hidden="true">→</span><span class="sr">leads to</span> ${esc(paperName(pById(e[1])))}: <i>${esc(e[2])}</i>.</p>` : "";
  const A = [pa, pb].map(p => ARC[p.id]), lands = A[0] && A[1] ? `<section class="sect"><p class="label">What each adds up to</p><div class="vt"><div class="vr two">${[pa, pb].map((p, i) =>
    `<div><span class="label who-p always">${esc(paperName(p))}</span><p class="lands">${esc(cap(A[i].end))}.</p><p>${esc(A[i].sum[reg === "isle" ? 1 : 0])}</p></div>`).join("")}</div></div></section>` : "";
  return `<div class="map vs">${head.replace(`<p class="idea"></p>`, link)}
    ${setupHTML(pa, pb)}
    <section class="sect"><p class="label">The scenes, in pairs</p><p class="fine">Scenes with the same outcome are set beside each other, then the rest in order. Change a pairing with “Set beside”.</p>${pairs.map(([a, b]) => pairHTML(pa, pb, a, b)).join("")}</section>
    ${lands}</div>`;
}
