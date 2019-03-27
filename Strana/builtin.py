from Strana.library import Library

builtin = Library()


@builtin.pattern_action(name='do', pattern='do <> times', need_body=True, need_context=True)
def do_action(node_id, body, context, times):
    result = ''
    try:
        times = int(times)
        for i in range(times):
            c = context.push_temporary({'iteration': i}, node_id)
            result += ''.join([str(node.render(c)) for node in body])
    except ValueError:
        pass
    return result

@builtin.pattern_action(name='for',pattern='for <> in <>',need_body=True,need_context=True)
def for_action(node_id,body,context,i,l):
    result = ''
    li = context[l]
    for x in li:
        c = context.push_temporary({i:x},node_id)
        result += ''.join([str(node.render(c)) for node in body])
    return result
