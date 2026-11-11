"""Turn the world renders into the page's stage data.

Each result gets its own picture, cut from its group's full-size overview to just the places in it, so buildings come
out larger. Each also gets a small close-up of the place you are inside, cut from that place's close view.
Run:  python3 make_stage.py <world/render folder> <out .js>
"""
import base64, io, json, os, sys
from PIL import Image

render, out = sys.argv[1], sys.argv[2]
world = json.load(open(os.path.join(render, "world.json")))
SPECS = {  # result: (overview, places to frame, places that get a close-up)
    "snapshot": ("overview", ["fishery", "granary", "winery", "potter"], ["fishery"]),
    "flp": ("legislators", ["legislator A", "legislator B", "legislator C", "temple"], ["legislator A"]),
    "quorum": ("scholars", ["town library", "hill school", "cape library"], ["cape library", "town library"]),
    "liars": ("soldiers", ["commander's camp", "camp A", "camp B", "camp C", "enemy city"], ["camp A"]),
    "clocks": ("overview", ["fishery", "granary", "winery"], ["fishery"]),
    "commit": ("overview", ["fishery", "granary", "agora"], ["fishery"]),
    "cops": ("scholars", ["town library", "cape library"], ["town library"]),
    "suspect": ("legislators", ["legislator A", "legislator B", "legislator C", "temple"], ["legislator A"]),
    "benor": ("legislators", ["legislator A", "legislator B", "legislator C", "temple"], ["legislator A"]),
    "paxos": ("legislators", ["legislator A", "legislator B", "legislator C", "proposer P", "proposer Q", "temple"], ["proposer P", "proposer Q", "legislator B"]),
    "vr": ("legislators", ["legislator A", "legislator B", "legislator C", "temple"], ["legislator B", "legislator C"]),
    "pbft": ("soldiers", ["commander's camp", "camp A", "camp B", "camp C", "enemy city"], ["camp A"]),
    "linear": ("scholars", ["town library", "hill school"], ["town library"]),
    "cap": ("scholars", ["town library", "cape library"], ["town library"]),
    "merge": ("scholars", ["town library", "hill school", "cape library"], ["town library"]),
    "bayou": ("scholars", ["town library", "hill school", "cape library"], ["town library"]),
}
CLOSE = {"potter": "potter", "commander's camp": "camp"}       # close views whose name is not the place's name with dashes
SHIFT = {"camp A": (.07, .1), "camp B": (.07, .1), "camp C": (.07, .1), "commander's camp": (.07, .1)}   # tents stand beside the pavilion the centre marks
def b64(im, q):
    buf = io.BytesIO(); im.convert("RGB").save(buf, "JPEG", quality=q, optimize=True); return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), len(buf.getvalue())

parts = []; pictures = {}; closeups = {}; seen = {}   # each distinct picture and close-up is stored once
for key, (view, frame, close) in SPECS.items():
    info = world[view]; src = Image.open(os.path.join(render, view + ".png")); W, H = src.size
    pts = [info["places"][p]["centre"] for p in frame]
    x0, x1 = min(p[0] for p in pts) * W, max(p[0] for p in pts) * W; y0, y1 = min(p[1] for p in pts) * H, max(p[1] for p in pts) * H
    x0 -= .08 * W; x1 += .08 * W; y0 -= .14 * H; y1 += .14 * H          # room round the outermost places for their labels
    cw = max(x1 - x0, .42 * W, 2.0 * (y1 - y0)); ch = cw / 2.0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cw, ch = min(cw, W), min(ch, H); left = min(max(0, cx - cw / 2), W - cw); top = min(max(0, cy - ch / 2), H - ch)
    sea = max(p[1] for p in pts) * H + .07 * H                         # keep only a strip of sea below the lowest place: deep water reads as a dark vignette
    need = sea - (min(p[1] for p in pts) * H - .14 * H)
    if need < ch: ch = max(need, cw / 2.6)                               # a wide crop may be shorter (up to 2.6:1) rather than show deep sea
    top = min(max(0, cy - ch / 2), H - ch)
    if top + ch > sea: top = max(0, sea - ch)
    crop = src.crop((round(left), round(top), round(left + cw), round(top + ch))); crop = crop.resize((1800, round(1800 * crop.height / crop.width)), Image.LANCZOS) if crop.width > 1800 else crop
    m = lambda p: [round((p[0] * W - left) / cw, 4), round((p[1] * H - top) / ch, 4)]
    data = {"w": crop.width, "h": crop.height, "places": {k: m(v["centre"]) for k, v in info["places"].items()},
            "roads": {n: [m(p) for p in info["roads"][i]] for i, n in enumerate(info["road_names"])}, "label": {"potter": "the amphora maker"}, "inset": {}}
    sig = (view, tuple(sorted(frame)))
    if sig not in seen:
        seen[sig] = "p%d" % len(seen)
        crop.convert("RGB").save(os.path.join(render, seen[sig] + ".jpg"), "JPEG", quality=70, optimize=True)
        pictures[seen[sig]] = "../world/render/%s.jpg" % seen[sig]
    data["img"] = seen[sig]; total = os.path.getsize(os.path.join(render, seen[sig] + ".jpg"))
    for place in close:
        if place in closeups: data["inset"][place] = 1; continue
        cv = CLOSE.get(place, place.replace(" ", "-").replace("'", ""))
        if cv not in world: print("  no close view for", place); continue
        cim = Image.open(os.path.join(render, cv + ".png")); cW, cH = cim.size; c = world[cv]["places"].get(place, {"centre": [.5, .5]})["centre"]; c = (c[0] + SHIFT.get(place, (0, 0))[0], c[1] + SHIFT.get(place, (0, 0))[1])
        iw, ih = .46 * cW, .46 * cH; il = min(max(0, c[0] * cW - iw / 2), cW - iw); it = min(max(0, c[1] * cH - ih * .55), cH - ih)
        ins = cim.crop((round(il), round(it), round(il + iw), round(it + ih))).resize((480, 320), Image.LANCZOS)
        closeups[place], size = b64(ins, 72); data["inset"][place] = 1; total += size
    parts.append(json.dumps(key) + ": " + json.dumps(data))
    print(key, "from", view, "%.0f%% of its width," % (100 * cw / W), crop.width, "px,", total // 1024, "KB with", len(data["inset"]), "close-ups")
open(out, "w").write("\n// ---------- the island pictures, rendered from world/build_world.py ----------\nconst PICTURES = " + json.dumps(pictures) + ";\nconst CLOSEUPS = " + json.dumps(closeups) + ";\nconst STAGES = {" + ",\n".join(parts) + "};\n")
print(len(pictures), "pictures and", len(closeups), "close-ups stored once")
