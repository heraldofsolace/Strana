from Strana.context import Context
from Strana.template import Lexer, Parser

l = Lexer('{= var =} \n Lol let\'s go')
li = l.tokenize()
print(li)
parser = Parser(li)
# print(getfullargspec(x))
for node in parser.parse():
    print(node.render(Context(None, {'lil': [1, 2, 3], 'var': "a"}, 'lol')))
