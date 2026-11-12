"""Download the textures and models the Paxos world is built from.

Everything comes from Poly Haven (polyhaven.com), which publishes its assets under CC0.
Each asset goes into its own folder under world/assets/. Run:  python3 world/fetch_assets.py
"""
import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
UA = {"User-Agent": "diorama-build/0.1"}

# Surface textures, tiled at real-world size. 2k is already finer than one rendered pixel at our scale.
TEXTURES = ["coast_sand_01", "dry_ground_rocks", "aerial_grass_rock", "rocky_terrain_02", "stony_dirt_path", "white_rough_plaster", "white_stucco_02",
            "yellow_plaster", "marble_01", "clay_roof_tiles", "medieval_blocks_05", "brown_planks_09", "hessian_230", "thatch_roof_angled",
            # added for world/build_polis.py: aerial ground, limestone crag, ashlar and rubble masonry, weathered plaster, paving
            "aerial_ground_rock", "dirt_aerial_02", "dirt_aerial_03", "aerial_rocks_02", "marble_cliff_03", "marble_cliff_05", "rocky_terrain_03",
            "aerial_beach_01", "aerial_beach_02", "withered_grass", "sparse_grass", "farm_soil", "dry_mud_field_001", "gravelly_sand", "coast_sand_rocks_02",
            "sandstone_blocks_08", "sandstone_blocks_05", "white_sandstone_blocks_02", "old_stone_wall", "rustic_stone_wall", "stacked_stone_wall",
            "worn_plaster_wall", "plaster_stone_wall_01", "rough_plaster_broken", "white_plaster_rough_01", "beige_wall_001", "clay_plaster",
            "stone_tiles_02", "large_floor_tiles_02", "cobblestone_large_01", "mixed_stone_tiles", "clay_roof_tiles_02"]
TEX_MAPS = ["Diffuse", "nor_gl", "Rough"]
TEX_RES = "2k"
# Scanned and modelled objects, taken as .blend files with their textures.
MODELS = ["tree_small_02", "island_tree_02", "searsia_burchellii", "searsia_lucida", "shrub_01", "shrub_02", "shrub_04", "grass_medium_01",
          "wild_rooibos_bush", "namaqualand_stones_01", "boulder_01", "wicker_basket_01", "wooden_crate_02", "ceramic_vase_01",
          "ceramic_vase_03", "jug_01",
          # added for world/build_polis.py: scanned crags and boulders, olive-like and pine trees, statuary
          "namaqualand_boulder_02", "namaqualand_boulder_03", "namaqualand_boulder_05", "namaqualand_boulder_06", "namaqualand_cliff_02", "rock_face_01",
          "rock_face_02", "coastal_cliff_02", "coast_rocks_05", "rock_moss_set_01", "rock_moss_set_02", "island_tree_01", "island_tree_03",
          "jacaranda_tree", "pine_tree_01", "marble_bust_01", "horse_statue_01"]
MODEL_RES = "1k"
# Skies with no sun in them (the sun is a lamp, set to the drawing's shadows), for world/build_world3d.py.
HDRIS = ["kloofendal_48d_partly_cloudy_puresky", "qwantani_puresky"]


def get_json(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120))


def download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, open(path + ".part", "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    os.replace(path + ".part", path)
    return os.path.getsize(path)


def main():
    total = 0
    for name in TEXTURES:
        files = get_json("https://api.polyhaven.com/files/" + name)
        for m in TEX_MAPS:
            if m not in files:
                print("  (no %s for %s)" % (m, name)); continue
            total += download(files[m][TEX_RES]["jpg"]["url"], os.path.join(ASSETS, name, m + ".jpg"))
        print("texture", name); sys.stdout.flush()
    for name in MODELS:
        entry = get_json("https://api.polyhaven.com/files/" + name)["blend"][MODEL_RES]["blend"]
        total += download(entry["url"], os.path.join(ASSETS, name, name + ".blend"))
        for rel, inc in entry.get("include", {}).items():
            total += download(inc["url"], os.path.join(ASSETS, name, rel))
        print("model", name); sys.stdout.flush()
    for name in HDRIS:
        total += download(get_json("https://api.polyhaven.com/files/" + name)["hdri"]["2k"]["hdr"]["url"], os.path.join(ASSETS, name, name + "_2k.hdr"))
        print("hdri", name); sys.stdout.flush()
    print("downloaded %.0f MB" % (total / 1e6))


if __name__ == "__main__":
    main()
