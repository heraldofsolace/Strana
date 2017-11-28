from PEng.context import Context

c = Context(None, {'Test': {'X': 2}}, 'root')
c.context.push({'Test2': 'x'}, 'ry')
c.context.push({'Test2': 'y'}, 'zl')
c.context['Test3'] = 'D'
with c.push_temporary({'Testing': 1}, 'try') as k:
    print(k)

# c.push_permanent({'Lol':1},'dd')
print(c)
