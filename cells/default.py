# Import necessary modules for game mechanics
import logging
from .texturing import *  # Import texturing utilities for rendering surfaces
from .indicator import numbers  # Import number textures for overlay display
from math import ceil  # Import ceiling function for mathematical operations

# Configure custom logging level for debug output
logging.addLevelName(60, "LIGHTNING")
logging.basicConfig(level=60, format='%(asctime)s - %(levelname)s - %(message)s')

class default():
    # Direction mapping array: maps input directions to their opposite directions
    # Used for light beam calculations and direction conversions
    dirFrom= [2,3,0,1]
    
    def beamRenderer(self, layer:dict):
        """
        Renders the beam texture based on light state.
        Creates visual representation of light beams with proper colors and break effects.
        \n--STATE--
        \n colorA : (int, int, int) - RGB color values for beam A
        \n colorB : (int, int, int) - RGB color values for beam B  
        \n breakA : bool - Whether beam A is broken/interrupted
        \n breakB : bool - Whether beam B is broken/interrupted
        \n vertical : bool - Whether beam should be rendered vertically
        """
        # Extract state information from the layer
        state= layer["state"]
        # Create transparent surface for rendering beams
        final = surface.Surface((40,40), SRCALPHA)

        # Render beam A if it has color (not black/off)
        if state["colorA"] != (0,0,0):
            # Choose texture based on whether beam is broken
            if state["breakA"]:
                finalA = layer["textures"][2]  # Use break texture
            else:
                finalA = layer["textures"][0]  # Use normal beam texture
            # Apply color tinting and blit to final surface
            final.blit(multiply(finalA, state["colorA"]), (0, 0))

        # Render beam B if it has color (not black/off)
        if state["colorB"] != (0,0,0):
            # Choose texture based on whether beam is broken
            if state["breakB"]:
                finalB = layer["textures"][3]  # Use break texture
            else:
                finalB = layer["textures"][1]  # Use normal beam texture
            # Apply color tinting and blit to final surface
            final.blit(multiply(finalB, state["colorB"]), (0, 0))
        
        # Rotate beam 270 degrees if it should be vertical
        if state["vertical"]:
            final = transform.rotate(final, 270)
        
        return final
    
    def overlayRenderer(self, layer:dict):
        """
        Renders debug overlay showing RGB color values for each beam direction.
        Displays numerical indicators for light intensity in each color channel.
        """
        # Only render overlay if explicitly requested
        if layer["state"]["show"]:
            # Start with base overlay texture
            final = layer["textures"][-1].copy()
            imgs= layer["textures"]

            # Extract color values for each beam direction
            color0= layer["state"]["stateY"]["colorA"]  # Vertical beam A (up)
            color1= layer["state"]["stateX"]["colorA"]  # Horizontal beam A (right)
            color2= layer["state"]["stateY"]["colorB"]  # Vertical beam B (down)
            color3= layer["state"]["stateX"]["colorB"]  # Horizontal beam B (left)

            # Define pixel coordinates for number placement
            coordsh= (13,18,23)  # Horizontal positions for RGB values
            coordsv= (11,17,23)  # Vertical positions for RGB values
            commons= (5,30,6,30)  # Common coordinate pairs for positioning

            # Process each beam's color values
            for i, color in enumerate([color0, color2, color1, color3]):
                # Process each RGB channel
                for j, rgb in enumerate(color):
                    # Convert color intensity back to display range (0-10)
                    rgb = ceil((rgb / 25.5 - 3 * int(bool(rgb))) * 1.428571)
                    # Position numbers based on beam direction (vertical vs horizontal)
                    if i < 2:  # Vertical beams (up/down)
                        # Use red, cyan, blue color coding for R, G, B channels
                        final.blit(multiply(imgs[rgb], ((255,50,50)[j], (50,255,180)[j], (50,50,255)[j])), (coordsh[j], commons[i]))
                    else:  # Horizontal beams (left/right)
                        final.blit(multiply(imgs[rgb], ((255,50,50)[j], (50,255,180)[j], (50,50,255)[j])), (commons[i], coordsv[j]))

            return final
        else:
            # Return empty transparent surface if overlay is disabled
            return surface.Surface((40,40), SRCALPHA)

    def __init__(self, xy: tuple[int, int]|None = None, name:str="D", breaks=None, layout=None, data=None):
        """
        Initialize a default cell object with position, textures, and light states.
        Sets up rendering layers for base cell, beams, and debug overlay.
        """
        # Initialize texture manager for multi-layer rendering
        self.texture= texturing()
        # Store cell position in grid coordinates
        self.xy = xy
        # Store cell identifier/name
        self.name = name
        
        # Set default data if none provided
        if data is None or data == {}:
            data= {"direction":0}
        # Store rotation direction (0-3 for 0°, 90°, 180°, 270°)
        self.direction= data["direction"]
        
        # Initialize light input array for 4 directions (up, right, down, left)
        self.inputs= [(0,0,0), (0,0,0), (0,0,0), (0,0,0)]
        
        # Initialize horizontal beam state (left-right light flow)
        self.stateX= {"colorA": (0, 0, 0), "colorB": (0, 0, 0), "breakA": False, "breakB": False, "vertical": False}
        # Initialize vertical beam state (up-down light flow)
        self.stateY= {"colorA": (0, 0, 0), "colorB": (0, 0, 0), "breakA": False, "breakB": False, "vertical": True}
        
        # Add base cell texture layer (only for non-default cells)
        if name != "D":
            self.texture.newLayer(layer=0, name="base", textures=["cell.png"])
        
        # Add vertical beam rendering layer (layer 2, higher priority)
        self.texture.newLayer(layer=2, name="beamV", textures=["beams/beamA.png", "beams/beamB.png", "beams/breakA.png", "beams/breakB.png"], renderer=self.beamRenderer, state=self.stateY)
        # Add horizontal beam rendering layer (layer 1, lower priority)
        self.texture.newLayer(layer=1, name="beamH", textures=["beams/beamA.png", "beams/beamB.png", "beams/breakA.png", "beams/breakB.png"], renderer=self.beamRenderer, state=self.stateX)
        # Add debug overlay layer (layer 20, highest priority)
        self.texture.newLayer(layer=20, name="overlay", textures= numbers + ["indicators/overlay.png"], state={"show": False, "stateX": self.stateX, "stateY": self.stateY}, renderer=self.overlayRenderer)
        
        # Initialize list of directions where light breaks/stops
        self.breaks= breaks if breaks is not None else []

    def changeDirection(self, direction: int):
        """
        Update the cell's rotation direction.
        Direction values: 0=0°, 1=90°, 2=180°, 3=270°
        """
        self.direction = direction

    def editProperty(self, index:int, changing:int):
        """
        Attempt to modify a cell property. 
        Default implementation returns False (no properties can be edited).
        Overridden by subclasses that have editable properties.
        """
        return False

    def getData(self, pocket=False):
        """
        Serialize cell data for saving/loading levels.
        
        Args:
            pocket: If True, returns default/template data (direction=0)
                   If False, returns current cell state data
        
        Returns:
            Dictionary containing cell type and configuration data
        """
        if pocket:
            # Return template data for level editor palette
            return {
                "type": self.__class__.__name__.lower(),
                "data": {
                    "direction": 0
                }
            }
        
        # Return current cell state for level saving
        return {
            "type": self.__class__.__name__.lower(),
            "data": {
                "direction": self.direction
            }
        }
    
    def changeBeamStates(self, vertical=False, beamDirs=None, **states):
        """
        Update beam rendering states for light visualization.
        
        Args:
            vertical: True for vertical beams (up-down), False for horizontal (left-right)
            beamDirs: List of specific beam directions to update (0=up, 1=right, 2=down, 3=left)
            **states: State properties to update (colorA, colorB, breakA, breakB, etc.)
        """
        # Update states for all beams in a direction (vertical or horizontal)
        if beamDirs is None:
            if vertical:
                # Update vertical beam states (up-down light flow)
                for key, value in states.items():
                    if key in ["colorA", "colorB"]:
                        # Convert color intensity from game scale (0-10) to display scale (0-255)
                        # Formula: intensity = (value/1.428571 + 3*bool(value)) * 25.5
                        # This ensures 0→0 but 1→5, scaling up to 10→255 for proper RGB rendering
                        self.stateY[key]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                    elif key in self.stateY:
                        self.stateY[key]= value
            else:
                # Update horizontal beam states (left-right light flow)
                for key, value in states.items():
                    if key in ["colorA", "colorB"]:
                        # Apply same color intensity conversion as vertical beams
                        self.stateX[key]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                    elif key in self.stateX:
                        self.stateX[key]= value
        else:
            # Update states for specific beam directions
            for i in beamDirs:
                match i:
                    case 0:  # Up direction - vertical beam A
                        for key, value in states.items():
                            if key == "color":
                                self.stateY["colorA"]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                            else:
                                self.stateY[key]= value
                    case 1:  # Right direction - horizontal beam A
                        for key, value in states.items():
                            if key == "color":
                                self.stateX["colorA"]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                            else:
                                self.stateX[key] = value
                    case 2:  # Down direction - vertical beam B
                        for key, value in states.items():
                            if key == "color":
                                self.stateY["colorB"]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                            else:
                                self.stateY[key]= value
                    case 3:  # Left direction - horizontal beam B
                        for key, value in states.items():
                            if key == "color":
                                self.stateX["colorB"]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                            else:
                                self.stateX[key]= value
    
    def convDir(self, wantedDir):
        """
        Convert direction based on cell's current rotation.
        
        Args:
            wantedDir: Direction to convert (0=up, 1=right, 2=down, 3=left)
            
        Returns:
            Adjusted direction accounting for cell's rotation
        """
        # Direction conversion matrix based on cell rotation:
        # Each row represents a rotation state (0°, 90°, 180°, 270°)
        # Each column maps input direction to rotated direction
        return [[0,1,2,3],[1,2,3,0],[2,3,0,1],[3,0,1,2]][self.direction][wantedDir]

    def checkBreak(self, From):
        """
        Check if incoming light should break/stop at this cell.
        
        Args:
            From: Direction light is coming from (0=up, 1=right, 2=down, 3=left)
            
        Returns:
            True if light breaks, False if it passes through
        """
        # Adjust break directions based on cell's rotation
        breaks= []
        for b in self.breaks:
            b+= self.direction
            if b > 3:
                b -= 4
            breaks.append(b)

        # Check if light breaks at the entry point
        if From in breaks:
            # Determine which beam type (vertical/horizontal) based on direction
            match From:
                case 0 | 2:  # Up or Down - vertical beam
                    beam= True
                case 1 | 3:  # Right or Left - horizontal beam
                    beam= False
            
            # Set appropriate break flag based on entry direction
            match From:
                case 0 | 1:  # Up or Right - affects beam A
                    self.changeBeamStates(beam, breakA=True)
                case 3 | 2:  # Left or Down - affects beam B
                    self.changeBeamStates(beam, breakB=True)

            return True
        
        # Check if light breaks at the opposite direction (exit point)
        if [2, 3, 0, 1][From] in breaks:
            return True
        
        return False
    
    def restart(self):
        """
        Reset cell to initial state.
        Clears all light inputs and beam states for a fresh puzzle start.
        """
        # Clear all
        self.inputs= [(0,0,0), (0,0,0), (0,0,0), (0,0,0)]
        # Reset vertical beam states (no color, no breaks)
        self.changeBeamStates(True, colorA= (0,0,0), colorB=(0,0,0), breakA= False, breakB= False)
        # Reset horizontal beam states (no color, no breaks)
        self.changeBeamStates(False, colorA= (0,0,0), colorB=(0,0,0), breakA= False, breakB= False)

    def changeLight(self, From, color=None):
        """
        Process incoming light and update cell's beam states.
        Handles light combining, breaking, and beam rendering updates.
        
        Args:
            From: Direction light is coming from (0=up, 1=right, 2=down, 3=left)
            color: RGB tuple for light color, defaults to (0,0,0) if None
            
        Returns:
            Tuple of (light_data_dict, break_occurred_bool)
        """
        # Set default color if none provided
        if color is None:
            color=(0,0,0)
        # Store light input for this direction
        self.inputs[From] = color

        # Handle vertical light (up/down directions)
        if From in [0, 2]:
            # Check if light should break at this cell
            Break= self.checkBreak(From)
            if Break:
                # Light breaks - create separate beams for A and B
                match From:
                    case 0:  # Light from above - affects beam A
                        colorA= color
                        self.changeBeamStates(colorA= colorA, vertical=True)
                    case 2:  # Light from below - affects beam B
                        colorB= color
                        self.changeBeamStates(colorB=colorB, vertical=True)
            else:
                # Light passes through - combine with opposite direction input
                # Add RGB values with opposite direction, clamping to max of 10
                Color= tuple(min(10, color[i] + self.inputs[self.dirFrom[From]][i]) for i in range(3))
                colorA= Color
                colorB= Color
                self.changeBeamStates(colorA= colorA, colorB=colorB, vertical=True)

        else:  # Handle horizontal light (left/right directions)
            # Check if light should break at this cell
            Break= self.checkBreak(From)
            if Break:
                # Light breaks - create separate beams for A and B
                match From:
                    case 1:  # Light from right - affects beam A
                        colorA= color
                        self.changeBeamStates(vertical=False, colorA= colorA)
                    case 3:  # Light from left - affects beam B
                        colorB= color
                        self.changeBeamStates(vertical=False, colorB=colorB)
            else:
                # Light passes through - combine with opposite direction input
                # Add RGB values with opposite direction, clamping to max of 10
                Color= tuple(min(10, color[i] + self.inputs[self.dirFrom[From]][i]) for i in range(3))
                colorA= Color
                colorB= Color
                self.changeBeamStates(vertical=False, colorA= colorA, colorB=colorB)
        
        # Return light data and break status for game logic
        return {From:color}, Break
    
    def __eq__(self, other):
        """
        Compare cell with another object for equality.
        Used for cell type identification in game logic.
        """
        if self.name == "D":
            return "D" == other
        else:
            return self.name[0].upper() == other

    def convert(self, other:object, name=None, layout= None, data= None):
        """
        Convert this cell to a different cell type while preserving state.
        
        Args:
            other: Target cell class to convert to
            name: New cell name/identifier
            layout: Layout data for new cell
            data: Configuration data for new cell
            
        Returns:
            New cell instance of the target type with preserved light inputs
        """
        if data is not None:
            data= data.copy()
        # Create new cell instance with same position and provided parameters
        new= other(xy= self.xy, name=name, layout= layout, data= data)
        # Preserve current light inputs in the new cell
        new.inputs= self.inputs.copy()
        return new
    
    def flip(self):
        """
        Attempt to flip/mirror the cell.
        Default implementation returns False (cannot be flipped).
        Overridden by cells that support flipping (like mirrors).
        """
        return False

    def render(self,overlay=False, scale= (80, 80)):
        """
        Render the cell as a pygame surface.
        
        Args:
            overlay: If True, includes debug overlay showing RGB values
            scale: Target size for the rendered surface (width, height)
            
        Returns:
            Scaled pygame surface containing the rendered cell
        """
        if overlay:
            # Temporarily enable overlay, render, then disable
            self.texture.update("overlay", show= True)
            final= transform.scale(self.texture.render(), scale)
            self.texture.update("overlay", show= False)
            return final

        # Render normal cell without overlay and scale to requested size
        return transform.scale(self.texture.render(), scale)
    
