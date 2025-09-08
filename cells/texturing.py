import logging
from pygame import image, surface, SRCALPHA, transform, BLEND_MULT

logging.addLevelName(50, "TEXTURE LOAD")
logging.addLevelName(51, "TEXTURING")
logging.addLevelName(52, "LAYER UPDATE")

logging.basicConfig(level=50, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=51, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=52, format='%(asctime)s - %(levelname)s - %(message)s')

def multiply(texture: surface.Surface, color: tuple[int, int, int]) -> surface.Surface:
    """
    Multiplies the texture with the given color.
    """
    result = texture.copy()
    result.fill(color + (0,), special_flags=BLEND_MULT)
    return result

class texturing():
    def __init__(self):
        """
        To make the texturing you need to add layers with newLayer.
        """
        self.layers = {}
        self.referencer = {}

    def defaultRender(layer:dict):
        """
        Default renderer that returns the texture in the index corresponding to the current state.
            state: {'index' : int, 'direction' : int}
        """
        #logging.log(51, f"Default render called with state: {layer['state']}")
        if "direction" not in layer["state"]:
            layer["state"]["direction"]= 0
        if layer["state"]["index"] is -1:
            final= surface.Surface((40,40), SRCALPHA)
            for img in layer["textures"]:
                final.blit(img, (0,0))
            return transform.rotate(final, [0,90,180,270][layer["state"]["direction"]])
        elif layer["state"]["index"] == None:
            return surface.Surface((40,40), SRCALPHA)
        return transform.rotate(layer["textures"][layer["state"]["index"]], [0,90,180,270][layer["state"]["direction"]])

    def newLayer(self, layer:int, name:str, textures:list[str], renderer:callable=defaultRender, state:dict=None):
        """
        Adds a new layer with the given parameters.
        Layer 0 is cell, 1 and 2 are beams
        """
        if state is None:
            state = {"index": 0, "direction": 0}
            
        loaded= []
        for texture in textures:
            loaded.append(image.load("assets/" + texture).convert_alpha())

        self.layers[layer] = {"textures": loaded, "renderer": renderer, "state": state}
        self.referencer[name] = layer
        #logging.log(50, f"Texture {name} added to layer {layer}")

    def getState(self, name):
        """
        Gets the state dict from a layer
        """
        return self.layers[self.referencer[name]]["state"].copy()

    def update(self, name, **newState):
        """
        Calls the renderer associated with the given name with the provided arguments.
        """
        #logging.log(52, f"Updating layer '{name}' with state changes: {newState}")
        for state, value in newState.items():
            if state not in self.getState(name):
                logging.error(f"State '{state}' not found in layer '{name}'")
                return
            self.layers[self.referencer[name]]["state"][state] = value

    def render(self):
        finalRender= surface.Surface((40,40), SRCALPHA)
        for i in set(self.layers.keys()):
            finalRender.blit(self.layers[i]["renderer"](self.layers[i]), (0, 0))

        return finalRender