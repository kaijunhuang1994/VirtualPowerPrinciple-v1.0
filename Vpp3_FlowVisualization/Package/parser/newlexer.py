"""Lexer definition for input databases

January 2017, C.J. Voesenek
"""

import ply.lex as lex

__author__ = "C.J. Voesenek"
__maintainer__ = "C.J. Voesenek"
__email__ = "cees.voesenek@wur.nl"

tokens = ("BOOLEAN",
          "VARIABLE",
          "STRING",
          "COMMENT",
          "EQUALS",
          "MINUS",
          "PLUS",
          "TIMES",
          "DIVIDE",
          "POWER",
          "COMMA",
          "COLON",
          "OPEN_PARENTHESIS",
          "CLOSE_PARENTHESIS",
          "OPEN_BRACKET",
          "CLOSE_BRACKET",
          "OPEN_CURLY_BRACKET",
          "CLOSE_CURLY_BRACKET",
          "INTEGER",
          "FLOAT")

t_ignore = " \t\r\n"
t_COMMENT = r"//.*"
t_EQUALS = r"="
t_MINUS = r"-"
t_PLUS = r"\+"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_POWER = r"\^"
t_COMMA = r","
t_COLON = r":"
t_OPEN_PARENTHESIS = r"\("
t_CLOSE_PARENTHESIS = r"\)"
t_OPEN_BRACKET = r"\["
t_CLOSE_BRACKET = r"\]"
t_OPEN_CURLY_BRACKET = r"\{"
t_CLOSE_CURLY_BRACKET = r"\}"

# We add BOOLEAN, VARIABLE, and STRING as functions to ensure their order is
# correct - we need BOOLEAN to be first, since it will be parsed as a
# VARIABLE otherwise.
def t_BOOLEAN(t):
    r"(?<!\w)(TRUE|FALSE|true|false|True|False)(?!\w)"
    if t.value.lower() == "true":
        t.value = True
    else:
        t.value = False
    return t


def t_VARIABLE(t):
    r"[a-zA-Z_][\w\d_]*"
    return t


def t_STRING(t):
    r"\"[^\"]*\""
    t.value = t.value[1:-1]
    return t


def t_INTEGER(t):
    r"[-+]?\d+(?!(\.|e|\d))"
    t.value = int(t.value)
    return t


def t_FLOAT(t):
    r"(" \
    r"[-+]?(?P<leading>(\d+)?)\.(?(leading)\d*|\d+)(e(-)?\d+)?" \
    r"|" \
    r"[-+]?\d+e(-)?\d+" \
    r")"
    t.value = float(t.value)
    return t


def t_error(t):
    raise TypeError("Invalid string: {}".format(t.value))


lexer = lex.lex()
