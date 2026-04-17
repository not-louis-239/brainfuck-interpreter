import re
from ..crim_tokens import Token, TokenMetadata, CrimTokenType
from ..exceptions import CompilerSyntaxError

class Lexer:
    """Converts Crimscript source code into Crimscript tokens.
    The first stage."""

    def _preprocess_code(self, code: list[str]) -> list[str]:
        """Returns a pre-processed version of the code to handle
        line continuations, whitespace and statement terminators.
        Returns a list of processed lines ready for tokenisation."""
        processed = []

        i = 0; code_len = len(code)
        while i < code_len:
            line = code[i].rstrip()  # Remove trailing whitespace

            # Handle line continuations
            while line.endswith('\\') and i + 1 < len(code):
                line = line[:-1] + code[i + 1].lstrip()
                i += 1

            processed.append(line)
            i += 1

        return processed

    def _unescape_string(self, s: str) -> str:
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

    def tokenise(self, code: list[str]) -> list[str]:
        """
        Tokenises the input Crimscript code into a list of Tokens.
        Each line of code is processed to identify valid commands and their arguments.
        """
        tokens = []

        # First, handle line continuations and join multi-line statements
        processed_code = self._preprocess_code(code)

        # Join all lines into a single string for tokenization
        full_code = '\n'.join(processed_code)
        full_code_lines = full_code.split('\n')

        # Define regex patterns for different token types
        # Order matters: patterns near the top are applied first
        patterns = [
            # Comments (must come before other patterns)
            (r'//.*', None),  # Single-line comments - skip
            (r'/\*.*?\*/', None),  # Multi-line comments - skip

            # Strings (with escape sequence support)
            (r'"(?:[^"\\]|\\.)*"', lambda m: Token(CrimTokenType.STRING, self._unescape_string(m.group(0)))),

            # Condensed operations (must come before single operators)
            (r'\+(\d+)', lambda m: Token(CrimTokenType.VAL_INC, int(m.group(1)))),
            (r'-(\d+)', lambda m: Token(CrimTokenType.VAL_DEC, int(m.group(1)))),
            (r'>(\d+)', lambda m: Token(CrimTokenType.PTR_INC, int(m.group(1)))),
            (r'<(\d+)', lambda m: Token(CrimTokenType.PTR_DEC, int(m.group(1)))),

            # Numbers (must come after condensed operations)
            (r'\d+', lambda m: Token(CrimTokenType.INTEGER, int(m.group(0)))),

            # Keywords (must come before identifiers)
            (r'\bprint\b', lambda m: Token(CrimTokenType.PRINT, m.group(0))),
            (r'\binput\b', lambda m: Token(CrimTokenType.INPUT, m.group(0))),
            (r'\buntil\b', lambda m: Token(CrimTokenType.UNTIL, m.group(0))),
            (r'\bset\b', lambda m: Token(CrimTokenType.SET, m.group(0))),
            (r'\bclear\b', lambda m: Token(CrimTokenType.CLEAR, m.group(0))),
            (r'\bmv\b', lambda m: Token(CrimTokenType.MOVE, m.group(0))),  # move
            (r'\bcp\b', lambda m: Token(CrimTokenType.COPY, m.group(0))),  # copy

            # Single operators (must come after condensed operations)
            (r'\+', lambda m: Token(CrimTokenType.VAL_INC, 1)),
            (r'-', lambda m: Token(CrimTokenType.VAL_DEC, 1)),
            (r'>', lambda m: Token(CrimTokenType.PTR_INC, 1)),
            (r'<', lambda m: Token(CrimTokenType.PTR_DEC, 1)),

            # Punctuation
            (r'\{', lambda m: Token(CrimTokenType.BRACE_L, m.group(0))),
            (r'\}', lambda m: Token(CrimTokenType.BRACE_R, m.group(0))),
            (r'\(', lambda m: Token(CrimTokenType.BRACKET_L, m.group(0))),
            (r'\)', lambda m: Token(CrimTokenType.BRACKET_R, m.group(0))),
            (r',', lambda m: Token(CrimTokenType.COMMA, m.group(0))),
            (r':', lambda m: Token(CrimTokenType.COLON, m.group(0))),
            (r';', lambda m: Token(CrimTokenType.TERMINATOR, m.group(0))),

            # Whitespace (skip)
            (r'\s+', None),
        ]

        # Process the full code as one string
        pos = 0
        while pos < len(full_code):
            matched = False
            line_num = len(full_code_lines)
            col_num = len(full_code_lines[-1]) + 1

            for pattern, token_func in patterns:
                if pattern == r'/\*.*?\*/':  # Multi-line comment needs DOTALL flag
                    regex = re.compile(pattern, re.DOTALL)
                else:
                    regex = re.compile(pattern)
                match = regex.match(full_code, pos)

                if match:
                    if token_func is not None:
                        new_token = token_func(match)

                        # Set token metadata
                        new_token.metadata = TokenMetadata(contents=match.group(0), loc=(line_num, col_num))

                        tokens.append(new_token)
                    pos = match.end()
                    matched = True
                    break

            if not matched:
                # No pattern matched - syntax error
                # Calculate line and column for better error reporting
                raise CompilerSyntaxError(f"Unexpected character '{full_code[pos]}' at line {line_num}, column {col_num}", pos, full_code)

        return tokens
