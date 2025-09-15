import logging
from .texturing import *
from .indicator import numbers
from math import ceil

logging.addLevelName(60, "LIGHTNING")
logging.basicConfig(level=60, format='%(asctime)s - %(levelname)s - %(message)s')

class default():
    dirFrom= [2,3,0,1]
    def beamRenderer(self, layer:dict):
        """
        Renders the beam texture.
        \n--STATE--
        \n colorA : (int, int, int)
        \n colorB : (int, int, int)
        \n breakA : bool
        \n breakB : bool
        \n vertical : bool
        """
        state= layer["state"]
        final = surface.Surface((40,40), SRCALPHA)

        if state["colorA"] != (0,0,0):
            if state["breakA"]:
                finalA = layer["textures"][2]
            else:
                finalA = layer["textures"][0]
            final.blit(multiply(finalA, state["colorA"]), (0, 0))

        if state["colorB"] != (0,0,0):
            if state["breakB"]:
                finalB = layer["textures"][3]
            else:
                finalB = layer["textures"][1]
            final.blit(multiply(finalB, state["colorB"]), (0, 0))
        
        if state["vertical"]:
            final = transform.rotate(final, 270)
        
        return final
    
    def overlayRenderer(self, layer:dict):
        if layer["state"]["show"]:
            final = layer["textures"][-1].copy()

            imgs= layer["textures"]

            color0= layer["state"]["stateY"]["colorA"]
            color1= layer["state"]["stateX"]["colorA"]
            color2= layer["state"]["stateY"]["colorB"]
            color3= layer["state"]["stateX"]["colorB"]

            coordsh= (13,18,23)
            coordsv= (11,17,23)
            commons= (5,30,6,30)


            for i, color in enumerate([color0, color2, color1, color3]):
                for j, rgb in enumerate(color):
                    rgb = ceil((rgb / 25.5 - 3 * int(bool(rgb))) * 1.428571)
                    if i < 2:
                        final.blit(multiply(imgs[rgb], ((255,50,50)[j], (50,255,180)[j], (50,50,255)[j])), (coordsh[j], commons[i]))
                    else:
                        final.blit(multiply(imgs[rgb], ((255,50,50)[j], (50,255,180)[j], (50,50,255)[j])), (commons[i], coordsv[j]))

            return final
        else:
            return surface.Surface((40,40), SRCALPHA)

    def __init__(self, xy: tuple[int, int]|None = None, name:str="D", breaks=None, layout=None, data=None):
        self.texture= texturing()
        self.xy = xy
        self.name = name
        if data is None or data == {}:
            data= {"direction":0}
        self.direction= data["direction"]
        self.inputs= [(0,0,0), (0,0,0), (0,0,0), (0,0,0)]
        self.stateX= {"colorA": (0, 0, 0), "colorB": (0, 0, 0), "breakA": False, "breakB": False, "vertical": False}
        self.stateY= {"colorA": (0, 0, 0), "colorB": (0, 0, 0), "breakA": False, "breakB": False, "vertical": True}
        if name != "D":
            self.texture.newLayer(layer=0, name="base", textures=["cell.png"])
        self.texture.newLayer(layer=2, name="beamV", textures=["beams/beamA.png", "beams/beamB.png", "beams/breakA.png", "beams/breakB.png"], renderer=self.beamRenderer, state=self.stateY)
        self.texture.newLayer(layer=1, name="beamH", textures=["beams/beamA.png", "beams/beamB.png", "beams/breakA.png", "beams/breakB.png"], renderer=self.beamRenderer, state=self.stateX)
        self.texture.newLayer(layer=20, name="overlay", textures= numbers + ["indicators/overlay.png"], state={"show": False, "stateX": self.stateX, "stateY": self.stateY}, renderer=self.overlayRenderer)
        self.breaks= breaks if breaks is not None else []

    def changeDirection(self, direction: int):
        self.direction = direction

    def editProperty(self, index:int, changing:int):
        return False

    def getData(self, pocket=False):
        if pocket:
            return {
                "type": self.__class__.__name__.lower(),
                "data": {
                    "direction": 0
                }
            }
        
        return {
            "type": self.__class__.__name__.lower(),
            "data": {
                "direction": self.direction
            }
        }
    
    def changeBeamStates(self, vertical=False, beamDirs=None, **states):
        if beamDirs is None:
            if vertical:
                for key, value in states.items():
                    if key in ["colorA", "colorB"]:
                        self.stateY[key]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value) #Channel intensity (ej.R)= R/2 + 5 * int(bool(R))  This is so that 0 is 0 but 1 will be 5 up to 10 that is 10, after that we multiply by 25.5 to get R/255
                    elif key in self.stateY:
                        self.stateY[key]= value
            else:
                for key, value in states.items():
                    if key in ["colorA", "colorB"]:
                        self.stateX[key]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                    elif key in self.stateX:
                        self.stateX[key]= value
        else:
            for i in beamDirs:
                match i:
                    case 0:
                        for key, value in states.items():
                            if key == "color":
                                self.stateY["colorA"]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                            else:
                                self.stateY[key]= value
                    case 1:
                        for key, value in states.items():
                            if key == "color":
                                self.stateX["colorA"]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                            else:
                                self.stateX[key] = value
                    case 2:
                        for key, value in states.items():
                            if key == "color":
                                self.stateY["colorB"]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                            else:
                                self.stateY[key]= value
                    case 3:
                        for key, value in states.items():
                            if key == "color":
                                self.stateX["colorB"]= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in value)
                            else:
                                self.stateX[key]= value
    
    def convDir(self, wantedDir):
        return [[0,1,2,3],[1,2,3,0],[2,3,0,1],[3,0,1,2]][self.direction][wantedDir]

    def checkBreak(self, From):
        breaks= []
        for b in self.breaks:
            b+= self.direction
            if b > 3:
                b -= 4
            breaks.append(b)

        if From in breaks: #If light has a break on location
            match From:
                case 0 | 2:
                    beam= True
                case 1 | 3:
                    beam= False
            match From:
                case 0 | 1:
                    self.changeBeamStates(beam, breakA=True)
                case 3 | 2:
                    self.changeBeamStates(beam, breakB=True)

            return True
        
        if [2, 3, 0, 1][From] in breaks: #If light has a break opossite of location
            return True
        
        return False
    
    def restart(self):
        self.inputs= [(0,0,0), (0,0,0), (0,0,0), (0,0,0)]
        self.changeBeamStates(True, colorA= (0,0,0), colorB=(0,0,0), breakA= False, breakB= False)
        self.changeBeamStates(False, colorA= (0,0,0), colorB=(0,0,0), breakA= False, breakB= False)

    def changeLight(self, From, color=None):
        if color is None:
            color=(0,0,0)
        self.inputs[From] = color

        if From in [0, 2]: #Light is vertical
            Break= self.checkBreak(From)
            if Break:
                #If it breaks make separate beams for A and B
                match From:
                    case 0:
                        colorA= color
                        self.changeBeamStates(colorA= colorA, vertical=True)
                    case 2:
                        colorB= color
                        self.changeBeamStates(colorB=colorB, vertical=True)
            else:
                #If it doesnt add light inputs
                Color= tuple(min(10, color[i] + self.inputs[self.dirFrom[From]][i]) for i in range(3))
                colorA= Color
                colorB= Color
                self.changeBeamStates(colorA= colorA, colorB=colorB, vertical=True)

        else:
            Break= self.checkBreak(From)
            if Break:
                #If it breaks make separate beams for A and B
                match From:
                    case 1:
                        colorA= color
                        self.changeBeamStates(vertical=False, colorA= colorA)
                    case 3:
                        colorB= color
                        self.changeBeamStates(vertical=False, colorB=colorB)
            else:
                #If it doesnt add light inputs
                Color= tuple(min(10, color[i] + self.inputs[self.dirFrom[From]][i]) for i in range(3))
                colorA= Color
                colorB= Color
                self.changeBeamStates(vertical=False, colorA= colorA, colorB=colorB)
        
        
        return {From:color}, Break
    
    def __eq__(self, other):
        if self.name == "D":
            return "D" == other
        else:
            return self.name[0].upper() == other

    def convert(self, other:object, name=None, layout= None, data= None):
        if data is not None:
            data= data.copy()
        new= other(xy= self.xy, name=name, layout= layout, data= data)
        new.inputs= self.inputs.copy()
        return new
    
    def flip(self):
        return False

    def render(self,overlay=False, scale= (80, 80)):
        if overlay:
            self.texture.update("overlay", show= True)
            final= transform.scale(self.texture.render(), scale)
            self.texture.update("overlay", show= False)
            return final

        return transform.scale(self.texture.render(), scale)
    
