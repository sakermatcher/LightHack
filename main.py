from play import LightHackGame
import pygame
from cells import cells
from cells.level import level
from cells.indicator import numbers
import json

tutTxt=[
    "Welcome to lightHack!, a puzzle game where you use light to win, you can see that there is a laser in the game with a certain power on Red, Green, and\nBlue ranging from 0-10 noted on the indicators in the corner of the laser, your objective is to get the needed power for the generator (you know how\nmuch you will need by its indicators), right now you have 1 mirror in your pocket which will bend light in 90 degrees. Use WASD to move your selection\nand click to place blocks. Right Click to remove blocks, R to rotate them, and E will show you the light on a specific cell.",
    "Here we have 5 power on the Red channel, but we need 10 to power the generator, the light lens empowers all channels passing through it by the number\non its indicator, you have to pass the light through the lens, because on its sides it will only break the beam",
    "Here we have verious mirrors and a lens, use the mirrors to bend the light to the lens, and then use the lens to empower the light to the needed power\nfor the generator, you can select things from your pocket (on the right) by clicking on them, or move your selection by using WASD.",
    "Here we have 10 Blue and 10 Red on the laser, but we need 5 Blue and 5 Red, with the use of a dark lens, we can reduce the power of all channels by the\nnumber on its indicator, so we will pass the light through the dark lens to reduce both channels by 5",
    "The prism is a block that can be used to separate a light in its different channels by passing it through the prism on the multicolor section, here we have\n Yellow (Red and Green), but we only need Red, so we will pass the light through the prism and take the Red channel to the generator, note that\nthe prism has specific sides for each color, and one multicolor side so only a specific color can pass through each.",
    "The prism can also be used to combine different channels into one beam, here we have 10 Red and 10 Blue, but we need Magenta (Red and Blue), so we will\npass both beams through the prism to combine them into one, note that the prism has specific sides for each color, and one multicolor side.",
    "Here we will use one prism to separate the beam, then a lens to change just the Green channel and then place another prism to combine the beam back\ntogether, so we can get the needed power for the generator, use F to flip a prism (Red with Blue)."
]


