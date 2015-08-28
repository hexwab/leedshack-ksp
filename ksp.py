import os, pygame, math, random, pygame.gfxdraw
from pygame.locals import *

class planet:
    """
    For reference:
    Earth's radius: 6,371km Scale height: 8.5km (distance over which atmosphere decreases by a factor of e (2.71828)) Atmospheric height: 
    Kerbin's radius: 600km Scale height: 5.067km Atmospheric height: 70km (1E-5 atm, ~1 Pa)
    This planet's radius: 600km Scale height: 5km Atmospheric height: ??
    """
    r = 600000
    scale = 5000
    mu = 500000000

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
    ticks = 1

class ship:
    x = 0 #planet.r
    y = planet.r #+ 1000
    dx = 0 #15
    dy = 0
    phi = math.pi/2  # -math.pi*5.5/4
    dphi = 0
    maxthrust = .02
    thrust = 0
    sas = False
    parachute = False
    crash_tolerance = 0.5
    fuel = 0
    maxfuel = 4000
    landed = False

def fmt_distance(d):
    if d==None: return '-'
    return "%.1f km" % (d/1000)

def fmt_time(t):
    if t==None: return '-'
    if t<60: return "%.1f s" % t
    if t<3600: return "%.1f m" % (t/60)
    if t<86400: return "%.1f h" % (t/3600)
    return "%.1f d" % (t/86400)

