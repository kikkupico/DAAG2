// Checks that the Abstraction register's own text never uses the Allegory's vocabulary.
// Usage: node site/tools/check-leaks.js     (exit 1 if anything leaks)
//
// Allegory words are collected from TELL (roles, hats, node and place names, the words `lex`
// swaps in, the left side of each `gloss`). The plain surfaces are scanned for them:
// scene names, narration, state, messages and notes in SCENES and in the global traces, and the idea/frame of each paper.
// Exempt: PAPERS[].cite and PAPERS[].names. `names` is the glossary of the cited papers' own terms,
// which is allowed to use the paper's story (the Byzantine commander, Dynamo's cart).
const fs = require("fs"), path = require("path"), vm = require("vm");
const dir = path.join(__dirname, "..", "js");
const ctx = vm.createContext({ console });
const load = f => vm.runInContext(fs.readFileSync(path.join(dir, f), "utf8"), ctx, { filename: f });
// the same order index.html loads them in (state.js and later need the DOM, so they are not loaded)
["data/scenes.js", "rows.js", "data/papers.js", "data/telling-text.js", "data/scenes-extra.js", "data/telling.js", "data/traces.js"].forEach(load);
const get = n => vm.runInContext(`typeof ${n} === "undefined" ? undefined : ${n}`, ctx);
const SCENES = get("SCENES"), PAPERS = get("PAPERS"), TELL = get("TELL"), HAT = get("HAT"), TRACES = get("TRACES") || {};

// ---- the Allegory's vocabulary
const vocab = new Map();                       // lower-case phrase -> where it came from
const add = (w, from) => {
  if (typeof w !== "string") return;
  w = w.trim().toLowerCase().replace(/\{[a-z]\}/gi, "").trim();
  if (w.length < 3 || /[$\\]/.test(w)) return;
  if (!vocab.has(w)) vocab.set(w, from);
};
for (const [, [plural]] of Object.entries(HAT)) add(plural, "HAT");
for (const [id, I] of Object.entries(TELL)) {
  const f = `TELL.${id}`;
  add(I.role, f + ".role"); add(I.client, f + ".client");
  Object.values(I.roles || {}).forEach(w => add(w, f + ".roles"));
  Object.values(I.names || {}).forEach(w => add(w, f + ".names"));
  const st = I.stage || {};
  Object.entries(st).forEach(([k, v]) => { if (typeof v === "string" && !["view"].includes(k)) add(v, f + ".stage"); });
  Object.values(st.labels || {}).forEach(w => add(w, f + ".stage.labels"));
  Object.keys(st.labels || {}).forEach(w => add(w, f + ".stage.labels"));
  (st.also || []).forEach(w => add(w, f + ".stage.also"));
  (I.lex || []).forEach(([, b]) => add(b, f + ".lex"));
  (I.gloss || []).forEach(([a]) => add(a, f + ".gloss"));
  // `msg` is a function: run it over the result's own messages and keep what it changes
  if (typeof I.msg === "function") for (const sc of SCENES[id] || []) for (const r of sc.rows || []) for (const dir of ["in", "out"]) for (const m of (dir === "in" ? r.recv : r.sent) || []) {
    const t = m[1]; if (!t || typeof t !== "string") continue;
    let out; try { out = I.msg(t, m[0], dir); } catch (e) { continue; }
    if (typeof out !== "string" || out === t) continue;
    let i = 0; while (i < out.length && i < t.length && out[out.length - 1 - i] === t[t.length - 1 - i]) i++;
    add(out.slice(0, out.length - i), f + ".msg");
  }
}
// Words that are ordinary technical English in the plain text too (the Allegory merely reuses them).
const OK = new Set(["client", "node", "value", "primary", "server", "view", "replica", "transaction", "student", "reader", "visitor", "write", "read", "total", "the total", "primary", "photo", "album"]);
OK.forEach(w => vocab.delete(w));
if (fs.existsSync(path.join(__dirname, "leak-allow.txt")))
  fs.readFileSync(path.join(__dirname, "leak-allow.txt"), "utf8").split("\n").map(s => s.trim().toLowerCase()).filter(s => s && !s.startsWith("#")).forEach(w => vocab.delete(w));

// ---- the plain surfaces
const strings = [];                            // [where, text]
const walk = (v, where) => {
  if (typeof v === "string") strings.push([where, v]);
  else if (Array.isArray(v)) v.forEach((x, i) => walk(x, `${where}[${i}]`));
  else if (v && typeof v === "object") for (const [k, x] of Object.entries(v)) walk(x, `${where}.${k}`);
};
for (const [pid, list] of Object.entries(SCENES)) list.forEach(s => walk(s, `SCENES.${pid}.${s.id}`));
for (const p of PAPERS) for (const k of ["name", "idea", "frame"]) walk(p[k], `PAPERS.${p.id}.${k}`);
const plainOf = o => JSON.parse(JSON.stringify(o, (k, v) => k === "isle" ? undefined : v));      // `isle` is the Allegory's own account
for (const [k, T] of Object.entries(TRACES)) walk(plainOf(T), `TRACES.${k}`);      // the other nodes' accounts are shown as they are in the Abstraction

const esc = w => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const re = new Map([...vocab.keys()].map(w => [w, new RegExp(`(^|[^a-z])${esc(w)}(s|es)?([^a-z]|$)`, "i")]));
let bad = 0;
for (const [where, text] of strings) {
  for (const [w, r] of re) if (r.test(text)) { bad++; console.log(`${where}: "${w}" (from ${vocab.get(w)})\n    ${text.length > 110 ? text.slice(0, 110) + "…" : text}`); }
}
console.log(bad ? `\n${bad} possible leak(s). Fix the text, or add a word to tools/leak-allow.txt if it is plain English there.` : `no leaks: ${strings.length} strings checked against ${vocab.size} allegory words`);
process.exit(bad ? 1 : 0);
