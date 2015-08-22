import os, pygame, math
from pygame.locals import *

class planet:
    r = 2000

class game:
    width = 320*2
    height = 256*2
    crashed = False
    landed = False
    zoom = 1
    running = True
    screen = None

class ship:
    x = 0
    y = planet.r + 100
    dx = 0
    dy = 0
    phi = math.pi/2
    dphi = 0
    maxthrust = .02
    thrust = 0

def loop():
    SKY = (0,128,255)
    GROUND = (0,128,0)

    game.clock.tick(60)

    # Sky and planet
    pygame.draw.rect(game.screen, SKY, (0,0,game.width,game.height))
    planetx = game.width/2 + ship.x*math.sin(ship.phi) + ship.y*math.cos(ship.phi)
    planety = game.height/2 - ship.x*math.cos(ship.phi) + ship.y*math.sin(ship.phi)
    pygame.draw.circle(game.screen,(0,255,0), (int(planetx),int(planety)), planet.r)

    # Spaceship
    if not game.crashed:
        game.screen.blit(ship.rocket,(game.width/2-9,game.height/2-40))

        ship.dx += ship.maxthrust * ship.thrust * math.cos(ship.phi)
        ship.dy += ship.maxthrust * ship.thrust * math.sin(ship.phi)
        dr = math.sqrt(ship.dx*ship.dx+ship.dy*ship.dy)
        r = math.sqrt(ship.x*ship.x+ship.y*ship.y)
        theta = math.atan2(ship.y,ship.x)

        ship.phi+=ship.dphi
        ship.x += ship.dx
        ship.y += ship.dy

        landed = False
        if (abs(r-planet.r)<=-dr and abs(dr) < 0.5 and 1):
            ship.dx = ship.dy = 0
            landed = True
        elif (r < planet.r):
            print("crashed")
            game.crashed = True
        else:
            g = 0.01
            ship.dx -= g * math.cos(theta)
            ship.dy -= g * math.sin(theta)
    else:
        text = game.font.render("CRASHED", 0, (255,0,0))
        textpos = text.get_rect()
        textpos.centerx = game.screen.get_rect().centerx
        textpos.centery = game.screen.get_rect().centery
        game.screen.blit(text,textpos)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            game.running = False
            return
        elif event.type == KEYDOWN:
            if event.key == ord('q'):
                game.running = False
            elif event.key == ord('x'):
                ship.thrust = 0 # no thrust
            elif event.key == ord('z'):
                ship.thrust = 1 # 100% thrust
            elif event.key == ord('w'):
                ship.thrust += 1./16
            elif event.key == ord('s'):
                ship.thrust -= 1./16
            elif event.key == ord('a'):
                ship.dphi += .001
            elif event.key == ord('d'):
                ship.dphi -= .001

    if ship.thrust < 0:
        ship.thrust = 0
    elif ship.thrust > 1:
        ship.thrust = 1
    print ship.thrust

def main():
    pygame.init()
    pygame.display.set_caption('Leedshack-KSP')
    pygame.key.set_repeat(20, 20)
    game.screen = pygame.display.set_mode((game.width,game.height))
    game.clock = pygame.time.Clock()
    ship.rocket = pygame.image.load("images/real stuff/FULL ROKET.png")
    game.font = pygame.font.Font(None, 64)
    while game.running:
        loop()
        pygame.display.flip()

    pygame.quit()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()

