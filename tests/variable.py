import re

constant_string = r"""
(%(strdq)s|%(strsq)s)
""" % {
    'strdq': r'"[^"\\]*(?:\\.[^"\\]*)*"',  # double-quoted string
    'strsq': r"'[^'\\]*(?:\\.[^'\\]*)*'",  # single-quoted string
}
constant_string = constant_string.replace("\n", "")

filter_raw_string = r"""
^(?P<constant>%(constant)s)|
^(?P<var>[%(var_chars)s]+|%(num)s)|
 (?:\s*%(filter_sep)s\s*
     (?P<filter_name>\w+)
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
    'filter_sep': re.escape('>>'),
    'arg_sep': re.escape('=>'),
}

filter_re = re.compile(filter_raw_string, re.VERBOSE)

for i in filter_re.finditer('var>>test'):
    print(i.group('filter_name'))
