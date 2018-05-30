from source.body import *

import pyglet

from source.game import *
from source.syncedobject import *
from source.packets import *

class Bullet(Body, SyncedObject):

    def __init__(self, position=None, velocity=None, traillength=20, color= (255, 255, 255), life= 10.0, damage=1.0, **kwargs):
        Body.__init__(self, position = position, velocity= velocity, **kwargs)
        SyncedObject.__init__(self, **kwargs)
        self._color = color
        if Game().Client:
            self._trail = []
            self._trainlength = traillength

        self._active = True
        if Game().Server:
            self._death_counter = traillength
            self._life = life
            self._damage = damage

    def update(self, dt):
        Body.update(self, dt)
        if Game().Client:
            self._trail.append(np.array(self._position))
            if len(self._trail) > self._trainlength:
                self._trail.pop(0)
        if self._active:
            if Game().Server:
                self._life -= dt
                if(self._life < 0):
                    self.on_collide()

                # Ship Collisions
                for ship in Game().ships:
                    distance = np.linalg.norm(ship._position - self._position)
                    if distance < ship._radius:
                        ship.on_hit(self)
                        self.on_collide()

            for planet in Game().planets:
                distance = np.linalg.norm(planet._position - self._position)

                # Gravity Force
                self._velocity += 0.5 * planet._mass * (planet._position - self._position) / (distance * distance * distance)

                # Planet Collisions
                if distance < planet._radius:
                    self.on_collide()
        else:
            if Game().Server:
                self._death_counter -= 1
                if self._death_counter < 0:
                    Game().bullets_dirty = True

    def on_collide(self):
        if Game().Server:
            self._active = False
            self._velocity = np.array([0.0,0.0])
            Game().bullets_dirty = True

    def draw(self):
        numberOfVertices = len(self._trail)
        vertices = []  # initialize a list of vertices
        for pt in self._trail:
            vertices.append(pt[0])  # append the x value to the vertex list
            vertices.append(pt[1])  # append the y value to the vertex list

        vertexList = pyglet.graphics.vertex_list(numberOfVertices, ('v2f', vertices))

        # now use pyGlet commands to draw lines between the vertices
        pyglet.gl.glColor3f(self._color[0]/255.0, self._color[1]/255.0, self._color[2]/255.0)  # specify colors
        vertexList.draw(pyglet.gl.GL_LINE_STRIP)  # draw

    def update_connected(self, client):
        client.callRemote(PacketBulletNew,
                          id=int(self.id),
                          color_r = int(self._color[0]),
                          color_g=int(self._color[1]),
                          color_b=int(self._color[2]),
                          position_x=float(self._position[0]),
                          position_y=float(self._position[1]),
                          velocity_x=float(self._velocity[0]),
                          velocity_y=float(self._velocity[1])
                          )

    def update_sync(self, client):
        client.callRemote(PacketBulletUpdate,
                          id = int(self.id),
                          position_x = float(self._position[0]),
                          position_y=float(self._position[1]),
                          velocity_x=float(self._velocity[0]),
                          velocity_y=float(self._velocity[1]),
                            active=self._active
                          )