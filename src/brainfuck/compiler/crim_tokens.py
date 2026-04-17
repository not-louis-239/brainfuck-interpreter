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
    """Stores the location of the token in the source code (COMMENTS INCLUDED!).
    This is abstracted out into a separate class in case more
    metadata needs to be added in the future."""
    loc: int

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

    def format_str(self, src_code: list[str]):
        if self.metadata is not None:
            return (
                "Token("
                f"type={self.typ}, "
                f"value={self.val}, "
                f"loc={get_line_and_col(src_code, self.metadata.loc)}"
                ")"
            )
        return (
            "Token("
            f"type={self.typ}, "
            f"value={self.val}, "
            f"<no metadata>"
            ")"
        )

def get_line_and_col(src_code: list[str], pos: int) -> tuple[int, int]:
    """Translates a flat integer position into (line, col) using
    a list of source code lines (COMMENTS INCLUDED!)."""

    # Performance shouldn't matter too much here as it is only used
    # once to format errors.

    current_pos = 0
    for line_num, line_content in enumerate(src_code):
        line_len = len(line_content)
        # Check if the position falls within this line
        if current_pos <= pos < current_pos + line_len:
            col = pos - current_pos
            return line_num + 1, col + 1

        current_pos += line_len

    # Fallback for EOF or empty files
    return len(src_code), 1
