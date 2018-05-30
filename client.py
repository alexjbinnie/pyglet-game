"""A simple example of Pyglet/Twisted integration. A Pyglet window
is displayed, and both Pyglet and Twisted are making scheduled calls
and regular intervals. Interacting with the window doesn't interfere
with either calls.
"""
import pyglet

from source import pygletreactor
from source.game import *
from source.ship import *
from source.planet import *
from source.packets import *

pygletreactor.install()  # Must be installed before importing reactor from twisted.internet
from twisted.internet import reactor, task, protocol

# Create a Pyglet window with a simple message
window = pyglet.window.Window(fullscreen=False)

# Set resource path
pyglet.resource.path = ["resources"]
pyglet.resource.reindex()

# Establish to the game that this is the Client
Game().Server = False
Game().Client = True

# Set the initial game size (will be resized on connection to server)
Game().width = window.width;
Game().height = window.height;

# Input handling
# TODO: Needs reworking
Game.keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(Game.keys)
keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)

# The main drawing loop of pyglet
@window.event
def on_draw():
    window.clear()
    Game().draw()


# The main update loop in pyglet
def update(dt):
    Game().dt = dt
    Game().update(dt)

# Schedule the update loop to run at 60 FPS
pyglet.clock.schedule_interval(update, 1.0 / 60.0)


@window.event
def on_close():
    reactor.callFromThread(reactor.stop)
    # Return true to ensure that no other handlers on the stack receive the on_close event
    return True

# Handle key presses
@window.event
def on_key_press(symbol, modifiers):
    for ship in Game().ships:
        ship.on_key_press(symbol, modifiers)

# Handle key releases
@window.event
def on_key_release(symbol, modifiers):
    for ship in Game().ships:
        ship.on_key_release(symbol, modifiers)


# Client Protocol
class ClientAMPProtocol(amp.AMP):
    def __init__(self):
        self.output = None
        self._ship = None
        Game()._server = self

    def input_loop(self):
        if self._ship:
            self.callRemote(PacketShipInput, id=self._ship.id,
                            up=Game().keys[self._ship._input_up],
                            down=Game().keys[self._ship._input_down],
                            left=Game().keys[self._ship._input_left],
                            right=Game().keys[self._ship._input_right],
                            fire=Game().keys[self._ship._input_fire])


    def connectionMade(self):
        print("Client has Made a Connection")
        self._input_loop = task.LoopingCall(self.input_loop)
        self._input_loop.start(1/10.0)

    @PacketGameSize.responder
    def packetgamesize(self, width, height):
        #print("Packet Game Size:")
        window.set_size(width, height)
        return {}

    @PacketPlanet.responder
    def packetplanet(self, id=None, image=None, radius=None, mass=None, position_x=None, position_y=None):
        #print("Packet Planet")
        Game().planets.append(Planet(id=id, image=image, radius=radius, mass=mass, position=np.array([position_x, position_y])))
        return {}

    @PacketShip.responder
    def packetship(self, id=None, color_r=None, color_g=None, color_b=None, position_x=None, position_y=None, velocity_x=None, velocity_y=None, rotation=None,
                   angvelocity=None, isme=None):
        if id is not None and id not in SyncedObject.objects.keys():
            ship = Ship(
                id = id,
                position=np.array([position_x, position_y]),
                color=(color_r, color_g, color_b),
                velocity=np.array([velocity_x, velocity_y]),
                rotation=rotation,
                angvelocity=angvelocity
            );
            if isme:
                self._ship = ship
            Game().ships.append(ship)
            ship.set_input(pyglet.window.key.UP, pyglet.window.key.DOWN, pyglet.window.key.LEFT, pyglet.window.key.RIGHT, pyglet.window.key.SPACE)
        return {}

    @PacketShipUpdate.responder
    def packetshipupdate(self, id=None, position_x=0.0, position_y=0.0,
                   velocity_x=0.0, velocity_y=0.0, rotation=None,
                   angvelocity=None, health=None):
        #print("Packet Ship Update. ID: " + str(id))
        try:
            ship = SyncedObject.objects[id]
            ship._position = np.array([position_x, position_y])
            ship._velocity = np.array([velocity_x, velocity_y])
            ship._rotation = rotation
            ship._angvelocity = angvelocity
            ship._health = health
        except KeyError as e:
            print("no ship with id " + str(id))


        return {}

    @PacketBulletNew.responder
    def packetbulletnew(self, id=None, color_r=None, color_g=None, color_b=None, position_x=None, position_y=None,
                   velocity_x=None, velocity_y=None):
        #print("Packet Bullet. ID: " + str(id))
        if id is not None:
            bullet = Bullet(
                id=id,
                position=np.array([position_x, position_y]),
                color=(color_r, color_g, color_b),
                velocity=np.array([velocity_x, velocity_y])
            );
            Game().bullets.append(bullet)

        return {}

    @PacketBulletUpdate.responder
    def packetbulletupdate(self, id=None, position_x=None, position_y=None,
                         velocity_x=None, velocity_y=None, active=True):
        #print("Packet Bullet Update. ID: " + str(id))
        try:
            bullet = SyncedObject.objects[id]
            bullet._position = np.array([position_x, position_y])
            bullet._velocity = np.array([velocity_x, velocity_y])
            bullet._active = active
        except KeyError as e:
            pass

        return {}

    @PacketDelete.responder
    def packetdelete(self, id=None):
        print("Delete " + str(id))
        try:
            obj = SyncedObject.objects[id]
            Game().ships = [ship for ship in Game().ships if ship != obj]
            Game().bullets = [bullet for bullet in Game().bullets if bullet != obj]
            del obj
        except KeyError as e:
            pass

        return {}


class ClientFactory(protocol.ClientFactory):
    def __init__(self):
        self.protocol = ClientAMPProtocol

    def clientConnectionLost(self, transport, reason):
        print("Client Connection Lost")
        reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        print("Client Connection Failed")
        reactor.stop()


reactor.connectTCP("localhost", 5001, ClientFactory())

# Start the reactor
reactor.run()