import pygame
import json
from cells import cells

level= "test"

width, height= 10, 10

#Keep window on top

gameDisplay = pygame.display.set_mode((width * 80 + 365, height * 80), pygame.RESIZABLE)

pygame.init()

gameDisplay.fill((0, 0, 0))

clock = pygame.time.Clock()

background = pygame.image.load("assets/background.png")
background = pygame.transform.scale(background, (80, 80))
highlight= pygame.image.load("assets/highlight.png").convert_alpha()
highlightPoket= pygame.transform.scale(highlight, (160, 160))
highlight = pygame.transform.scale(highlight, (80, 80))

cellData= {
    "X": {"type": "block", "data": {}},
    "D": {"type": "default", "data": {}}
}

def placeBack(x:int, y:int):
    '''
    Cell x, y
    '''
    global gameDisplay, background
    gameDisplay.blit(background, (x * 80, y * 80))

for y in range(height):
    for x in range(width):
        placeBack(x, y)

#Add a separator after everything

simpleLayout=[["" for _ in range(width)] for _ in range(height)]

lettersToCell= {
    "X": cells["block"],
    "L": cells["laser"]
}

complexLayout= [[None for _ in range(width)] for _ in range(height)]

def placeCell(x:int, y:int):
    '''
    Cell x, y
    '''
    global gameDisplay, complexLayout
    if complexLayout[y][x] is not None:
        gameDisplay.blit(complexLayout[y][x].render(), (x*80, y*80))

pygame.draw.rect(gameDisplay, (0, 75, 85), (width * 80, 0, width + 5, height * 80))

pygame.display.update()

pastCol= None
pastRow= None

letter= "X"

while True:
    #Show fps
    fps = clock.get_fps()
    pygame.display.set_caption(f"FPS: {fps:.2f}")
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_x:
                    letter= "X"
                case pygame.K_l:
                    letter= "L"

                case pygame.K_ESCAPE:
                    default= json.load(open(f"levels/def.json", "r"))
                    default["width"]= width
                    default["height"]= height
                    default["cells"]= cellData
                    default["layout"]= [["D" if cell == "" else cell for cell in row] for row in simpleLayout]
                    json.dump(default, open(f"levels/{level}.json", "w+"), indent=4)

                case pygame.K_TAB:
                    mouseX, mouseY= pygame.mouse.get_pos()
                    col, row= mouseX // 80, mouseY // 80
                    if col >= 0 and row >= 0 and col < width and row < height:
                        changed= False
                        data= input("Enter cell data to edit (d: Dir, c: Color): ").lower()
                        match data:
                            case "d":
                                directionInput= input("Enter new direction (N, E, S, W): ").upper()
                                directionMap= {
                                    "N": 0,
                                    "E": 3,
                                    "S": 2,
                                    "W": 1
                                }
                                direction= directionMap.get(directionInput)
                                if direction is not None:
                                    complexLayout[row][col].changeDirection(direction)
                                    gameDisplay.blit(highlight, (col * 80, row * 80))
                                    placeCell(col, row)
                                    changed= True
                                else:
                                    print("Invalid direction")
                            case "c":
                                colorInput= input("Enter new color as R,G,B (0-10 each): ")
                                try:
                                    color= tuple(int(c) for c in colorInput.split(","))
                                    if len(color) == 3 and all(0 <= c <= 10 for c in color):
                                        complexLayout[row][col].changeColor(color)
                                        gameDisplay.blit(highlight, (col * 80, row * 80))
                                        placeCell(col, row)
                                        changed= True
                                    else:
                                        print("Invalid color")
                                except ValueError:
                                    print("Invalid color format")
                    if simpleLayout[row][col] in cellData and changed:
                        cellData[simpleLayout[row][col]]= complexLayout[row][col].getData()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if letter in ["D", "X"]:
                    simpleLayout[row][col] = letter
                    complexLayout[row][col] = lettersToCell[letter]((col, row))
                else:
                    for i in range(10):
                        if f"{letter}{i}" not in cellData:
                            complexLayout[row][col] = lettersToCell[letter]((col, row))
                            cellData[f"{letter}{i}"] = complexLayout[row][col].getData()
                            simpleLayout[row][col] = f"{letter}{i}"
                            break
                placeCell(col, row)


            elif event.button == 3:  # Right mouse button
                if len(simpleLayout[row][col]) > 1:
                    del(cellData[simpleLayout[row][col]])
                simpleLayout[row][col] = ""
                complexLayout[row][col] = None

    #Get mouse pos and highlight cell
    mouseX, mouseY = pygame.mouse.get_pos()
    col, row = mouseX // 80, mouseY // 80
    if col >= 0 and row >= 0 and col < width and row < height:
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

    pygame.display.update()