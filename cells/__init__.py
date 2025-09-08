from .laser import laser
from .block import xblock
from .default import default
from .mirror import mirror
from .prism import prism
from .glass import glass
from .final import final

cells= {
    "default": default,
    "laser": laser,
    "block": xblock,
    "mirror":mirror,
    "prism":prism,
    "glass":glass,
    "final":final
}