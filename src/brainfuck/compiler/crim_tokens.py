"""Module for generic Crimscript token types."""

from enum import StrEnum
from dataclasses import dataclass

from brainfuck.compiler.get_line_and_col import get_line_and_col

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
    """Stores the location of the token in the source code (COMMENTS INCLUDED!).
    This is abstracted out into a separate class in case more
    metadata needs to be added in the future."""
    pos: int

class Token:
    def __init__(
            self, typ: CrimTokenType, val: str | int | None,
            metadata: TokenMetadata | None = None
        ) -> None:
        # Using TokenMetadata | None allows for lazy initialisation
        # and then assigning metadata.
        self.typ = typ
        self.val = val
        self.metadata = metadata

    def __repr__(self):
        if self.metadata is not None:
            return (
                "Token("
                f"type={self.typ}, "
                f"value={self.val}, "
                f"pos={self.metadata.pos}"
                ")"
            )
        return (
            "Token("
            f"type={self.typ}, "
            f"value={self.val}, "
            f"<no metadata>"
            ")"
        )

