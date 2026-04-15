from enum import StrEnum

class CrimTokenType(StrEnum):
    # With the exception of literals, these MUST match the
    # keywords in-code.

    # Operators
    VAL_INC = '+'
    VAL_DEC = '-'
    PTR_INC = '>'
    PTR_DEC = '<'

    # Keywords
    PRINT = 'print'
    INPUT = 'input'
    UNTIL = 'until'
    SET = 'set'
    CLEAR = 'clear'
    MOVE = 'mv'   # move
    COPY = 'cp'   # copy

    # Punctuation
    BRACE_L = '{'
    BRACE_R = '}'
    BRACKET_L = '('
    BRACKET_R = ')'
    TERMINATOR = ';'

    # Comments
    COMMENT_INLINE = '//'
    COMMENT_LONG_START = '/*'
    COMMENT_LONG_END = '*/'

    # Literals
    INTEGER = 'INTEGER'
    STRING = 'STRING'
    IDENTIFIER = 'IDENTIFIER'

class Token:
    def __init__(self, typ: CrimTokenType, val: str | int | None) -> None:
        self.typ = typ
        self.val = val

    def __repr__(self):
        return f"Token(type={self.typ}, value={self.val})"
