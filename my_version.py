import os, random, math, pygame
from os import listdir
from os.path import isfile, join
import random
from pygame import mixer
import time

pygame.init()
pygame.mixer.pre_init(44100, 16, 2, 256)
pygame.display.init()
pygame.display.set_caption("Platformer for AI to play.")

# sounds
BG_MUSIC = pygame.mixer.Sound(join("assets", "background-game-music.mp3"))
BG_MUSIC.set_volume(0.2)

HURT_SOUND = pygame.mixer.Sound(join("assets", "game-hurt.mp3"))
HURT_SOUND.set_volume(1)

# DEATH_SOUND = pygame.mixer.Sound(join("assets", "game-death-sound.mp3"))
# DEATH_SOUND.set_volume(1.0)

# JUMP_SOUND = pygame.mixer.Sound(join("assets", "game-jump-sound.mp3"))
# JUMP_SOUND.set_volume(1.0)

# GRASS_CRUNCH_RUN = pygame.mixer.Sound(join("assets", "game-grass-run-sound.mp3"))
# GRASS_CRUNCH_RUN.set_volume(0.2)


WIDTH, HEIGHT = 1000, 800
FPS = 60
VEL = 5

win = pygame.display.set_mode((WIDTH, HEIGHT))


def play_sound_fx(sound):
        sound.play()


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


##load_sprite_sheets("MainCharacters","MaskDude", 32, 32, True) - needs to be passed to player class to be used as class variable sprites
def load_sprite_sheets(dir1, dir2, width, height, direction=False):  # This loads the images in the assets folder.
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,
                                              image)).convert_alpha()  # convert.alpha() is for generating a transparent background where possible
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

    # print(all_sprites)
    return all_sprites


def load_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size,
                       size)  # change 96,0 to take different blocks  change size to change the width and height of the place you want to grab.
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 6

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = 100

    def gain_health(self, gain = 1):
        #(str(self.health) + "gain")
        if self.health < 100:
            self.health += gain
            if self.health > 100:
                self.health -= (self.health - 100)
    def lose_health(self,  loss = 5):
            self.health -= loss
            print(str(self.health) + "health in lose_health")
            if self.health < 1:
                self.die()

    def die(self):
        return True

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def was_hit(self):
        global timer
        self.hit = True
        self.hit_count = 0
        if timer > 1000:
            play_sound_fx(HURT_SOUND)
            timer = 0
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
        if self.y_vel < 9:
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.fall_count = 0
        self.y_vel *= -0.8

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        if self.x_vel != 0:
            sprite_sheet = "run"
        if self.y_vel != 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        if self.y_vel > (self.GRAVITY * 1.2):
            sprite_sheet = "fall"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def draw(self, win, offset_x, offset_y):

        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
        self.x = x
        self.y = y

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        # print(self.fire)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.fire)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()  # the underscores are to prevent the top left corner coords from being passed from get.rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(win, background, bg_image, player, objects, offset_x, offset_y):
    for tile in background:
        win.blit(bg_image, tile)

    for object in objects:
        object.draw(win, offset_x, offset_y)

    player.draw(win, offset_x, offset_y)
    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            if dy > 0.2 and player.rect.y + 0.01 * player.height <= object.rect.y:
                player.rect.y += 1
                #print(player.rect.y + player.height)
                #print("player bottom y")
                #print(object.rect.y)
                #print("object top left y")
                #print("collisions occured")
                player.rect.bottom = object.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = object.rect.bottom
                player.hit_head()
            collided_objects.append(object)
    return collided_objects


def collide_h(player, objects, dx):
    player.move(dx, -1)
    player.update()
    collided_object = None
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            collided_object = object
            break
    player.move(-dx, 1)
    player.update()

    return collided_object


def handle_move_collisions(player, objects, timer):
    keys = pygame.key.get_pressed()
    # print(keys)
    player.x_vel = 0
    collide_left = collide_h(player, objects, -VEL * 2)
    collide_right = collide_h(player, objects, VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(VEL)
    elif keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check_vertical = [*vertical_collide]
    to_check_horizontal = [collide_left, collide_right]
    for object_v in to_check_vertical:
        if object_v and (object_v.name == "fire"):
            player.was_hit()
    for object_h in to_check_horizontal:
        if object_h and (object_h.name == "spikes"):
            player.was_hit()



def main(win):
    global timer

    clock = pygame.time.Clock()
    clock_timer = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    timer = 0

    # music
    BG_MUSIC.play(-1, 0, 3000)

    block_size = 96

    fires = [Fire(block_size + 16, HEIGHT - block_size - 64, 16, 32),
             Fire(block_size * 4 + (block_size / 2) - 16, HEIGHT - (block_size * 8) - 64, 16, 32),
             Fire(block_size * 3.5 - 16, HEIGHT - block_size - 64, 16, 32)]

    for fire in fires:
        fire.on()

    player = Player(0, HEIGHT - (2 * block_size) - 400, 64, 64)
    # Block template = Block(x,y,size)
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in
             range(- 2 * WIDTH // block_size, (WIDTH * 5) // block_size)]
    blocks = [Block(0, HEIGHT - block_size * 2, block_size),
              Block(block_size * 3, HEIGHT - block_size * 4, block_size),
              Block(block_size * 4, HEIGHT - block_size * 4, block_size),
              Block(block_size * 5, HEIGHT - block_size * 5, block_size),
              Block(block_size * 6, HEIGHT - block_size * 6, block_size),
              Block(block_size * 7, HEIGHT - block_size * 7, block_size),
              Block(block_size * 8, HEIGHT - block_size * 7, block_size),
              Block(block_size * 8, HEIGHT - block_size * 8, block_size),  #####
              Block(block_size * 8, HEIGHT - block_size * 9, block_size),
              Block(block_size * 4, HEIGHT - block_size * 8, block_size),
              Block(block_size * 8, HEIGHT - block_size * 7, block_size),
              Block(block_size * 8, HEIGHT - block_size * 7, block_size), ]

    objects = [*floor, *blocks, *fires]

    offset_x = 0
    scroll_area_width = 250

    offset_y = 0
    scroll_area_height = 150

    run = True

    while run:
        clock.tick(FPS)
        dt = clock_timer.tick()
        timer += dt



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        player.loop(FPS)
        for fire in fires:
            fire.loop()
        handle_move_collisions(player, objects, timer)
        player.update_sprite()
        draw(win, background, bg_image, player, objects, offset_x, offset_y)

        if ((player.rect.right - offset_x) >= (WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x) <= scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel

        if (player.rect.top - offset_y) <= scroll_area_height and player.y_vel < 0:
            offset_y += player.y_vel
        elif (player.rect.bottom - offset_y) >= (HEIGHT - scroll_area_height - player.height) and player.y_vel > 0.7:
            offset_y += player.y_vel
        if player.die():
            pass  #In future will play animation for death, and allow a restart.
    pygame.mixer.quit()
    pygame.quit()


if __name__ == "__main__":
    main(win)
