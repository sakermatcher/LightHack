# Import necessary modules for game functionality
from .texturing import *  # Import texture handling utilities
from .default import default  # Import base cell class

class mirror(default):
    """
    Mirror cell class that reflects light beams at 90-degree angles.
    Supports two orientations that determine the reflection pattern:
    - Direction 0: Reflects light from vertical/horizontal to diagonal directions
    - Direction 1: Reflects light in the opposite diagonal pattern
    """

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "M", layout=None, data=None):
        """
        Initialize a mirror cell with reflection capabilities.
        
        Args:
            xy: Grid coordinates (x,y) where the mirror is placed
            name: Cell identifier/name for the mirror
            layout: Grid layout information (unused for mirrors) 
            data: Dictionary with relevant data (direction for reflection orientation)
        """
        # Set default configuration if none provided
        if data is None:
            data = {"direction": 0}
            
        # Initialize parent class with no breaking walls (light passes through via reflection)
        super().__init__(xy= xy, name= name, breaks=[], data= data)
        
        # Add mirror texture layer - single texture that rotates based on direction
        self.texture.newLayer(layer=3, name="mirror", textures=["others/mirror.png"], state={"index": 0, "direction": self.direction})

    def changeDirection(self, direction):
        """
        Update the mirror's reflection orientation.
        Note: Mirror only supports two orientations (0 and 1), mapped from input direction.
        
        Args:
            direction: Input direction (0-3), mapped to mirror orientation (0 or 1)
        """
        # Map input direction to mirror orientation: even numbers→1, odd numbers→0
        direction= [1,0][self.direction]
        
        # Update mirror texture to show correct orientation
        self.texture.update("mirror", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        """
        Process light reflection through the mirror.
        Reflects incoming light at 90-degree angles based on mirror orientation.
        
        Args:
            From: Direction light is coming from (0=up, 1=right, 2=down, 3=left)
            color: RGB color tuple of the incoming light
            
        Returns:
            Tuple of (reflected_light_dict, light_blocked_bool)
        """
        # Handle case where no specific input direction is given (process all inputs)
        if From is None:
            end= {}
            # Process all active light inputs and calculate their reflections
            for i in range(4):
                if self.inputs[i] != (0,0,0):
                    # Recursively process each input and map to reflection direction
                    self.changeLight(i, self.inputs[i])
                    # Map input direction to output direction based on mirror orientation
                    # Direction mappings: [3,2,1,0] for orientation 0, [1,0,3,2] for orientation 1
                    end[[[3,2,1,0],[1,0,3,2]][self.direction][i]]= color
            return end.copy(), False
        else:
            # Process specific light input
            if color is None:
                color=(0,0,0)
            
            # Store the incoming light
            self.inputs[From] = color

            # Calculate reflected light color by combining with light from reflection partner
            # The reflection mapping depends on mirror orientation
            reflection_partner = [[3,2,1,0],[1,0,3,2]][self.direction][From]
            Color= tuple(min(10, color[i] + self.inputs[reflection_partner][i]) for i in range(3))
            
            # Update beam visual states based on incoming light direction
            match From:
                case 0:  # Light from above
                    self.changeBeamStates(vertical=True, colorA= Color)
                case 1:  # Light from right
                    self.changeBeamStates(vertical=False, colorA= Color)
                case 2:  # Light from below
                    self.changeBeamStates(vertical=True, colorB= Color)
                case 3:  # Light from left
                    self.changeBeamStates(vertical=False, colorB= Color)
                
            # Update beam visual states for reflected light based on mirror orientation
            match self.direction:
                case 0:  # Mirror orientation 0 (\ diagonal reflection)
                    match From:
                        case 0:  # Up → Left
                            self.changeBeamStates(vertical=False, colorB= Color)
                        case 1:  # Right → Down
                            self.changeBeamStates(vertical=True, colorB= Color)
                        case 2:  # Down → Right
                            self.changeBeamStates(vertical=False, colorA= Color)
                        case 3:  # Left → Up
                            self.changeBeamStates(vertical=True, colorA= Color)

                case 1:  # Mirror orientation 1 (/ diagonal reflection)
                    match From:
                        case 0:  # Up → Right
                            self.changeBeamStates(vertical=False, colorA= Color)
                        case 1:  # Right → Up
                            self.changeBeamStates(vertical=True, colorA= Color)
                        case 2:  # Down → Left
                            self.changeBeamStates(vertical=False, colorB= Color)
                        case 3:  # Left → Down
                            self.changeBeamStates(vertical=True, colorB= Color)

            # Return reflected light in the calculated direction
            reflection_direction = [[3,2,1,0],[1,0,3,2]][self.direction][From]
            return {reflection_direction: color}, False
        
    def getData(self, pocket=False):
        """
        Serialize mirror data for saving/loading levels.
        
        Args:
            pocket: If True, returns template data for level editor palette
                   If False, returns current mirror state for level saving
                   
        Returns:
            Dictionary containing mirror type and configuration data
        """
        # Get base cell data from parent class
        data= super().getData()
        
        if pocket:
            # Return template data for level editor (default orientation)
            data["data"]= {
                "direction": 0  # Default mirror orientation
            }
            return data
            
        # Return current mirror state data for level saving
        data["data"]= {
            "direction": self.direction  # Current reflection orientation
        }
        return data