import logging
from .texturing import *
from .default import default

class myName(default):

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "Laser", layout=None, data=None):
        """
        xy= (x,y)
        name= cell name
        layout= simple layout (if needed)
        data= dict with relevant data (direction, color, etc.)
        """
        if data is None:
            data = {"color": (0,0,0), "direction": 0}
        super().__init__(xy= xy, name= name, breaks=[0,1,2,3], data= data) #Breaks which walls break the beam 
        self.texture.newLayer(layer=3, name="layerName", textures=["textureLocation"], state={"index": 0, "direction": data["direction"]})

    def changeDirection(self, direction): #Rotate Your Textures!
        # ej. self.texture.update("layerName", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        if From is not None:
            return super().changeLight(From, color)
        else:
            return {[2,3,0,1][self.direction]:color}, False

    def getData(self): #Data thats needed to be saved on level info
        data= super().getData()
        data["data"]= {
            "direction": self.direction
        }
        return data