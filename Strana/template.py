import re
from inspect import getcallargs, getfullargspec

from Strana.engine import DefaultEngine
from Strana.exception import *
from Strana.node import TextNode, VariableNode

TOKEN_TYPE_TEXT = 0
TOKEN_TYPE_VAR = 1
TOKEN_TYPE_BLOCK = 2
TOKEN_TYPE_COMMENT = 3
TOKEN_TYPE_SPECIAL = 4  # reserved for future

TOKEN_MAP = {
    TOKEN_TYPE_TEXT: 'Text',
    TOKEN_TYPE_VAR: 'Variable',
    TOKEN_TYPE_BLOCK: 'Block',
    TOKEN_TYPE_COMMENT: 'Comment',
    TOKEN_TYPE_SPECIAL: 'Special'
}

VARIABLE_ATTRIBUTE_SEPERATOR = '.'
INDEX_ACCESS = ':'
BLOCK_TAG_START = '{>'
BLOCK_TAG_END = '<}'
COMMENT_TAG_START = '{#'
COMMENT_TAG_END = '#}'
VARIABLE_TAG_START = '{='
VARIABLE_TAG_END = '=}'
MODIFIER = '>>'
MODIFIER_ARGUMENT_SEPARATOR = '=>'
tag_expr_re = re.compile('({}.*?{}|{}.*?{}|{}.*?{})'.format(
    re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END),
    re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END),
    re.escape(COMMENT_TAG_START), re.escape(COMMENT_TAG_END)
))

split_re = re.compile(r"""
    ((?:
        [^\s'"]*
        (?:
            (?:"(?:[^"\\]|\\.)*" | '(?:[^'\\]|\\.)*')
            [^\s'"]*
        )+
    ) | \S+)
""", re.VERBOSE)


def split(text):
    for bit in split_re.finditer(str(text)):
        yield bit.group(0)


class Template:
    def __init__(self, source, engine=None, libraries=None):
        if engine is None:
            self.engine = DefaultEngine()
        else:
            self.engine = engine
        if libraries is None:

            self.libraries = self.engine.libraries
        else:
            self.libraries = libraries
        self.source = source
        self.node_list = self.compile_nodes()

    def render(self, context):
        result = ''
        for node in self.node_list:
            result += str(node.render(context))
            result += ''
        return result

    def compile_nodes(self):
        lexer = Lexer(self.source)
        li = lexer.tokenize()
        parser = Parser(li, libraries=self.libraries)
        try:
            return parser.parse()
        except Exception as e:
            raise


class Parser:
    def __init__(self, tokens, libraries=None):
        self.tokens = tokens
        self.modifiers = {}
        if libraries is None:
            self.libraries = {}
        else:
            self.libraries = libraries

        self.actions = {}
        self.stack = []
        for lib in self.libraries:
            self.add_library(lib)

    def parse(self, stop=None):
        node_list = []
        if stop is None:
            stop = []

        while self.tokens:
            token = self.next()
            if token.type == TOKEN_TYPE_TEXT:
                self.extend_list(node_list, TextNode(token.contents), token)
            elif token.type == TOKEN_TYPE_VAR:
                if not token.contents:
                    raise EmptyVariableTagException(token.lineno)
                try:
                    var_node = VariableNode(self.compile_modifier(token.contents, token.lineno))
                except (NoSuchVariableException, CharacterParseException, NoAttributeToAccessException) as e:
                    ex = NoSuchVariableException(e.var_name, e.lineno)
                    raise ex
                self.extend_list(node_list, var_node, token)
            elif token.type == TOKEN_TYPE_BLOCK:
                try:
                    command = token.contents.split()[0]
                except IndexError:
                    raise EmptyBlockTagException('Empty block tag', token.lineno)
                if command in stop:
                    self.prepend_token(token)
                    return node_list
                self.stack.append((command, token))
                try:

                    f = self.actions[command]

                except KeyError:
                    raise NoSuchActionException(token.lineno)
                try:
                    pattern = getattr(f, 'pattern', None)
                    if pattern is not None:
                        m = re.search(pattern, token.contents)
                        if m.string != token.contents:
                            raise WrongPatternForActionException(pattern, token.contents, token.lineno)
                        c = command + ' '
                        for i in m.groups():
                            c += ('\"' + i + '\"' + ' ')

                        token.contents = c
                    result = f(self, token, token.lineno)
                except Exception as e:
                    raise e
                self.extend_list(node_list, result, token)
                self.stack.pop()
        if stop:
            raise UnclosedBlockTagException('Unclosed Block tag', token.lineno)
        return node_list

    def find_modifier(self, name):
        if name in self.modifiers:
            return self.modifiers[name]
        else:
            raise NoSuchModifierException('Bitch')

    def compile_modifier(self, expr, lineno):
        return ModifierExpression(expr, lineno, self)

    def skip_past(self, endtag):
        while self.tokens:
            token = self.next()
            if token.type == TOKEN_TYPE_BLOCK and token.contents == endtag:
                return
        raise UnclosedBlockTagException('Tag not closed')

    def extend_list(self, nodelist, node, token):
        node.token = token
        nodelist.append(node)

    def next(self):
        return self.tokens.pop(0)

    def prepend_token(self, token):
        self.tokens.insert(0, token)

    def delete_first_token(self):
        del self.tokens[0]

    def add_library(self, lib):
        self.actions.update(lib.actions)
        self.modifiers.update(lib.modifiers)


