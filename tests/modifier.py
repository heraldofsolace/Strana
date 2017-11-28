from Template.library import Library
from Template.template import ModifierExpression
from Template.template import Parser

r = Library()


@r.register_modifier(name='test')
def x(val):
    return val + 2


token = 'var>>test'
p = Parser('', [r])
fe = ModifierExpression(token, p, 1)
print(fe.var)