def tick():
    # Physics-y stuff
    ship.dx += ship.maxthrust * ship.thrust * math.cos(ship.phi)
    ship.dy += ship.maxthrust * ship.thrust * math.sin(ship.phi)
        #print "thrust ", ship.thrust * ship.maxthrust * math.cos(ship.phi), ship.maxthrust * ship.thrust * math.sin(ship.phi)
    ship.speed = speed = math.sqrt(ship.dx*ship.dx+ship.dy*ship.dy)
    r = math.sqrt(ship.x*ship.x+ship.y*ship.y)
    ship.theta = theta = math.atan2(ship.y,ship.x)
    
    if ship.landed and ship.fuel < 4000:
        ship.fuel += 4
    else:
        ship.fuel -= ship.thrust
        
    ship.phi+=ship.dphi
    ship.x += ship.dx
    ship.y += ship.dy
    if ship.sas:
        if ship.dphi:
            ship.dphi += -0.0002 if ship.dphi>0 else 0.0002

    ship.landed = False
    # we must be:
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
        game.map = False
    else:
        # gravity
        g = planet.mu / (r*r)
        ship.dx -= g * math.cos(theta)
        ship.dy -= g * math.sin(theta)
        #print "grav ", -g * math.cos(theta), -g * math.sin(theta)
        
        # drag
        """ Do we want the KSP 70km drag cutout so it's not wasting resources calculating drag for increadibly small numbers?
            As per the KSP wiki, air pressure at that height should be 1E-6 atmospheres, or ~0.1 pascals which is
            0.1N over 1m^2 """
        drag = math.exp(-(r-planet.r)/planet.scale)*0.035 if ship.parachute else math.exp(-(r-planet.r)/planet.scale)*0.0005
        #print "drag=",drag
        ship.dx *= 1-drag
        ship.dy *= 1-drag
        
        #print "theta=",theta
        #print ship.x, ship.dx, ship.y, ship.dy, r, ship.phi

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
        scale = 0.0003*game.zoom

        # orbit
        h = ship.x*ship.dy - ship.y*ship.dx
        ex = ship.dy*h/planet.mu - ship.x/r
        ey =-ship.dx*h/planet.mu - ship.y/r
        e = math.sqrt(ex*ex+ey*ey)
        if e!=1:
            a = h*h / planet.mu
            omega = math.atan2(ey,ex)
            n = 1000
            for i in xrange(0,n-1):
                theta = i*2*math.pi/n
                c = 1+e*math.cos(-theta + omega)
                if c!=0:
                    d = a/c
                    x = d*scale*math.cos(theta)
                    y = d*scale*math.sin(theta)
                    if d>0 and d*scale < 2000:
                        game.screen.set_at((int(game.width/2+x),int(game.height/2+y)),WHITE)
            apo = a/(1-e)
            peri = a/(1+e)
            apo -= planet.r
            peri -= planet.r
            T = None
            if e<1: # elliptic
                a /= (1-e*e)
                T = 2*math.pi*math.sqrt(a*a*a/planet.mu) # CHECKME
                if peri<0:
                    peri = None; T = None
            else: # hyperbolic
                apo = None
                if peri<0:
                    peri = None
        else: #FIXME
            apo = None
            peri = None
            T = None

        # parameter display
        params = (("Ecc.","%.5f" % e),
                  ("Apo. ",fmt_distance(apo)),
                  ("Peri. ",fmt_distance(peri)),
                  ("T", fmt_time(T)),
        )
        x=10; y = 40
        for line in params:
            game.screen.blit(game.textfont.render(line[0], True, WHITE), (x,y))
            game.screen.blit(game.textfont.render(line[1], True, WHITE), (x+40,y))
            y += 18

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
        atmo =(1-math.exp(-(r-planet.r)/planet.scale))
        skycolour = (0,128-atmo*128,255-atmo*255) if atmo < 1 else (0,128,255)
        pygame.draw.rect(game.screen, skycolour, (0,0,game.width,game.height))
        planetx = game.width/2 + ship.x*math.sin(ship.phi) - ship.y*math.cos(ship.phi)
        planety = game.height/2 + ship.x*math.cos(ship.phi) + ship.y*math.sin(ship.phi)
        # pygame's circle is inaccurate for large radii, so draw a circle ourself
        for y in xrange(0,game.height-1):
            if planet.r > abs(y-planety):
                x = math.sqrt(planet.r*planet.r - (y-planety) * (y-planety))
                xmin = planetx-x
                xmax = planetx+x
                xmin = 0 if xmin<0 else xmin
                xmax = game.width-1 if xmax>game.width-1 else xmax
                if xmin<xmax:
                    pygame.draw.line(game.screen,GROUND,(xmin,y),(xmax,y))

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
        for i in xrange(0,game.ticks):
            tick()
        
    # Altimeter
    game.screen.blit(game.altimeter,(game.width/2-65-65-8+16-3,5))
    text = game.font.render(str(int(r-planet.r)).zfill(5), 0, (20,20,20))
    textpos = text.get_rect()
    textpos.centerx = game.screen.get_rect().centerx-65-8
    textpos.centery += 14
    game.screen.blit(text,textpos)

    # Velocityometer
    game.screen.blit(game.velocity,(game.width/2+16+8-3,5))
    text = game.font.render(str(int(ship.speed*60)).zfill(5),0,(20,20,20))
    textpos = text.get_rect()
    textpos.centerx = game.screen.get_rect().centerx+65+8
    textpos.centery += 14
    game.screen.blit (text,textpos)

    # Fuel bar and fuel management
    fuelincrement = int(ship.maxfuel/8)
    if ship.fuel > ship.maxfuel-fuelincrement:
        ship.fuelbar = pygame.image.load("images/fuel/fuel_8.png")
    elif ship.fuel > ship.maxfuel-fuelincrement*2:
        ship.fuelbar = pygame.image.load("images/fuel/fuel_7.png")
    elif ship.fuel > ship.maxfuel-fuelincrement*3:
        ship.fuelbar = pygame.image.load("images/fuel/fuel_6.png")
    elif ship.fuel > ship.maxfuel-fuelincrement*4:
        ship.fuelbar = pygame.image.load("images/fuel/fuel_5.png")
    elif ship.fuel > ship.maxfuel-fuelincrement*5:
        if pygame.time.get_ticks() % 2000 < 500:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_4-1.png")
        else:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_4.png")
    elif ship.fuel > ship.maxfuel-fuelincrement*6:
        if pygame.time.get_ticks() % 2000 < 750:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_3-1.png")
        else:
            ship.fuelbar = pygame.image.load("images/fuel/fuel_3.png")
    elif ship.fuel > ship.maxfuel-fuelincrement*7:
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
    game.thrust = pygame.image.load("images/GUI/thrustbar.png") #Reloading to clear surface every time
    pygame.draw.rect(game.thrust,RED,(1,64-ship.thrust*64,22,1),2)
    game.screen.blit(game.thrust,(game.width-64-8-8-24,game.height-8-64))
    
    # Navcircle
    rotatedNavcircle = pygame.transform.rotate(game.navcircle,math.degrees(ship.theta-ship.phi))
    correctedNavcircle = pygame.transform.flip(rotatedNavcircle,1,0)
    navpos = rotatedNavcircle.get_rect()
    game.screen.blit(correctedNavcircle,(game.width-navpos.width/2-32-8,game.height-navpos.height/2-32-8))

    # Sky
    if not game.map:
        global cloudx; global cloudy
        if r > planet.r+1000 and cloudy > -100:
            cloudx -= 2
            cloudy -= 2
            game.screen.blit(game.cloudedsky, (cloudx,cloudy))

    # Controls
    for event in pygame.event.get():
        if event.type == QUIT:
            game.running = False
            return
        elif event.type == KEYDOWN:
            if event.key == ord('q'):
                game.running = False # Quit
            elif event.key == ord('x'):
                ship.thrust = 0 # 0% thrust
            elif event.key == ord('z'):
                ship.thrust = 1 # 100% thrust
            elif event.key == ord('w'):
                ship.thrust += 1./16 # Thrust increase
            elif event.key == ord('s'):
                ship.thrust -= 1./16 # Thrust decrease
            elif event.key == ord('a'):
                ship.dphi -= .001 # Rotate anticlockwise
            elif event.key == ord('d'):
                ship.dphi += .001 # Rotate clockwise
        elif event.type == KEYUP:
            if event.key == ord(' '):
                game.paused = not game.paused # Pause
            if event.key == ord('m'):
                game.map = not game.map # Map screen
            if event.key == ord('t'):
                ship.sas = not ship.sas # SAS (rotation stabilisation)
                print "sas enabled" if ship.sas else "sas disabled"
            if event.key == ord('p'):
                ship.parachute = True # Parachute
                print "chute deployed"
            if event.key == ord('r'):
                cloudx = game.width # Reset cloud easter egg
                cloudy = game.height
                print "The sky is falling!"
            if event.key == ord('.'): # Time accelerate
                game.ticks*=2
                print game.ticks
            if event.key == ord(','): # Time decelerate
                game.ticks/=2
                if game.ticks < 1:
                    game.ticks = 1
                print game.ticks
            if event.key == ord('-'): # Map zoom out
                game.zoom*=.5
            if event.key == ord('='): # Map zoom in
                game.zoom*=2

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
    messages = ["CRASHED","WASTED","YOU DEAD","THE SKY IS UP","OOPS","HARDLY APOLLO 11","FAILURE"]
    game.crashtext = messages[random.randint(0,6)]
    game.explosionalpha = 255
    cloudx = game.width
    cloudy = game.height
    game.screen = pygame.display.set_mode((game.width,game.height))
    game.clock = pygame.time.Clock()
    ship.rocket = pygame.image.load("images/spaceship/rocket_complete.png")
    ship.parachuteimage = pygame.image.load("images/spaceship/parachute.png")
    ship.flame = pygame.image.load("images/spaceship/flames.png")
    game.altimeter = pygame.image.load("images/GUI/altimeter.png")
    game.velocity = pygame.image.load("images/GUI/velocity_meter.png")
    game.thrust = pygame.image.load("images/GUI/thrustbar.png")
    game.navcircle = pygame.image.load("images/GUI/navcircle.png")
    game.cloudedsky = pygame.image.load("images/secret/cloud_full_of_sky.png")
    game.crashfont = pygame.font.Font("fonts/8-BIT_WONDER.TTF", 45)
    game.font = pygame.font.Font("fonts/DSEG7Classic-Bold.ttf", 20)
    game.textfont = pygame.font.Font(None, 24)
    game.altfont = pygame.font.Font("fonts/8-BIT_WONDER.TTF", 20)
    game.explosion = pygame.image.load("images/world/explosion.png")
    ship.fuelbar = pygame.image.load("images/fuel/fuel_8.png")
    ship.fuel = ship.maxfuel
    while game.running:
        loop()
        pygame.display.flip()

    pygame.quit()

#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()

