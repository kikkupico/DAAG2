// ---------- the allegory: its places' names and its own words, written into the telling ----------
// The telling (data/telling.js) never names a place outright. It writes {fishery}, and the name comes from the world's network
// file by way of CITY.label and SIEGE.label; {town} is the allegory's town. {Fishery} starts with a capital and {FISHERY} is the
// initial alone. {A}, a single capital, stays what it was: a person's letter. An allegory may also bring `words`, pairs
// [from, to] swapped in as whole words after the names, for the things its people handle (an amphora, an ox-cart).
// This runs once, before anything is drawn, and only over the Allegory's text: the Abstraction's is never touched.
{
  const names = { town: ALLEGORY.town }, capital = t => t.charAt(0).toUpperCase() + t.slice(1);
  for (const G of [CITY, SIEGE]) for (const k in G.label) names[k.toLowerCase()] = G.label[k];
  const words = (ALLEGORY.words || []).map(([a, b]) => [new RegExp("\\b" + a.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "gi"), b]);
  const fill = t => {
    t = t.replace(/\{([A-Za-z][A-Za-z' ]+)\}/g, (m, k) => { const v = names[k.toLowerCase()]; return v === undefined ? m : k === k.toUpperCase() ? v.charAt(0).toUpperCase() : /^[A-Z]/.test(k) ? capital(v) : v; });
    for (const [re, b] of words) t = t.replace(re, m => /^[A-Z]/.test(m) ? capital(b) : b);
    return t;
  };
  const seen = new Set();
  const walk = o => {          // every string in o, in place
    if (!o || typeof o !== "object" || o instanceof RegExp || seen.has(o)) return;
    seen.add(o);
    for (const k of Object.keys(o)) { if (typeof o[k] === "string") o[k] = fill(o[k]); else walk(o[k]); }
  };
  for (const I of Object.values(TELL)) {
    for (const k of Object.keys(I)) {
      const v = I[k];
      if (k === "hat") continue;                                                                          // a key into HAT, not text
      if (k === "stage") { if (v.labels) for (const p in v.labels) v.labels[p] = fill(v.labels[p]); }      // the rest of a stage is role ids
      else if (k === "lex") I.lex = v.map(([a, b]) => [a, typeof b === "string" ? fill(b) : b]);          // [the Abstraction's text, the Allegory's]
      else if (k === "gloss") I.gloss = v.map(([a, b]) => [fill(a), b]);                                  // [the Allegory's term, the plain one]
      else if (k === "clientFor") I.clientFor = v.map(([a, b]) => [a, fill(b)]);
      else if (typeof v === "function") I[k] = (...a) => fill(v(...a));
      else if (typeof v === "string") I[k] = fill(v);
      else walk(v);
    }
  }
  walk(HAT);
  // the Allegory's side of the text kept outside the telling: what a result adds up to, the hazards' names, the page's own labels
  if (typeof ARC !== "undefined") for (const a of Object.values(ARC)) if (a.sum) a.sum[1] = fill(a.sum[1]);
  if (typeof HAZARDS !== "undefined") HAZARDS.forEach(h => { h[2] = fill(h[2]); });
  if (typeof UI !== "undefined") walk(UI.isle);
  ALLEGORY.fill = fill;
}

// ---------- the menu of allegories: shown in the drawer when the page holds more than one ----------
// Choosing one loads the page again, since the telling was filled with the current one's names when it loaded.
if (typeof document !== "undefined" && ALLEGORIES.list.length > 1) {
  const el = document.getElementById("alg");
  el.hidden = false;
  el.innerHTML = `<label class="label" for="algsel">Allegory</label><select id="algsel">${ALLEGORIES.list.map(a => `<option value="${a.id}"${a.id === ALLEGORIES.current ? " selected" : ""}>${a.name.replace(/[&<>"]/g, "")}</option>`).join("")}</select>`;
  el.querySelector("select").addEventListener("change", e => {
    const id = e.target.value, u = new URL(location.href); let kept = false;
    try { localStorage.setItem("allegory", id); kept = localStorage.getItem("allegory") === id; } catch (err) {}
    if (kept) u.searchParams.delete("allegory"); else u.searchParams.set("allegory", id);      // with no storage, the address carries the choice
    if (u.href === location.href) location.reload(); else location.href = u.href;
  });
}
