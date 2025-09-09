import logging
from .texturing import *
from .default import default
from.indicator import indicatorRender, numbers

class final(default):

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "F", layout=None, data=None):
        """
        xy= (x,y)
        name= cell name
        layout= simple layout (if needed)
        data= dict with relevant data (direction, color, final.)
        """
        if data is None:
            data = {"direction": 0, "final": True, "color": (0,0,0)}
        if "final" not in data:
            data["final"]= True

        if "color" not in data:
            data["color"]= (0,0,0)
        
        if data["final"]:
            idx= 0
            breaks= [0,2,3]
        else:
            idx= None
            breaks= [0,2]

        self.color= data["color"]
        self.final= data["final"]
        self.isCompleated= False
        
        super().__init__(xy= xy, name= name, breaks=breaks, data= data) #Breaks which walls break the beam
        self.texture.newLayer(layer=3, name="final", textures=["final/main.png"], state={"index": 0, "direction": data["direction"]})
        self.texture.newLayer(layer=4, name="cover", textures=["final/cover.png"], state={"index": idx, "direction": data["direction"]})
        self.texture.newLayer(layer=5, name="led", textures=["final/off.png", "final/on.png"], state={"index": 0, "direction": data["direction"]})
        self.texture.newLayer(6, "screens", ["indicators/UL.png", "indicators/UR.png", "indicators/DL.png"], state={"index": -1})
        self.texture.newLayer(7, "colorR", numbers, state={"corner": "UL", "color": (255,50,50), "number": self.color[0]}, renderer=indicatorRender)
        self.texture.newLayer(8, "colorG", numbers, state={"corner": "UR", "color": (50,255,50), "number": self.color[1]}, renderer=indicatorRender)
        self.texture.newLayer(9, "colorB", numbers, state={"corner": "DL", "color": (50,180,255), "number": self.color[2]}, renderer=indicatorRender)
        

    def changeDirection(self, direction): #Rotate Your Textures!
        self.texture.update("final", direction=direction)
        self.texture.update("cover", direction=direction)
        self.texture.update("led", direction=direction)
        return super().changeDirection(direction)
    
    def editProperty(self, index:int, changing:int):
        """Edits the RGB (changing) color of the input based on the index.
        index (intensity of that channel) 0 = 10, None= 0, 1 = 1, 2 = 2, ...
        changing: R= 0, G= 1, B= 2
        """
        if index is not None:
            if index == 0:
                index = 10
            current = list(self.color)
            current[changing] = index
            self.color = tuple(current)
        else:
            current = list(self.color)
            current[changing] = 0
            self.color = tuple(current)
        self.texture.update("colorR", number=self.color[0])
        self.texture.update("colorG", number=self.color[1])
        self.texture.update("colorB", number=self.color[2])
        return True

    def changeLight(self, From=None, color=None):
        self.isCompleated= False
        self.texture.update("led", index=0)
        if color is None:
            color= (0,0,0)
        
        if self.final and From == self.convDir(1):
            if color[0] == self.color[0] and color[1] == self.color[1] and color[2] == self.color[2]:
                self.isCompleated= True
                self.texture.update("led", index=1)
        elif not self.final and (From == self.convDir(1) or From == self.convDir(3)):
            self.inputs[From]= color
            print("Printing")
            print(From, color)
            color1= tuple(min(10, self.inputs[self.convDir(1)][i] + max(0, self.inputs[self.convDir(3)][i] - self.color[i])) for i in range(3))
            color3= tuple(min(10, self.inputs[self.convDir(3)][i] + max(0, self.inputs[self.convDir(1)][i] - self.color[i])) for i in range(3))
            print(color1, color3)
            self.changeBeamStates(beamDirs=[self.convDir(1)], color= color1)
            self.changeBeamStates(beamDirs=[self.convDir(3)], color= color3)
            output= tuple(max(0, color[i] - self.color[i]) for i in range(3))
            color= tuple(min(10, self.inputs[self.convDir(1)][i] + self.inputs[self.convDir(3)][i]) for i in range(3))
            print(color, self.color)
            if color[0] >= self.color[0] and color[1] >= self.color[1] and color[2] >= self.color[2]:
                self.isCompleated= True
                self.texture.update("led", index=1)
            
            if output != (0,0,0):
                return {self.dirFrom[From]:output}, False
            else:
                return {}, True

        return super().changeLight(From, color)
    
    def flip(self):
        self.final= not self.final
        self.texture.update("cover", index=0 if self.final else None)
        return True

    def getData(self, pocket= False): #Data thats needed to be saved on level info
        data= super().getData()
        data["data"]= {
            "direction": self.direction,
            "final": self.final,
            "color": self.color
        }
        return data
    
