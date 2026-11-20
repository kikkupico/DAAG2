// ---------- the guide: how the site works, and how to read a scene ----------
// Not a page: a panel over the whole window, opened over the stage (the ? in its head, the drawer's Introduction, an
// address ending #intro, or the front page's ways in, which arrive with it open). It leads nowhere but back to the stage.
let guideOpen = false;
function renderGuide() {
  let el = $("guide");
  if (!guideOpen) { if (el) el.remove(); document.documentElement.classList.remove("guiding"); return; }
  const fresh = !el;
  if (fresh) { document.body.insertAdjacentHTML("beforeend", `<div class="gmodal" id="guide" role="dialog" aria-modal="true" aria-labelledby="guide-t"></div>`); el = $("guide"); }
  const top = el.querySelector(".gbody") ? el.querySelector(".gbody").scrollTop : 0;
  el.innerHTML = `<button type="button" class="gclose" data-guideclose="1" aria-label="Close the guide" title="Close (Esc)"><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M4 4l10 10M14 4L4 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>`
    + `<div class="gbody">${introHTML()}<p class="gend"><button type="button" class="btn go-out" data-guideclose="1">Begin</button></p></div>`;
  el.querySelector(".gbody").scrollTop = top;
  document.documentElement.classList.add("guiding");
  if (fresh) el.querySelector(".gclose").focus();
}
function openGuide() { guideOpen = true; renderGuide(); }
function closeGuide() { guideOpen = false; renderGuide(); const b = document.querySelector(".thead .tguide"); if (b) b.focus(); }
// Why the idea exists, and Lamport's stories, are told on the front page (home.js). This page is about how to read it,
// so it reads the same in both registers; only the title and a few nouns follow the register.
const REPO = "https://github.com/kikkupico/DAAG2";
function introHTML() {
  const isle = reg === "isle", first = ALL[0];
  const ext = (href, text) => `<a href="${href}" target="_blank" rel="noopener">${text}</a>`;
  const sect = (label, title, body) => `<section class="sect"><p class="label">${label}</p><h2>${title}</h2>${body}</section>`;
  const ps = (...xs) => xs.map(x => `<p>${x}</p>`).join("");
  const items = list => `<ul class="customs">${list.map(([a, b]) => `<li><span class="label">${a}</span>${b}</li>`).join("")}</ul>`;
  const chamber = sect("What was left out", "Why Paxos has no Chamber here", ps(
    `Lamport's legislators meet in a Chamber. Two earlier versions of this project kept it. ${ext("https://kikkupico.github.io/paxos-illustrated/", "Paxos Illustrated")} set Lamport's text, word for word, among illustrations of the hall. ${ext("https://kikkupico.github.io/DAAG/", "The first Distributed Algorithms of Ancient Greece")} built the Chamber as a round hall on the island's summit and set several of its books inside. Both were sincere attempts to draw the paper as written, and both ran into the same wall.`)
    + items([
      ["A room gathers people", "Draw legislators in one hall and the picture says they can see who is present and hear what was decided. The algorithm is about people who can do neither. Lamport gave the hall poor acoustics to stop them talking, but a drawing of a hall still shows everyone together."],
      ["A room has no distance", "A note carried across a hall cannot believably take a day, go missing, or be overtaken by a later one. A courier crossing a town can, and you can watch it happen on the road."],
      ["Absence looks checkable", "Leaving the Chamber stands for failing. In a hall you could look up and see who has left. In the algorithm a colleague who is gone and one who is merely slow are equally silent, and much of the theory rests on that."],
      ["Only one paper lives there", "A parliament hall suits Paxos and nothing else. Every other result needed a setting of its own, and the reader had to learn a new place each time."],
    ])
    + ps(`So this version keeps Lamport's island, his legislators, their ledgers and their messengers, and removes the hall. The legislators were always part-time, so here they are found at their other work, in the fishery, the granary and the winery, and they legislate from there. Nothing about the algorithm changes. What changes is that the picture now agrees with it: nobody is ever in the same room as anybody else.`));

  const one = sect("The point of view", "Why one node at a time", ps(
    `Most explanations draw the system from above: every node in a row, every message an arrow, one clock for all of it. That is the one view no participant ever has. From up there the algorithms look obvious and the impossibility results look absurd, because you can see the very thing the nodes are struggling to find out.`,
    `Here each scene is told from inside a single ${isle ? "person" : "node"}, and that makes things simpler in three ways.`)
    + items([
      ["Less to track", `There is one ${isle ? "ledger and one slate" : "state"} on screen, not one per node. Each step is one small rule: this arrived, so this is written down, so this is sent.`],
      ["The rules are local anyway", "An algorithm is only what each node does with what it has. Read from inside, a scene is the algorithm itself, with nothing to translate."],
      ["The hard arguments become visible", "Two different worlds can look identical from inside. When a pair of scenes takes the very same steps and ends differently, you have seen the proof, not been told it."],
    ])
    + `<div class="sys"><p class="sys-h">${EYE}<b>${U().seen}</b><span>shown like this</span></p><p>What the ${isle ? "person" : "node"} cannot see is never hidden from you. It is set beside the step it belongs to, in a dashed frame like this one, so that it never reads as something the ${isle ? "person" : "node"} knows.</p></div>`);

  const how = sect("A short guide", "How to use it", `<ol class="guide">${[
      ["Pick a result", "The menu, behind the three lines at the top left, lists the " + NUMWORD + " in five chapters; open a chapter to see its results. Read in order, or open " + UI.isle.map + " to see every paper, and which result answers a problem another one raises."],
      ["Read its page, then its scenes", "A result opens on its Introduction: the idea, the papers behind it and the words used, beside its picture. Its scenes follow, each marked as one that works, one that goes wrong, or one that never finishes. The head names the result and the scene, and the menu goes anywhere. The last step of a scene leads on to the next."],
      ["Step through a scene", "Use the arrows beside the row of dots, the dots themselves, or the left and right arrow keys. In the picture, couriers walk the roads; the replay button runs a step again. Beside it, each step reads top to bottom: what arrives, what is kept, what leaves. The last dot is the end: what happened, and the way on."],
      ["Know where you stand", "Each scene's name and its point sit over its steps. The ⓘ beside the name tells what the scene rests on, the paper it comes from, who you are in it, and the rule you follow."],
      ["See through other eyes", "Some scenes have tabs over their steps, one for each participant. The first tells the scene as written; any other tells the same moments from inside someone else, with what they could not see in the dashed frame."],
      ["Switch the telling", "Allegory and Abstraction, at the top of every page, tell the same steps as islanders or as nodes A, B and C. Switch at any point without losing your place."],
      ["Set two side by side", "Compare, in the menu, puts any two results next to each other. Some scenes also offer their near-twin for a step by step comparison."],
      ["Filter by what can go wrong", `Under “${U().inplay}” in the menu, pick a hazard, such as lost messages or liars, to find the results that have to live with it.`],
    ].map(([a, b]) => `<li><b>${a}.</b> ${b}</li>`).join("")}</ol>`);

  const skin = (file, alt, cap) => `<figure><img src="https://images.detangled.dev/img/${file}-800.webp" srcset="https://images.detangled.dev/img/${file}-800.webp 800w, https://images.detangled.dev/img/${file}-1200.webp 1200w" sizes="(max-width: 640px) 100vw, 300px" width="800" height="600" loading="lazy" alt="${alt}"><figcaption>${cap}</figcaption></figure>`;
  const skins = `<div class="skins">${skin("himalaya-city", "A Himalayan village seen from above: whitewashed flat-roofed houses round a white chorten, a monastery with a golden roof, barley terraces, and a turquoise river in a gorge crossed by timber bridges.", "A monastery village in the Himalaya, built in Blender")}${skin("himalaya-siege", "A fortress-monastery on a crag in the snow by night, its windows lit, ringed by a trodden track with watch fires and four camps of tents in the corners.", "Its siege: a dzong shut in by four camps in the snow")}${skin("venice-city", "A town on low islands in a teal lagoon: a domed basilica and bell tower, a paved square, palazzi and workshops, joined by stone quays and timber bridges.", "A town of the Venetian lagoon, painted by an image generator")}${skin("venice-siege", "A walled Venetian island town by night, its lanterns lit, surrounded on the dark water by four squadrons of galleys under sail and oar.", "Its siege: an island stronghold blockaded by night")}</div>`;
  const fork = `<aside class="fork"><p class="label">Not fond of the Greeks?</p>
    <p>The allegory is one choice among many. An allegory here is three things: a picture of a town and a picture of a siege, the network of roads in each, and the names of the places that stand on them. The steps of every scene are plain data and belong to neither telling, so another allegory changes none of them, and the Abstraction stays exactly as it is.</p>
    <p>To build one, ${ext(REPO, "fork the repository")}, open it with a coding agent, and point the agent at ${ext(REPO + "/tree/main/skills/build-allegory", "<code>skills/build-allegory</code>")} with a setting of your choice: a research colony on Mars, a Nile town of Ancient Egypt, a monastery in the snow.</p>
    ${skins}
    <p>Both of these were built with that skill, and both are in the menu at the foot of the side drawer.</p>
    <p>The skill paints or models the world, lays out its roads, and renames every place to match.</p></aside>`;

  return `<div class="map about">
    <div class="intro"><p class="label">The guide</p><h1 id="guide-t">How this site works</h1>
      <p class="idea">${NUMWORD.charAt(0).toUpperCase() + NUMWORD.slice(1)} results from distributed computing, each told as a few short scenes from inside one participant. In the Allegory they are ${esc(ALLEGORY.people)}. In the Abstraction they are nodes A, B and C. The steps are the same. Here is how to find your way around.</p>
    </div>
    ${how}${one}${chamber}${fork}
    <p class="src">The code, the text and the pictures are on GitHub at ${ext(REPO, "kikkupico/DAAG2")}: the code under MIT, the text and pictures under CC BY 4.0. Corrections are welcome as issues.</p>
  </div>`;
}
