import os, random, math, pygame
from os import listdir
from os.path import isfile, join
pygame.init()
pygame.display.set_caption("platformer for AI to play.")

WIDTH , HEIGHT = 1000,800
FPS = 60
PLAYER_VEL = 5

win = pygame.display.set_mode((WIDTH, HEIGHT))












def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _, _, width, height = image.get_rect()  # the underscores are to prevent the top left corner coords from being passed from get.rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles,image

def draw(win,background, bg_image):
    for tile in background:
        win.blit(bg_image, tile)

    pygame.display.update()

def main(win):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    run = True

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        draw(win,background,bg_image)
    pygame.quit()
if __name__ == "__main__":
    main(win)