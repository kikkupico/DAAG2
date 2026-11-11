// ---------- the stage: the island picture, with one step's couriers drawn on its roads ----------
let stageStep = 0;
const stageOf = it => { const T = TELL[it.p.id]; return T && T.stage && typeof STAGES !== "undefined" && STAGES[T.stage.view] ? T.stage : null; };
function routePts(G, a, b) {   // the shortest way by road from one place to another, as fractions of the picture
  const len = pts => pts.slice(1).reduce((s, p, i) => s + Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]), 0), next = {};
  Object.entries(G.roads).forEach(([k, pts]) => { const i = k.indexOf("-"), x = k.slice(0, i), y = k.slice(i + 1); (next[x] = next[x] || []).push([y, pts]); (next[y] = next[y] || []).push([x, [...pts].reverse()]); });
  const direct = (next[a] || []).find(([v]) => v === b); if (direct) return direct[1];
  const best = { [a]: [0, []] }, todo = new Set([a]);
  while (todo.size) {
    const u = [...todo].sort((p, q) => best[p][0] - best[q][0])[0]; todo.delete(u);
    (next[u] || []).forEach(([v, pts]) => { const d = best[u][0] + len(pts); if (!best[v] || d < best[v][0]) { best[v] = [d, [...best[u][1], ...pts]]; todo.add(v); } });
  }
  return best[b] && best[b][1].length ? best[b][1] : [G.places[a], G.places[b]];
}
function along(pts, t) {    // the point a fraction t of the way along a line of points
  const L = pts.slice(1).map((p, i) => Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1])); let d = t * L.reduce((a, b) => a + b, 0);
  for (let i = 0; i < L.length; i++) { if (d <= L[i] || i === L.length - 1) { const f = L[i] ? Math.min(1, d / L[i]) : 0; return [pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f]; } d -= L[i]; }
  return pts[0];
}
// In the Abstraction register the same layout is drawn as a diagram: each node where its place is on the island, straight
// links between the nodes, and the messages with their own names. No picture and no close-up.
function diagramHTML(it, S, G) {
  const { rows } = tellOf(it), n = Math.min(stageStep, rows.length - 1), r = rows[n], W = 1000, H = Math.round(W * G.h / G.w);
  const px = p => [p[0] * W, p[1] * H], fx = v => v.toFixed(1), me = it.s.who;
  const nodes = [...new Set([it.s.who, ...(it.s.peers.match(/\b[A-Z]\b/g) || [])])].filter(l => S[l] && G.places[S[l]]), at = l => px(G.places[S[l]]);
  const decided = r.perm && typeof r.perm.decided === "string" && r.perm.decided !== "none" ? r.perm.decided : "", you = "you" + (decided ? ", decided " + decided : "");
  const boxes = nodes.map(l => [at(l)[0], at(l)[1], 44]).concat(S[me] && G.places[S[me]] ? [[at(me)[0], at(me)[1] + 35, you.length * 7.6 + 10]] : []);   // the nodes, and the label under your own
  const clear = (x, y, text) => {        // above the dot if there is room, else beside it, else further up
    const w = text.length * 8.4 + 10, h = 17, hit = (cx, cy) => boxes.some(b => Math.abs(b[0] - cx) < (b[2] + w) / 2 && Math.abs(b[1] - cy) < h + 8);
    const keep = cx => Math.max(w / 2 + 4, Math.min(W - w / 2 - 4, cx));      // labels stay inside the frame
    const tries = [[0, 0], [w / 2 + 12, 17], [-w / 2 - 12, 17], [0, 33], [0, -19], [w / 2 + 12, -2], [-w / 2 - 12, -2], [0, 52], [0, -38], [0, -57]];
    const [dx, dy] = tries.find(([dx, dy]) => !hit(keep(x + dx), y + dy)) || tries[0];
    boxes.push([keep(x + dx), y + dy, w]); return [keep(x + dx), y + dy]; };
  const line = pts => pts.map(p => p.map(fx).join(",")).join(" ");
  let roads = "";
  nodes.forEach((a, i) => nodes.slice(i + 1).forEach(b => { roads += `<polyline class="rd" points="${line([at(a), at(b)])}"/>`; }));
  let g = "";
  const message = ([peer, text, lost], dir, k) => {
    const from = peer === "outside" ? (S.client && G.places[S.client] ? null : undefined) : peer; if (from === undefined || !text || (peer !== "outside" && !S[peer])) return;
    const far = peer === "outside" ? px(G.places[S.client]) : at(peer), pts = dir === "in" ? [far, at(me)] : [at(me), far];
    const [x, y] = along(pts, lost ? .5 : dir === "in" ? .78 : .22 + .1 * k), label = text + (lost ? " ✕" : "");
    g += `<g class="cr ${dir}${lost ? " xo lostc" : ""}"><polyline points="${line(pts)}"/><circle cx="${fx(x)}" cy="${fx(y)}" r="6"/>${(([lx, ly]) => `<text x="${fx(lx)}" y="${fx(ly)}" text-anchor="middle">${esc(label)}</text>`)(clear(x, y - 12, label))}</g>`;
  };
  r.recv.forEach((m, k) => message(m, "in", k)); r.sent.forEach((m, k) => message(m, "out", k));
  const client = S.client && G.places[S.client] && [...r.recv, ...r.sent].some(m => m[0] === "outside") ? (([x, y]) => `<g class="nd cl"><rect x="${fx(x - 15)}" y="${fx(y - 15)}" width="30" height="30" rx="4"/><text x="${fx(x)}" y="${fx(y + 32)}" text-anchor="middle" class="nl">client</text></g>`)(px(G.places[S.client])) : "";
  const dots = nodes.map(l => { const [x, y] = at(l);
    return `<g class="nd${l === me ? " me" : ""}"><circle cx="${fx(x)}" cy="${fx(y)}" r="19"/><text x="${fx(x)}" y="${fx(y + 6)}" text-anchor="middle" class="ll">${l}</text>${l === me ? `<text x="${fx(x)}" y="${fx(y + 40)}" text-anchor="middle" class="nl">${esc(you)}</text>` : ""}</g>`; }).join("");
  const [mx] = at(me) || [W / 2];
  return `<figure class="stage abs" id="stage" data-mx="${(mx / W).toFixed(3)}" style="--ar:${(G.w / G.h).toFixed(3)}"><div class="stv"><div class="stw"><div class="stg"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Nodes ${esc(nodes.join(", "))} and the links between them, with this step's messages.">${roads}${g}${client}${dots}</svg></div></div></div></figure>`;
}
// ---------- the city stage: the isometric city from world/city_mockup.py, with messengers walking its roads ----------
// A step plays as a short animation: timers ring at your place, messengers arriving walk in along the roads, the step happens
// at your place (a ring), then messengers leaving walk out. Each leaves a trail; a lost one stops partway. Replay runs it again.
const cityRoute = (a, b) => {
  const r = a === b ? null : CITY.routes[a < b ? a + "|" + b : b + "|" + a];
  return r ? (a < b ? r : [...r].reverse()) : [CITY.doors[a], CITY.doors[b]];
};
const polyLen = pts => pts.slice(1).reduce((s, p, i) => s + Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]), 0);
const clamp01 = v => Math.max(0, Math.min(1, v));
function cityCast(it, S) {
  const inScene = new Set([it.s.who, ...(it.s.peers.match(/\b[A-Z]\b/g) || [])]);
  return [...new Set(["A", "B", "C", "D", "P", "Q", "S", "K"].filter(k => inScene.has(k)).map(k => S[k]).filter(k => k && CITY.places[k]))];
}
function cityTrips(it, S) {        // this step's messages as walks along the roads, and timers
  const { rows } = tellOf(it), r = rows[Math.min(stageStep, rows.length - 1)], I = isleOf(it.p), me = S[it.s.who], trips = [];
  const say = (text, peer, dir) => I ? lexT(I.msg && !PSEUDO.has(peer) ? I.msg(text, peer, dir) : text, I) : text;
  const add = ([peer, text, lost], dir) => {
    if (!text || peer === "nothing") return;
    if (peer === "timer") { trips.push({ kind: "here", icon: "⌛", label: say(text, peer, dir) }); return; }
    if (peer === "outside" && I && clientOf(I, say(text, peer, dir)) !== I.client) {      // the node's own need, or a due date: nobody walks in, it starts at your place
      trips.push({ kind: "here", icon: "✦", label: clientOf(I, say(text, peer, dir)) + ": " + say(text, peer, dir) }); return; }
    const pl = peer === "outside" ? S.client : S[peer]; if (!pl || !CITY.doors[pl]) return;
    trips.push({ kind: "walk", dir, lost: !!lost, outside: peer === "outside", from: dir === "in" ? pl : me, to: dir === "in" ? me : pl, label: say(text, peer, dir) + (lost ? " ✕" : "") });
  };
  r.recv.forEach(m => add(m, "in")); r.sent.forEach(m => add(m, "out"));
  trips.forEach(x => { if (x.kind === "walk") { x.pts = cityRoute(x.from, x.to); x.len = polyLen(x.pts); } });
  return { r, me, trips };
}
const cityBox = () => [0, 0, CITY.w, CITY.h];      // the whole picture, at its own 4:3, for every scene
function cityPlaces(it, S) {       // the names of the scene's places, yours marked, and what you have decided
  const { r, me, trips } = cityTrips(it, S), I = isleOf(it.p), fx = v => v.toFixed(1);
  const title = k => (S.labels && S.labels[k]) || (/^(legislator|proposer|camp) /.test(k) ? k : "the " + k);
  const shown = [...new Set([...cityCast(it, S), ...(trips.some(x => x.outside) ? [S.client] : []), ...(S.also || []).filter(k => CITY.places[k])])];
  const decided = r.perm && typeof r.perm.decided === "string" && r.perm.decided !== "none" ? (I ? lexT(r.perm.decided, I) : r.perm.decided) : "";
  return shown.map(k => { const [x, y] = CITY.places[k], name = title(k) + (k === me ? " (you)" : "");
    return `<g class="cpl${k === me ? " me" : ""}"><circle class="pin" cx="${fx(x)}" cy="${fx(y)}" r=".4em"/><text x="${fx(x)}" y="${fx(y)}" dy="1.9em" text-anchor="middle">${esc(name)}</text>${k === me && decided ? `<circle class="dec d${esc(decided)}" cx="${fx(x)}" cy="${fx(y)}" r=".55em" transform="translate(0 -40)"/><text class="dect" x="${fx(x)}" y="${fx(y - 40)}" dx=".9em" dy=".35em">decided ${esc(decided)}</text>` : ""}</g>`; }).join("");
}
function cityHTML(it, S) {
  const [bx, by, bw, bh] = cityBox(it, S), u = bw / 650, me = S[it.s.who], [mx] = CITY.places[me];
  return `<figure class="stage city" id="stage" data-scene="${esc(it.key)}" data-u="${u.toFixed(3)}" data-mx="${((mx - bx) / bw).toFixed(3)}" style="--ar:${(bw / bh).toFixed(3)}"><div class="stv"><div class="stw"><div class="stg">`
    + `<svg viewBox="${[bx, by, bw, bh].map(v => v.toFixed(1)).join(" ")}" style="font-size:${(15 * u).toFixed(2)}px" role="img" aria-label="The city from above: ${esc(cityCast(it, S).join(", "))}, and the roads between them. This step's messengers walk the roads.">`
    + `<g class="world">${CITY.svg}</g><g class="trips"></g><g class="places">${cityPlaces(it, S)}</g></svg></div></div>`
    + `<button type="button" class="replay" data-replay="1" aria-label="Replay this step's messengers"><svg width="13" height="13" viewBox="0 0 14 14" aria-hidden="true"><path d="M11.5 7A4.5 4.5 0 1 1 7 2.5h2.5M8 .5l2 2-2 2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>Replay</button></div></figure>`;
}
let cityAnim = 0;
function playCity() {
  cancelAnimationFrame(cityAnim);
  const fig = $("stage"), it = byKey(sel), S = it && stageOf(it); if (!fig || !fig.classList.contains("city") || !S) return;
  const { me, trips } = cityTrips(it, S), u = +fig.dataset.u, layer = fig.querySelector(".trips"), [px, py] = CITY.places[me], fx = v => v.toFixed(1);
  // the schedule, in seconds: timers, then arrivals, then the step itself at your place, then departures
  const SPEED = 560, walk = (x, k, t0) => { x.stop = x.lost ? .55 : 1; x.start = t0 + .25 * k; x.dur = Math.min(2.8, Math.max(.9, x.len / SPEED)) * x.stop; x.end = x.start + x.dur; };
  const timers = trips.filter(x => x.kind === "here"), ins = trips.filter(x => x.dir === "in"), outs = trips.filter(x => x.dir === "out");
  let t = .25; timers.forEach(x => { x.start = t; x.end = t + .5; }); if (timers.length) t += .9;
  ins.forEach((x, k) => walk(x, k, t));
  const here = ins.length ? Math.max(...ins.map(x => x.end)) + .1 : t;
  outs.forEach((x, k) => walk(x, k, here + (ins.length || timers.length ? .5 : 0)));
  const T = Math.max(here + .9, ...trips.map(x => x.end + .7));
  const ends = {}; trips.forEach(x => { if (x.kind === "walk") { const e = x.lost ? "lost" + x.to : x.to; x.stack = ends[e] = (ends[e] || 0) + 1; } });   // tags at one place stack up
  const line = pts => pts.map(p => p.join(",")).join(" ");
  layer.innerHTML = trips.map(x => x.kind === "here"
    ? `<g class="tmr"><text x="${fx(px)}" y="${fx(py)}" dy="-2.2em" dx="${px < CITY.w * .3 ? "-1em" : px > CITY.w * .7 ? "1em" : "0"}" text-anchor="${px < CITY.w * .3 ? "start" : px > CITY.w * .7 ? "end" : "middle"}">${x.icon} ${esc(x.label)}</text></g>`
    : `<g class="trip ${x.dir}${x.lost ? " lost" : ""}"><polyline class="way" points="${line(x.pts)}"/><polyline class="trail" points="${line(x.pts)}" stroke-dasharray="${fx(x.len)} ${fx(x.len)}" stroke-dashoffset="${fx(x.len)}"/>`
      + `<g class="mx" opacity="0"><g transform="scale(${(u * .8).toFixed(3)})"><ellipse class="sh" rx="10" ry="3.6" cy="1"/><g class="bob"><circle r="11" cy="-9"/><rect class="scroll" x="-6" y="-13" width="12" height="8" rx="2"/><path class="scroll" d="M-3.5 -10.5h7M-3.5 -7.5h5"/></g></g></g>`
      + `<text class="tag" text-anchor="middle" opacity="0">${esc(x.label)}</text><text class="xx" text-anchor="middle" dy=".35em" opacity="0">✕</text></g>`).join("")
    + `<circle class="pulse" cx="${fx(px)}" cy="${fx(py)}" r="0" opacity="0"/>`;
  const gs = [...layer.children], pulse = layer.querySelector(".pulse");
  const frame = now => {
    const t = (now - t0) / 1000;
    trips.forEach((x, i) => {
      const g = gs[i];
      if (x.kind === "here") { const a = clamp01((t - x.start) / .4); g.setAttribute("opacity", a); g.setAttribute("transform", `translate(${fx(px * (1 - (.7 + .3 * a)))} ${fx(py * (1 - (.7 + .3 * a)))}) scale(${(.7 + .3 * a).toFixed(3)})`); return; }
      const f = clamp01((t - x.start) / x.dur), p = f * x.stop, [cx, cy] = along(x.pts, p), done = t >= x.end, after = clamp01((t - x.end) / .45);
      const [trail, mx, tag, xx] = [g.children[1], g.children[2], g.children[3], g.children[4]];
      trail.setAttribute("stroke-dashoffset", fx(x.len * (1 - p)));
      mx.setAttribute("opacity", t < x.start ? 0 : done ? 1 - after : 1);
      mx.setAttribute("transform", `translate(${fx(cx)} ${fx(cy)})`);
      mx.children[0].children[1].setAttribute("transform", `translate(0 ${done ? 0 : fx(-Math.abs(Math.sin(t * 11)) * 3)})`);   // a little bounce as it walks
      tag.setAttribute("opacity", t < x.start ? 0 : 1); tag.setAttribute("x", fx(cx)); tag.setAttribute("y", fx(cy - (28 + (done ? 22 * (x.stack - 1) : 0)) * u));
      if (x.lost) { xx.setAttribute("x", fx(cx)); xx.setAttribute("y", fx(cy)); xx.setAttribute("opacity", done ? after : 0); }
    });
    const a = clamp01((t - here) / .8); pulse.setAttribute("r", fx((8 + 46 * a) * u)); pulse.setAttribute("opacity", t < here ? 0 : (1 - a).toFixed(3));
    if (t < T) cityAnim = requestAnimationFrame(frame);
  };
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches, t0 = performance.now() - (still ? T * 1000 : 0);
  cityAnim = requestAnimationFrame(frame);
}
document.addEventListener("click", e => { if (e.target.closest && (e.target.closest("[data-replay]") || e.target.closest(".stage.city svg"))) playCity(); });

