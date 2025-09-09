from play import LightHackGame
import pygame

if __name__ == "__main__":
    while True:
        pygame.init()
        menu= pygame.display.set_mode((400,300))
        pygame.display.set_caption("LightHack Tutorials")
        font= pygame.font.Font(None, 36)
        text= font.render("Press T for tutorials", True, (255,255,255))
        menu.fill((0,0,0))
        menu.blit(text, (10,10))
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
            pygame.display.flip()

        pygame.quit()
        if out == "tut":
            for i in range(1, 7):
                game = LightHackGame()
                game.load(f"tutorials/tut{i}")
                game.play()
