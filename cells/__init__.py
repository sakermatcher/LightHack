from .laser import laser
from .block import block
from .default import default
from .mirror import mirror
from .prism import prism
from .glass import glass


cells= {
    "default": default,
    "laser": laser,
    "block": block,
    "mirror":mirror,
    "prism":prism,
    "glass":glass
}