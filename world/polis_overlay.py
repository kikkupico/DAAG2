"""Mark this build's places, doors and route samples on its render, to check by eye that every node sits where the page expects.
Run:  python3 world/polis_overlay.py world/build3d/polis.png [scene.json]   (reads polis-heights.json beside it, writes polis-overlay.png)"""
import json, math, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
png = sys.argv[1]; base = png.rsplit(".", 1)[0]
S = json.load(open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "build3d", "city.json"))); H = json.load(open(base + "-heights.json")); F = S["frame"]
im = Image.open(png).convert("RGB"); k = im.width / F["aw"]
def px(x, y, z=0.0):
    return (F["aw"] / 2 + F["k"] * (x + y) / math.sqrt(2)) * k, (F["ah"] / 2 + F["k"] * (math.sin(F["elev"]) * (x - y) / math.sqrt(2) - math.cos(F["elev"]) * z)) * k
d = ImageDraw.Draw(im)
for key, z in H["heights"].items():
    x, y = map(float, key.split(",")); u, v = px(x, y, z); d.ellipse((u - 2 * k, v - 2 * k, u + 2 * k, v + 2 * k), fill=(255, 255, 255), outline=(20, 60, 160))
for x, y, *_ in H["hidden"]:
    u, v = px(x, y, H["heights"]["%g,%g" % (x, y)]); d.ellipse((u - 2 * k, v - 2 * k, u + 2 * k, v + 2 * k), fill=(240, 80, 60))
for name, p in H["places"].items():
    u, v = px(*p["door"], p["zdoor"]); d.ellipse((u - 5 * k, v - 5 * k, u + 5 * k, v + 5 * k), outline=(0, 0, 0), width=max(1, int(2 * k)), fill=(255, 220, 60)); d.text((u + 7 * k, v - 6 * k), name, fill=(0, 0, 0), stroke_width=2, stroke_fill=(255, 255, 255))
im.save(base + "-overlay.png"); print("wrote", base + "-overlay.png")
