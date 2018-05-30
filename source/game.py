

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

from source.spawn import *

import numpy as np
import random

class Game(metaclass = Singleton):

    Instance = None

    def __init__(self):
        self.ships = []
        self.bullets = []
        self.planets = []
        self.spawns = []
        self.bullets_dirty = False

    def update(self, dt):
        if Game().Server:
            if self.bullets_dirty:
                print("Clear bullets")
                bullets_destroyed = [bullet for bullet in self.bullets if not bullet._active and bullet._death_counter <= 0]
                self.bullets = [bullet for bullet in self.bullets if bullet._active or bullet._death_counter > 0]
                self.bullets_dirty = False
                for bullet in bullets_destroyed:
                    print("Delete bullet")
                    bullet.on_delete()
                    del bullet

        for ship in self.ships:
            ship.update(dt)
        for bullet in self.bullets:
            bullet.update(dt)

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()
        for ship in self.ships:
            ship.draw()
        for planet in self.planets:
            planet.draw()

    def random_spawn(self):
        spawns_dist = [(spawn, sum([np.linalg.norm(spawn._position - ship._position) for ship in self.ships])) for spawn in self.spawns]
        spawns_dist.sort(key=lambda x: x[1]);
        return spawns_dist[-1][0];

    def generate(self):

        types = []

        #types.append(PlanetType(size=24, image="planet-24", density=1))
        #types.append(PlanetType(size=32, image="planet-32", density=1))
        #types.append(PlanetType(size=40, image="planet-40", density=1))
        #types.append(PlanetType(size=48, image="gasgiant-48", density=1))

        types.append(PlanetType(size=24, image="logan-24", density=1))
        types.append(PlanetType(size=32, image="logan-32", density=1))
        types.append(PlanetType(size=40, image="logan-40", density=1))
        types.append(PlanetType(size=48, image="logan-48", density=1))

        width = self.width
        height = self.height

        self.spawns.append(Spawn(np.array([64.0, height / 2 + 48]), 90.0))
        self.spawns.append(Spawn(np.array([width - 64.0, height / 2 + 48]), 270.0))

        self.spawns.append(Spawn(np.array([64.0, height / 2 - 48]), 90.0))
        self.spawns.append(Spawn(np.array([width - 64.0, height / 2 - 48]), 270.0))

        #player1 = Ship(color=(200, 0, 0));
        #player2 = Ship(color=(0, 200, 200));



        def random_position():
            valid = False
            pos = np.array([0.0,0.0])
            while not valid:
                valid = True
                pos = np.array([random.randrange(0.0, 1.0*width), random.randrange(0.0, 1.0*height)])
                for spawn in self.spawns:
                    if np.linalg.norm(spawn._position - pos) < 100.0:
                        valid = False
                for planet in self.planets:
                    if np.linalg.norm(planet._position - pos) < 40.0 + planet._radius:
                        valid = False
            return pos


        #player2.respawn(self.spawns[1])
        #player2.set_input(pyglet.window.key.UP, pyglet.window.key.DOWN, pyglet.window.key.LEFT, pyglet.window.key.RIGHT, pyglet.window.key.RSHIFT)

        #Game().ships.append(player1)
        #Game().ships.append(player2)

        density = 1.0 / (250.0*250.0);
        num_planets = int(density *  width * height)

        for i in range(1, num_planets):
            type = types[random.randrange(0, len(types))]
            Game().planets.append(Planet(random_position(), radius=type._size, mass=type._size*type._size*type._size*type._density, image=type._image))

from source.ship import *
from source.planet import *