class menu(LightHackGame): # Final menu class for playing levels and tutorials
    def __init__(self):
        super().__init__()
        self.load("bak")
        super().calculate()
        pygame.display.set_caption(f"Light Hack - Menu")
        #Darken the screen
        darken= pygame.Surface((self.min_width, self.min_height))
        darken.set_alpha(100)
        darken.fill((0,0,0))
        self.gameDisplay.blit(darken, (0,0))
        #Write "Light Hack" in the middle of the screen
        font= pygame.font.Font(None, 100)
        text1= font.render("Light Hack", True, (50,200,255))
        self.gameDisplay.blit(text1, (self.min_width//2 - text1.get_width()//2, self.min_height//2 - text1.get_height()//2 - 100))
        #Write "Click to Play" below
        text2= font.render("Click to Play", True, (50,200,255))
        self.gameDisplay.blit(text2, (self.min_width//2 - text2.get_width()//2, self.min_height//2 - text2.get_height()//2))
        pygame.display.update()
        # Wait for a click to continue

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return
                elif (self.lastWidth, self.lastHeight) != self.gameDisplay.get_size():
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

                    self.gameDisplay.blit(darken, (0,0))
                    self.gameDisplay.blit(text1, (self.min_width//2 - text1.get_width()//2, self.min_height//2 - text1.get_height()//2 - 100))
                    self.gameDisplay.blit(text2, (self.min_width//2 - text2.get_width()//2, self.min_height//2 - text2.get_height()//2))

                    pygame.display.update()
            
        
    def calculate(self):
        for y in range(len(self.complexLayout)):
            for x in range(len(self.complexLayout[0])):
                self.complexLayout[y][x].restart()

        for y in range(len(self.complexLayout)):
            for x in range(len(self.complexLayout[0])):
                if self.simpleLayout[y][x] == "L0":
                    newLights, rtrn = self.complexLayout[y][x].changeLight()
                    if rtrn is not True:
                        for Dir, color in newLights.items():
                            self.beam(x, y, Dir, color)
                self.placeBack(x, y)
                self.placeCell(x, y)

        pygame.display.update()

    def keyHandler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            mouseX, mouseY = pygame.mouse.get_pos()
            x, y = (mouseX - self.offsetX) // 80, (mouseY - self.offsetY) // 80
            if event.button == 1:
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    if self.complexLayout[y][x].name == "L":
                        if self.complexLayout[y][x].state in [1, 2]:
                            lvl= self.complexLayout[y][x].openLevel()
                            if lvl[0] == "t":
                                playing= LightHackGame()
                                pygame.display.quit()
                                pygame.quit()
                                tutNum= int(lvl[1:])
                                playing.load(f"{self.levelName}/{lvl}", startSize=(self.lastWidth, self.lastHeight), texts= tutTxt[tutNum-1].split("\n"))
                                if playing.play() == "win":
                                    at= self.simpleLayout[y][x]
                                    self.levelData["cells"][at]["data"]["state"] = 1
                                    with open(f"levels/{self.levelName}.json", "w") as f:
                                        json.dump(self.levelData, f, indent=4)
                                self.load(self.levelName, (playing.lastWidth, playing.lastHeight))
                            else:
                                playing= LightHackGame()
                                pygame.display.quit()
                                pygame.quit()
                                playing.load(f"{self.levelName}/{lvl}", startSize=(self.lastWidth, self.lastHeight))
                                if playing.play() == "win":
                                    at= self.simpleLayout[y][x]
                                    self.levelData["cells"][at]["data"]["state"] = 1
                                    with open(f"levels/{self.levelName}.json", "w") as f:
                                        json.dump(self.levelData, f, indent=4)
                                self.load(self.levelName, (playing.lastWidth, playing.lastHeight))
                        self.calculate()

        return False

    def load(self, levelName, startSize=(0, 0)):
        try:
            self.levelData = json.load(open(f"levels/{levelName}.json", "r"))
        except FileNotFoundError:
            print("Level not found")
            return

        pygame.init()
        # --- MUSIC ---
        pygame.mixer.init()
        pygame.mixer.music.load("assets/lightHackV1.mp3")
        pygame.mixer.music.play(-1)  # Loop indefinitely
        # --- END MUSIC ---
        self.levelName= levelName
        self.min_width = self.levelData["width"] * 80 + 66
        self.min_height = self.levelData["height"] * 80 + 66
        self.offsetX = (max(startSize[0], self.min_width) - self.min_width) // 2 + 33
        self.offsetY = (max(startSize[1], self.min_height) - self.min_height) // 2 + 33
        self.gameDisplay = pygame.display.set_mode((max(self.min_width, startSize[0]), max(self.min_height, startSize[1])), pygame.RESIZABLE)
        pygame.display.set_caption(f"Light Hack")
        # Load and scale background textures
        self.borderC = pygame.image.load("assets/border/corner.png").convert_alpha()
        self.borderS = pygame.image.load("assets/border/side.png").convert_alpha()
        self.background = pygame.image.load("assets/background.png")
        self.background = pygame.transform.scale(self.background, (80, 80))
        self.highlight = pygame.image.load("assets/menu/highlight.png").convert_alpha()
        self.highlight = pygame.transform.scale(self.highlight, (80, 80))
        self.lastWidth, self.lastHeight = self.gameDisplay.get_size()

        self.simpleLayout = self.levelData["layout"]
        self.cellData = self.levelData["cells"]
        cells["level"]= level
        self.pocket = self.levelData["pocket"]
        self.complexLayout = []
        self.finals= []

        for y, row in enumerate(self.simpleLayout):
            self.complexLayout.append([])
            for x, cell in enumerate(row):
                self.complexLayout[y].append(
                    cells[self.cellData[cell]["type"]](
                        xy=(x, y),
                        name=cell,
                        layout=self.simpleLayout,
                        data=self.cellData[cell]["data"]
                    )
                )
                if cell[0] == "F":
                    self.finals.append(self.complexLayout[y][-1])

        self.gameDisplay.fill((0, 75, 85))

        self.makeGradient()
        self.makeBorder()

        # Draw initial cells
        for y in range(self.levelData["height"]):
            for x in range(self.levelData["width"]):
                self.placeBack(x, y)
                self.placeCell(x, y)

        for y in range(len(self.simpleLayout)):
            for x in range(len(self.simpleLayout[0])):
                if self.simpleLayout[y][x] == "L0":
                    newLights, rtrn = self.complexLayout[y][x].changeLight()
                    if rtrn is not True:
                        for Dir, color in newLights.items():
                            self.beam(x, y, Dir, color)


                        self.beam(x, y, Dir, color)

        pygame.display.update()

    def play(self):
        pastCol = None
        pastRow = None
        out = False
        while not out:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                        out = True
                    out= self.keyHandler(event)
                    if out:
                        break
            except SystemError:
                pass

            # ---------- CELL HIGHLIGHT -------------
            mouseX, mouseY = pygame.mouse.get_pos()
            col, row = (mouseX - self.offsetX) // 80, (mouseY - self.offsetY) // 80
            if col >= 0 and row >= 0 and col < self.levelData["width"] and row < self.levelData["height"]:
                if (col, row) != (pastCol, pastRow):
                    if pastCol is not None and pastRow is not None:
                        self.placeBack(pastCol, pastRow)
                        self.placeCell(pastCol, pastRow)
                    pastCol, pastRow = col, row
                    if self.complexLayout[row][col].name == "L":
                        if self.complexLayout[row][col].state in [1, 2]:
                            self.gameDisplay.blit(self.highlight, (col * 80 + self.offsetX, row * 80 + self.offsetY))
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
                self.offsetX = (self.lastWidth - self.min_width) // 2 + 33
                self.offsetY = (self.lastHeight - self.min_height) // 2 + 33
                self.makeGradient()
                self.makeBorder()
                for y in range(self.levelData["height"]):
                    for x in range(self.levelData["width"]):
                        self.placeBack(x, y)
                        self.placeCell(x, y)
            pygame.display.update()
if __name__ == "__main__":
    game = menu()
    game.load("section1")
    game.play()