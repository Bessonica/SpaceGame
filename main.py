#import
import pygame
import sys
import os
import time
import random
import math
pygame.font.init()

width = 1250
height = 750

size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("SpaceGame, Panfilov")


#загружаем файлы из assets



spaceShip_EnRed = pygame.image.load(os.path.join("assets", "Ship_EnemyRed.png"))
spaceShip_EnBlue = pygame.image.load(os.path.join("assets", "Ship_EnemyBlue.png"))

spaceShip_player = pygame.image.load(os.path.join("assets", "Ship_Player.png"))

laser_red = pygame.image.load(os.path.join("assets", "laser_red.png"))
laser_yellow = pygame.image.load(os.path.join("assets", "laser_yellow.png"))
laser_blue = pygame.image.load(os.path.join("assets", "laser_blue.png"))


background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.jpg")), (size))


#общий класс для кораблей,от него наследуют корабли врагов и корабль игрока
class Ship:
    CoolDown = 30


    def __init__(self, x, y, hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        self.img_ship = None
        self.img_laser = None
        self.lasers = []
        self.coolD_counter = 0

    def draw(self, window):
        screen.blit(self.img_ship, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(screen)


    def get_width(self):
        return self.img_ship.get_width()

    def get_height(self):
        return self.img_ship.get_height()


    def give_position(self):
        return self.x, self.y

    #тестовый метод,если у кораблей будут разные стили стрельбы то нужно делать метод для каждого класса,

    def shoot(self, direction):   #аргумент что будет решать куда пойдет лазер
        if self.coolD_counter == 0:
            laser = Laser(self.x, self.y, self.img_laser, direction)
            self.lasers.append(laser)
            self.coolD_counter = 1

    #нам не нужно что бы корабли могли спамить своими выстрелами,
    def cooldown(self):
        if self.coolD_counter >= self.CoolDown:
            self.coolD_counter = 0
        elif self.coolD_counter > 0:
            self.coolD_counter += 1


    def laser_draw(self, vel, obj):  #метод рисует лазеры и проверяет столкнулись они с обьектом,а поведение обьектов будет расписано в классах
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.notOn_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.hp -= 1
                self.lasers.remove(laser)



#класс player наследует от ship
class Player(Ship):
    def __init__(self, x, y,vel = 8 , hp=10):
        super().__init__(x, y, hp) #используем метод инит из ship
        self.img_ship = spaceShip_player
        self.img_laser = laser_yellow
        self.mask = pygame.mask.from_surface(self.img_ship)#коллизия!!!!
        self.hp_max = hp
        self.vel = vel


    def laser_draw(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.notOn_screen(height):
                self.lasers.remove(laser)
            else:
                for enShip in obj:
                    if laser.collision(enShip):
                        obj.remove(enShip)
                        if laser in self.lasers:
                            self.lasers.remove(laser)


    def hp_bar(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y + self.img_ship.get_height() + 10, self.img_ship.get_width(), 10))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y + self.img_ship.get_height() + 10, self.img_ship.get_width()*(self.hp/self.hp_max), 10))
        #print(self.x, self.y, "TEST")

    #взяли метод у родителя(ship) и добавили в него hp_bar()
    def draw(self, screen):
        super().draw(screen)
        self.hp_bar(screen)


    def stop(self):
        self.x = width + 50
        self.y = height + 50



#у каждого корабля свои свойства(крансые=мины и тд)
class Enemy(Ship):
    color_map = {
        "red": (spaceShip_EnRed, laser_red),
        "blue":(spaceShip_EnBlue, laser_blue)
    }

    def __init__(self, x, y, color, hp=100):
        super().__init__(x, y, hp)
        self.img_ship, self.img_laser = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.img_ship)



