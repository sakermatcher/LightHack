import logging
from .texturing import *
from .default import default

class block(default):
    def __init__(self, xy: tuple[int, int]|None = None, name: str = "X", layout=None, data=None):
        self.texture= texturing()
        super().__init__(xy= xy, name= name, breaks=[0,1,2,3], data= data)
        sorroundings= []
        if layout is not None and xy is not None:
            for i, (dx, dy) in enumerate([(0, -1), (1, 0), (0, 1), (-1, 0)]): #N, E, S, W
                if 0 <= xy[1]+dy < len(layout) and 0 <= xy[0]+dx < len(layout[0]):
                    if layout[xy[1]+dy][xy[0]+dx] == "X":
                        sorroundings.append(i)
            match len(sorroundings):
                case 0:
                    self.texture.newLayer(0, "base", ["disabledCells/0.png"])
                case 1:
                    self.texture.newLayer(0, "base", ["disabledCells/1.png"])
                    dir= [0,3,2,1][sorroundings[0]]
                    self.texture.update("base", direction=dir)
                case 2:
                    if sum(sorroundings)%2 == 0:
                        self.texture.newLayer(0, "base", ["disabledCells/2I.png"])
                        if sorroundings[0] == 1:
                            self.texture.update("base", direction=1)
                        else:
                            self.texture.update("base", direction=0)
                    else:
                        self.texture.newLayer(0, "base", ["disabledCells/2L.png"])
                        match sorroundings:
                            case [0, 1]:
                                self.texture.update("base", direction=0)
                            case [1, 2]:
                                self.texture.update("base", direction=3)
                            case [2, 3]:
                                self.texture.update("base", direction=2)
                            case [0, 3]:
                                self.texture.update("base", direction=1)
                case 3:
                    self.texture.newLayer(0, "base", ["disabledCells/3.png"])
                    match sorroundings:
                        case [0, 1, 3]:
                            self.texture.update("base", direction=0)
                        case [0, 2, 3]:
                            self.texture.update("base", direction=1)
                        case [1, 2, 3]:
                            self.texture.update("base", direction=2)
                        case [0, 1, 2]:
                            self.texture.update("base", direction=3)
                case 4:
                    self.texture.newLayer(0, "base", ["disabledCells/4.png"])

        else:
            self.texture.newLayer(0, "base", ["disabledCells/0.png"])

        #logging.log(50, f"Empty cell created at {self.xy}, sorroundings: {sorroundings}")