# Import necessary modules for game functionality
import logging
from .texturing import *  # Import texture handling utilities
from .default import default  # Import base cell class
from uuid import uuid4  # Import UUID generation for unique level IDs

class level(default):
    """
    Level cell class that acts as a level selector/gateway in the game map.
    Manages level unlocking, state tracking, and navigation to different levels.
    Supports conditional unlocking based on light inputs and AND/OR logic.
    """

    def __init__(self, data= None, **kwargs):
        """
        Initialize a level selector cell with unlock conditions and navigation.
        
        Args:
            data: Dictionary containing level configuration:
                - state: Level accessibility (0=locked, 1=unlocked, 2=current/active)
                - unlocksWith: Number of light inputs required to unlock
                - level: Unique level identifier string
                - next: Dictionary mapping directions to output light colors
        """
        # Initialize unlock logic mode (False = AND logic, True = OR logic)
        self.andOr= False
        
        # Set default data if none provided
        if data is None:
            data= {}
            
        # Initialize level state (0=locked, 1=unlocked, 2=current)
        if "state" not in data:
            data["state"] = 1  # Default to unlocked
        self.state = data["state"]
        
        # Initialize unlock requirements
        if "unlocksWith" not in data:
            data["unlocksWith"] = 0  # Default: no inputs required to unlock
        self.unlocksWith= data["unlocksWith"]
        
        # Configure visual appearance and light blocking based on state
        if self.state == 0:  # Locked state
            idx= 1           # Use locked texture
            passer= None     # No pass indicator
            breaks= [0,1,2,3]  # Block all light directions
        elif self.state == 1:  # Unlocked state
            idx= 0           # Use normal level texture
            passer= 0        # Show "can pass" indicator
            breaks= []       # Allow light through
        else:  # Current/active state (state == 2)
            idx= 0           # Use normal level texture
            passer= 1        # Show "currently doing" indicator
            breaks= []       # Allow light through
            
        # Generate or load level identifier
        if "level" not in data:
            self.levelID= str(uuid4())[:8]  # Generate 8-character unique ID
        else:
            self.levelID= data["level"]

        # Track state changes for level editor
        self.stateChanger= 0

        # Initialize output light configuration
        if "next" not in data:
            data["next"] = {}
        self.next= {}
        # Convert string keys to integer directions for output mapping
        for key, value in data["next"].items():
            self.next[int(key)]= value

        # Initialize parent class with appropriate blocking configuration
        super().__init__(name= "L", breaks=breaks, data= {})
        
        # Add base level texture layer (normal or locked appearance)
        self.texture.newLayer(layer=0, name="base", textures=["menu/level.png", "disabledCells/0.png"], state={"index": idx, "direction": 0})
        
        # Add pass indicator layer (shows level completion status)
        self.texture.newLayer(layer=3, name="pass", textures=["menu/levelPass.png", "menu/levelDo.png"], state={"index": passer, "direction": 0})

    def changeLight(self, From=None, color=None):
        """
        Process incoming light and handle level unlocking logic.
        Updates visual states and determines if level should be unlocked.
        
        Args:
            From: Direction light is coming from (0=up, 1=right, 2=down, 3=left)
            color: RGB color tuple of the incoming light
            
        Returns:
            Tuple of (output_light_dict, light_blocked_bool)
        """
        # Store incoming light from specified direction
        if From is not None:
            self.inputs[From]= color
            
        # Check unlock conditions if level is currently locked and receiving light
        if From is not None and color is not None and self.state == 0:
            # Count number of active light inputs (non-black colors)
            total= 0
            for i in self.inputs:
                if i != (0,0,0):
                    total += 1
                    
            # Unlock level if sufficient inputs are received
            if self.unlocksWith <= total:
                self.state= 2        # Change to "current" state
                self.breaks= []      # Remove light blocking
                self.texture.update("base", index=0)     # Show normal texture
                self.texture.update("pass", index=1)     # Show "doing" indicator

        # Update visual beam states for all active inputs
        for i in range(4):
            if self.inputs[i] != (0,0,0):
                # Update beam visuals for this direction
                self.changeBeamStates(beamDirs=[i], color= self.inputs[i])
                # Check if light should be blocked in this direction
                self.checkBreak(i)

        # Return appropriate output based on level state
        if self.state == 0:
            # Locked state: block all light
            return {}, True
        elif self.state == 1:
            # Unlocked state: output configured light patterns
            # Update beam visuals for all output directions
            for i in self.next:
                self.changeBeamStates(beamDirs=[i], color= self.next[i])
            return self.next, False  # Pass through configured outputs
        else:
            # Current state (state == 2): block light (level is being played)
            return {}, True
        
    def openLevel(self):
        """
        Get the level identifier for loading/opening this level.
        
        Returns:
            String containing the unique level ID
        """
        return self.levelID
    
    def unlock(self):
        """
        Manually unlock the level (used for level progression management).
        Changes state from locked to unlocked and updates visual appearance.
        """
        self.state= 1  # Set to unlocked state
        self.texture.update("base", index=0)     # Show normal texture
        self.texture.update("pass", index=0)     # Show "can pass" indicator
    
    def editProperty(self, index, changing):
        """
        Edit level properties in the level editor.
        
        Args:
            index: Property/action selector:
                   0-3: Configure output direction colors
                   4: Change level ID
                   5: Set unlock state
                   6: Set lock state  
                   7: Set AND logic mode
                   8: Set OR logic mode
                   9: Show help information
            changing: Color selection for direction outputs (0=green, 1=blue, 2=red)
            
        Returns:
            True indicating the property edit was processed
        """
        # Handle special property changes
        if index == 4:
            # Change level identifier
            self.levelID= input("New Level ID: ")
            return True
        if index == 5:
            # Set to unlock state for saving
            self.stateChanger= 2
            return True
        if index == 6:
            # Set to lock state for saving
            self.stateChanger= 0
            return True
        if index == 7:
            # Set AND logic mode (all inputs required)
            self.andOr= False
            return True
        if index == 8:
            # Set OR logic mode (any input sufficient)
            self.andOr= True
            return True
        if index == 9:
            # Display help information
            print("Inputs; 0,1,2,3: Direction, 4: LevelID, 5: Unlock, 6: Lock, 7: AND, 8: OR")
            
        # Handle directional output configuration
        # Available colors: green (0,10,0), blue (0,0,10), red (10,0,0)
        color_options = [(0,10,0), (0,0,10), (10,0,0)]
        
        if index in self.next:
            # Toggle existing output direction (remove if same color selected)
            if self.next[index] == color_options[changing]:
                del self.next[index]
            else:
                self.next[index] = color_options[changing]
        elif index in [0, 1, 2, 3]:
            # Add new output direction with selected color
            self.next[index] = color_options[changing]
        return True

    def getData(self, pocket= False):
        """
        Serialize level cell data for saving/loading levels.
        Calculates unlock requirements based on current logic mode.
        
        Args:
            pocket: If True, returns template data for level editor palette
                   If False, returns current level state for level saving
                   
        Returns:
            Dictionary containing level type and configuration data
        """
        # Calculate unlock requirements based on logic mode
        self.unlocksWith= 0
        data= super().getData()
        
        if self.andOr:
            # OR logic: only one input needed
            self.unlocksWith= 1
        else:
            # AND logic: count number of True inputs (debug print shows current inputs)
            print(self.inputs)
            for i in self.inputs:
                if i == True:  # This seems to be checking boolean rather than color
                    self.unlocksWith += 1
            
        # Return level configuration data
        data["data"]= {
            "state": self.stateChanger,    # State to save (from editor changes)
            "next": self.next,             # Output light directions and colors
            "unlocksWith": self.unlocksWith,  # Number of inputs required to unlock
            "level": self.levelID          # Unique level identifier
        }
        return data