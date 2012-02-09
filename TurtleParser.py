import re
import ast
from TurtleTokenizer import Tokenizer

class Parser(object):
    """Parse turtle code into an AST.

    >>> parser = Parser('''a=2
    ... b=a * 5''')
    >>> ast.dump(ast.Module(body=list(parser.parse())))
    "Module(body=[Assign(targets=[Name(id='a', ctx=Store())], value=Num(n=2)), Assign(targets=[Name(id='b', ctx=Store())], value=BinOp(left=Name(id='a', ctx=Load()), op=Mult(), right=Num(n=5)))])"
    """

    def __init__(self, input="", tokenizer=Tokenizer):
        self.tokenizer = tokenizer(input)

    def update(self, string):
        self.tokenizer.update(string)

    def parse(self):
        return Parser.handle_statements(self.tokenizer.analyze())

    @staticmethod
    def handle_statements(stmt):
        """Parse blocks of statements.

        >>> tree = Parser.handle_loop(Tokenizer.tokenize('''for X=0 to 100 do
        ...     for Y=1 to 10 do
        ...         move(X, Y)
        ...     end
        ... end'''))
        >>> ast.dump(tree)
        "For(target=Name(id='X', ctx=Store()), iter=Call(func=Name(id='range', ctx=Load()), args=[Num(n=0), Num(n=100)]), body=[For(target=Name(id='Y', ctx=Store()), iter=Call(func=Name(id='range', ctx=Load()), args=[Num(n=1), Num(n=10)]), body=[Expr(value=Call(func=Name(id='move', ctx=Load()), args=[Name(id='X', ctx=Load()), Name(id='Y', ctx=Load())]))])])"
        """

        tokens = []
        depth = 0
        for token in stmt:
            if token[0] == 'DO': depth += 1
            elif token[0] == 'END': depth -= 1

            if depth == 0 and token[0] == 'NEWLINE':
                if len(tokens):
                    tree = Parser.handle_statement(tokens)
                    del tokens[:]
                    yield tree
            else:
                tokens.append(token)
        
        if depth != 0:
            raise SyntaxError('wrong block overlapping')
        if len(tokens):
            tree = Parser.handle_statement(tokens)
            yield tree

    @staticmethod
    def handle_statement(stmt):
        n = len(stmt)
        token_type, value = zip(*stmt)
        if token_type[0] == 'IDENTIFIER':
            if n > 2 and token_type[1] == 'EQUAL':
                return Parser.handle_assignment(stmt)
            if n == 1 or n > 2:
                return Parser.handle_call(stmt)
        elif token_type[0] in ('INTEGER', 'OPERATOR'):
            return ast.Expression(Parser.handle_arithmetic(stmt))
        elif token_type[0] == 'FOR' and token_type[-1] == 'END':
            return Parser.handle_loop(stmt)
        raise SyntaxError('unknown statement %i %s' % (n, ' '.join(token_type)))

    @staticmethod
    def handle_loop(stmt):
        """Parse loops for X=0 to 100 do... end

        >>> tree = Parser.handle_loop(Tokenizer.tokenize('for blah=0 to 2 do test end'))
        >>> ast.dump(tree)
        "For(target=Name(id='blah', ctx=Store()), iter=Call(func=Name(id='range', ctx=Load()), args=[Num(n=0), Num(n=2)]), body=[Expr(value=Call(func=Name(id='test', ctx=Load()), args=[]))])"

        >>> tree = Parser.handle_loop(Tokenizer.tokenize('for blah to 2 do test end'))
        Traceback (most recent call last):
            ...
        SyntaxError: invalid loop format
        """

        token_type, value = zip(*stmt)
        to = token_type.index('TO')
        do = token_type.index('DO')
        if token_type[1] != 'IDENTIFIER' or token_type[2] != 'EQUAL' or to > do:
            raise SyntaxError('invalid loop format')

        start = Parser.handle_arithmetic(stmt[3:to])
        end = Parser.handle_arithmetic(stmt[to + 1:do])
        body = list(Parser.handle_statements(stmt[do + 1:-1]))
        return ast.For(target=ast.Name(id=value[1], ctx=ast.Store()), iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[start, end]), body=body)


    @staticmethod
    def handle_call(stmt):
        """Parse function calls and their arguments.

        >>> tree = Parser.handle_call(Tokenizer.tokenize('test'))
        >>> ast.dump(tree)
        "Expr(value=Call(func=Name(id='test', ctx=Load()), args=[]))"

        >>> tree = Parser.handle_call(Tokenizer.tokenize('testa(5, 2, 2+4)'))
        >>> ast.dump(tree)
        "Expr(value=Call(func=Name(id='testa', ctx=Load()), args=[Num(n=5), Num(n=2), BinOp(left=Num(n=2), op=Add(), right=Num(n=4))]))"
        """

        n = len(stmt)
        args = []
        if n > 2 and stmt[1][0] == 'OPEN' and stmt[-1][0] == 'CLOSE':
            if n > 3:
                arg = []
                for item in stmt[2:-1]:
                    if item[0] == 'SEPARATOR':
                        if len(arg) == 0: raise SyntaxError('Separator missing')
                        args.append(Parser.handle_arithmetic(arg))
                        del arg[:]
                    else:
                        arg.append(item)
                if len(arg) == 0: raise SyntaxError('Separator missing')
                args.append(Parser.handle_arithmetic(arg))
        return ast.Expr(ast.Call(func=ast.Name(id=stmt[0][1], ctx=ast.Load()), args=args))

    @staticmethod
    def handle_arithmetic(stmt):
        """Parse arithmetic operations and variables loading.

        >>> tree = Parser.handle_arithmetic(Tokenizer.tokenize('2+4*b'))
        >>> ast.dump(tree)
        "BinOp(left=Num(n=2), op=Add(), right=BinOp(left=Num(n=4), op=Mult(), right=Name(id='b', ctx=Load())))"
        
        Parenthesis are not supported:

        >>> tree = Parser.handle_arithmetic(Tokenizer.tokenize('(6-7)'))
        Traceback (most recent call last):
        ...
        SyntaxError: must be an arithmetic operation or an integer
        """

        token_type, value = zip(*stmt)
        for item in token_type:
            if item not in ('INTEGER', 'OPERATOR', 'IDENTIFIER'):
                raise SyntaxError('must be an arithmetic operation or an integer')
        return ast.parse(''.join(value), mode='eval').body

    @staticmethod
    def handle_assignment(stmt):
        """Parse variable assignments.

        >>> tree = Parser.handle_assignment(Tokenizer.tokenize('a = 2'))
        >>> ast.dump(tree)
        "Assign(targets=[Name(id='a', ctx=Store())], value=Num(n=2))"

        >>> tree = Parser.handle_assignment(Tokenizer.tokenize('a = b'))
        >>> ast.dump(tree)
        "Assign(targets=[Name(id='a', ctx=Store())], value=Name(id='b', ctx=Load()))"
        """

        identifier = ast.Name(id=stmt[0][1], ctx=ast.Store())
        value = Parser.handle_arithmetic(stmt[2:])
        return ast.Assign(targets=[identifier], value=value)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
