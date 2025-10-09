from play import LightHackGame
import pygame
from cells import cells
from cells.level import level
from cells.indicator import numbers
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


class menu(LightHackGame): # Final menu class for playing levels and tutorials
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
            x, y = mouseX // 80, mouseY // 80
            if event.button == 1:
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    if self.complexLayout[y][x].name == "L":
                        self.complexLayout[y][x].unlock()
                        self.calculate()

        return False

    def load(self, levelName):
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
        self.min_width = self.levelData["width"] * 80
        self.min_height = self.levelData["height"] * 80
        self.gameDisplay = pygame.display.set_mode((self.min_width, self.min_height), pygame.RESIZABLE)
        self.background = pygame.image.load("assets/background.png")
        self.backgroundPocket = pygame.transform.scale(self.background, (160, 160))
        self.background = pygame.transform.scale(self.background, (80, 80))
        self.qty = pygame.image.load("assets/indicators/qty.png").convert_alpha()
        self.numbers= tuple(pygame.image.load(f"assets/{i}").convert_alpha() for i in numbers)
        highlight = pygame.image.load("assets/menu/highlight.png").convert_alpha()
        self.highlight = pygame.transform.scale(highlight, (80, 80))
        self.highlightPocket = pygame.transform.scale(highlight, (160, 160))
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

        # Draw initial cells
        for y in range(self.levelData["height"]):
            for x in range(self.levelData["width"]):
                self.placeBack(x, y)
                self.placeCell(x, y)

        # Add a separator after everything
        pygame.draw.rect(
            self.gameDisplay, (0, 75, 85),
            (self.levelData["width"] * 80, 0, self.levelData["width"] + 5, self.levelData["height"] * 80)
        )

        for y in range(len(self.simpleLayout)):
            for x in range(len(self.simpleLayout[0])):
                if self.simpleLayout[y][x] == "L0":
                    newLights, rtrn = self.complexLayout[y][x].changeLight()
                    if rtrn is not True:
                        for Dir, color in newLights.items():
                            self.beam(x, y, Dir, color)


                        self.beam(x, y, Dir, color)

        self.drawPocketCells()
        pygame.display.update()

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
            col, row = mouseX // 80, mouseY // 80
            if col >= 0 and row >= 0 and col < self.levelData["width"] and row < self.levelData["height"]:
                if (col, row) != (pastCol, pastRow):
                    if pastCol is not None and pastRow is not None:
                        self.placeBack(pastCol, pastRow)
                        self.placeCell(pastCol, pastRow)
                    pastCol, pastRow = col, row
                    if self.complexLayout[row][col].name == "L":
                        if self.complexLayout[row][col].state in [1, 2]:
                            self.gameDisplay.blit(self.highlight, (col * 80, row * 80))
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
if __name__ == "__mai__":
    game = menu()
    game.load("section1")
    game.play()

if __name__ == "__main__": # Basic main menu for testing tutorials and levels
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
            for i in ["section1/lvlEz1", "section1/a", "section1/lvlHard1", "section1/b"]:
                game = LightHackGame()
                game.load(i)
                game.play()
