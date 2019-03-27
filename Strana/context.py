from collections import OrderedDict
from copy import deepcopy


class ContextStack:
    def __init__(self):

        self.stack = OrderedDict({'builtin': {'True': True, 'False': False, 'None': None}})
        self.node_stack = []

    def push(self, context, node_id):
        if node_id in self.stack:
            self.stack[node_id].update(context)
        else:
            self.stack[node_id] = context
            self.node_stack.append(node_id)

    def pop_node(self, node_id):
        self.node_stack.remove(node_id)
        del self.stack[node_id]

    def pop(self):
        del self.stack[self.node_stack[-1]]
        self.node_stack.pop()

    def __getitem__(self, item):
        result = None
        for node, ctx in reversed(self.stack.items()):

            try:
                result = ctx[item]
                return result
            except KeyError:
                pass
        if result is None:
            raise KeyError

    def __setitem__(self, key, value):
        self.stack[self.node_stack[-1]][key] = value

    def __str__(self):
        return str(self.stack)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.stack[self.node_stack[-1]]
        self.node_stack.pop()


class Context:
    def __init__(self, engine, context, node_id):
        self.engine = engine
        self.context = ContextStack()
        if not isinstance(context, dict):
            raise Exception  # TODO:not a dict
        self.context.push(context, node_id)
        self.node_id = node_id

    def push_temporary(self, ctx, node_id):
        if not isinstance(ctx, dict):
            raise Exception  # TODO:Not a dict
        temp_context = deepcopy(self)
        temp_context.node_id = node_id
        temp_context.context.push(ctx, node_id)

        return temp_context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop_last()

    def push_permanent(self, ctx, node_id):
        self.context.push(ctx, node_id)
        self.node_id = node_id

    def __setitem__(self, key, value):

        self.context[key] = value

    def __getitem__(self, item):
        result = None
        try:
            result = self.context[item]
            return result
        except KeyError:
            raise

    def pop_last(self):
        self.context.pop()

    def __repr__(self):
        return 'Context bound to node {}: {}'.format(self.node_id, str(self.context))
