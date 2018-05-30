import pyglet


import math

from source.body import *

from source.game import *

from source.bullet import *

from source.packets import *

class Ship(Body, SyncedObject):

    id = 0

    def __init__(self, color = (255, 255, 255), **kwargs):
        self._id = Ship.id + 1
        Ship.id += 1
        Body.__init__(self, drag = 2.0, angdrag= 3.0, **kwargs)
        self._radius = 24.0
        self._laser = 0.0
        self._health = 1.0
        self._color = color

        SyncedObject.__init__(self, **kwargs)

        if Game().Server:
            self._client = None
            self._key_up = False
            self._key_down = False
            self._key_left = False
            self._key_right = False
            self._key_fire = False

        if Game().Client:
            self._images = [
                pyglet.resource.image('galpin-0.png'),
                pyglet.resource.image('galpin-1.png'),
                pyglet.resource.image('galpin-2.png')
                ]
            for image in self._images:
                image.anchor_x = image.width // 2
                image.anchor_y = image.height // 2

            self._sprites = [pyglet.sprite.Sprite(img=image) for image in self._images]
            for sprite in self._sprites:
                sprite.scale = (2*self._radius) / sprite.image.width
                sprite.color = self._color
            self._sound_fire = pyglet.resource.media('fire.wav', streaming=False)
            self._sound_explosion = pyglet.resource.media('explosion.wav', streaming=False)




    def respawn(self, spawn):
        self._velocity = np.array([0.0, 0.0])
        self._angvelocity = 0.0
        self._position = np.array(spawn._position)
        self._rotation = np.array(spawn._rotation)
        self._laser = 0.0
        self._health = 1.0

    def update(self, dt):
        super().update(dt)
        if Game().Server:

            self.set_throttle(dt, 1.0 if self._key_up else (-0.5 if self._key_down else 0.0))
            self.set_turn(dt, self._key_left, self._key_right)
            if self._key_fire:
                self._laser += dt

            if self._laser < 0.0:
                self._laser += dt
                if self._laser > 0.0:
                    self._laser = 0.0
            for ship in Game().ships:
                if ship == self:
                    continue;
                self.prevent_collisions(ship, dt);
            for planet in Game().planets:
                self.prevent_collisions(planet, dt);

            if self._position[0] < 0:
                dif = 0 - self._position[0];
                self._velocity += np.array([1,0]) * dt * 100 * max(1, dif / 5)
            if self._position[1] < 0:
                dif = 0 - self._position[1];
                self._velocity += np.array([0,1]) * dt * 100 * max(1, dif / 5)
            if self._position[0] > Game().width:
                dif = self._position[0] - Game().width;
                self._velocity += np.array([-1,0]) * dt * 100 * max(1, dif / 5)
            if self._position[1] > Game().height:
                dif = self._position[1] - Game().height;
                self._velocity += np.array([0,-1]) * dt * 100 * max(1, dif / 5)

    def prevent_collisions(self, ship, dt):
        offset = self._position - ship._position
        distance = np.linalg.norm(offset)
        minrad = self._radius + ship._radius
        if not distance > 0:
            distance = 0.01
        if distance < minrad :
            dif = minrad - distance;
            self._velocity += (offset / distance) * dt * 100 * max(1, dif/5)

    def draw(self):
        sprite = self._sprites[0]
        if(self._health < 0.66):
            sprite = self._sprites[1]
        if (self._health < 0.33):
            sprite = self._sprites[2]

        sprite.rotation = self._rotation;
        sprite.set_position(self._position[0], self._position[1])
        sprite.draw()

    def set_throttle(self, dt, value):
         self._velocity += dt * self.forward() * 200 * value

    def set_turn(self, dt, left, right):
        if left:
            self._angvelocity -= dt * 200;
        if right:
            self._angvelocity += dt * 200;

    def set_input(self, up, down, left, right, fire):
        self._input_up = up
        self._input_down = down
        self._input_left = left
        self._input_right = right
        self._input_fire = fire

    def on_key_press(self, key, modifiers):
        pass

    def on_key_release(self, key, modifiers):
        if key == self._input_fire:
            self.fire()

    def fire(self):
        if Game().Client:
            Game()._server.callRemote(PacketShipFire, id=self.id)
            self._sound_fire.play()
        if Game().Server:
            if self._laser > 0:
                Game().bullets.append(Bullet(position=self._position + self.forward() * 24.0,
                                             velocity=self._velocity + self.forward() * (50+200*self._laser),
                                             traillength=50, damage=0.7, color=self._color))
                self._laser = -0.5

    def on_hit(self, bullet):
        self._health -= bullet._damage

        off = self._position - bullet._position
        dist = np.linalg.norm(off)

        self._velocity += (off/dist) * Game().dt * 4000 * bullet._damage

        if(self._health < 0.0):
            self.on_destroy()

    def on_destroy(self):
        for i in range(0, 10):
            ang = random.randrange(0, 360)
            rad = random.randrange(0, self._radius)
            velmag = random.randrange(20, 100) * (0.5 + 0.5 * rad/self._radius)
            pos = rad * np.array([math.cos(ang), math.sin(ang)])
            vel = velmag * np.array([math.cos(ang), math.sin(ang)])
            if False:
                Game().bullets.append(Bullet(self._position + pos,
                                             self._velocity + vel,
                                             15,
                                             life = random.randrange(2, 4),
                                             damage = 0.2,
                                             color=self._color))
        self.respawn(Game().random_spawn())
        #self._sound_explosion.play()

    def update_connected(self, client):
        client.callRemote(PacketShip,
                          id = int(self.id),
                          color_r = int(self._color[0]),
                          color_g = int(self._color[1]),
                          color_b = int(self._color[2]),
                          position_x = float(self._position[0]),
                          position_y = float(self._position[1]),
                          velocity_x = float(self._velocity[0]),
                          velocity_y = float(self._velocity[1]),
                          rotation = float(self._rotation),
                          angvelocity = float(self._angvelocity),
                          isme = self._client == client
                          )

    def update_sync(self, client):
        client.callRemote(PacketShipUpdate,
                          id=int(self.id),
                          position_x=float(self._position[0]),
                          position_y=float(self._position[1]),
                          velocity_x=float(self._velocity[0]),
                          velocity_y=float(self._velocity[1]),
                          rotation=float(self._rotation),
                          angvelocity=float(self._angvelocity),
                          health=float(self._health)
                          )

import random