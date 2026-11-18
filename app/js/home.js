// ---------- the front page: the idea in a few seconds ----------
// Shown when the address has no hash. It plays one real scene, Paxos's clean round, on two layers that share one clock:
// the allegory's town above, the Abstraction's plain roads beneath. The switch wipes from one to the other, so the same
// couriers carry on walking while the telling changes under them. The page keeps its own telling; it never touches `reg`.
const HOME_SCENE = "paxos-round";
// The papers shown as a sample: which line of the citation is the famous one, and the hook, in the allegory's words.
const HOME_CARDS = [
  ["paxos", 0, "Part-time legislators agree on one colour for the {temple} columns, though any of them may leave office mid-vote."],
  ["liars", 1, "Generals besiege a city and must agree to attack or retreat, knowing some among them are traitors."],
  ["clocks", 0, "The {fishery}, the {granary} and the {winery} share no clock, yet must agree which order came first."],
  ["flp", 0, "A legislator has gone quiet. Gone for good, or only slow? Nobody can ever be sure, and that is enough to stall any vote."],
  ["cap", 1, "When the roads are cut, a scholar asked a question must answer with what they have, or wait."],
  ["snapshot", 0, "Count every amphora in town, on the shelves and on the road, without stopping anyone from trading."],
];
let homeReg = "isle", homeAuto = true, homePaused = false, homeAnim = 0, homeLast = 0, homeT = 0, homeSeen = true, homePlan = null;
const homeStill = window.matchMedia("(prefers-reduced-motion: reduce)");

function homeScene() {
  const it = byKey(HOME_SCENE), S = TELL.paxos.stage, I = TELL.paxos;
  return { it, S, I, me: S[it.s.who], rows: it.s.rows };
}
// One step's couriers, on one layer's roads. Labels come from the scene itself: the Allegory's through the telling's own words.
function homeTrips(i, G, isle) {
  const { S, I, me, rows } = homeScene(), r = rows[i], out = [];
  const route = (a, b) => { const rt = G.routes[a < b ? a + "|" + b : b + "|" + a]; return rt ? (a < b ? rt : [...rt].reverse()) : [G.doors[a], G.doors[b]]; };
  const add = ([peer, text], dir) => {
    const pl = peer === "outside" ? S.client : S[peer]; if (!pl || !G.doors[pl]) return;
    const say = isle ? lexT(text, I) : text, who = peer === "outside" ? (isle ? I.client : "client") + ": " : "";
    const pts = dir === "in" ? route(pl, me) : route(me, pl);
    out.push({ dir, pts, len: polyLen(pts), label: who + say });
  };
  (r.recv || []).forEach(m => add(m, "in")); (r.sent || []).forEach(m => add(m, "out"));
  return out;
}
// The timing of every step, from the allegory's roads, so both layers keep the same pace even where their roads differ.
function homeSchedule() {
  const { rows } = homeScene(), SPEED = 520, plan = [];
  rows.forEach((_, i) => {
    const trips = homeTrips(i, CITY, true), ins = trips.filter(x => x.dir === "in"), outs = trips.filter(x => x.dir === "out");
    const walk = (x, k, t0) => { x.start = t0 + .3 * k; x.dur = Math.min(2.6, Math.max(1.1, x.len / SPEED)); x.end = x.start + x.dur; };
    ins.forEach((x, k) => walk(x, k, .2));
    const here = ins.length ? Math.max(...ins.map(x => x.end)) + .15 : .2;
    outs.forEach((x, k) => walk(x, k, here + (ins.length ? .5 : 0)));
    const T = Math.max(here + 1, ...trips.map(x => x.end)) + 1.4;
    plan.push({ trips: [...ins, ...outs].map(({ start, dur, end }) => ({ start, dur, end })), here, T });
  });
  return plan;
}

