import os, pygame, math, random, pygame.gfxdraw
from pygame.locals import *

class planet:
    r = 10000

class game:
    width = 320*2
    height = 256*2
    crashed = False
    zoom = 1
    running = True
    paused = False
    screen = None
    map = False
    fuel = 0

class ship:
    x = 0 #planet.r
    y = planet.r #+ 100
    dx = 0
    dy = 0
    phi = math.pi/2  # -math.pi*5.5/4
    dphi = 0
    maxthrust = .02
    thrust = 0
    sas = False
    parachute = False
    crash_tolerance = 0.5
    fuel = 0
    landed = False

def loop():
    SKY = (0,128,255)
    GROUND = (40,120,70)
    RED = (255,0,0)
    BLACK = (0,0,0)
    WHITE = (255,255,255)

    game.clock.tick(60)

    r = math.sqrt(ship.x*ship.x+ship.y*ship.y)

    if game.map:
        # map screen
        pygame.draw.rect(game.screen, BLACK, (0,0,game.width,game.height))
        scale = 0.005

        # orbit
        mu = 100000000 # CHECKME
        h = ship.x*ship.dy - ship.y*ship.dx
        ex = ship.dy*h/mu - ship.x/r
        ey =-ship.dx*h/mu - ship.y/r
        e = math.sqrt(ex*ex+ey*ey)
        if e!=1:
            a = h*h / (mu*(1-e*e))
            omega = math.atan2(ey,ex)
            n = 1000
            for i in xrange(0,n-1):
                theta = i*2*math.pi/n
                d = a*(1-e*e)/(1+e*math.cos(-theta + omega))
                x = d*scale*math.cos(theta)
                y = d*scale*math.sin(theta)
                print d
                game.screen.set_at((int(game.width/2+x),int(game.height/2+y)),WHITE)

        # planet
        pygame.draw.circle(game.screen,GROUND, (int(game.width/2),int(game.height/2)), int(planet.r*scale))

        # ship
        shipx=int(game.width/2+ship.x*scale)
        shipy=int(game.height/2+ship.y*scale)
        pygame.draw.circle(game.screen,WHITE, (shipx, shipy), 2)
        pygame.draw.line(game.screen,WHITE, (shipx,shipy), (int(shipx+10*math.cos(ship.phi)), int(shipy+10*math.sin(ship.phi))))
        pygame.draw.line(game.screen,RED, (shipx,shipy), (int(shipx+ship.dx*4), int(shipy+ship.dy*4)))
    else:
        # Sky and planet

        pygame.draw.rect(game.screen, (0,128-(r-planet.r)/125,255-(r-planet.r)/250), (0,0,game.width,game.height))
        planetx = game.width/2 + ship.x*math.sin(ship.phi) - ship.y*math.cos(ship.phi)
        planety = game.height/2 + ship.x*math.cos(ship.phi) + ship.y*math.sin(ship.phi)
        # circle is inaccurate for large radii
#        if planet.r > 5000:
#            pygame.draw.polygon(game.screen, GROUND, 
#        for x in xrange(0,game.width-1):
#            for y in xrange(0,game.width-1):
#                if (x-planetx)*(x-planetx)+(y-planety)*(y-planety) < planet.r *planet.r:
#                    game.screen.set_at((x,y),GROUND)

        if abs(planetx)<planet.r*2 and abs(planety)<planet.r*2:
            pygame.draw.circle(game.screen,GROUND, (int(planetx),int(planety)), planet.r)
