# Import necessary modules for game functionality
import logging
from .texturing import *  # Import texture handling utilities
from .default import default  # Import base cell class

class prism(default):
    """
    Prism cell class that can split white light into RGB components or combine RGB into white.
    Supports two orientations (normal and flipped) that affect the color splitting/combining behavior.
    """

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "P", layout=None, data=None):
        """
        Initialize a prism cell with position, textures, and configuration.
        
        Args:
            xy: Grid coordinates (x,y) where the prism is placed
            name: Cell identifier/name for the prism
            layout: Grid layout information (if needed for context)
            data: Dictionary with relevant data (direction, flipped state)
        """
        # Set default configuration if none provided
        if data is None:
            data = {"direction": 0, "flipped": False}
        
        # Initialize parent class with no breaking walls (light passes through)
        super().__init__(xy= xy, name= name, breaks=[], data= data)
        
        # Add prism texture layer with normal and flipped variants
        self.texture.newLayer(layer=3, name="prism", textures=["prism/normal.png", "prism/flipped.png"], state={"index": 0, "direction": data["direction"]})
        
        # Track previous output to detect state changes and prevent infinite loops
        self.pastOutput= (0,0,0)
        
        # Ensure flipped property exists in data
        if "flipped" not in data:
            data["flipped"]= False
        
        # Set initial flip state and apply flip if needed
        if data["flipped"] == True:
            self.flipped= False
            self.flip()  # This will set flipped to True and update texture
        else:
            self.flipped= False

    def changeDirection(self, direction):
        """
        Update the prism's rotation direction and rotate the texture accordingly.
        
        Args:
            direction: New rotation direction (0=0°, 1=90°, 2=180°, 3=270°)
        """
        # Update prism texture rotation to match new direction
        self.texture.update("prism", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        """
        Process incoming light through the prism - either split white light into RGB or combine RGB into white.
        The prism behavior depends on its orientation (normal vs flipped) and the light entry direction.
        
        Args:
            From: Direction the light is coming from (0=up, 1=right, 2=down, 3=left)
            color: RGB color tuple of the incoming light
            
        Returns:
            Tuple of (output_light_dict, light_blocked_bool)
        """
        # Set default color if none provided
        if color is None:
            color= (0,0,0)
        
        # Store the incoming light in the appropriate input slot
        self.inputs[From]= color
        
        # Process light based on prism orientation (normal vs flipped)
        if not self.flipped:
            # Normal orientation: calculate combined light colors
            # For each RGB channel, combine light from opposite directions (3-i maps R→B, G→G, B→R)
            colors= tuple(min(10, self.inputs[self.convDir(3 - i)][i] + self.inputs[self.convDir(0)][i] ) for i in range(3))
            
            # Create individual color beams for each output direction
            colorRside= (colors[0], self.inputs[self.convDir(3)][1], self.inputs[self.convDir(3)][2])  # Red output
            colorGside= (self.inputs[self.convDir(2)][0], colors[1],self.inputs[self.convDir(2)][2])   # Green output  
            colorBside= (self.inputs[self.convDir(1)][0],self.inputs[self.convDir(1)][1], colors[2])   # Blue output
            
            # Update beam visual states for all output directions
            self.changeBeamStates(beamDirs=[self.convDir(3)], color= colorRside)
            self.changeBeamStates(beamDirs=[self.convDir(2)], color= colorGside)
            self.changeBeamStates(beamDirs=[self.convDir(1)], color= colorBside)
            self.changeBeamStates(beamDirs=[self.convDir(0)], color= colors)

        else:
            # Flipped orientation: different mapping for RGB separation/combination
            # For each RGB channel, combine light from sequential directions (i+1 maps R→G, G→B, B→R)
            colors= tuple(min(10, self.inputs[self.convDir(i + 1)][i] + self.inputs[self.convDir(0)][i] ) for i in range(3))
            
            # Create individual color beams for flipped output directions
            colorRside= (colors[0], self.inputs[self.convDir(1)][1], self.inputs[self.convDir(1)][2])  # Red output
            colorGside= (self.inputs[self.convDir(2)][0], colors[1],self.inputs[self.convDir(2)][2])   # Green output
            colorBside= (self.inputs[self.convDir(3)][0],self.inputs[self.convDir(3)][1], colors[2])   # Blue output
            
            # Update beam visual states for all flipped output directions
            self.changeBeamStates(beamDirs=[self.convDir(1)], color= colorRside)
            self.changeBeamStates(beamDirs=[self.convDir(2)], color= colorGside)
            self.changeBeamStates(beamDirs=[self.convDir(3)], color= colorBside)
            self.changeBeamStates(beamDirs=[self.convDir(0)], color= colors)

        # Determine output behavior based on light entry direction
        if From == self.direction: # Light entering from the main direction - SPLIT white into RGB
            if not self.flipped:
                # Normal orientation: output pure RGB beams to directions 3, 2, 1
                return {self.convDir(3):(self.inputs[self.convDir(0)][0], 0, 0), self.convDir(2):(0, self.inputs[self.convDir(0)][1], 0), self.convDir(1):(0, 0, self.inputs[self.convDir(0)][2])}, False
            else:
                # Flipped orientation: output pure RGB beams to directions 1, 2, 3
                return {self.convDir(1):(self.inputs[self.convDir(0)][0], 0, 0), self.convDir(2):(0, self.inputs[self.convDir(0)][1], 0), self.convDir(3):(0, 0, self.inputs[self.convDir(0)][2])}, False
        
        else: # Light entering from side directions - COMBINE RGB into white
            if not self.flipped:
                # Normal orientation: extract RGB channels from specific input directions
                outColor=tuple(self.inputs[self.convDir(3 - i)][i] for i in range(3))
                
                # Prevent infinite loops by checking if output has changed
                if outColor == self.pastOutput:
                    self.pastOutput= colors
                    return {}, True  # Block propagation to prevent loops
                else:
                    self.pastOutput= colors
                    return {self.convDir(0):outColor}, False  # Output combined white light
            else:
                # Flipped orientation: extract RGB channels from sequential input directions
                outColor=tuple(self.inputs[self.convDir(i + 1)][i] for i in range(3))
                
                # Prevent infinite loops by checking if output has changed
                if outColor == self.pastOutput:
                    self.pastOutput= colors
                    return {}, True  # Block propagation to prevent loops
                else:
                    self.pastOutput= colors
                    return {self.convDir(0):outColor}, False  # Output combined white light
                
    def restart(self):
        """
        Reset the prism to initial state for a new puzzle attempt.
        Clears the previous output tracking and calls parent restart method.
        """
        # Reset output tracking to prevent state carryover between puzzle attempts
        self.pastOutput= (0,0,0)
        return super().restart()

    def flip(self):
        """
        Toggle the prism between normal and flipped orientations.
        Changes the texture and internal state to affect light splitting/combining behavior.
        
        Returns:
            True indicating the flip operation was successful
        """
        # Update texture to show appropriate orientation (normal=0, flipped=1)
        self.texture.update("prism", index=1 if not self.flipped else 0)
        
        # Toggle the internal flip state
        self.flipped= not self.flipped
        return True

    def getData(self, pocket=False):
        """
        Serialize prism data for saving/loading levels.
        
        Args:
            pocket: If True, returns template data for level editor palette
                   If False, returns current prism state for level saving
                   
        Returns:
            Dictionary containing prism type and configuration data
        """
        # Get base cell data from parent class
        data= super().getData()
        
        if pocket:
            # Return template data for level editor (default values)
            data["data"]= {
                "direction": 0,      # Default rotation
                "flipped": 0         # Default orientation (normal)
            }
            return data
            
        # Return current prism state data for level saving
        data["data"]= {
            "direction": self.direction,  # Current rotation direction
            "flipped": self.flipped       # Current flip state
        }
        return data