// ---------- the stage: a result's own page and its scenes fill the window ----------
// It is not a mode: a scene with a picture is always told this way, and so is a result's own page (its "Introduction").
// The front page, the guide, the overview and a comparison stay ordinary pages. A scene's picture goes beside the stepper
// and the step's panel ("side") or above them ("stack"), whichever leaves it larger; a result's own page has its picture
// at rest beside its text ("intro"). `theater` says whether the open page is on the stage; layTheater sets it.
let theater = false;
const onStage = () => isPaper(sel) || sel === "map" || (!!$("stepbar") && !!$("stage"));
// The head, over everything on the stage: the menu (the way to anywhere); where you are, the result as a title over the
// scene; the overview; the two tellings; the guide. The way on through a result is the scene's own: its stepper, and the
// end card's next scene.
function theaterHead(key) {
  const isMap = key === "map", it = isMap ? null : resolve(key), land = isPaper(key);
  const n = it ? it.p.scenes.findIndex(s => s.id === it.s.id) + 1 : 0;
  const where = isMap ? `<span class="tp"><b>${U().map}</b></span><span class="ts">The ${NUMWORD}, and how they connect</span>`
    : land ? `<span class="tp">Introduction</span><span class="ts">${esc(paperName(it.p))}</span>`
    : `<span class="tp"><b>${esc(paperName(it.p))}</b><i> · scene ${n} of ${it.p.scenes.length}</i></span><span class="ts">${esc(nameOf(it))}</span>`;
  const regs = `<div class="reg" role="group" aria-label="How the scenes are told">${[["isle", "Allegory"], ["plain", "Abstraction"]].map(([r, w]) => `<button type="button" data-reg="${r}" aria-pressed="${reg === r}">${w}</button>`).join("")}</div>`;
  const menu = `<button type="button" class="tnav tmenu" data-drawer="toggle" aria-label="Contents" title="Contents" aria-controls="drawer" aria-expanded="${$("shell").dataset.drawer === "open"}"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M2 4.5h14M2 9h14M2 13.5h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>`;
  const map = `<button type="button" class="tnav tmap" data-key="map" aria-label="${U().map}: the ${NUMWORD}, and how they connect" title="${U().map}"${isMap ? ` aria-current="page"` : ""}><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M1.5 4.5l5-2 5 2 5-2v11l-5 2-5-2-5 2z M6.5 2.5v11 M11.5 4.5v11" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg></button>`;
  const guide = `<button type="button" class="tnav tguide" data-key="intro" aria-label="The guide: how this site works" title="How this site works"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="7.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M6.9 7a2.2 2.2 0 1 1 3 2c-.6.3-.9.7-.9 1.4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="9" cy="12.9" r=".9" fill="currentColor"/></svg></button>`;
  return `<div class="thead" id="thead">${menu}<div class="tgo"><div class="tt">${where}</div></div>${map}${regs}${guide}</div>`;
}
// Sizes the stage for the window; called whenever the page is drawn, its head changes height, or the window changes.
function layTheater() {
  const root = document.documentElement, bar = $("stepbar"), fig = $("stage"), img = fig && fig.querySelector && fig.querySelector("img.wld");
  theater = onStage();
  // on an upright phone two pictures do not go side by side: they take turns, full width, and a swipe changes which is up
  const swipe = theater && !!$("stage2") && window.innerWidth < 640 && window.innerHeight > window.innerWidth;
  if (swipe) root.dataset.swipe = "1"; else delete root.dataset.swipe;
  if (!theater) { delete root.dataset.theater; if (bar) bar.style.removeProperty("--tw"); if (img) img.sizes = "(max-width: 640px) 100vw, 900px"; return; }
  // two twin scenes side by side are one picture twice as wide
  const vw = window.innerWidth, ar = (fig ? parseFloat(fig.style.getPropertyValue("--ar")) || 4 / 3 : 4 / 3) * ($("stage2") && !swipe ? 2 : 1);
  if (isPaper(sel) || sel === "map") {      // a result's own page: its picture at rest on the left; the Papers page: the map on the right (theater.css) where the window is wide enough; the text scrolls beside it
    root.dataset.theater = "intro";
    const map = sel === "map", hh = $("thead") ? $("thead").offsetHeight : 0, vh = window.innerHeight - hh;
    const w = vw < 960 ? 0 : map ? Math.floor(.42 * vw) : fig ? Math.floor(Math.min(.5 * vw, vh * ar)) : 0;
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
  const narrow = vw < 640, side = Math.max(260, Math.min(380, .27 * vw)), rest = Math.max(330, .38 * vh) + Math.min(sh, 160);
  const a = Math.min(vw - side, vh * ar), b = Math.min(vw, (vh - rest) * ar);
  // an upright phone: the picture under the head takes about a third of the height, so the step's text has room
  const up = narrow && a < Math.min(vw, .34 * window.innerHeight * ar), w = Math.floor(up ? Math.min(vw, .34 * window.innerHeight * ar) : Math.max(a, b));
  root.dataset.theater = up || a < b ? "stack" : "side";
  bar.style.setProperty("--tw", w + "px");
  if (img) img.sizes = w + "px";      // so the browser picks a file sharp enough for the larger picture
}
window.addEventListener("resize", () => { if (theater) layTheater(); });