#        n = 16
#        for i in xrange(1,n):
#            pygame.gfxdraw.pie(game.screen, int(planetx), int(planety), int(planet.r*10), 360*i/n, 360*(i+1)/n, (RED if i%2 else BLACK))
        # Spaceship
        if not game.crashed:
            if ship.thrust > 0:
                flames = ship.flame.copy()
                alpha = int(ship.thrust * 255)
                flames.fill((255,255,255,alpha),None,pygame.BLEND_RGBA_MULT)
                game.screen.blit(flames,(game.width/2-5,game.height/2))
                
            if ship.parachute:
                game.screen.blit(ship.parachuteimage,(game.width/2-18,game.height/2-76))
            game.screen.blit(ship.rocket,(game.width/2-10,game.height/2-40))
        else:
            text = game.crashfont.render(game.crashtext, 0, RED)
            textpos = text.get_rect()
            textpos.centerx = game.screen.get_rect().centerx
            textpos.centery = game.screen.get_rect().centery
            game.screen.blit(text,textpos)

            if game.explosionalpha > 1:
                boom = game.explosion.copy()
                game.explosionalpha -= 2
                boom.fill((255,255,255,game.explosionalpha),None,pygame.BLEND_RGBA_MULT)
                game.screen.blit(boom,(game.width/2-64,game.height/2-64))

    # calculations
    if not game.crashed and not game.paused:

        # Physics-y stuff
        ship.dx += ship.maxthrust * ship.thrust * math.cos(ship.phi)
        ship.dy += ship.maxthrust * ship.thrust * math.sin(ship.phi)
        #print "thrust ", ship.thrust * ship.maxthrust * math.cos(ship.phi), ship.maxthrust * ship.thrust * math.sin(ship.phi)

        speed = math.sqrt(ship.dx*ship.dx+ship.dy*ship.dy)
        r = math.sqrt(ship.x*ship.x+ship.y*ship.y)
        theta = math.atan2(ship.y,ship.x)
        
        # Altimeter
        game.screen.blit(game.altimeter,(game.width/2-65-65-8+16-3,5))
        text = game.font.render(str(int(r-planet.r)).zfill(5), 0, (20,20,20))
        textpos = text.get_rect()
        textpos.centerx = game.screen.get_rect().centerx-65-8
        textpos.centery += 14
        game.screen.blit(text,textpos)

        # Velocityometer
        game.screen.blit(game.velocity,(game.width/2+16+8-3,5))
        text = game.font.render(str(int(speed*60)).zfill(5),0,(20,20,20))
        textpos = text.get_rect()
        textpos.centerx = game.screen.get_rect().centerx+65+8
        textpos.centery += 14
        game.screen.blit (text,textpos)

        # Fuel bar and fuel management
        if ship.landed == True and ship.fuel < 4000:
            ship.fuel += 4
        else:
            ship.fuel -= ship.thrust
        if ship.fuel > 3500:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_8.png")
        elif ship.fuel > 3000:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_7.png")
        elif ship.fuel > 2500:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_6.png")
        elif ship.fuel > 2000:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_5.png")
        elif ship.fuel > 1500:
            if pygame.time.get_ticks() % 2000 < 500:
                ship.fuelbar = pygame.image.load("images/fuel/fuel_4-1.png")
            else:
                ship.fuelbar = pygame.image.load("images/fuel/fuel_4.png")
        elif ship.fuel > 1000:
            if pygame.time.get_ticks() % 2000 < 750:
                ship.fuelbar = pygame.image.load("images/fuel/fuel_3-1.png")
            else:
                ship.fuelbar = pygame.image.load("images/fuel/fuel_3.png")
        elif ship.fuel > 500:
            if pygame.time.get_ticks() % 1000 < 500:
                ship.fuelbar = pygame.image.load("images/fuel/fuel_2-1.png")
            else:
                ship.fuelbar = pygame.image.load("images/fuel/fuel_2.png")
        elif ship.fuel > 0:
            if pygame.time.get_ticks() % 1000 < 500:
                ship.fuelbar = pygame.image.load("images/fuel/fuel_1-1.png")
            else:
                ship.fuelbar = pygame.image.load("images/fuel/fuel_1.png")
        else:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_0.png")
            ship.thrust = 0
        game.screen.blit(ship.fuelbar,(8,game.height-59-8))

        # Thrustometer
        game.thrust = pygame.image.load("images/EXTRA BITS/da PEN15 thrust.png") #Reloading to clear surface every time
        pygame.draw.rect(game.thrust,RED,(1,64-ship.thrust*64,22,1),2)
        game.screen.blit(game.thrust,(game.width-64-8-8-24,game.height-8-64))
        
        ship.phi+=ship.dphi
        ship.x += ship.dx
        ship.y += ship.dy
        if ship.sas:
            if ship.dphi:
                ship.dphi += -0.001 if ship.dphi>0 else 0.001

        # Navcircle
        rotatedNavcircle = pygame.transform.rotate(game.navcircle,math.degrees(theta-ship.phi))
        correctedNavcircle = pygame.transform.flip(rotatedNavcircle,1,0)
        navpos = rotatedNavcircle.get_rect()
        game.screen.blit(correctedNavcircle,(game.width-navpos.width/2-32-8,game.height-navpos.height/2-32-8))

        # Sky
        if not map:
            global cloudx; global cloudy
            if r > planet.r+1000 and cloudy > -100:
                cloudx -= 2
                cloudy -= 2
                game.screen.blit(game.cloudedsky, (cloudx,cloudy))

        ship.landed = False
        # we must be:m
        # (a) within epsilon of the surface;
        # (b) going below the maximum safe speed;
        # (c) heading downwards;
        # [(d) pointing up (not yet)]
        # to land safely
        if r < planet.r+1e-8 and planet.r-r<=speed*2 and speed < ship.crash_tolerance \
                and ((ship.x+ship.dx)*(ship.x+ship.dx) + (ship.y+ship.dy)*(ship.y+ship.dy) <= ship.x*ship.x+ship.y*ship.y):
            ship.dx = ship.dy = 0
            ship.x = planet.r * math.cos(theta)
            ship.y = planet.r * math.sin(theta)
            ship.landed = True
            ship.parachute = False
            
        elif (r < planet.r):
            print "crashed", abs(r-planet.r), speed
            game.crashed = True
        else:
            # gravity
            g = 0.01
            ship.dx -= g * math.cos(theta)
            ship.dy -= g * math.sin(theta)
            #print "grav ", -g * math.cos(theta), -g * math.sin(theta)

            # drag
            drag = math.exp(-r/5000)*0.1 if ship.parachute else math.exp(-r/5000)*0.005
            #print "drag=",drag
            ship.dx *= 1-drag
            ship.dy *= 1-drag
        
        #print "theta=",theta
        #print ship.x, ship.dx, ship.y, ship.dy, r, ship.phi

    # Key detection
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
            if event.key == ord('p'):
                ship.parachute = True
                print "chute deployed"
            if event.key == ord('r'):
                cloudx = game.width
                cloudy = game.height
                print "The sky is falling!"

    if ship.thrust < 0:
        ship.thrust = 0
    elif ship.thrust > 1:
        ship.thrust = 1
    if ship.fuel == 0:
        ship.thrust = 0

