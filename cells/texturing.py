# Import necessary pygame modules for texture manipulation
from pygame import image, surface, SRCALPHA, transform, BLEND_MULT

# Utility function for color blending
def multiply(texture: surface.Surface, color: tuple[int, int, int]) -> surface.Surface:
    """
    Multiplies the texture with the given color using BLEND_MULT mode.
    Creates a color overlay effect by multiplying each pixel with the specified color.
    
    Args:
        texture: The source texture surface to modify
        color: RGB color tuple to multiply with the texture
    
    Returns:
        A new surface with the color multiplication applied
    """
    # Create a copy of the original texture to avoid modifying it
    result = texture.copy()
    
    # Apply color multiplication blending (adds alpha channel to color tuple)
    result.fill(color + (0,), special_flags=BLEND_MULT)
    
    return result

# Main texturing class for managing layered texture rendering
class texturing():
    def __init__(self):
        """
        Initializes the texturing system with empty layer containers.
        Layers allow for composited rendering of multiple texture elements.
        """
        # Dictionary to store layer data (textures, renderers, states)
        self.layers = {}
        
        # Dictionary to map layer names to layer indices for easy access
        self.referencer = {}

    # Static method for default texture rendering with rotation support
    def defaultRender(layer:dict):
        """
        Default renderer that returns the texture based on the current layer state.
        Handles texture selection by index and applies rotation based on direction.
        
        Args:
            layer: Dictionary containing 'textures', 'state', and 'renderer' keys
                state: {'index': int, 'direction': int}
                    - index: -1 = composite all textures, None = transparent, >=0 = specific texture
                    - direction: 0-3 representing 0°, 90°, 180°, 270° rotation
        
        Returns:
            A 40x40 surface with the rendered and rotated texture
        """
        # Ensure direction state exists, default to 0 (no rotation)
        if "direction" not in layer["state"]:
            layer["state"]["direction"] = 0
            
        # Handle special case: composite all textures (index = -1)
        if layer["state"]["index"] == -1:
            # Create transparent surface for compositing
            final = surface.Surface((40,40), SRCALPHA)
            
            # Blit all textures on top of each other
            for img in layer["textures"]:
                final.blit(img, (0,0))
                
            # Apply rotation based on direction (0°, 90°, 180°, 270°)
            return transform.rotate(final, [0,90,180,270][layer["state"]["direction"]])
            
        # Handle transparent/empty case (index = None)
        elif layer["state"]["index"] == None:
            return surface.Surface((40,40), SRCALPHA)
            
        # Handle normal case: render specific texture by index with rotation
        return transform.rotate(layer["textures"][layer["state"]["index"]], [0,90,180,270][layer["state"]["direction"]])

    # Method to create and register a new texture layer
    def newLayer(self, layer:int, name:str, textures:list[str], renderer:callable=defaultRender, state:dict=None):
        """
        Creates a new texture layer with the specified configuration.
        
        Args:
            layer: Layer index (0 = cell, 1-2 = beams, higher numbers for additional elements)
            name: String identifier for easy layer access
            textures: List of texture file paths relative to 'assets/' directory
            renderer: Function to render this layer (defaults to defaultRender)
            state: Initial state dictionary (defaults to index=0, direction=0)
        """
        # Set default state if none provided
        if state is None:
            state = {"index": 0, "direction": 0}
        
        # Load all texture files from the assets directory
        loaded = []
        for texture in textures:
            # Convert to alpha format for transparency support
            loaded.append(image.load("assets/" + texture).convert_alpha())

        # Store layer configuration in layers dictionary
        self.layers[layer] = {"textures": loaded, "renderer": renderer, "state": state}
        
        # Create name-to-layer mapping for easy access
        self.referencer[name] = layer

    # Method to safely retrieve layer state information
    def getState(self, name):
        """
        Retrieves a copy of the current state dictionary for the specified layer.
        
        Args:
            name: String identifier of the layer
            
        Returns:
            A copy of the layer's state dictionary to prevent external modifications
        """
        # Return a copy to prevent external state modifications
        return self.layers[self.referencer[name]]["state"].copy()

    # Method to update layer state with new values
    def update(self, name, **newState):
        """
        Updates the state of a specified layer with new values.
        Validates that all provided state keys exist before applying changes.
        
        Args:
            name: String identifier of the layer to update
            **newState: Keyword arguments representing state changes (e.g., index=1, direction=2)
        """
        # Iterate through all provided state changes
        for state, value in newState.items():
            # Validate that the state key exists in the layer
            if state not in self.getState(name):
                # Print error and abort if invalid state key is found
                print(f"Error: State '{state}' not found in layer '{name}'")
                return
                
            # Apply the state change to the layer
            self.layers[self.referencer[name]]["state"][state] = value

    # Method to render all layers into a final composite image
    def render(self):
        """
        Renders all layers in order to create the final composite texture.
        Each layer is rendered using its associated renderer function and blitted onto the final surface.
        
        Returns:
            A 40x40 surface containing the composite of all active layers
        """
        # Create the base transparent surface for the final composite
        finalRender = surface.Surface((40,40), SRCALPHA)
        
        # Render each layer in order and composite them together
        for layer_index in set(self.layers.keys()):
            # Get the rendered layer surface using the layer's renderer function
            layer_surface = self.layers[layer_index]["renderer"](self.layers[layer_index])
            
            # Blit the layer onto the final composite surface
            finalRender.blit(layer_surface, (0, 0))

        return finalRender