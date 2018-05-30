import math
import numpy as np

class Body:

    def __init__(self, position=np.array([0.0, 0.0]), velocity=np.array([0.0, 0.0]), rotation=0.0, drag=0.0, angvelocity=0.0, angdrag = 0.0, **kwargs):
        self._position = np.array(position)
        self._velocity = np.array(velocity)
        self._rotation = rotation
        self._drag = drag
        self._angvelocity = angvelocity
        self._angdrag = angdrag

    def update(self, dt):
        self._position += dt * self._velocity
        self._velocity *= (1.0 - dt * self._drag)
        self._rotation += dt * self._angvelocity
        self._angvelocity *= (1.0 - dt * self._angdrag)

    def forward(self):
        return np.array([math.sin(math.radians(self._rotation)), math.cos(math.radians(self._rotation))])

