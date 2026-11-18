// ---------- theater mode: the stepper box fills the window, and the picture takes all the room the rest can spare ----------
// The picture goes beside the stepper and the step's panel ("side") or above them ("stack"), whichever leaves it larger.
// On a touch screen the page also goes fullscreen where the browser allows it, to win back the browser's own bars.
let theater = false, theaterFs = false;
const theaterBtn = () => `<button type="button" class="thb" data-theater="1" aria-pressed="${theater}" aria-label="Theater mode" title="${theater ? "Leave theater mode (Esc)" : "Theater mode (F)"}">`
  + `<svg class="ti-in" viewBox="0 0 14 14" aria-hidden="true"><path d="M1.5 5V1.5H5M9 1.5h3.5V5M12.5 9v3.5H9M5 12.5H1.5V9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`
  + `<svg class="ti-out" viewBox="0 0 14 14" aria-hidden="true"><path d="M5 1.5V5H1.5M12.5 5H9V1.5M9 12.5V9h3.5M1.5 9H5v3.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>`;
// The result's name and the scene's, and the way to the pages before and after in the reading order: shown only in theater mode,
// where the page's own title and pager are out of sight. A result's own page gets the same head, with the way out of theater mode.
function theaterHead(key) {
  const i = ORDER.indexOf(key), it = resolve(key), land = isPaper(key), n = it.p.scenes.indexOf(it.s) + 1;
  const nameOfKey = k => isPaper(k) ? paperName(resolve(k).p) + ", introduction" : nameOf(byKey(k));
  const icon = d => `<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="${d}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const nav = (k, cls, word, d) => `<button type="button" class="tnav ${cls}"${k ? ` data-key="${k}" title="${word}: ${esc(nameOfKey(k))}"` : " disabled"} aria-label="${word}${k ? ": " + esc(nameOfKey(k)) : ""}">${icon(d)}</button>`;
  return `<div class="thead" id="thead">${nav(ORDER[i - 1], "prev", "Previous", "M9 3.5L4.5 8 9 12.5M12.5 3.5v9")}`
    + `<div class="tt"><span class="tp"><b>${esc(paperName(it.p))}</b><i>${land ? "" : ` · scene ${n} of ${it.p.scenes.length}`}</i></span><span class="ts">${land ? "Introduction" : esc(nameOf(it))}</span></div>`
    + `${nav(ORDER[i + 1], "next", "Next", "M7 3.5L11.5 8 7 12.5M3.5 3.5v9")}${land ? `<button type="button" class="tnav thx" aria-label="Leave theater mode" title="Leave theater mode (Esc)">${icon("M6 2.5V6H2.5M13.5 6H10V2.5M10 13.5V10h3.5M2.5 10H6v3.5")}</button>` : ""}</div>`;
}
document.addEventListener("click", e => {      // the page is drawn afresh for the new scene, so the button that was pressed gets the focus back
  const b = e.target.closest && e.target.closest(".thead .tnav"); if (!b) return;
  const cls = b.classList.contains("prev") ? ".prev" : ".next"; setTimeout(() => { const el = document.querySelector(".thead " + cls); if (el && !el.disabled) el.focus(); }, 0);
});
function layTheater() {      // sizes the picture for the window; called whenever the page is drawn, the mode changes or the window does
  const root = document.documentElement, bar = $("stepbar"), fig = $("stage"), img = fig && fig.querySelector && fig.querySelector("img.wld");
  const land = isPaper(sel);
  if (theater && !land && (!bar || !fig)) { theater = false; leaveFullscreen(); }      // a page with nothing to show this way: the map, a comparison
  document.querySelectorAll(".thb").forEach(b => { b.setAttribute("aria-pressed", String(theater)); b.title = theater ? "Leave theater mode (Esc)" : "Theater mode (F)"; });
  if (!theater) { delete root.dataset.theater; if (bar) bar.style.removeProperty("--tw"); if (img) img.sizes = "(max-width: 640px) 100vw, 900px"; return; }
  if (land) { root.dataset.theater = "intro"; return; }      // a result's own page: the page itself fills the window, under the same head
  const vw = window.innerWidth, vh = window.innerHeight, ar = parseFloat(fig.style.getPropertyValue("--ar")) || 4 / 3;
  const side = Math.max(260, Math.min(360, .26 * vw)), rest = Math.max(330, .38 * vh);      // the least the stepper and panel need: beside the picture, or under it
  const a = Math.min(vw - side, vh * ar), b = Math.min(vw, (vh - rest) * ar), w = Math.floor(Math.max(a, b));
  root.dataset.theater = a >= b ? "side" : "stack";
  bar.style.setProperty("--tw", w + "px");
  if (img) img.sizes = w + "px";      // so the browser picks a file sharp enough for the larger picture
}
function leaveFullscreen() { if (theaterFs && document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(() => {}); theaterFs = false; }
// A phone held upright gains nothing from theater mode, so there the button asks for the phone to be turned. Where the browser allows it
// (Android), the page goes fullscreen and turns itself; elsewhere a prompt waits for the turn. Turning the phone back upright leaves theater mode.
const UPRIGHT = window.matchMedia("(max-width: 640px) and (orientation: portrait) and (pointer: coarse)");
let turnAsk = false;
function askTurn() {
  turnAsk = true;
  let el = $("turn");
  if (!el) {
    document.body.insertAdjacentHTML("beforeend", `<div class="turn" id="turn" role="dialog" aria-modal="true" aria-labelledby="turn-t"><div class="turn-c">`
      + `<svg class="turn-i" width="56" height="56" viewBox="0 0 56 56" aria-hidden="true"><rect x="18" y="8" width="20" height="40" rx="4" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M25 42h6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>`
      + `<p id="turn-t">Turn your phone sideways for theater mode</p><button type="button" class="btn sm">Cancel</button></div></div>`);
    el = $("turn");
  }
  el.hidden = false; el.querySelector("button").focus();
  const d = document.documentElement, o = screen.orientation;
  if (d.requestFullscreen && !document.fullscreenElement) d.requestFullscreen().then(() => { theaterFs = true; return o && o.lock ? o.lock("landscape") : null; }).catch(() => {});
}
function endTurn() { turnAsk = false; const el = $("turn"); if (el) el.hidden = true; }
function turned(upright) {
  if (!upright && turnAsk) { endTurn(); setTheater(true); }
  else if (upright && theater) setTheater(false);
}
UPRIGHT.addEventListener("change", () => turned(UPRIGHT.matches));
function setTheater(on) {
  if (on && UPRIGHT.matches) { if ($("stepbar") && $("stage")) askTurn(); return; }
  endTurn();
  theater = on && (isPaper(sel) || (!!$("stepbar") && !!$("stage")));
  const el = document.documentElement;
  if (theater && window.matchMedia("(pointer: coarse)").matches && el.requestFullscreen && !document.fullscreenElement) el.requestFullscreen().then(() => { theaterFs = true; }).catch(() => {});
  if (!theater) leaveFullscreen();
  layTheater(); playCity();
  const g = document.querySelector(".stepbar .sgs"), dot = document.querySelector(".stepbar .sgs .sd.on"); if (g && dot) g.scrollLeft = dot.offsetLeft - (g.clientWidth - dot.offsetWidth) / 2;
}
document.addEventListener("click", e => { const t = e.target.closest && e.target.closest("#turn"); if (t && (e.target === t || e.target.closest("button"))) setTheater(false); });      // Cancel, or a tap outside the prompt
document.addEventListener("click", e => { if (e.target.closest && e.target.closest(".thb, .thx")) setTheater(!theater); });
document.addEventListener("keydown", e => {
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  if (e.key === "Escape" && (theater || turnAsk)) { setTheater(false); const b = document.querySelector(".thb"); if (b) b.focus(); }
  else if ((e.key === "f" || e.key === "F") && ($("stage") || isPaper(sel)) && !(e.target.closest && e.target.closest("input, textarea, select"))) setTheater(!theater);
});
document.addEventListener("fullscreenchange", () => { if (!document.fullscreenElement && theaterFs) { theaterFs = false; setTheater(false); } });      // the browser's own way out of fullscreen leaves theater mode too
window.addEventListener("resize", () => { if (theater) layTheater(); });
