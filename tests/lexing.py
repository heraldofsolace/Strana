import re

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
print(tag_expr_re.split('{> x <} fkjg {= g =}'))