#камикадзе- идут напрямую на игрока,медленные,при сближении с гг взрываются наносят урон  игроку
class RedEnemy(Enemy):
    colorShip = "red"


    def __init__(self, x, y, color, player, hp = 100):
        super().__init__(x, y, color, hp)
        self.x = x
        self.y = y
        self.vec_start = pygame.math.Vector2((player.x, player.y))
        self.vec_end = pygame.math.Vector2((x, y)).normalize()


    def move(self, player, vel = 3):  #корабль следует медленно за игроком.
        v = Vector(player, self)
        # print("VECTOR POINTS",v.pointX, v.pointY)
        # print(v.Length())


        if v != 0:
            if v.pointX > 0:
                self.x += vel
                # self.y += vel
            elif v.pointX <= 0:
                self.x -= vel
            else:
                pass

            if v.pointY > 0:
                self.y += vel
                # self.y += vel
            elif v.pointY <= 0:
                self.y -= vel
            else:
                pass



    def attack(self, player, laserVel, obj):  #x, y =player pos.  self.x, self.y = ENEMY POS
        self.move(player)

#снайпер
class BlueEnemy(Enemy):
    colorShip = "blue"
    def __init__(self, x, y, color, hp = 100):
        super().__init__(x, y, color, hp)


    def move(self,player, vel = 5):  #корабль следует медленно за игроком
        pass

    def attack(self, player, laserVel, obj):   #здесь применяем move и laser
        self.laser_draw(laserVel, obj)
        #self.move()
        if random.randrange(0, 120) == 1:
            self.shoot("up")

            #print(x, y)

#____________________________________

#подумай, лазер будет иметь в себе расположение игрока,или это будет определяться в методе attack(скорее всего в атак,ведь
#у каждого корабля свой стиль атаки может быть
#
#в будущем сделать потомков лазера=разне виды выстрелов(сплошной луч,короткий,но быстрый выстрел и тд)
class Laser:
    def __init__(self, x, y, img, direction):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img) #коллизия
        self.direction = direction
        self.imgRev = pygame.transform.rotate(self.img, 90)
        self.imgRec = self.imgRev.get_rect(topleft=(self.x, self.y))


    def draw(self, screen):
         if self.direction == "up" or self.direction == "down":
            screen.blit(self.img, (self.x, self.y))
         elif self.direction == "left" or self.direction == "right":  #если влево или право поворачив использ повернутый лазер
             screen.blit(self.imgRev, (self.x, self.y))


    def move(self, vel):     #
        if self.direction == "up":
            self.y += vel
        elif self.direction == "down":
            self.y -= vel
        elif self.direction == "left":
            self.x += vel
        elif self.direction == "right":
            self.x -= vel


    def notOn_screen(self, height):  #удалить лазер если он вне экрана
        return  not(self.y <= height and self.y >= 0)



    # создать универс. функцию collide что будет смотреть-попал ли лазер по кораблю(любому) и прикоснулся ли red ship
    # с другим кораблем.по сути смотрит на коллизию любых двух обьектов.
    # а здесь мы смотрим как поведет лазер,если он соприкоснется с кораблем(collide == True)
    def collision(self, obj):
        return Collide(obj, self)


#____________________________________________



#проверяет столкнулись ли два обьекта(корабли лазеры с кораблями и тд)
# возвращает true если произошло столкновение
def Collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#___________________________________________


class Vector:
    def __init__(self, obj1, obj2):   #obj1 куда, obj2 откуда
        self.pointX = obj1.x - obj2.x
        self.pointY = obj1.y - obj2.y

    def Length(self):
        return math.sqrt((self.pointX**2) + (self.pointY**2))



def mainMenu():

    game = True
    menu_font = pygame.font.SysFont("comicsans", 70)
    menu_tutor = pygame.font.SysFont("comicsans", 40)
    while game:
        screen.blit(background, (0, 0))
        menu_label = menu_font.render("SpaceBar to start", 1, (255, 255, 255))
        menu_tut_label = menu_tutor.render("WASD-move, arrow keys-shoot", 1, (255, 255, 255))


        screen.blit(menu_label, (width/2 - menu_label.get_width()/2, 350))
        screen.blit(menu_tut_label, (width / 2 - menu_label.get_width() / 2 - 5, 600))

        pygame.display.update()

        for event in pygame.event.get():
            menu_keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                game = False
            if menu_keys[pygame.K_SPACE]:
                main()
    pygame.quit()


