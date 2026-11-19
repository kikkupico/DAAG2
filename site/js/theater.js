// ---------- the stage: a result's own page and its scenes fill the window ----------
// It is not a mode: a scene with a picture is always told this way, and so is a result's own page (its "Introduction").
// The front page, the guide, the overview and a comparison stay ordinary pages. A scene's picture goes beside the stepper
// and the step's panel ("side") or above them ("stack"), whichever leaves it larger; a result's own page has its picture
// at rest beside its text ("intro"). `theater` says whether the open page is on the stage; layTheater sets it.
let theater = false;
const onStage = () => isPaper(sel) || (!cmp && !!$("stepbar") && !!$("stage"));
// The head, over everything on the stage: the menu, pickers for the result and the scene, the way to the pages before and
// after in the reading order, the two tellings, and the guide.
function theaterHead(key) {
  const i = ORDER.indexOf(key), it = resolve(key), land = isPaper(key);
  const nameOfKey = k => isPaper(k) ? paperName(resolve(k).p) + ", introduction" : nameOf(byKey(k));
  const icon = d => `<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="${d}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const nav = (k, cls, word, d) => `<button type="button" class="tnav ${cls}"${k ? ` data-key="${k}" title="${word}: ${esc(nameOfKey(k))}"` : " disabled"} aria-label="${word}${k ? ": " + esc(nameOfKey(k)) : ""}">${icon(d)}</button>`;
  const papers = PAPERS.map(p => `<option value="${p.id}"${p === it.p ? " selected" : ""}>${esc(paperName(p))}</option>`).join("");
  const scenes = `<option value="${it.p.id}"${land ? " selected" : ""}>Introduction</option>`
    + it.p.scenes.map((s, n) => { const k = `${it.p.id}-${s.id}`; return `<option value="${k}"${!land && k === key ? " selected" : ""}>${n + 1}. ${esc(nameOf(byKey(k)))}</option>`; }).join("");
  const pick = (which, label, opts) => `<label class="tpick ${which}"><span class="label">${label}</span><select data-tpick="${which}" aria-label="${label}">${opts}</select></label>`;
  const regs = `<div class="reg" role="group" aria-label="How the scenes are told">${[["isle", "Allegory"], ["plain", "Abstraction"]].map(([r, w]) => `<button type="button" data-reg="${r}" aria-pressed="${reg === r}">${w}</button>`).join("")}</div>`;
  const menu = `<button type="button" class="tnav tmenu" data-drawer="toggle" aria-label="Contents" title="Contents" aria-controls="drawer" aria-expanded="${$("shell").dataset.drawer === "open"}"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M2 4.5h14M2 9h14M2 13.5h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>`;
  const guide = `<button type="button" class="tnav tguide" data-key="intro" aria-label="The guide: how this site works" title="How this site works"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="7.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M6.9 7a2.2 2.2 0 1 1 3 2c-.6.3-.9.7-.9 1.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="9" cy="12.9" r=".9" fill="currentColor"/></svg></button>`;
  return `<div class="thead" id="thead">${menu}<div class="tgo">${nav(ORDER[i - 1], "prev", "Previous", "M9 3.5L4.5 8 9 12.5M12.5 3.5v9")}`
    + pick("paper", "Result", papers) + pick("scene", "Scene", scenes)
    + `${nav(ORDER[i + 1], "next", "Next", "M7 3.5L11.5 8 7 12.5M3.5 3.5v9")}</div>${regs}${guide}</div>`;
}
// The pickers: a result opens at its first scene (or its own page, from its own page); a scene opens as it is. The page is
// drawn afresh, so the picker that was used gets the focus back.
document.addEventListener("change", e => {
  const s = e.target.closest && e.target.closest("select[data-tpick]"); if (!s) return;
  const which = s.dataset.tpick, p = PAPERS.find(x => x.id === s.value);
  go(which === "paper" && p && !isPaper(sel) ? `${p.id}-${p.scenes[0].id}` : s.value, true);
  const el = document.querySelector(`.thead select[data-tpick="${which}"]`); if (el) el.focus();
});
document.addEventListener("click", e => {      // the page is drawn afresh for the new scene, so the button that was pressed gets the focus back
  const b = e.target.closest && e.target.closest(".thead .tnav.prev, .thead .tnav.next"); if (!b) return;
  const cls = b.classList.contains("prev") ? ".prev" : ".next"; setTimeout(() => { const el = document.querySelector(".thead " + cls); if (el && !el.disabled) el.focus(); }, 0);
});
// Sizes the stage for the window; called whenever the page is drawn, its head changes height, or the window changes.
function layTheater() {
  const root = document.documentElement, bar = $("stepbar"), fig = $("stage"), img = fig && fig.querySelector && fig.querySelector("img.wld");
  theater = onStage();
  if (!theater) { delete root.dataset.theater; if (bar) bar.style.removeProperty("--tw"); if (img) img.sizes = "(max-width: 640px) 100vw, 900px"; return; }
  const vw = window.innerWidth, ar = fig ? parseFloat(fig.style.getPropertyValue("--ar")) || 4 / 3 : 4 / 3;
  if (isPaper(sel)) {          // a result's own page: its picture at rest on the left, where the window is wide enough; the text scrolls beside it
    root.dataset.theater = "intro";
    const hh = $("thead") ? $("thead").offsetHeight : 0, vh = window.innerHeight - hh, w = vw >= 960 && fig ? Math.floor(Math.min(.5 * vw, vh * ar)) : 0;
    root.style.setProperty("--hh", hh + "px"); root.style.setProperty("--iw", w + "px");
    if (img) img.sizes = (w || 600) + "px";
    return;
  }
  // the head spans the window's width, over the picture: lay it out first (a freshly drawn stepper box has no picture width
  // yet, and without one its grid falls apart), then measure it, and the scene's own head, which the panel's column also holds
  root.dataset.theater = root.dataset.theater && root.dataset.theater !== "intro" ? root.dataset.theater : "side";
  if (!bar.style.getPropertyValue("--tw")) bar.style.setProperty("--tw", "50vw");
  const hh = $("thead") ? $("thead").offsetHeight : 0, sh = $("shead") ? $("shead").offsetHeight : 0;
  const vh = window.innerHeight - hh;
  // the least the stepper and panel need: beside the picture, or under it. On a phone the panel scrolls under a picture as
  // wide as the screen, so it is left less
  const narrow = vw < 640, side = Math.max(260, Math.min(380, .27 * vw)), rest = narrow ? Math.max(240, .3 * vh) : Math.max(330, .38 * vh) + Math.min(sh, 160);
  const a = Math.min(vw - side, vh * ar), b = Math.min(vw, (vh - rest) * ar), w = Math.floor(Math.max(a, b));
  root.dataset.theater = a >= b ? "side" : "stack";
  bar.style.setProperty("--tw", w + "px");
  if (img) img.sizes = w + "px";      // so the browser picks a file sharp enough for the larger picture
}
window.addEventListener("resize", () => { if (theater) layTheater(); });
