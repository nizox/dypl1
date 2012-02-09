import re

class Tokenizer(object):
    """Tokenizer splits the code into known tokens.

    Example from the subject:

    >>> t=Tokenizer('''put(100, 100, 90)
    ... move(10, 45)
    ... for X=0 to 4 do
    ...    move(50, 90)
    ... end''')
    >>> [ w[0] for w in t.analyze() ]
    ['IDENTIFIER', 'OPEN', 'INTEGER', 'SEPARATOR', 'INTEGER', 'SEPARATOR', 'INTEGER', 'CLOSE', 'NEWLINE', 'IDENTIFIER', 'OPEN', 'INTEGER', 'SEPARATOR', 'INTEGER', 'CLOSE', 'NEWLINE', 'FOR', 'IDENTIFIER', 'EQUAL', 'INTEGER', 'TO', 'INTEGER', 'DO', 'NEWLINE', 'IDENTIFIER', 'OPEN', 'INTEGER', 'SEPARATOR', 'INTEGER', 'CLOSE', 'NEWLINE', 'END']

    Arithmetic operations are also tokenized:

    >>> t.update('a = 5 + 6 - 12 * 5')
    >>> [ w[0] for w in t.analyze() ]
    ['IDENTIFIER', 'EQUAL', 'INTEGER', 'OPERATOR', 'INTEGER', 'OPERATOR', 'INTEGER', 'OPERATOR', 'INTEGER']

    Input can be updated at any time.
    """

    keywords = [ 'FOR', 'TO', 'DO', 'END' ]
    rules = [ ('IDENTIFIER', r'[a-zA-Z_]\w*'),
              ('SEPARATOR', r','),
              ('OPEN', r'\('),
              ('CLOSE', r'\)'),
              ('INTEGER', r'\d+'),
              ('EQUAL', r'='),
              ('OPERATOR', r'[+\-*]'),
              ('WHITESPACE', r'[ \t]+'),
              ('NEWLINE', r'\n') ]

    def __init__(self, input=""):
        regex = '|'.join([ '(?P<%s>%s)' % rule for rule in self.rules ])
        self.prog = re.compile(regex)
        self.input = input
        self.position = 0

    def update(self, string):
        self.input += string

    def analyze(self):
        while self.position < len(self.input):
            word = self.prog.match(self.input, self.position)
            if not word:
                raise RuntimeError('invalid input')
            word_type = word.lastgroup
            word_value = word.group(word_type)
            if word_type == 'IDENTIFIER' and word_value.upper() in self.keywords:
                word_type = word_value.upper()
            self.position = word.end()
            if word_type != 'WHITESPACE':
                yield (word_type, word_value)

    @staticmethod
    def tokenize(input):
        return list(Tokenizer(input).analyze())

if __name__ == "__main__":
    import doctest
    doctest.testmod()
