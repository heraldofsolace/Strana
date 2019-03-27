# from Template.engine import Engine
from datetime import datetime

from Strana.context import Context
from Strana.library import Library
from Strana.template import Template

r = Library()


@r.basic_action(name='time', need_context=False)
def x(node_id):
    return str(datetime.now())


@r.loop_action(name='if', need_context=True)
def fun(node_id, body, context, cond):
    if cond:
        return ''.join([str(node.render(context)) for node in body])
    else:
        return ''


source = """
    {> if True <}
        Hi
    {> /if <}
"""
# engine = Engine(libraries=[builtin],string_if_invalid='Invalid method',templates_path='/home/aniket/Downloads')
t = Template(source, None, [r])
print(t.render(Context(None, {'title': 'Tits', 'l': [1, 2, 3]}, 'root')))
