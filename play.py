from time import sleep
from cells.default import default
from cells.texturing import multiply
from cells.indicator import numbers
import pygame
import logging
import json
from cells import cells

class LightHackGame:
    def __init__(self):
        self.complexLayout: list[list[default]] = []
        self.gameDisplay = None
        self.background = None
        self.backgroundPocket = None
        self.highlightPocket = None
        self.simpleLayout = None
        self.cellData = None
        self.pocket = None
        self.levelData = None
        self.selectedPocket = 0

    def placeBack(self, x: int, y: int):
        self.gameDisplay.blit(self.background, (x * 80, y * 80))

    def placeCell(self, x: int, y: int, overlay=False):
        if self.complexLayout[y][x] is not None:
            self.gameDisplay.blit(self.complexLayout[y][x].render(overlay=overlay), (x*80, y*80))

    def drawPocketCells(self):
        for i in range(15):
            x = i % 3
            y = i // 3
            self.gameDisplay.blit(self.backgroundPocket, (self.levelData["width"] * 80 + 5 + x*160, y*160))
            if i == self.selectedPocket:
                self.gameDisplay.blit(self.highlightPocket, (self.levelData["width"] * 80 + 5 + x*160, y*160))
        for i, (cell, qty) in enumerate(self.pocket.items()):
            x = i % 3
            y = i // 3
            self.gameDisplay.blit(
                cells[self.cellData[cell]["type"]](data=self.cellData[cell]["data"]).render(scale=(144,144)),
                (self.levelData["width"] * 80 + 5 + x*144 + (x+1) * 8 + x * 8, y*144 + (y+1) * 8 + y * 8)
            )
            if qty > 0:
                qty= "0" + str(qty)
                indicator = self.qty.copy()
                indicator.blit(multiply(self.numbers[int(qty[-2])], (0,255,255)), (13, 33))
                indicator.blit(multiply(self.numbers[int(qty[-1])], (0,255,255)), (23, 33))
                self.gameDisplay.blit(pygame.transform.scale(indicator, (160, 160)), (self.levelData["width"] * 80 + 5 + x*160, y*160))
            else:
                qty= "00"
                indicator = self.qty.copy()
                indicator.blit(multiply(self.numbers[0], (255,155,0)), (13, 33))
                indicator.blit(multiply(self.numbers[0], (255,155,0)), (23, 33))
                self.gameDisplay.blit(pygame.transform.scale(indicator, (160, 160)), (self.levelData["width"] * 80 + 5 + x*160, y*160))

    def beam(self, startX, startY, Dir, color):
        dx, dy = [0, -1, 0, 1][Dir], [-1, 0, 1, 0][Dir]
        x, y = startX + dx, startY + dy
        while self.complexLayout[y][x] == 'D':
            self.complexLayout[y][x].changeLight(From=[2, 3, 0, 1][Dir], color=color)
            self.placeBack(x, y)
            self.placeCell(x, y)
            x, y = x + dx, y + dy

        newLights, rtrn = self.complexLayout[y][x].changeLight(From=[2, 3, 0, 1][Dir], color=color)
        self.placeBack(x, y)
        self.placeCell(x, y)
        if not rtrn:
            for Dir, color in newLights.items():
                self.beam(x, y, Dir, color)

    def calculate(self):
        for y in range(len(self.complexLayout)):
            for x in range(len(self.complexLayout[0])):
                self.complexLayout[y][x].restart()

        for y in range(len(self.simpleLayout)):
            for x in range(len(self.simpleLayout[0])):
                if self.simpleLayout[y][x][0] == "L":
                    Dir, color = self.complexLayout[y][x].changeLight()
                    self.beam(x, y, Dir, color)
                self.placeBack(x, y)
                self.placeCell(x, y)

        pygame.display.update()

    def keyHandler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN :
            mouseX, mouseY = pygame.mouse.get_pos()
            x, y = mouseX // 80, mouseY // 80
            if event.button == 1:
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.selectedPocket < len(self.pocket):
                    cellKey = list(self.pocket.keys())[self.selectedPocket]
                    if self.pocket[cellKey] > 0 and self.complexLayout[y][x].name == "D":
                        self.complexLayout[y][x] = self.complexLayout[y][x].convert(cells[self.cellData[cellKey]["type"]], name=cellKey, data=self.cellData[cellKey]["data"])
                        self.pocket[cellKey] -= 1
                        self.drawPocketCells()
                        self.calculate()
            elif event.button == 3:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    if self.complexLayout[y][x].name in self.pocket:
                        self.pocket[self.complexLayout[y][x].name] += 1
                        self.complexLayout[y][x] = self.complexLayout[y][x].convert(other=cells["default"], name="D")
                        self.calculate()
                        self.drawPocketCells()
                    else:
                        print(self.complexLayout[y][x].name, "is not in pocket")

        elif event.type == pygame.KEYDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            if event.key == pygame.K_w:
                if self.selectedPocket > 2:
                    self.selectedPocket -= 3
                elif self.selectedPocket == 0:
                    self.selectedPocket = 12
                elif self.selectedPocket == 1:
                    self.selectedPocket = 13
                else:
                    self.selectedPocket = 14
                self.drawPocketCells()

            elif event.key == pygame.K_s:
                if self.selectedPocket < 12:
                    self.selectedPocket += 3
                elif self.selectedPocket == 12:
                    self.selectedPocket = 0
                elif self.selectedPocket == 13:
                    self.selectedPocket = 1
                else:
                    self.selectedPocket = 2
                self.drawPocketCells()

            elif event.key == pygame.K_a:
                if self.selectedPocket > 0:
                    self.selectedPocket -= 1
                else:
                    self.selectedPocket = 14
                self.drawPocketCells()

            elif event.key == pygame.K_d:
                if self.selectedPocket < 14:
                    self.selectedPocket += 1
                else:
                    self.selectedPocket = 0    
                self.drawPocketCells()

            elif event.key == pygame.K_r:
                x, y = mouseX // 80, mouseY // 80
                
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.levelData["layout"][y][x] == "D":
                    now = self.complexLayout[y][x].direction
                    newDir = 0 if now == 3 else now + 1
                    self.complexLayout[y][x].changeDirection(newDir)
                    self.calculate()

            elif event.key == pygame.K_f:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.levelData["layout"][y][x] == "D":
                    if self.complexLayout[y][x].flip():
                        self.calculate()

            elif event.key == pygame.K_e:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    self.placeCell(x, y, overlay=True)

            elif event.key == pygame.K_DELETE: #TODO: PAUSE MENU def
                return True
            
        for f in self.finals:
            if not f.isCompleated:
                break
        else:
            print("Level Compleated!")
            font = pygame.font.SysFont('Arial', 64)
            text = font.render('Level Compleated!', True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.min_width // 2, self.min_height // 2))
            self.gameDisplay.blit(text, text_rect)
            pygame.display.update()
            sleep(3)
            return True

        return False

    def load(self, level):
        try:
            self.levelData = json.load(open(f"levels/{level}.json", "r"))
        except FileNotFoundError:
            logging.error(f"Level file levels/{level}.json not found.")
            return
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from levels/{level}.json.")
            return
        
        pygame.init()
        self.min_width = self.levelData["width"] * 80 + 485
        self.min_height = self.levelData["height"] * 80
        self.gameDisplay = pygame.display.set_mode((self.min_width, self.min_height), pygame.RESIZABLE)
        self.background = pygame.image.load("assets/background.png")
        self.backgroundPocket = pygame.transform.scale(self.background, (160, 160))
        self.background = pygame.transform.scale(self.background, (80, 80))
        self.qty = pygame.image.load("assets/indicators/qty.png").convert_alpha()
        self.numbers= tuple(pygame.image.load(f"assets/{i}").convert_alpha() for i in numbers)
        highlight = pygame.image.load("assets/highlight.png").convert_alpha()
        self.highlight = pygame.transform.scale(highlight, (80, 80))
        self.highlightPocket = pygame.transform.scale(highlight, (160, 160))
        self.lastWidth, self.lastHeight = self.gameDisplay.get_size()

        self.simpleLayout = self.levelData["layout"]
        self.cellData = self.levelData["cells"]
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
                if self.simpleLayout[y][x][0] == "L":
                    Dir, color = self.complexLayout[y][x].changeLight()
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

if __name__ == "__main__":
    game = LightHackGame()
    game.load("a")
    game.play()