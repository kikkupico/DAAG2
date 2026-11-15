"""Reskin kit: repaints a stage (the city, or the siege) in another setting with an image generator, in two passes, so that
every messenger route and every place stays where the animation expects it while everything else follows the setting.

  python3 world/reskin/reskin.py build                         # writes the plates, guides and inpainting masks of both stages here
  python3 world/reskin/reskin.py generate "<setting>" [name]   # both passes through the Gemini API, into out/<name>-*.png
  python3 world/reskin/reskin.py prompts "<setting>"           # prints the two prompts, for pasting into a generator by hand
  python3 world/reskin/reskin.py mark <image>                  # writes <image>-marked.png: the numbered discs drawn over a pass-1 painting
  python3 world/reskin/reskin.py lock <image> <ground>         # writes <image>-locked.png: the pass-1 routes pasted back over a finished picture
  python3 world/reskin/reskin.py check <image>                 # writes <image>-overlay.png: routes and doors drawn over a generated picture

Add --siege anywhere for the siege stage; the city is the default. Pass 1 turns the stage's plate (its routes as dark bands,
pixel paths taken straight from app/js/data/<stage>.js) into the bare ground of the setting. Pass 2 gets that painting with a
numbered disc on every place and builds a landmark on each. For the siege, generate then locks the routes (see lock)."""
import base64, json, os, re, sys, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
MODEL = "gemini-nano-banana-2.1"    # the only model to use here: it edits in place. gemini-3-pro-image repaints the picture and leaves discs in it
AVOID = "people, animals, text, numbers, discs, labels, new routes, moved routes, haze or shadow hiding the routes"

# Per stage: the places in the reading order of their discs, with the kind of landmark each one is; the places whose disc
# sits on their door, not on the place itself; whether the routes of pass 1 are pasted back over pass 2 (see lock); what
# pass 1 is told about the ground; what pass 2 is told to build.
STAGES = {
    "city": dict(
        doors=(), lock=False, high="The highest ground is at the upper right.", what="the empty landscape of {setting}",
        build="build the settlement into it", fill="Do not fall back on a generic town with fields.",
        order=[("winery", "a place where goods are produced: a working estate of its own"),
               ("northwest library", "a place where knowledge or records are kept"),
               ("temple library", "a place where knowledge or records are kept, close to the seat of power"),
               ("temple", "the seat of power: the grandest place in the picture, on the highest ground"),
               ("proposer P", "a prosperous household, marked by one strong blue feature"),
               ("crossroads", "an open public space where the routes cross, with one centrepiece standing beside the crossing; travellers arrive here"),
               ("pottery", "a workshop where something is made by hand"),
               ("proposer Q", "a rival household, the same size and style as 5, marked by one strong red feature"),
               ("fishery", "a place where goods are produced: a working estate of its own"),
               ("southeast library", "a place where knowledge or records are kept"),
               ("granary", "a place where goods are produced: a working estate of its own")]),
    "siege": dict(
        doors=("enemy city",), lock=True, high="The ground inside the ring of routes is open and nearly level. It is a clear night, lit by the moon.",
        what="the empty ground on which a stronghold of {setting} will stand and be besieged",
        build="build a siege into it, by night", fill="Nothing here is at peace: it is the ground of a siege. The ring of routes keeps its exact size and its straight sides, reaching as near the edges of the frame as it does now; the camps fit into the corners outside it.",
        order=[("camp C", "a compact camp of the besieging force, lit from within, wholly outside the ring of routes"),
               ("commander's camp", "the headquarters of the besieging force: the best appointed of the four camps, lit from within, wholly outside the ring of routes"),
               ("enemy city", "the besieged stronghold: a large, dense, fortified place that fills most of the ground inside the ring of routes and stops short of it all round, shut tight, with no way in from any route"),
               ("camp B", "a compact camp of the besieging force, lit from within, wholly outside the ring of routes"),
               ("camp A", "a compact camp of the besieging force, lit from within, wholly outside the ring of routes")]),
}
# The stage's camera (iso in the stage data): the animation's paths are drawn for this view and no other.
CAMERA = ("The camera is fixed: a parallel projection with no perspective and no vanishing point, as in an isometric map, looking "
          "down from the south-east at about 50 degrees above the horizon. North is toward the upper right of the frame and east "
          "toward the lower right. Everything upright rises straight up the frame and shows its top together with its south and "
          "east sides; a circle lying on the ground appears as an ellipse three quarters as tall as it is wide. It is never a "
          "straight-down plan view.")
