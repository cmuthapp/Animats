
###
# This file contains definitions for the objects used in the simulation
###

import random
import math
import pickle
import numpy
from pybrain.structure import RecurrentNetwork, FeedForwardNetwork, LinearLayer, SigmoidLayer, FullConnection
import datetime

class Environment:
    def __init__(self, num_animats_A, num_animats_B, width, height, filename):
        # Helper method
        def load_animats(self, animats, num_animats, type, saved_states=[]):
            while len(animats) < num_animats:
                pos = self.findSpace(Animat.radius, (0, self.height))
                if len(saved_states) > 0:
                    a = saved_states.pop(0)
                    a.x = pos[0]
                    a.y = pos[1]
                else:
    	            a = type(pos[0], pos[1], random.random() * 360)
    	            a.generation = 0
                animats.append(a)

        # training mode (foods everywhere)
        self.training_mode = False
        # environment
        self.width = width
        self.height = height
        # record log
        self.log = []
        self.moveLog = []
        # save state
        self.filename = filename

        # Fruit
        self.num_oranges = num_animats_B
        self.num_bananas = num_animats_A
        self.oranges = []
        self.bananas = []

        self.produceFruits 


        # animats
        self.num_animats_A = num_animats_A
        self.num_animats_B = num_animats_B

        self.deaths_A = []
        self.deaths_B = []

        self.animats_A = []
        self.animats_B = []

        saved_states_A, saved_states_B = self.load()

        # Load the animats of type A
        load_animats(self, self.animats_A, self.num_animats_A, TypeA, saved_states_A)
        load_animats(self, self.animats_B, self.num_animats_B, TypeB, saved_states_B)

        # Start time
        self.start_time = datetime.datetime.utcnow()

    # animat line of sight
    def line_of_sight(self, animat):
        step_x = int(math.cos(animat.direction*math.pi / 180) * 10)
        step_y = int(math.sin(animat.direction*math.pi / 180) * 10)
        new_x = animat.x + step_x
        new_y = animat.y + step_y
        sees = None
        while not sees:
            new_x += step_x
            new_y += step_y
            sees = self.collision(new_x, new_y, Animat.radius, animat)

        return sees

    # find a random spot to spawn animats
    def findSpace(self, radius, bounds):
        spawns_x = list(range(0, self.width, 10))
        spawns_y = list(range(int(bounds[0]), int(bounds[1]), 10))
        random.shuffle(spawns_x)
        random.shuffle(spawns_y)
        for x in spawns_x:
            for y in spawns_y:
                if not self.collision(x, y, radius):
                    return (x, y)

    # return the amount of food in the environment to a fixed state
    def produceFruits(self, train=False):
        # fruit_bounds = (0, self.height / 7)
        # veggie_bounds =  (self.height - self.height / 7, self.height)
        # if self.training_mode:
        bounds = (0, self.height)

        # Fill oranges
        while len(list(filter(lambda f : isinstance(f, Orange), self.oranges))) < self.num_oranges:
            pos = self.findSpace(Fruit.radius, bounds)
            self.oranges.append(Orange(pos[0], pos[1]))

        while len(list(filter(lambda f : isinstance(f, Banana), self.bananas))) < self.num_bananas:
            pos = self.findSpace(Fruit.radius, bounds)
            self.bananas.append(Banana(pos[0], pos[1]))

    def update(self):
        ###
        # If an animat  died, the two fittest animats of each type mate
        ###
        def update_deaths(self, deaths, animats_same_type, animats_other_type):
            while len(deaths) > 0:
                fittest_same_type  = sorted(animats_same_type, key = lambda a : -a.avg_hunger)
                fittest_other_type = sorted(animats_other_type, key = lambda a : -a.avg_hunger)

                pos = self.findSpace(Animat.radius, (0, self.height))
                child = fittest_same_type[0].mate(fittest_other_type[1])
                child.x = pos[0]
                child.y = pos[1]
                animats_same_type.append(child)

                self.log.append((
                    (datetime.datetime.utcnow() - self.start_time).total_seconds(),
                    deaths[0].__class__.__name__,
                    deaths[0].generation,
                    deaths[0].age,
                    deaths[0].num_peeled
                ))

                # Remove animat from active
                animats_same_type.remove(deaths.pop(0))

        update_deaths(self, self.deaths_A, self.animats_A, self.animats_B)
        update_deaths(self, self.deaths_B, self.animats_B, self.animats_A)

        for animat in (self.animats_A + self.animats_B):
            # update sensory information from environment
            animat.sees = self.line_of_sight(animat)
            step = 3
            step_x = int(math.cos(animat.direction*math.pi / 180) * step)
            step_y = int(math.sin(animat.direction*math.pi / 180) * step)
            animat.touching = self.collision(animat.x + step_x, animat.y + step_y, Animat.radius, animat)

            # update animat response to environment
            animat.update()

            # perform animat decided action in environment
            if animat.wants_to_move and (not animat.touching):
                animat.x = step_x + animat.x
                animat.y = step_y + animat.y

            if isinstance(animat.touching, Fruit) and animat.wants_to_peel and animat.can_peel(animat.touching):
                animat.num_peeled += 1
                animat.touching.is_peeled = True

            if isinstance(animat.touching, Fruit) and animat.wants_to_eat and animat.can_eat(animat.touching):
                # Remove food
                if isinstance(animat.touching, Orange):
                    self.oranges.remove(animat.touching)
                else:
                    self.bananas.remove(animat.touching)

                # Update hunger
                emwa_constant = 0.5
                animat.hunger = animat.hunger + 500
                animat.avg_hunger = (1 - emwa_constant) * animat.avg_hunger + emwa_constant * animat.hunger

            self.produceFruits()

            # murder animat
            if (animat not in self.deaths_A) and (animat not in self.deaths_B) and (animat.hunger < 500):
                if isinstance(animat, TypeA):
                    self.deaths_A.append(animat)
                else:
                    self.deaths_B.append(animat)


    def collision(self, x, y, radius, without=None):
        # check wall collision
        if (y + radius) > self.height or (x + radius) > self.width or (x - radius) < 0 or (y - radius) < 0:
            return self

        # check food collision
        for food in (self.oranges + self.bananas):
            if (x - food.x) ** 2 + (y - food.y) ** 2 <= Fruit.radius ** 2:
                return food

        # check animat-animat collision
        animats = list(self.animats_A + self.animats_B)
        if without:
            animats.remove(without)

        for animat in animats:
            if (x - animat.x)**2 + (y - animat.y)**2 <= Animat.radius**2:
                return animat

        # no collision
        return None


    # load saved animat states into environment
    def load(self):
        if self.filename == "":
            return [], []
        try:
            with open(self.filename, 'rb') as f:
                return pickle.load(f)
        except:
            print("Could not load file " + self.filename)
            return [], []

    def save(self):
        if self.filename != "":
            with open(self.filename, 'wb') as f:
                pickle.dump((self.animats_A, self.animats_B), f)


