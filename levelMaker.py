import pygame
import json
from play import LightHackGame
from cells import cells
from cells.texturing import multiply

class levelMaker(LightHackGame):
    def __init__(self):
        super().__init__()
        self.changing= 0
        self.selectedCell= 0
        self.toPocket = [[],[]]

    def placeCell(self, x: int, y: int, overlay=False):
        if self.complexLayout[y][x] is not None:
            if (x, y) in self.toPocket[0]:
                self.gameDisplay.blit(multiply(self.complexLayout[y][x].render(overlay=overlay), (255,180,180)), (x*80, y*80))
            else:
                self.gameDisplay.blit(self.complexLayout[y][x].render(overlay=overlay), (x*80, y*80))

    def makeId(self, name, IDs):
        for i in range(100):
            if f"{name}{i}" not in IDs:
                return f"{name}{i}"



    def loadLevel(self, level:str, **kwargs):
        self.LevelName= level
        try:
            with open(f"levels/{level}.json", "r") as f:
                pass
        except FileNotFoundError:
            with open(f"levels/def.json", "r") as f:
                self.levelData = json.load(f)
            self.levelData["width"]= kwargs["width"] if "width" in kwargs else 10
            self.levelData["height"]= kwargs["height"] if "height" in kwargs else 10
            for y in range(self.levelData["height"]):
                self.levelData["layout"].append(["D"]*self.levelData["width"])
                for x in range(self.levelData["width"]):
                    if y == 0 or y == self.levelData["height"]-1 or x == 0 or x == self.levelData["width"]-1:
                        self.levelData["layout"][y][x] = "X"

            with open(f"levels/{level}.json", "w+") as f:
                json.dump(self.levelData, f, indent=4)
        super().load(level)
        self.min_height= self.min_height + 80
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
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.selectedCell < len(cells)-1:
                    if (x, y) in self.toPocket[0]:
                        self.toPocket[0].remove((x, y))
                        self.toPocket[1].remove(self.complexLayout[y][x])
                    cellKey = list(cells.keys())
                    cellKey.remove("default")
                    cellKey= cellKey[self.selectedCell]
                    self.complexLayout[y][x] = self.complexLayout[y][x].convert(other=cells[cellKey], name=cellKey)
                    self.simpleLayout[y][x] = cellKey[0].upper()
                    self.calculate()
                return False
            
            elif event.button == 3:
                x, y = mouseX // 80, mouseY // 80
                if (x, y) in self.toPocket[0]:
                    self.toPocket[1].remove(self.complexLayout[y][x])
                    self.toPocket[0].remove((x, y))
                self.complexLayout[y][x] = self.complexLayout[y][x].convert(other=cells["default"], name="D")
                self.simpleLayout[y][x] = "D"
                self.calculate()
                return False

        elif event.type == pygame.KEYDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            if event.key == pygame.K_SPACE:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.simpleLayout[y][x] != "D" and self.simpleLayout[y][x] != "X":
                    if (x, y) in self.toPocket[0]:
                        self.toPocket[1].remove(self.complexLayout[y][x])
                        self.toPocket[0].remove((x, y))
                    else:
                        self.toPocket[0].append((x, y))
                        self.toPocket[1].append(self.complexLayout[y][x])
                    self.calculate()
                return False
            
            elif event.key == pygame.K_r:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    now = self.complexLayout[y][x].direction
                    newDir = 0 if now == 3 else now + 1
                    self.complexLayout[y][x].changeDirection(newDir)
                    self.calculate()
            
            elif event.key == pygame.K_f:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    if self.complexLayout[y][x].flip():
                        self.calculate()

            elif event.key == pygame.K_w:
                if self.selectedPocket > 0:
                    self.selectedPocket -= 1
                else:
                    self.selectedPocket = 14
                self.drawPocketCells()
                return False

            elif event.key == pygame.K_s:
                if self.selectedPocket < 14:
                    self.selectedPocket += 1
                else:
                    self.selectedPocket = 0    
                self.drawPocketCells()
                return False

            elif event.key == pygame.K_a:
                if self.selectedCell > 0:
                    self.selectedCell -= 1
                self.drawSelectedCells()
                return False

            elif event.key == pygame.K_d:
                if self.selectedCell < len(cells) - 2:
                    self.selectedCell += 1
                self.drawSelectedCells()
                return False
            
            elif event.key == pygame.K_z:
                x, y = mouseX // 80, mouseY // 80
                self.changing= 0
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.simpleLayout[y][x] != "D":
                    if self.complexLayout[y][x].editProperty(None, self.changing):
                        self.calculate()
                return False
            
            elif event.key == pygame.K_x:
                x, y = mouseX // 80, mouseY // 80
                self.changing= 1
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.simpleLayout[y][x] != "D":
                    if self.complexLayout[y][x].editProperty(None, self.changing):
                        self.calculate()
                return False

            elif event.key == pygame.K_c:
                x, y = mouseX // 80, mouseY // 80
                self.changing= 2
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.simpleLayout[y][x] != "D":
                    if self.complexLayout[y][x].editProperty(None, self.changing):
                        self.calculate()
                return False
        
            elif event.key == pygame.K_q:
                if self.selectedPocket < len(self.pocket):
                    self.pocket[list(self.pocket.keys())[self.selectedPocket]] += 1
                    del(self.pocket[list(self.pocket.keys())[self.selectedPocket]])
                    self.drawPocketCells()
                return False

            elif event.key == pygame.K_ESCAPE:
                newData= [[],[],[]] #ID, qty, data
                for i in self.pocket:
                    newData[0].append(i)
                    newData[1].append(self.pocket[i])
                    newData[2].append(self.cellData[i])

                self.pocket= {}
                self.cellData= {}
                
                for y in range(self.levelData["height"]):
                    for x in range(self.levelData["width"]):
                        if (x, y) in self.toPocket[0]:
                            i = self.toPocket[0].index((x, y))
                            data= self.toPocket[1][i].getData().copy()
                            data["direction"]= 0
                            if data not in newData[2]:
                                newData[0].append(self.makeId(self.simpleLayout[y][x][0], newData[0]))
                                newData[1].append(1)
                                newData[2].append(data)
                                self.simpleLayout[y][x] = "D"
                                self.complexLayout[y][x] = self.complexLayout[y][x].convert(other=cells["default"], name="D")
                            else:
                                index= newData[2].index(data)
                                newData[1][index] += 1
                                self.simpleLayout[y][x] = "D"
                                self.complexLayout[y][x] = self.complexLayout[y][x].convert(other=cells["default"], name="D")
                            
                        elif self.simpleLayout[y][x] != "D" and self.simpleLayout[y][x] != "X":
                            if self.complexLayout[y][x].getData() not in newData[2]:
                                newData[0].append(self.makeId(self.simpleLayout[y][x][0], newData[0]))
                                newData[1].append(0)
                                newData[2].append(self.complexLayout[y][x].getData())
                                print(newData[0][-1])
                                self.simpleLayout[y][x] = newData[0][-1]
                            else:
                                index= newData[2].index(self.complexLayout[y][x].getData())
                                self.simpleLayout[y][x] = newData[0][index].upper()
                for i in range(len(newData[0])):
                    if newData[1][i] > 0:
                        self.pocket[newData[0][i]]= newData[1][i]
                    self.cellData[newData[0][i]]= newData[2][i]
                
                self.cellData["X"]= {
                        "type": "block",
                        "data": {}
                }
                self.cellData["D"]= {
                        "type": "default",
                        "data": {}
                }

                with open(f"levels/{self.LevelName}.json", "w") as f:
                    json.dump({
                        "width": self.levelData["width"],
                        "height": self.levelData["height"],
                        "pocket": self.pocket,
                        "cells": self.cellData,
                        "layout": self.simpleLayout
                    }, f, indent=4)

                return False



            else:
                for num in range(pygame.K_0, pygame.K_9 + 1):
                    if event.key == num:
                        x, y = mouseX // 80, mouseY // 80
                        if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.simpleLayout[y][x] != "D":
                            index = num - pygame.K_0
                            if self.complexLayout[y][x].editProperty(index, self.changing):
                                self.calculate()
                            return False

        return super().keyHandler(event)

if __name__ == "__main__":
    game = levelMaker()
    game.loadLevel("lvl1", width=10, height=10)
    game.drawSelectedCells()
    game.play()