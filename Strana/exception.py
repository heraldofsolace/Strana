class NoSuchVariableException(Exception):
    def __init__(self, var_name, lineno):
        self.var_name = var_name
        self.lineno = lineno
        self.msg = "No such variable found: {} at line {}".format(var_name, lineno)

    def __str__(self):
        return self.msg


class EmptyVariableTagException(Exception):
    def __init__(self, lineno):
        self.lineno = lineno
        self.msg = 'Empty variable tag at line {}'.format(lineno)

    def __str__(self):
        return self.msg


class NoAttributeToAccessException(Exception):
    def __init__(self, var_name, attribute_name, lineno):
        self.lineno = lineno
        self.msg = "Variable {} has no attribute {} at line {}".format(var_name, attribute_name, lineno)

    def __str__(self):
        return self.msg


class NotIndexableException(Exception):
    def __init__(self, variable, lineno):
        self.lineno = lineno
        self.msg = "Variable {} is not indexable at line {}".format(variable, lineno)

    def __str__(self):
        return self.msg


class NoSuchModifierException(Exception):
    def __init__(self, modifier, lineno):
        self.modifier = modifier
        self.lineno = lineno
        self.msg = "No such modifier {} at line {}".format(modifier, lineno)

    def __str__(self):
        return self.msg


class NoSuchActionException(Exception):
    def __init__(self, action, lineno):
        self.lineno = lineno
        self.msg = 'No such action {} at line {}'.format(action, lineno)

    def __str__(self):
        return self.msg


class WrongPatternForActionException(Exception):
    def __init__(self, pattern_expected, pattern_found, lineno):
        self.msg = 'Expected pattern {}, but found {} at line {}'.format(pattern_expected, pattern_found, lineno)

    def __str__(self):
        return self.msg


class UnclosedBlockTagException(Exception):
    def __init__(self, tag, lineno):
        self.msg = 'Block tag {} not closed at line {}'.format(tag, lineno)

    def __str__(self):
        return self.msg


class EmptyBlockTagException(Exception):
    def __init__(self, tag, lineno):
        self.msg = 'Empty block tag {} at line {}'.format(tag, lineno)

    def __str__(self):
        return self.msg


class CharacterParseException(Exception):
    def __init__(self, contents, lineno):
        self.msg = 'Cannot parse {} at line {}'.format(contents, lineno)

    def __str__(self):
        return self.msg


class VariableParseException(Exception):
    def __init__(self, contents, lineno):
        self.msg = 'Cannot parse variable {} at line {}'.format(contents, lineno)

    def __str__(self):
        return self.msg
