import functools
import re
from inspect import getfullargspec

from Strana.node import BasicNode, LoopNode
from Strana.template import parse_args


class Library:
    def __init__(self):
        self.actions = {}
        self.modifiers = {}

    def register_action(self, name=None, compiled_func=None, is_loop=False):
        end = None
        if name is None and is_loop:
            raise Exception  # TODO:Is a loop but has no name
        if name is not None and is_loop:
            end = '/' + name
        if name is None and compiled_func is None:
            return self.action_func
        elif name is not None and compiled_func is None:
            if callable(name):
                return self.action_func(name, end)
            else:
                def decorate(func):
                    return self.register_action(func, name, is_loop)

                return decorate
        elif name is not None and compiled_func is not None:
            self.actions[name] = compiled_func
            return compiled_func
        else:
            raise ValueError('Unsupported arguments')

    def action_func(self, fun, end):

        setattr(fun, 'end', end)
        self.actions[getattr(fun, '_decorated_function', fun).__name__] = fun
        return fun

    def loop_action(self, func=None, need_context=False, name=None, node=None):
        def dec(func):
            params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(func)
            function_name = (name or getattr(func, '_decorated_function', func).__name__)

            @functools.wraps(func)
            def compile_func(parser, token, lineno):

                bits = token.split()[1:]
                # bits = []
                # splits = split(token)
                # for bit in splits:
                #     bits.append(bit)
                # bits = bits[3:-1]

                end = None

                if params[1] == 'body':
                    end = '/' + function_name
                if len(bits) >= 2 and bits[-2] == 'as':
                    raise Exception  # TODO:Can't have as
                args, kwargs = parse_args(lineno,
                                          parser, bits, params, varargs, varkw, defaults,
                                          kwonly, kwonly_defaults, need_context, function_name, True
                                          )
                body = parser.parse((end,))
                parser.skip_past(end)
                if node is None:
                    return LoopNode(func, need_context, body, args, kwargs)
                return node(func, need_context, body, args, kwargs)

            self.register_action(function_name, compile_func, True)
            return func

        if func is None:
            return dec
        elif callable(func):
            return dec(func)
        else:
            raise ValueError('Unsupported arguments')

    def pattern_action(self, func=None, need_context=False, name=None, pattern=None, need_body=False, node=None):
        if pattern is None:
            raise Exception  # TODO:No pattern provided to pattern tag

        def dec(func):
            args_match_re = re.compile('<.*?>')
            args = []
            a = args_match_re.finditer(pattern)
            for i in a:
                args.append(i)

            pat = re.sub('<>', '(\w+)', pattern)

            setattr(func, 'pattern', pat)
            if need_body:
                return self.loop_action(func, need_context, name, node)
            else:
                return self.basic_action(func, need_context, name, node)

        if func is None:
            return dec
        elif callable(func):
            return dec(func)
        else:
            raise ValueError

    def basic_action(self, func=None, need_context=False, name=None, node=None):
        def dec(func):
            params, varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(func)
            function_name = (name or getattr(func, '_decorated_function', func).__name__)

            @functools.wraps(func)
            def compile_func(parser, token, lineno):
                bits = token.split()[1:]
                target_var = None

                if len(bits) >= 2 and bits[-2] == 'as':
                    target_var = bits[-1]
                    bits = bits[:-2]
                args, kwargs = parse_args(lineno,
                                          parser, bits, params, varargs, varkw, defaults,
                                          kwonly, kwonly_defaults, need_context, function_name
                                          )
                if node is None:
                    return BasicNode(func, need_context, args, kwargs, target_var)
                return node(func, need_context, args, kwargs, target_var)

            self.register_action(function_name, compile_func, False)
            return func

        if func is None:
            # @register.simple_tag(...)
            return dec
        elif callable(func):
            # @register.simple_tag
            return dec(func)
        else:
            raise ValueError("Invalid arguments provided to simple_tag")

    def register_modifier(self, name=None, modifier_func=None, **flags):
        if name is None and modifier_func is None:
            def dec(func):
                return self.modifier_function(func, **flags)

            return dec
        elif name is not None and modifier_func is None:
            if callable(name):
                return self.modifier_function(name, **flags)
            else:
                def dec(func):
                    return self.register_modifier(name, func, **flags)

                return dec
        elif name is not None and modifier_func is not None:
            self.modifiers[name] = modifier_func
            modifier_func._modifier_name = name
            return modifier_func
        else:
            raise ValueError  # TODO:Unsupported args to modifier

    def modifier_function(self, func, **flags):
        name = getattr(func, "_decorated_function", func).__name__
        return self.register_modifier(name, func, **flags)
