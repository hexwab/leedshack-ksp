import os, pygame, math
from pygame.locals import *

class planet:
    r = 2000

class game:
    width = 320
    height = 256
    crashed = False
    landed = False
    zoom = 1
    running = True
    screen = None

class ship:
    x = 0
    y = planet.r
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
    planetx = 160 + ship.x*math.sin(ship.phi) + ship.y*math.cos(ship.phi)
    planety = 128 - ship.x*math.cos(ship.phi) + ship.y*math.sin(ship.phi)
    pygame.draw.circle(game.screen,(0,255,0), (int(planetx),int(planety)), planet.r)

    # Spaceship
    game.screen.blit(ship.rocket,(160-9,128-40))
    
    for event in pygame.event.get():
        if event.type == QUIT:
            game.running = False
            return
        elif event.type == KEYDOWN:
            if event.key == ord('q'):
                game.running = False

def main():
    pygame.init()
    pygame.display.set_caption('Leedshack-KSP')
    game.screen = pygame.display.set_mode((game.width,game.height))
    game.clock = pygame.time.Clock()
    ship.rocket = pygame.image.load("images/real stuff/FULL ROKET.png")
    while game.running:
        loop()
        pygame.display.flip()

    pygame.quit()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()

