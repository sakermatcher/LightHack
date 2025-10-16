# Import necessary modules for game functionality
import logging
from .texturing import *  # Import texture handling utilities
from .default import default  # Import base cell class
from.indicator import indicatorRender, numbers  # Import indicator rendering for RGB displays

class final(default):
    """
    Final cell class that serves as the goal/target for light puzzles.
    Features two modes: 
    - Final mode: Requires exact RGB color match to complete the level
    - Filter mode: Subtracts its color values from passing light and allows light through
    """

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "F", layout=None, data=None):
        """
        Initialize a final/goal cell with target color requirements.
        
        Args:
            xy: Grid coordinates (x,y) where the final cell is placed
            name: Cell identifier/name for the final cell
            layout: Grid layout information (unused for final cells)
            data: Dictionary with direction, final mode (True/False), and target color
        """
        # Set default configuration if none provided
        if data is None:
            data = {"direction": 0, "final": True, "color": (0,0,0)}
        
        # Ensure final mode property exists
        if "final" not in data:
            data["final"]= True

        # Ensure color property exists
        if "color" not in data:
            data["color"]= (0,0,0)
        
        # Configure visual appearance and blocking behavior based on mode
        if data["final"]:
            idx= 0           # Show cover (final mode appearance)
            breaks= [0,2,3]  # Block light from top, bottom, and left (only accept from right)
        else:
            idx= None        # Hide cover (filter mode appearance)
            breaks= [0,2]    # Block light from top and bottom (allow left-right passage)

        # Store final cell properties
        self.color= data["color"]      # Target RGB color that must be matched
        self.final= data["final"]      # True = final mode, False = filter mode
        self.isCompleated= False       # Tracks whether the puzzle goal has been achieved
        
        # Initialize parent class with appropriate blocking configuration
        super().__init__(xy= xy, name= name, breaks=breaks, data= data)
        
        # Add main final cell body texture
        self.texture.newLayer(layer=3, name="final", textures=["final/main.png"], state={"index": 0, "direction": data["direction"]})
        
        # Add cover layer (visible in final mode, hidden in filter mode)
        self.texture.newLayer(layer=4, name="cover", textures=["final/cover.png"], state={"index": idx, "direction": data["direction"]})
        
        # Add status LED (off/on indicator for puzzle completion)
        self.texture.newLayer(layer=5, name="led", textures=["final/off.png", "final/on.png"], state={"index": 0, "direction": data["direction"]})
        
        # Add indicator screen backgrounds for RGB target value display
        self.texture.newLayer(6, "screens", ["indicators/UL.png", "indicators/UR.png", "indicators/DL.png"], state={"index": -1})
        
        # Add RGB target value indicators with colored numbers
        # Red target value indicator (Upper Left corner)
        self.texture.newLayer(7, "colorR", numbers, state={"corner": "UL", "color": (255,50,50), "number": self.color[0]}, renderer=indicatorRender)
        # Green target value indicator (Upper Right corner)
        self.texture.newLayer(8, "colorG", numbers, state={"corner": "UR", "color": (50,255,50), "number": self.color[1]}, renderer=indicatorRender)
        # Blue target value indicator (Down Left corner)
        self.texture.newLayer(9, "colorB", numbers, state={"corner": "DL", "color": (50,180,255), "number": self.color[2]}, renderer=indicatorRender)
        

    def changeDirection(self, direction):
        """
        Update the final cell's rotation direction and rotate all visual elements accordingly.
        
        Args:
            direction: New rotation direction (0=0°, 1=90°, 2=180°, 3=270°)
        """
        # Update all texture layers to match new direction
        self.texture.update("final", direction=direction)  # Main body
        self.texture.update("cover", direction=direction)  # Cover (if visible)
        self.texture.update("led", direction=direction)    # Status LED
        return super().changeDirection(direction)
    
    def editProperty(self, index:int, changing:int):
        """
        Edit the target RGB color value for a specific channel in the level editor.
        
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
        
        # Update all RGB indicator displays to show new target values
        self.texture.update("colorR", number=self.color[0])  # Update red indicator
        self.texture.update("colorG", number=self.color[1])  # Update green indicator
        self.texture.update("colorB", number=self.color[2])  # Update blue indicator
        return True

    def changeLight(self, From=None, color=None):
        """
        Process incoming light and check for puzzle completion.
        Behavior depends on mode: final mode checks for exact color match,
        filter mode subtracts color values and passes remaining light through.
        
        Args:
            From: Direction light is coming from (0=up, 1=right, 2=down, 3=left)
            color: RGB color tuple of the incoming light
            
        Returns:
            Tuple of (output_light_dict, light_blocked_bool)
        """
        # Reset completion status and LED at start of each light processing
        self.isCompleated= False
        self.texture.update("led", index=0)  # Turn off success LED
        
        # Set default color if none provided
        if color is None:
            color= (0,0,0)
        
        # FINAL MODE: Check for exact color match to complete puzzle
        if self.final and From == self.convDir(1):  # Light coming from the right (input direction)
            # Check if incoming light exactly matches target color
            if color[0] == self.color[0] and color[1] == self.color[1] and color[2] == self.color[2]:
                self.isCompleated= True
                self.texture.update("led", index=1)  # Turn on success LED
                
        # FILTER MODE: Process light passing through horizontally with color subtraction
        elif not self.final and (From == self.convDir(1) or From == self.convDir(3)):  # Light from left or right
            # Store incoming light from this direction
            self.inputs[From]= color
            
            # Calculate combined light for visual display (bidirectional flow)
            # Add light from both directions, but subtract target color from the opposite direction
            color1= tuple(min(10, self.inputs[self.convDir(1)][i] + max(0, self.inputs[self.convDir(3)][i] - self.color[i])) for i in range(3))
            color3= tuple(min(10, self.inputs[self.convDir(3)][i] + max(0, self.inputs[self.convDir(1)][i] - self.color[i])) for i in range(3))
            
            # Update beam visual states for both horizontal directions
            self.changeBeamStates(beamDirs=[self.convDir(1)], color= color1)
            self.changeBeamStates(beamDirs=[self.convDir(3)], color= color3)
            
            # Calculate output light (subtract target color from input, minimum 0)
            output= tuple(max(0, color[i] - self.color[i]) for i in range(3))
            
            # Calculate total combined light intensity for completion check
            combined_color= tuple(min(10, self.inputs[self.convDir(1)][i] + self.inputs[self.convDir(3)][i]) for i in range(3))
            
            # Check if combined light meets or exceeds target requirements
            if combined_color[0] >= self.color[0] and combined_color[1] >= self.color[1] and combined_color[2] >= self.color[2]:
                self.isCompleated= True
                self.texture.update("led", index=1)  # Turn on success LED
            
            # Return filtered light output or block if no light remains
            if output != (0,0,0):
                return {self.dirFrom[From]:output}, False  # Pass filtered light to opposite direction
            else:
                return {}, True  # No light output, effectively blocked

        # Default case: handle other light interactions normally (will likely be blocked)
        return super().changeLight(From, color)
    
    def flip(self):
        """
        Toggle between final mode and filter mode.
        Changes the cell's behavior and visual appearance.
        
        Returns:
            True indicating the flip operation was successful
        """
        # Toggle between final mode (True) and filter mode (False)
        self.final= not self.final
        
        # Update cover visibility: show cover in final mode, hide in filter mode
        self.texture.update("cover", index=0 if self.final else None)
        return True

    def getData(self, pocket= False):
        """
        Serialize final cell data for saving/loading levels.
        
        Args:
            pocket: If True, returns template data for level editor palette
                   If False, returns current final cell state for level saving
                   
        Returns:
            Dictionary containing final cell type and configuration data
        """
        # Get base cell data from parent class
        data= super().getData()
        
        # Return current final cell state data (same for both pocket and save)
        data["data"]= {
            "direction": self.direction,  # Current rotation direction
            "final": self.final,          # Current mode (True=final, False=filter)
            "color": self.color           # Target RGB color values
        }
        return data
    
