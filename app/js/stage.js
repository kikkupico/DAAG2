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
// ---------- labels: where the names of places and the messages' tags go ----------
// Boxes are [left, top, right, bottom] in the picture's own units; E is one em of the picture's text.
const boxHit = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));
function fitBox(w, h, spots, blocks, E) {      // the cheapest of the spots [left, top, cost], once pushed inside the frame: clear of every block [box, weight] if it can be
  const pad = .35 * E; let best = null;
  spots.forEach(([x, y, c]) => {
    const bx = Math.max(pad, Math.min(GEO.w - pad - w, x)), by = Math.max(pad, Math.min(GEO.h - pad - h, y)), box = [bx, by, bx + w, by + h];
    let cost = c + 3 * (Math.abs(bx - x) + Math.abs(by - y)) / E;
    for (const [b, wt] of blocks) { const a = boxHit(box, b); if (a > 0) cost += wt * (1 + a / (E * E)); }
    if (!best || cost < best.cost) best = { box, cost };
  });
  return best.box;
}
const setAll = (el, o) => { if (el) for (const k in o) el.setAttribute(k, typeof o[k] === "number" ? o[k].toFixed(1) : o[k]); };
function sizeLabel(lb, E) {      // a place's plate: the node's chip, the place's name, and under them what it has decided
  const q = c => lb.querySelector(c), ct = q(".ct"), nm = q(".nm"), sub = q(".sub"), px = .42 * E, py = .24 * E, rh = 1.2 * E;
  let x = ct ? py : px, h = ct || nm ? py * 2 + rh : py;
  if (ct) { const cw = Math.max(rh, ct.getComputedTextLength() + .64 * E); setAll(q(".chip"), { x, y: py, width: cw, height: rh, rx: .16 * E }); setAll(ct, { x: x + cw / 2, y: py + rh / 2 }); x += cw + (nm ? .38 * E : py - px); }
  if (nm) { setAll(nm, { x, y: py + rh / 2 }); x += nm.getComputedTextLength(); }
  let w = x + px;
  if (sub) { setAll(q(".dec"), { cx: px + .34 * E, cy: h + .32 * E, r: .3 * E }); setAll(sub, { x: px + .9 * E, y: h + .32 * E }); w = Math.max(w, px * 2 + .9 * E + sub.getComputedTextLength()); h += .9 * E; }
  setAll(q(".bg"), { width: w, height: h, rx: .28 * E });
  return [w, h];
}
function layPlaces(fig, E) {     // puts each place's plate beside its mark, inside the frame and clear of the others; returns everything a tag must keep off
  const svg = fig.querySelector(".stg > svg"), o = svg.getBoundingClientRect(), k = GEO.w / (o.width || GEO.w), plain = fig.classList.contains("abs"), g = .3 * E;
  const blocks = [...fig.querySelectorAll(".replay")].map(b => { const q = b.getBoundingClientRect(); return [[(q.left - o.left) * k - g, (q.top - o.top) * k - g, (q.right - o.left) * k + g, (q.bottom - o.top) * k + g], 60]; });
  const gs = [...fig.querySelectorAll(".cpl")], { e, n, u } = GEO.iso, hw = (e[0] + n[0]) * 7.6, dn = (e[1] - n[1]) * 7.6, up = dn - u[1] * 9;      // in the Abstraction register the mark is a block
  const marks = gs.map(c => { const x = +c.dataset.x, y = +c.dataset.y; return plain ? [x - hw, y - up, x + hw, y + dn] : [x - .55 * E, y - .55 * E, x + .55 * E, y + .55 * E]; });
  marks.forEach(m => blocks.push([m, 25]));
  gs.map((c, i) => i).sort((a, b) => gs[b].classList.contains("me") - gs[a].classList.contains("me")).forEach(i => {
    const lb = gs[i].querySelector(".lb"); if (!lb) return;
    const [w, h] = sizeLabel(lb, E), [l, t, r, b] = marks[i], cx = (l + r) / 2, cy = (t + b) / 2;
    const box = fitBox(w, h, [[cx - w / 2, b + g, 0], [cx - w / 2, t - g - h, 1], [r + g, cy - h / 2, 1.5], [l - g - w, cy - h / 2, 1.5], [l, b + g, 2], [r - w, b + g, 2], [l, t - g - h, 2.5], [r - w, t - g - h, 2.5]], blocks, E);
    lb.setAttribute("transform", `translate(${box[0].toFixed(1)} ${box[1].toFixed(1)})`); blocks.push([box, 100]);
  });
  return blocks;
}
function layTag(g, p, blocks, E) {     // sizes a message's tag and finds where it comes to rest about the point p; returns its size and its centre's offset from p
  const tx = g.querySelector("text"), h = 1.3 * E, w = tx.getComputedTextLength() + 1.05 * E, st = h + .14 * E, spots = [];
  setAll(g.querySelector(".bg"), { width: w, height: h, rx: .2 * E }); setAll(g.querySelector(".bar"), { width: .24 * E, height: h }); setAll(tx, { x: .62 * E, y: h / 2 });
  for (let k = 0; k < 5; k++) [0, -1, 1].forEach(sx => { const x = p[0] - w / 2 + sx * (w / 2 - .6 * E), c = k + (sx ? .6 : 0);
    spots.push([x, p[1] - 1.9 * E - k * st - h / 2, c], [x, p[1] + 1.9 * E + k * st - h / 2, c + 1.5]); });
  [-1, 1].forEach(sx => spots.push([p[0] - w / 2 + sx * (w / 2 + 1.2 * E), p[1] - h / 2, 2]));
  const box = fitBox(w, h, spots, blocks, E); blocks.push([box, 100]);
  return { w, h, fin: [(box[0] + box[2]) / 2 - p[0], (box[1] + box[3]) / 2 - p[1]] };
}
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
function cityPlaces(it, S) {       // the scene's places, each named as the step panel names its node: the same letter or business, then where it is
  useGeo(S);
  const { r, me, trips } = cityTrips(it, S), I = isleOf(it.p), fx = v => v.toFixed(1), plain = reg !== "isle";
  const letterOf = k => Object.keys(S).find(l => /^[A-Z]$/.test(l) && S[l] === k);
  const site = k => ((S.labels && S.labels[k]) || (GEO.label && GEO.label[k]) || k.replace(/ [A-Z]$/, "")).replace(/^(the|an?) /, "");
  const shown = [...new Set([...cityCast(it, S), ...(trips.some(x => x.outside) ? [S.client] : []), ...(plain ? [] : (S.also || []).filter(k => GEO.places[k]))])];
  const d0 = decided(r), dv = d0 && I ? lexT(d0, I) : d0;
  return shown.map(k => {
    const [x, y] = GEO.places[k], l = letterOf(k), cl = !l && k === S.client, you = k === me;
    const chip = plain ? "" : l ? nmOf(I, l) || l : cl ? I.client || "" : "";
    const name = plain ? (cl ? U().client : "") : site(k) === chip ? "" : site(k);
    const lb = (chip ? `<rect class="chip"/><text class="ct" dy=".35em">${esc(chip)}</text>` : "")
      + (name || you ? `<text class="nm" dy=".35em">${esc(name)}${you ? `<tspan class="yo">${name ? " · " : ""}you</tspan>` : ""}</text>` : "")
      + (you && dv ? `<circle class="dec d${esc(dv)}"/><text class="sub" dy=".35em">decided ${esc(dv)}</text>` : "");
    return `<g class="cpl${you ? " me" : ""}${cl ? " cl" : ""}" data-x="${fx(x)}" data-y="${fx(y)}">${plain ? cityBlock(k, x, y, you, l) : `<circle class="pin" cx="${fx(x)}" cy="${fx(y)}" r=".4em"/>`}${lb ? `<g class="lb"><rect class="bg"/>${lb}</g>` : ""}</g>`; }).join("");
}
function cityHTML(it, S) {
  useGeo(S);
  const [bx, by, bw, bh] = cityBox(it, S), u = bw / 650, me = S[it.s.who], [mx] = GEO.places[me];
  const plain = reg !== "isle", baked = !plain && GEO.img;     // the drawn city and siege: baked to WebP by world/city_mockup.py, under the messengers
  const r3 = baked && GEO.img3d && bg === "rendered", pic = r3 ? GEO.img3d : GEO.img;   // or the same frame rendered in Blender: same pixels, same roads
  const world = plain ? `<rect class="gnd" width="${GEO.w}" height="${GEO.h}"/><path class="rdn street" d="${GEO.plain.street}"/><path class="rdn road" d="${GEO.plain.road}"/>` : baked ? "" : GEO.svg;
  return `<figure class="stage city${plain ? " abs" : GEO.night ? " night" : ""}" id="stage" data-scene="${esc(it.key)}" data-reg="${reg}" data-pic="${r3 ? "rendered" : "drawn"}" data-u="${u.toFixed(3)}" data-mx="${((mx - bx) / bw).toFixed(3)}" style="--ar:${(bw / bh).toFixed(3)}"><div class="stv"><div class="stw"><div class="stg${baked ? " baked" : ""}">`
    + (baked ? `<img class="wld" src="${Object.values(pic)[0]}" srcset="${Object.entries(pic).map(([w, f]) => f + " " + w + "w").join(", ")}" sizes="(max-width: 640px) 100vw, 900px" width="${GEO.w}" height="${GEO.h}" alt="" decoding="async">` : "")
    + `<svg viewBox="${[bx, by, bw, bh].map(v => v.toFixed(1)).join(" ")}" style="font-size:${(15 * u).toFixed(2)}px" role="img" aria-label="${plain ? "Nodes " + esc(cityCast(it, S).map(k => Object.keys(S).find(l => S[l] === k)).join(", ")) + " and the roads between them" : "The city from above: " + esc(cityCast(it, S).join(", ")) + ", and the roads between them"}. This step's messages travel the roads.">`
    + `<g class="world">${world}</g><g class="trips"></g><g class="places">${cityPlaces(it, S)}</g><g class="tags"></g></svg></div></div>`
    + `<button type="button" class="replay" data-replay="1" aria-label="Replay this step's messengers" title="Replay"><svg width="11" height="11" viewBox="0 0 14 14" aria-hidden="true"><path d="M11.5 7A4.5 4.5 0 1 1 7 2.5h2.5M8 .5l2 2-2 2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div></figure>`;
}
let cityAnim = 0;
function playCity() {
  cancelAnimationFrame(cityAnim);
  const fig = $("stage"), it = byKey(sel), S = it && stageOf(it); if (!fig || !fig.classList.contains("city") || !S) return;
  useGeo(S);
  const svg = fig.querySelector(".stg > svg"), W = svg.clientWidth || 1000, u = Math.max(+fig.dataset.u, 11.5 * GEO.w / (15 * W));    // on a small screen the text grows, so it stays about 11.5 px
  svg.style.fontSize = (15 * u).toFixed(2) + "px"; cityW = svg.clientWidth;
  const { me, trips } = cityTrips(it, S), layer = fig.querySelector(".trips"), [px, py] = GEO.places[me], fx = v => v.toFixed(1);
  // the schedule, in seconds: timers, then arrivals, then the step itself at your place, then departures
  const SPEED = 560, walk = (x, k, t0) => { x.stop = x.lost ? .55 : 1; x.start = t0 + .25 * k; x.dur = Math.min(2.8, Math.max(.9, x.len / SPEED)) * x.stop; x.end = x.start + x.dur; };
  const timers = trips.filter(x => x.kind === "here"), ins = trips.filter(x => x.dir === "in"), outs = trips.filter(x => x.dir === "out");
  let t = .25; timers.forEach(x => { x.start = t; x.end = t + .5; }); if (timers.length) t += .9;
  ins.forEach((x, k) => walk(x, k, t));
  const here = ins.length ? Math.max(...ins.map(x => x.end)) + .1 : t;
  outs.forEach((x, k) => walk(x, k, here + (ins.length || timers.length ? .5 : 0)));
  const T = Math.max(here + .9, ...trips.map(x => x.end + .7));
  const line = pts => pts.map(p => p.join(",")).join(" "), E = 15 * u, tagLayer = fig.querySelector(".tags");
  layer.innerHTML = trips.map(x => x.kind === "here" ? `<g></g>`
    : `<g class="trip ${x.dir}${x.lost ? " lost" : ""}"><polyline class="way" points="${line(x.pts)}"/><polyline class="trail" points="${line(x.pts)}" stroke-dasharray="${fx(x.len)} ${fx(x.len)}" stroke-dashoffset="${fx(x.len)}"/>`
      + `<g class="mx" opacity="0"><g transform="scale(${(u * .8).toFixed(3)})"><ellipse class="sh" rx="10" ry="3.6" cy="1"/><g class="bob"><circle r="11" cy="-9"/><rect class="scroll" x="-6" y="-13" width="12" height="8" rx="2"/><path class="scroll" d="M-3.5 -10.5h7M-3.5 -7.5h5"/></g></g></g>`
      + `<text class="xx" text-anchor="middle" dy=".35em" opacity="0">✕</text></g>`).join("")
    + `<circle class="pulse" cx="${fx(px)}" cy="${fx(py)}" r="0" opacity="0"/>`;
  tagLayer.innerHTML = trips.map(x => `<g class="tg ${x.kind === "here" ? "here" : x.dir + (x.lost ? " lost" : "")}" opacity="0"><rect class="bg"/><rect class="bar"/><text dy=".35em">${x.kind === "here" ? x.icon + " " : ""}${esc(x.label)}</text></g>`).join("");
  const gs = [...layer.children], tags = [...tagLayer.children], pulse = layer.querySelector(".pulse");
  // where every tag comes to rest: in the order they arrive, each clear of the places' names, the frame's edge and the tags before it
  const blocks = layPlaces(fig, E), pad = .35 * E, ease = v => v * v * (3 - 2 * v);
  trips.forEach((x, i) => { x.at = x.kind === "here" ? [px, py] : along(x.pts, x.stop); Object.assign(x, layTag(tags[i], x.at, blocks, E)); });
  const put = (g, x, cx, cy) => g.setAttribute("transform", `translate(${fx(Math.max(pad, Math.min(GEO.w - pad - x.w, cx - x.w / 2)))} ${fx(Math.max(pad, Math.min(GEO.h - pad - x.h, cy - x.h / 2)))})`);
  const frame = now => {
    const t = (now - t0) / 1000;
    trips.forEach((x, i) => {
      const g = gs[i], tag = tags[i];
      if (x.kind === "here") { const a = clamp01((t - x.start) / .4); tag.setAttribute("opacity", a); put(tag, x, px + x.fin[0], py + x.fin[1] + (1 - a) * .5 * E); return; }
      const f = clamp01((t - x.start) / x.dur), p = f * x.stop, [cx, cy] = along(x.pts, p), done = t >= x.end, after = clamp01((t - x.end) / .45);
      const [trail, mx, xx] = [g.children[1], g.children[2], g.children[3]];
      trail.setAttribute("stroke-dashoffset", fx(x.len * (1 - p)));
      mx.setAttribute("opacity", t < x.start ? 0 : done ? 1 - after : 1);
      mx.setAttribute("transform", `translate(${fx(cx)} ${fx(cy)})`);
      mx.children[0].children[1].setAttribute("transform", `translate(0 ${done ? 0 : fx(-Math.abs(Math.sin(t * 11)) * 3)})`);   // a little bounce as it walks
      const k = ease(clamp01((f - .5) / .5));      // the tag rides above its messenger, and over the last half of the walk eases to its resting place
      tag.setAttribute("opacity", t < x.start ? 0 : 1); put(tag, x, cx + x.fin[0] * k, cy - 1.9 * E * (1 - k) + x.fin[1] * k);
      if (x.lost) { xx.setAttribute("x", fx(cx)); xx.setAttribute("y", fx(cy)); xx.setAttribute("opacity", done ? after : 0); }
    });
    const a = clamp01((t - here) / .8); pulse.setAttribute("r", fx((8 + 46 * a) * u)); pulse.setAttribute("opacity", t < here ? 0 : (1 - a).toFixed(3));
    if (t < T) cityAnim = requestAnimationFrame(frame);
  };
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches, t0 = performance.now() - (still ? T * 1000 : 0);
  cityAnim = requestAnimationFrame(frame);
}
// The labels are measured, so they are laid out again once the page's fonts have loaded, and when the picture changes width.
if (document.fonts && document.fonts.status !== "loaded") document.fonts.ready.then(() => playCity());
let cityW = 0;
{ let timer = 0; window.addEventListener("resize", () => { clearTimeout(timer); timer = setTimeout(() => { const s = document.querySelector("#stage .stg > svg"); if (s && s.clientWidth && s.clientWidth !== cityW) playCity(); }, 200); }); }
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
  if (el.classList.contains("city") && el.dataset.scene === it.key && el.dataset.reg === reg && (el.dataset.pic || "drawn") === (reg === "isle" && GEO.img3d && bg === "rendered" ? "rendered" : "drawn")) { el.querySelector(".places").innerHTML = cityPlaces(it, stageOf(it)); playCity(); return; }   // same scene: keep the picture, replay the step
  const keep = el.querySelector(".stw").scrollLeft; el.outerHTML = stageHTML(it); const s = $("stage") && $("stage").querySelector(".stw"); if (s) s.scrollLeft = keep; playCity();
}