function homeLayer(isle) {
  const { S, me } = homeScene(), G = isle ? CITY : PLAIN.city, fx = v => v.toFixed(1);
  const letterOf = k => Object.keys(S).find(l => /^[A-Z]$/.test(l) && S[l] === k);
  const cast = [...new Set([S.client, ...["A", "B", "C", "P"].map(l => S[l])])].filter(k => G.places[k]);
  let ground = "";
  if (!isle) { const was = GEO; GEO = G; ground = `<rect class="gnd" width="${G.w}" height="${G.h}"/><path class="rdn street" d="${G.plain.street}"/><path class="rdn road" d="${G.plain.road}"/>`
    + cast.map(k => cityBlock(k, G.places[k][0], G.places[k][1], k === me, letterOf(k) || "")).join(""); GEO = was; }
  else ground = cast.map(k => `<circle class="pin${k === me ? " me" : ""}" cx="${fx(G.places[k][0])}" cy="${fx(G.places[k][1])}" r="9"/>`).join("");
  const name = k => { const l = letterOf(k);
    if (!isle) return l ? (k === me ? "proposer P" : "node " + l) : "client";
    const lab = esc((S.labels && S.labels[k]) || (G.label && G.label[k]) || k); return l ? `<b>${l}</b>${lab}` : lab; };
  // the plates go under the place, or above it near the bottom edge; the Abstraction's blocks stand taller, so its plates sit lower
  const plates = cast.map(k => { const [x, y] = G.places[k], low = y > G.h * .8, dy = isle ? (low ? -3.4 : 3.2) : (low ? -9 : 4.2);
    return `<span class="hpl${k === me ? " me" : ""}" data-k="${esc(k)}" style="left:${(100 * x / G.w).toFixed(2)}%;top:${(100 * y / G.h + dy).toFixed(2)}%;--ty:${low ? "-100%" : "0"}">${isle ? name(k) : esc(name(k))}<i></i></span>`; }).join("");
  const pic = CITY.img3d || CITY.img;
  return `<div class="hl ${isle ? "isle" : "plain"}${isle && CITY.night ? " night" : ""}" aria-hidden="true">`
    + (isle ? `<img class="hpic" src="${pic[1200]}" srcset="${Object.entries(pic).map(([w, f]) => f + " " + w + "w").join(", ")}" sizes="(max-width: 900px) 100vw, 760px" width="${G.w}" height="${G.h}" alt="">` : "")
    + `<svg viewBox="0 0 ${G.w} ${G.h}" preserveAspectRatio="xMidYMid slice"><g class="world">${ground}</g><g class="trips"></g><circle class="pulse" r="0" opacity="0"/></svg>`
    + `<div class="hov">${plates}<div class="htags"></div></div></div>`;
}

function homeStageHTML() {
  const { it } = homeScene(), n = it.s.rows.length;
  const dots = Array.from({ length: n }, (_, i) => `<button type="button" class="hd" data-hstep="${i}" aria-label="Step ${i + 1} of ${n}"></button>`).join("");
  return `<figure class="hstage" id="hstage" data-telling="${homeReg}">
    <div class="hframe" role="img" aria-label="An animation of one round of Paxos. In the Allegory, couriers walk the roads of ${esc(ALLEGORY.town)} between three legislators and a proposer; in the Abstraction, the same messages travel between nodes A, B, C and P.">
      ${homeLayer(false)}${homeLayer(true)}<div class="hseam" aria-hidden="true"></div>
    </div>
    <div class="hswitch" role="group" aria-label="How the scene is told"><button type="button" data-hreg="isle">Allegory</button><button type="button" data-hreg="plain">Abstraction</button></div>
    <figcaption class="hcap">
      <div class="hctl"><button type="button" class="hplay" data-hplay="1" aria-label="Pause"><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path class="i-pause" d="M3 2v8M9 2v8" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><path class="i-play" d="M3 1.5v9l7.5-4.5z" fill="currentColor"/></svg></button>
        <div class="hdots">${dots}</div><span class="hwhat"><b>Paxos</b>, one clean round</span></div>
      <p class="hnar" id="hnar"></p>
    </figcaption>
  </figure>`;
}

