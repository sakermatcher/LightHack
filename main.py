from play import LightHackGame
import pygame

tutTxt=[
    "Welcome to lightHack!, a puzzle game where you use light to win, you can see that there is a laser in the game with a certain power on Red, Green, and\nBlue ranging from 0-10 noted on the indicators in the corner of the laser, your objective is to get the needed power for the generator (you know how\nmuch you will need by its indicators), right now you have 1 mirror in your pocket which will bend light in 90 degrees. Use WASD to move your selection\nand click to place blocks. Right Click to remove blocks, R to rotate them, and E will show you the light on a specific cell.",
    "Here we have 5 power on the Red channel, but we need 10 to power the generator, the light lens empowers all channels passing through it by the number\non its indicator, you have to pass the light through the lens, because on its sides it will only break the beam",
    "Here we have 10 Blue and 10 Red on the laser, but we need 5 Blue and 5 Red, with the use of a dark lens, we can reduce the power of all channels by the\nnumber on its indicator, so we will pass the light through the dark lens to reduce both channels by 5",
    "The prism is a block that can be used to separate a light in its different channels by passing it through the prism on the multicolor section, here we have\n Yellow (Red and Green), but we only need Red, so we will pass the light through the prism and take the Red channel to the generator, note that\nthe prism has specific sides for each color, and one multicolor side so only a specific color can pass through each.",
    "The prism can also be used to combine different channels into one beam, here we have 10 Red and 10 Blue, but we need Magenta (Red and Blue), so we will\npass both beams through the prism to combine them into one, note that the prism has specific sides for each color, and one multicolor side.",
    "Here we will use one prism to separate the beam, then a lens to change just the Red channel and then another prism to combine the beam back together, so\nwe can get the needed power for the generator, you can use F to flip a prism (Red with Blue).",
    ""
]

if __name__ == "__main__":
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
            for i in ["lvlEz1", "a", "lvlHard1"]:
                game = LightHackGame()
                game.load(i)
                game.play()
