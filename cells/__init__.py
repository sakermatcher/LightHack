# Import all cell classes for the LightHack puzzle game
# Each cell type implements different light manipulation mechanics

from .laser import laser      # Light source with configurable RGB output
from .block import xblock     # Solid obstacle that blocks all light
from .default import default  # Base class for all cell types
from .mirror import mirror    # Reflects light at 90-degree angles
from .prism import prism      # Splits white light into RGB or combines RGB into white
from .glass import glass      # Amplifies (light) or attenuates (dark) light intensity
from .final import final      # Goal cell that checks for color matches or filters light

# Dictionary mapping cell type names to their corresponding classes
# Used by the level loader to instantiate the correct cell type from saved data
cells= {
    "default": default,    # Base/empty cell (no special behavior)
    "laser": laser,        # Configurable light source
    "block": xblock,       # Light-blocking obstacle with smart textures
    "mirror": mirror,      # Light reflection with two orientations
    "prism": prism,        # RGB light splitting/combining with flip modes
    "glass": glass,        # Light intensity modification (amplify/attenuate)
    "final": final         # Level goal with exact match or filter modes
}