class Lexer:
    def __init__(self, string):
        self.string = string

    def tokenize(self):
        in_tag = False
        lineno = 1
        result = []
        for bit in tag_expr_re.split(self.string):
            if bit:
                result.append(self.create_token(lineno, bit, in_tag))
            in_tag = not in_tag
            lineno += bit.count('\n')
        return result

    def create_token(self, lineno, token_string, in_tag):
        if in_tag:
            if token_string.startswith(BLOCK_TAG_START):
                block = token_string[2:-2].strip()
                token = Token(TOKEN_TYPE_BLOCK, block, lineno)
            elif token_string.startswith(VARIABLE_TAG_START):
                token = Token(TOKEN_TYPE_VAR, token_string[2:-2].strip(), lineno)
            elif token_string.startswith(COMMENT_TAG_START):
                token = Token(TOKEN_TYPE_COMMENT, token_string[2:-2].strip(), lineno)
        else:
            token = Token(TOKEN_TYPE_TEXT, token_string, lineno)
        return token


class Token:
    def __init__(self, type, contents, lineno):
        self.type = type
        self.contents = contents
        self.lineno = lineno

    def __repr__(self):
        return '<Token - {}: {}... at line {}>'.format(TOKEN_MAP[self.type], self.contents[:20], self.lineno)

    def split(self):
        s = []
        splited = split(self.contents)
        for bit in splited:
            s.append(bit)
        return s


class Variable:
    def __init__(self, var, lineno):
        self.var = var
        self.lookups = None
        self.literal = None
        self.lineno = lineno
        try:
            if '.' in var or 'e' in var.lower():
                self.literal = float(var)
                if var.endswith('.'):
                    raise ValueError
            else:
                self.literal = int(var)
        except ValueError:
            try:
                if var[0] not in "\"'" or var[-1] != var[0]:
                    raise ValueError("Not a string literal: {}".format(var))
                quote = var[0]
                self.literal = var[1:-1].replace(r'\%s' % quote, quote).replace(r'\\', '\\')
            except ValueError:
                self.lookups = tuple(var.split(VARIABLE_ATTRIBUTE_SEPERATOR))

    def _resolve(self, context):
        if self.lookups is not None:
            value = self._lookup(context)
        else:
            value = self.literal
        return value

    def __str__(self):
        return self.var

    def resolve(self, context):
        return self._resolve(context)

    def _lookup(self, context):
        curr = context

        try:
            for var in self.lookups:

                try:

                    curr = curr[var]

                except (TypeError, KeyError, IndexError, AttributeError, ValueError):
                    try:

                        curr = getattr(curr, var)
                    except (TypeError, AttributeError):
                        try:

                            curr = curr[int(var)]

                        except (IndexError, ValueError, TypeError, KeyError):

                            raise NoSuchVariableException(var, self.lineno)
            if callable(curr):
                if getattr(curr, 'call_not_allowed', False):
                    pass
                elif getattr(curr, 'alters_data', False):
                    curr = context.engine.string_if_invalid
                else:
                    try:
                        curr = curr()
                    except TypeError:
                        try:
                            getcallargs(curr)
                        except TypeError:
                            curr = "Invalid method call"
        except Exception as e:
            raise
        return curr


constant_string = r"""
(%(strdq)s|%(strsq)s)
""" % {
    'strdq': r'"[^"\\]*(?:\\.[^"\\]*)*"',  # double-quoted string
    'strsq': r"'[^'\\]*(?:\\.[^'\\]*)*'",  # single-quoted string
}
constant_string = constant_string.replace("\n", "")

modifier_raw_string = r"""
^(?P<constant>%(constant)s)|
^(?P<var>[%(var_chars)s]+|%(num)s)|
 (?:\s*%(modifier_sep)s\s*
     (?P<modifier_name>\w+)
         (?:%(arg_sep)s
             (?:
              (?P<constant_arg>%(constant)s)|
              (?P<var_arg>[%(var_chars)s]+|%(num)s)
             )
         )?
 )""" % {
    'constant': constant_string,
    'num': r'[-+\.]?\d[\d\.e]*',
    'var_chars': r'\w\.',
    'modifier_sep': re.escape(MODIFIER),
    'arg_sep': re.escape(MODIFIER_ARGUMENT_SEPARATOR),
}

modifier_re = re.compile(modifier_raw_string, re.VERBOSE)


