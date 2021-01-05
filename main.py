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
screen = pygame.display.set_mode(size)
pygame.display.set_caption("SpaceGame")


#загружаем файлы из assets

#!!! В КОНЦЕ КАЖДОГО image.load должен быть .convert() !!

spaceShip_red = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
spaceShip_green = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
spaceShip_blue = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

spaceShip_yellow = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

laser_red = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
laser_yellow = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
laser_green = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
laser_blue = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))


background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (size))


#общий класс для кораблей,от него наследуют корабли врагов и корабль игрока
class Ship:
    def __init__(self, x, y, hp=100):  #присваиваем общие характеристики всех кораблей
        self.x = x
        self.y = y
        self.hp = hp
        self.img_ship = None
        self.img_laser = None
        self.lasers = []   #тут будут хранится разные лазеры для разных классов кораблей
        self.coolD_counter = 0


    def draw(self, window):
        screen.blit(self.img_ship, (self.x, self.y))


    def get_width(self):
        return self.img_ship.get_width()

    def get_height(self):
        return self.img_ship.get_height()


    def give_position(self):
        return self.x, self.y


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
# мины/пилоты камикадзе что не могут стрелять но следуют за игроком и взрываются рядом с ним

#снайперы,что редко стреляют,но выстреливают один сплошной луч+держутся на расстоянии от гг
#или пусть снафперы делают один выстрел и отлетают в рандомную сторону
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

    # def move(self, vel):  #для каждого типа корабля свое передвижение,так что это немного бесполезно
    #     self.y += vel


#камикадзе- идут напрямую на игрока,медленные,при сближении с гг или смерти взрываются!!наносят урон как игроку так и врагам!!
class RedEnemy(Enemy):


    def __init__(self, x, y, color, hp = 100):
        super().__init__(x, y, color, hp)

#может переименовать move в attack?или отдельный метод attack, что внутри себя использует move?+++после части #управление
#вместо move вписать attack
    def move(self, vel = 1):  #корабль следует медленно за игроком
        self.x -= vel

    def attack(self):
        self.move()

#проблема как достать координату игроку в класс Redenemy


#снайпер
class BlueEnemy(Enemy):
    def __init__(self, x, y, color, hp = 100):
        super().__init__(x, y, color, hp)


    def move(self, vel = 1):  #корабль отлетает от игрока в сторону и снова делает выстрел
        self.y -= vel

    def attack(self):
        self.move()


#подумай, лазер будет иметь в себе расположение игрока,или это будет определяться в методе attack(скорее всего в атак,ведь
#у каждого корабля свой стиль атаки может быть
class Laser:
    def __init__(self, x, y, img):
        pass





def main():
    game = True
    lives = 4
    font = pygame.font.SysFont("comicsans", 50)
    font_game_over = pygame.font.SysFont("comicsans", 70)  #?поменять цвет?
    fps = 60
    clock = pygame.time.Clock()

    #враги
    enemies = []
    wave_length = 5


    player = Player(300, 650)
    player_velocity = 5
    game_over = False    #перемення что бы знать когда создавать меню при проигрыше,перезагружать игру
#________________________________________

    def window_redraw():
        screen.blit(background, (0, 0)) #на surface screen перемещаем изобр background на координаты 0, 0
        label_lives = font.render(f"{lives} lives", 1, (255, 255, 255)) #создаем surface с текстом
        screen.blit(label_lives, (10, 10)) # накладываем surface на экран

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if game_over:    #ввсти выход в меню и удалить всех врагов+вернуть hp игроку
            label_game_over = font.render("GAME OVER BUDDY", 1, (255, 255, 255))
            screen.blit(label_game_over, (width/2-label_game_over.get_width()/2, height/2))


        pygame.display.update()
#_____________________________________

    while game:
        clock.tick(fps)

        if lives <= 0 or player.hp <= 0:  #!!game over screen!!  game_over = true. ввсти выход в меню и удалить всех врагов+вернуть hp игроку
            game_over = True


        # также здесь можно организовать переходна новый уровень
        #спавн врагов  !!!на будущие- сделай спавн врагов рандомным,что бы на каждой новой волне было разное кол врагов
        # random.choice(["red","blue", "green"])


        if len(enemies) == 0:  #также если игрок все еще не начал новую игру(game_over=true)не спавнить врагов
            for i in range(wave_length):
                enemy = RedEnemy(random.randrange(50, width-100), random.randrange(10, 150), "red") #!!!!!!!!!!!!!!!redenemy = enemy
                enemies.append(enemy)
                # print(enemy.color_map)

            for i in range(wave_length):
                enemy = BlueEnemy(random.randrange(50, width - 100), random.randrange(10, 150),
                              random.choice(["blue"]))  #!!!
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


# здесь нужно ввест координату игрока в метод attack(сделал метод give_position у ship- можно применить у всех кораблей)
        for enemy in enemies:
            enemy.attack()  # 2 = enemy velocity



        #print(player.give_position())
        #print(enemies[0].give_position())
        window_redraw()



main()

# как получить расположение мыши
# pg.mouse.get_pos()
#
#сделать коллизию - взрыв камикадзе
#сделать стрельу для корабля игрока и убийство врагов
#
#


















