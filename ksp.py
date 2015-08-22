import os, pygame, math
from pygame.locals import *
import pygame.gfxdraw

class planet:
    r = 2000

class game:
    width = 320*2
    height = 256*2
    crashed = False
    landed = False
    zoom = 1
    running = True
    paused = False
    screen = None
    map = False

class ship:
    x = 0 #planet.r
    y = planet.r + 100
    dx = 0
    dy = 0
    phi = 0  # -math.pi*5.5/4
    dphi = 0
    maxthrust = .02
    thrust = 0.5
    sas = False

def loop():
    SKY = (0,128,255)
    GROUND = (0,128,0)
    RED = (255,0,0)
    BLACK = (0,0,0)
    WHITE = (255,255,255)

    game.clock.tick(60)

    if game.map:
        # map screen
        pygame.draw.rect(game.screen, BLACK, (0,0,game.width,game.height))
        scale = 0.05
        pygame.draw.circle(game.screen,GROUND, (int(game.width/2),int(game.height/2)), int(planet.r*scale))
        shipx=int(game.width/2+ship.x*scale)
        shipy=int(game.height/2+ship.y*scale)
        pygame.draw.circle(game.screen,WHITE, (shipx, shipy), 2)
        pygame.draw.line(game.screen,WHITE, (shipx,shipy), (int(shipx+10*math.cos(ship.phi)), int(shipy+10*math.sin(ship.phi))))
        pygame.draw.line(game.screen,RED, (shipx,shipy), (int(shipx+ship.dx*4), int(shipy+ship.dy*4)))
    else:
        # Sky and planet
        pygame.draw.rect(game.screen, SKY, (0,0,game.width,game.height))
        planetx = game.width/2 + ship.x*math.sin(ship.phi) + ship.y*math.cos(ship.phi)
        planety = game.height/2 - ship.x*math.cos(ship.phi) + ship.y*math.sin(ship.phi)
        pygame.draw.circle(game.screen,(0,255,0), (int(planetx),int(planety)), planet.r)
        n = 16
        for i in xrange(1,n):
            pygame.gfxdraw.pie(game.screen, int(planetx), int(planety), int(planet.r*10), 360*i/n, 360*(i+1)/n, (RED if i%2 else BLACK))
        # Spaceship
        if not game.crashed:
            game.screen.blit(ship.rocket,(game.width/2-9,game.height/2-40))
        else:
            text = game.crashfont.render("CRASHED", 0, (255,0,0))
            textpos = text.get_rect()
            textpos.centerx = game.screen.get_rect().centerx
            textpos.centery = game.screen.get_rect().centery
            game.screen.blit(text,textpos)

    # calculations
    if not game.crashed and not game.paused:
        ship.dx += ship.maxthrust * ship.thrust * math.cos(ship.phi)
        ship.dy += ship.maxthrust * ship.thrust * math.sin(ship.phi)
        print "thrust ", ship.maxthrust * ship.thrust * math.cos(ship.phi), ship.maxthrust * ship.thrust * math.sin(ship.phi)

        dr = math.sqrt(ship.dx*ship.dx+ship.dy*ship.dy)
        r = math.sqrt(ship.x*ship.x+ship.y*ship.y)
        theta = math.atan2(ship.y,ship.x)
        
        # altimeter
        game.screen.blit(game.altimeter,(game.width/2-65+16-3,5))
        text = game.font.render(str(int(r-planet.r)), 0, (20,20,20))
        textpos = text.get_rect()
        print textpos
        textpos.centerx = game.screen.get_rect().centerx
        textpos.centery += 14
        game.screen.blit(text,textpos)

        ship.phi+=ship.dphi
        ship.x += ship.dx
        ship.y += ship.dy
        if ship.sas:
            if ship.dphi:
                ship.dphi += -0.001 if ship.dphi>0 else 0.001

        landed = False
        if (abs(r-planet.r)<=-dr and abs(dr) < 0.5):
            ship.dx = ship.dy = 0
            landed = True
        elif (r < planet.r):
            print("crashed")
            game.crashed = True
        else:
            g = 0.01
            ship.dx -= g * math.cos(theta)
            ship.dy -= g * math.sin(theta)
            print "grav ", -g * math.cos(theta), -g * math.sin(theta)
        
        print "theta=",theta
        print ship.x, ship.dx, ship.y, ship.dy, r, ship.phi
    
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
                ship.dphi -= .001
            elif event.key == ord('d'):
                ship.dphi += .001
        elif event.type == KEYUP:
            if event.key == ord(' '):
                game.paused = not game.paused
            if event.key == ord('m'):
                game.map = not game.map
            if event.key == ord('t'):
                ship.sas = not ship.sas
                print "sas enabled" if ship.sas else "sas disabled"

    if ship.thrust < 0:
        ship.thrust = 0
    elif ship.thrust > 1:
        ship.thrust = 1

def main():
    pygame.init()
    pygame.display.set_caption('Leedshack-KSP')
    pygame.key.set_repeat(20, 20)
    game.screen = pygame.display.set_mode((game.width,game.height))
    game.clock = pygame.time.Clock()
    ship.rocket = pygame.image.load("images/real stuff/FULL ROKET.png")
    game.altimeter = pygame.image.load("images/real stuff/altimeter.png")
    game.crashfont = pygame.font.Font(None, 64)
    game.font = pygame.font.Font(None, 32)
    while game.running:
        loop()
        pygame.display.flip()

    pygame.quit()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()

