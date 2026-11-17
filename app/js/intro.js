// ---------- the introduction: what this is, where it comes from, and how to read it ----------
// The landing page. It is about the app itself, so it reads the same in both registers; only the title and a few nouns follow the register.
const REPO = "https://github.com/kikkupico/DAAG2";
function introHTML() {
  const isle = reg === "isle", first = ALL[0];
  const ext = (href, text) => `<a href="${href}" target="_blank" rel="noopener">${text}</a>`;
  const sect = (label, title, body) => `<section class="sect"><p class="label">${label}</p><h2>${title}</h2>${body}</section>`;
  const ps = (...xs) => xs.map(x => `<p>${x}</p>`).join("");
  const items = list => `<ul class="customs">${list.map(([a, b]) => `<li><span class="label">${a}</span>${b}</li>`).join("")}</ul>`;
  const go = `<div class="ctl"><button type="button" class="btn go-out" data-key="${first.p.id}">Start with ${esc(paperName(first.p))}</button><button type="button" class="btn" data-key="map">${UI.isle.map}: how the sixteen connect</button></div>`;
  const pic = CITY.img3d || CITY.img, H = ALLEGORY.hero || {};
  const hero = `<figure class="hero"><img src="${pic[1200]}" srcset="${Object.entries(pic).map(([w, f]) => f + " " + w + "w").join(", ")}" sizes="(max-width: 640px) 100vw, 900px" width="1200" height="900" alt="${esc(H.alt || "The town of " + ALLEGORY.town + " seen from above, with roads between the places where its people work.")}">
    <figcaption>${esc(H.caption || "The town of " + ALLEGORY.town + ". Nobody here shares a room. Every message in every scene walks one of these roads.")}</figcaption></figure>`;

  const purpose = sect("The purpose", "Sixteen results, one message at a time", ps(
    `The classic results of distributed computing are short to state and hard to keep in your head. Logical clocks, Paxos, the FLP impossibility, the CAP theorem, Byzantine agreement: each fits on a page, and each tends to slip away a week after you have read it.`,
    `The rules are not the hard part. The hard part is that nobody in the system sees the whole of it. A participant knows what it has written down and what has reached it, and everything else is a guess. This app lets you sit in that seat. Each result is told as a few short scenes, each scene is a handful of steps, and at each step you see exactly what one participant holds, what arrives and what it sends.`));

  const inspiration = sect("The inspiration", "Lamport told it as a story, twice", ps(
    `In 1982 Leslie Lamport, Robert Shostak and Marshall Pease described agreement among faulty computers as ${ext("https://lamport.azurewebsites.net/pubs/byz.pdf", "<cite>The Byzantine Generals Problem</cite>")}: generals camped around an enemy city, who can reach one another only by messenger, must settle on one plan although some of them are traitors. The story made the problem famous.`,
    `Encouraged by that, Lamport cast his next algorithm as archaeology. ${ext("https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf", "<cite>The Part-Time Parliament</cite>")} reports on the lost parliament of the Greek island of Paxos, whose legislators wandered in and out of the Chamber, kept their own ledgers, spoke only through forgetful messengers, and still never passed two conflicting laws. It was written in 1990 and published in 1998. Readers found the story harder than the algorithm, and in 2001 he retold it without the island as <cite>Paxos Made Simple</cite>.`,
    `This app takes both stories at their word and puts them in one place. The part-time legislators and the besieging generals are Lamport's. Merchants and scholars were added to carry the results that are about ordering events and about answering without waiting. All of them live in the same town and use the same few things: a courier, a ledger, a slate, an hourglass.`));

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
      ["Pick a result", "The menu lists the sixteen in four chapters. Read in order, or open the " + UI.isle.map + " to see which result answers a problem another one raises."],
      ["Read its page, then its scenes", "A result's own page gives the idea, the papers behind it and the words used. Its scenes follow, each marked as one that works, one that goes wrong, or one that never finishes."],
      ["Step through a scene", "Use the arrows beside the row of dots, the dots themselves, or the left and right arrow keys. In the picture, couriers walk the roads; the replay button runs a step again. Under it, each step reads left to right: what arrives, what is kept, what leaves."],
      ["Switch the telling", "Allegory and Abstraction, at the top of every page, tell the same steps as islanders or as nodes A, B and C. Switch at any point without losing your place."],
      ["Fill the window", "Theater mode, the button on the picture or the F key, gives the scene the whole screen."],
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
    <div class="intro"><h1>${U().title}</h1>
      <p class="idea">Sixteen results from distributed computing, each told as a few short scenes from inside one participant. In the Allegory they are ${esc(ALLEGORY.people)}. In the Abstraction they are nodes A, B and C. The steps are the same.</p>
      ${go}</div>
    ${hero}${purpose}${inspiration}${chamber}${one}${how}${fork}
    <p class="src">The code, the text and the pictures are on GitHub at ${ext(REPO, "kikkupico/DAAG2")}: the code under MIT, the text and pictures under CC BY 4.0. Corrections are welcome as issues.</p>
    <nav class="pager" aria-label="Reading order"><button type="button" data-key="map"><span class="label">Next</span><span>${U().map}</span></button><button type="button" data-key="${first.p.id}"><span class="label">Or begin · the first result</span><span>${esc(paperName(first.p))}</span></button></nav>
  </div>`;
}
