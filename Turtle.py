import ast
import DYPL
from JythonTranslater import Jtrans
from TurtleParser import Parser
from TurtleRuntime import Runtime

class RuntimeTransformer(ast.NodeTransformer):
    """Sandbox the code inside the Runtime namespace."""

    def __init__(self, instance_name, instance_type=Runtime.__class__):
        self.name = ast.Name(id=instance_name, ctx=ast.Load())
        self.type = ast.Name(id=instance_type, ctx=ast.Load())

    def visit_Call(self, node):
        #jython!@#$% ast.Attribute != org.python.antlr.ast.Attribute
        from org.python.antlr.ast import Attribute

        newnode = ast.Call(func=Attribute(value=self.type,
                                          attr=node.func.id,
                                          ctx=node.func.ctx),
                           args=[ self.name ] + node.args)
        return ast.copy_location(newnode, node)


class Turtle(Jtrans):
    """Bridge between java things and python world"""

    var = '_turtle'

    def __init__(self, input="", parser=Parser, runtime=Runtime):
        self.dypl = None
        self.runtime = None
        self.runtime_type = runtime
        self.parser = parser(input)
        self.transformer = RuntimeTransformer(self.var, runtime.__name__)

    def actionPerformed(self, event):
        if not self.dypl:
            raise RuntimeError('DYPL instance not set')
        self.runCode(self.dypl.getCode())

    def setDYPL(self, instance):
        self.runtime = self.runtime_type(instance)
        self.dypl = instance

    def runCode(self, code):
        self.parser.reset(code)
        tree = ast.Module(list(self.parser.parse()))
        tree = ast.fix_missing_locations(tree)
        tree = self.transformer.visit(tree)

        bc = compile(tree, '<string>', 'exec')
        exec(bc, { self.var: self.runtime,
                   self.runtime_type.__name__: self.runtime_type,
                   '__builtins__': None })

if __name__ == "__main__":
    DYPL(Turtle())
