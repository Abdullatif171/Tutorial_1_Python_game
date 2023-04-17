import pygame
import os
import random
import csv
import button

pygame.init()

# creat the screen
SCREEN_WIDTH = 800
SCREEN_HIGH = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGH))
pygame.display.set_caption("JumpmanC4")

# set framerate
clock = pygame.time.Clock()
FPS = 60
toplamscore = 0
sayı = 0

# define game veriable
SCROLL_THRESH = 200
ROWS = 16
COLS = 20
TILE_SIZE = SCREEN_HIGH // ROWS
TILE_TYPES = 7
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

# define player action veriable
move_left = False
move_right = False
climbup = False
climbdown = False

# load music and sounds
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.08)

music_fx = pygame.mixer.Sound('audio/music.mp3')
music_fx.set_volume(0.1)

# Health Bar
Healthbar = pygame.image.load('img/Healthbar.png').convert_alpha()
# button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
# background
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
coin_box_img = pygame.image.load('img/icons/coin.png').convert_alpha()
fireball_box_img = pygame.image.load('img/icons/fireball.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'coin': coin_box_img,
    'fireball': fireball_box_img
}

# define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# define font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    screen.blit(sky_img, ((x / 100) - bg_scroll, 0))


# function to reset level
def reset_level():
    enemy_group.empty()
    item_box_group.empty()
    ladder_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


class Man(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.GRAVITY = 0.75
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.health = 100
        self.max_health = self.health
        self.coin = 0
        self.bonusscore = 1500
        self.zamanlayıcı = 0
        self.direction = 1
        self.vel_y = 0
        self.climb = False
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'death', 'climb']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()

    def moving(self, move_left, move_right, climbup, climbdown):
        # reset mevement veriables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement veriables if moving left or right
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # climb
        if pygame.sprite.spritecollide(player, ladder_group, False):
            player.climb = True
            player.GRAVITY = 0
            if climbup:
                dy = -self.speed
                self.vel_y = -1
                if pygame.sprite.spritecollide(player, ladder_group, False):
                    self.vel_y = 0

            if climbdown:
                dy = self.speed
                self.vel_y = 1
                if pygame.sprite.spritecollide(player, ladder_group, False):
                    self.vel_y = 0
        else:
            player.GRAVITY = 0.75

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += player.GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with exit
        level_complete = False
        self.num_coin = 12
        if player.coin == player.num_coin * 100:
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HIGH:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check in enought time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1
        # if the animation has run out the reset back to start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def ai(self):
        self.move_direction = 3
        self.rect.x += self.move_direction
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH - 1000

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)



class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile == 1:
                        self.obstacle_list.append(tile_data)
                    elif tile == 0:
                        lader = ladder(img, x * TILE_SIZE, y * TILE_SIZE)
                        ladder_group.add(lader)
                    elif tile == 2:  # create player
                        player = Man('player', x * TILE_SIZE, y * TILE_SIZE, 0.4, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 3:  # create enemies
                        enemy = Man('enemy', x * TILE_SIZE, y * TILE_SIZE, 0.4, 4)
                        enemy_group.add(enemy)
                    elif tile == 5:  # create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 4:  # create coin
                        item_box = ItemBox('coin', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])


class ladder(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
                # delete the item box
                self.kill()
            elif self.item_type == 'coin':
                player.coin += 100
                # delete the item box
                self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HIGH))
            pygame.draw.rect(screen, self.colour,
                             (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HIGH))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HIGH // 2))
            pygame.draw.rect(screen, self.colour,
                             (0, SCREEN_HIGH // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HIGH))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = item_boxes['fireball']
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-1000, -500)
        self.speedy = random.randrange(3, 8)
        self.speedx = random.randrange(-2, 2)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HIGH + 10:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-1000, -500)
            self.speedy = random.randrange(3, 8)



# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

# create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HIGH // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HIGH // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HIGH // 2 - 50, restart_img, 2)

# create sprite groups
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
ladder_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
mob_group = pygame.sprite.Group()
for i in range(3):
    m = Mob()
    mob_group.add(m)

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        # draw menu
        screen.fill(BG)
        # add buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        # update background
        draw_bg()
        # draw world map
        world.draw()
        # show player health
        health_bar.draw(player.health)
        # show score
        draw_text(f'Score: {player.coin}', font, WHITE, 10, 60)

        player.update()
        player.draw()

        # Muzik
        if player.health > 0:
            music_fx.play()
        else:
            music_fx.stop()

        if level == 2 or level == 3:
            for enemy in enemy_group:
                enemy.ai()
                enemy.update()
                enemy.draw()

        item_box_group.update()
        ladder_group.update()
        exit_group.update()

        item_box_group.draw(screen)
        ladder_group.draw(screen)
        exit_group.draw(screen)

        # Bonus score
        player.zamanlayıcı += 1
        if player.zamanlayıcı == sayı + 300:
            player.bonusscore -= 100
            sayı += 300

        if level == 1:
            draw_text(f'Level: 1', font, WHITE, 10, 35)
            draw_text(f'Bonus Score: {player.bonusscore}', font, WHITE, 10, 110)
            draw_text(f'Toplam Score: {toplamscore}', font, WHITE, 10, 85)
            mob_group.update()
            mob_group.draw(screen)
            if pygame.sprite.spritecollide(player, mob_group, False):
                player.health -= 100

        if level == 2:
            draw_text(f'Level: 2', font, WHITE, 10, 35)
            draw_text(f'Bonus Score: {player.bonusscore}', font, WHITE, 10, 110)
            draw_text(f'Toplam Score: {toplamscore}', font, WHITE, 10, 85)
            if pygame.sprite.spritecollide(player, enemy_group, False):
                player.health -= 100

        if level == 3:
            draw_text(f'Level: 3', font, WHITE, 10, 35)
            draw_text(f'Bonus Score: {player.bonusscore}', font, WHITE, 10, 110)
            draw_text(f'Toplam Score: {toplamscore}', font, WHITE, 10, 85)
            mob_group.update()
            mob_group.draw(screen)
            if pygame.sprite.spritecollide(player, mob_group, False):
                player.health -= 3
            if pygame.sprite.spritecollide(player, enemy_group, False):
                player.health -= 3

        # show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # update player action
        if player.alive:
            if player.in_air:
                player.update_action(2)  # 2: jump
            elif move_left or move_right:
                player.update_action(1)  # 1: walk
            elif climbup or climbdown:
                player.update_action(4)  # 1: walk
            else:
                player.update_action(0)  # 0: Idle
            screen_scroll, level_complete = player.moving(move_left, move_right, climbup, climbdown)
            bg_scroll -= screen_scroll

            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                toplamscore = player.bonusscore + player.coin + toplamscore
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    # load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keybord presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_w and player.climb:
                climbup = True
            if event.key == pygame.K_s and player.climb:
                climbdown = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # keybord button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
                player.climb = False
            if event.key == pygame.K_d:
                move_right = False
                player.climb = False
            if event.key == pygame.K_w:
                climbup = False
                player.climb = False
            if event.key == pygame.K_s:
                climbdown = False
                player.climb = False

    pygame.display.update()

pygame.quit()
