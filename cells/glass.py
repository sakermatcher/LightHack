import logging
from .texturing import *
from .default import default
from .indicator import indicatorRender, numbers

class glass(default):

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "glass", layout=None, data=None):
        """
        xy= (x,y)
        name= cell name
        layout= simple layout (if needed)
        data= dict with relevant data (direction, color, etc.)
        """
        if data is None:
            data = {"direction": 0, "type":0, "potency": 5}
        super().__init__(xy= xy, name= name, breaks=[0,2], data= data) #Breaks which walls break the beam 
        self.type= data["type"] #0: Light, 1 is dark
        self.potency= data["potency"]
        self.texture.newLayer(layer=3, name="lens", textures=["glass/light.png", "glass/dark.png"], state={"index": self.type, "direction": data["direction"]})
        self.texture.newLayer(layer=4, name="indicator", textures=["indicators/DR.png"], state={"index": 0, "direction": 0})
        self.texture.newLayer(layer=5, name= "number", textures=numbers, renderer=indicatorRender, state={"corner": "DR", "color": (255,255,255), "number": self.potency})

    def changeDirection(self, direction):
        if direction == 2:
            direction = 0
        self.texture.update("lens", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        if color is None:
            color= (0,0,0)
        
        self.inputs[From]= color

        if self.checkBreak(From):
            match From:
                    case 0:
                        self.changeBeamStates(colorA= color, vertical=True)
                    case 1:
                        self.changeBeamStates(colorA=color, vertical=False)
                    case 2:
                        self.changeBeamStates(colorB=color, vertical=True)
                    case 3:
                        self.changeBeamStates(colorB=color, vertical=False)
            return {}, True

        if self.type == 1: #Dark
            colorA= tuple(max(0, color[i] + self.inputs[self.dirFrom[From]][i] - self.potency * int(bool(self.inputs[self.dirFrom[From]][i]))) for i in range(3))
            colorB= tuple(max(0, self.inputs[self.dirFrom[From]][i] + color[i] - self.potency * int(bool(color[i]))) for i in range(3))
            self.changeBeamStates(beamDirs=[From], color= colorA)
            self.changeBeamStates(beamDirs=[self.dirFrom[From]], color= colorB)
            return {self.dirFrom[From]: tuple(max(0, color[i] - self.potency * int(bool(color[i]))) for i in range(3))}, False
        else: #Light
            colorA= tuple(min(10, color[i] + self.inputs[self.dirFrom[From]][i] + self.potency * int(bool(self.inputs[self.dirFrom[From]][i]))) for i in range(3))
            colorB= tuple(min(10, self.inputs[self.dirFrom[From]][i] + color[i] + self.potency * int(bool(color[i]))) for i in range(3))
            self.changeBeamStates(beamDirs=[From], color= colorA)
            self.changeBeamStates(beamDirs=[self.dirFrom[From]], color= colorB)
            return {self.dirFrom[From]: tuple(min(10, color[i] + self.potency * int(bool(color[i]))) for i in range(3))}, False

        
    def getData(self): #Data thats needed to be saved on level info
        data= super().getData()
        data["data"]= {
            "direction": self.direction,
            "type": self.type,
            "potency": self.potency
        }
        return data