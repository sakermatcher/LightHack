# Import necessary modules for game functionality
from .texturing import *  # Import texture handling utilities
from .default import default  # Import base cell class

class myName(default):
    """
    Template/sketch class for creating new cell types in the LightHack game.
    This serves as a boilerplate that can be copied and modified to implement
    new game mechanics and cell behaviors. Contains all the basic structure
    and methods that most cell types need.
    
    NOTE: This is a template class - rename 'myName' to your actual cell type name!
    """

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "Laser", layout=None, data=None):
        """
        Initialize a new cell type with basic properties and texture layers.
        
        TEMPLATE INSTRUCTIONS:
        - Change the class name from 'myName' to your actual cell type
        - Update the default name parameter to match your cell type
        - Modify the breaks array to control which directions block light
        - Add appropriate texture layers for your cell's visual appearance
        
        Args:
            xy: Grid coordinates (x,y) where the cell is placed
            name: Cell identifier/name for this cell type
            layout: Grid layout information (if needed for neighbor detection)
            data: Configuration data dictionary (direction, colors, etc.)
        """
        # Set default configuration if none provided
        if data is None:
            data = {"direction": 0}
            
        # Initialize parent class - modify breaks array to control light blocking:
        # breaks=[0,1,2,3] blocks all directions (like a wall)
        # breaks=[] allows light through all directions (like glass)
        # breaks=[1,2,3] blocks sides/back but allows forward (like laser)
        super().__init__(xy= xy, name= name, breaks=[0,1,2,3], data= data)
        
        # Add texture layer for this cell type
        # TEMPLATE: Replace "textureLocation" with actual texture file path
        # Example: "laser/main.png", "mirror/mirror.png", etc.
        self.texture.newLayer(layer=3, name="layerName", textures=["textureLocation"], state={"index": 0, "direction": data["direction"]})

    def changeDirection(self, direction):
        """
        Update the cell's rotation direction and rotate visual elements.
        
        TEMPLATE INSTRUCTIONS:
        - Uncomment and modify the texture update line to match your layer name
        - Add any additional rotation logic specific to your cell type
        
        Args:
            direction: New rotation direction (0=0°, 1=90°, 2=180°, 3=270°)
        """
        # TEMPLATE: Uncomment and update layer name to match your texture layer
        # Example: self.texture.update("laser", direction=direction)
        # self.texture.update("layerName", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        """
        Process light interactions with this cell type.
        
        TEMPLATE INSTRUCTIONS:
        - Modify this method to implement your cell's light behavior
        - Examples: reflection (mirror), color splitting (prism), amplification (glass)
        - The current implementation just passes light to the opposite direction
        
        Args:
            From: Direction light is coming from (0=up, 1=right, 2=down, 3=left)
            color: RGB color tuple of the incoming light
            
        Returns:
            Tuple of (output_light_dict, light_blocked_bool)
        """
        if From is not None:
            # Handle incoming light from a specific direction
            # TEMPLATE: Add your custom light processing logic here
            return super().changeLight(From, color)
        else:
            # Handle cell generating its own light (like a laser)
            # Current implementation outputs light in opposite direction to cell's facing
            # Direction mapping: [2,3,0,1] converts facing direction to opposite
            return {[2,3,0,1][self.direction]:color}, False

    def getData(self, pocket= False):
        """
        Serialize cell data for saving/loading levels.
        
        TEMPLATE INSTRUCTIONS:
        - Add any additional properties your cell type needs to save
        - Examples: color settings, potency values, flip states, etc.
        
        Args:
            pocket: If True, returns template data for level editor palette
                   If False, returns current cell state for level saving
                   
        Returns:
            Dictionary containing cell type and configuration data
        """
        # Get base cell data from parent class
        data= super().getData()
        
        if pocket:
            # Return template data for level editor (default values)
            data["data"]= {
                "direction": 0  # Default rotation
                # TEMPLATE: Add other default properties here
                # "color": (0,0,0), "potency": 5, etc.
            }
            return data
            
        # Return current cell state data for level saving
        data["data"]= {
            "direction": self.direction  # Current rotation direction
            # TEMPLATE: Add other current state properties here
            # "color": self.color, "potency": self.potency, etc.
        }
        return data