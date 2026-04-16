"""Module for generic Crimscript token types."""

from enum import StrEnum
from dataclasses import dataclass

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
    CLEAR = 'clear'
    SET = 'set'
    MOVE = 'mv'   # move
    COPY = 'cp'   # copy

    # Punctuation
    BRACE_L = '{'
    BRACE_R = '}'
    BRACKET_L = '('
    BRACKET_R = ')'
    COMMA = ','
    COLON = ':'
    TERMINATOR = ';'

    # Comments
    COMMENT_INLINE = '//'
    COMMENT_LONG_START = '/*'
    COMMENT_LONG_END = '*/'

    # Literals
    INTEGER = 'INTEGER'
    STRING = 'STRING'
    IDENTIFIER = 'IDENTIFIER'

@dataclass
class TokenMetadata:
    """
    contents   the string literal from which the token originated, e.g. "("
    loc        the (lineno, column) of the token start in the source code
    """
    contents: str
    loc: tuple[int, int]

class Token:
    def __init__(
            self, typ: CrimTokenType, val: str | int | None,
            metadata: TokenMetadata
        ) -> None:
        self.typ = typ
        self.val = val
        self.metadata = metadata

    def __repr__(self):
        return (
            "Token("
            f"type={self.typ},"
            f"value={self.val},"
            f"contents={self.metadata.contents},"
            f"loc={self.metadata.loc[0] + 1}:{self.metadata.loc[1] + 1}"
            ")"
        )
