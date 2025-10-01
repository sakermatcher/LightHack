import logging
from .texturing import *
from .default import default
from uuid import uuid4

class level(default):

    def __init__(self, data= None, **kwargs):
        """
        opens= levelDir
        state= 0= locked, 1= unlocked, 2= current
        """
        self.andOr= False #False= and, True= or
        if data is None:
            data= {}
        if "state" not in data:
            data["state"] = 1
        self.state = data["state"]
        if "unlocksWith" not in data:
            data["unlocksWith"] = 0 #number of inputs to unlock this level
        self.unlocksWith= data["unlocksWith"]
        if self.state == 0:
            idx= 1
            passer= None
        elif self.state == 1:
            idx= 0
            passer= 0
        else:
            idx= 0
            passer= 1
        if "level" not in data:
            self.levelID= str(uuid4())[:8]
        else:
            self.levelID= data["level"]

        self.stateChanger= 0


        if "next" not in data:
            data["next"] = {}
        self.next= {}
        for key, value in data["next"].items():
            self.next[int(key)]= value

        super().__init__(name= "L", breaks=[], data= {}) #Breaks which walls break the beam
        self.texture.newLayer(layer=0, name="base", textures=["menu/level.png", "disabledCells/0.png"], state={"index": idx, "direction": 0})
        self.texture.newLayer(layer=3, name="pass", textures=["menu/levelPass.png", "menu/levelDo.png"], state={"index": passer, "direction": 0})

        self.inputs= [False, False, False, False]

    def changeLight(self, From=None, color=None):
        if From is not None:
            self.inputs[From]= True
        if From is not None and color is not None and self.state == 0:
            total= 0
            for i in self.inputs:
                if i == True:
                    total += 1
            if self.unlocksWith <= total:
                self.state= 2
                self.texture.update("base", index=0)
                self.texture.update("pass", index=1)

        if self.state == 0:
            return {}, True
        elif self.state == 1:
            for i in self.next:
                self.changeBeamStates(beamDirs=[i], color= self.next[i])
            return self.next, False
        else:
            return {}, True
        
    def openLevel(self):
        return self.levelID
    
    def unlock(self):
        self.state= 1
        self.texture.update("base", index=0)
        self.texture.update("pass", index=0)
    
    def editProperty(self, index, changing): #0,1,2,3= next directions, 4= levelID, 5= unlock, 6= lock, 7= and, 8= or
        if index == 4:
            self.levelID= input("New Level ID: ")
            return True
        if index == 5:
            self.stateChanger= 2
            return True
        if index == 6:
            self.stateChanger= 0
            return True
        if index == 7:
            self.andOr= False
            return True
        if index == 8:
            self.andOr= True
            return True
        if index == 9:
            print("Inputs; 0,1,2,3: Direction, 4: LevelID, 5: Unlock, 6: Lock, 7: AND, 8: OR")
        if index in self.next:
            if self.next[index] == [(0,10,0), (0,0,10), (10,0,0)][changing]:
                del self.next[index]
            else:
                self.next[index] = [(0,10,0), (0,0,10), (10,0,0)][changing]
        elif index in [0, 1, 2, 3]:
            self.next[index] = [(0,10,0), (0,0,10), (10,0,0)][changing]
        return True

    def getData(self, pocket= False): #Data thats needed to be saved on level info
        self.unlocksWith= 0
        data= super().getData()
        if self.andOr:
            self.unlocksWith= 1
        else:
            print(self.inputs)
            for i in self.inputs:
                if i == True:
                    self.unlocksWith += 1
            
        data["data"]= {
            "state": self.stateChanger,
            "next": self.next,
            "unlocksWith": self.unlocksWith,
            "level": self.levelID
        }
        return data