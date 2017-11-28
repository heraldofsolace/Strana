import uuid


class Node:
    def __init__(self):
        self.id = uuid.uuid4()

    def render(self, context):
        pass

    def __iter__(self):
        yield self


class TextNode(Node):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def render(self, context):
        return self.text

    def __repr__(self):
        return '<{} - {}...>'.format(self.__class__.__name__, self.text[:20])


class VariableNode(Node):
    def __init__(self, modifier_expression):
        super().__init__()
        self.modifier_expression = modifier_expression

    def render(self, context):
        return self.modifier_expression.resolve(context)

    def __repr__(self):
        return '<{}:{}>'.format(self.__class__.__name__, self.modifier_expression)


class HelperNode(Node):
    def __init__(self, func, need_context, args, kwargs):
        super().__init__()
        self.func = func
        self.need_context = need_context
        self.args = args
        self.kwargs = kwargs

    def get_args(self, context):
        resolved_args = [var.resolve(context) for var in self.args]
        if self.need_context:
            resolved_args = [context] + resolved_args
        resolved_kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}
        return resolved_args, resolved_kwargs


class BasicNode(HelperNode):
    def __init__(self, func, need_context, args, kwargs, target):
        super().__init__(func, need_context, args, kwargs)
        self.target = target

    def render(self, context):
        resolved_args, resolved_kwargs = self.get_args(context)
        output = self.func(self.id, *resolved_args, **resolved_kwargs)
        if self.target is not None:
            context.push_permanent({self.target: output}, self.id)
            return ''
        return output


class LoopNode(HelperNode):
    def __init__(self, func, need_context, body, args, kwargs):
        super().__init__(func, need_context, args, kwargs)
        self.body = body

    def render(self, context):
        resolved_args, resolved_kwargs = self.get_args(context)
        output = self.func(self.id, self.body, *resolved_args, **resolved_kwargs)
        return output