function homeHTML() {
  const F = ALLEGORY.fill || (t => t), ext = (href, text) => `<a href="${href}" target="_blank" rel="noopener">${text}</a>`;
  const brand = document.querySelector(".brand svg").outerHTML;
  const cards = HOME_CARDS.map(([id, line, hook]) => {
    const p = PAPERS.find(x => x.id === id); if (!p) return "";
    const ln = p.cite.split("\n")[line] || p.cite.split("\n")[0], [who, title] = ln.split(" · ");
    return `<button type="button" class="hcard" data-key="${p.id}"><span class="hy">${esc(who)}</span><b>${esc(title)}</b><span class="hk">${esc(F(hook))}</span><span class="hgo">${esc(paperName(p))} →</span></button>`;
  }).join("");
  const pairs = [["a courier on the road", "a message"], ["the {fishery}, the {granary}, the {winery}", "nodes A, B and C"], ["the ledger", "permanent state, kept through a crash"],
    ["the slate", "temporary state, lost in a crash"], ["an hourglass", "a timer"], ["a legislator who leaves office", "a node that stops, and its replacement"], ["a traitor", "a node that lies"], ["roads cut off", "a network partition"]];
  const { it, I } = homeScene(), step = 1;
  return `<div class="home">
  <header class="htop"><button type="button" class="hbrand" data-key="intro">${brand}<span>${esc(ALLEGORY.title)}</span></button>
    <nav>${ext(REPO, "GitHub")}<button type="button" class="hopen" data-key="intro">Get started</button></nav></header>
  <section class="hero">
    <div class="htext">
      <p class="hey">Lamport did it first</p>
      <h1>Distributed algorithms, told as stories.</h1>
      <p class="hlede">Leslie Lamport first published Paxos as an archaeologist's report on the lost parliament of a Greek island. This site tells sixteen classic results the same way: as scenes in one town, where every message is a courier walking the roads. One switch turns the story back into nodes A, B and C.</p>
      <div class="hcta"><button type="button" class="hbtn pri" data-key="intro">Start with the guide</button><button type="button" class="hbtn" data-key="paxos">Or step right into Paxos</button></div>
      <p class="hhint">The guide takes two minutes. Paxos opens on its own page, with the idea, the papers and four scenes.</p>
    </div>
    ${homeStageHTML()}
  </section>

  <section class="hsec hstory">
    <div class="hcol">
      <p class="hlab">Where the idea comes from</p>
      <h2>Paxos was never meant to be dry</h2>
      <blockquote><p>“Recent archaeological discoveries on the island of Paxos reveal that the parliament functioned despite the peripatetic propensity of its part-time legislators.”</p>
        <footer>Leslie Lamport, ${ext("https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf", "<cite>The Part-Time Parliament</cite>")}, written 1990, published 1998</footer></blockquote>
      <p>In 1982 Lamport, Shostak and Pease had told agreement among faulty computers as ${ext("https://lamport.azurewebsites.net/pubs/byz.pdf", "<cite>The Byzantine Generals Problem</cite>")}, and the story made the problem famous. So Lamport wrote his next algorithm as archaeology: legislators who wander in and out, keep their own ledgers, speak only through forgetful messengers, and still never pass two conflicting laws.</p>
      <p>Readers found the story harder than the algorithm, and in 2001 he retold it plainly as <cite>Paxos Made Simple</cite>. This site keeps both. The story makes an idea stick; the plain version is one click away.</p>
    </div>
  </section>

  <section class="hsec">
    <div class="hcol">
      <p class="hlab">The allegory</p>
      <h2>One town for every paper</h2>
      <p>The same treatment, given to fifteen more results. They all happen in ${esc(ALLEGORY.town)}, among ${esc(ALLEGORY.people)}. Nobody ever shares a room: a courier can be slow, lost, or overtaken by a later one, and you watch it happen on the road. Each result is a few short scenes, seen from inside one participant.</p>
      <dl class="hmap">${pairs.map(([a, b]) => `<div><dt>${esc(F(a))}</dt><dd>${esc(b)}</dd></div>`).join("")}</dl>
    </div>
  </section>

  <section class="hsec">
    <div class="hwide">
      <p class="hlab">A sample of the sixteen</p>
      <h2>The papers everyone cites, and few remember</h2>
      <div class="hcards">${cards}</div>
      <p class="hmore"><button type="button" class="hbtn" data-key="map">See all sixteen, and how they connect</button></p>
    </div>
  </section>

  <section class="hsec">
    <div class="hcol">
      <p class="hlab">Two tellings</p>
      <h2>Story or abstraction, one click apart</h2>
      <p>Every page has a switch at the top. The steps underneath are identical, so you can flip in the middle of a scene: to see what the story stands for, or to read the bare algorithm once the story has made it stick. Here is the same step, both ways.</p>
      <div class="htwo">
        <div class="hside isle"><p class="hlab">Allegory</p><p>${mk(I.scenes.round.prose[step + 1])}</p></div>
        <div class="hside plain"><p class="hlab">Abstraction</p><p>${nodeText(it.s.prose[step + 1], it.s)}</p></div>
      </div>
    </div>
  </section>

  <section class="hsec hend">
    <div class="hcol">
      <p class="hlab">Where to begin</p>
      <h2>Step inside ${esc(ALLEGORY.town)}</h2>
      <div class="hpaths">
        <button type="button" class="hpath first" data-key="intro"><span class="hlab">Recommended · two minutes</span><b>Start with the guide</b>
          <span>How a scene is told, how to step through it, what the dashed frames mean, and how to switch between the tellings. Then the sixteen results, in order.</span><span class="hgo">How this site works →</span></button>
        <button type="button" class="hpath" data-key="paxos"><span class="hlab">Or step right in</span><b>Explore Paxos</b>
          <span>${esc(F("The idea in a paragraph, the papers behind it, then four scenes: a clean round, one legislator's own view, a successor who inherits a ledger, and what breaks if promises are kept on the slate."))}</span><span class="hgo">Paxos →</span></button>
      </div>
      <p class="hfine">Prefer another setting? The same scenes are also told in ${ALLEGORIES.list.filter(a => a.id !== ALLEGORIES.current).map(a => esc(a.name.replace(/^The /, "the "))).join(" and ")}: choose one from the menu at the foot of the side drawer. Or ${ext(REPO + "/tree/main/skills/build-allegory", "build your own")}. Code under MIT, text and pictures under CC BY 4.0, on ${ext(REPO, "GitHub")}.</p>
    </div>
  </section>
</div>`;
}

