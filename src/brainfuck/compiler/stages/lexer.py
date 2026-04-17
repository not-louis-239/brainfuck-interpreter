import re
from typing import Callable, TypeAlias

from ..crim_tokens import Token, TokenMetadata, CrimTokenType
from ..exceptions import CompilerSyntaxError
from ..get_line_and_col import get_line_and_col

def unescape_string(s: str) -> str:
    """Unescape escape sequences in a string literal (including the surrounding quotes)."""

    # Remove surrounding quotes
    content = s[1:-1]

    # Handle common escape sequences
    SEQUENCES = [
        ('\\n', '\n'),
        ('\\t', '\t'),
        ('\\r', '\r'),
        ('\\"', '"'),
        ('\\\\', '\\'),
    ]

    for seq in SEQUENCES:
        content = content.replace(seq[0], seq[1])

    # Handle escapes like "\xhh" for hex values
    def replace_hex(match: re.Match) -> str:
        return chr(int(match.group(1), 16))
    return re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, content)

# Type for our regex action: takes a match, returns a Token or None (to skip)
# Order matters: patterns are applied from the top down
_TokenAction: TypeAlias = Callable[[re.Match], Token]
LEXER_PATTERNS: list[tuple[re.Pattern, _TokenAction | None]] = [
    # Line continuations (backslash + newline)
    (re.compile(r'\\\n'), None),

    # Strings (with escape sequence support)
    (re.compile(r'"(?:[^"\\]|\\.)*"'), lambda m: Token(CrimTokenType.STRING, unescape_string(m.group(0)))),

    # Comments (must come before other patterns)
    (re.compile(r'//.*'), None),       # Inline comments
    (re.compile(r'/\*.*?\*/', re.DOTALL), None),  # Multi-line comments

    # Condensed operations (must come before single operators)
    (re.compile(r'\+(\d+)'), lambda m: Token(CrimTokenType.VAL_INC, int(m.group(1)))),
    (re.compile(r'-(\d+)'), lambda m: Token(CrimTokenType.VAL_DEC, int(m.group(1)))),
    (re.compile(r'>(\d+)'), lambda m: Token(CrimTokenType.PTR_INC, int(m.group(1)))),
    (re.compile(r'<(\d+)'), lambda m: Token(CrimTokenType.PTR_DEC, int(m.group(1)))),

    # Integers (must come after condensed operations)
    (re.compile(r'\d+'), lambda m: Token(CrimTokenType.INTEGER, int(m.group(0)))),

    # Keywords (must come before identifiers)
    (re.compile(r'\bprint\b'), lambda m: Token(CrimTokenType.PRINT, m.group(0))),
    (re.compile(r'\binput\b'), lambda m: Token(CrimTokenType.INPUT, m.group(0))),
    (re.compile(r'\buntil\b'), lambda m: Token(CrimTokenType.UNTIL, m.group(0))),
    (re.compile(r'\bset\b'), lambda m: Token(CrimTokenType.SET, m.group(0))),
    (re.compile(r'\bclear\b'), lambda m: Token(CrimTokenType.CLEAR, m.group(0))),
    (re.compile(r'\bmv\b'), lambda m: Token(CrimTokenType.MOVE, m.group(0))),  # move
    (re.compile(r'\bcp\b'), lambda m: Token(CrimTokenType.COPY, m.group(0))),  # copy

    # Single operators (must come after condensed operations)
    (re.compile(r'\+'), lambda m: Token(CrimTokenType.VAL_INC, 1)),
    (re.compile(r'-'), lambda m: Token(CrimTokenType.VAL_DEC, 1)),
    (re.compile(r'>'), lambda m: Token(CrimTokenType.PTR_INC, 1)),
    (re.compile(r'<'), lambda m: Token(CrimTokenType.PTR_DEC, 1)),

    # Punctuation
    (re.compile(r'\{'), lambda m: Token(CrimTokenType.BRACE_L, m.group(0))),
    (re.compile(r'\}'), lambda m: Token(CrimTokenType.BRACE_R, m.group(0))),
    (re.compile(r'\('), lambda m: Token(CrimTokenType.BRACKET_L, m.group(0))),
    (re.compile(r'\)'), lambda m: Token(CrimTokenType.BRACKET_R, m.group(0))),
    (re.compile(r','), lambda m: Token(CrimTokenType.COMMA, m.group(0))),
    (re.compile(r':'), lambda m: Token(CrimTokenType.COLON, m.group(0))),
    (re.compile(r';'), lambda m: Token(CrimTokenType.TERMINATOR, m.group(0))),

    # Whitespace (Skip)
    (re.compile(r'\s+'), None),
]

class Lexer:
    """Converts Crimscript source code into Crimscript tokens.
    The first stage."""

    def tokenise(self, src_code: list[str]) -> list[Token]:
        """
        Tokenises the input Crimscript code into a list of Tokens.
        Each line of code is processed to identify valid commands and their arguments.
        """
        tokens = []
        full_code = "\n".join(src_code)

        pos = 0
        full_code_len = len(full_code)

        while pos < full_code_len:
            matched = False
            line_num, col_num = get_line_and_col(src_code, pos)

            for pattern, token_func in LEXER_PATTERNS:
                match = pattern.match(full_code, pos)

                if not match:
                    continue

                if token_func is not None:
                    token = token_func(match)
                    token.metadata = TokenMetadata(
                        pos=pos
                    )

                    tokens.append(token)

                pos = match.end()
                matched = True
                break

            if not matched:
                raise CompilerSyntaxError(
                    f"unexpected character '{full_code[pos]}'",
                    pos=pos, src_code=src_code,
                )

        return tokens
