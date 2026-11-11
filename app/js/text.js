// ---------- marks ----------
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const $ = id => document.getElementById(id);
const OC = {
  works: `<path d="M1.5 6.5l3 3 6-7.5" fill="none" stroke="currentColor" stroke-width="1.8"/>`,
  wrong: `<path d="M2 2l8 8M10 2l-8 8" fill="none" stroke="currentColor" stroke-width="1.8"/>`,
  stuck: `<circle cx="2" cy="6" r="1.3" fill="currentColor"/><circle cx="6" cy="6" r="1.3" fill="currentColor"/><circle cx="10" cy="6" r="1.3" fill="currentColor"/>`,
};
const ocMark = (o, cls = "") => `<svg class="oc ${cls}" width="12" height="12" viewBox="0 0 12 12" role="img" aria-label="${VERDICT[o]}">${OC[o]}</svg>`;

const val = v => `<span class="val v${v}">${v}</span>`;
const vec = (counts, names) => `<span class="vec">${counts.map((n, i) => `<i${n ? ` class="on"` : ""}>${names ? `<b>${names[i]}</b>` : ""}${n}</i>`).join("")}</span>`;
// Message and state text: pick out tagged values, count lists, rounds, stamps and the values x and y.
const TOK = /\b([xy]):([A-Z]\d+)|@\[([\d,]+)\]|\br(\d+)\b|@(\d+)|\b([xy])\b(?![=:\w])|\b(red|blue)\b|\bv(\d+(?:\.\d+)?)\b/g;
function tokens(s) {
  let out = "", last = 0, m;
  TOK.lastIndex = 0;
  while ((m = TOK.exec(s))) {
    out += esc(s.slice(last, m.index));
    if (m[1]) out += val(m[1]) + `<span class="tag">${m[2]}</span>`;
    else if (m[3]) out += vec(m[3].split(",").map(Number));
    else if (m[4]) out += `<span class="rnd">r${m[4]}</span>`;
    else if (m[5]) out += `<span class="stamp">@${m[5]}</span>`;
    else if (m[7]) out += `<span class="hue h${m[7]}">${m[7]}</span>`;
    else if (m[8]) out += `<span class="rnd">v${m[8]}</span>`;
    else out += val(m[6]);
    last = TOK.lastIndex;
  }
  return out + esc(s.slice(last));
}
function logCells(arr, prev) {
  const cell = (x, cls) => { const m = x.match(/^(#\d+ r\d+|v\d+\.\d+) (.+)$/); return `<i class="${cls}">${esc(m ? m[2] : x)}${m ? `<small>${m[1]}</small>` : ""}</i>`; };
  const gone = prev ? prev.filter(x => !arr.includes(x)) : [];
  return `<span class="log">${arr.map(x => cell(x, prev && !prev.includes(x) ? "new" : "")).join("")}${gone.map(x => cell(x, "gone")).join("")}</span>`;
}
function stateVal(v, prev, I) {
  if (Array.isArray(v)) return logCells(v.map(x => lexT(x, I)), Array.isArray(prev) ? prev.map(x => lexT(x, I)) : null);
  v = lexT(v, I);
  if (/^(?:[A-Z]\d+\s*)+$/.test(v)) { const m = [...v.matchAll(/([A-Z])(\d+)/g)]; return vec(m.map(x => +x[2]), m.map(x => nmOf(I, x[1]) ? nmOf(I, x[1])[0].toUpperCase() : x[1])); }
  if (/^(none|nobody|nothing|empty|free)$/.test(v)) return `<span class="nil">${v}</span>`;
  return tokens(v);
}
// The starting step shows everything the node holds. Later steps show what changed; the rest folds away.
function stateBox(r, I) {
  const first = !r.prevPerm, same = (cur, prev, k) => JSON.stringify(prev[k]) === JSON.stringify(cur[k]);
  const parts = [["perm", U().perm, r.perm, r.prevPerm], ["temp", U().temp, r.temp, r.prevTemp]];
  const grp = ([cls, label, cur, prev], changed) => {
    const keys = Object.keys(cur).filter(k => first || same(cur, prev, k) !== changed);
    if (!keys.length) return "";
    return `<div class="grp ${cls}"><span class="label">${label}</span>` + keys.map(k => {
      const v = cur[k], chg = !first && changed;
      const was = chg && k in prev && !Array.isArray(v) ? `<span class="was">was ${stateVal(prev[k], null, I)}</span>` : "";
      return `<div class="kv${chg ? " chg" : ""}"><span class="k">${esc(lexT(k, I))}</span><span class="v"><span class="cur">${stateVal(v, chg ? prev[k] : null, I)}</span>${was}</span></div>`;
    }).join("") + `</div>`;
  };
  const moved = parts.map(p => grp(p, true)).join("");
  if (first) return `<div class="state">${moved}</div>`;
  const rest = parts.map(p => grp(p, false)).join("");
  const names = parts.flatMap(([, , cur, prev]) => Object.keys(cur).filter(k => same(cur, prev, k))).map(k => lexT(k, I));
  return `<div class="state">${moved}${rest ? `<details class="rest"><summary>${moved ? "unchanged" : "nothing changes"}: ${esc(names.join(", "))}</summary>${rest}</details>` : ""}</div>`;
}

// Long structured messages are broken into labelled parts.
function splitTop(s) {
  const out = []; let depth = 0, cur = "";
  for (const ch of s) {
    if ("([".includes(ch)) depth++; else if (")]".includes(ch)) depth--;
    if (ch === "," && !depth) { out.push(cur.trim()); cur = ""; } else cur += ch;
  }
  return [...out, cur.trim()];
}
function msgText(text) {
  const m = text.match(/^(append|add line|estimate|leaning|lists)\((.*)\)$/);
  if (!m) return `<span class="txt">${tokens(text)}</span>`;
  const parts = splitTop(m[2]);
  if (/^a/.test(m[1]) && parts.length === 4) { parts[0] = (m[1] === "append" ? "round " : "term ") + parts[0]; parts[2] = parts[2] === "[]" ? "no new entries" : "adds " + parts[2].slice(1, -1); }
  return `<span class="txt card"><b>${m[1]}</b>${parts.map(p => `<span>${tokens(p)}</span>`).join("")}</span>`;
}
// One line per distinct message: the same text to several peers is drawn once, and a long resend is named, not repeated.
function msgs(list, dir, seen, t, I) {
  const groups = [], ext = { outside: I ? I.client : U().client, timer: U().timer, nothing: U().nothing, coin: U().coin };
  list.forEach(([peer, text, lost]) => {
    const isExt = PSEUDO.has(peer), g = !isExt && groups.find(x => !x.ext && x.raw === text);
    if (g) g.to.push([peer, lost]); else groups.push({ raw: text, text: lexT(I && I.msg && !isExt ? I.msg(text, peer, dir) : text, I), ext: isExt, kind: isExt ? peer : "peer", to: [[peer, lost]] });
  });
  return groups.map(g => {
    const all = g.to.every(x => x[1]), gone = g.to.filter(x => x[1]).map(x => nmOf(I, x[0]) || x[0]);
    const chips = g.to.map(([p, l]) => `<span class="who${g.ext ? " ext" : ""}${l ? " lw" : ""}">${esc(g.ext ? (p === "outside" && I ? clientOf(I, g.text) : ext[p]) : nmOf(I, p) || p)}</span>`).join("");
    const before = dir === "out" && g.text.length > 24 ? seen.get(g.raw) : undefined;
    if (dir === "out" && before === undefined) seen.set(g.raw, t);
    const text = !g.text ? "" : before !== undefined ? `<span class="txt again" title="${esc(g.text)}">same ${esc(g.text.split(/[(@]/)[0].trim())} as step ${before}</span>` : msgText(g.text);
    const tag = gone.length ? `<span class="xo losttag">${all ? "lost" : gone.join(", ") + " lost"}</span>` : "";
    const body = `<span class="mb">${chips}${text}${tag}</span>`;
    const wire = `<span class="wire" aria-hidden="true"></span>`, word = g.kind === "nothing" ? "" : `<span class="sr">${dir === "in" ? "from" : "to"}</span>`;
    return `<div class="m ${g.kind}${all ? " lost" : ""}">${dir === "in" ? word + body + wire : wire + word + body}</div>`;
  }).join("");
}

// In running text, node names get a small box so "A" the node never reads as "a" the article.
const ARTICLE_NEXT = new Set("client write reader different higher faster fresh single third tie majority copy list remove voter blank message task snapshot stream transfer proposal coin".split(" "));
function nodeText(text, scene) {
  const nodes = new Set([scene.who, ...(scene.peers.match(/\b[A-Z]\b/g) || [])]);
  return esc(text).replace(/\b([A-Z])\b/g, (m, n, off, str) => {
    if (!nodes.has(n)) return m;
    const next = (str.slice(off + 1).match(/^\s+(\w+)/) || [])[1];
    if (n === "A" && ARTICLE_NEXT.has(next) && /(^|[.!?:]\s+|[“(]\s*)$/.test(str.slice(0, off))) return m;
    return `<span class="nd">${n}</span>`;
  });
}
// In the telling, {A} marks a person's letter.
const mk = t => esc(t).replace(/\{([A-Z])\}/g, (m, l) => ND(l));
const listAnd = a => a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1];

