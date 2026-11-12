// ---------- pages ----------
// ---------- the drawer: faceted filter above, then results with their scenes nested under them ----------
const tagsOf = p => PAPER_TAGS[p.id].split(" ");
const matches = p => [...haz].every(h => tagsOf(p).includes(h));
const expanded = new Set();
function facetsHTML() {
  const count = h => PAPERS.filter(p => [...new Set([...haz, h])].every(x => tagsOf(p).includes(x))).length;
  const hit = PAPERS.filter(matches).length, [one, many] = U().unit;
  const chips = HAZARDS.map(([id, plain, isle]) => { const c = count(id), on = haz.has(id);
    return `<button type="button" data-haz="${id}" aria-pressed="${on}"${c || on ? "" : ` class="zero"`}><span>${isle_(plain, isle)}</span><b>${c}</b></button>`; }).join("");
  return `<div class="fhead"><span class="label">${U().inplay}</span>${haz.size ? `<button type="button" class="link" data-hazclear="1">Clear</button>` : ""}</div>
    <div class="chips" role="group" aria-label="${U().inplay}. ${U().pick}.">${chips}</div>
    <p class="fnote" aria-live="polite">${haz.size ? (hit ? `<b>${hit}</b> of ${PAPERS.length} ${hit === 1 ? one : many} have ${haz.size > 1 ? "all of these" : "this"} in play.` : `No ${one} has all of these in play.`) : U().pick + "."}</p>`;
}
const isle_ = (plain, isle) => reg === "isle" ? isle : plain;
function indexHTML(it, land) {
  const cur = it ? it.p : null;
  const chev = `<svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M4 2.5L7.5 6 4 9.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const paper = p => {
    const open = expanded.has(p.id), here = land && p === cur, inside = !land && p === cur;
    const scenes = open ? `<ul class="scl">${p.scenes.map(s => { const x = byKey(`${p.id}-${s.id}`); return `<li><button type="button" class="sl" data-key="${x.key}" aria-pressed="${!land && x === it}"><span>${esc(nameOf(x))}</span>${ocMark(x.oc, "xo")}</button></li>`; }).join("")}</ul>` : "";
    return `<div class="pg${matches(p) ? "" : " off"}${open ? " open" : ""}"><div class="prow"><button type="button" class="pl" data-key="${p.id}" aria-pressed="${here}"${inside ? ` aria-current="true"` : ""}><span>${esc(paperName(p))}</span><small>${esc(p.year)}</small></button><button type="button" class="chev" data-tog="${p.id}" aria-expanded="${open}" aria-label="Scenes in ${esc(paperName(p))}">${chev}</button></div>${scenes}</div>`;
  };
  return `<button type="button" class="pl map" data-key="map" aria-pressed="${!it}"><span>${U().map}</span></button>`
    + CHAPTERS.map(([name, ids]) => {
      const ps = ids.map(id => PAPERS.find(x => x.id === id)).filter(p => matches(p) || p === cur);
      if (!ps.length) return "";
      return `<div class="chap"><span class="label">${reg === "isle" ? listAnd([...new Set(ids.map(id => HAT[TELL[id].hat][0]))]) + " · " : ""}${esc(name)}</span>${ps.map(paper).join("")}</div>`;
    }).join("");
}
// A result's own page: the shared header, then the way in.
function landHTML(it) {
  const n = it.p.scenes.length;
  return `<div class="start"><p class="fine">${n} ${n === 1 ? "scene" : "scenes"}: ${listAnd(it.p.scenes.map(s => esc(nameOf(byKey(`${it.p.id}-${s.id}`)))))}.</p>
    <div><button type="button" class="btn go-out" data-key="${it.key}">Start exploring</button></div></div>`;
}
function paperHTML(it) {
  const p = it.p, f = p.frame, I = isleOf(p);
  const cite = `<div class="cite">${p.cite.split("\n").map(c => `<span>${esc(c)}</span>`).join("")}</div>`;
  const lexi = I ? `<dl class="lexi"><dt class="label">In the telling</dt><dd class="label">In plain terms</dd>${I.gloss.map(([a, b]) => `<dt>${esc(a)}</dt><dd>${esc(b)}</dd>`).join("")}</dl>` : "";
  const facts = g => `<dl class="facts">${[["The goal", g.goal], ["What is shared", g.shared], ["What it assumes", g.assumes]].map(([k, v]) => `<div><dt class="label">${k}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl>`;
  if (I) return `<h1>${esc(p.name)}</h1>
    <div class="gloss">${cite}${lexi}</div>
    <p class="idea">Told among the ${HAT[I.hat][0].toLowerCase()} of Paxos. ${esc(HAT[I.hat][1])} ${esc(I.tale)}</p>
    ${I.frame ? facts(I.frame) : ""}`;
  const gloss = (p.names || "").split(" · ").map(e => { const i = e.indexOf(" = "); return i < 0 ? `<dt>${esc(e)}</dt><dd></dd>` : `<dt>${esc(e.slice(0, i))}</dt><dd>${esc(e.slice(i + 3))}</dd>`; }).join("");
  return `<h1>${esc(p.name)}</h1>
    <div class="gloss">${cite}<dl>${gloss}</dl></div>
    <p class="idea">${esc(p.idea)}</p>
    ${facts(f)}
    
`;
}

// What each step is told as, in the current register.
function tellOf(it) {
  const s = it.s, O = ovOf(it), rows = buildRows(s);
  rows.forEach(r => {
    r.say = O ? mk(O.prose[r.t] || "") : nodeText(r.note, s);
    r.sayPlain = O ? (O.prose[r.t] || "").replace(/[{}]/g, "") : r.note;
    r.aside = O ? mk((O.out || {})[r.t] || "") : r.out ? nodeText(r.out, s) : "";
  });
  const phases = (s.phases || []).map(([from, name, why], i) => [from, O ? (O.phases || [])[i] || name : name, O ? "" : why]);
  return { rows, phases };
}
// The scene at a glance: one dot per step.
// The stepper box, the scene's main view: the controls, then the picture, which folds away, then what happens in the chosen step.
function stripHTML(it) {
  const pic = stageHTML(it);
  return `<div class="strip stepbar" id="stepbar" role="group" aria-label="Steps of the scene">${pic ? `<div class="pict" id="pict">${pic}</div>` : ""}${ctlHTML(it)}${panelHTML(it)}</div>`;
}
function ctlHTML(it) {     // one circle per step
  const { rows, phases } = tellOf(it), atEnd = stageStep >= rows.length, n = atEnd ? -1 : stageStep;
  const cls = r => (r.t && JSON.stringify(r.perm) !== JSON.stringify(r.prevPerm) ? "p" : r.t && JSON.stringify(r.temp) !== JSON.stringify(r.prevTemp) ? "t" : "n")
    + (r.recv.some(m => m[0] !== "nothing") ? " r" : "") + (r.sent.length ? " s" : "") + (r.t === n ? " on" : "");
  const say = r => `Step ${r.t}: ${r.sayPlain}`;
  const dot = r => `<button type="button" class="sd ${cls(r)}" data-step="${r.t}" title="${esc(say(r))}" aria-label="${esc(say(r))}"${r.t === n ? ` aria-current="step"` : ""}>${r.t}</button>`;
  const ph = phases.length ? phases : [[0, ""]];
  const end = `<button type="button" class="sd fin${atEnd ? " on" : ""}" data-step="${rows.length}" title="${U().endStep}" aria-label="${U().endStep}"${atEnd ? ` aria-current="step"` : ""}><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 6.2l2.4 2.4 4.6-5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg></button>`;
  const groups = ph.map(([from, name], i) => `<div class="sg">${name ? `<span class="label">${esc(name)}</span>` : ""}<div class="dots">${rows.slice(from, i + 1 < ph.length ? ph[i + 1][0] : rows.length).map(dot).join("")}${i === ph.length - 1 ? end : ""}</div></div>`).join("");
  const k = U().strip;
  return `<div class="sctl" id="sctl">
    <button type="button" class="btn sm arrow" data-stage="-1" aria-label="Previous step"${stageStep ? "" : " disabled"}><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M8.5 2.5L4 7l4.5 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="sgs">${groups}</div><button type="button" class="btn sm arrow" data-stage="1" aria-label="Next step"${atEnd ? " disabled" : ""}><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M5.5 2.5L10 7l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    <div class="sfoot"><div class="skey"><span><i class="sd p"></i>${k[0]}</span><span><i class="sd t"></i>${k[1]}</span><span><i class="sd n"></i>${k[2]}</span><span><i class="sd n r"></i>${k[3]}</span><span><i class="sd n s"></i>${k[4]}</span></div></div></div>`;
}
const whoOf = it => { const I = isleOf(it.p), n = nmOf(I, it.s.who); return n ? "the " + esc(n) : (I ? esc(roleOf(I, it.s.who)) + " " : "") + ND(esc(it.s.who)); };
function timelineHTML(it, col, dv, only) {      // only: one step's number, or "end"; the panel under the picture shows just that
  const s = it.s, I = isleOf(it.p), { rows, phases } = tellOf(it), seen = new Map(), me = whoOf(it);
  const tw = twinOf(it), same = tw ? sameRows(s, tw.s) : 0, whole = tw && same === Math.max(s.rows.length, tw.s.rows.length);
  const phaseAt = new Map(phases.map(([from, name, why]) => [from, [name, why]]));
  const solo = only !== undefined, phaseOf = t => phases.filter(([from]) => from <= t).pop();
  let tl = solo ? "" : `<div class="lane-h l label">${U().arrives}</div><div class="band mid-h"><b>${I ? cap(me) : `Inside node ${esc(s.who)}`}</b><div class="legend"><span>${U().permL}</span><span>${U().tempL}</span></div></div><div class="lane-h r label">${U().leaves}</div>`;
  if (solo && only !== "end" && phaseOf(only)) { const [, name, why] = phaseOf(only); tl += `<div class="band ph"><b>${esc(name)}</b>${why ? `<i>${nodeText(why, s)}</i>` : ""}</div>`; }
  rows.forEach(r => {
    if (solo && r.t !== only) { if (only === "end" || r.t < only) msgs(r.sent, "out", seen, r.t, I); return; }    // earlier steps still count for "same order as step 2"
    if (!solo && phaseAt.has(r.t)) { const [name, why] = phaseAt.get(r.t); tl += `<div class="band ph"><b>${esc(name)}</b>${why ? `<i>${nodeText(why, s)}</i>` : ""}</div>`; }
    tl += `<div class="in">${msgs(r.recv, "in", seen, r.t, I)}</div>`
      + `<div class="band core${solo ? " solo" : ""}" id="st-${col}-${r.t}"><span class="tm" aria-label="step ${r.t}">${r.t}</span>${dv === r.t ? `<span class="dv">First difference</span>` : ""}<p class="say">${r.say}</p>${stateBox(r, I)}</div>`
      + `<div class="outb">${msgs(r.sent, "out", seen, r.t, I)}${r.aside ? `<p class="xo aside">${r.aside}</p>` : ""}</div>`;
  });
  const through = whole ? "" : `, through step ${same},`;
  const twinLine = !tw ? "" : `${I ? cap(me) : "Node " + me} takes exactly these steps${through} in “${esc(nameOf(tw))}” too. Only the world differs.`;
  if (!solo || only === "end") tl += `<div class="band end"><span class="tm" aria-hidden="true"></span>
      <p class="xi">That is everything ${I ? me : "node " + me} can know.${tw ? " At least two different worlds look exactly like this from in here." : ""}</p>
      <div class="xi"><button type="button" class="btn go-out" data-lens="outside">${U().goOut}</button></div>
      <p class="xo verdict">${ocMark(it.oc)}${U().seen}: ${VERDICT[it.oc].toLowerCase()}</p>
      <p class="xo">${esc(TAKE[it.key])}${tw ? " " + twinLine : ""}</p>
      <div class="xo btns">${tw ? `<button type="button" class="btn go-out" data-key="${tw.key}" data-keep="1">Swap worlds</button>` : ""}<button type="button" class="btn" data-lens="inside">${U().goIn}</button></div>
    </div>`;
  return `<div class="tlw"><div class="tl">${tl}</div></div>`;
}
// The panel under the picture: the chosen step told in full, then what arrives, what the node keeps, and what leaves, left to right.
function panelHTML(it) {
  const s = it.s, I = isleOf(it.p), { rows, phases } = tellOf(it);
  if (stageStep >= rows.length) return `<div class="panel" id="panel" aria-live="polite">${timelineHTML(it, 0, -1, "end")}</div>`;
  const r = rows[stageStep], seen = new Map(), ph = phases.filter(([from]) => from <= r.t).pop();
  rows.filter(x => x.t < r.t).forEach(x => msgs(x.sent, "out", seen, x.t, I));          // so a repeat reads "same order as step 2"
  const col = (cls, label, body, none) => `<div class="fcol ${cls}"><span class="label">${label}</span>${body || `<p class="none">${none}</p>`}</div>`;
  return `<div class="panel" id="panel" aria-live="polite"><div class="sp">
    ${ph ? `<p class="sp-ph"><b>${esc(ph[1])}</b>${ph[2] ? ` <i>${nodeText(ph[2], s)}</i>` : ""}</p>` : ""}
    <p class="say">${r.say}</p>
    <div class="flow">${col("fin", U().arrives, msgs(r.recv, "in", seen, r.t, I), U().noneIn)}${col("fst", U().kept, stateBox(r, I))}${col("fout", U().leaves, msgs(r.sent, "out", seen, r.t, I), U().noneOut)}</div>
    ${r.aside ? `<p class="xo aside">${r.aside}</p>` : ""}
  </div></div>`;
}
const noteOf = it => { const O = ovOf(it); return O ? mk(O.note || "") : it.s.note ? nodeText(it.s.note, it.s) : ""; };
function briefHTML(it) {
  const O = ovOf(it), text = O ? mk(O.outside || "") : it.s.outside ? nodeText(it.s.outside, it.s) : "";
  return text ? `<div class="xo brief"><span class="label">${O ? "What the world view shows, and " + (nmOf(isleOf(it.p), it.s.who) ? "the " + esc(nmOf(isleOf(it.p), it.s.who)) : esc(it.s.who)) + " could not see" : `What ${esc(it.s.who)} cannot see`}</span><p>${text}</p></div>` : "";
}
const pointHTML = it => `<p class="point"><span class="label">${U().point}: </span>${esc(TAKE[it.key])}</p>`;
function castHTML(it) {
  const s = it.s, I = isleOf(it.p), O = ovOf(it);
  if (!I) return `You are inside node <span class="nd">${esc(s.who)}</span>${s.role ? `, ${/^(coordinator|primary)$/.test(s.role) ? "the" : "a"} ${esc(s.role)}` : ""}. Out there: ${nodeText(s.peers, s)}.`;
  const ls = s.peers.match(/\b[A-Z]\b/g) || [];
  if (I.names) return `You run the ${esc(I.names[s.who])}. You hear from ${listAnd(ls.map(l => "the " + esc(I.names[l])))}, and only by courier.`;
  const r0 = roleOf(I, ls[0]), same = ls.every(l => roleOf(I, l) === r0);
  const peers = O.peers ? mk(O.peers) : I.peers ? mk(I.peers) : same ? `${r0}${ls.length > 1 ? "s" : ""} ${listAnd(ls.map(ND))}` : listAnd(ls.map(l => `${roleOf(I, l)} ${ND(l)}`));
  return `You are ${esc(roleOf(I, s.who))} ${ND(esc(s.who))}${O.as ? `, ${esc(O.as)}` : ""}. You hear from ${peers}, and only by courier.`;
}
function sceneHTML(it) {
  const { p, s } = it, I = isleOf(p);
  const other = byKey(PAIR[it.key]), both = cmp && other;
  const lensBtns = `<button type="button" class="lsw" role="switch" data-lens="toggle" aria-checked="${lens === "outside"}"><span class="tr" aria-hidden="true"><span class="kn"></span></span>${U().outBtn}</button>`;
  const cmpBtn = other ? `<button type="button" class="btn sm" data-cmp="1" aria-pressed="${!!both}">${both ? "Close comparison" : `Compare with “${esc(nameOf(other))}”`}</button>` : "";
  const i = ALL.indexOf(it), prev = ALL[i - 1], next = ALL[i + 1];
  const pg = (x, word) => x ? `<button type="button" data-key="${x.key}"><span class="label">${word}${x.p !== p ? " · " + esc(paperName(x.p)) : ""}</span><span>${esc(nameOf(x))}</span></button>` : "";
  let body;
  if (both) {
    const d = firstDiff(s, other.s);
    const column = (x, n) => `<section class="col"><h3>${esc(nameOf(x))}${ocMark(x.oc, "xo")}</h3>${pointHTML(x)}${noteOf(x) ? `<p class="rule">${noteOf(x)}</p>` : ""}${briefHTML(x)}${timelineHTML(x, n, d)}</section>`;
    body = `<p class="cmpnote">${d < 0 ? U().same : d === 0 ? U().differ0 : U().until(d)}</p><div class="cmp">${column(it, 0)}${column(other, 1)}</div>`;
  } else body = briefHTML(it) + `<div class="player">${stripHTML(it)}</div>`;
  return `<div class="scene-head">
      <div class="stitle"><h2>${esc(nameOf(it))}</h2><div class="ctl">${cmpBtn}${lensBtns}</div></div>
      ${both ? "" : pointHTML(it)}
      <p class="cast">${castHTML(it)}</p>
      ${noteOf(it) && !both ? `<p class="rule">${noteOf(it)}</p>` : ""}
    </div>
    ${body}
    <nav class="pager" aria-label="Reading order">${prev ? pg(prev, "Before") : `<button type="button" data-key="map"><span class="label">Before</span><span>${U().map}</span></button>`}${pg(next, "Next")}</nav>`;
}

// The map: which result answers a problem another one raises.
function mapHTML() {
  const X = [20, 260, 500, 740], Y = [30, 150, 270, 390, 510], W = 170, H = 58, isle = reg === "isle";
  const at = { snapshot: [0, 0], clocks: [0, 1], cops: [0, 2], commit: [0, 3], benor: [1, 0], flp: [1, 1], suspect: [1, 2], paxos: [1, 3], vr: [1, 4],
    liars: [2, 3], pbft: [2, 4], linear: [3, 0], cap: [3, 1], quorum: [3, 2], merge: [3, 3], bayou: [3, 4] };
  const edges = [["clocks", "snapshot", "a state that could have been"], ["clocks", "cops", "causes before effects"], ["flp", "benor", "or flip a coin"], ["flp", "suspect", "so guess, and allow mistakes"],
    ["suspect", "paxos", "stay safe whatever the timing"], ["paxos", "vr", "one value becomes a stream"], ["commit", "paxos", "a majority, not all"], ["flp", "cap", "the same blindness, for reads"],
    ["linear", "cap", "what lost messages take away"], ["cap", "quorum", "wait for some copies, not all"], ["quorum", "merge", "or never wait, and merge"], ["merge", "bayou", "when merging needs one order"],
    ["liars", "pbft", "the same, for a stream"], ["vr", "pbft", "the same, among liars"]];
  let g = "";
  edges.forEach(([a, b, label]) => {
    const [ca, ra] = at[a], [cb, rb] = at[b];
    if (ca === cb) {
      const x = X[ca] + 26, down = rb > ra, y1 = down ? Y[ra] + H : Y[ra], y2 = down ? Y[rb] : Y[rb] + H, k = down ? -8 : 8;
      g += `<path class="me" d="M${x} ${y1}V${y2 + k}"/><path class="mh" d="M${x - 5} ${y2 + k}L${x} ${y2}L${x + 5} ${y2 + k}z"/><text class="ml" x="${x + 12}" y="${(y1 + y2) / 2 + 4}">${esc(label)}</text>`;
    } else {
      const y = Y[ra] + H / 2, x1 = X[ca] + W, x2 = X[cb], far = cb - ca > 1;
      g += `<path class="me" d="M${x1} ${y}H${x2 - 8}"/><path class="mh" d="M${x2 - 8} ${y - 5}L${x2} ${y}L${x2 - 8} ${y + 5}z"/><text class="ml" text-anchor="middle" x="${(x1 + x2) / 2}" y="${far ? y - 9 : Y[ra] + H + 18}">${esc(label)}</text>`;
    }
  });
  PAPERS.forEach(p => {
    const [c, r] = at[p.id], x = X[c], y = Y[r], n = p.scenes.length;
    g += `<g class="mn" role="button" tabindex="0" data-key="${p.id}" aria-label="${esc(paperName(p))}: ${esc(p.name)}"><rect x="${x}" y="${y}" width="${W}" height="${H}" rx="5"/><text class="n1" x="${x + 13}" y="${y + 25}">${esc(paperName(p))}</text><text class="n2" x="${x + 13}" y="${y + 44}">${esc(isle ? HAT[TELL[p.id].hat][0] : `${p.year} · ${n} ${n === 1 ? "scene" : "scenes"}`)}</text></g>`;
  });
  const svg = `<div class="mapbox"><svg viewBox="0 0 980 610" role="group" aria-label="How the sixteen lead to one another">${g}</svg></div>`;
  const start = `<div><button type="button" class="btn go-out" data-key="${ALL[0].key}">Start with ${esc(paperName(ALL[0].p))}</button></div>`;
  const words = [["Courier", "A message. It may be slow, lost, or overtaken by a later one."], ["Ledger", "Permanent state. It passes to whoever takes over."], ["Slate", "Temporary state. It is wiped when its owner goes."],
    ["Hourglass", "A timer. It says how long you have waited, never why."], ["Successor", "A replacement, who starts from the ledger alone."], ["World view", "Everything that happened, everywhere, seen from above. Nobody on the island has it."]];
  const items = list => `<ul class="customs">${list.map(([a, b]) => `<li><span class="label">${a}</span>${b}</li>`).join("")}</ul>`;
  if (isle) return `<div class="map">
    <h1>${U().title}</h1>
    <p class="idea">Paxos has no assembly hall. Its people work from their own places, legislating part-time between other duties, and everything one of them knows about another arrived by courier. Sixteen results from distributed computing are told here as scenes from that island, each from inside one person's view.</p>
    <p class="label">Four kinds of work, four kinds of problem</p>
    ${items(Object.values(HAT))}
    ${svg}
    <p class="label">Six words used everywhere</p>
    ${items(words)}
    <p class="fine">The part-time legislators are Leslie Lamport's, from The Part-Time Parliament, and the commander and lieutenants are the generals of Lamport, Shostak and Pease. People have no names: a role and a letter, the same letter in both tellings. The merchants are the one exception. Their three businesses, a fishery, a granary and a winery, stand in for A, B and C. What is asked for and decided is specific here, such as a colour for the temple columns or an order for grain, but the steps are the same. Switch to Abstraction at any point to drop the island.</p>
    ${start}
  </div>`;
  return `<div class="map">
    <h1>${U().title}</h1>
    <p class="idea">Each result is told as a few short scenes from inside one node. You see what it holds, what arrives and what it sends. Then you step outside and see what it could not.</p>
    <p class="idea">An arrow leads from a result to one that answers a problem it raises, or builds on it.</p>
    ${svg}${start}
  </div>`;
}

