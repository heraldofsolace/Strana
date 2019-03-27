from Strana.context import Context
from Strana.library import Library
from Strana.template import Template

source = """<html>
    <head><title> {= title>>up =}</title></head>
    <body>
    {> do 3 times <}
        <p> I am a{= quality>>up=>0 =}boy at {= iteration =} </p>
    {> /do <}
    </body>
    </html>

"""

# print(source)
r = Library()


@r.register_modifier(name='up')
def up(value, first=False):
    return value.title() if first else value.upper()


@r.pattern_action(name='do', pattern='do <> times', need_context=True, need_body=True)
def do_tag(node_id, body, context, time):
    result = ''
    try:
        time = int(time)
        for i in range(time):
            c = context.push_temporary({'iteration': i}, node_id)

            result += ' '.join([str(node.render(c)) for node in body])

    except ValueError:
        pass
    #
    return result


t = Template(source, None, [r])
print(t.render(Context(None, {'title': 'Test', 'quality': 'good'}, 'root')))
