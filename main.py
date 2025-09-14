from play import LightHackGame
import pygame
from cells import cells
from cells.level import level
import json

tutTxt=[
    "Welcome to lightHack!, a puzzle game where you use light to win, you can see that there is a laser in the game with a certain power on Red, Green, and\nBlue ranging from 0-10 noted on the indicators in the corner of the laser, your objective is to get the needed power for the generator (you know how\nmuch you will need by its indicators), right now you have 1 mirror in your pocket which will bend light in 90 degrees. Use WASD to move your selection\nand click to place blocks. Right Click to remove blocks, R to rotate them, and E will show you the light on a specific cell.",
    "Here we have 5 power on the Red channel, but we need 10 to power the generator, the light lens empowers all channels passing through it by the number\non its indicator, you have to pass the light through the lens, because on its sides it will only break the beam",
    "Here we have 10 Blue and 10 Red on the laser, but we need 5 Blue and 5 Red, with the use of a dark lens, we can reduce the power of all channels by the\nnumber on its indicator, so we will pass the light through the dark lens to reduce both channels by 5",
    "The prism is a block that can be used to separate a light in its different channels by passing it through the prism on the multicolor section, here we have\n Yellow (Red and Green), but we only need Red, so we will pass the light through the prism and take the Red channel to the generator, note that\nthe prism has specific sides for each color, and one multicolor side so only a specific color can pass through each.",
    "The prism can also be used to combine different channels into one beam, here we have 10 Red and 10 Blue, but we need Magenta (Red and Blue), so we will\npass both beams through the prism to combine them into one, note that the prism has specific sides for each color, and one multicolor side.",
    "Here we will use one prism to separate the beam, then a lens to change just the Red channel and then another prism to combine the beam back together, so\nwe can get the needed power for the generator, you can use F to flip a prism (Red with Blue).",
    ""
]


class menu(LightHackGame):
    def __init__(self):
        super().__init__()
        self.save_data = json.load(open("save.json"))

    def makeLayout(self):
        self.bottom= []

    def placeCell(self, x, y):
        self.gameDisplay.blit(self.complexLayout[y][x].render(), (x*80, y*80 + 130))

    def placeBack(self, x, y):
        self.gameDisplay.blit(self.background, (x*80, y*80 + 130))

    def load(self):
        self.difficulties= json.load(open("save.json"))
        self.levelData= {
            "width": 10,
            "height": 10
        }
        pygame.init()
        self.gameDisplay = pygame.display.set_mode((1050, 1000))
        self.lastHeight, self.lastWidth = 1000, 1050
        self.min_height= 1000
        self.min_width= 1050
        self.background = pygame.Surface((80, 80))
        self.background.fill((25,25,0))
        pygame.display.set_caption("LightHack Menu")
        #self.button= pygame.image.load("assets/menu/button.png").convert_alpha()
        #self.active= pygame.image.load("assets/menu/active.png").convert_alpha()
        self.highlight= pygame.image.load("assets/menu/highlight.png").convert_alpha()
        self.highlight= pygame.transform.scale(self.highlight, (80, 80))
        self.finals= [cells["final"](xy=(0,0), name="F", data={"direction": 0, "color": (10,10,10)})]

        self.complexLayout= []
        for y in range(10):
            self.complexLayout.append([])
            for x in range(10):
                if y != 0 and y % 4 == 0 and x == 1:
                    self.complexLayout[y].append(cells["mirror"](xy=(x,y), name="M0", data={"direction": 1}))
                elif y != 0 and (y + 2) % 4 == 0 and x == 8:
                    self.complexLayout[y].append(cells["mirror"](xy=(x,y), name="M1", data={"direction": 0}))
                else:
                    self.complexLayout[y].append(cells["default"](xy=(x,y), name="D", data=self.cellData["D"]["data"]))

        self.calculate()
        pygame.display.flip()


    def play(self):
        pastCol = None
        pastRow = None
        out = False
        while not out:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                out= self.keyHandler(event)
                if out:
                    break

            # ---------- CELL HIGHLIGHT -------------
            mouseX, mouseY = pygame.mouse.get_pos()
            col, row = mouseX // 80, (mouseY - 130) // 80
            if col >= 0 and row >= 0 and col < self.levelData["width"] and row < self.levelData["height"]:
                if (col, row) != (pastCol, pastRow):
                    if pastCol is not None and pastRow is not None:
                        self.placeBack(pastCol, pastRow)
                        self.placeCell(pastCol, pastRow)
                    pastCol, pastRow = col, row
                    self.gameDisplay.blit(self.highlight, (col * 80, row * 80 + 130))
                    self.placeCell(col, row)
            elif pastCol is not None and pastRow is not None:
                self.placeBack(pastCol, pastRow)
                self.placeCell(pastCol, pastRow)
                pastCol, pastRow = None, None

            if (self.lastWidth, self.lastHeight) != self.gameDisplay.get_size():
                cur_width, cur_height = self.gameDisplay.get_size()
                new_width = max(cur_width, self.min_width)
                new_height = max(cur_height, self.min_height)
                if (cur_width, cur_height) != (new_width, new_height):
                    self.gameDisplay = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                self.lastWidth, self.lastHeight = self.gameDisplay.get_size()
                for y in range(self.levelData["height"]):
                    for x in range(self.levelData["width"]):
                        self.placeBack(x, y)
                        self.placeCell(x, y)
                pygame.draw.rect(
                    self.gameDisplay, (0, 75, 85),
                    (self.levelData["width"] * 80, 0, self.levelData["width"] + 5, self.levelData["height"] * 80)
                )
                self.drawPocketCells()

            pygame.display.update()

if __name__ == "__main__":
    game = menu()
    game.load()
    game.play()

if __name__ == "":
    while True:
        pygame.init()
        menu= pygame.display.set_mode((1000,800))
        pygame.display.set_caption("LightHack Tutorials")
        font= pygame.font.Font(None, 40)
        text= font.render("Press T for tutorials, or click to play levels", True, (255,255,255))
        menu.fill((0,0,0))
        menu.blit(text, (100,380))
        out= None
        while out is None:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        out= "tut"
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    out= "lvl"
                    break
            pygame.display.flip()

        pygame.quit()
        if out == "tut":
            for i in range(1, 7):
                game = LightHackGame()
                game.load(f"tutorials/tut{i}")
                game.gameDisplay= pygame.display.set_mode((game.min_width, game.min_height + 130))
                pygame.display.set_caption(f"LightHack Tutorial {i}")
                font= pygame.font.Font(None, 26)
                for j, txt in enumerate(tutTxt[i-1].split("\n")):
                    text= font.render(txt, True, (50,200,255))
                    game.gameDisplay.blit(text, (10, game.min_height + 10 + j * 20))
                game.play()
        elif out == "lvl":
            for i in ["lvlEz1", "a", "lvlHard1"]:
                game = LightHackGame()
                game.load(i)
                game.play()
