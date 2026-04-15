from dataclasses import dataclass
from typing import List, Optional

from .exceptions import (
    CompilerSyntaxError,
    CompilerMemoryError,
    CompilerWarning,
    CompilerTypeError,
    compiler_err,
    compiler_warn
)

import re
from .crim_tokens import Token, CrimTokenType

# AST node definitions
@dataclass
class Statement:
    pass

@dataclass
class ValueChange(Statement):
    amount: int

@dataclass
class PointerChange(Statement):
    distance: int

@dataclass
class PrintStmt(Statement):
    text: str | None = None

@dataclass
class InputStmt(Statement):
    prompt: str | None = None

@dataclass
class ClearStmt(Statement):
    pass

@dataclass
class SetStmt(Statement):
    value: int

@dataclass
class UntilStmt(Statement):
    target: int
    body: List[Statement]

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

    def _parse_statement(self) -> Statement:
        """Parse the next top-level Crimscript statement from the token stream."""
        token = self._peek()

        if token.typ == CrimTokenType.PRINT:
            return self._parse_print()
        if token.typ == CrimTokenType.INPUT:
            return self._parse_input()
        if token.typ == CrimTokenType.CLEAR:
            return self._parse_clear()
        if token.typ == CrimTokenType.SET:
            return self._parse_set()
        if token.typ == CrimTokenType.UNTIL:
            return self._parse_until()
        if token.typ in (CrimTokenType.VAL_INC, CrimTokenType.VAL_DEC):
            return self._parse_value_change()
        if token.typ in (CrimTokenType.PTR_INC, CrimTokenType.PTR_DEC):
            return self._parse_pointer_change()

        compiler_err(f"Unexpected token {token.typ} in statement position", CompilerSyntaxError)

    def _parse_print(self) -> PrintStmt:
        """Parse a print() statement, optionally with a string argument."""
        self._expect(CrimTokenType.PRINT)
        self._expect(CrimTokenType.BRACKET_L)

        text: str | None = None
        if self._peek().typ == CrimTokenType.STRING:
            advance = self._advance()
            assert isinstance(advance.val, str) or advance.val is None
            text = advance.val

        self._expect(CrimTokenType.BRACKET_R)
        return PrintStmt(text=text)

    def _parse_input(self) -> InputStmt:
        """Parse an input() statement, optionally with a prompt string."""
        self._expect(CrimTokenType.INPUT)
        self._expect(CrimTokenType.BRACKET_L)

        prompt: str | None = None
        if self._peek().typ == CrimTokenType.STRING:
            advance = self._advance()
            assert isinstance(advance.val, str) or advance.val is None
            prompt = advance.val

        self._expect(CrimTokenType.BRACKET_R)
        return InputStmt(prompt=prompt)

    def _parse_clear(self) -> ClearStmt:
        """Parse a clear() statement, which clears the current data cell."""
        self._expect(CrimTokenType.CLEAR)
        self._expect(CrimTokenType.BRACKET_L)
        self._expect(CrimTokenType.BRACKET_R)
        return ClearStmt()

    def _parse_set(self) -> SetStmt:
        """Parse a set(n) statement and validate that its argument is an integer."""
        self._expect(CrimTokenType.SET)
        self._expect(CrimTokenType.BRACKET_L)

        if self._peek().typ != CrimTokenType.NUMBER:
            compiler_err("set() requires an integer argument", CompilerSyntaxError)

        value = self._advance().val
        self._expect(CrimTokenType.BRACKET_R)

        if not isinstance(value, int):
            compiler_err("set() argument must be an integer", CompilerSyntaxError)

        return SetStmt(value=value)

    def _parse_until(self) -> UntilStmt:
        """Parse an until N { ... } loop and its nested statement body."""
        self._expect(CrimTokenType.UNTIL)

        if self._peek().typ != CrimTokenType.NUMBER:
            compiler_err("until requires a numeric target", CompilerSyntaxError)

        target = self._advance().val
        if not isinstance(target, int):
            compiler_err("until target must be an integer", CompilerSyntaxError)

        self._expect(CrimTokenType.BRACE_L)
        body: list[Statement] = []

        while not self._eof() and self._peek().typ != CrimTokenType.BRACE_R:
            if self._peek().typ == CrimTokenType.TERMINATOR:
                self._advance()
                continue
            body.append(self._parse_statement())
            while not self._eof() and self._peek().typ == CrimTokenType.TERMINATOR:
                self._advance()

        self._expect(CrimTokenType.BRACE_R)
        return UntilStmt(target=target, body=body)

    def _parse_value_change(self) -> ValueChange:
        """Parse a numeric value increment or decrement operation."""
        token = self._advance()
        if not isinstance(token.val, int):
            compiler_err("Value change token must include an integer count", CompilerSyntaxError)
        amount = token.val if token.typ == CrimTokenType.VAL_INC else -token.val
        return ValueChange(amount=amount)

    def _parse_pointer_change(self) -> PointerChange:
        """Parse a numeric pointer movement instruction."""
        token = self._advance()
        if not isinstance(token.val, int):
            compiler_err("Pointer change token must include an integer distance", CompilerSyntaxError)
        distance = token.val if token.typ == CrimTokenType.PTR_INC else -token.val
        return PointerChange(distance=distance)

    def _compile_statement(self, stmt: Statement) -> str:
        """Convert a parsed AST statement into Brainfuck source code."""
        if isinstance(stmt, ValueChange):
            return '+' * stmt.amount if stmt.amount > 0 else '-' * (-stmt.amount)
        if isinstance(stmt, PointerChange):
            return '>' * stmt.distance if stmt.distance > 0 else '<' * (-stmt.distance)
        if isinstance(stmt, PrintStmt):
            return self._compile_print(stmt)
        if isinstance(stmt, InputStmt):
            return self._compile_input(stmt)
        if isinstance(stmt, ClearStmt):
            return '[-]'
        if isinstance(stmt, SetStmt):
            if stmt.value == 0:
                return '[-]'
            return '[-]' + ('+' * stmt.value)
        if isinstance(stmt, UntilStmt):
            return self._compile_until(stmt)

        compiler_err(f"Unknown statement type: {type(stmt).__name__}", CompilerSyntaxError)

    def _compile_print(self, stmt: PrintStmt) -> str:
        """Compile a print statement to Brainfuck, either '.' or string output."""
        if stmt.text is None:
            return '.'

        result = []
        for char in stmt.text:
            result.append('[-]')
            result.append('+' * ord(char))
            result.append('.')
        result.append('[-]')
        return ''.join(result)

    def _compile_input(self, stmt: InputStmt) -> str:
        """Compile an input statement to Brainfuck, optionally emitting a prompt first."""
        code = []
        if stmt.prompt is not None:
            code.append(self._compile_print(PrintStmt(text=stmt.prompt)))
        code.append(',')
        return ''.join(code)

    def _compile_until(self, stmt: UntilStmt) -> str:
        """Compile an until loop into Brainfuck with offset checking and body code."""
        offset = '-' * stmt.target
        restore = '+' * stmt.target
        body = ''.join(self._compile_statement(child) for child in stmt.body)
        return f"{offset}[{restore}{body}{offset}]{restore}"

    def _peek(self) -> Token:
        """Return the current token without consuming it."""
        if self.pos >= len(self.tokens):
            compiler_err("Unexpected end of input", CompilerSyntaxError)
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        """Consume and return the current token."""
        token = self._peek()
        self.pos += 1
        return token

    def _expect(self, expected_type: CrimTokenType) -> Token:
        """Consume a token and verify it matches the expected type."""
        token = self._peek()
        if token.typ != expected_type:
            compiler_err(f"Expected {expected_type} but got {token.typ}", CompilerSyntaxError)
        return self._advance()

    def _eof(self) -> bool:
        """Return True when the parser has consumed all tokens."""
        return self.pos >= len(self.tokens)

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

    def parse(self, tokens: list[Token]) -> list[Statement]:
        """Parse a list of tokens into a list of statements."""
        self.tokens = tokens
        self.pos = 0
        statements: list[Statement] = []

        while not self._eof():
            if self._peek().typ == CrimTokenType.TERMINATOR:
                self._advance()
                continue

            statements.append(self._parse_statement())

            while not self._eof() and self._peek().typ == CrimTokenType.TERMINATOR:
                self._advance()

        return statements

    def compile_brainfuck(self, code: list[str]) -> str:
        """
        Accepts a document of macrolang code and converts it to Brainfuck.
        The input is a list of strings, where each string is a line of Crimscript code.
        The output is a single string of Brainfuck code.
        """

        tokens = self.tokenise(code)
        ast = self.parse(tokens)
        bf_code: list[str] = []

        for statement in ast:
            bf_code.append(self._compile_statement(statement))

        return "".join(bf_code)
