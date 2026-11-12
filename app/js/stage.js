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
// ---------- the city stage: the isometric city from world/city_mockup.py, with messengers walking its roads ----------
// A step plays as a short animation: timers ring at your place, messengers arriving walk in along the roads, the step happens
// at your place (a ring), then messengers leaving walk out. Each leaves a trail; a lost one stops partway. Replay runs it again.
// The geometry a stage plays on: the city from world/city_mockup.py, or, for scenes not yet moved to it (the army's), an older
// island picture with its places and roads. Each entry point below sets GEO from its scene's stage before drawing.
const GEOS = {};
function geoFor(S) {
  if (S.view === "city") return CITY;
  if (S.view === "siege") return SIEGE;
  if (GEOS[S.view]) return GEOS[S.view];
  const G = STAGES[S.view], W = 1600, H = Math.round(W * G.h / G.w), px = p => [+(p[0] * W).toFixed(1), +(p[1] * H).toFixed(1)];
  const places = Object.fromEntries(Object.entries(G.places).map(([k, p]) => [k, px(p)]));
  return GEOS[S.view] = { w: W, h: H, places, doors: places, label: G.label || {}, route: (a, b) => routePts(G, a, b).map(px),
    svg: `<image href="${PICTURES[G.img]}" width="${W}" height="${H}" preserveAspectRatio="none"/>`,
    plain: { street: "", road: Object.values(G.roads).map(pts => "M" + pts.map(q => px(q).join(",")).join("L")).join("") },
    iso: { e: [3.3, 1.65], n: [3.3, -1.65], u: [0, -2.9] } };      // the island renders' camera, near enough for the blocks
}
let GEO = typeof CITY !== "undefined" ? CITY : null;
const useGeo = S => (GEO = geoFor(S));
const cityRoute = (a, b) => {
  if (GEO.route) return a === b ? [GEO.doors[a], GEO.doors[a]] : GEO.route(a, b);
  const r = a === b ? null : GEO.routes[a < b ? a + "|" + b : b + "|" + a];
  return r ? (a < b ? r : [...r].reverse()) : [GEO.doors[a], GEO.doors[b]];
};
const polyLen = pts => pts.slice(1).reduce((s, p, i) => s + Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]), 0);
const clamp01 = v => Math.max(0, Math.min(1, v));
const edgeAnchor = x => x < GEO.w * .15 ? ["start", "-.8em"] : x > GEO.w * .85 ? ["end", ".8em"] : ["middle", "0"];     // labels near an edge read inward
function cityCast(it, S) {
  useGeo(S);
  const inScene = new Set([it.s.who, ...(it.s.peers.match(/\b[A-Z]\b/g) || [])]);
  return [...new Set(["A", "B", "C", "D", "P", "Q", "S", "K"].filter(k => inScene.has(k)).map(k => S[k]).filter(k => k && GEO.places[k]))];
}
function cityTrips(it, S) {        // this step's messages as walks along the roads, and timers
  useGeo(S);
  const { rows } = tellOf(it), r = rows[Math.min(stageStep, rows.length - 1)], I = isleOf(it.p), me = S[it.s.who], trips = [];
  const say = (text, peer, dir) => I ? lexT(I.msg && !PSEUDO.has(peer) ? I.msg(text, peer, dir) : text, I) : text;
  const add = ([peer, text, lost], dir) => {
    if (!text || peer === "nothing") return;
    if (peer === "timer") { trips.push({ kind: "here", icon: "⌛", label: say(text, peer, dir) }); return; }
    if (peer === "coin") { trips.push({ kind: "here", icon: "◐", label: say(text, peer, dir) }); return; }
    if (peer === "outside" && ((I && clientOf(I, say(text, peer, dir)) !== I.client) || !S.client || !GEO.doors[S.client])) {    // the node's own need, a due date, or a client with no place in the picture: it starts at your place
      trips.push({ kind: "here", icon: "✦", label: (I ? clientOf(I, say(text, peer, dir)) : U().client) + ": " + say(text, peer, dir) }); return; }
    const pl = peer === "outside" ? S.client : S[peer]; if (!pl || !GEO.doors[pl]) return;
    trips.push({ kind: "walk", dir, lost: !!lost, outside: peer === "outside", from: dir === "in" ? pl : me, to: dir === "in" ? me : pl, label: say(text, peer, dir) + (lost ? " ✕" : "") });
  };
  r.recv.forEach(m => add(m, "in")); r.sent.forEach(m => add(m, "out"));
  trips.forEach(x => { if (x.kind === "walk") { x.pts = cityRoute(x.from, x.to); x.len = polyLen(x.pts); } });
  return { r, me, trips };
}
const cityBox = () => [0, 0, GEO.w, GEO.h];      // the whole picture, at its own aspect (the city's is 4:3), for every scene
const decided = r => r.perm && typeof r.perm.decided === "string" && r.perm.decided !== "none" ? r.perm.decided : "";
function cityBlock(k, x, y, me, letter) {    // a node in the Abstraction register: a solid block standing where its place is
  const { e, n, u } = GEO.iso, s = 7, h = 9, fx = v => v.toFixed(1);
  const P = (a, b, c) => fx(x + e[0] * a + n[0] * b + u[0] * c) + "," + fx(y + e[1] * a + n[1] * b + u[1] * c);
  const face = (cls, pts) => `<polygon class="${cls}" points="${pts.map(q => P(...q)).join(" ")}"/>`;
  const [tx, ty] = [x + u[0] * h, y + u[1] * h];
  return `<g class="blk${me ? " me" : ""}${letter ? "" : " cl"}">${face("fs", [[-s, -s, 0], [s, -s, 0], [s, -s, h], [-s, -s, h]])}${face("fe", [[s, -s, 0], [s, s, 0], [s, s, h], [s, -s, h]])}${face("ft", [[-s, -s, h], [s, -s, h], [s, s, h], [-s, s, h]])}`
    + `<text class="bl" x="${fx(tx)}" y="${fx(ty)}" dy=".36em" text-anchor="middle">${letter || "·"}</text></g>`;
}
function cityPlaces(it, S) {       // the names of the scene's places, yours marked, and what you have decided
  useGeo(S);
  const { r, me, trips } = cityTrips(it, S), I = isleOf(it.p), fx = v => v.toFixed(1), plain = reg !== "isle";
  const letterOf = k => Object.keys(S).find(l => /^[A-Z]$/.test(l) && S[l] === k);
  const title = k => plain ? (k === S.client ? U().client : "") : (S.labels && S.labels[k]) || (GEO.label && GEO.label[k]) || (/^(legislator|proposer|camp) /.test(k) ? k : "the " + k);
  const shown = [...new Set([...cityCast(it, S), ...(trips.some(x => x.outside) ? [S.client] : []), ...(plain ? [] : (S.also || []).filter(k => GEO.places[k]))])];
  if (plain) return shown.map(k => { const [x, y] = GEO.places[k], name = title(k) + (k === me ? "you" : "");
    return `<g class="cpl${k === me ? " me" : ""}">${cityBlock(k, x, y, k === me, letterOf(k))}${name ? `<text x="${fx(x)}" y="${fx(y)}" dy="2.1em" dx="${edgeAnchor(x)[1]}" text-anchor="${edgeAnchor(x)[0]}">${esc(name)}${k === me && decided(r) ? ", decided " + esc(decided(r)) : ""}</text>` : ""}</g>`; }).join("");
  const decidedV = decided(r), dv = decidedV && I ? lexT(decidedV, I) : decidedV;
  return shown.map(k => { const [x, y] = GEO.places[k], name = title(k) + (k === me ? " (you)" : "");
    return `<g class="cpl${k === me ? " me" : ""}"><circle class="pin" cx="${fx(x)}" cy="${fx(y)}" r=".4em"/><text x="${fx(x)}" y="${fx(y)}" dy="1.9em" dx="${edgeAnchor(x)[1]}" text-anchor="${edgeAnchor(x)[0]}">${esc(name)}</text>${k === me && dv ? `<circle class="dec d${esc(dv)}" cx="${fx(x)}" cy="${fx(y)}" r=".55em" transform="translate(0 -40)"/><text class="dect" x="${fx(x)}" y="${fx(y - 40)}" dx="${x > GEO.w * .75 ? "-.9em" : ".9em"}" dy=".35em" text-anchor="${x > GEO.w * .75 ? "end" : "start"}">decided ${esc(dv)}</text>` : ""}</g>`; }).join("");
}
function cityHTML(it, S) {
  useGeo(S);
  const [bx, by, bw, bh] = cityBox(it, S), u = bw / 650, me = S[it.s.who], [mx] = GEO.places[me];
  const plain = reg !== "isle", baked = !plain && GEO.img;     // the drawn city and siege: baked to WebP by world/city_mockup.py, under the messengers
  const world = plain ? `<rect class="gnd" width="${GEO.w}" height="${GEO.h}"/><path class="rdn street" d="${GEO.plain.street}"/><path class="rdn road" d="${GEO.plain.road}"/>` : baked ? "" : GEO.svg;
  return `<figure class="stage city${plain ? " abs" : GEO.night ? " night" : ""}" id="stage" data-scene="${esc(it.key)}" data-reg="${reg}" data-u="${u.toFixed(3)}" data-mx="${((mx - bx) / bw).toFixed(3)}" style="--ar:${(bw / bh).toFixed(3)}"><div class="stv"><div class="stw"><div class="stg${baked ? " baked" : ""}">`
    + (baked ? `<img class="wld" src="${Object.values(GEO.img)[0]}" srcset="${Object.entries(GEO.img).map(([w, f]) => f + " " + w + "w").join(", ")}" sizes="(max-width: 640px) 100vw, 900px" width="${GEO.w}" height="${GEO.h}" alt="" decoding="async">` : "")
    + `<svg viewBox="${[bx, by, bw, bh].map(v => v.toFixed(1)).join(" ")}" style="font-size:${(15 * u).toFixed(2)}px" role="img" aria-label="${plain ? "Nodes " + esc(cityCast(it, S).map(k => Object.keys(S).find(l => S[l] === k)).join(", ")) + " and the roads between them" : "The city from above: " + esc(cityCast(it, S).join(", ")) + ", and the roads between them"}. This step's messages travel the roads.">`
    + `<g class="world">${world}</g><g class="trips"></g><g class="places">${cityPlaces(it, S)}</g></svg></div></div>`
    + `<button type="button" class="replay" data-replay="1" aria-label="Replay this step's messengers" title="Replay"><svg width="11" height="11" viewBox="0 0 14 14" aria-hidden="true"><path d="M11.5 7A4.5 4.5 0 1 1 7 2.5h2.5M8 .5l2 2-2 2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div></figure>`;
}
let cityAnim = 0;
function playCity() {
  cancelAnimationFrame(cityAnim);
  const fig = $("stage"), it = byKey(sel), S = it && stageOf(it); if (!fig || !fig.classList.contains("city") || !S) return;
  useGeo(S);
  const svg = fig.querySelector(".stg > svg"), W = svg.clientWidth || 1000, u = Math.max(+fig.dataset.u, 11.5 * GEO.w / (15 * W));    // on a small screen the text grows, so it stays about 11.5 px
  svg.style.fontSize = (15 * u).toFixed(2) + "px";
  const { me, trips } = cityTrips(it, S), layer = fig.querySelector(".trips"), [px, py] = GEO.places[me], fx = v => v.toFixed(1);
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
    ? `<g class="tmr"><text x="${fx(px)}" y="${fx(py)}" dy="-2.2em" dx="${px < GEO.w * .3 ? "-1em" : px > GEO.w * .7 ? "1em" : "0"}" text-anchor="${px < GEO.w * .3 ? "start" : px > GEO.w * .7 ? "end" : "middle"}">${x.icon} ${esc(x.label)}</text></g>`
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
      const [an, dx] = edgeAnchor(cx); if (x.an !== an) { x.an = an; tag.setAttribute("text-anchor", an); tag.setAttribute("dx", dx); }    // text layout is dear: only when it changes
      tag.setAttribute("opacity", t < x.start ? 0 : 1); tag.setAttribute("x", fx(cx)); tag.setAttribute("y", fx(cy - (28 + (done ? 22 * (x.stack - 1) : 0)) * u));
      if (x.lost) { xx.setAttribute("x", fx(cx)); xx.setAttribute("y", fx(cy)); xx.setAttribute("opacity", done ? after : 0); }
    });
    const a = clamp01((t - here) / .8); pulse.setAttribute("r", fx((8 + 46 * a) * u)); pulse.setAttribute("opacity", t < here ? 0 : (1 - a).toFixed(3));
    if (t < T) cityAnim = requestAnimationFrame(frame);
  };
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches, t0 = performance.now() - (still ? T * 1000 : 0);
  cityAnim = requestAnimationFrame(frame);
}
document.addEventListener("click", e => { if (e.target.closest && (e.target.closest("[data-replay]") || e.target.closest(".stage.city .stg"))) playCity(); });