class Animat:
    radius = 30
    def __init__(self, x, y, direction):
        self.age = 0

        # position
        self.x = x
        self.y = y

        # number of going back and forth for different foods
        self.num_peeled = 0

        # orientation (0 - 359 degrees)
        self.direction = direction

        # touching anything
        self.touching = None
        self.sees = None

        # hunger sensor
        self.hunger = 2000
        self.avg_hunger = 0

        ###
        # Neural Network
        #
        # Inputs:
        # 1. sees_peeled_orange
        # 2. sees_unpeeled_orange
        # 3. sees_peeled_banana
        # 4. sees_unpeeled_banana
        # 5. sees_animat
        # 6. sees_wall
        # 7. hunger
        # 8. touching_peeled_orange
        # 9. touching_unpeeled_orange
        # 10. touching_peeled_banana
        # 11. touching_unpeeled_banana
        # 12. touching_animat
        # 13. touching_wall
        ###

        self.net = FeedForwardNetwork()
        self.net.addInputModule(LinearLayer(13, name='in'))
        self.net.addModule(SigmoidLayer(14, name='hidden'))
        self.net.addOutputModule(LinearLayer(5, name='out'))
        self.net.addConnection(FullConnection(self.net['in'], self.net['hidden']))
        self.net.addConnection(FullConnection(self.net['hidden'], self.net['out']))
        self.net.sortModules()

        # thresholds for deciding an action
        self.move_threshold = 0
        self.peel_threshold = 0
        self.eat_threshold = 0

    def update(self):

        # basics
        self.age += 1
        self.hunger -= 0.5 # Hunger increases with time

        sensors = (
            # 1. sees_peeled_orange
            2000 * int(isinstance(self.sees, Orange) and self.sees.is_peeled),
            # 2. sees_unpeeled_orange
            2000 * int(isinstance(self.sees, Orange) and not self.sees.is_peeled),
            # 3. sees_peeled_banana
            2000 * int(isinstance(self.sees, Banana) and self.sees.is_peeled),
            # 4. sees_unpeeled_banana
            2000 * int(isinstance(self.sees, Banana) and not self.sees.is_peeled),
            # 5. sees_animat
            2000 * int(isinstance(self.sees, Animat)),
            # 6. sees_wall
            2000 * int(isinstance(self.sees, Environment)),
            # 7. hunger
            self.hunger,
            # 8. touching_peeled_orange
            2000 * int(isinstance(self.touching, Orange) and not self.touching.is_peeled),
            # 9. touching_unpeeled_orange
            2000 * int(isinstance(self.touching, Orange) and self.touching.is_peeled),
            # 10. touching_peeled_banana
            2000 * int(isinstance(self.touching, Banana) and not self.touching.is_peeled),
            # 11. touching_unpeeled_banana
            2000 * int(isinstance(self.touching, Banana) and self.touching.is_peeled),
            # 12. touching_animat
            2000 * int(isinstance(self.touching, Animat)),
            # 13. touching_wall
            2000 * int(isinstance(self.touching, Environment))
        )

        decision = self.net.activate(sensors)

        ###
        # Output layer in neural network
        # 0. wants_to_move
        # 1. turn_left
        # 2. turn_right
        # 3. wants_to_peel
        # 4. wants_to_eat
        ###

        # move forward
        self.wants_to_move = (decision[0] > self.move_threshold)

        # turn_left
        self.direction -= decision[1]

        # turn_right
        self.direction += decision[2]

        # wants_to_peel
        self.wants_to_peel = decision[3] > self.peel_threshold

        # wants_to_eat
        self.wants_to_eat = decision[4] > self.eat_threshold

    # returns a child with a genetic combination of neural net weights of 2 parents
    def mate(self, other):
        child = type(self)(0, 0, random.random() * 360)
        child.generation = min(self.generation, other.generation) + 1

        # inherit parents connection weights
        for i in range(0,len(self.net.params)):
            if random.random() > .1:
                child.net.params[i] = random.choice([self.net.params[i], other.net.params[i]])

        return child

###
# Separate types of animats
# 1. Type A: Eats Banana and peels Orange
# 2. Type B: Eats Orange and peels Banana
###
class TypeA(Animat):
    def can_peel(self, obj):
        return isinstance(obj, Orange) and not obj.is_peeled

    def can_eat(self, obj):
        return isinstance(obj, Banana) and obj.is_peeled

class TypeB(Animat):
    def can_peel(self, obj):
        return isinstance(obj, Banana) and not obj.is_peeled

    def can_eat(self, obj):
        return isinstance(obj, Orange) and obj.is_peeled

###
# Fruit items that populate the map
###
class Fruit:
    radius = 20
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_peeled = False

class Orange(Fruit): pass
class Banana(Fruit): pass
