# from Template.engine import Engine
from Template.context import Context
from Template.engine import DefaultEngine
from Template.template import Template

engine = DefaultEngine()
# engine = Engine(libraries=[builtin],string_if_invalid='Invalid method',templates_path='/home/aniket/Downloads')
t = Template(engine.load_template('test'), engine, None)
print(t.render(Context(engine, {'title': 'Tits'}, 'root')))
