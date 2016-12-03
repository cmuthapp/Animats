#!/usr/bin/python
import pygame
import sys
from .model import *
import os
import time

folder_root = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
resource_folder = os.path.abspath(os.path.join(folder_root, "resources"))
# "/Users/pranav/Academic/CS263/altruism_in_animats/resources/"

class Simulation:
    def __init__(self, num_animats_A, num_animats_B, width, height, saved_nets):
        # initialize pygame
        pygame.init()

        # initialize the screen
        self.size = width, height
        self.screen = pygame.display.set_mode(self.size)
        self.screenWidth = width
        self.screenHeight = height

        # set the name of display windows
        pygame.display.set_caption('Altruism Experiment')

        #initialize sprites
        print(os.getcwd())
        self.bg = pygame.image.load(os.path.join(resource_folder, "bg.jpg"))

        # pictures resources
        self.animat_A_sprite = pygame.image.load(os.path.join(resource_folder, "animat_A.png"))
        self.animat_B_sprite = pygame.image.load(os.path.join(resource_folder, "animat_B.png"))
        self.orange_unpeeled = pygame.image.load(os.path.join(resource_folder, "orange_unpeeled.png"))
        self.orange_peeled   = pygame.image.load(os.path.join(resource_folder, "orange_peeled.png"))
        self.banana_peeled   = pygame.image.load(os.path.join(resource_folder, "banana_peeled.png"))
        self.banana_unpeeled = pygame.image.load(os.path.join(resource_folder, "banana_unpeeled.png"))

        # modify pictures to appropriate sizes
        self.animat_A_sprite = pygame.transform.scale(self.animat_A_sprite, (32,32))
        self.animat_B_sprite = pygame.transform.scale(self.animat_B_sprite, (32,32))

        self.bg            = pygame.transform.scale(self.bg, (width, height))
        self.orange_unpeeled = pygame.transform.scale(self.orange_unpeeled, (26, 26))
        self.orange_peeled   = pygame.transform.scale(self.orange_peeled, (26, 26))
        self.banana_peeled   = pygame.transform.scale(self.banana_peeled, (26, 26))
        self.banana_unpeeled = pygame.transform.scale(self.banana_unpeeled, (26, 26))

        self.env = Environment(num_animats_A, num_animats_B, width, height, saved_nets)

    def update(self, speed):
        # update model a certain number of times
        for i in range(speed):
            self.env.update()

        # for future 'pause' button, the parameter take milliseconds pause time
        # pygame.time.wait()

        # repaint
        self.screen.blit(self.bg, (0,0))

        # paint fruit
        for fruit in (self.env.oranges + self.env.bananas):
            coord = (fruit.x - Fruit.radius, fruit.y - Fruit.radius)
            if isinstance(fruit, Orange) and fruit.is_peeled:
                self.screen.blit(self.orange_peeled, coord)
            elif isinstance(fruit, Orange) and not fruit.is_peeled:
                self.screen.blit(self.orange_unpeeled, coord)
            elif isinstance(fruit, Banana) and fruit.is_peeled:
                self.screen.blit(self.banana_peeled, coord)
            elif isinstance(fruit, Banana) and not fruit.is_peeled:
                self.screen.blit(self.banana_unpeeled, coord)

        # paint animats
        for animat in (self.env.animats_A + self.env.animats_B):
            sprite = self.animat_A_sprite if isinstance(animat, TypeA) else self.animat_B_sprite
            self.screen.blit(
                pygame.transform.rotate(sprite, 360 - animat.direction),
                (animat.x - Animat.radius, animat.y - Animat.radius)
            )

        pygame.display.flip()

def runSim(num_animats_A = 10, num_animats_B = 10, width = 1000, height = 700, filename=""):
    simulation = Simulation(num_animats_A, num_animats_B, width, height, filename)

    # Create file
    fLog = open(os.path.join(folder_root, "log.txt"), 'w')
    fLog.close()


    def flush_logs():
        with open(os.path.join(folder_root, "log.txt"),'a') as fLog:
            for r in simulation.env.log:
                fstr = " ".join(map(str, r))
                fLog.write(fstr + '\n')
            simulation.env.log = []


    i = 1
    while 1:
        i = i + 1
        if i % 5 == 0:
            flush_logs()

        for event in pygame.event.get():
            # check for exit
            if event.type == pygame.QUIT:
                simulation.env.save()
                flush_logs()
                sys.exit()

        simulation.update(10)