COUNT = "zero one two three four five six seven eight nine ten eleven twelve".split()

def load(stage):
    global S, C, AW, AH, PRE
    S = STAGES[stage]; src = open(os.path.join(REPO, f"app/js/data/{stage}.js")).read()
    C = json.loads(re.search(r"const [A-Z]+ = (\{.*?\});\n", src, re.S).group(1)); AW, AH = C["w"], C["h"]
    PRE = "" if stage == "city" else stage + "-"                               # the siege's files are prefixed, the city's are not

def bands(d, ss, width, fill):
    for pts in C["routes"].values():
        q = [(x * ss, y * ss) for x, y in pts]; d.line(q, fill=fill, width=round(width * ss), joint="curve"); r = width * ss / 2
        for x, y in (q[0], q[-1]): d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

def discs(im, ss=1):
    """Draws the numbered disc of every place over im (in place), at ss times the stage's pixel scale."""
    d = ImageDraw.Draw(im)
    try: font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", int(30 * ss))
    except OSError: font = ImageFont.load_default(size=int(30 * ss))
    for i, (n, _) in enumerate(S["order"], 1):
        x, y = (c * ss for c in C["doors" if n in S["doors"] else "places"][n]); r = 26 * ss
        d.ellipse((x - r, y - r, x + r, y + r), fill=(214, 40, 40), outline=(255, 255, 255), width=int(4 * ss))
        d.text((x, y), str(i), fill=(255, 255, 255), font=font, anchor="mm")
    return im

def build(ss=2):
    im = Image.new("RGB", (AW * ss, AH * ss), (226, 222, 212)); bands(ImageDraw.Draw(im), ss, 22, (60, 52, 44))
    im.resize((AW, AH), Image.LANCZOS).save(os.path.join(HERE, PRE + "plate.png"))
    discs(im, ss).resize((AW, AH), Image.LANCZOS).save(os.path.join(HERE, PRE + "guide.png"))
    m = Image.new("L", (AW, AH), 0); bands(ImageDraw.Draw(m), 1, 44, 255)       # every route widened, for an inpainting pass
    m.save(os.path.join(HERE, PRE + "inpaint-mask-1600.png")); m.resize((1024, 768), Image.LANCZOS).save(os.path.join(HERE, PRE + "inpaint-mask-1024.png"))

def mark(path):
    im = Image.open(path).convert("RGB"); discs(im, im.width / AW)
    out = path.rsplit(".", 1)[0] + "-marked.png"; im.save(out); print("wrote", out)

def lock(final, ground, out):
    """Pastes the routes of the pass-1 painting back over the finished one, with soft edges, so that a road lies exactly under
    every route whatever pass 2 did to it. Right for the siege, whose ring pass 2 rounds off and where nothing tall stands by
    the road; in the city a building in front of a road would be cut by it, and pass 2 keeps the roads anyway."""
    f = Image.open(final).convert("RGB"); g = Image.open(ground).convert("RGB").resize(f.size, Image.LANCZOS); ss = f.width / AW
    m = Image.new("L", f.size, 0); bands(ImageDraw.Draw(m), ss, 34, 255)
    Image.composite(g, f, m.filter(ImageFilter.GaussianBlur(7 * ss))).save(out); print("wrote", out)

def check(path):
    im = Image.open(path).convert("RGB").resize((AW, AH)); d = ImageDraw.Draw(im)
    for pts in C["routes"].values(): d.line([tuple(p) for p in pts], fill=(255, 0, 200), width=3)
    for n, (x, y) in C["doors"].items():
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 220, 0), outline=(0, 0, 0), width=2)
        d.text((x + 12, y - 8), n, fill=(0, 0, 0), stroke_width=3, stroke_fill=(255, 255, 255))
    out = path.rsplit(".", 1)[0] + "-overlay.png"; im.save(out); print("wrote", out)

GROUND = """The attached image is a plate: blank pale ground crossed by dark bands.

Repaint it as {what}, as a detailed, realistic aerial illustration, before anything large has been built there. {camera}

Treat this as an edit: the network of dark bands stays exactly where it is in the frame (every band, bend, junction and dead end, at the same position, shape and width) and only its surface changes.

- Each dark band becomes a route that people in this setting walk along, whatever that is here (never a waterway). This includes the bands that run close to the edges of the frame. Every route is continuous, open to the sky and clearly visible from above along its whole length, in strong contrast with what lies beside it. A route ends where its band ends, short of the frame. No other route of similar width exists anywhere.
- Between the routes, paint only what this setting stands on (land, water, ice, sand, rock, whatever it is here), with its relief, its vegetation, its weather and its light, and make it as particular to this setting as you can. {high} The view looks down on the ground: it fills the whole frame, with no horizon and no sky. No buildings yet.

Avoid: people, animals, text, labels, extra routes, haze or shadow hiding the routes, a changed framing."""

