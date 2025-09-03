from .laser import laser
from .block import block
from .default import default
from .mirror import mirror
from .prism import prism
from .glass import glass


cells= {
    "laser": laser,
    "block": block,
    "default": default,
    "mirror":mirror,
    "prism":prism,
    "glass":glass
}