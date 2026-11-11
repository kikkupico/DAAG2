"""Write the site names onto the blockout pictures. Run after blockout_island.py:  python3 world/label_plan.py world/plan"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

folder = sys.argv[1]
plan = json.load(open(os.path.join(folder, "plan.json")))
try: font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
except OSError: font = ImageFont.load_default()
SHOW = {"merchants": {"merchants", "common"}, "legislators": {"legislators", "common"}, "scholars": {"scholars", "common"}, "soldiers": {"soldiers", "enemy"}}
for view, rec in plan["views"].items():
    im = Image.open(os.path.join(folder, view + ".png")).convert("RGB"); d = ImageDraw.Draw(im); W, H = im.size
    for name, s in rec["sites"].items():
        if view in SHOW and s["group"] not in SHOW[view]: continue
        x, y = s["at"][0] * W, s["at"][1] * H
        if not (0 <= x <= W and 0 <= y <= H): continue
        rgb = tuple(int(255 * min(1, c * 1.5 + .25)) for c in plan["groups"][s["group"]])
        tw = d.textlength(name, font=font); d.text((x - tw / 2, y - 44), name, font=font, fill=rgb, stroke_width=4, stroke_fill=(10, 20, 26))
    im.save(os.path.join(folder, view + ".jpg"), quality=86)
    print("labelled", view)
