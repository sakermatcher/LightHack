import logging
from .texturing import *
from .default import default

class prism(default):

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "P", layout=None, data=None):
        """
        xy= (x,y)
        name= cell name
        layout= simple layout (if needed)
        data= dict with relevant data (direction, flipped)
        """
        if data is None:
            data = {"direction": 0, "flipped": False}
        super().__init__(xy= xy, name= name, breaks=[], data= data) #Breaks which walls break the beam 
        self.texture.newLayer(layer=3, name="prism", textures=["prism/normal.png", "prism/flipped.png"], state={"index": 0, "direction": data["direction"]})
        self.pastOutput= (0,0,0)
        if "flipped" not in data:
            data["flipped"]= False
        if data["flipped"] == True:
            self.flipped= False
            self.flip()
        else:
            self.flipped= False

    def changeDirection(self, direction): #Rotate Your Textures!
        self.texture.update("prism", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        if color is None:
            color= (0,0,0)
        
        self.inputs[From]= color
        if not self.flipped:
            colors= tuple(min(10, self.inputs[self.convDir(3 - i)][i] + self.inputs[self.convDir(0)][i] ) for i in range(3))
            colorRside= (colors[0], self.inputs[self.convDir(3)][1], self.inputs[self.convDir(3)][2])
            colorGside= (self.inputs[self.convDir(2)][0], colors[1],self.inputs[self.convDir(2)][2])
            colorBside= (self.inputs[self.convDir(1)][0],self.inputs[self.convDir(1)][1], colors[2])
            self.changeBeamStates(beamDirs=[self.convDir(3)], color= colorRside)
            self.changeBeamStates(beamDirs=[self.convDir(2)], color= colorGside)
            self.changeBeamStates(beamDirs=[self.convDir(1)], color= colorBside)
            self.changeBeamStates(beamDirs=[self.convDir(0)], color= colors)

        else:
            colors= tuple(min(10, self.inputs[self.convDir(i + 1)][i] + self.inputs[self.convDir(0)][i] ) for i in range(3))
            colorRside= (colors[0], self.inputs[self.convDir(1)][1], self.inputs[self.convDir(1)][2])
            colorGside= (self.inputs[self.convDir(2)][0], colors[1],self.inputs[self.convDir(2)][2])
            colorBside= (self.inputs[self.convDir(3)][0],self.inputs[self.convDir(3)][1], colors[2])
            self.changeBeamStates(beamDirs=[self.convDir(1)], color= colorRside)
            self.changeBeamStates(beamDirs=[self.convDir(2)], color= colorGside)
            self.changeBeamStates(beamDirs=[self.convDir(3)], color= colorBside)
            self.changeBeamStates(beamDirs=[self.convDir(0)], color= colors)

    
        if From == self.direction: #If the beam is being separated
            if not self.flipped:
                return {self.convDir(3):(colors[0], 0, 0), self.convDir(2):(0, colors[1], 0), self.convDir(1):(0, 0, colors[2])}, False
            else:
                return {self.convDir(1):(colors[0], 0, 0), self.convDir(2):(0, colors[1], 0), self.convDir(3):(0, 0, colors[2])}, False
        
        else: #If beam is being combined
            if not self.flipped:
                outColor=tuple(self.inputs[self.convDir(3 - i)][i] for i in range(3))
                if outColor == self.pastOutput:
                    return {}, True
                else:
                    return {self.convDir(0):outColor}, False
            else:
                outColor=tuple(self.inputs[self.convDir(i + 1)][i] for i in range(3))
                if outColor == self.pastOutput:
                    return {}, True
                else:
                    return {self.convDir(0):outColor}, False

    def restart(self):
        super().restart()

    def flip(self):
        self.texture.update("prism", index=1 if not self.flipped else 0)
        self.flipped= not self.flipped
        return True

    def getData(self): #Data thats needed to be saved on level info
        data= super().getData()
        data["data"]= {
            "direction": self.direction,
            "flipped": False
        }
        return data