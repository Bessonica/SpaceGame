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
pygame.display.set_caption("SpaceGame")


#загружаем файлы из assets

#!!! В КОНЦЕ КАЖДОГО image.load должен быть .convert() !! convert не работает,вокруг корабля стоит прямоугольник черный

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
    CoolDown = 30


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
        for laser in self.lasers:
            laser.draw(screen)


    def get_width(self):
        return self.img_ship.get_width()

    def get_height(self):
        return self.img_ship.get_height()


    def give_position(self):  #нужно что бы корабли могли прицелиться и выстрелить в гг
        return self.x, self.y

    #тестовый метод,если у кораблей будут разные стили стрельбы то нужно делать метод для каждого класса,
    # !!ИЛИ СДЕЛАТЬ ОБЕРТКУ!!! в классах redenemy,blue
    def shoot(self):
        if self.coolD_counter == 0:
            laser = Laser(self.x, self.y, self.img_laser)
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
                self.lasers.remove(laser)  #лазер попал по обьекту и пропал



#класс player наследует от ship
class Player(Ship):
    def __init__(self, x, y,vel = 8 , hp=10):
        super().__init__(x, y, hp) #используем метод инит из ship
        self.img_ship = spaceShip_yellow
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

    #взяли метод у родителя(ship) и добавили в него hp_bar()
    def draw(self, screen):
        super().draw(screen)
        self.hp_bar(screen)







# как их запрограммировать ччто бы они следовали за тобой,стреляли по игроку?
# типы врагов
# мины/пилоты камикадзе что не могут стрелять но следуют за игроком и взрываются рядом с ним

#снайперы,что редко стреляют,но выстреливают один сплошной луч+держутся на расстоянии от гг
#или пусть снафперы делают один выстрел и отлетают в рандомную сторону
# можно ввести противника турель у кот не будет метода(из ship) cooldown-a
#
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
        self.mask = pygame.mask.from_surface(self.img_ship)

    # def move(self, vel):  #для каждого типа корабля свое передвижение,так что это немного бесполезно
    #     self.y += vel


#камикадзе- идут напрямую на игрока,медленные,при сближении с гг или смерти взрываются!!наносят урон как игроку так и врагам!!
class RedEnemy(Enemy):
    colorShip = "red"


    def __init__(self, x, y, color, player, hp = 100):
        super().__init__(x, y, color, hp)
        self.x = x
        self.y = y
        self.vec_start = pygame.math.Vector2((player.x, player.y))
        self.vec_end = pygame.math.Vector2((x, y)).normalize()

    #может переименовать move в attack?или отдельный метод attack, что внутри себя использует move?+++после части #управление
    #вместо move вписать attack
    # def move(self,x, y, vel = 5):  #корабль следует медленно за игроком
    #     self.x += vel
    #  движение выглядит неестественно.корабль !!!!не движется по вектору!!! исправит ь это
    def move(self, player, vel = 1):  #корабль следует медленно за игроком.
        #print("PLAYER POS", player.x, player.y)
        v = Vector(player, self)
        print("MEGA VECTOR BLYAD", v.pointX, v.pointY)
        print(v.Length())

        #плохая версия,корабли не движутся по вектору.попробуй сделать так что бы на один кадр вычисляли небольшой вектор и
        #на его координату(мал вектора) отправляли корабль
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





            #Y
            # if v.pointY > 0:
            #     self.y += vel
            #     # self.y += vel
            # elif v.pointY <= 0:
            #     self.y -= vel
            # else:
            #     pass

            #X
            # if v.pointX > 0:
            #     self.x += vel
            #     #self.y += vel
            # elif v.pointX <=0:
            #     self.x -= vel
            # else:
            #     pass


        #print("red vector", Vector(player, self))





    def moveLeft(self, vel = 5):
        self.x -=vel







            # if self.x>= width:
            #     self.x -= vel
            # elif self.x <= 0:
            #     self.x += vel



        # dirvect = pygame.math.Vector2(x - self.x, y - self.y) # КОД ЧТО БЫ КРАСНЫЙ ПРЕСЛЕДОВАЛ ИГРОКА
        # dirvect.normalize()
        # dirvect.scale_to_length(vel)
        # print("DIRVECT", dirvect)   #dirvect[0] = x


    def attack(self, player, laserVel, obj):  #x, y =player pos.  self.x, self.y = ENEMY POS
        self.move(player)
        # self.laser_draw(laserVel, player)
        # if random.randrange(0, 120) == 1:  #frames PER SECOND = 60, шанс попадания в 2 сек = 50%
        #     self.shoot()

       # print(x, y)
       # self.move()