def main():
    pygame.init()
    pygame.display.set_caption('Leedshack-KSP')
    pygame.key.set_repeat(20, 20)
    global cloudx
    global cloudy
    messages = ["CRASHED","WASTED","YOU DEAD","THE SKY IS UP","OOPS","NOT APOLLO 11","STS-FAILURE"]
    game.crashtext = messages[random.randint(0,6)]
    game.explosionalpha = 255
    cloudx = game.width
    cloudy = game.height
    game.screen = pygame.display.set_mode((game.width,game.height))
    game.clock = pygame.time.Clock()
    ship.rocket = pygame.image.load("images/real stuff/FULL ROKET.png")
    ship.parachuteimage = pygame.image.load("images/real stuff/para_open.png")
    ship.flame = pygame.image.load("images/real stuff/FLAMES.png")
    game.altimeter = pygame.image.load("images/real stuff/altimeter.png")
    game.velocity = pygame.image.load("images/real stuff/velocity_meter.png")
    game.thrust = pygame.image.load("images/EXTRA BITS/da PEN15 thrust.png")
    game.navcircle = pygame.image.load("images/EXTRA BITS/all da ball.png")
    game.cloudedsky = pygame.image.load("images/EASTER_sGGE/cloud_full_of_yks.png")
    game.crashfont = pygame.font.Font("fonts/8-BIT_WONDER.TTF", 48)
    game.font = pygame.font.Font("fonts/DSEG7Classic-Bold.ttf", 20)
    game.explosion = pygame.image.load("images/real stuff/explosion.png")
    ship.fuelbar = pygame.image.load("images/fuel/fuel_8.png")
    ship.fuel = 4000
    while game.running:
        loop()
        pygame.display.flip()

    pygame.quit()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()

