from dataclasses import dataclass

from .exceptions import (
    CompilerSyntaxError,
    CompilerTypeError
)

import re
from .crim_tokens import Token, CrimTokenType

LINESIZE = 80  # split the final BF code to this many chars per line for readability

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
    body: list[Statement]

@dataclass
class MoveStmt(Statement):
    delta_ptr_min: int
    delta_ptr_max: int

@dataclass
class CopyStmt(Statement):
    delta_ptr_min: int
    delta_ptr_max: int
    delta_ptr_tmp: int

class _ParseHelper:
    """Class to handle token parsing. Stores parse_* methods."""
    def __init__(self):
        pass

    # TODO: move relevant methods here

class _CompileHelper:
    """Class to store token conversions to Brainfuck commands. Stores compile_* methods."""
    def __init__(self):
        pass

    # TODO: move relevant methods here

class CrimscriptCompiler:
    def __init__(self):
        # Initialize any necessary data structures or state here
        self.parser = _ParseHelper()
        self.compiler = _CompileHelper()

    def _preprocess_code(self, code: list[str]) -> list[str]:
        """
        Preprocess the code to handle line continuations and remove comments.
        Returns a list of processed lines ready for tokenization.
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

        self.code = "\n".join(processed)  # Store the full code for error reporting
        return processed

    def _unescape_string(self, s: str) -> str:
        """Unescape escape sequences in a string literal (including the surrounding quotes)."""

        # Remove surrounding quotes
        content = s[1:-1]

        # Handle common escape sequences
        content_replaced = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r').replace('\\"', '"').replace('\\\\', '\\')

        # Handle escapes like "\xhh" for hex values
        def replace_hex(match: re.Match) -> str:
            return chr(int(match.group(1), 16))
        return re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, content_replaced)

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

        raise CompilerSyntaxError(f"Unexpected token: {token.typ}", self.pos, self.code)

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

        if self._peek().typ != CrimTokenType.INTEGER:
            raise CompilerTypeError("set() requires an integer argument", self.pos, self.code)

        value = self._advance().val
        self._expect(CrimTokenType.BRACKET_R)

        if not isinstance(value, int):
            raise CompilerTypeError("set() argument must be an integer", self.pos, self.code)

        return SetStmt(value=value)

    def _parse_until(self) -> UntilStmt:
        """Parse an until N { ... } loop and its nested statement body."""
        self._expect(CrimTokenType.UNTIL)

        if self._peek().typ != CrimTokenType.INTEGER:
            raise CompilerTypeError("until requires an integer target", self.pos, self.code)

        target = self._advance().val
        if not isinstance(target, int):
            raise CompilerTypeError("until target must be an integer", self.pos, self.code)

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
            raise CompilerTypeError("Value change token must include an integer count", self.pos, self.code)

        amount = token.val if token.typ == CrimTokenType.VAL_INC else -token.val
        return ValueChange(amount=amount)

    def _parse_pointer_change(self) -> PointerChange:
        """Parse a numeric pointer movement instruction."""
        token = self._advance()
        if not isinstance(token.val, int):
            raise CompilerTypeError("Pointer change token must include an integer distance", self.pos, self.code)

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

        raise CompilerSyntaxError(f"Unknown statement type: {type(stmt).__name__}", self.pos, self.code)

    def _compile_print(self, stmt: PrintStmt) -> str:
        """Compile a print statement to Brainfuck, either '.' or string output."""

        # Use a greedy approach so that instead of clearing then plussing
        # we remember the value from the last character and calculate how
        # many increments/decrements we need to get to the next character.

        if stmt.text is None:
            return '.'

        result: list[str] = []
        last_val: int = 0

        result.append('[-]')  # initial clear to ensure there is no residue

        for char in stmt.text:
            new_val = ord(char)
            diff = new_val - last_val

            # We can abuse how Brainfuck wraps values
            # at >255 or <0 to make our print even more efficient
            diff = (diff + 128) % 256 - 128  # this caps diff to [-128...127]

            result.append('+' * diff if diff > 0 else '-' * -diff)
            result.append('.')
            last_val = new_val

        result.append('[-]')  # final clear to leave cell at 0 after printing
        return ''.join(result)

    def _compile_input(self, stmt: InputStmt) -> str:
        """Compile an input statement to Brainfuck, optionally emitting a prompt first."""
        code: list[str] = []
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
            raise CompilerSyntaxError("Unexpected end of input", self.pos, self.code)
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
            raise CompilerSyntaxError(f"Expected {expected_type} but got {token.typ}", self.pos, self.code)
        return self._advance()

    def _eof(self) -> bool:
        """Return True when the parser has consumed all tokens."""
        return self.pos >= len(self.tokens)

    def _optimise_brainfuck(self, code: str) -> str:
        """Optimise the generated Brainfuck code by collapsing sequences of +/-, >/<, which cancel out."""
        def simplify_operators(match: re.Match) -> str:
            text = match.group(0)
            net = (text.count('+') - text.count('-') + 128) % 256 - 128  # net effect of the sequence, wrapped to [-128...127]
            if net > 0:
                return '+' * net
            elif net < 0:
                return '-' * -net
            else:
                return ''

        def simplify_pointers(match: re.Match) -> str:
            text = match.group(0)
            net = (text.count('>') - text.count('<'))  # no %256 here since pointer movement can be unbounded
            if net > 0:
                return '>' * net
            elif net < 0:
                return '<' * -net
            else:
                return ''

        code = re.sub(r'[+-]+', simplify_operators, code)
        code = re.sub(r'[<>]+', simplify_pointers, code)
        return code

    def tokenise(self, code: list[str]) -> list[Token]:
        """
        Tokenises the input Crimscript code into a list of Tokens.
        Each line of code is processed to identify valid commands and their arguments.
        """
        tokens = []

        # First, handle line continuations and join multi-line statements
        processed_code = self._preprocess_code(code)

        # Join all lines into a single string for tokenization
        full_code = '\n'.join(processed_code)

        # Define regex patterns for different token types
        # Order matters: longer/more specific patterns first
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

        # Process the full code as one string
        pos = 0
        while pos < len(full_code):
            matched = False

            for pattern, token_func in patterns:
                if pattern == r'/\*.*?\*/':  # Multi-line comment needs DOTALL flag
                    regex = re.compile(pattern, re.DOTALL)
                else:
                    regex = re.compile(pattern)
                match = regex.match(full_code, pos)

                if match:
                    if token_func is not None:
                        tokens.append(token_func(match))
                    pos = match.end()
                    matched = True
                    break

            if not matched:
                # No pattern matched - syntax error
                # Calculate line and column for better error reporting
                lines = full_code[:pos].split('\n')
                line_num = len(lines)
                col_num = len(lines[-1]) + 1
                raise CompilerSyntaxError(f"Unexpected character '{full_code[pos]}' at line {line_num}, column {col_num}", pos, full_code)

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

    def compile_crimscript(self, code: list[str]) -> str:
        """
        Accepts a document of macrolang code and converts it to Brainfuck.
        The input is a list of strings, where each string is a line of Crimscript code.
        The output is a single string of Brainfuck code.
        """

        tokens = self.tokenise(code)
        ast = self.parse(tokens)
        bf_code: list[str] = [
            self._compile_statement(stmt) for stmt in ast
        ]

        bf_code_str = self._optimise_brainfuck(''.join(bf_code))
        return "\n".join([bf_code_str[i:i + LINESIZE] for i in range(0, len(bf_code_str), LINESIZE)])
