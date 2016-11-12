#!/usr/bin/python
import pygame
import sys
from .model import *

class Simulation:
    def __init__(self, num_animats, width, height, saved_nets):
        # initialize pygame
        pygame.init()

        # initialize the screen
        self.size = width, height
        self.screen = pygame.display.set_mode(self.size)
        self.screenWidth = width
        self.screenHeight = height

        # set the name of display windows
        pygame.display.set_caption('Import/Export project')

        #initialize sprites
        self.bg = pygame.image.load("resources/bg.png")

        # pictures resources
        self.animat_sprite  = pygame.image.load("resources/animat.png")
        self.fruit          = pygame.image.load("resources/banana.png")
        self.veggie         = pygame.image.load("resources/tomato.png")

        # modify pictures to appropriate sizes
        self.animat_sprite = pygame.transform.scale(self.animat_sprite, (32,32))
        self.bg            = pygame.transform.scale(self.bg, (1000, 700))
        self.fruit         = pygame.transform.scale(self.fruit, (26, 26))
        self.veggie        = pygame.transform.scale(self.veggie, (26, 26))

        self.env = Environment(num_animats, width, height, saved_nets)

    def update(self, speed):
        # update model a certain number of times
        for i in range(speed):
            self.env.update()

        # for future 'pause' button, the parameter take milliseconds pause time
        # pygame.time.wait()

        # repaint
        self.screen.blit(self.bg, (0,0))

        # paint food
        for food in self.env.foods:
            if isinstance(food, Fruit):
                self.screen.blit(
                    self.fruit,
                    (food.x - Food.radius, food.y - Food.radius)
                )
            else:
                self.screen.blit(
                    self.veggie,
                    (food.x - Food.radius, food.y - Food.radius)
                )

        # paint animats
        for animat in self.env.animats:
            self.screen.blit(
                pygame.transform.rotate(self.animat_sprite, 360 - animat.direction),
                (animat.x - Animat.radius, animat.y - Animat.radius)
            )
            if animat.food:
                if isinstance(animat.food, Fruit):
                    self.screen.blit(
                        self.fruit,
                        (animat.x - Animat.radius, animat.y - Animat.radius)
                    )
                elif isinstance(animat.food, Veggie):
                    self.screen.blit(
                        self.veggie,
                        (animat.x - Animat.radius, animat.y - Animat.radius)
                    )

        pygame.display.flip()

def runSim(num_animats = 10, width = 1000, height = 700, filename=""):
    simulation = Simulation(num_animats, width, height, filename)

    while 1:
        for event in pygame.event.get():
            # check for exit
            if event.type == pygame.QUIT:
                simulation.env.save()

                # save record log
                fLog = open("log.txt",'w')
                map(lambda r: fLog.write( str(r) + '\n'), simulation.env.log)
                fLog.close()
                sys.exit()

        simulation.update(10)
