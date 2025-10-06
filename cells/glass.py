# Import necessary modules for game functionality
import logging
from .texturing import *  # Import texture handling utilities
from .default import default  # Import base cell class
from .indicator import indicatorRender, numbers  # Import indicator rendering for potency display

class glass(default):
    """
    Glass cell class that modifies light intensity as it passes through.
    Features two types: Light glass (amplifies) and Dark glass (attenuates).
    Has configurable potency value that determines the strength of the effect.
    """

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "G", layout=None, data=None):
        """
        Initialize a glass cell with light modification properties.
        
        Args:
            xy: Grid coordinates (x,y) where the glass is placed
            name: Cell identifier/name for the glass
            layout: Grid layout information (unused for glass)
            data: Dictionary with direction, type (0=light/1=dark), and potency settings
        """
        # Set default configuration if none provided
        if data is None:
            data = {"direction": 0, "type":0, "potency": 5}
            
        # Initialize parent class - glass blocks light from top and bottom (directions 0,2)
        # Light can only pass through horizontally (left-right)
        super().__init__(xy= xy, name= name, breaks=[0,2], data= data)
        
        # Store glass properties
        self.type= data["type"]      # 0 = Light glass (amplifies), 1 = Dark glass (attenuates)
        self.potency= data["potency"] # Strength of the amplification/attenuation effect
        
        # Add glass texture layer - switches between light and dark glass appearances
        self.texture.newLayer(layer=3, name="lens", textures=["glass/light.png", "glass/dark.png"], state={"index": self.type, "direction": data["direction"]})
        
        # Add potency indicator background (Down Right corner)
        self.texture.newLayer(layer=4, name="indicator", textures=["indicators/DR.png"], state={"index": 0, "direction": 0})
        
        # Add potency value number display
        self.texture.newLayer(layer=5, name= "number", textures=numbers, renderer=indicatorRender, state={"corner": "DR", "color": (255,255,255), "number": self.potency})

    def changeDirection(self, direction):
        """
        Update the glass rotation direction with constraint.
        Glass is symmetric, so direction 2 is mapped to 0 for simplicity.
        
        Args:
            direction: New rotation direction (0-3), with 2 automatically converted to 0
        """
        # Map direction 2 to 0 since glass is rotationally symmetric
        if direction == 2:
            direction = 0
        
        # Update glass texture rotation
        self.texture.update("lens", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        """
        Process light passing through the glass with intensity modification.
        Light glass amplifies brightness, dark glass reduces it.
        
        Args:
            From: Direction light is coming from (0=up, 1=right, 2=down, 3=left)
            color: RGB color tuple of the incoming light
            
        Returns:
            Tuple of (modified_light_dict, light_blocked_bool)
        """
        # Set default color if none provided
        if color is None:
            color= (0,0,0)
        
        # Store the incoming light
        self.inputs[From]= color

        # Check if light hits a blocking wall (top/bottom for this glass orientation)
        if self.checkBreak(From):
            # Light is blocked - update visual beam state but don't pass through
            match From:
                    case 0:  # Light from above - blocked
                        self.changeBeamStates(colorA= color, vertical=True)
                    case 1:  # Light from right - passes through (shouldn't break)
                        self.changeBeamStates(colorA=color, vertical=False)
                    case 2:  # Light from below - blocked
                        self.changeBeamStates(colorB=color, vertical=True)
                    case 3:  # Light from left - passes through (shouldn't break)
                        self.changeBeamStates(colorB=color, vertical=False)
            return {}, True  # Light blocked, no output

        # Light passes through - apply glass effect based on type
        if self.type == 1:  # Dark glass - attenuates/reduces light intensity
            # Calculate attenuated light for visual display (combines input with opposite direction)
            colorA= tuple(max(0, color[i] + self.inputs[self.dirFrom[From]][i] - self.potency * int(bool(self.inputs[self.dirFrom[From]][i]))) for i in range(3))
            colorB= tuple(max(0, self.inputs[self.dirFrom[From]][i] + color[i] - self.potency * int(bool(color[i]))) for i in range(3))
            
            # Update beam visual states for both directions
            self.changeBeamStates(beamDirs=[From], color= colorA)
            self.changeBeamStates(beamDirs=[self.dirFrom[From]], color= colorB)
            
            # Output attenuated light (subtract potency, minimum 0)
            output_color = tuple(max(0, color[i] - self.potency * int(bool(color[i]))) for i in range(3))
            return {self.dirFrom[From]: output_color}, False
            
        else:  # Light glass - amplifies/increases light intensity
            # Calculate amplified light for visual display (combines input with opposite direction)
            colorA= tuple(min(10, color[i] + self.inputs[self.dirFrom[From]][i] + self.potency * int(bool(self.inputs[self.dirFrom[From]][i]))) for i in range(3))
            colorB= tuple(min(10, self.inputs[self.dirFrom[From]][i] + color[i] + self.potency * int(bool(color[i]))) for i in range(3))
            
            # Update beam visual states for both directions
            self.changeBeamStates(beamDirs=[From], color= colorA)
            self.changeBeamStates(beamDirs=[self.dirFrom[From]], color= colorB)
            
            # Output amplified light (add potency, maximum 10)
            output_color = tuple(min(10, color[i] + self.potency * int(bool(color[i]))) for i in range(3))
            return {self.dirFrom[From]: output_color}, False
    
    def editProperty(self, index, changing):
        """
        Edit glass properties in the level editor.
        
        Args:
            index: Property value to set (0=toggle type, other values=set potency)
            changing: Property type selector (unused for glass)
            
        Returns:
            True if property was changed, False otherwise
        """
        if index is not None:
            if index == 0:
                # Toggle between light glass (0) and dark glass (1)
                self.type = int(not bool(self.type))
                # Update texture to show light or dark glass appearance
                self.texture.update("lens", index=self.type)
            else:
                # Set potency value (strength of light modification)
                self.potency = index
                # Update potency number display
                self.texture.update("number", number=self.potency)
            return True
        else:
            return False

    def getData(self, pocket=False):
        """
        Serialize glass data for saving/loading levels.
        
        Args:
            pocket: If True, returns template data for level editor palette
                   If False, returns current glass state for level saving
                   
        Returns:
            Dictionary containing glass type and configuration data
        """
        # Get base cell data from parent class
        data= super().getData()
        
        if pocket:
            # Return template data for level editor (preserves type and potency)
            data["data"]= {
                "direction": 0,           # Default rotation
                "type": self.type,        # Current glass type (light/dark)
                "potency": self.potency   # Current potency setting
            }
            return data
        
        # Return current glass state data for level saving
        data["data"]= {
            "direction": self.direction,  # Current rotation direction
            "type": self.type,            # Current glass type (0=light, 1=dark)
            "potency": self.potency       # Current potency value
        }
        return data