function stageHTML(it) {
  const S = stageOf(it); if (!S) return "";
  if (reg !== "isle") return diagramHTML(it, S, STAGES[S.view]);
  if (S.view === "city") return cityHTML(it, S);
  const G = STAGES[S.view], I = isleOf(it.p), { rows } = tellOf(it), n = Math.min(stageStep, rows.length - 1), r = rows[n], W = 1000, H = Math.round(W * G.h / G.w), me = S[it.s.who];
  const px = p => [p[0] * W, p[1] * H], fx = v => v.toFixed(1), title = k => (S.labels && S.labels[k]) || G.label[k] || (/^(legislator|proposer|camp) /.test(k) ? k : "the " + k);
  let g = ""; const boxes = [];
  const clear = (x, y, text) => {        // move a label up until it overlaps no earlier one
    const w = text.length * 7.8 + 8, h = 17;
    for (let i = 0; i < 6; i++) { if (!boxes.some(b => Math.abs(b[0] - x) < (b[2] + w) / 2 && Math.abs(b[1] - y) < h)) break; y -= h + 1; }
    boxes.push([x, y, w]); return y;
  };
  const drop = (x, y, text) => {
    const w = text.length * 7.8 + 8, h = 17;
    for (let i = 0; i < 4; i++) { if (!boxes.some(b => Math.abs(b[0] - x) < (b[2] + w) / 2 && Math.abs(b[1] - y) < h)) break; y += h + 1; }
    boxes.push([x, y, w]); return y;
  };
  const courier = ([peer, text, lost], dir, k) => {
    const pl = peer === "outside" ? S.client : S[peer]; if (!pl || !text) return;
    const pts = (dir === "in" ? routePts(G, pl, me) : routePts(G, me, pl)).map(px), [x, y] = along(pts, lost ? .5 : dir === "in" ? .8 : .2 + .1 * k);
    const label = lexT(I.msg && !PSEUDO.has(peer) ? I.msg(text, peer, dir) : text, I);
    g += `<g class="cr ${dir}${lost ? " xo lostc" : ""}"><polyline points="${pts.map(p => p.map(fx).join(",")).join(" ")}"/><circle cx="${fx(x)}" cy="${fx(y)}" r="7"/><text x="${fx(x)}" y="${fx(clear(x, y - 13, label + (lost ? " ✕" : "")))}" text-anchor="middle">${esc(label)}${lost ? " ✕" : ""}</text></g>`;
  };
  const inScene = new Set([it.s.who, ...(it.s.peers.match(/\b[A-Z]\b/g) || [])]);
  const cast = [...new Set(["A", "B", "C", "D", "P", "Q", "S", "K"].filter(k => inScene.has(k)).map(k => S[k]).filter(Boolean))], shown = [...cast, ...(S.also || [])];
  const decided = r.perm && typeof r.perm.decided === "string" && r.perm.decided !== "none" ? lexT(r.perm.decided, I) : "";
  const places = shown.map(k => { const [x, y] = px(G.places[k]);
    const ly = drop(x, y + 30, title(k) + (k === me ? " (you)" : ""));    // a name that would sit on another name moves down below it
    return `<g class="pl${k === me ? " me" : ""}"><text x="${fx(x)}" y="${fx(ly)}" text-anchor="middle">${esc(title(k))}${k === me ? " (you)" : ""}</text>${k === me && decided ? `<circle class="dec d${esc(decided)}" cx="${fx(x - 52)}" cy="${fx(y + 48)}" r="9"/><text class="dect" x="${fx(x - 38)}" y="${fx(y + 53)}">decided ${esc(decided)}</text>` : ""}</g>`; }).join("");
  r.recv.forEach((m, k) => courier(m, "in", k)); r.sent.forEach((m, k) => courier(m, "out", k));
  const [mx, my] = px(G.places[me]);
  // the close-up goes in a corner with nothing of this scene's in it: no place, no road between its places. Failing that, below the picture.
  let corner = "below";
  if (G.inset && G.inset[me]) {
    const avoid = cast.flatMap(a => cast.filter(b => b > a).flatMap(b => routePts(G, a, b).map(px))).concat(shown.map(k => px(G.places[k])));
    const iw = 285, ih = 215, rects = { "r t": [W - iw, 0], "l t": [0, 0], "r b": [W - iw, H - ih], "l b": [0, H - ih] };
    const order = Object.keys(rects).sort((p, q) => Math.hypot(rects[q][0] + iw / 2 - mx, rects[q][1] + ih / 2 - my) - Math.hypot(rects[p][0] + iw / 2 - mx, rects[p][1] + ih / 2 - my));
    corner = order.find(c => !avoid.some(([x, y]) => x > rects[c][0] - 30 && x < rects[c][0] + iw + 30 && y > rects[c][1] - 40 && y < rects[c][1] + ih + 20)) || "below";
  }
  const inset = G.inset && G.inset[me] ? `<div class="inset ${corner}"><img src="${CLOSEUPS[me]}" alt="${esc(title(me))}, up close."><span>Up close: ${esc(title(me))}</span></div>` : "";
  return `<figure class="stage" id="stage" data-mx="${(mx / W).toFixed(3)}" style="--ar:${(G.w / G.h).toFixed(3)}"><div class="stv">${corner === "below" ? "" : inset}<div class="stw"><div class="stg"><img src="${PICTURES[G.img]}" alt="Paxos from above: ${esc(shown.map(title).join(", "))}, and the roads between them.">
    <svg viewBox="0 0 ${W} ${H}" aria-hidden="true">${g}${places}</svg></div></div></div>${corner === "below" ? inset : ""}</figure>`;
}
function centreStage() { playCity(); const f = $("stage"), s = f && f.querySelector && f.querySelector(".stw"); if (!s) return; if (s.scrollWidth > s.clientWidth) s.scrollLeft = +f.dataset.mx * s.scrollWidth - s.clientWidth / 2; }
function refreshStepper() { const it = byKey(sel), el = $("sctl"); if (!it || !el) return; el.outerHTML = ctlHTML(it, !!$("pict")); }
function showStep(n) {
  const it = byKey(sel); if (!it) return;
  stageStep = Math.max(0, Math.min(it.s.rows.length + 1, n)); refreshStage(); refreshStepper();      // one past the last step is the end
  const p = $("panel"); if (p) p.outerHTML = panelHTML(it);
}
// Left and right arrows step through the scene, unless a field or the drawer's buttons have the keys.
document.addEventListener("keydown", e => {
  if (e.altKey || e.ctrlKey || e.metaKey || !$("panel") || (e.key !== "ArrowLeft" && e.key !== "ArrowRight")) return;
  if (e.target.closest && e.target.closest("input, textarea, select, #drawer")) return;
  e.preventDefault(); showStep(stageStep + (e.key === "ArrowRight" ? 1 : -1));
  const b = document.querySelector(".stepbar .sd.on"); if (b && document.activeElement && document.activeElement.closest && document.activeElement.closest(".stepbar")) b.focus();
});
// The picture inside the stepper box folds away, and stays folded across steps and scenes.
let picOpen = true;
try { if (localStorage.getItem("pic") === "shut") picOpen = false; } catch (e) {}
function togglePic() {
  picOpen = !picOpen; try { localStorage.setItem("pic", picOpen ? "open" : "shut"); } catch (e) {}
  const p = $("pict"); if (p) p.hidden = !picOpen; refreshStepper(); if (picOpen) centreStage();
  const t = document.querySelector(".pictog"); if (t) t.focus();
}
function refreshStage() {
  const it = byKey(sel), el = $("stage"); if (!it || !el) return;
  if (el.classList.contains("city") && el.dataset.scene === it.key && reg === "isle") { el.querySelector(".places").innerHTML = cityPlaces(it, stageOf(it)); playCity(); return; }   // same scene: keep the picture, replay the step
  const keep = el.querySelector(".stw").scrollLeft; el.outerHTML = stageHTML(it); const s = $("stage") && $("stage").querySelector(".stw"); if (s) s.scrollLeft = keep; playCity();
}

