#import
import pygame
import sys
import os
import time
import random
pygame.font.init()

width = 1250
height = 750

size = (width, height)
screen = pygame.display.set_mode(size) #WIN
pygame.display.set_caption("SpaceGame")


#загружаем файлы из assets

spaceShip_red = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
spaceShip_green = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
spaceShip_blue = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

spaceShip_yellow = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

laser_red = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
laser_yellow = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
laser_green = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
laser_blue = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))

#BG
background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (size))


#общий класс для кораблей,от него наследуют корабли врагов и корабль игрока
class Ship:
    def __init__(self, x, y, hp=100):  #присваиваем общие характеристики всех кораблей
        self.x = x
        self.y = y
        self.hp = hp
        self.img_ship = None
        self.img_laser = None
        self.lasers = []
        self.coolD_counter = 0


    def draw(self, window):
        screen.blit(self.img_ship, (self.x, self.y))


    def get_width(self):
        return self.img_ship.get_width()

    def get_height(self):
        return self.img_ship.get_height()


#класс player наследует от ship
class Player(Ship):
    def __init__(self, x, y, hp=100):
        super().__init__(x, y, hp) #используем метод инит из ship
        self.img_ship = spaceShip_yellow
        self.img_laser = laser_yellow
        self.mask = pygame.mask.from_surface(self.img_ship)#коллизия
        self.hp_max = hp



# как их запрограммировать ччто бы они следовали за тобой,стреляли по игроку?
# типы врагов
# мины/пилоты камикадзе что не могут стрелять но следуют за игроком
#снайперы,что редко стреляют,но выстреливают один сплошной луч+держутся на расстоянии от гг
#
#
#ПЕРЕДЕЛАТЬ из enemy идут классы red enemy,blue и тд
#у каждого корабля свои свойства(крансые=мины и тд)
class Enemy(Ship):
    color_map = {
        "red": (spaceShip_red, laser_red),
        "green":(spaceShip_green, laser_green),
        "blue":(spaceShip_blue, laser_blue)
    }

    def __init__(self, x, y, color, hp=100):
        super().__init__(x, y, hp)
        self.img_ship, self.img_laser = self.color_map[color]

    def move(self, vel):
        self.y += vel


def main():
    game = True
    lives = 4
    font = pygame.font.SysFont("comicsans", 50)
    fps = 60
    clock = pygame.time.Clock()

    #враги
    enemies = []
    wave_length = 5


    player = Player(300, 650)
    player_velocity = 5


    def window_redraw():
        screen.blit(background, (0, 0)) #на surface screen перемещаем изобр background на координаты 0, 0
        label_lives = font.render(f"{lives} lives", 1, (255, 255, 255)) #создаем surface с текстом
        screen.blit(label_lives, (10, 10)) # накладываем surface на экран

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)



        pygame.display.update()


    while game:
        clock.tick(fps)

        # также здесь можно организовать переходна новый уровень
        #спавн врагов
        if len(enemies) == 0:
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width-100), random.randrange(10, 150), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
                # print(enemy.color_map)
            #game = False


        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                game = False

#управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_velocity >0:
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < width:
            player.x += player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() < height:
            player.y += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity >0:
            player.y -= player_velocity

        window_redraw()







main()





