function stageHTML(it) {       // both registers, every scene: the same messengers; only the background differs
  const S = stageOf(it); return S ? cityHTML(it, S) : "";
}
function centreStage() { playCity(); const f = $("stage"), s = f && f.querySelector && f.querySelector(".stw"); if (!s) return; if (s.scrollWidth > s.clientWidth) s.scrollLeft = +f.dataset.mx * s.scrollWidth - s.clientWidth / 2; }
function refreshStepper() { const it = byKey(sel), el = $("sctl"); if (!it || !el) return; el.outerHTML = ctlHTML(it); const on = document.querySelector(".stepbar .sgs .sd.on"), g = document.querySelector(".stepbar .sgs"); if (on && g) g.scrollLeft = on.offsetLeft - (g.clientWidth - on.offsetWidth) / 2; }
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
function refreshStage() {
  const it = byKey(sel), el = $("stage"); if (!it || !el) return;
  if (el.classList.contains("city") && el.dataset.scene === it.key && el.dataset.reg === reg) { el.querySelector(".places").innerHTML = cityPlaces(it, stageOf(it)); playCity(); return; }   // same scene: keep the picture, replay the step
  const keep = el.querySelector(".stw").scrollLeft; el.outerHTML = stageHTML(it); const s = $("stage") && $("stage").querySelector(".stw"); if (s) s.scrollLeft = keep; playCity();
}

