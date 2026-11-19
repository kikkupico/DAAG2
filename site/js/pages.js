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
    <p class="fnote" aria-live="polite">${haz.size ? (hit ? `<b>${hit}</b> of ${PAPERS.length} ${hit === 1 ? one : many} have ${haz.size > 1 ? "all of these" : "this"} in play.` : `No ${one} has all of these in play.`) : ""}</p>`;
}
const isle_ = (plain, isle) => reg === "isle" ? isle : plain;
// Under the list of results and the filter: the tool that works across results.
const moreHTML = () => `<span class="label">Across results</span><button type="button" class="pl map" data-key="${isVs(sel) ? sel : "cmp"}" aria-pressed="${isVs(sel)}"><span>Compare two results</span></button><span class="label">This project</span><a class="pl ext" href="${REPO}" target="_blank" rel="noopener"><span>Source on GitHub</span><small aria-hidden="true">↗</small></a>`;
function indexHTML(it, land) {
  const cur = it ? it.p : null;
  const chev = `<svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M4 2.5L7.5 6 4 9.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const paper = p => {
    const open = expanded.has(p.id), here = land && p === cur, inside = !land && p === cur;
    const scenes = open ? `<ul class="scl">${p.scenes.map(s => { const x = byKey(`${p.id}-${s.id}`); return `<li><button type="button" class="sl" data-key="${x.key}" aria-pressed="${!land && x === it}"><span>${esc(nameOf(x))}</span>${ocMark(x.oc)}</button></li>`; }).join("")}</ul>` : "";
    return `<div class="pg${matches(p) ? "" : " off"}${open ? " open" : ""}"><div class="prow"><button type="button" class="pl" data-key="${p.id}" aria-pressed="${here}"${inside ? ` aria-current="true"` : ""}><span>${esc(paperName(p))}</span><small>${esc(p.year)}</small></button><button type="button" class="chev" data-tog="${p.id}" aria-expanded="${open}" aria-label="Scenes in ${esc(paperName(p))}">${chev}</button></div>${scenes}</div>`;
  };
  return `<div class="chap"><button type="button" class="pl map" data-key="intro" aria-pressed="${guideOpen}"><span>The guide</span></button><button type="button" class="pl map" data-key="map" aria-pressed="${sel === "map"}"><span>${U().map}</span></button></div>`
    + CHAPTERS.map(([name, ids]) => {
      const ps = ids.map(id => PAPERS.find(x => x.id === id)).filter(p => matches(p) || p === cur);
      if (!ps.length) return "";
      return `<div class="chap"><span class="label">${reg === "isle" ? listAnd([...new Set(ids.map(id => HAT[TELL[id].hat][0]))]) + " · " : ""}${esc(name)}</span>${ps.map(paper).join("")}</div>`;
    }).join("");
}
// A result's own page: the shared header, then the way in.
function withHTML(p) {      // a way into a comparison: the results the map links to this one come first, with the arrow's words
  const linked = MAP_EDGES.filter(([a, b]) => a === p.id || b === p.id).map(([a, b, l]) => [a === p.id ? b : a, l]), ids = linked.map(x => x[0]);
  const opt = (id, l) => `<option value="${id}">${esc(paperName(pById(id)))}${l ? " · " + esc(l) : ""}</option>`;
  return `<select class="pick" data-vs="with" data-a="${p.id}" aria-label="Compare ${esc(paperName(p))} with another"><option value="" selected>Compare with…</option>${linked.length ? `<optgroup label="Linked on the map">${linked.map(([id, l]) => opt(id, l)).join("")}</optgroup>` : ""}<optgroup label="Any other">${PAPERS.filter(x => x !== p && !ids.includes(x.id)).map(x => opt(x.id)).join("")}</optgroup></select>`;
}
function landHTML(it) {
  const xs = it.p.scenes.map(s => byKey(`${it.p.id}-${s.id}`));
  return `<div class="start"><div class="ctl"><button type="button" class="btn go-out" data-key="${it.key}">Start with the first scene</button>${withHTML(it.p)}</div>
    <ol class="toc">${xs.map((x, i) => `<li><button type="button" data-key="${x.key}"><span class="n">${i + 1}</span><span class="t">${esc(nameOf(x))}</span><span class="d">${esc(TAKE[x.key])}</span></button></li>`).join("")}</ol>${sumHTML(it.p, true)}</div>${theaterHead(it.p.id)}<div class="ipict" id="pict">${stageHTML(it)}</div>${pagerHTML(it.p.id)}`;
}
// The reading order: each result's own page, then its scenes. The pager under a page, and theater mode's arrows, walk it.
const ORDER = ALL.flatMap((x, i) => i && ALL[i - 1].p === x.p ? [x.key] : [x.p.id, x.key]);
function pagerHTML(key) {
  const i = ORDER.indexOf(key), cur = resolve(key).p;
  const pg = (k, word) => { if (!k) return ""; const p = resolve(k).p, intro = isPaper(k);
    return `<button type="button" data-key="${k}"><span class="label">${word}${intro ? (p !== cur ? " · the next result" : " · about this result") : p !== cur ? " · " + esc(paperName(p)) : ""}</span><span>${esc(intro ? paperName(p) : nameOf(byKey(k)))}</span></button>`; };
  return `<nav class="pager" aria-label="Reading order">${i > 0 ? pg(ORDER[i - 1], "Before") : `<button type="button" data-key="map"><span class="label">Before</span><span>${U().map}</span></button>`}${pg(ORDER[i + 1], "Next")}</nav>`;
}
// A result's header: its name and sources, the idea, three facts, then the words the telling uses.
function paperHTML(it) {
  const p = it.p, I = isleOf(p);
  const head = `<div class="phead"><h1>${esc(p.name)}</h1><p class="cite">${p.cite.split("\n").map(c => `<span>${esc(c)}</span>`).join("")}</p></div>`;
  const facts = g => `<dl class="facts">${[["The goal", g.goal], ["What is shared", g.shared], ["What it assumes", g.assumes]].map(([k, v]) => `<div><dt class="label">${k}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl>`;
  const words = (label, list) => list.length ? `<div class="words"><p class="label">${label}</p><dl class="lexi">${list.map(([a, b]) => `<dt>${esc(a)}</dt><dd>${esc(b)}</dd>`).join("")}</dl></div>` : "";
  if (I) return `${head}
    <p class="idea">Told among the ${HAT[I.hat][0].toLowerCase()} of ${esc(ALLEGORY.town)}. ${esc(HAT[I.hat][1])} ${esc(I.tale)}</p>
    ${I.frame ? facts(I.frame) : ""}
    ${words("In the telling, in plain terms", I.gloss)}`;
  const names = (p.names || "").split(" · ").filter(Boolean).map(e => { const i = e.indexOf(" = "); return i < 0 ? [e, ""] : [e.slice(0, i), e.slice(i + 3)]; });
  return `${head}
    <p class="idea">${esc(p.idea)}</p>
    ${facts(p.frame)}
    ${words("Names used", names)}`;
}

// What each step is told as, in the current register.
function tellOf(it) {
  const s = it.s, O = ovOf(it), rows = buildRows(s), V = it.told;
  if (V) {      // another node's view (pov.js): its accounts and asides are already told, in the current telling
    const I = isleOf(it.p);
    rows.forEach(r => { r.say = V.say[r.t] || (r.t ? "" : startOf(it)); r.sayPlain = r.say.replace(/<[^>]+>/g, ""); r.aside = V.asides[r.t] || ""; });
    return { rows, phases: V.phases.map(([from, name, why, iname]) => [from, I ? iname || name : name, I ? "" : why]) };
  }
  const brief = O ? mk(O.outside || "") : s.outside ? nodeText(s.outside, s) : "";     // how things stand beyond the node's sight, told with the starting step
  rows.forEach(r => {
    r.say = O ? mk(O.prose[r.t] || "") : nodeText(r.note, s);
    r.sayPlain = O ? (O.prose[r.t] || "").replace(/[{}]/g, "") : r.note;
    r.aside = O ? mk((O.out || {})[r.t] || "") : r.out ? nodeText(r.out, s) : "";
    if (!r.t && brief) r.aside = r.aside ? brief + " " + r.aside : brief;
  });
  const phases = (s.phases || []).map(([from, name, why], i) => [from, O ? (O.phases || [])[i] || name : name, O ? "" : why]);
  return { rows, phases };
}
// Another node's starting step, which no telling writes: who it is, and that it has not acted yet.
const startOf = it => { const I = isleOf(it.p), X = it.s.who, n = nmOf(I, X);
  return n ? `The ${esc(n)} has done nothing yet.` : I ? `${cap(esc(roleOf(I, X)))} ${ND(X)} has done nothing yet.` : `${ND(X)}${it.s.role ? `, a ${esc(it.s.role)},` : ""} has done nothing yet.`; };
// The scene at a glance: one dot per step.
// The stepper box, the scene's main view: the controls, then the picture, which folds away, then what happens in the chosen step.
function stripHTML(it) {
  const pic = stageHTML(it);
  return `<div class="strip stepbar" id="stepbar" role="group" aria-label="Steps of the scene">${pic ? `<div class="pict" id="pict">${pic}</div>${theaterHead(it.key)}${sheadHTML(it)}` : ""}${ctlHTML(it)}${panelHTML(it)}</div>`;
}
// The scene's own head, on the stage: its name and its point, and behind the ⓘ what it rests on (the concept, the papers,
// its place in the result's argument), who you are in it, its rule, and its near-twin to compare with. The ⓘ stays as the
// reader left it from scene to scene.
let aboutOpen = false;
const twinBtn = it => { const other = it.pov ? null : byKey(PAIR[it.key]); return other ? `<button type="button" class="btn sm" data-cmp="1" aria-pressed="${cmp}">${cmp ? "Close comparison" : `Compare with “${esc(nameOf(other))}”`}</button>` : ""; };
function sheadHTML(it) {
  const rule = noteOf(it), cmpB = twinBtn(it);
  return `<div class="shead" id="shead">${sheetHandle()}<div class="sh-t"><h2>${esc(nameOf(it))}</h2><button type="button" class="sh-i" data-about="1" aria-expanded="${aboutOpen}" aria-controls="sabout" aria-label="About this scene" title="About this scene">`
    + `<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="7.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M9 8v5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="9" cy="5.4" r="1" fill="currentColor"/></svg></button></div>`
    + `${pointHTML(it)}<div class="sabout" id="sabout"${aboutOpen ? "" : " hidden"}><div class="sab-point">${pointHTML(it)}</div>${basisHTML(it)}<p class="cast">${castHTML(it)}</p>${rule ? `<p class="rule">${rule}</p>` : ""}${cmpB ? `<div class="ctl">${cmpB}</div>` : ""}</div></div>`;
}
// ---------- twin scenes on one stage ----------
// A scene and its near-twin side by side: two pictures, each playing its own scene's step, and one stepper for both, over
// the longer one's steps. The dots mark the first step where the two differ from inside, and the steps only one of them has.
// The panel tells the open scene's step, then the twin's: the same, from inside, until they part; then its own words.
function splitOf() {
  const it = byKey(sel), other = it && (beside ? byKey(beside) : cmp ? byKey(PAIR[it.key]) : null); if (!other || !stageOf(it) || !stageOf(other)) return null;
  const far = other.p !== it.p;      // two results' scenes, set beside each other from a comparison: nothing is the same from inside
  return { it, other, far, long: other.s.rows.length > it.s.rows.length ? other : it, short: other.s.rows.length > it.s.rows.length ? it : other, d: far ? 0 : firstDiff(it.s, other.s) };
}
function splitHTML(sp) {
  // each caption carries two dots, its own filled: on an upright phone, where the pictures take turns, they say which is up and switch
  const pg = i => `<span class="pg">${[0, 1].map(j => `<button type="button" data-pside="${j}" aria-label="${j ? "The second picture" : "The first picture"}"${i === j ? ` aria-current="true"` : ""}></button>`).join("")}</span>`;
  const { it, other, far } = sp, half = (x, id, word, i) => `<div class="half"><p class="hcap">${pg(i)}<span class="label">${word}</span><b>${esc(nameOf(x))}</b>${ocMark(x.oc)}</p>${stageHTML(x, id)}</div>`;
  const note = far ? "The two step together by number, not by kind: each picture plays its own scene's step. “Line up the steps”, on the comparison, matches them by kind."
    : sp.d < 0 ? U().same : sp.d === 0 ? U().differ0 : U().until(sp.d);
  const close = far ? `<button type="button" class="btn sm" data-key="${vsKey(it.p.id, other.p.id)}">Back to the comparison</button>` : `<button type="button" class="btn sm" data-cmp="1" aria-pressed="true">Close comparison</button>`;
  return `<div class="strip stepbar split${far ? " far" : ""}" id="stepbar" role="group" aria-label="Steps of the two scenes"><div class="pict" id="pict">${half(it, "stage", far ? esc(paperName(it.p)) : "This scene", 0)}${half(other, "stage2", far ? esc(paperName(other.p)) : "Beside it", 1)}</div>${theaterHead(it.key)}`
    + `<div class="shead" id="shead">${sheetHandle()}<div class="sh-t"><h2>${esc(nameOf(it))} <span class="beside">beside “${esc(nameOf(other))}”</span></h2></div>`
    + `<p class="cmpnote">${note}</p><div class="ctl">${close}</div></div>`
    + `${splitCtlHTML(sp)}${splitPanelHTML(sp)}</div>`;
}
function splitCtlHTML(sp) {      // the longer scene's dots, marked where the two part and where only one goes on
  const n = sp.short.s.rows.length, N = sp.long.s.rows.length, only = esc(nameOf(sp.long));
  return ctlHTML(sp.long).replace(/(<button type="button" class="sd [^"]*") data-step="(\d+)" title="([^"]*)"/g, (m, a, t, title) => {
    t = +t; const dv = !sp.far && t === sp.d, mark = dv ? ` data-dv="1"` : t > n && t <= N ? ` data-only="1"` : "";
    const note = dv ? " (the first difference)" : t > n && t <= N ? ` (only in “${only}”)` : "";
    return `${a} data-step="${t}"${mark} title="${title}${note}"`;
  });
}
function splitPanelHTML(sp) {
  const { other, d, far } = sp, n = stageStep, rows = tellOf(other).rows;
  const head = `<p class="tw-h"><span class="label">${far ? esc(paperName(other.p)) : "Beside it"}</span><b>${esc(nameOf(other))}</b>${far && n < rows.length ? `<span class="tw-n">step ${n}</span>` : ""}</p>`;
  const body = n >= rows.length ? sysHTML(other, `<p class="verdict">${ocMark(other.oc)}${VERDICT[other.oc]}</p><p>${esc(TAKE[other.key])}</p>`)
    : (!far && (d < 0 || n < d) ? `<p class="tw-same">${U().sameStep}</p>` : `<p class="say">${rows[n].say}</p>`) + (rows[n].aside ? sysHTML(other, `<p>${rows[n].aside}</p>`) : "");
  return panelHTML(sp.it).replace(/<\/div>$/, `<div class="twinp">${head}${body}</div></div>`);
}
// Which of the two pictures is up, where they take turns. It holds from step to step, and when the page is drawn again.
let pictSide = 0;
function showSide(i, smooth) {
  const p = $("pict"); if (!p || document.documentElement.dataset.swipe !== "1") return;
  pictSide = i; p.scrollTo({ left: i * p.clientWidth, behavior: smooth ? "smooth" : "auto" });
}
document.addEventListener("scroll", e => { const p = e.target; if (p.id === "pict" && p.clientWidth && document.documentElement.dataset.swipe === "1") pictSide = Math.round(p.scrollLeft / p.clientWidth); }, true);
// On a phone, under the picture, the scene's column is a sheet: its handle (a tap, or a swipe up or down) pulls it up over
// most of the picture to read, and back down to watch. It stays where the reader left it.
let sheetUp = false;
const sheetHandle = () => `<button type="button" class="sheet-h" data-sheet="1" aria-expanded="${sheetUp}" aria-label="${sheetUp ? "Show the picture" : "Show more of the step"}"><i></i></button>`;
function setSheet(up) {
  sheetUp = up; document.documentElement.dataset.sheet = up ? "up" : "";
  const b = document.querySelector(".sheet-h"); if (b) { b.setAttribute("aria-expanded", String(up)); b.setAttribute("aria-label", up ? "Show the picture" : "Show more of the step"); }
}
{ let y0 = null;
  document.addEventListener("pointerdown", e => { if (e.target.closest && e.target.closest(".sheet-h")) y0 = e.clientY; });
  document.addEventListener("pointerup", e => { if (y0 === null) return; const dy = e.clientY - y0; y0 = null; if (Math.abs(dy) > 24) { setSheet(dy < 0); swiped = true; } });
}
let swiped = false;      // a swipe on the handle ends in a click too: that click is the swipe's, not a tap
function toggleSheet() { if (swiped) { swiped = false; return; } setSheet(!sheetUp); }
function toggleAbout() {
  aboutOpen = !aboutOpen;
  const a = $("sabout"), b = document.querySelector(".sh-i"); if (a) a.hidden = !aboutOpen; if (b) b.setAttribute("aria-expanded", String(aboutOpen));
  layTheater();
}
function ctlHTML(it) {     // one circle per step
  const { rows, phases } = tellOf(it), atEnd = stageStep >= rows.length, n = atEnd ? -1 : stageStep;
  const cls = r => (r.t && JSON.stringify(r.perm) !== JSON.stringify(r.prevPerm) ? "p" : r.t && JSON.stringify(r.temp) !== JSON.stringify(r.prevTemp) ? "t" : "n")
    + (r.recv.some(m => m[0] !== "nothing") ? " r" : "") + (r.sent.length ? " s" : "") + (r.t === n ? " on" : "");
  const say = r => `Step ${r.t}: ${r.sayPlain}`;
  const dot = r => `<button type="button" class="sd ${cls(r)}" data-step="${r.t}" title="${esc(say(r))}" aria-label="${esc(say(r))}"${r.t === n ? ` aria-current="step"` : ""}>${r.t}</button>`;
  const ph = phases.length ? phases : [[0, ""]];
  const end = `<button type="button" class="sd fin${atEnd ? " on" : ""}" data-step="${rows.length}" title="${U().endStep}. ${VERDICT[it.oc]}" aria-label="${U().endStep}. ${VERDICT[it.oc]}"${atEnd ? ` aria-current="step"` : ""}><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">${OC[it.oc]}</svg></button>`;
  const groups = ph.map(([from, name], i) => `<div class="sg">${name ? `<span class="label">${esc(name)}</span>` : ""}<div class="dots">${rows.slice(from, i + 1 < ph.length ? ph[i + 1][0] : rows.length).map(dot).join("")}${i === ph.length - 1 ? end : ""}</div></div>`).join("");
  const k = U().strip;
  return `<div class="sctl" id="sctl">${povHTML(it)}
    <button type="button" class="btn sm arrow" data-stage="-1" aria-label="Previous step"${stageStep ? "" : " disabled"}><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M8.5 2.5L4 7l4.5 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button><div class="sgs">${groups}</div><button type="button" class="btn sm arrow" data-stage="1" aria-label="Next step"${atEnd ? " disabled" : ""}><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M5.5 2.5L10 7l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    <div class="sfoot"><div class="skey"><span><i class="sd p"></i>${k[0]}</span><span><i class="sd t"></i>${k[1]}</span><span><i class="sd n"></i>${k[2]}</span><span><i class="sd n r"></i>${k[3]}</span><span><i class="sd n s"></i>${k[4]}</span></div></div></div>`;
}
// The world view: what happened out of the node's sight. It is set into the telling at the step it belongs to, always in the second ink
// and a dashed frame, under an eye and a line saying whose sight it lies beyond, so it never reads as something the node knows.
const EYE = `<svg class="eye" width="17" height="12" viewBox="0 0 17 12" aria-hidden="true"><path d="M1 6c2.1-3.3 4.6-5 7.5-5s5.4 1.7 7.5 5c-2.1 3.3-4.6 5-7.5 5S3.1 9.3 1 6z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><circle cx="8.5" cy="6" r="2.3" fill="currentColor"/></svg>`;
const sysHTML = (it, body, cls = "") => `<div class="sys${cls ? " " + cls : ""}"><p class="sys-h">${EYE}<b>${U().seen}</b><span>${U().unseen(isleOf(it.p) ? whoOf(it) : "node " + whoOf(it))}</span></p>${body}</div>`;
const whoOf = it => { const I = isleOf(it.p), n = nmOf(I, it.s.who); return n ? "the " + esc(n) : (I ? esc(roleOf(I, it.s.who)) + " " : "") + ND(esc(it.s.who)); };
function timelineHTML(it, col, dv, only, bare) {      // only: one step's number, or "end"; the panel under the picture shows just that
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
      + `<div class="outb">${msgs(r.sent, "out", seen, r.t, I)}${r.aside ? sysHTML(it, `<p>${r.aside}</p>`) : ""}</div>`;
  });
  const through = whole ? "" : `, through step ${same},`;
  const twinLine = !tw ? "" : `${I ? cap(me) : "Node " + me} takes exactly these steps${through} in “${esc(nameOf(tw))}” too. Only the world differs.`;
  if (!solo || only === "end") tl += `<div class="band end"><span class="tm" aria-hidden="true"></span>
      <p>That is everything ${I ? me : "node " + me} can know.${tw ? " At least two different worlds look exactly like this from in here." : ""}</p>
      ${sysHTML(it, `<p class="verdict">${ocMark(it.oc)}${VERDICT[it.oc]}</p><p>${esc(TAKE[it.key])}${tw ? " " + twinLine : ""}</p>`)}
      ${solo && !bare && s.id === it.p.scenes[it.p.scenes.length - 1].id ? sumHTML(it.p) : ""}
    </div>`;
  return `<div class="tlw"><div class="tl">${tl}</div></div>`;
}
// The panel under the picture: the chosen step told in full, then what arrives, what the node keeps, and what leaves, left to right.
function panelHTML(it) {
  const s = it.s, I = isleOf(it.p), { rows, phases } = tellOf(it);
  if (stageStep >= rows.length) {      // the end: the verdict, then the way on (the next page in the reading order), again, or to the twin
    const nx = ORDER[ORDER.indexOf(it.key) + 1], nn = nx && (isPaper(nx) ? `${paperName(resolve(nx).p)}, introduction` : nameOf(byKey(nx)));
    return `<div class="panel" id="panel" aria-live="polite">${timelineHTML(it, 0, -1, "end")}<div class="ctl endnav">${nx ? `<button type="button" class="btn go-out" data-key="${nx}">Next: ${esc(nn)} →</button>` : ""}<button type="button" class="btn" data-step="0">Replay from the start</button>${twinBtn(it)}</div></div>`;
  }
  const r = rows[stageStep], seen = new Map(), ph = phases.filter(([from]) => from <= r.t).pop();
  rows.filter(x => x.t < r.t).forEach(x => msgs(x.sent, "out", seen, x.t, I));          // so a repeat reads "same order as step 2"
  const col = (cls, label, body, none) => `<div class="fcol ${cls}"><span class="label">${label}</span>${body || `<p class="none">${none}</p>`}</div>`;
  return `<div class="panel" id="panel" aria-live="polite"><div class="sp">
    ${ph ? `<p class="sp-ph"><b>${esc(ph[1])}</b>${ph[2] ? ` <i>${nodeText(ph[2], s)}</i>` : ""}</p>` : ""}
    <p class="say">${r.say}</p>
    <div class="flow">${col("fin", U().arrives, msgs(r.recv, "in", seen, r.t, I), U().noneIn)}${col("fst", U().kept, /class="kv/.test(stateBox(r, I)) ? stateBox(r, I) : "", U().noneKept)}${col("fout", U().leaves, msgs(r.sent, "out", seen, r.t, I), U().noneOut)}</div>
    ${r.aside ? sysHTML(it, `<p>${r.aside}</p>`) : ""}
  </div></div>`;
}
const noteOf = it => { if (it.pov) return ""; const O = ovOf(it); return O ? mk(O.note || "") : it.s.note ? nodeText(it.s.note, it.s) : ""; };
// What a scene is based on: the idea in the literature's own terms, and the paper it comes from. The same in both registers.
function basisHTML(it) {
  const b = BASIS[it.key]; if (!b) return "";
  const lines = it.p.cite.split("\n"), src = b[1].map(i => { const c = lines[i].replace(/^Related: /, ""), k = c.indexOf(" · "); return `<span>${esc(c.slice(0, k))}, <cite>${esc(c.slice(k + 3).replace(/ \(.*\)$/, ""))}</cite></span>`; }).join("");
  // the thread: each scene's part in the result's argument, this one marked, ending where the argument lands
  const A = ARC[it.p.id], arc = !A ? "" : `<div><dt class="label">Argument</dt><dd><ol class="arc" aria-label="Scene ${it.p.scenes.findIndex(x => x.id === it.s.id) + 1} of ${it.p.scenes.length} in the argument">${it.p.scenes.map(s => `<li><button type="button" data-key="${it.p.id}-${s.id}"${s.id === it.s.id ? ` aria-current="true"` : ""}>${esc(A.steps[s.id])}</button></li>`).join("")}<li class="fin">${esc(A.end)}</li></ol></dd></div>`;
  return `<dl class="basis"><div><dt class="label">Concept</dt><dd>${esc(b[0])}</dd></div><div><dt class="label">${b[1].length > 1 ? "Papers" : "Paper"}</dt><dd>${src}</dd></div>${arc}</dl>`;
}
// What a result's scenes add up to: each scene's outcome and takeaway side by side, then the idea that only follows from all of them.
// Shown at the end of the result's last scene, and (the idea alone) on the result's own page under its list of scenes.
const COUNT = ["", "", "two", "three", "four", "five"];
function sumHTML(p, bare) {
  const A = ARC[p.id]; if (!A) return "";
  const xs = p.scenes.map(s => byKey(`${p.id}-${s.id}`)), n = COUNT[xs.length] || xs.length;
  const list = bare ? "" : `<ul>${xs.map(x => `<li>${ocMark(x.oc)}<button type="button" data-key="${x.key}">${esc(nameOf(x))}</button><span>${esc(TAKE[x.key])}</span></li>`).join("")}</ul>`;
  return `<section class="sum"><p class="label">What the ${n} scenes add up to</p>${list}<p class="together">${bare ? "" : `<b class="label">Together</b>`}${esc(A.sum[reg === "isle" ? 1 : 0])}</p></section>`;
}
const pointHTML = it => `<p class="point"><span class="label">${U().point}: </span>${esc(TAKE[it.key])}</p>`;
function castHTML(it) {
  const s = it.s, I = isleOf(it.p), O = it.pov ? {} : ovOf(it);      // another node's view has none of the narrator's own words
  if (!I) return `You are inside node <span class="nd">${esc(s.who)}</span>${s.role ? `, ${/^(coordinator|primary)$/.test(s.role) ? "the" : "a"} ${esc(s.role)}` : ""}. Out there: ${nodeText(s.peers, s)}.`;
  const ls = s.peers.match(/\b[A-Z]\b/g) || [];
  if (I.names) return `You run the ${esc(I.names[s.who])}. You hear from ${listAnd(ls.map(l => "the " + esc(I.names[l])))}, and only by courier.`;
  const r0 = roleOf(I, ls[0]), same = ls.every(l => roleOf(I, l) === r0);
  const peers = O.peers ? mk(O.peers) : I.peers && !it.pov ? mk(I.peers) : same ? `${r0}${ls.length > 1 ? "s" : ""} ${listAnd(ls.map(ND))}` : listAnd(ls.map(l => `${roleOf(I, l)} ${ND(l)}`));
  return `You are ${esc(roleOf(I, s.who))} ${ND(esc(s.who))}${O.as ? `, ${esc(O.as)}` : ""}. You hear from ${peers}, and only by courier.`;
}
function sceneHTML(base) {
  const it = viewOf(base), { p, s } = it, I = isleOf(p);
  const other = it.pov ? null : byKey(PAIR[it.key]), both = cmp && other;      // a comparison is of the two scenes as told
  if (beside && splitOf()) return `<div class="player">${splitHTML(splitOf())}</div>`;      // a scene of another result beside it, from a comparison
  const cmpBtn = other ? `<button type="button" class="btn sm" data-cmp="1" aria-pressed="${!!both}">${both ? "Close comparison" : `Compare with “${esc(nameOf(other))}”`}</button>` : "";
  let body;
  if (both) {
    const d = firstDiff(s, other.s);
    const column = (x, n) => `<section class="col"><h3>${esc(nameOf(x))}${ocMark(x.oc)}</h3>${pointHTML(x)}${noteOf(x) ? `<p class="rule">${noteOf(x)}</p>` : ""}${timelineHTML(x, n, d)}</section>`;
    body = `<p class="cmpnote">${d < 0 ? U().same : d === 0 ? U().differ0 : U().until(d)}</p><div class="cmp">${column(it, 0)}${column(other, 1)}</div>`;
  } else body = `<div class="player">${stripHTML(it)}</div>`;
  if (!both && stageOf(it)) return body;
  if (both && stageOf(it)) return `<div class="player">${splitHTML(splitOf())}</div>`;
  return `<div class="scene-head">
      <div class="stitle"><h2>${esc(nameOf(it))}</h2>${cmpBtn ? `<div class="ctl">${cmpBtn}</div>` : ""}</div>
      ${both ? "" : pointHTML(it)}
      ${basisHTML(it)}
      <p class="cast">${castHTML(it)}</p>
      ${noteOf(it) && !both ? `<p class="rule">${noteOf(it)}</p>` : ""}
    </div>
    ${body}
    ${pagerHTML(it.key)}`;
}