# и цикл для лазеров(lasers) что проверяет вышли ли они за предел экрана.
#может ввести метод(notOn_screen) в функцию attack?

def main():
    game = True
    lives = 5
    level = 0
    font = pygame.font.SysFont("comicsans", 50)
    font_game_over = pygame.font.SysFont("comicsans", 20)
    fps = 60
    clock = pygame.time.Clock()

    #враги
    enemies = []
    wave_length = 6

    laser_vel = 8
    player = Player(300, 650)

    game_over = False    #перемення что бы знать когда создавать меню при проигрыше,перезагружать игру

    #________________________________________
    def window_redraw():   #выписать HP игрока на экран!!!
        screen.blit(background, (0, 0)) #на surface screen перемещаем изобр background на координаты 0, 0
        label_enem = font.render(f"Enemies remaining: {len(enemies)}", 1, (255, 255, 255)) #создаем surface с текстом
        label_level = font.render(f"Level: {level}", 1, (255, 255, 255))
        screen.blit(label_level, (10, 10))
        screen.blit(label_enem, (width - label_enem.get_width(), 10)) # накладываем surface на экран

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if game_over:    #ввсти выход в меню
            label_game_over = font.render("YOU DIED", 1, (255, 0, 0))
            label_game_over_comm = font_game_over.render("прям как в DarkSouls,понял да", 1, (255, 255, 255))
            label_game_over_space = font_game_over.render("press space to start over", 1, (255, 255, 255))

            screen.blit(label_game_over, (width/2-label_game_over.get_width()/2, height/2))
            screen.blit(label_game_over_comm, (width - label_game_over_comm.get_width()-10, height-10-label_game_over_comm.get_height()))
            screen.blit(label_game_over_space, (width / 2 - label_game_over_space.get_width()/2 , height-20))

            player.stop()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                mainMenu()  # ДАТЬ ТАЙМЕР

        pygame.display.update()
    #_____________________________________

    while game:
        clock.tick(fps)
        window_redraw()

        if lives <= 0 or player.hp <= 0:
            game_over = True

        if len(enemies) == 0:
            level += 1
            for i in range(wave_length):
                enemy = RedEnemy(random.randrange(50, width-100), random.randrange(10, 150), "red", player)
                enemies.append(enemy)

                enemy = BlueEnemy(random.randrange(50, width - 100), random.randrange(10, 150),random.choice(["blue"]))  #!!!
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

#управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player.vel  >0:
            player.x -= player.vel
        if keys[pygame.K_d] and player.x + player.vel + player.get_width() < width:
            player.x += player.vel
        if keys[pygame.K_s] and player.y + player.vel + player.get_height() < height:
            player.y += player.vel
        if keys[pygame.K_w] and player.y - player.vel >0:
            player.y -= player.vel
        if keys[pygame.K_UP]:
            player.shoot("up")
        if keys[pygame.K_DOWN]:
            player.shoot("down")
        if keys[pygame.K_LEFT]:
            player.shoot("left")
        if keys[pygame.K_RIGHT]:
            player.shoot("right")


        for enemy in enemies:
            enemy.attack(player, laser_vel, player)


        for enemy in enemies:
            if enemy.colorShip == "red":
                if Collide(enemy, player):
                    player.hp -= 5
                    # lives -= 1
                    enemies.remove(enemy)
            else:
                if Collide(enemy, player):
                    player.hp -= 3
                    # lives -= 1
                    enemies.remove(enemy)


        player.laser_draw(-laser_vel, enemies)



mainMenu()






































