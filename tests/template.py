from Template.context import Context
from Template.engine import Engine
from Template.library import Library
from Template.template import Template

r = Library()


@r.basic_action(name='x')
def kx():
    return 'p'


# print([r])
e = Engine([r], 'Lol')
t = Template('{= f.2 =}\n{> x <}', libraries=[r], engine=e)
print(t.render(Context(e, {'f': [1, 2, 3]}, 'root')))
