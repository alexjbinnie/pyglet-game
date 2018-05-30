from twisted.protocols import amp

class PacketGameSize(amp.Command):
    requiresAnswer = False
    arguments = [(b'width', amp.Integer()),
                 (b'height', amp.Integer())]
    response = []


class PacketPlanet(amp.Command):
    requiresAnswer = False
    arguments = [ (b'id', amp.Integer()),
                (b'radius', amp.Integer()),
                 (b'position_x', amp.Float()),
                 (b'position_y', amp.Float()),
                 (b'mass', amp.Float()),
                 (b'image', amp.Unicode())]
    response = []


class PacketShip(amp.Command):
    requiresAnswer = False
    arguments = [(b'id', amp.Integer()),
                (b'color_r', amp.Integer()),
                 (b'color_g', amp.Integer()),
                 (b'color_b', amp.Integer()),
                 (b'position_x', amp.Float()),
                 (b'position_y', amp.Float()),
                 (b'velocity_x', amp.Float()),
                 (b'velocity_y', amp.Float()),
                 (b'rotation', amp.Float()),
                 (b'angvelocity', amp.Float()),
                 (b'isme', amp.Boolean())
                 ]
    response = []


class PacketShipInput(amp.Command):
    requiresAnswer = False
    arguments = [
                (b'id', amp.Integer()),
                (b'up', amp.Boolean()),
                 (b'down', amp.Boolean()),
                 (b'left', amp.Boolean()),
                 (b'right', amp.Boolean()),
                 (b'fire', amp.Boolean())
                 ]
    response = []


class PacketShipUpdate(amp.Command):
    requiresAnswer = False
    arguments = [
                (b'id', amp.Integer()),
                (b'position_x', amp.Float()),
                 (b'position_y', amp.Float()),
                 (b'velocity_x', amp.Float()),
                 (b'velocity_y', amp.Float()),
                 (b'rotation', amp.Float()),
                 (b'angvelocity', amp.Float()),
                 (b'health', amp.Float())
                 ]
    response = []


class PacketShipFire(amp.Command):
    requiresAnswer = False
    arguments = [
        (b'id', amp.Integer())
    ]
    response = []


class PacketBulletNew(amp.Command):
    requiresAnswer = False
    arguments = [(b'id', amp.Integer()),
                (b'color_r', amp.Integer()),
                 (b'color_g', amp.Integer()),
                 (b'color_b', amp.Integer()),
                 (b'position_x', amp.Float()),
                 (b'position_y', amp.Float()),
                 (b'velocity_x', amp.Float()),
                 (b'velocity_y', amp.Float())
                 ]
    response = []

class PacketBulletUpdate(amp.Command):
    requiresAnswer = False
    arguments = [
                (b'id', amp.Integer()),
                (b'position_x', amp.Float()),
                 (b'position_y', amp.Float()),
                 (b'velocity_x', amp.Float()),
                 (b'velocity_y', amp.Float()),
                 (b'active', amp.Boolean())
                 ]
    response = []

class PacketDelete(amp.Command):
    requiresAnswer = False
    arguments = [
                (b'id', amp.Integer())
                 ]
    response = []