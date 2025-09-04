import pygame
import json
from play import LightHackGame
from cells import cells

class levelMaker(LightHackGame):
    def __init__(self):
        super().__init__()
        self.changing= 0
        self.selectedCell= 0

    def loadLevel(self, level:str):
        try:
            with open(f"levels/{level}.json", "r") as f:
                pass
        except FileNotFoundError:
            with open(f"levels/def.json", "r") as f:
                levelData = json.load(f)
            with open(f"levels/{level}.json", "w+") as f:
                json.dump(levelData, f, indent=4)
        super().load(level)
        self.min_height= self.min_height + 160
        self.gameDisplay = pygame.display.set_mode((self.min_width, self.min_height), pygame.RESIZABLE)

    def drawSelectedCells(self):
        availableCells= cells.copy()
        availableCells.pop("default")
        for i, cell in enumerate(availableCells):
            self.gameDisplay.blit(self.background, (i * 80, self.levelData["height"] * 80))
            if i == self.selectedCell:
                self.gameDisplay.blit(self.highlight, (i * 80, self.levelData["height"] * 80))
            self.gameDisplay.blit(cells[cell]().render(), (i * 80, self.levelData["height"] * 80))

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
                        self.calculate()
                        self.placeBack(x, y)
                        self.placeCell(x, y)
                        self.drawPocketCells()
                return False
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
                return False

        elif event.type == pygame.KEYDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            if event.key == pygame.K_r:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.levelData["layout"][y][x] == "D":
                    now = self.complexLayout[y][x].direction
                    newDir = 0 if now == 3 else now + 1
                    self.complexLayout[y][x].changeDirection(newDir)
                    self.calculate()
                return False

            elif event.key == pygame.K_TAB:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    self.placeCell(x, y, overlay=True)
                return False

            elif event.key == pygame.K_q:
                if self.selectedCell >= 0:
                    self.selectedCell -= 1
                self.drawSelectedCells()
                return False

            elif event.key == pygame.K_e:
                if self.selectedCell < len(self.cellData) - 1:
                    self.selectedCell += 1
                self.drawSelectedCells()
                return False

        return super().keyHandler(event)

if __name__ == "__main__":
    game = levelMaker()
    game.loadLevel(input("Level to load: "))
    game.play()