// ---------- playing it ----------
function homeSetReg(r, byHand) {
  homeReg = r; if (byHand) homeAuto = false;
  const f = $("hstage"); if (!f) return;
  f.dataset.telling = r; homeDirty = true;
  f.querySelectorAll("[data-hreg]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.hreg === r)));
  homeNarrate();
}
function homeNarrate() {
  const { it, I } = homeScene(), n = $("hnar"), i = homeStepAt().i; if (!n) return;
  n.innerHTML = homeReg === "isle" ? mk(I.scenes.round.prose[i + 1]) : nodeText(it.s.prose[i + 1], it.s);
  document.querySelectorAll(".hd").forEach((d, k) => d.setAttribute("aria-current", String(k === i)));
}
const homeTotal = () => homePlan.reduce((s, p) => s + p.T, 0);
function homeStepAt() { let t = homeT; for (let i = 0; i < homePlan.length; i++) { if (t < homePlan[i].T || i === homePlan.length - 1) return { i, t: Math.min(t, homePlan[i].T) }; t -= homePlan[i].T; } return { i: 0, t: 0 }; }
const homeStepStart = i => homePlan.slice(0, i).reduce((s, p) => s + p.T, 0);
let homeShown = -1;
function homeBuildStep(i) {
  const f = $("hstage"); if (!f) return;
  homeShown = i;
  f.querySelectorAll(".hl").forEach(L => {
    const isle = L.classList.contains("isle"), G = isle ? CITY : PLAIN.city, trips = homeTrips(i, G, isle), plan = homePlan[i];
    trips.forEach((x, k) => Object.assign(x, plan.trips[k]));
    L._trips = trips; L._G = G;
    L.querySelector(".trips").innerHTML = trips.map(x => `<g class="trip ${x.dir}"><polyline class="way" points="${x.pts.map(p => p.join(",")).join(" ")}"/><polyline class="trail"/>`
      + `<g class="mx" opacity="0"><g class="mxs"><ellipse class="sh" rx="10" ry="3.6" cy="1"/><g class="bob"><circle r="11" cy="-9"/><rect class="scroll" x="-6" y="-13" width="12" height="8" rx="2"/><path class="scroll" d="M-3.5 -10.5h7M-3.5 -7.5h5"/></g></g></g></g>`).join("");
    L.querySelector(".htags").innerHTML = trips.map(x => `<span class="htg ${x.dir}">${esc(x.label)}</span>`).join("");
    const [px, py] = G.places[homeScene().me], pu = L.querySelector(".pulse"); pu.setAttribute("cx", px); pu.setAttribute("cy", py);
  });
  homeNarrate();
}
// The wipe between the tellings: where the seam stands, 0 (all town) to 1 (all plain), eased toward the chosen telling each frame.
let homeCut = 0;
function homeWipe(dt) {
  const f = $("hstage"), goal = homeReg === "plain" ? 1 : 0; if (!f) return;
  homeCut = homeStill.matches || dt === null ? goal : goal > homeCut ? Math.min(goal, homeCut + dt / 1.1) : Math.max(goal, homeCut - dt / 1.1);
  const e = homeCut * homeCut * (3 - 2 * homeCut);
  f.style.setProperty("--cut", (100 * e).toFixed(2) + "%");
  f.toggleAttribute("data-wiping", homeCut > 0 && homeCut < 1);
}
function homeDraw() {
  const f = $("hstage"); if (!f) return;
  const { i, t } = homeStepAt(); if (i !== homeShown) homeBuildStep(i);
  const plan = homePlan[i], still = homeStill.matches, last = i === homePlan.length - 1, ease = v => v * v * (3 - 2 * v);
  f.querySelectorAll(".hl").forEach(L => {
    const G = L._G, svg = L.querySelector("svg"), W = svg.clientWidth || 600, k = Math.max(1, G.w / W) * .9, gs = L.querySelector(".trips").children, tags = L.querySelector(".htags").children;
    L._trips.forEach((x, n) => {
      const g = gs[n], tag = tags[n], fr = still ? 1 : clamp01((t - x.start) / x.dur), done = still || t >= x.end, after = still ? 1 : clamp01((t - x.end) / .5);
      const [cx, cy] = along(x.pts, fr), L0 = x.len * fr, pts = [];
      let acc = 0; for (let j = 0; j < x.pts.length; j++) { if (j && acc + Math.hypot(x.pts[j][0] - x.pts[j - 1][0], x.pts[j][1] - x.pts[j - 1][1]) > L0) break; if (j) acc += Math.hypot(x.pts[j][0] - x.pts[j - 1][0], x.pts[j][1] - x.pts[j - 1][1]); pts.push(x.pts[j]); }
      pts.push([cx, cy]);
      g.children[1].setAttribute("points", t < x.start && !still ? "" : pts.map(p => p.map(v => v.toFixed(1)).join(",")).join(" "));
      const mx = g.children[2]; mx.setAttribute("opacity", t < x.start && !still ? 0 : done ? 1 - after : 1);
      mx.setAttribute("transform", `translate(${cx.toFixed(1)} ${cy.toFixed(1)})`);
      mx.firstChild.setAttribute("transform", `scale(${k.toFixed(3)})`);
      mx.firstChild.children[1].setAttribute("transform", `translate(0 ${done ? 0 : (-Math.abs(Math.sin(t * 11)) * 3).toFixed(1)})`);
      // the tag rides above its courier once the couriers have spread out, and is gone before it reaches the place's own name
      const show = still ? 1 : t < x.start ? 0 : Math.min(clamp01((fr - .1) / .12), 1 - clamp01((fr - .8) / .12));
      tag.style.opacity = show.toFixed(3);
      tag.style.left = (100 * cx / G.w).toFixed(2) + "%"; tag.style.top = (100 * cy / G.h).toFixed(2) + "%";
    });
    const a = still ? 1 : clamp01((t - plan.here) / .8), pu = L.querySelector(".pulse");
    pu.setAttribute("r", ((8 + 50 * ease(a)) * k).toFixed(1)); pu.setAttribute("opacity", t < plan.here || still ? 0 : (1 - a).toFixed(3));
    const me = L.querySelector(".hpl.me i"), chosen = last && (still || t >= plan.here);
    if (me) me.textContent = chosen ? " · chose " + (L.classList.contains("isle") ? lexT("x", TELL.paxos) : "x") : "";
  });
}
// Until the reader picks a telling, the page switches it once in every step, just after the step's couriers set out:
// the first switch comes a few seconds in, and every step is seen both ways. Drawing happens only when something moved.
let homeFlipped = -1, homeDirty = true;
function homeTick(now) {
  if (!$("hstage")) { homeAnim = 0; return; }
  const dt = Math.min(.1, (now - (homeLast || now)) / 1000); homeLast = now;
  let moved = homeDirty || (homeCut > 0 && homeCut < 1) || (homeReg === "plain") !== (homeCut === 1);
  if (!homePaused && homeSeen && !document.hidden && !homeStill.matches) {
    const before = homeStepAt().i; homeT += dt; moved = true;
    if (homeT >= homeTotal()) { homeT = 0; homeFlipped = -1; }      // one round done: play it again
    const { i, t } = homeStepAt();
    if (homeAuto && homeFlipped !== i && t >= homePlan[i].here + .6) { homeFlipped = i; homeSetReg(homeReg === "isle" ? "plain" : "isle"); }
    if (i !== before) homeNarrate();
  }
  if (moved) { homeWipe(dt); homeDraw(); homeDirty = false; }
  homeAnim = requestAnimationFrame(homeTick);
}
window.addEventListener("resize", () => { homeDirty = true; });
function homeSetPaused(p) {
  homePaused = p; const b = document.querySelector("[data-hplay]"); if (!b) return;
  b.dataset.paused = String(p); b.setAttribute("aria-label", p ? "Play" : "Pause");
}
let homeIO = null;
function playHome() {
  cancelAnimationFrame(homeAnim); homeAnim = 0;
  const f = $("hstage"); if (!f) return;
  homePlan = homePlan || homeSchedule(); homeShown = -1; homeLast = 0; homeDirty = true; homeWipe(null);
  if (homeStill.matches) { homeAuto = false; homeSetPaused(true); }
  homeSetReg(homeReg); homeSetPaused(homePaused);
  if (homeIO) homeIO.disconnect();
  if ("IntersectionObserver" in window) { homeIO = new IntersectionObserver(es => { homeSeen = es[0].isIntersecting; }, { threshold: .15 }); homeIO.observe(f); }
  homeAnim = requestAnimationFrame(homeTick);
}
document.addEventListener("click", e => {
  const b = e.target.closest && e.target.closest("[data-hreg], [data-hstep], [data-hplay]"); if (!b) return;
  if (b.dataset.hreg) homeSetReg(b.dataset.hreg, true);
  else if (b.dataset.hstep) { homeT = homeStepStart(+b.dataset.hstep); homeFlipped = +b.dataset.hstep; homeDirty = true; homeNarrate(); }
  else homeSetPaused(!homePaused);
});
