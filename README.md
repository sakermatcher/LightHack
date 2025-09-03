# LightHack

LightHack is a puzzle game developed as a university project at Tec de Monterrey Campus Puebla. The objective is to manipulate beams of colored light using various optical elements to solve increasingly complex puzzles.

## Features

- **Grid-based puzzles:** Each level is a grid where you place and rotate cells to guide light beams.
- **Optical elements:** Use mirrors, prisms, glass, and lasers to bend, split, and combine colored light.
- **Color mixing:** Experiment with RGB color mixing to achieve target results.
- **Level editor:** Create and customize your own levels.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/LightHack.git
   cd LightHack
   ```

2. **Install dependencies:**
   - Python 3.10+ is required.
   - Install [pygame](https://www.pygame.org/news) and any other dependencies:
     ```sh
     pip install pygame
     ```

3. **Run the game:**
   ```sh
   python play.py
   ```

## How to Play

- **Objective:** Use lasers to direct colored beams to targets by placing and rotating cells.
- **Controls:**
    *Note that this controls are temporary for testing purposes, until a proper menu and control scheme is implemented.*
  - Mouse: Select and place cells.
  - Keyboard:
    - `SPACE`: Convert cell to mirror.
    - `E`: Convert cell to prism.
    - `W`: Convert cell to glass.
    - `A`: Place special glass.
    - `R`: Rotate cell.
    - `Q`: Reset cell to default.
    - `TAB`: Highlight cell.
    - `DELETE`: Exit level.
- **Level Editor:** Run `python levelMaker.py` to design custom levels.

## Project Structure

```
LightHack/
├── assets/           # Images and textures
├── cells/            # Cell logic and rendering
├── levels/           # Level data (JSON)
├── play.py           # Main game loop
├── levelMaker.py     # Level editor
├── README.md         # This file
└── ...
```

## Contributing

For the moment its just me but contributions are always welcome! Please open issues or submit pull requests for bug fixes, features, or improvements.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Credits

- Developed by Juan Pablo Pagán for Tec de Monterrey Campus Puebla.
- Special thanks to all contributors and testers.

---
Enjoy bending light and solving puzzles!