class ModifierExpression:
    def __init__(self, token, lineno, parser):
        self.token = token
        self.lineno = lineno
        matches = modifier_re.finditer(token)
        var_obj = None
        modifiers = []
        upto = 0
        for match in matches:
            start = match.start()
            if upto != start:
                raise CharacterParseException(token, 0)
            if var_obj is None:
                var, constant = match.group("var", "constant")

                if constant:
                    try:
                        var_obj = Variable(constant, self.lineno).resolve({})
                    except NoSuchVariableException:
                        var_obj = None
                elif var is None:
                    raise VariableParseException(token, 0)
                else:
                    var_obj = Variable(var, self.lineno)
            else:
                modifier_name = match.group("modifier_name")
                args = []
                constant_arg, var_arg = match.group("constant_arg", "var_arg")
                if constant_arg:
                    args.append((False, Variable(constant_arg, self.lineno).resolve({})))
                elif var_arg:
                    args.append((True, Variable(var_arg, self.lineno)))
                modifier_func = parser.find_modifier(modifier_name)
                self.args_check(modifier_name, modifier_func, args)
                modifiers.append((modifier_func, args))
            upto = match.end()
        if upto != len(token):
            raise VariableParseException(token, self.lineno)

        self.modifiers = modifiers
        self.var = var_obj

    def resolve(self, context, ignore_failures=False):
        if isinstance(self.var, Variable):
            try:
                obj = self.var.resolve(context)
            except NoSuchVariableException:

                if ignore_failures:
                    obj = None
                else:
                    raise
                    string_if_invalid = context.engine.string_if_invalid
                    if string_if_invalid:
                        if '%s' in string_if_invalid:
                            return string_if_invalid % self.var
                        else:
                            return string_if_invalid
                    else:
                        obj = string_if_invalid
        else:
            obj = self.var

        for func, args in self.modifiers:
            arg_vals = []

            for lookup, arg in args:
                if not lookup:
                    arg_vals.append(arg)
                else:
                    arg_vals.append(arg.resolve(context))
            obj = func(obj, *arg_vals)
        return obj

    def args_check(name, func, provided):
        provided = list(provided)
        # First argument, modifier input, is implied.
        plen = len(provided) + 1
        # Check to see if a decorator is providing the real function.
        func = getattr(func, '_decorated_function', func)

        args, _, _, defaults, _, _, _ = getfullargspec(func)
        alen = len(args)
        dlen = len(defaults or [])
        # Not enough OR Too many
        if plen < (alen - dlen) or plen > alen:
            raise Exception  # TODO: Less or too many arguments

        return True

    args_check = staticmethod(args_check)

    def __str__(self):
        return self.token


def parse_args(lineno, parser, bits, params, varargs, varkw, defaults, kwonly, kwonly_defaults,
               need_context, name, is_loop=False):
    if params[0] == 'node_id':
        params = params[1:]
    else:
        raise Exception  # TODO:node_id not taken
    if is_loop:
        if params[0] == 'body':
            params = params[1:]
        else:
            raise Exception  # TODO:Body Not supplied
    if need_context:
        if params[0] == 'context':
            params = params[1:]
        else:
            raise Exception  # Todo:Context not supplied

    args = []
    kwargs = {}
    unhandled_params = list(params)
    unhandled_kwargs = [
        kwarg for kwarg in kwonly
        if not kwonly_defaults or kwarg not in kwonly_defaults
    ]

    for bit in bits:
        # First we try to extract a potential kwarg from the bit
        kwarg = token_kwargs([bit], parser)
        if kwarg:
            # The kwarg was successfully extracted
            param, value = kwarg.popitem()
            if param not in params and param not in unhandled_kwargs and varkw is None:
                # An unexpected keyword argument was supplied
                raise Exception  # TODO:Unexpected argument
            elif param in kwargs:
                # The keyword argument has already been supplied once
                raise Exception  # TODO:Multiple value for keyword
            else:
                # All good, record the keyword argument
                kwargs[str(param)] = value
                if param in unhandled_params:
                    # If using the keyword syntax for a positional arg, then
                    # consume it.
                    unhandled_params.remove(param)
                elif param in unhandled_kwargs:
                    # Same for keyword-only arguments
                    unhandled_kwargs.remove(param)
        else:
            if kwargs:
                raise Exception  # TODO:Positional args after keywords
            else:
                # Record the positional argument
                args.append(parser.compile_modifier(bit, lineno))
                try:
                    # Consume from the list of expected positional arguments
                    unhandled_params.pop(0)
                except IndexError:
                    if varargs is None:
                        raise  # TODO:Too many positional args
    if defaults is not None:
        # Consider the last n params handled, where n is the
        # number of defaults.
        unhandled_params = unhandled_params[:-len(defaults)]

    if unhandled_params or unhandled_kwargs:
        # Some positional arguments were not supplied
        raise Exception
    return args, kwargs


kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")


def token_kwargs(bits, parser):
    if not bits:
        return {}
    match = kwarg_re.match(bits[0])
    kwarg_format = match and match.group(1)
    if not kwarg_format:
        return {}

    kwargs = {}
    while bits:
        if kwarg_format:
            match = kwarg_re.match(bits[0])
            if not match or not match.group(1):
                return kwargs
            key, value = match.groups()
            del bits[:1]
        else:
            if len(bits) < 3 or bits[1] != 'as':
                return kwargs
            key, value = bits[2], bits[0]
            del bits[:3]
        kwargs[key] = parser.compile_modifier(value)
        if bits and not kwarg_format:
            if bits[0] != 'and':
                return kwargs
            del bits[:1]
    return kwargs
