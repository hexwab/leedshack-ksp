import os, pygame, math
from pygame.locals import *

planet = { "r": 2000 }
ship = { "x": 0, "y": planet["r"], "dx": 0, "dy": 0, "phi": math.pi/2, "dphi": 0, "maxthrust": .02, "thrust": 0 }
crashed = False
landed = False
zoom=1


def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((640,480))
    pygame.display.set_caption('Leedshack-KSP')
    pygame.mouse.set_visible(0)

    pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()

    SKY = (0,128,255)
    GROUND = (0,128,0)

#Main Loop
    while 1:
        clock.tick(60)
        pygame.draw.rect(screen, SKY, (0,0,640,480))
        planetx = 160 + ship["x"]*math.sin(ship["phi"]) + ship["y"]*math.cos(ship["phi"])
        planety = 128 - ship["x"]*math.cos(ship["phi"]) + ship["y"]*math.sin(ship["phi"])
        pygame.draw.circle(screen,(0,255,0), (int(planetx),int(planety)), planet["r"])
        

    #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == ord('q'):
                    return

        pygame.display.flip()



#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()

