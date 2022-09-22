import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 800,600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Game")

    #load in images
RED_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
    #player 
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
    #lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
    #background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

############
## LASERS
############
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel 

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj) 

###########
## SHIP
###########
class Ship:
    COOLDOWN = 20 

    def __init__(self, x, y, health=100):
            #so ship can store x, y, and health
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser) 

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img) 
            self.lasers.append(laser) 
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

############
## PLAYER
############
class Player(Ship): 
        #can use ship inside of player
        #initializes like Ship, but adds extension
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) 
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


###########
## ENEMIES
###########
class Enemy(Ship):
    COLOR_COMBO = {
                "red": (RED_SHIP, RED_LASER),
                "green": (GREEN_SHIP, GREEN_LASER),
                "blue": (BLUE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_COMBO[color]
        self.mask = pygame.mask.from_surface(self.ship_img) 

        #moves enemy ships down
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img) 
            self.lasers.append(laser) 
            self.cool_down_counter = 1

def collide(obj1, obj2):
        #given 2 masks, do they overlap or not
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

###########
## RUN GAME
###########
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
        #choose font and size
    main_font = pygame.font.SysFont("Times New Roman", 20) 
    lost_font = pygame.font.SysFont("Times New Roman", 50)

    enemies = []
    wave_length = 5
    shoot_prob = 10
        #velocities
    enemy_vel = 1
    player_vel = 4
    laser_vel = 4

    player = Player(350, 480)

    clock = pygame.time.Clock()

    lost = False 
    lost_count = 0

    def redraw_window():
        WINDOW.blit(BG, (0,0))  
            #draw text (turn text into surface, put it on screen)
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 225, 225)) #(r,g,b)
        level_label = main_font.render(f"Level: {level}", 1, (225, 225, 225))

        WINDOW.blit(lives_label, (10, 10)) #top left corner
        WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

            #draw in enemies and player
        for enemy in enemies:
            enemy.draw(WINDOW)

        player.draw(WINDOW)

        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (225, 225, 225))
            WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 250))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue 
        
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            enemy_vel += 0.1
            player_vel += 0.1
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
                #if x is pressed, stop game
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()     #checks 60 times every second if a key is pressed
        if keys[pygame.K_a] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: #up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel) 
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 5*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies) 

def main_menu():
    title_font = pygame.font.SysFont("Times New Roman", 60)
    run = True
    while run:
        WINDOW.blit(BG, (0, 0))
        title_label = title_font.render("Press enter to begin...", 1, (255, 255, 255))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 250))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_RETURN:
                    main()

    pygame.quit()

main_menu()