"""Build the Paxos city as a Hellenistic town in Blender, in exactly the frame of the page's southeast picture; or, given the
siege scene (world/build3d/siege.json), the same kind of town shut up at night inside a Hellenistic siege (see polis/siege.py).

Fixed by the page (and read from the scene file city_mockup.py dumps): the camera, every place and door, and the plan of every
road a messenger walks. The heights of those roads are this build's own: the land rises gently from the shore to the acropolis,
and the build writes the height of every route sample to <out>-heights.json so the page can follow.

Everything else is modelled afresh on Hellenistic precedent (Priene above all): courtyard houses in a grid of blocks, an agora
framed by stoas, a council house, a theatre cut into the acropolis' slope, a palaistra, ashlar walls with roofed towers, a
sanctuary on the summit, farms, vineyards, a potters' quarter and a harbour outside the walls.

Run:  blender -b --factory-startup -P world/build_polis.py -- --scene world/build3d/city.json --out world/build3d/polis.png
          [--width 2400] [--samples 96] [--only land,walls,...] [--skip plants] [--border x0,y0,x1,y1] [--save] [--no-render]
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
T0 = time.time()
def lap(msg): print("[%6.1fs] %s" % (time.time() - T0, msg)); sys.stdout.flush()

from polis import core, mats, land
from polis.core import stage, flag
lap("start")
land.init(); lap("land shaped")
for name in (("walls", "town", "siege", "plants") if core.SIEGE else ("walls", "town", "acropolis", "country", "plants")):
    if not stage(name): continue
    mod = __import__("polis." + name, fromlist=["build"]); mod.build(); lap(name + " built")
core.flush(); core.Scatter.flush(); land.finish(); lap("terrain made")
from polis import render
render.setup(); render.check(); lap("checked")
render.render(); lap("done")
