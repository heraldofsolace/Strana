from Strana.library import Library
from Strana.template import ModifierExpression
from Strana.template import Parser

r = Library()


@r.register_modifier(name='test')
def x(val):
    return val + 2


token = 'var>>test'
p = Parser('', [r])
fe = ModifierExpression(token, p, 1)
print(fe.var)
