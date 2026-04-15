from .exceptions import (
    CompilerSyntaxError,
    CompilerMemoryError,
    CompilerWarning,
    compiler_err,
    compiler_warn
)

import re
from .crim_tokens import Token, CrimTokenType

class CrimscriptCompiler:
    def __init__(self):
        # Initialize any necessary data structures or state here
        pass

    def _preprocess_code(self, code: list[str]) -> list[str]:
        """
        Preprocess the code to handle line continuations and remove comments.
        """
        processed = []
        i = 0
        while i < len(code):
            line = code[i].rstrip()  # Remove trailing whitespace

            # Handle line continuations
            while line.endswith('\\') and i + 1 < len(code):
                line = line[:-1] + code[i + 1].lstrip()
                i += 1

            processed.append(line)
            i += 1

        return processed

    def tokenise(self, code: list[str]) -> list[Token]:
        """
        Tokenises the input Crimscript code into a list of Tokens.
        Each line of code is processed to identify valid commands and their arguments.
        """
        tokens = []

        # First, handle line continuations and join multi-line statements
        processed_code = self._preprocess_code(code)

        # Define regex patterns for different token types
        # Order matters: longer/more specific patterns first
        patterns = [
            # Comments (must come before other patterns)
            (r'//.*', None),  # Single-line comments - skip
            (r'/\*.*?\*/', None),  # Multi-line comments - skip

            # Strings
            (r'"([^"]*)"', lambda m: Token(CrimTokenType.STRING, m.group(1))),

            # Condensed operations (must come before single operators)
            (r'\+(\d+)', lambda m: Token(CrimTokenType.VAL_INC, int(m.group(1)))),
            (r'-(\d+)', lambda m: Token(CrimTokenType.VAL_DEC, int(m.group(1)))),
            (r'>(\d+)', lambda m: Token(CrimTokenType.PTR_INC, int(m.group(1)))),
            (r'<(\d+)', lambda m: Token(CrimTokenType.PTR_DEC, int(m.group(1)))),

            # Numbers (must come after condensed operations)
            (r'\d+', lambda m: Token(CrimTokenType.NUMBER, int(m.group(0)))),

            # Keywords (must come before identifiers)
            (r'\bprint\b', lambda m: Token(CrimTokenType.PRINT, m.group(0))),
            (r'\binput\b', lambda m: Token(CrimTokenType.INPUT, m.group(0))),
            (r'\buntil\b', lambda m: Token(CrimTokenType.UNTIL, m.group(0))),
            (r'\bset\b', lambda m: Token(CrimTokenType.SET, m.group(0))),
            (r'\bclear\b', lambda m: Token(CrimTokenType.CLEAR, m.group(0))),

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
            (r';', lambda m: Token(CrimTokenType.TERMINATOR, m.group(0))),

            # Whitespace (skip)
            (r'\s+', None),
        ]

        # Process each line
        for line in processed_code:
            pos = 0
            while pos < len(line):
                matched = False

                for pattern, token_func in patterns:
                    regex = re.compile(pattern)
                    match = regex.match(line, pos)

                    if match:
                        if token_func is not None:
                            tokens.append(token_func(match))
                        pos = match.end()
                        matched = True
                        break

                if not matched:
                    # No pattern matched - syntax error
                    compiler_err(f"Unexpected character '{line[pos]}' at position {pos}", CompilerSyntaxError)

        return tokens

    def parse(self):
        # TODO
        # ... rest of implementation ...
        ...

    def compile_brainfuck(self, code: list[str]) -> str:
        """
        Accepts a document of macrolang code and converts it to Brainfuck.
        The input is a list of strings, where each string is a line of Crimscript code.
        The output is a single string of Brainfuck code.
        """

        tokens = self.tokenise(code)
        bf_code: list[str] = []  # list of Brainfuck code characters

        # TODO
        # ... rest of implementation ...

        return "".join(bf_code)
