// ---------- wiring ----------
// A key is "map", a result's id (its own page), or a scene.
const isPaper = k => PAPERS.some(x => x.id === k);
const resolve = k => { const p = PAPERS.find(x => x.id === k); return p ? byKey(`${p.id}-${p.scenes[0].id}`) : byKey(k); };
function renderDrawer() {
  const it = resolve(sel), land = isPaper(sel), a = document.activeElement;
  const f = a && a.closest && a.closest("#drawer") && (a.dataset.haz ? `[data-haz="${a.dataset.haz}"]` : a.dataset.tog ? `[data-tog="${a.dataset.tog}"]` : a.dataset.hazclear ? "[data-hazclear]" : "");
  if (it) expanded.add(it.p.id);
  $("facets").innerHTML = facetsHTML();
  $("index").innerHTML = indexHTML(it, land);
  if (f) { const el = $("drawer").querySelector(f); if (el) el.focus(); }
}
function render() {
  const it = resolve(sel), land = isPaper(sel);
  document.documentElement.dataset.reg = reg;
  $("brand").textContent = document.title = U().title;
  document.querySelectorAll(".reg button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.reg === reg)));
  renderDrawer();
  // a scene's page is the scene alone: the bar names its result, and leads back to the result's own page
  const vs = isVs(sel);
  $("where").innerHTML = vs ? "Compare" : !it ? esc(U().map) : land ? esc(paperName(it.p)) : `<button type="button" data-key="${it.p.id}">${esc(paperName(it.p))}</button><span class="sep" aria-hidden="true">/</span>${esc(nameOf(it))}`;
  $("paper").hidden = !land;
  $("paper").innerHTML = land ? paperHTML(it) : "";
  $("scene").innerHTML = vs ? vsHTML(sel) : land ? landHTML(it) : it ? sceneHTML(it) : mapHTML();
  centreStage();
  try { if (location.hash.slice(1) !== sel) history.replaceState(null, "", "#" + sel); } catch (e) {}
}
const WIDE = window.matchMedia("(min-width: 1100px)");
function setDrawer(open, keep) {
  $("app").dataset.drawer = open ? "open" : "closed";
  $("dtog").setAttribute("aria-expanded", String(open));
  if (!keep) try { localStorage.setItem("drawer", open ? "open" : "closed"); } catch (e) {}
}
// to: where the page lands. "top" (from the side menu) shows the top of the page; "scene" (from the pager) puts the scene's title under the bar.
function go(key, keep, to) {
  const was = resolve(sel), it = resolve(key);
  if (!it && key !== "map" && !vsValid(key)) return;
  if (key !== sel) stageStep = 0;
  sel = key;
  if (!keep) cmp = false;
  render();
  if (!WIDE.matches) setDrawer(false, true);
  if (keep) return;
  if (to === "top" || (to === "scene" && key === "map") || isVs(key)) window.scrollTo(0, 0);
  else if (to === "scene") $("scene").scrollIntoView({ block: "start" });
  else if (!it || !was || was.p !== it.p || isPaper(key)) $("main").scrollIntoView({ block: "start" });
  else if ($("scene").getBoundingClientRect().top < 0) $("scene").scrollIntoView({ block: "start" });
}
function act(b) {
  const d = b.dataset;
  if (d.key) go(d.key, !!d.keep, b.closest("#drawer") ? "top" : b.closest(".pager") ? "scene" : "");
  else if (d.drawer) setDrawer(d.drawer === "toggle" ? $("app").dataset.drawer !== "open" : d.drawer === "open");
  else if (d.tog) { expanded.has(d.tog) ? expanded.delete(d.tog) : expanded.add(d.tog); renderDrawer(); }
  else if (d.reg) { reg = d.reg; try { localStorage.setItem("reg", reg); } catch (e) {} render(); }
  else if (d.cmp) { cmp = !cmp; render(); }
  else if (d.haz) { haz.has(d.haz) ? haz.delete(d.haz) : haz.add(d.haz); renderDrawer(); }
  else if (d.hazclear) { haz.clear(); renderDrawer(); }
  else if (d.vsopen) { vsOpen.has(d.vsopen) ? vsOpen.delete(d.vsopen) : vsOpen.add(d.vsopen); render(); const el = document.querySelector(`[data-vsopen="${d.vsopen}"]`); if (el) el.focus(); }
  else if (d.vsswap) { const [a, b] = vsIds(sel), pk = vsPick[vsKey(a, b)]; if (pk) delete vsPick[vsKey(a, b)]; go(vsKey(b, a), true); }
  else if (d.stage) showStep(stageStep + +d.stage);
  else if (d.step) showStep(+d.step);
}
const HOT = "[data-key],[data-drawer],[data-tog],[data-reg],[data-cmp],[data-haz],[data-hazclear],[data-step],[data-stage],[data-vsopen],[data-vsswap]";
document.addEventListener("click", e => { const b = e.target.closest(HOT); if (b) act(b); });
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && !WIDE.matches && $("app").dataset.drawer === "open") { setDrawer(false, true); $("dtog").focus(); return; }
  if (e.key !== "Enter" && e.key !== " ") return;
  const b = e.target.closest(".mn, .mx");
  if (b) { e.preventDefault(); act(b); }
});
// The pickers on the compare page, a row's "set beside", and a result page's "compare with".
document.addEventListener("change", e => {
  const s = e.target.closest && e.target.closest("select[data-vs]"); if (!s) return;
  const d = s.dataset, [a, b] = vsIds(sel);
  if (d.vs === "with") { if (s.value) go(vsKey(d.a, s.value)); return; }
  if (d.vs === "pair") { const k = vsKey(a, b); (vsPick[k] = vsPick[k] || {})[d.a] = s.value; render(); }
  else go(d.vs === "a" ? vsKey(s.value, b) : vsKey(a, s.value), true);
  const el = document.querySelector(d.vs === "pair" ? `select[data-vs="pair"][data-a="${d.a}"]` : `select[data-vs="${d.vs}"]`); if (el) el.focus();
});
const fromHash = () => { const k = decodeURIComponent(location.hash.slice(1)); if (k === "map" || resolve(k) || vsValid(k)) sel = k; };
window.addEventListener("hashchange", () => { fromHash(); render(); });
let stored = null; try { stored = localStorage.getItem("drawer"); } catch (e) {}
setDrawer(WIDE.matches && stored !== "closed", true);
WIDE.addEventListener("change", () => setDrawer(WIDE.matches && stored !== "closed", true));
fromHash();
render();