BUILD = """The attached painting shows {what} with its routes. {count} numbered red discs have been placed on it.

Edit the painting: {build}. {camera}

Change nothing else: same framing and scale, same light, same ground, and every route exactly as painted, at the same position in the frame, with the same shape, width and surface.

- Replace each numbered disc with one landmark of the kind listed below. The landmark stands exactly where its disc is (the disc marks the centre of its footprint), beside the route, never on it, with its entrance at the nearest route end. Choose what each landmark is so that it belongs to this setting. No disc or number is left in the finished painting.
- Fill the remaining gaps between the routes with the smaller structures, working areas and props that only this setting would have, so that it looks lived in. {fill}
- Every route stays open to the sky and visible along its whole length. Nothing stands on, bridges over or overhangs a route.

Landmarks:
{landmarks}

Avoid: {avoid}."""

def prompts(setting):
    what = S["what"].format(setting=setting)
    return (GROUND.format(what=what, high=S["high"], camera=CAMERA),
            BUILD.format(what=what, camera=CAMERA, count=COUNT[len(S["order"])].capitalize(), build=S["build"], fill=S["fill"], avoid=AVOID,
                         landmarks="\n".join(f"{i}. {k}" for i, (_, k) in enumerate(S["order"], 1))))

def paint(prompt, src, out):
    """One edit of the image at src through the Gemini interactions API (key in GEMINI_API_KEY), saved to out."""
    body = {"model": MODEL, "store": False, "response_format": {"type": "image", "aspect_ratio": "4:3", "image_size": "2K"},
            "input": [{"type": "text", "text": prompt},
                      {"type": "image", "mime_type": "image/png", "data": base64.b64encode(open(src, "rb").read()).decode()}]}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", json.dumps(body).encode(),
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json", "Api-Revision": "2026-05-20"})
    try: r = json.load(urllib.request.urlopen(req, timeout=600))
    except urllib.error.HTTPError as e: sys.exit(f"{e.code}: {e.read().decode()[:800]}")
    data = [c["data"] for s in r.get("steps", []) for c in s.get("content") or [] if c.get("type") == "image" and c.get("data")]
    if not data: sys.exit("no image came back: " + json.dumps(r)[:800])
    open(out, "wb").write(base64.b64decode(data[-1])); print("wrote", out)

def generate(setting, name=None):
    """Both passes. An existing out/<name>-ground.png is kept, so a good ground can be built on again after a poor pass 2
    (delete it to repaint the ground)."""
    out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True); p1, p2 = prompts(setting)
    base = os.path.join(out, PRE + (name or re.sub(r"[^a-z0-9]+", "-", setting.lower()).strip("-")[:40])); ground = base + "-ground.png"
    if os.path.exists(ground): print("keeping", ground)
    else: paint(p1, os.path.join(HERE, PRE + "plate.png"), ground)
    check(ground); mark(ground)
    if S["lock"]: paint(p2, base + "-ground-marked.png", base + "-raw.png"); lock(base + "-raw.png", ground, base + ".png")
    else: paint(p2, base + "-ground-marked.png", base + ".png")
    check(base + ".png")

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--siege"]; cmd = a[0] if a else ""; load("siege" if "--siege" in sys.argv else "city")
    if cmd == "build":
        for st in STAGES: load(st); build()
        print("wrote plate, guide and inpaint masks for", ", ".join(STAGES), "in", HERE)
    elif cmd == "check" and len(a) > 1: check(a[1])
    elif cmd == "mark" and len(a) > 1: mark(a[1])
    elif cmd == "lock" and len(a) > 2: lock(a[1], a[2], a[1].rsplit(".", 1)[0] + "-locked.png")
    elif cmd == "generate" and len(a) > 1: generate(*a[1:3])
    elif cmd == "prompts" and len(a) > 1: print("PASS 1 (with {0}plate.png)\n\n{1}\n\n\nPASS 2 (with the marked pass-1 painting)\n\n{2}".format(PRE, *prompts(a[1])))
    else: print(__doc__)
