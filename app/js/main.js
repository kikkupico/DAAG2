// ---------- wiring ----------
function setLens(v) {
  lens = v;
  document.documentElement.dataset.lens = v;
  document.querySelectorAll(".lsw").forEach(b => b.setAttribute("aria-checked", String(v === "outside")));
  try { localStorage.setItem("lens", v); } catch (e) {}
}
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
  $("where").textContent = it ? paperName(it.p) + (land ? "" : " · " + nameOf(it)) : U().map;
  $("paper").hidden = !it;
  $("paper").innerHTML = it ? paperHTML(it) : "";
  $("scene").innerHTML = land ? landHTML(it) : it ? sceneHTML(it) : mapHTML();
  setLens(lens); centreStage();
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
  if (!it && key !== "map") return;
  if (key !== sel) stageStep = 0;
  sel = key;
  if (!keep) cmp = false;
  render();
  if (!WIDE.matches) setDrawer(false, true);
  if (keep) return;
  if (to === "top" || (to === "scene" && key === "map")) window.scrollTo(0, 0);
  else if (to === "scene") $("scene").scrollIntoView({ block: "start" });
  else if (!it || !was || was.p !== it.p || isPaper(key)) $("main").scrollIntoView({ block: "start" });
  else if ($("scene").getBoundingClientRect().top < 0) $("scene").scrollIntoView({ block: "start" });
}
function act(b) {
  const d = b.dataset;
  if (d.key) go(d.key, !!d.keep, b.closest("#drawer") ? "top" : b.closest(".pager") ? "scene" : "");
  else if (d.drawer) setDrawer(d.drawer === "toggle" ? $("app").dataset.drawer !== "open" : d.drawer === "open");
  else if (d.tog) { expanded.has(d.tog) ? expanded.delete(d.tog) : expanded.add(d.tog); renderDrawer(); }
  else if (d.lens) setLens(d.lens === "toggle" ? (lens === "outside" ? "inside" : "outside") : d.lens);
  else if (d.reg) { reg = d.reg; try { localStorage.setItem("reg", reg); } catch (e) {} render(); }
  else if (d.cmp) { cmp = !cmp; render(); }
  else if (d.haz) { haz.has(d.haz) ? haz.delete(d.haz) : haz.add(d.haz); renderDrawer(); }
  else if (d.hazclear) { haz.clear(); renderDrawer(); }
  else if (d.stage) showStep(stageStep + +d.stage);
  else if (d.step) showStep(+d.step);
}
const HOT = "[data-key],[data-drawer],[data-tog],[data-lens],[data-reg],[data-cmp],[data-haz],[data-hazclear],[data-step],[data-stage]";
document.addEventListener("click", e => { const b = e.target.closest(HOT); if (b) act(b); });
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && !WIDE.matches && $("app").dataset.drawer === "open") { setDrawer(false, true); $("dtog").focus(); return; }
  if (e.key !== "Enter" && e.key !== " ") return;
  const b = e.target.closest(".mn");
  if (b) { e.preventDefault(); act(b); }
});
const fromHash = () => { const k = location.hash.slice(1); if (k === "map" || resolve(k)) sel = k; };
window.addEventListener("hashchange", () => { fromHash(); render(); });
let stored = null; try { stored = localStorage.getItem("drawer"); } catch (e) {}
setDrawer(WIDE.matches && stored !== "closed", true);
WIDE.addEventListener("change", () => setDrawer(WIDE.matches && stored !== "closed", true));
fromHash();
render();
