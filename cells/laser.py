import logging
from .texturing import *
from .default import default
from .indicator import indicatorRender, numbers

class laser(default):
    def renderLaser(self, layer:dict):
        """
        Renders the laser light.
        """
        state= layer["state"]
        logging.log(50, f"Laser render called with state: {layer['state']}")

        if state["color"] != (0,0,0): #Multiply state["color"] by 25.5 to get 0-255 range
            color= tuple(int((c/1.428571+3*int(bool(c)))*25.5)for c in state["color"])
            final = multiply(layer["textures"][0], color)
            final = transform.rotate(final, [0,90,180,270][state["direction"]])
            return final
        return surface.Surface((40,40), SRCALPHA)

    def __init__(self, xy: tuple[int, int]|None = None, name: str = "L", layout=None, data=None):
        if data is None:
            data = {"color": (0,0,0), "direction": 0}
        super().__init__(xy= xy, name= name, breaks=[1,2,3], data= data)
        self.texture.newLayer(3, "Laser", ["laser/main.png"], state={"index": 0, "direction": data["direction"]})
        self.texture.newLayer(4, "Light", ["laser/light.png"], renderer=self.renderLaser, state={"color": data["color"], "direction": data["direction"]})
        self.texture.newLayer(5, "screens", ["indicators/UL.png", "indicators/UR.png", "indicators/DL.png"], state={"index": None})
        self.color = tuple(data["color"])
        self.texture.newLayer(6, "colorR", numbers, state={"corner": "UL", "color": (255,50,50), "number": self.color[0]}, renderer=indicatorRender)
        self.texture.newLayer(7, "colorG", numbers, state={"corner": "UR", "color": (50,255,50), "number": self.color[1]}, renderer=indicatorRender)
        self.texture.newLayer(8, "colorB", numbers, state={"corner": "DL", "color": (50,180,255), "number": self.color[2]}, renderer=indicatorRender)
        self.texture.update("Light", color=self.color, direction=self.direction)

    def changeDirection(self, direction):
        self.texture.update("Laser", direction=direction)
        self.texture.update("Light", direction=direction)
        return super().changeDirection(direction)

    def changeColor(self, color):
        self.color = color
        self.texture.update("Light", color=color)

    def changeLight(self, From=None, color=None):
        if From is not None:
            return super().changeLight(From, color)
        else:
            return self.direction, self.color 

    def getData(self):
        data= super().getData()
        data["data"]= {
            "direction": self.direction,
            "color": self.color
        }
        return data