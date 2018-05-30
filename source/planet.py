from source.body import *

import pyglet

from source.game import *
from source.packets import *


class Planet(Body, SyncedObject):

    def __init__(self, position, radius = 24.0, mass = 24.0 * 24.0, image = "planet-40", **kwargs):
        Body.__init__(self, position=position)
        SyncedObject.__init__(self, **kwargs)
        self._radius = radius
        self._mass = mass
        self._imagepath = image;
        if Game().Client:
            self._image = pyglet.resource.image(image + '.png')
            self._image.anchor_x = self._image.width // 2
            self._image.anchor_y = self._image.height // 2
            self._sprite = pyglet.sprite.Sprite(img=self._image)
            self._sprite.scale = (2*self._radius) / self._image.width

    def draw(self):
        self._sprite.set_position(self._position[0], self._position[1])
        self._sprite.draw()

    def update_connected(self, client):
        client.callRemote(PacketPlanet, id = self.id, mass = float(self._mass), radius = float(self._radius), image = self._imagepath, position_x = float(self._position[0]), position_y = float(self._position[1]))

class PlanetType:

    def __init__(self, size=40, image="planet-40", density=1):
        self._size = size
        self._image = image
        self._density = density