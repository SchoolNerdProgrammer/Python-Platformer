import os, random, math, pygame
from os import listdir
from os.path import isfile, join
import json

pygame.init()
pygame.display.set_caption("Platformer for AI to play.")

WIDTH, HEIGHT = 1000, 800
FPS = 60
VEL = 5

win = pygame.display.set_mode((WIDTH, HEIGHT))





class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacter","MaskDude", 32, 32, True)


    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel -= vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel += vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count // fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, self.rect)



def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

##load_sprite_sheets("MainCharacter","MaskDude", 32, 32, True) - needs to be passed to player file to be used as class variable sprites
def load_sprite_sheets(dir1, dir2, width, height, direction=False):  # This loads the images in the assets folder.
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()  # convert.alpha() is for generating a transparent background where possible
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    print(all_sprites)
    return all_sprites

def convert_to_string(all_sprites):
        vals = all_sprites[0]
        print(vals)


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()  # the underscores are to prevent the top left corner coords from being passed from get.rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(win, background, bg_image, player):
    for tile in background:
        win.blit(bg_image, tile)

    player.draw(win)
    pygame.display.update()


def handle_move(player):
    keys = pygame.key.get_pressed()
    # print(keys)
    player.x_vel = 0
    if keys[pygame.K_LEFT]:
        player.move_left(VEL)
    elif keys[pygame.K_RIGHT]:
        player.move_right(VEL)


def main(win):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")
    player = Player(100, 100, 64, 64)
    all_sprites = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)##
    convert_to_string(all_sprites)
    run = True

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        player.loop(FPS)
        handle_move(player)
        draw(win, background, bg_image, player)


    pygame.quit()


if __name__ == "__main__":
    main(win)
