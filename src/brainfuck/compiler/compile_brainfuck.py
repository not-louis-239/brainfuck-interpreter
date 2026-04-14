from .exceptions import (
    CompilerException,
    CompilerSyntaxError,
    CompilerMemoryError,
    CompilerWarning,
    compiler_err,
    compiler_warn
)

import re
from enum import StrEnum

class CrimTokenType(StrEnum):
    VAL_INC = '+'
    VAL_DEC = '-'
    PTR_INC = '>'
    PTR_DEC = '<'
    PRINT = 'print'
    INPUT = 'input'
    LOOP_START = 'loop_start'
    LOOP_END = 'loop_end'

class CrimToken:
    def __init__(self, type: CrimTokenType, value: str | None = None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"CrimToken(type={self.type}, value={self.value})"

class CrimscriptCompiler:
    def __init__(self):
        # Initialize any necessary data structures or state here
        pass

    def tokenise(self, code: list[str]) -> list[CrimToken]:
        """
        Tokenises the input Crimscript code into a list of CrimTokens.
        Each line of code is processed to identify valid commands and their arguments.
        """

        tokens = []

        # TODO
        # ... rest of implementation ...

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
        bf_code: list[str] = []

        # TODO
        # ... rest of implementation ...

        return "".join(bf_code)
