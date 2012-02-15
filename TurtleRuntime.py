from math import pi, sin, cos, radians
from operator import add

class Vector(tuple):

    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def __add__(self, right):
        return Vector(*map(add, self, right))

    def __mul__(self, other):
        if isinstance(other, int):
            return Vector(*map(lambda x: other * x, self))
        raise NotImplemented

    def rotate(self, angle):
        "Only true for 2 dimensions vector"
        if len(self) != 2:
            raise NotImplemented
        perp = Vector(- self[1], self[0])
        angle = radians(angle)
        c, s = cos(angle), sin(angle)
        return Vector(self[0] * c + perp[0] * s,
                      self[1] * c + perp[1] * s)


class Runtime(object):
    """Turtle runtime implementation"""

    def __init__(self, dypl):
        self._dypl = dypl
        self.put(0, 0)
        self.pen_down()

    def _rotate(self, angle):
        self._orientation = self._orientation.rotate(angle)

    def _draw_line(self, pos1, pos2):
        issteep = abs(pos2[1] - pos1[1]) > abs(pos2[0] - pos1[0])
        if issteep:
            pos1 = Vector(pos1[1], pos1[0])
            pos2 = Vector(pos2[1], pos2[0])
        if pos1[0] > pos2[0]:
            pos1, pos2 = pos2, pos1
        deltax = pos2[0] - pos1[0]
        deltay = abs(pos2[1] - pos1[1])
        error = int(deltax / 2)
        y = pos1[1]
        ystep = None
        if pos1[1] < pos2[1]:
            ystep = 1
        else:
            ystep = -1
        for x in self.range(pos1[0], pos2[0]):
            if issteep:
                self._dypl.setPixel(y, x)
            else:
                self._dypl.setPixel(x, y)
            error -= deltay
            if error < 0:
                y += ystep
                error += deltax

    def turn_cw(self, angle):
        self._rotate(- angle)

    def turn_ccw(self, angle):
        self._rotate(angle)

    def pen_down(self):
        self._on = True

    def pen_up(self):
        self._on = False

    def put(self, x, y, angle=None):
        self._position = Vector(x, y)
        self._orientation = Vector(0, -1)
        if angle is not None:
            self._rotate(angle)

    def move(self, steps, angle=None):
        if angle is not None:
            self._rotate(angle)
        end = self._position + self._orientation * steps
        if self._on:
            self._draw_line(Vector(*map(int, self._position)),
                            Vector(*map(int, end)))
        self._position = end

    def move_forward(self):
        self.move(1)

    def move_backward(self):
        self.move(-1)

    def range(self, a, b):
        #pythonify the loops
        return range(a, b + 1)
