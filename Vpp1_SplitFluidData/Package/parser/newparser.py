"""Parser definition for input databases

January 2017, C.J. Voesenek
"""

import ply.yacc as yacc

import newlexer 
from .inputdatabase import InputDatabase, Expression

__author__ = "C.J. Voesenek"
__maintainer__ = "C.J. Voesenek"
__email__ = "cees.voesenek@wur.nl"

tokens = newlexer.tokens
database = InputDatabase()

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("left", "POWER"),
    ("right", "UMINUS")
)


def p_database(p):
    """database : contents_root"""
    p[0] = database


def p_empty(p):
    """empty :"""
    p[0] = []


def p_contents_root_empty(p):
    """contents_root : empty"""
    p[0] = []


def p_contents_root_append_assign(p):
    """contents_root : contents_root assign"""
    database.add(p[2][0], p[2][1])


def p_contents_root_comment(p):
    """contents_root : contents_root COMMENT"""
    pass


def p_contents_empty(p):
    """contents : empty"""
    p[0] = []


def p_contents_append_assign(p):
    """contents : contents assign"""
    p[0] = p[1]
    p[0].append(p[2])


def p_contents_comment(p):
    """contents : contents COMMENT"""
    p[0] = p[1]


def p_block(p):
    """block : OPEN_CURLY_BRACKET contents CLOSE_CURLY_BRACKET"""
    p[0] = InputDatabase(root=database)
    for entry in p[2]:
        p[0].add(entry[0], entry[1])


def p_assign(p):
    """
    assign : VARIABLE EQUALS expr
    assign : VARIABLE EQUALS list
    assign : VARIABLE EQUALS tuple
    assign : VARIABLE EQUALS dictionary
    assign : VARIABLE EQUALS STRING
    assign : VARIABLE EQUALS BOOLEAN
    """
    p[0] = (p[1], p[3])


def p_assign_block(p):
    """assign : VARIABLE block"""
    p[0] = (p[1], p[2])


def p_expr_operator(p):
    """
    expr : expr PLUS expr
         | expr MINUS expr
         | expr TIMES expr
         | expr DIVIDE expr
         | expr POWER expr
    """
    p[0] = Expression(p[2], p[1], p[3])


def p_expr_uminus(p):
    """expr : MINUS expr %prec UMINUS"""
    p[0] = Expression("--", p[2])


def p_expr_integer(p):
    """
    expr : INTEGER
         | FLOAT
    """
    p[0] = p[1]


def p_expr_variable(p):
    """expr : VARIABLE"""
    p[0] = Expression("var", p[1])


def p_factor_expr(p):
    """expr : OPEN_PARENTHESIS expr CLOSE_PARENTHESIS"""
    p[0] = p[2]


def p_list_empty(p):
    """list : OPEN_BRACKET CLOSE_BRACKET"""
    p[0] = []


def p_list_single_expr(p):
    """list : OPEN_BRACKET item CLOSE_BRACKET"""
    p[0] = [p[2]]


def p_list_brackets(p):
    """list : OPEN_BRACKET items CLOSE_BRACKET"""
    p[0] = p[2]


def p_list_bare(p):
    """list : items"""
    p[0] = p[1]


def p_tuple(p):
    """tuple : OPEN_PARENTHESIS items CLOSE_PARENTHESIS"""
    p[0] = tuple(p[2])


def p_items_comma(p):
    """items : item COMMA items"""
    p[0] = p[3]
    p[0].insert(0, p[1])


def p_items_expr(p):
    """items : item COMMA item"""
    p[0] = [p[1], p[3]]


def p_item(p):
    """
    item : expr
    item : tuple
    item : dictionary
    item : BOOLEAN
    item : STRING
    """
    p[0] = p[1]


def p_dictionary(p):
    """dictionary : OPEN_CURLY_BRACKET dictionary_items CLOSE_CURLY_BRACKET"""
    p[0] = p[2]


def p_dictionary_empty(p):
    """dictionary : OPEN_CURLY_BRACKET CLOSE_CURLY_BRACKET"""
    p[0] = dict()


def p_dictionary_items_single(p):
    """dictionary_items : dictionary_item"""
    p[0] = p[1]


def p_dictionary_items_multiple(p):
    """dictionary_items : dictionary_item COMMA dictionary_items"""
    p[0] = {**p[1], **p[3]}


def p_dictionary_item(p):
    """dictionary_item : key COLON item"""
    p[0] = dict()
    p[0][p[1]] = p[3]


def p_key(p):
    """
    key : STRING
    key : INTEGER
    key : FLOAT
    key : BOOLEAN
    """
    p[0] = p[1]


def p_error(p):
    raise SyntaxError("Syntax error at {} token: {}".format(p.type,
                                                            p.value))


parser = yacc.yacc()


def parse(file) -> InputDatabase:
    """Parses the input file.

    This function wraps a Python lex/yacc (PLY) parser for input files.

    Args:
        file: The input file to parse.

    Returns:
        An input database with the parsed input file.
    """
    global database
    database = InputDatabase()
    with open(file, "r") as f:
        raw = f.read()
        result = parser.parse(raw)
        parser.restart()
        return result
