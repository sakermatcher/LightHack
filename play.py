from time import sleep
from cells.default import default
import pygame
import logging
import json
from cells import cells

complexLayout:list[list[default]]= []

gameDisplay, background, simpleLayout =None, None, None

def placeBack(x:int, y:int):
    '''
    Cell x, y
    '''
    global gameDisplay, background
    gameDisplay.blit(background, (x * 80, y * 80))

def placeCell(x:int, y:int, overlay=False):
    '''
    Cell x, y
    '''
    global gameDisplay, complexLayout
    if complexLayout[y][x] is not None:
        gameDisplay.blit(complexLayout[y][x].render(overlay=overlay), (x*80, y*80))

def beam(startX, startY, Dir, color):
    global complexLayout
    dx, dy= [0, -1, 0, 1][Dir], [-1, 0, 1, 0][Dir]
    x, y= startX + dx, startY + dy
    while complexLayout[y][x] == 'D':
        complexLayout[y][x].changeLight(From= [2, 3, 0, 1][Dir], color= color)
        placeBack(x, y)
        placeCell(x, y)
        x, y= x + dx, y + dy
    
    newLights, rtrn= complexLayout[y][x].changeLight(From= [2, 3, 0, 1][Dir], color= color)
    placeBack(x, y)
    placeCell(x, y)
    if not rtrn:
        for Dir, color in newLights.items():
            beam(x, y, Dir, color)

def calculate():
    global complexLayout, simpleLayout
    for y in range(len(complexLayout)):
        for x in range(len(complexLayout[0])):
            complexLayout[y][x].restart()

    for y in range(len(simpleLayout)):
        for x in range(len(simpleLayout[0])):
            if simpleLayout[y][x][0] == "L":
                Dir, color= complexLayout[y][x].changeLight()
                beam(x, y, Dir, color)
            placeBack(x, y)
            placeCell(x, y)
    pygame.display.update()

def play(level):
    global gameDisplay, background, complexLayout, simpleLayout
    try:
        levelData= json.load(open(f"levels/{level}.json", "r"))

    except FileNotFoundError:
        logging.error(f"Level file levels/{level}.json not found.")
        return
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from levels/{level}.json.")
        return
    
    pygame.init()
    gameDisplay = pygame.display.set_mode((levelData["width"] * 80 + 365, levelData["height"] * 80), pygame.RESIZABLE)

    simpleLayout= levelData["layout"]
    cellData= levelData["cells"]
    pocket= levelData["pocket"]
    complexLayout= []

    for y, row in enumerate(simpleLayout):
        complexLayout.append([])
        for x, cell in enumerate(row):
            complexLayout[y].append(cells[cellData[cell]["type"]] (xy=(x,y), name=cellData[cell]["type"], layout=simpleLayout, data=cellData[cell]["data"]))

    gameDisplay.fill((0, 0, 0))

    clock = pygame.time.Clock()

    background = pygame.image.load("assets/background.png")
    background = pygame.transform.scale(background, (80, 80))
    highlight= pygame.image.load("assets/highlight.png").convert_alpha()
    highlightPoket= pygame.transform.scale(highlight, (160, 160))
    highlight = pygame.transform.scale(highlight, (80, 80))



    for y in range(levelData["height"]):
        for x in range(levelData["width"]):
            placeBack(x, y)
            placeCell(x, y)

    #Add a separator after everything

    pygame.draw.rect(gameDisplay, (0, 75, 85), (levelData["width"] * 80, 0, levelData["width"] + 5, levelData["height"] * 80))

    for y in range(len(simpleLayout)):
        for x in range(len(simpleLayout[0])):
            if simpleLayout[y][x][0] == "L":
                Dir, color= complexLayout[y][x].changeLight()
                beam(x, y, Dir, color)


    pygame.display.update()

    pastCol= None
    pastRow= None
    out= False

    while not out:
        #Show fps
        fps = clock.get_fps()
        pygame.display.set_caption(f"FPS: {fps:.2f}")
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key== pygame.K_SPACE:
                    x, y = mouseX // 80, mouseY // 80
                    complexLayout[y][x]= complexLayout[y][x].convert(cells["mirror"])
                    calculate()
                if event.key== pygame.K_e:
                    x, y = mouseX // 80, mouseY // 80
                    complexLayout[y][x]= complexLayout[y][x].convert(cells["prism"])
                    calculate()
                if event.key== pygame.K_w:
                    x, y = mouseX // 80, mouseY // 80
                    complexLayout[y][x]= complexLayout[y][x].convert(cells["glass"])
                    calculate()
                if event.key== pygame.K_a:
                    x, y = mouseX // 80, mouseY // 80
                    complexLayout[y][x]= complexLayout[y][x].convert(cells["glass"], data={"direction":0, "type":1, "potency":5})
                    calculate()
                    
                if event.key== pygame.K_r:
                    x, y = mouseX // 80, mouseY // 80
                    now= complexLayout[y][x].direction
                    if now == 3:
                        newDir= 0
                    else:
                        newDir= now+1
                    complexLayout[y][x].changeDirection(newDir)
                    calculate()

                if event.key == pygame.K_DELETE:
                    out= True
                if event.key== pygame.K_q:
                    x, y = mouseX // 80, mouseY // 80
                    complexLayout[y][x]= complexLayout[y][x].convert(cells["default"])
                    calculate()

                if event.key == pygame.K_TAB:
                    x, y = mouseX // 80, mouseY // 80
                    placeBack(x, y)
                    placeCell(x, y, overlay=True)


        # ---------- CELL HIGHLIGHT -------------
        mouseX, mouseY = pygame.mouse.get_pos()
        col, row = mouseX // 80, mouseY // 80
        if col >= 0 and row >= 0 and col < levelData["width"] and row < levelData["height"]:
            if (col, row) != (pastCol, pastRow):
                if pastCol is not None and pastRow is not None:
                    #Place Background Back
                    placeBack(pastCol, pastRow)
                    placeCell(pastCol, pastRow)
                pastCol, pastRow = col, row
                #Place Highlight
                gameDisplay.blit(highlight, (col * 80, row * 80))
                placeCell(col, row)

        elif pastCol is not None and pastRow is not None:
            #Place Background Back
            placeBack(pastCol, pastRow)
            placeCell(pastCol, pastRow)
            pastCol, pastRow = None, None
        gameDisplay.
        pygame.display.update()

if __name__ == "__main__":
    while True:
        play("test1")