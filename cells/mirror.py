from .texturing import *
from .default import default

class mirror(default):

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "M", layout=None, data=None):
        """
        xy= (x,y)
        name= cell name
        layout= simple layout (if needed)
        data= dict with relevant data (direction, color, etc.)
        """
        if data is None:
            data = {"direction": 0}
        super().__init__(xy= xy, name= name, breaks=[], data= data) #Breaks which walls break the beam 
        self.texture.newLayer(layer=3, name="mirror", textures=["others/mirror.png"], state={"index": 0, "direction": self.direction})

    def changeDirection(self, direction): #Rotate Your Textures!
        direction= [1,0][self.direction]
        self.texture.update("mirror", direction=direction)
        return super().changeDirection(direction)

    def changeLight(self, From=None, color=None):
        if From is None:
            end= {}
            for i in range(4):
                if self.inputs[i] != (0,0,0):
                    self.changeLight(i, self.inputs[i])
                    end[[[3,2,1,0],[1,0,3,2]][self.direction][i]]= color
            return end.copy(), False
        else:
            if color is None:
                color=(0,0,0)
            self.inputs[From] = color

            Color= tuple(min(10, color[i] + self.inputs[[[3,2,1,0],[1,0,3,2]][self.direction][From]] [i]) for i in range(3))
            match From:
                case 0:
                    self.changeBeamStates(vertical=True, colorA= Color)
                case 1:
                    self.changeBeamStates(vertical=False, colorA= Color)
                case 2:
                    self.changeBeamStates(vertical=True, colorB= Color)
                case 3:
                    self.changeBeamStates(vertical=False, colorB= Color)
                

            match self.direction:
                case 0:
                    match From:
                        case 0:
                            self.changeBeamStates(vertical=False, colorB= Color)
                        case 1:
                            self.changeBeamStates(vertical=True, colorB= Color)
                        case 2:
                            self.changeBeamStates(vertical=False, colorA= Color)
                        case 3:
                            self.changeBeamStates(vertical=True, colorA= Color)

                case 1:
                    match From:
                        case 0:
                            self.changeBeamStates(vertical=False, colorA= Color)
                        case 1:
                            self.changeBeamStates(vertical=True, colorA= Color)
                        case 2:
                            self.changeBeamStates(vertical=False, colorB= Color)
                        case 3:
                            self.changeBeamStates(vertical=True, colorB= Color)

            return {[[3,2,1,0],[1,0,3,2]][self.direction][From]:color}, False
        
    def getData(self): #Data thats needed to be saved on level info
        data= super().getData()
        data["data"]= {
            "direction": self.direction
        }
        return data