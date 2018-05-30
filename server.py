from twisted.internet import reactor, protocol
from twisted.protocols import basic
import time

from source.game import *
from source.syncedobject import *

Game().Client = False
Game().Server = True

Game().width = 1300
Game().height = 700

Game().generate()

Game().keys = {}



from twisted.protocols import amp

from source.packets import *

def t():
    return "["+ time.strftime("%H:%M:%S") +"] "

class EchoProtocol(amp.AMP):
    name = "Unnamed"
    def connectionMade(self):
        #self.sendLine(b"Welcome to the server")
        self.factory.clients.append(self)
        self.callRemote(PacketGameSize, width=Game().width, height=Game().height)
        print(t() + "+ Connection from: "+ self.transport.getPeer().host)
        for planet in Game().planets:
            planet.update_connected(self)
        for ship in Game().ships:
            ship.update_connected(self)
        for bullet in Game().bullets:
            bullet.update_connected(self)
        # Spawn Ship
        player = Ship(color=(random.randrange(100, 255), random.randrange(100, 255), random.randrange(100, 255)))
        player._client = self
        Game().ships.append(player)
        player.respawn(Game().random_spawn())
        player.update_connected(self)
        player.set_input(pyglet.window.key.UP, pyglet.window.key.LEFT, pyglet.window.key.RIGHT, pyglet.window.key.DOWN, pyglet.window.key.SPACE)
        # New syncedobjects automatically synced to all clients

    def connectionLost(self, reason):
        playership = None
        playershipindex = 0
        i = 0
        for ship in Game().ships:
            if ship._client == self:
                playership = ship
                playershipindex = i + 0
            i += 1

        del Game().ships[playershipindex]
        del SyncedObject.objects[playership.id]

        self.sendMsg("- %s left." % self.name)
        print(t() + "- Connection lost: "+ self.name)
        self.factory.clients.remove(self)

    @PacketShipInput.responder
    def packetshipinput(self, id=None, up=False, left=False, right=False, down=False, fire=False):
        #print("Packet Ship Input. ID: " + str(id))
        ship = SyncedObject.objects[id]
        ship._key_up = up
        ship._key_down = down
        ship._key_left = left
        ship._key_right = right
        ship._key_fire = fire
        return {}

    @PacketShipFire.responder
    def packetshipfire(self, id=None):
        # print("Packet Ship Input. ID: " + str(id))
        ship = SyncedObject.objects[id]
        ship.fire()
        return {}

    def sendMsg(self, message):
        pass
 #       for client in self.factory.clients:
#            client.sendLine(bytes(t() + message, "UTF-8"))

from twisted.internet import task

class EchoServerFactory(protocol.ServerFactory):
    protocol = EchoProtocol
    clients = []

    def __init__(self):
        self.updateloop = task.LoopingCall(self.update)
        self.updateloop.start(1/60.0)
        self.syncloop = task.LoopingCall(self.sync)
        self.syncloop.start(1 / 30.0)

    def sync(self):
        for client in self.clients:
            for ship in Game().ships:
                ship.update_network(client)
            for bullet in Game().bullets:
                bullet.update_network(client)
            for id in SyncedObject.destroyed_ids:
                client.callRemote(PacketDelete, id=id);
            SyncedObject.destroyed_ids = []
        for ship in Game().ships:
            ship._dirty_creation = False
        for bullet in Game().bullets:
            bullet._dirty_creation = False


    def update(self):
        Game().dt = 1/60.0
        Game().update(1/60.0)

if __name__ == "__main__":
    reactor.listenTCP(5001, EchoServerFactory())
    reactor.run()