#проблема как достать координату игроку в класс Redenemy


#снайпер
class BlueEnemy(Enemy):
    colorShip = "blue"
    def __init__(self, x, y, color, hp = 100):
        super().__init__(x, y, color, hp)


    # def move(self,x, y, vel = 5):  #корабль следует медленно за игроком
    #     self.x += vel

    def move(self,player, vel = 5):  #корабль следует медленно за игроком
        pass
        # vector = Vector(player, self)
        # vel_x = vector[0]/50
        # vel_y = vector[1]/50
        # print("VEL X Y", vel_x, vel_y)
        # self.x += vel_x
        # self.y += vel_y
        # print("PLAYER", player.x, player.y)
        # print("ENEMY", self.x, self.y)
        # print("vector lenthg", Vector(player, self))
        #print("VECTOR", vectorX, vectorY)

    def moveLeft(self, vel = 5):
        self.x -=vel

    def attack(self, player, laserVel, obj):   #здесь применяем move и laser
        self.laser_draw(laserVel, obj)
        #self.move()
        if random.randrange(0, 120) == 1:
            self.shoot()

            #print(x, y)

        #тест для что бы не писать лишний код в ивент лупе,нужно вставить в аргументы enemies, player, lives.как то геморно
        # for enemy in enemies:
        #     if Collide(enemy, player):
        #         lives -= 1
        #         enemies.remove(enemy)



#____________________________________

#подумай, лазер будет иметь в себе расположение игрока,или это будет определяться в методе attack(скорее всего в атак,ведь
#у каждого корабля свой стиль атаки может быть
#
#в будущем сделать потомков лазера=разне виды выстрелов(сплошной луч,короткий,но быстрый выстрел и тд)
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img) #коллизия?


    def draw(self, window):
        window.blit(self.img, (self.x, self.y))


        # лазер должен двигаться по прямой траектории,не следовать за игроком.во время выстрела
        #метод находит координату игрока и движется к ней,делает только один раз,во время выстрела
    def move(self, vel):     #
        self.y +=vel   #сделать так что бы лазер летел на позицию игрока!!!,или в сторону мышки


    def notOn_screen(self, height):  #удалить лазер если он вне экрана
        return  not(self.y <= height and self.y >= 0)

        pass

    # создать универс. функцию collide что будет смотреть-попал ли лазер по кораблю(любому) и прикоснулся ли red ship
    # с другим кораблем.по сути смотрит на коллизию любых двух обьектов.
    # а здесь мы смотрим как поведет лазер,если он соприкоснется с кораблем(collide == True)
    def collision(self, obj):
        return Collide(obj, self)
        pass


#____________________________________________



#проверяет столкнулись ли два обьекта(корабли лазеры с кораблями и тд)
#мож ввести взрыв,когда два лезара врезаются в друг дргуа
# возвращает true если произошло столкновение
def Collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#___________________________________________


# def Vector(obj1, obj2):   #obj1 = обьект к которому направляемся(player), obj2 = enemy
#     print(obj1.x, obj1.y )
#     vectorX = obj1.x - obj2.x
#     vectorY = obj1.y - obj2.y
#     vectorLength = math.sqrt((vectorX ** 2) + (vectorY ** 2))
#     return vectorX, vectorY


class Vector:
    def __init__(self, obj1, obj2):   #obj1 куда, obj2 откуда
        self.pointX = obj1.x - obj2.x
        self.pointY = obj1.y - obj2.y

    def Length(self):
        return math.sqrt((self.pointX**2) + (self.pointY**2))




def mainMenu():

    game = True
    menu_font = pygame.font.SysFont("comicsans", 70)
    while game:
        screen.blit(background, (0, 0))
        menu_label = menu_font.render("SpaceBar to start", 1, (255, 255, 255))
        screen.blit(menu_label, (width/2 - menu_label.get_width()/2, 350))

        pygame.display.update()

        for event in pygame.event.get():
            menu_keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                game = False
            if menu_keys[pygame.K_SPACE]:
                main()
    pygame.quit()

