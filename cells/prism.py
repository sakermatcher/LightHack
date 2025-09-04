import logging
from .texturing import *
from .default import default

class prism(default):

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "P", layout=None, data=None):
        """
        xy= (x,y)
        name= cell name
        layout= simple layout (if needed)
        data= dict with relevant data (direction, color, etc.)
        """
        if data is None:
            data = {"color": (0,0,0), "direction": 0}
        super().__init__(xy= xy, name= name, breaks=[], data= data) #Breaks which walls break the beam 
        self.texture.newLayer(layer=3, name="prism", textures=["others/prism.png"], state={"index": 0, "direction": data["direction"]})
        self.pastOutput= (0,0,0)

    def changeDirection(self, direction): #Rotate Your Textures!
        self.texture.update("prism", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        if color is None:
            color= (0,0,0)
        
        self.inputs[From]= color
        colors= tuple(min(10, self.inputs[self.convDir(3 - i)][i] + self.inputs[self.convDir(0)][i] ) for i in range(3))

        colorRside= (colors[0], self.inputs[self.convDir(3)][1], self.inputs[self.convDir(3)][2])
        colorGside= (self.inputs[self.convDir(2)][0], colors[1],self.inputs[self.convDir(2)][2])
        colorBside= (self.inputs[self.convDir(1)][0],self.inputs[self.convDir(1)][1], colors[2])

        self.changeBeamStates(beamDirs=[self.convDir(3)], color= colorRside)
        self.changeBeamStates(beamDirs=[self.convDir(2)], color= colorGside)
        self.changeBeamStates(beamDirs=[self.convDir(1)], color= colorBside)
        self.changeBeamStates(beamDirs=[self.convDir(0)], color= colors)
    
        if From == self.direction: #If the beam is being separated
            return {self.convDir(3):(colors[0], 0, 0), self.convDir(2):(0, colors[1], 0), self.convDir(1):(0, 0, colors[2])}, False
        
        else: #If beam is being combined
            outColor=tuple(self.inputs[self.convDir(3 - i)][i] for i in range(3))
            if outColor == self.pastOutput:
                return {}, True
            else:
                return {self.convDir(0):outColor}, False

    def restart(self):
        super().restart()

    def getData(self): #Data thats needed to be saved on level info
        data= super().getData()
        data["data"]= {
            "direction": self.direction
        }
        return data