// The map: which result answers a problem another one raises.
const MAP_EDGES = [["clocks", "snapshot", "a state that could have been"], ["clocks", "cops", "causes before effects"], ["flp", "benor", "or flip a coin"], ["flp", "suspect", "so guess, and allow mistakes"],
    ["suspect", "paxos", "stay safe whatever the timing"], ["paxos", "vr", "one value becomes a stream"], ["commit", "paxos", "a majority, not all"], ["flp", "cap", "the same blindness, for reads"],
    ["linear", "cap", "what lost messages take away"], ["cap", "quorum", "wait for some copies, not all"], ["quorum", "merge", "or never wait, and merge"], ["merge", "bayou", "when merging needs one order"],
    ["liars", "pbft", "the same, for a stream"], ["vr", "pbft", "the same, among liars"]];
function mapHTML() {
  const X = [20, 260, 500, 740], Y = [30, 150, 270, 390, 510], W = 196, H = 58, isle = reg === "isle";
  const at = { snapshot: [0, 0], clocks: [0, 1], cops: [0, 2], commit: [0, 3], benor: [1, 0], flp: [1, 1], suspect: [1, 2], paxos: [1, 3], vr: [1, 4],
    liars: [2, 3], pbft: [2, 4], linear: [3, 0], cap: [3, 1], quorum: [3, 2], merge: [3, 3], bayou: [3, 4] };
  let g = "";
  MAP_EDGES.forEach(([a, b, label]) => {
    const [ca, ra] = at[a], [cb, rb] = at[b];
    g += `<g class="mx" role="button" tabindex="0" data-key="cmp=${a}~${b}" aria-label="Compare ${esc(paperName(pById(a)))} with ${esc(paperName(pById(b)))}: ${esc(label)}"><title>Compare the two</title>`;
    if (ca === cb) {
      const x = X[ca] + 26, down = rb > ra, y1 = down ? Y[ra] + H : Y[ra], y2 = down ? Y[rb] : Y[rb] + H, k = down ? -8 : 8;
      g += `<path class="me" d="M${x} ${y1}V${y2 + k}"/><path class="mh" d="M${x - 5} ${y2 + k}L${x} ${y2}L${x + 5} ${y2 + k}z"/><text class="ml" x="${x + 12}" y="${(y1 + y2) / 2 + 4}">${esc(label)}</text><path class="mhit" d="M${x} ${y1}V${y2}"/></g>`;
    } else {
      const y = Y[ra] + H / 2, x1 = X[ca] + W, x2 = X[cb], far = cb - ca > 1;
      g += `<path class="me" d="M${x1} ${y}H${x2 - 8}"/><path class="mh" d="M${x2 - 8} ${y - 5}L${x2} ${y}L${x2 - 8} ${y + 5}z"/><text class="ml" text-anchor="${far ? "middle" : "end"}" x="${far ? (x1 + x2) / 2 : x2 + 18}" y="${far ? y - 9 : Y[ra] + H + 18}">${esc(label)}</text><path class="mhit" d="M${x1} ${y}H${x2}"/></g>`;
    }
  });
  PAPERS.forEach(p => {
    const [c, r] = at[p.id], x = X[c], y = Y[r], n = p.scenes.length;
    g += `<g class="mn" role="button" tabindex="0" data-key="${p.id}" aria-label="${esc(paperName(p))}: ${esc(p.name)}"><rect x="${x}" y="${y}" width="${W}" height="${H}" rx="5"/><text class="n1" x="${x + 13}" y="${y + 25}">${esc(paperName(p))}</text><text class="n2" x="${x + 13}" y="${y + 44}">${esc(isle ? HAT[TELL[p.id].hat][0] : `${p.year} · ${n} ${n === 1 ? "scene" : "scenes"}`)}</text></g>`;
  });
  const svg = `<div class="mapbox"><svg viewBox="0 0 980 610" role="group" aria-label="How the sixteen lead to one another">${g}</svg></div>`;
  const words = [["Courier", "A message. It may be slow, lost, or overtaken by a later one."], ["Ledger", "Permanent state. It passes to whoever takes over."], ["Slate", "Temporary state. It is wiped when its owner goes."],
    ["Hourglass", "A timer. It says how long you have waited, never why."], ["Successor", "A replacement, who starts from the ledger alone."], ["World view", "Everything that happened, everywhere, seen from above. Nobody in " + ALLEGORY.town + " has it. Here it is set beside the telling, in a dashed frame."]];
  const items = list => `<ul class="customs">${list.map(([a, b]) => `<li><span class="label">${a}</span>${b}</li>`).join("")}</ul>`;
  const sect = (label, body) => `<section class="sect"><p class="label">${label}</p>${body}</section>`;
  // on the stage: the map on the left, where the window is wide enough (else at the top of the text), the words on the right
  const pane = `${theaterHead("map")}<div class="ipict mpict">${svg}</div>`;
  if (isle) return `${pane}<div class="map">
    <div class="intro"><h1>${U().map}</h1>
      <p class="idea">The sixteen results, each marked with who tells it. An arrow leads from one result to another that answers the problem it raises, or builds on it. Pick a result to open it, or an arrow to set the two side by side.</p></div>
    ${sect("Four kinds of work, four kinds of problem", items(Object.values(HAT)))}
    ${sect("Six words used everywhere", items(words))}
    ${sect("About the telling", `<p class="fine">Those who do the work have no names: a role and a letter, the same letter in both tellings. The merchants are the one exception. Their three businesses, the ${esc(CITY.label.fishery)}, the ${esc(CITY.label.granary)} and the ${esc(CITY.label.winery)}, stand in for A, B and C, and a notary for K. A few of the people they serve are named, such as Ann and Bob, who book the reading room. What is asked for and decided is specific here, such as a colour for the ${esc(CITY.label.temple)} columns or an order for ${ALLEGORY.fill("grain")}, but the steps are the same.</p>`)}
  </div>`;
  return `${pane}<div class="map">
    <div class="intro"><h1>${U().map}</h1>
      <p class="idea">The sixteen results and how they connect. An arrow leads from one result to another that answers the problem it raises, or builds on it. Pick a result to open it, or an arrow to compare the two.</p></div>
  </div>`;
}