#мож сделать цикл в while game: где есть цикл где каждый обьект в enemies проверяется с Collide,если да то исполь метод

# и цикл для лазеров(lasers) что проверяет вышли ли они за предел экрана.думаю такая себе идея,столько лазеров возможны лаги
#может ввести метод(notOn_screen) в функцию attack

def main():
    game = True
    lives = 5
    font = pygame.font.SysFont("comicsans", 80)
    font_game_over = pygame.font.SysFont("comicsans", 70)  #?поменять цвет?
    fps = 60
    clock = pygame.time.Clock()

    #враги
    enemies = []
    wave_length = 5

    laser_vel = 8
    player = Player(300, 650)


    game_over = False    #перемення что бы знать когда создавать меню при проигрыше,перезагружать игру



    #________________________________________
    def window_redraw():   #выписать HP игрока на экран!!!
        screen.blit(background, (0, 0)) #на surface screen перемещаем изобр background на координаты 0, 0
        label_lives = font.render(f"{lives} lives", 1, (255, 255, 255)) #создаем surface с текстом
        screen.blit(label_lives, (10, 10)) # накладываем surface на экран

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if game_over:    #ввсти выход в меню и удалить всех врагов+вернуть hp игроку
            label_game_over = font.render("YOU DIED", 1, (255, 0, 0))
            screen.blit(label_game_over, (width/2-label_game_over.get_width()/2, height/2))


        pygame.display.update()
    #_____________________________________

    # мож сделать цикл в while game: где есть цикл где каждый обьект в enemies проверяется с Collide,если да то исполь метод

    while game:
        clock.tick(fps)
        window_redraw()

        if lives <= 0 or player.hp <= 0:  #!!game over screen!!  game_over = true. ввсти выход в меню и удалить всех врагов+вернуть hp игроку
            game_over = True


        # также здесь можно организовать переходна новый уровень
        #спавн врагов  !!!на будущие- сделай спавн врагов рандомным,что бы на каждой новой волне было разное кол врагов
        # random.choice(["red","blue", "green"])


        if len(enemies) == 0:   #также если игрок все еще не начал новую игру(game_over=true)не спавнить врагов
            for i in range(wave_length):
                enemy = RedEnemy(random.randrange(50, width-100), random.randrange(10, 150), "red", player) #!!!!!!!!!!!!!!!redenemy = enemy
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
        if keys[pygame.K_SPACE]: #лазер формируется только один раз,мож проблема в cooldown?
            print('shoooot')
            player.shoot()



# здесь нужно ввест координату игрока в метод attack(сделал метод give_position у ship- можно применить у всех кораблей)
        # в attack ввести метод laser_draw

        for enemy in enemies:
            #enemy.move(player)
            enemy.attack(player, laser_vel, player)





            #enemy.attack(player.x, player.y, laser_vel, player)  # всунули laser_draw в attack


            #старая версия,всунул все в метод attack
            #enemy.laser_draw(laser_vel, player)
            # if random.randrange(0, 240) == 1:
            #     enemy.shoot()  # игрок получает урон но он не отображается на экране+некоторые корабли вообще не стреляют


            #здесь настроить поведение для камикадзе
            #если collide = true и враг = redenemy.запустить метод explode для red enemy.написать метод explode
            # ну или просто в петле вписать,но мне кажется сделать отдельный метод explode будет красивее
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



        #print(player.give_position())
        #print(enemies[0].give_position())




mainMenu()

# как получить расположение мыши
# pg.mouse.get_pos()
#
#сделать коллизию - взрыв камикадзе СТРОКА 69
#сделать стрельу для корабля игрока и убийство врагов
#
#!!часто игра начинает тормозить!! похоже это происходить при коллизии с врагами.через час проблема пропала,мож беда в ноуте самом?
#
#class Enemy передеать зачем нам теперь colormap?
#можно ли коллизию(self.mask = pygame.mask.from_surface(self.img)) поместить не в отдельные классы кораблей
#а в общий класс Ship? !!может поместить mask в класс Enemy,там уже определяют изображение кораблям

#идея как все организоваать у двух классов врагов разные методы attack но им обоим нужны координаты игрока
#
#переделать метод move в классе laser.надо в метод move или attack всунуть координаты игрока,что бы расчитать вектор
#метод attack в классах redEnemy, blueEnemy
#shoot в class SHip
#
#

































