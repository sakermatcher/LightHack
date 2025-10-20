# Import necessary modules for game functionality
import logging
from .texturing import *  # Import texture handling utilities
from .default import default  # Import base cell class

class xblock(default):
    """
    Block cell class that completely blocks light from passing through.
    Automatically adapts its visual appearance based on surrounding blocks to create 
    connected block structures with appropriate edge/corner graphics.
    """
    
    def __init__(self, xy: tuple[int, int]|None = None, name: str = "X", layout=None, data=None):
        """
        Initialize a block cell that stops all light and adapts appearance to neighbors.
        
        Args:
            xy: Grid coordinates (x,y) where the block is placed
            name: Cell identifier/name for the block (default "X")
            layout: 2D array representing the level layout for neighbor detection
            data: Configuration data (inherited from parent class)
        """
        # Initialize texture manager
        self.texture= texturing()
        
        # Initialize parent class with all directions as breaking walls (blocks all light)
        super().__init__(xy= xy, name= name, breaks=[0,1,2,3], data= data)
        
        # Analyze surrounding cells to determine appropriate block texture
        sorroundings= []
        
        # Check if we have position and layout information for smart texturing
        if layout is not None and xy is not None:
            # Check all four adjacent directions for other blocks
            for i, (dx, dy) in enumerate([(0, -1), (1, 0), (0, 1), (-1, 0)]): # North, East, South, West
                # Calculate neighbor position
                neighbor_x = xy[0] + dx
                neighbor_y = xy[1] + dy
                
                # Check if neighbor position is within layout bounds
                if 0 <= neighbor_y < len(layout) and 0 <= neighbor_x < len(layout[0]):
                    # If neighbor is also a block, add its direction to surroundings
                    if layout[neighbor_y][neighbor_x] == "X":
                        sorroundings.append(i)
            
            # Select appropriate texture based on number of surrounding blocks
            match len(sorroundings):
                case 0:
                    # Isolated block - use standalone texture
                    self.texture.newLayer(0, "base", ["disabledCells/0.png"])
                    
                case 1:
                    # Block with one neighbor - use single connection texture
                    self.texture.newLayer(0, "base", ["disabledCells/1.png"])
                    # Calculate rotation: map neighbor direction to texture orientation
                    dir= [0,3,2,1][sorroundings[0]]  # N→0, E→3, S→2, W→1
                    self.texture.update("base", direction=dir)
                    
                case 2:
                    # Block with two neighbors - check if they're opposite or adjacent
                    if sum(sorroundings) % 2 == 0:
                        # Opposite neighbors (0+2=2 or 1+3=4) - use straight line texture
                        self.texture.newLayer(0, "base", ["disabledCells/2I.png"])
                        # Orient the line: vertical (N-S) or horizontal (E-W)
                        if sorroundings[0] == 1:  # East-West orientation
                            self.texture.update("base", direction=1)
                        else:  # North-South orientation  
                            self.texture.update("base", direction=0)
                    else:
                        # Adjacent neighbors - use L-shaped corner texture
                        self.texture.newLayer(0, "base", ["disabledCells/2L.png"])
                        # Orient the corner based on which two directions are connected
                        match sorroundings:
                            case [0, 1]:  # North + East = NE corner
                                self.texture.update("base", direction=0)
                            case [1, 2]:  # East + South = SE corner
                                self.texture.update("base", direction=3)
                            case [2, 3]:  # South + West = SW corner
                                self.texture.update("base", direction=2)
                            case [0, 3]:  # North + West = NW corner
                                self.texture.update("base", direction=1)
                                
                case 3:
                    # Block with three neighbors - use T-junction texture
                    self.texture.newLayer(0, "base", ["disabledCells/3.png"])
                    # Orient the T-junction based on which three directions are connected
                    match sorroundings:
                        case [0, 1, 3]:  # North + East + West (T pointing down)
                            self.texture.update("base", direction=0)
                        case [0, 2, 3]:  # North + South + West (T pointing right)
                            self.texture.update("base", direction=1)
                        case [1, 2, 3]:  # East + South + West (T pointing up)
                            self.texture.update("base", direction=2)
                        case [0, 1, 2]:  # North + East + South (T pointing left)
                            self.texture.update("base", direction=3)
                            
                case 4:
                    # Block surrounded by other blocks - use cross/junction texture
                    self.texture.newLayer(0, "base", ["disabledCells/4.png"])

        else:
            # No layout information available - use default isolated block texture
            self.texture.newLayer(0, "base", ["disabledCells/0.png"])

        # Optional debug logging (commented out)
        # logging.log(50, f"Block cell created at {self.xy}, neighbors: {sorroundings}")