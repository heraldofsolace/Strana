from PEng.library import Library
from PEng.template import ModifierExpression
from PEng.template import Parser

r = Library()


@r.register_modifier(name='test')
def x(val):
    return val + 2


token = 'var>>test'
p = Parser('', [r])
fe = ModifierExpression(token, p, 1)
print(fe.var)
