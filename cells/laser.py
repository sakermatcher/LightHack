# Import necessary modules for game functionality
import logging
from .texturing import *  # Import texture handling utilities
from .default import default  # Import base cell class
from .indicator import indicatorRender, numbers  # Import indicator rendering for RGB displays

class laser(default):
    """
    Laser cell class that generates colored light based on user-configurable RGB values.
    Features editable RGB intensity settings and visual indicators showing current color values.
    """
    
    def renderLaser(self, layer:dict):
        """
        Custom renderer for the laser light beam effect.
        Creates a colored light effect based on the laser's current RGB settings.
        
        Args:
            layer: Dictionary containing textures, state, and renderer information
                   state contains: color (RGB tuple), direction (rotation)
                   
        Returns:
            Rendered surface with colored laser light effect, or transparent surface if off
        """
        # Extract rendering state information
        state= layer["state"]
        # Optional debug logging (commented out)
        # logging.log(50, f"Laser render called with state: {layer['state']}")

        # Only render light if laser has color (not black/off)
        if state["color"] != (0,0,0):
            # Convert game color scale (0-10) to display scale (0-255) for rendering
            # Formula: (value/1.428571 + 3*bool(value)) * 25.5
            # This ensures 0→0 but 1→76.5, scaling up to 10→255 for proper brightness
            color= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in state["color"])
            
            # Apply color tint to the laser light texture
            final = multiply(layer["textures"][0], color)
            
            # Rotate the light effect based on laser direction (0°, 90°, 180°, 270°)
            final = transform.rotate(final, [0,90,180,270][state["direction"]])
            return final
            
        # Return transparent surface when laser is off (color = black)
        return surface.Surface((40,40), SRCALPHA)

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "L", layout=None, data=None):
        """
        Initialize a laser cell with RGB color controls and visual indicators.
        
        Args:
            xy: Grid coordinates (x,y) where the laser is placed
            name: Cell identifier/name for the laser
            layout: Grid layout information (unused for lasers)
            data: Dictionary with color (RGB tuple) and direction settings
        """
        # Set default configuration if none provided
        if data is None:
            data = {"color": (0,0,0), "direction": 0}
        
        # Initialize parent class - laser blocks light from sides and back (directions 1,2,3)
        # Only emits light in the forward direction (direction 0 relative to rotation)
        super().__init__(xy= xy, name= name, breaks=[1,2,3], data= data)
        
        # Add main laser body texture layer
        self.texture.newLayer(3, "Laser", ["laser/main.png"], state={"index": 0, "direction": data["direction"]})
        
        # Add laser light effect layer with custom renderer
        self.texture.newLayer(4, "Light", ["laser/light.png"], renderer=self.renderLaser, state={"color": data["color"], "direction": data["direction"]})
        
        # Add indicator screen backgrounds for RGB value display
        self.texture.newLayer(5, "screens", ["indicators/UL.png", "indicators/UR.png", "indicators/DL.png"], state={"index": -1})
        
        # Store laser color configuration
        self.color = tuple(data["color"])
        
        # Add RGB value indicators with colored numbers
        # Red channel indicator (Upper Left corner)
        self.texture.newLayer(6, "colorR", numbers, state={"corner": "UL", "color": (255,50,50), "number": self.color[0]}, renderer=indicatorRender)
        # Green channel indicator (Upper Right corner)
        self.texture.newLayer(7, "colorG", numbers, state={"corner": "UR", "color": (50,255,50), "number": self.color[1]}, renderer=indicatorRender)
        # Blue channel indicator (Down Left corner)
        self.texture.newLayer(8, "colorB", numbers, state={"corner": "DL", "color": (50,180,255), "number": self.color[2]}, renderer=indicatorRender)
        # Update light effect to match initial color and direction
        self.texture.update("Light", color=self.color, direction=self.direction)

    def changeDirection(self, direction):
        """
        Update the laser's rotation direction and rotate all visual elements accordingly.
        
        Args:
            direction: New rotation direction (0=0°, 1=90°, 2=180°, 3=270°)
        """
        # Update laser body and light effect textures to match new direction
        self.texture.update("Laser", direction=direction)
        self.texture.update("Light", direction=direction)
        return super().changeDirection(direction)

    def editProperty(self, index:int, changing:int):
        """
        Edit the RGB color intensity for a specific channel of the laser.
        Used by the level editor to adjust laser output colors.
        
        Args:
            index: Intensity value for the channel (0=max/10, None=off/0, 1-9=that value)
            changing: Which RGB channel to modify (R=0, G=1, B=2)
            
        Returns:
            True indicating the property edit was successful
        """
        # Handle intensity value mapping
        if index is not None:
            if index == 0:
                index = 10  # Special case: 0 maps to maximum intensity (10)
            # Update the specified color channel
            current = list(self.color)
            current[changing] = index
            self.color = tuple(current)
        else:
            # Set channel to off (0 intensity)
            current = list(self.color)
            current[changing] = 0
            self.color = tuple(current)
        
        # Update all visual elements to reflect the new color
        self.texture.update("Light", color=self.color)  # Update light effect color
        self.texture.update("colorR", number=self.color[0])  # Update red indicator
        self.texture.update("colorG", number=self.color[1])  # Update green indicator
        self.texture.update("colorB", number=self.color[2])  # Update blue indicator
        return True

    def changeLight(self, From=None, color=None):
        """
        Handle light interactions with the laser cell.
        
        Args:
            From: Direction of incoming light (if any)
            color: Color of incoming light (if any)
            
        Returns:
            Tuple of (light_output_dict, light_blocked_bool)
        """
        if From is not None:
            # If light is coming from outside, handle it normally (will be blocked by breaks)
            return super().changeLight(From, color)
        else:
            # If no incoming light specified, this is the laser generating its own light
            # Emit laser's configured color in its facing direction
            return {self.direction: self.color}, False

    def getData(self, pocket=False):
        """
        Serialize laser data for saving/loading levels.
        
        Args:
            pocket: If True, returns template data for level editor palette
                   If False, returns current laser state for level saving
                   
        Returns:
            Dictionary containing laser type and configuration data
        """
        # Get base cell data from parent class
        data= super().getData()
        
        if pocket:
            # Return template data for level editor (includes color for configuration)
            data["data"]= {
                "direction": 0,           # Default rotation
                "color": self.color       # Current color (preserved in template)
            }
            return data
            
        # Return current laser state data for level saving
        data["data"]= {
            "direction": self.direction,  # Current rotation direction
            "color": self.color           # Current RGB color settings
        }
        return data