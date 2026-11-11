// How many leading rows two scenes share, as the narrator sees them (lost marks and outside notes aside).
// The commentary counts too: A can't tell the two worlds apart, so neither can its story.
const localRow = (r, prose) => JSON.stringify([r.perm || {}, r.temp || {}, r.recv || [], (r.sent || []).map(m => m.slice(0, 2)), prose || ""]);
function sameRows(a, b) {
  if (localRow(a.init, a.prose[0]) !== localRow(b.init, b.prose[0])) return 0;
  let n = 0;
  while (n < a.rows.length && n < b.rows.length && localRow(a.rows[n], a.prose[n + 1]) === localRow(b.rows[n], b.prose[n + 1])) n++;
  return n;
}
function buildRows(scene) {
  let perm = applyDelta({}, scene.init.perm), temp = applyDelta({}, scene.init.temp);
  const prose = scene.prose || [];
  const rows = [{ t: 0, perm, temp, sent: [], recv: [], note: prose[0] || "", prevPerm: null, prevTemp: null }];
  scene.rows.forEach((e, i) => {
    const pp = perm, pt = temp;
    perm = applyDelta(perm, e.perm); temp = applyDelta(temp, e.temp);
    rows.push({ t: i + 1, perm, temp, sent: e.sent || [], recv: e.recv || [], note: prose[i + 1] || "", out: e.out || "", prevPerm: pp, prevTemp: pt });
  });
  return rows;
}
function applyDelta(state, delta) {
  const out = { ...state };
  for (const [k, v] of Object.entries(delta || {})) {
    if (k.endsWith("+")) { const key = k.slice(0, -1); out[key] = [...(out[key] || []), ...v]; }
    else if (v === null) delete out[k];
    else out[k] = v;
  }
  return out;
}
