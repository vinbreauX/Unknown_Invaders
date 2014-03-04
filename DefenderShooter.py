#! /usr/bin/env python

# Unknown Invaders v1.0
# Defender-style, side=scrolling space shooter
#
# Created by Vin Breau, 2014
#
# Inspired by Space Shooter by Tyler Gray & Chad Haley



#Import
import os, sys, pygame, random
from pygame.locals import *

os.environ['SDL_VIDEO_CENTERED'] = "1"
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.display.set_caption("Unknown Invaders")
icon = pygame.image.load("VLogo.png")
icon = pygame.display.set_icon(icon)
screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
pygame.mouse.set_visible(0)


#Colors
BACKGROUND = (0, 0, 0)
HIGHLIGHT = (50, 50, 255)
FONTCOLOR = (170, 170, 255)

LOGOSIZE = 70
FONTSIZE = 40

#Background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(BACKGROUND)

#Music
music = pygame.mixer.music.load("data/music/Zone_66_Theme.ogg")  #Temp Music
pygame.mixer.music.play(-1)



#Load Images
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', fullname)
        raise SystemExit
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print('Cannot load sound:', fullname)
        raise SystemExit
    return sound

#Sprites

#This class controls the arena background
class Arena(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("menu/space.jpg", -1)
        self.dx = 5
        self.reset()

    def update(self):
        self.rect.left -= self.dx
        if self.rect.left <= -1600:
            self.reset()

    def reset(self):
        self.rect.left = 0

#Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/player.png", -1)
        self.rect.center = (100, 300)
        self.dx = 0
        self.dy = 0
        self.reset()
        self.lasertimer = 0
        self.lasermax = 5
        self.bombamount = 1
        self.bombtimer = 0
        self.bombmax = 10

    def update(self):
        self.rect.move_ip((self.dx, self.dy))

        #Fire the laser
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            self.lasertimer = self.lasertimer + 1
            if self.lasertimer == self.lasermax:
                laserSprites.add(Laser(self.rect.midright))
                fire.play()
                self.lasertimer = 0

        #Fire the bomb
        if key[pygame.K_LCTRL]:
            self.bombtimer = self.bombtimer + 1
            if self.bombtimer == self.bombmax:
                self.bombtimer = 0
                if self.bombamount > 0:
                    self.bombamount = self.bombamount - 1
                    score.bomb -= 1
                    bombSprites.add(Bomb(self.rect.midright))
                    torpedo.play()

        #Player Boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 800:
            self.rect.right = 800

        if self.rect.top <= 50:
            self.rect.top = 50
        elif self.rect.bottom >= 575:
            self.rect.bottom = 575


    def reset(self):
        self.rect.left = 0

#Laser class
class Laser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/laser.png", -1)
        self.rect.center = pos

    def update(self):
        if self.rect.left > 800:
            self.kill()
        else:
            self.rect.move_ip(15, 0)

#Bomb class
class Bomb(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/bomb.png", -1)
        self.rect.center = pos

    def update(self):
        if self.rect.right < 0:
            self.kill()
        else:
            self.rect.move_ip(5, 0)
        if pygame.sprite.groupcollide(enemySprites, bombSprites, 1, 1):
            bombExplosionSprites.add(BombExplosion(self.rect.center))
            explode.play()

#Enemy laser class
class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/elaser.png", -1)
        self.rect.center = pos

    def update(self):
        if self.rect.right < 0:
            self.kill()
        else:
            self.rect.move_ip(-15, 0)

#Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, centery):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/enemy.png", -1)
        self.rect = self.image.get_rect()
        self.dx = 8
        self.reset()

    def update(self):
        self.rect.centerx -= self.dx
        self.rect.centery -= self.dy
        if self.rect.right < 0:
            self.reset()
        if self.rect.top < 50:
            self.rect.top = 50
        if self.rect.bottom > 550:
            self.rect.bottom = 550

        #random 1 - 60 determines if firing
        efire = random.randint(1, 60)
        if efire == 1:
            enemyLaserSprites.add(EnemyLaser(self.rect.midleft))
            efire = load_sound("sounds/elaser.ogg")
            efire.play()

        #Laser collisions
        if pygame.sprite.groupcollide(enemySprites, laserSprites, 1, 1):
            explosionSprites.add(EnemyExplosion(self.rect.center))
            explode.play()
            score.score += 10

        #Bomb Collisions
        if pygame.sprite.groupcollide(enemySprites, bombSprites, 1, 1):
            bombExplosionSprites.add(BombExplosion(self.rect.center))
            explode.play()
            score.score += 10

        #Bomb Explosion Collisions
        if pygame.sprite.groupcollide(enemySprites, bombExplosionSprites, 1, 0):
            explosionSprites.add(EnemyExplosion(self.rect.center))
            explode.play()
            score.score += 10

    def reset(self):
        self.rect.left = 800
        self.rect.centery = random.randrange(50, 550)
        self.dx = random.randrange(5, 10)
        self.dy = random.randrange(-2, 2)

class Shield(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/shield.png", -1)
        self.rect.center = pos
        self.counter = 0
        self.maxcount = 2
    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()

class EnemyExplosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/enemyexplosion.png", -1)
        self.rect.center = pos
        self.counter = 0
        self.maxcount = 10
    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()

class BombExplosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/bombexplosion.png", -1)
        self.rect.center = pos
        self.counter = 0
        self.maxcount = 5
    def update(self):
        self.counter = self.counter + 1
        if self.counter == self.maxcount:
            self.kill()

#Bomb Powerup
class BombPowerup(pygame.sprite.Sprite):
    def __init__(self, centery):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/torpedopowerup.png", -1)
        self.rect = self.image.get_rect()
        self.rect.centery = random.randrange(60, screen.get_height() - 50)
        self.rect.centerx = 810
    def update(self):
        if self.rect.right < 0:
            self.kill()
        else:
            self.rect.move_ip(-6, 0)

#Shield Powerup
class ShieldPowerup(pygame.sprite.Sprite):
    def __init__(self, centery):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("sprites/shieldpowerup.png", -1)
        self.rect = self.image.get_rect()
        self.rect.centery = random.randrange(60, screen.get_height() - 50)
        self.rect.centerx = 810
    def update(self):
        if self.rect.right < 0:
            self.kill()
        else:
            self.rect.move_ip(-6, 0)

class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.shield = 100
        self.score = 0
        self.bomb = 1
        self.font = pygame.font.Font("data/fonts/Regen.otf", 23)
    def update(self):
        self.text = "Shield: %d                        Score: %d                        Torpedo: %d" % (self.shield, self.score, self.bomb)
        self.image = self.font.render(self.text, 1, FONTCOLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (400, 20)

class Gameover(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("data/fonts/BlackHoleBB.ttf", 48)

    def update(self):
        self.text = ("GAME OVER")
        self.image = self.font.render(self.text, 1, FONTCOLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)

class Gameoverscr(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("data/fonts/Regen.otf", 28)
    def update(self):
        self.text = "PRESS ESC TO RETURN"
        self.image = self.font.render(self.text, 1, HIGHLIGHT)
        self.rect = self.image.get_rect()
        self.rect.center = (400, 400)

#Game Module
def game():

    #Game Objects
    global player
    player = Player()
    global score
    score = Score()

    global fire
    fire = load_sound("sounds/laser.ogg")
    global explode
    explode = load_sound("sounds/explosion.ogg")
    global torpedo
    torpedo = load_sound("sounds/torpedo.ogg")
    global powerup
    powerup = load_sound("sounds/powerup.ogg")
    global shiphit
    shiphit = load_sound("sounds/shiphit.ogg")

    #Game Groups

    #Player/Enemy
    playerSprite = pygame.sprite.RenderPlain((player))

    global enemySprites
    enemySprites = pygame.sprite.RenderPlain(())
    enemySprites.add(Enemy(200))
    enemySprites.add(Enemy(300))
    enemySprites.add(Enemy(400))

    #Projectiles
    global laserSprites
    laserSprites = pygame.sprite.RenderPlain(())

    global bombSprites
    bombSprites = pygame.sprite.RenderPlain(())
    global enemyLaserSprites
    enemyLaserSprites = pygame.sprite.RenderPlain(())

    #Powerups
    global bombPowerups
    bombPowerups = pygame.sprite.RenderPlain(())
    global shieldPowerups
    shieldPowerups = pygame.sprite.RenderPlain(())

    #Special FX
    shieldSprites = pygame.sprite.RenderPlain(())

    global explosionSprites
    explosionSprites = pygame.sprite.RenderPlain(())

    global bombExplosionSprites
    bombExplosionSprites = pygame.sprite.RenderPlain(())

    #Score and Game Over
    scoreSprite = pygame.sprite.Group(score)
    gameOverSprite = pygame.sprite.RenderPlain(())

    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))

    #Set Clock
    clock = pygame.time.Clock()
    keepGoing = True
    counter = 0

    #Main Loop
    while keepGoing:
        clock.tick(30)
        #input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
                elif event.key == pygame.K_LEFT:
                    player.dx = -10
                elif event.key == pygame.K_RIGHT:
                    player.dx = 10
                elif event.key == pygame.K_UP:
                    player.dy = -10
                elif event.key == pygame.K_DOWN:
                    player.dy = 10
            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    player.dx = 0
                elif event.key == K_RIGHT:
                    player.dx = 0
                elif event.key == K_UP:
                    player.dy = 0
                elif event.key == K_DOWN:
                    player.dy = 0

        #Update and draw on the screen

        #Update
        screen.blit(background, (0, 0))
        playerSprite.update()
        enemySprites.update()
        laserSprites.update()
        bombSprites.update()
        enemyLaserSprites.update()
        bombPowerups.update()
        shieldPowerups.update()
        shieldSprites.update()
        explosionSprites.update()
        bombExplosionSprites.update()
        arena.update()
        scoreSprite.update()
        gameOverSprite.update()

        #Draw
        arena.draw(screen)
        playerSprite.draw(screen)
        enemySprites.draw(screen)
        laserSprites.draw(screen)
        bombSprites.draw(screen)
        enemyLaserSprites.draw(screen)
        bombPowerups.draw(screen)
        shieldPowerups.draw(screen)
        shieldSprites.draw(screen)
        explosionSprites.draw(screen)
        bombExplosionSprites.draw(screen)
        scoreSprite.draw(screen)
        gameOverSprite.draw(screen)
        pygame.display.flip()

        #Spawn new enemies
        counter += 1
        if counter >= 20:
            enemySprites.add(Enemy(300))
            counter = 0

        #Spawn Shield Power up
        spawnShieldPowerup = random.randint(1, 500)
        if spawnShieldPowerup == 1:
            shieldPowerups.add(ShieldPowerup(300))

        #Spawn Bomb Power up
        spawnBombPowerup = random.randint(1, 500)
        if spawnBombPowerup == 1:
            bombPowerups.add(BombPowerup(300))

        #Check if enemy lasers hit player's ship
        for hit in pygame.sprite.groupcollide(enemyLaserSprites, playerSprite, 1, 0):
            shiphit.play()
            explosionSprites.add(Shield(player.rect.center))
            score.shield -= 10
            if score.shield <= 0:
                gameOverSprite.add(Gameover())
                gameOverSprite.add(Gameoverscr())
                playerSprite.remove(player)

        #Check if enemy collides with player
        for hit in pygame.sprite.groupcollide(enemySprites, playerSprite, 1, 0):
            explode.play()
            explosionSprites.add(Shield(player.rect.center))
            score.shield -= 10
            if score.shield <= 0:
                gameOverSprite.add(Gameover())
                gameOverSprite.add(Gameoverscr())
                playerSprite.remove(player)

        #Check if player collides with shield powerup
        for hit in pygame.sprite.groupcollide(shieldPowerups, playerSprite, 1, 0):
            if score.shield < 100:
                powerup.play()
                score.shield += 10

        #Check if player collides with bomb powerup
        for hit in pygame.sprite.groupcollide(bombPowerups, playerSprite, 1, 0):
            powerup.play()
            player.bombamount += 1
            score.bomb += 1



#Class Module
class SpaceMenu:
    #Define the initialize self options
    def __init__(self, *options):

        self.options = options
        self.x = 0
        self.y = 0
        self.font = pygame.font.Font(None, 32)
        self.option = 0
        self.width = 1
        self.color = [0, 0, 0]
        self.hcolor = [0, 0, 0]
        self.height = len(self.options) * self.font.get_height()
        for o in self.options:
            text = o[0]
            ren = self.font.render(text, 1, (0, 0, 0))
            if ren.get_width() > self.width:
                self.width = ren.get_width()

    #Draw the menu
    def draw(self, surface):
        i = 0
        for o in self.options:
            if i == self.option:
                clr = self.hcolor
            else:
                clr = self.color
            text = o[0]
            ren = self.font.render(text, 1, clr)
            if ren.get_width() > self.width:
                self.width = ren.get_width()
            surface.blit(ren, (self.x, self.y + i * self.font.get_height()))
            i += 1

    #Menu Input
    def update(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.option += 1
                if e.key == pygame.K_UP:
                    self.option -= 1
                if e.key == pygame.K_RETURN:
                    self.options[self.option][1]()
        if self.option > len(self.options) - 1:
            self.option = 0
        if self.option < 0:
            self.option = len(self.options) - 1

    #Position Menu
    def set_pos(selfself, x, y):
        self.x = x
        self.y = y

    #Font Style
    def set_font(self, font):
        self.font = font

    #Highlight Color
    def set_highlight_color(self, color):
        self.hcolor = color

    #Font Color
    def set_normal_color(self, color):
        self.color = color

    #Font position
    def center_at(self, x, y):
        self.x = x - (self.width / 2)
        self.y = y - (self.height / 2)

def missionMenu():

    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))


    #Title for Option Menu
    menuTitle = SpaceMenu(
        ["Unknown Invaders"]
    )

    #Option Menu Text
    instructions = SpaceMenu(
        [""],
        ["Hostile aliens from the depths of space have invaded"],
        [""],
        ["Earth! You are the last of Earth's most elite fighters."],
        [""],
        ["Navigate your sub-orbital fighter with the arrow keys or"],
        [""],
        ["       The [SPACE] bar fires your assault lasers"],
        [""],
        [" while the left [CTRL] key fires your limited torpedoes."],
        [""],
        ["Last as long as you can against the invading force!"],
        [""],
        [""],
        [""],
        ["                   PRESS ESC TO RETURN                    "]
    )

    #Title
    menuTitle.center_at(150, 150)
    menuTitle.set_font(pygame.font.Font("data/fonts/BlackHoleBB_ital.ttf", LOGOSIZE))
    menuTitle.set_highlight_color(HIGHLIGHT)

    #Title Center
    instructions.center_at(400, 375)

    #Menu Font
    instructions.set_font(pygame.font.Font("data/fonts/BlackHoleBB.ttf", 20))

    #Highlight Color
    instructions.set_normal_color(FONTCOLOR)


    #Set Clock
    clock = pygame.time.Clock()
    keepGoing = True

    while keepGoing:
        clock.tick(30)
        #input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False

        #Draw
        screen.blit(background, (0, 0))
        arena.update()
        arena.draw(screen)
        menuTitle.draw(screen)
        instructions.draw(screen)
        pygame.display.flip()


def aboutMenu():

    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))

    #About Menu Text
    #Title for Option Menu
    menuTitle = SpaceMenu(
        ["Unknown Invaders"]
    )

    info = SpaceMenu(
        [""],
        ["            Unknown Invaders Alpha      "],
        [""],
        ["         Developed by Vin Breau, 2014   "],
        [""],
        ["Based on Space Shooter Beta and Defender"],
        [""],
        [""],
        ["             PRESS ESC TO RETURN        "]
    )

    #About Title Font color, alignment, and font type
    menuTitle.center_at(150, 150)
    menuTitle.set_font(pygame.font.Font("data/fonts/BlackHoleBB_ital.ttf", LOGOSIZE))
    menuTitle.set_highlight_color(HIGHLIGHT)

    #About Menu Text Alignment
    info.center_at(400, 350)

    #About Menu Font
    info.set_font(pygame.font.Font("data/fonts/BlackHoleBB.ttf", 20))

    #About Menu Font Color
    info.set_normal_color(FONTCOLOR)


    #Set Clock
    clock = pygame.time.Clock()
    keepGoing = True

    while keepGoing:
        clock.tick(30)
        #input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False

        #Draw
        screen.blit(background, (0, 0))
        arena.update()
        arena.draw(screen)
        menuTitle.draw(screen)
        info.draw(screen)
        pygame.display.flip()


#Functions
def option1():
    game()
def option2():
    missionMenu()
def option3():
    aboutMenu()
def option4():
    pygame.quit()
    sys.exit()

#Main
def main():
    #Arena
    arena = Arena()
    arena = pygame.sprite.RenderPlain((arena))

    #Defines menu, option functions, and option display. For example,
    #Changing "Start" to "Begin" will display Begin, instead of start.
    menuTitle = SpaceMenu(
        ["Unknown Invaders"]
    )

    menu = SpaceMenu(
        ["Start", option1],
        ["Mission", option2],
        ["About", option3],
        ["Quit", option4]
    )


    #Title
    menuTitle.center_at(150, 150)
    menuTitle.set_font(pygame.font.Font("data/fonts/BlackHoleBB_ital.ttf", LOGOSIZE))
    menuTitle.set_highlight_color(HIGHLIGHT)

    #Menu settings
    menu.center_at(375, 320)
    menu.set_font(pygame.font.Font("data/fonts/BlackHoleBB.ttf", FONTSIZE))
    menu.set_highlight_color(HIGHLIGHT)
    menu.set_normal_color(FONTCOLOR)

    clock = pygame.time.Clock()
    keepGoing = True

    while 1:
        clock.tick(30)

        #Events
        events = pygame.event.get()

        #Update Menu
        menu.update(events)

        #Quit Event
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                return

        #Draw
        screen.blit(background, (0, 0))
        arena.update()
        arena.draw(screen)
        menu.draw(screen)
        menuTitle.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()