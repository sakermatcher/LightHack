# Import necessary modules
from time import sleep
from cells.default import default
from cells.texturing import multiply
from cells.indicator import numbers
import pygame
import logging
import json
from cells import cells

class LightHackGame:
    """Main game class that handles the Light Hack puzzle game mechanics."""
    
    def __init__(self):
        """Initialize the game with default values for all game state variables."""
        # Game layout and cell management
        self.complexLayout: list[list[default]] = []  # 2D array of game cells with cell classes
        self.gameDisplay = None  # Pygame display surface
        
        # Visual assets
        self.background = None  # Background texture for cells
        self.backgroundPocket = None  # Background texture for pocket inventory
        self.highlightPocket = None  # Highlight texture for pocket selection
        
        # Game data
        self.simpleLayout = None  # Basic level structure with cell IDs
        self.cellData = None  # Cell type and property data
        self.pocket = None  # Player's inventory of available cells
        self.levelData = None  # Complete level configuration
        self.selectedPocket = 0  # Currently selected pocket slot (0-14)

    def placeBack(self, x: int, y: int): #Place the background of the cell
        """Draw the background texture for a cell at position (x, y)."""
        self.gameDisplay.blit(self.background, (x * 80, y * 80))

    def placeCell(self, x: int, y: int, overlay=False): #Place the cell
        """Draw a game cell at position (x, y) with optional overlay effect."""
        if self.complexLayout[y][x] is not None:
            self.gameDisplay.blit(self.complexLayout[y][x].render(overlay=overlay), (x*80, y*80))

    def drawPocketCells(self): #Draw the cells in the pocket
        """Render the inventory panel showing available cells and their quantities."""
        # Draw background grid for 15 pocket slots (3x5 grid)
        for i in range(15):
            x = i % 3
            y = i // 3
            self.gameDisplay.blit(self.backgroundPocket, (self.levelData["width"] * 80 + 5 + x*160, y*160))
            # Highlight currently selected pocket slot
            if i == self.selectedPocket:
                self.gameDisplay.blit(self.highlightPocket, (self.levelData["width"] * 80 + 5 + x*160, y*160))
        
        # Draw the actual cell items and their quantities
        for i, (cell, qty) in enumerate(self.pocket.items()):
            x = i % 3
            y = i // 3
            # Render the cell image in the pocket slot
            self.gameDisplay.blit(
                cells[self.cellData[cell]["type"]](data=self.cellData[cell]["data"]).render(scale=(144,144)),
                (self.levelData["width"] * 80 + 5 + x*144 + (x+1) * 8 + x * 8, y*144 + (y+1) * 8 + y * 8)
            )
            # Display quantity indicator for available items
            if qty > 0:
                qty= "0" + str(qty)  # Format quantity as 2-digit string
                indicator = self.qty.copy()
                # Draw cyan-colored quantity numbers
                indicator.blit(multiply(self.numbers[int(qty[-2])], (0,255,255)), (13, 33))
                indicator.blit(multiply(self.numbers[int(qty[-1])], (0,255,255)), (23, 33))
                self.gameDisplay.blit(pygame.transform.scale(indicator, (160, 160)), (self.levelData["width"] * 80 + 5 + x*160, y*160))
            else:
                # Display "00" in orange when item is out of stock
                qty= "00"
                indicator = self.qty.copy()
                indicator.blit(multiply(self.numbers[0], (255,155,0)), (13, 33))
                indicator.blit(multiply(self.numbers[0], (255,155,0)), (23, 33))
                self.gameDisplay.blit(pygame.transform.scale(indicator, (160, 160)), (self.levelData["width"] * 80 + 5 + x*160, y*160))

    def beam(self, startX, startY, Dir, color): #Shoot a beam from (startX, startY) in direction Dir with color
        """
        Cast a light beam from starting position in specified direction.
        The beam continues until it hits a non-empty cell or goes out of bounds.
        """
        # Calculate direction vectors: Up=0, Right=1, Down=2, Left=3
        dx, dy = [0, -1, 0, 1][Dir], [-1, 0, 1, 0][Dir]
        x, y = startX + dx, startY + dy
        
        # Continue beam through empty cells ('D' type)
        while self.complexLayout[y][x] == 'D':
            # Apply light effect to current cell
            self.complexLayout[y][x].changeLight(From=[2, 3, 0, 1][Dir], color=color)
            # Redraw the cell with updated lighting
            self.placeBack(x, y)
            self.placeCell(x, y)
            # Move to next position
            x, y = x + dx, y + dy
            # Check if beam goes out of bounds
            if x < 0 or y < 0 or x >= self.levelData["width"] or y >= self.levelData["height"]:
                x, y = x - dx, y - dy
                return

        # Handle interaction with non-empty cell
        newLights, rtrn = self.complexLayout[y][x].changeLight(From=[2, 3, 0, 1][Dir], color=color)
        self.placeBack(x, y)
        self.placeCell(x, y)
        # If cell doesn't absorb the light, continue with new beams
        if not rtrn:
            for Dir, color in newLights.items():
                self.beam(x, y, Dir, color)

    def calculate(self):
        """
        Recalculate all light beams in the game grid.
        First resets all cells, then processes laser sources to cast new beams.
        """
        # Reset all cells to their initial state (clear lighting effects)
        for y in range(len(self.complexLayout)):
            for x in range(len(self.complexLayout[0])):
                self.complexLayout[y][x].restart()

        # Process all laser sources and cast beams
        for y in range(len(self.complexLayout)):
            for x in range(len(self.complexLayout[0])):
                # Check if current cell is a laser source
                if self.complexLayout[y][x] == "L":
                    newLights, rtrn = self.complexLayout[y][x].changeLight()
                    # Cast beams from laser if it emits light
                    if rtrn is not True:
                        for Dir, color in newLights.items():
                            self.beam(x, y, Dir, color)
                # Redraw each cell after processing
                self.placeBack(x, y)
                self.placeCell(x, y)

        # Update the display to show all changes
        pygame.display.update()

    def keyHandler(self, event):
        """Handle all user input events (mouse clicks and keyboard presses)."""
        # Handle mouse button clicks
        if event.type == pygame.MOUSEBUTTONDOWN :
            mouseX, mouseY = pygame.mouse.get_pos()
            x, y = mouseX // 80, mouseY // 80
            
            # Left mouse button - place cells from inventory or select pocket slots
            if event.button == 1:
                # Click on game grid to place a cell
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.selectedPocket < len(self.pocket):
                    cellKey = list(self.pocket.keys())[self.selectedPocket]
                    # Place cell if available in inventory and target is empty
                    if self.pocket[cellKey] > 0 and self.complexLayout[y][x].name == "D":
                        self.complexLayout[y][x] = self.complexLayout[y][x].convert(cells[self.cellData[cellKey]["type"]], name=cellKey, data=self.cellData[cellKey]["data"])
                        self.pocket[cellKey] -= 1
                        self.drawPocketCells()
                        self.calculate()
                # Click on inventory panel to select different pocket slot
                else:
                    x, y= (mouseX - (self.levelData["width"] * 80 + 5)) // 160, mouseY // 160
                    if x >= 0 and y >= 0 and x < 3 and y < 5 and (y * 3 + x) < len(self.pocket):
                        self.selectedPocket = y * 3 + x
                        self.drawPocketCells()
            # Right mouse button - remove cells and return them to inventory
            elif event.button == 3:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    # Remove cell if it exists in inventory system
                    if self.complexLayout[y][x].name in self.pocket:
                        self.pocket[self.complexLayout[y][x].name] += 1
                        self.complexLayout[y][x] = self.complexLayout[y][x].convert(other=cells["default"], name="D")
                        self.calculate()
                        self.drawPocketCells()
                    else:
                        print(self.complexLayout[y][x].name, "is not in pocket")

        # Handle keyboard input
        elif event.type == pygame.KEYDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            # W key - navigate pocket selection up
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

            # S key - navigate pocket selection down
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

            # A key - navigate pocket selection left
            elif event.key == pygame.K_a:
                if self.selectedPocket > 0:
                    self.selectedPocket -= 1
                else:
                    self.selectedPocket = 14
                self.drawPocketCells()

            # D key - navigate pocket selection right
            elif event.key == pygame.K_d:
                if self.selectedPocket < 14:
                    self.selectedPocket += 1
                else:
                    self.selectedPocket = 0    
                self.drawPocketCells()

            # R key - rotate cell under mouse cursor
            elif event.key == pygame.K_r:
                x, y = mouseX // 80, mouseY // 80
                
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.levelData["layout"][y][x] == "D":
                    now = self.complexLayout[y][x].direction
                    newDir = 0 if now == 3 else now + 1
                    self.complexLayout[y][x].changeDirection(newDir)
                    self.calculate()

            # F key - flip cell under mouse cursor
            elif event.key == pygame.K_f:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.levelData["layout"][y][x] == "D":
                    if self.complexLayout[y][x].flip():
                        self.calculate()

            # E key - show overlay for cell under mouse cursor
            elif event.key == pygame.K_e:
                x, y = mouseX // 80, mouseY // 80
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    self.placeCell(x, y, overlay=True)

            # DELETE key - exit to pause menu (TODO: implement pause menu)
            elif event.key == pygame.K_DELETE:
                return True
            
        # Check if level is completed - all final cells must be completed
        for f in self.finals:
            if not f.isCompleated:
                break
        else:
            # Display level completion message
            font = pygame.font.SysFont('Arial', 64)
            text = font.render('Level Compleated!', True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.min_width // 2, self.min_height // 2))
            self.gameDisplay.blit(text, text_rect)
            pygame.display.update()
            sleep(3)
            return True

        return False

    def load(self, level):
        """Load and initialize a level from JSON file with all game assets."""
        # Load level data from JSON file with error handling
        try:
            self.levelData = json.load(open(f"levels/{level}.json", "r"))
        except FileNotFoundError:
            logging.error(f"Level file levels/{level}.json not found.")
            return
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from levels/{level}.json.")
            return
        
        # Initialize pygame and set up display
        pygame.init()
        # --- MUSIC INITIALIZATION ---
        pygame.mixer.init()
        pygame.mixer.music.load("assets/lightHackV1.mp3")
        pygame.mixer.music.play(-1)  # Loop indefinitely
        # --- END MUSIC ---
        
        # Calculate display dimensions based on level size + inventory panel
        self.min_width = self.levelData["width"] * 80 + 485
        self.min_height = self.levelData["height"] * 80
        self.gameDisplay = pygame.display.set_mode((self.min_width, self.min_height), pygame.RESIZABLE)
        
        # Load and scale background textures
        self.background = pygame.image.load("assets/background.png")
        self.backgroundPocket = pygame.transform.scale(self.background, (160, 160))
        self.background = pygame.transform.scale(self.background, (80, 80))
        self.qty = pygame.image.load("assets/indicators/qty.png").convert_alpha()
        self.numbers= tuple(pygame.image.load(f"assets/{i}").convert_alpha() for i in numbers)
        highlight = pygame.image.load("assets/highlight.png").convert_alpha()
        self.highlight = pygame.transform.scale(highlight, (80, 80))
        self.highlightPocket = pygame.transform.scale(highlight, (160, 160))
        self.lastWidth, self.lastHeight = self.gameDisplay.get_size()

        # Initialize game data from level configuration
        self.simpleLayout = self.levelData["layout"]
        self.cellData = self.levelData["cells"]
        self.pocket = self.levelData["pocket"]
        self.complexLayout = []
        self.finals= []

        # Create complex layout by converting simple layout to cell objects
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
                # Track final cells for level completion checking
                if cell[0] == "F":
                    self.finals.append(self.complexLayout[y][-1])

        # Set background color and draw initial game state
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

        # Initialize laser beams for the starting state
        for y in range(len(self.simpleLayout)):
            for x in range(len(self.simpleLayout[0])):
                if self.simpleLayout[y][x][0] == "L":
                    newLights, rtrn = self.complexLayout[y][x].changeLight()
                    if rtrn is not True:
                        for Dir, color in newLights.items():
                            self.beam(x, y, Dir, color)

        # Draw inventory panel and update display
        self.drawPocketCells()
        pygame.display.update()

    def play(self):
        """Main game loop that handles events, input, and display updates."""
        # Track mouse hover position for cell highlighting
        pastCol = None
        pastRow = None
        out = False
        
        # Main game loop
        while not out:
            # Handle all pygame events
            try:
                for event in pygame.event.get():
                    # Handle window close button
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    # Process user input and check for game exit conditions
                    out= self.keyHandler(event)
                    if out:
                        break
            except:
                pass

            # ---------- CELL HIGHLIGHT SYSTEM -------------
            # Track mouse position and highlight hovered cells
            mouseX, mouseY = pygame.mouse.get_pos()
            col, row = mouseX // 80, mouseY // 80
            
            # Check if mouse is over a valid cell
            if col >= 0 and row >= 0 and col < self.levelData["width"] and row < self.levelData["height"]:
                # Only redraw if mouse moved to a different cell
                if (col, row) != (pastCol, pastRow):
                    
                    # Remove highlight from previous cell
                    if pastCol is not None and pastRow is not None:
                        self.placeBack(pastCol, pastRow)
                        self.placeCell(pastCol, pastRow)
                    pastCol, pastRow = col, row

                    # Add highlight to current cell and redraw it
                    self.gameDisplay.blit(self.highlight, (col * 80, row * 80))
                    self.placeCell(col, row)

            # Remove highlight when mouse leaves game area
            elif pastCol is not None and pastRow is not None:
                self.placeBack(pastCol, pastRow)
                self.placeCell(pastCol, pastRow)
                pastCol, pastRow = None, None

            # Handle window resizing - enforce minimum window size
            if (self.lastWidth, self.lastHeight) != self.gameDisplay.get_size():
                cur_width, cur_height = self.gameDisplay.get_size()
                new_width = max(cur_width, self.min_width)
                new_height = max(cur_height, self.min_height)

                # Resize window if it's smaller than minimum size
                if (cur_width, cur_height) != (new_width, new_height):
                    self.gameDisplay = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                self.lastWidth, self.lastHeight = self.gameDisplay.get_size()

                # Redraw entire game grid after resize
                for y in range(self.levelData["height"]):
                    for x in range(self.levelData["width"]):
                        self.placeBack(x, y)
                        self.placeCell(x, y)

                # Redraw separator between game area and inventory
                pygame.draw.rect(
                    self.gameDisplay, (0, 75, 85),
                    (self.levelData["width"] * 80, 0, self.levelData["width"] + 5, self.levelData["height"] * 80)
                )
                self.drawPocketCells()

            pygame.display.update()

# Main program execution
if __name__ == "__main__":
    # Create game instance and run a hard level
    game = LightHackGame()
    game.load("testing")  # Load level from JSON file
    game.play()  # Start the game loop