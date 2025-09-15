import logging
from .texturing import *
from .default import default

class level(default):

    def __init__(self, data= None, **kwargs):
        """
        opens= levelDir
        state= 0= locked, 1= unlocked, 2= current
        """
        if data is None:
            data= {}
        if "state" not in data:
            data["state"] = 1
        self.state = data["state"]
        if self.state == 0:
            idx= 1
            passer= None
        elif self.state == 1:
            idx= 0
            passer= 0
        else:
            idx= 0
            passer= 1

        if "next" not in data:
            data["next"] = {}
        self.next = data["next"]

        super().__init__(name= "L", breaks=[], data= {}) #Breaks which walls break the beam
        self.texture.newLayer(layer=0, name="base", textures=["menu/level.png", "disabledCells/0.png"], state={"index": idx, "direction": 0})
        self.texture.newLayer(layer=3, name="pass", textures=["menu/levelPass.png", "menu/levelDo.png"], state={"index": passer, "direction": 0})

    def changeDirection(self, direction): #Rotate Your Textures!
        # ej. self.texture.update("layerName", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        self.changeBeamStates(beamDirs=[From], color=color)
        if From is None and self.next == {}:
            return {}, True
        if self.state == 2:
            return {}, True
        else:
            return self.next, False
    
    def editProperty(self, index, changing):
        if index in self.next:
            if self.next[index] == [(10,0,0), (0,10,0), (0,0,10)][changing]:
                del self.next[index]
            else:
                self.next[index] = [(10,0,0), (0,10,0), (0,0,10)][changing]
        elif index in [0, 1, 2, 3]:
            self.next[index] = [(10,0,0), (0,10,0), (0,0,10)][changing]
        return True

    def getDifficulty(self):
        return self.difficulty

    def getData(self, pocket= False): #Data thats needed to be saved on level info
        data= super().getData()
        data["data"]= {
            "state": 0,
            "next": self.next,
            "level": ""
        }
        return data