"""The town inside the walls: sixteen blocks on the drawing's grid of streets. Nine are housing; the rest are given to the
buildings a Hellenistic town had: the agora and its stoas at the crossroads, a council house and a small sanctuary behind the
north stoa, a theatre on the acropolis' slope, a palaistra by the south gate."""
import math, random
from . import core, land, houses, props
from .core import S, inst

R = {-2: (-71.0, -40.5), -1: (-35.5, -4.0), 1: (4.0, 35.5), 2: (40.5, 71.0)}
def blk(i, j): return (R[i][0], R[j][0], R[i][1], R[j][1])
HOUSING = {(-2, -2): (), (-1, -2): ("e",), (2, -2): (), (-2, -1): ("n",), (2, -1): ("n",), (-2, 1): ("s",), (2, 1): ("s",)}

def build():
    g = random.Random(9)
    P, Q = S["places"].get("proposer P"), S["places"].get("proposer Q")
    blocks = dict(HOUSING)
    if core.SIEGE: houses.CORNER[(True, False)] = 104.0                                  # room for the second wall the defenders are building behind the south-east corner
    if not land.HILL: blocks.update({(-2, 2): (), (-1, 2): ("e",), (1, 2): ("w",), (2, 2): ()})    # the besieged town has no hill: its north blocks are houses too
    for (i, j), shops in blocks.items():
        r = blk(i, j); reserve = None
        for pl, side in (((P, "e"), (Q, "w")) if P else ()):
            x, y = pl["at"]
            if r[0] <= x <= r[2] and r[1] <= y <= r[3]:                                   # a proposer's house, its door where the drawing has it
                dx, dy = pl["door"]; hx0, hx1 = (r[2] - 14.5, r[2]) if side == "e" else (r[0], r[0] + 14.5)
                reserve = (hx0, dy - 7.25, hx1, dy + 7.25); houses.peristyle_house(*reserve, g, side)
        houses.block(r, g, shops, reserve)
    if land.HILL:
        houses.terraced((-71.0, 40.5, -40.5, 71.0), g); houses.terraced((-35.5, 40.5, -6.0, 71.0), g)
    import importlib.util
    if importlib.util.find_spec("polis.civic"):
        from . import civic
        civic.build(g)
