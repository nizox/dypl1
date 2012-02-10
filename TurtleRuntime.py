class Runtime(object):
    """Turtle runtime implementation"""

    def __init__(self, dypl):
        self.dypl = dypl

    def test(self, x, y):
        self.dypl.setPixel(x, y)

    def pen_down(self):
        print('pen down')

    def pen_up(self):
        print('pen up')

    def range(self, a, b):
        #pythonify the loops
        return range(a, b + 1)
