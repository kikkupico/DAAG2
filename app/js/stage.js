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
function stageHTML(it) {
  const S = stageOf(it); if (!S) return "";
  if (reg !== "isle") return diagramHTML(it, S, STAGES[S.view]);
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
function centreStage() { const f = $("stage"), s = f && f.querySelector && f.querySelector(".stw"); if (!s) return; if (s.scrollWidth > s.clientWidth) s.scrollLeft = +f.dataset.mx * s.scrollWidth - s.clientWidth / 2; }
function refreshStepper() { const it = byKey(sel), el = $("sctl"); if (!it || !el) return; el.outerHTML = ctlHTML(it, !!$("pict")); }
function showStep(n, scroll) {
  const it = byKey(sel); if (!it) return;
  stageStep = Math.max(0, Math.min(it.s.rows.length, n)); refreshStage(); refreshStepper();
  const el = $("st-0-" + stageStep); if (!el || !scroll) return;
  spyPause = Date.now() + 1800;      // until the scroll this starts has finished (see scrollend below)
  const bar = $("stepbar"), below = (bar ? bar.getBoundingClientRect().height : 0) + 14;     // land the card just under the stepper box
  window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - below, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  el.classList.remove("hit"); void el.offsetWidth; el.classList.add("hit");
}
// The picture inside the stepper box folds away, and stays folded across steps and scenes.
let picOpen = true;
try { if (localStorage.getItem("pic") === "shut") picOpen = false; } catch (e) {}
function togglePic() {
  picOpen = !picOpen; try { localStorage.setItem("pic", picOpen ? "open" : "shut"); } catch (e) {}
  const p = $("pict"); if (p) p.hidden = !picOpen; refreshStepper(); if (picOpen) centreStage();
  const t = document.querySelector(".pictog"); if (t) t.focus();
}
window.addEventListener("scrollend", () => { if (spyPause > Date.now()) spyPause = Date.now() + 60; });   // a smooth scroll can outlast any fixed allowance
["wheel", "touchmove"].forEach(ev => window.addEventListener(ev, () => { spyPause = 0; }, { passive: true }));   // scrolling by hand takes over at once
// Scrolling by hand: the step whose card sits just below the stepper becomes the current one, so stepper and picture follow the reading.
let spyPause = 0, spyQueued = false;
function spy() {
  spyQueued = false; const bar = $("stepbar"), it = byKey(sel); if (!bar || !it || cmp || Date.now() < spyPause || !bar.getBoundingClientRect) return;
  const top = bar.getBoundingClientRect().bottom, line = top + (window.innerHeight - top) * .35; let cur = 0;   // the card a third of the way down the reading space
  for (let t = 0; t <= it.s.rows.length; t++) { const c = $("st-0-" + t); if (c && c.getBoundingClientRect && c.getBoundingClientRect().top <= line) cur = t; }
  if (cur !== stageStep) { stageStep = cur; refreshStage(); refreshStepper(); }
}
window.addEventListener("scroll", () => { if (!spyQueued) { spyQueued = true; requestAnimationFrame(spy); } }, { passive: true });
function refreshStage() { const it = byKey(sel), el = $("stage"); if (!it || !el) return; const keep = el.querySelector(".stw").scrollLeft; el.outerHTML = stageHTML(it); const s = $("stage") && $("stage").querySelector(".stw"); if (s) s.scrollLeft = keep; }

