# Import necessary modules
from time import sleep
from cells.default import default
from cells.texturing import multiply
from cells.indicator import numbers
import pygame
import logging
import numpy as np
import json
from cells import cells
from screeninfo import get_monitors

monitors = get_monitors()
main_monitor = min(monitors, key=lambda m: (abs(m.x), abs(m.y)))
screenHeight = main_monitor.height

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
        self.borderC = None  # Border texture (not used currently)
        self.borderS = None  # Border texture (not used currently)
        self.highlightPocket = None  # Highlight texture for pocket selection
        
        # Game data
        self.simpleLayout = None  # Basic level structure with cell IDs
        self.cellData = None  # Cell type and property data
        self.pocket = None  # Player's inventory of available cells
        self.levelData = None  # Complete level configuration
        self.selectedPocket = 0  # Currently selected pocket slot (0-14)

        self.cellSize = int(screenHeight / 13.5)  # Size of each cell in pixels

    def makeGradient(self):
        """Creates and returns a gradient surface filling the screen."""
        # Gradient should cover entire screen
        surf = pygame.Surface((self.lastWidth, self.lastHeight))
        arr = np.zeros((self.lastWidth, self.lastHeight, 3), dtype=np.uint8)  # <-- swapped order

        # Determine center
        center_x = self.lastWidth // 2
        center_y = self.lastHeight // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)

        # Build coordinate grids matching the array shape
        x = np.arange(self.lastWidth)
        y = np.arange(self.lastHeight)
        X, Y = np.meshgrid(x, y, indexing="xy")

        dx = X - center_x
        dy = Y - center_y
        dist = np.sqrt(dx**2 + dy**2) / max_dist
        dist = np.clip(1 - dist, 0, 1)

        # Adjust falloff so center is near full color
        inner_radius = min(self.min_width, self.min_height) / 1.5
        falloff_radius = max(center_x, center_y)
        falloff = np.clip(1 - (dist * (falloff_radius / inner_radius)) * 0.5, 0, 1)

        # Transpose falloff to match (width, height)
        falloff = falloff.T

        # Apply the color gradient
        for i in range(3):
            arr[..., i] = (np.array([0, 175, 185])[i] * falloff).astype(np.uint8)

        pygame.surfarray.blit_array(surf, arr)
        self.gameDisplay.blit(surf, (0, 0))
    
    def makeBorder(self):
        """Draw the border around the game area."""
        # Draw sides
        for x in range(self.min_width // 16 - 3):
            self.gameDisplay.blit(self.borderS, (self.offsetX + x * 16, self.offsetY - 33))  # Top side
            self.gameDisplay.blit(pygame.transform.rotate(self.borderS, 180), (self.offsetX + x * 16, self.offsetY + self.min_height - 66))  # Bottom side
        for y in range(self.min_height // 16 - 3):
            self.gameDisplay.blit(pygame.transform.rotate(self.borderS, 90), (self.offsetX - 33, self.offsetY + y * 16))  # Left side
            self.gameDisplay.blit(pygame.transform.rotate(self.borderS, 270), (self.offsetX + self.min_width - 66, self.offsetY + y * 16))  # Right side

        # Draw corners
        self.gameDisplay.blit(self.borderC, (self.offsetX - 33, self.offsetY - 33))  # Top-left
        self.gameDisplay.blit(pygame.transform.rotate(self.borderC, 270), (self.offsetX + self.min_width - 66, self.offsetY - 33))  # Top-right
        self.gameDisplay.blit(pygame.transform.rotate(self.borderC, 90), (self.offsetX - 33, self.offsetY + self.min_height - 66))  # Bottom-left
        self.gameDisplay.blit(pygame.transform.rotate(self.borderC, 180), (self.offsetX + self.min_width - 66, self.offsetY + self.min_height - 66))  # Bottom-right

    def placeBack(self, x: int, y: int): #Place the background of the cell
        """Draw the background texture for a cell at position (x, y)."""
        self.gameDisplay.blit(self.background, (x * self.cellSize + self.offsetX, y * self.cellSize + self.offsetY))

    def placeCell(self, x: int, y: int, overlay=False): #Place the cell
        """Draw a game cell at position (x, y) with optional overlay effect."""
        if self.complexLayout[y][x] is not None:
            self.gameDisplay.blit(self.complexLayout[y][x].render(scale=(self.cellSize,self.cellSize),overlay=overlay), (x*self.cellSize + self.offsetX, y*self.cellSize + self.offsetY))

    def drawPocketCells(self): #Draw the cells in the pocket
        """Render the inventory panel showing available cells and their quantities."""
        # Draw background grid for 15 pocket slots (3x5 grid)
        for i in range(15):
            x = i % 3
            y = i // 3
            self.gameDisplay.blit(self.backgroundPocket, (self.levelData["width"] * self.cellSize + 5 + x*self.cellSize*2 + self.offsetX, y*self.cellSize*2 + self.offsetY))
            # Highlight currently selected pocket slot
            if i == self.selectedPocket:
                self.gameDisplay.blit(self.highlightPocket, (self.levelData["width"] * self.cellSize + 5 + x*self.cellSize*2 +self.offsetX, y*self.cellSize*2 + self.offsetY))
        # Draw the actual cell items and their quantities
        for i, (cell, qty) in enumerate(self.pocket.items()):
            x = i % 3
            y = i // 3
            # Render the cell image in the pocket slot
            self.gameDisplay.blit(
                cells[self.cellData[cell]["type"]](data=self.cellData[cell]["data"]).render(scale=(self.cellSize*2,self.cellSize*2)),
                (self.levelData["width"] * self.cellSize + 5 + x*self.cellSize*2 + self.offsetX, y*self.cellSize*2 + self.offsetY)
            )
            # Display quantity indicator for available items
            if qty > 0:
                qty= "0" + str(qty)  # Format quantity as 2-digit string
                indicator = self.qty.copy()
                # Draw cyan-colored quantity numbers
                indicator.blit(multiply(self.numbers[int(qty[-2])], (0,255,255)), (13, 33))
                indicator.blit(multiply(self.numbers[int(qty[-1])], (0,255,255)), (23, 33))
                self.gameDisplay.blit(pygame.transform.scale(indicator, (self.cellSize*2, self.cellSize*2)), (self.levelData["width"] * self.cellSize + 5 + x*self.cellSize*2 + self.offsetX, y*self.cellSize*2 + self.offsetY))
            else:
                # Display "00" in orange when item is out of stock
                qty= "00"
                indicator = self.qty.copy()
                indicator.blit(multiply(self.numbers[0], (255,155,0)), (13, 33))
                indicator.blit(multiply(self.numbers[0], (255,155,0)), (23, 33))
                self.gameDisplay.blit(pygame.transform.scale(indicator, (self.cellSize*2, self.cellSize*2)), (self.levelData["width"] * self.cellSize + 5 + x*self.cellSize*2 + self.offsetX, y*self.cellSize*2 + self.offsetY))

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

        # Get mouse position and convert to grid coordinates
        mouseX, mouseY = pygame.mouse.get_pos()
        x, y = (mouseX - self.offsetX) // self.cellSize, (mouseY - self.offsetY) // self.cellSize
        # Handle mouse button clicks
        if event.type == pygame.MOUSEBUTTONDOWN :
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
                    x, y= (mouseX - (self.levelData["width"] * self.cellSize + 5 + self.offsetX)) // (self.cellSize*2), (mouseY - self.offsetY) // (self.cellSize*2)
                    if x >= 0 and y >= 0 and x < 3 and y < 5 and (y * 3 + x) < len(self.pocket):
                        self.selectedPocket = y * 3 + x
                        self.drawPocketCells()
            # Right mouse button - remove cells and return them to inventory
            elif event.button == 3:
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    # Remove cell if it exists in inventory system
                    if self.complexLayout[y][x].name in self.pocket:
                        self.pocket[self.complexLayout[y][x].name] += 1
                        self.complexLayout[y][x] = self.complexLayout[y][x].convert(other=cells["default"], name="D")
                        self.calculate()
                        self.drawPocketCells()

        # Handle keyboard input
        elif event.type == pygame.KEYDOWN:
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
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.levelData["layout"][y][x] == "D":
                    now = self.complexLayout[y][x].direction
                    newDir = 0 if now == 3 else now + 1
                    self.complexLayout[y][x].changeDirection(newDir)
                    self.calculate()

            # F key - flip cell under mouse cursor
            elif event.key == pygame.K_f:
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"] and self.levelData["layout"][y][x] == "D":
                    if self.complexLayout[y][x].flip():
                        self.calculate()

            # E key - show overlay for cell under mouse cursor
            elif event.key == pygame.K_e:
                if x >= 0 and y >= 0 and x < self.levelData["width"] and y < self.levelData["height"]:
                    self.placeCell(x, y, overlay=True)

            # ESC key - abrir menú de pausa con controles y botones
            elif event.key == pygame.K_ESCAPE:
                paused = True
                font_title = pygame.font.SysFont('Arial', 50)
                font_text = pygame.font.SysFont('Arial', 32)
                font_button = pygame.font.SysFont('Arial', 25)
                while paused:
                    self.gameDisplay.fill((30, 30, 50))
                    # Título
                    title = font_title.render("PAUSA", True, (50, 200, 255))
                    self.gameDisplay.blit(title, (self.min_width // 2 - title.get_width() // 2, 60))
                    # Controles
                    controles = [
                        "Controles:",
                        "WASD: Mover selección de inventario",
                        "Click Izq: Colocar celda",
                        "Click Der: Quitar celda",
                        "R: Rotar celda",
                        "F: Voltear celda",
                        "E: Overlay de celda",
                        "ESC: Pausa",
                    ]
                    for i, txt in enumerate(controles):
                        line = font_text.render(txt, True, (200, 200, 200))
                        self.gameDisplay.blit(line, (self.min_width // 2 - line.get_width() // 2, 140 + i * 35))
                    btn_continue = pygame.Rect(self.min_width // 2 - 160, 500, 140, 60) #estos son los botones
                    btn_exit = pygame.Rect(self.min_width // 2 + 20, 500, 140, 60)
                    pygame.draw.rect(self.gameDisplay, (50, 200, 100), btn_continue)
                    pygame.draw.rect(self.gameDisplay, (200, 50, 50), btn_exit)
                    txt_continue = font_button.render("Continuar", True, (0, 0, 0))
                    txt_exit = font_button.render("Salir", True, (0, 0, 0))
                    self.gameDisplay.blit(txt_continue, (btn_continue.x + 10, btn_continue.y + 10))
                    self.gameDisplay.blit(txt_exit, (btn_exit.x + 35, btn_exit.y + 10))
                    pygame.display.update()
                    for pause_event in pygame.event.get(): # Manejo de eventos en pausa
                        if pause_event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        elif pause_event.type == pygame.KEYDOWN:
                            if pause_event.key == pygame.K_ESCAPE:
                                paused = False
                        elif pause_event.type == pygame.MOUSEBUTTONDOWN and pause_event.button == 1:
                            mx, my = pygame.mouse.get_pos()
                            if btn_continue.collidepoint(mx, my):
                                paused = False
                            elif btn_exit.collidepoint(mx, my):
                                return

        # Check if level is completed - all final cells must be completed
        for f in self.finals:
            if not f.isCompleated:
                break
        else:
            # Display level completion message
            font = pygame.font.SysFont('Arial', 64)
            text = font.render('Level Completed!', True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.min_width // 2, self.min_height // 2))
            self.gameDisplay.blit(text, text_rect)
            pygame.display.update()
            sleep(2)
            return "win"

        return "continue"

    def load(self, level, startSize=(0,0), texts=None):
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
        if texts is None:
            self.min_width = self.levelData["width"] * self.cellSize + 5 + self.cellSize * 6 + 66
            self.min_height = self.levelData["height"] * self.cellSize + 66
        else:
            self.min_width = self.levelData["width"] * self.cellSize + 5 + self.cellSize * 6 + 66
            self.min_height = self.levelData["height"] * self.cellSize + 130 + 66
        self.texts = texts
        self.offsetX = (max(startSize[0], self.min_width) - self.min_width) // 2 + 33
        self.offsetY = (max(startSize[1], self.min_height) - self.min_height) // 2 + 33
        self.gameDisplay = pygame.display.set_mode((max(self.min_width, startSize[0]), max(self.min_height, startSize[1])), pygame.RESIZABLE)
        pygame.display.set_caption(f"Light Hack")
        
        # Load and scale background textures
        self.borderC = pygame.image.load("assets/border/corner.png").convert_alpha()
        self.borderS = pygame.image.load("assets/border/side.png").convert_alpha()
        self.background = pygame.image.load("assets/background.png")
        self.backgroundPocket = pygame.transform.scale(self.background, (self.cellSize*2, self.cellSize*2))
        self.background = pygame.transform.scale(self.background, (self.cellSize, self.cellSize))
        self.qty = pygame.image.load("assets/indicators/qty.png").convert_alpha()
        self.numbers= tuple(pygame.image.load(f"assets/{i}").convert_alpha() for i in numbers)
        highlight = pygame.image.load("assets/highlight.png").convert_alpha()
        self.highlight = pygame.transform.scale(highlight, (self.cellSize, self.cellSize))
        self.highlightPocket = pygame.transform.scale(highlight, (self.cellSize*2, self.cellSize*2))
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

        self.makeGradient()
        self.makeBorder()

        # Draw initial cells
        for y in range(self.levelData["height"]):
            for x in range(self.levelData["width"]):
                self.placeBack(x, y)
                self.placeCell(x, y)

        # Add a separator after everything
        pygame.draw.rect(
                    self.gameDisplay, (0, 75, 85),
                    (self.levelData["width"] * self.cellSize + self.offsetX, self.offsetY, 5, self.levelData["height"] * self.cellSize)
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

        # Render instructional texts if provided
        if self.texts is not None:
            font= pygame.font.Font(None, int(screenHeight / 45))
            for i, txt in enumerate(self.texts):
                rendered_txt = font.render(txt, True, (5,25,55))
                self.gameDisplay.blit(rendered_txt, (self.offsetX + 10, self.offsetY + self.min_height - 188 + i * 20))
        pygame.display.update()

    def play(self):
        """Main game loop that handles events, input, and display updates."""
        # Track mouse hover position for cell highlighting
        pastCol = None
        pastRow = None
        out = "continue"
        
        # Main game loop
        while out == "continue":
            # Handle all pygame events
            try:
                for event in pygame.event.get():
                    # Handle window close button
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    # Process user input and check for game exit conditions
                    out= self.keyHandler(event)
                    if out == "exit" or out == "win":
                        break
            except SystemError:
                pass

            # ---------- CELL HIGHLIGHT SYSTEM -------------
            # Track mouse position and highlight hovered cells
            mouseX, mouseY = pygame.mouse.get_pos()
            col, row = (mouseX - self.offsetX) // self.cellSize, (mouseY - self.offsetY) // self.cellSize
            
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
                    self.gameDisplay.blit(self.highlight, (col * self.cellSize + self.offsetX, row * self.cellSize + self.offsetY))
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
                self.offsetX = (self.lastWidth - self.min_width) // 2 + 33
                self.offsetY = (self.lastHeight - self.min_height) // 2 + 33

                # Redraw gradient background
                self.makeGradient()

                # Redraw border around game area
                self.makeBorder()

                # Redraw entire game grid after resize
                for y in range(self.levelData["height"]):
                    for x in range(self.levelData["width"]):
                        self.placeBack(x, y)
                        self.placeCell(x, y)

                # Redraw separator between game area and inventory
                pygame.draw.rect(
                    self.gameDisplay, (0, 75, 85),
                    (self.levelData["width"] * self.cellSize + self.offsetX, self.offsetY, 15, self.levelData["height"] * self.cellSize)
                )

                # Redraw inventory panel
                self.drawPocketCells()

                # Redraw texts if they exist
                if self.texts is not None:
                    font= pygame.font.Font(None,int(screenHeight / 45))
                    for i, txt in enumerate(self.texts):
                        rendered_txt = font.render(txt, True, (5,25,55))
                        self.gameDisplay.blit(rendered_txt, (self.offsetX + 10, self.offsetY + self.min_height - 188 + i * 20))

            pygame.display.update()
        
        pygame.display.quit()
        pygame.quit()
        return out

# Main program execution
if __name__ == "__main__":
    # Create game instance and run a hard level
    game = LightHackGame()
    game.load("testing")  # Load level from JSON file
    game.play()  # Start the game loop