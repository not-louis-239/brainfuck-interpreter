from .stages import (
    Lexer,
    Parser,
    Validator,
    Optimiser,
    Emitter
)

class CrimscriptDriver:
    def __init__(self) -> None:
        self.lexer = Lexer()
        self.parser = Parser()
        self.validator = Validator()
        self.optimiser = Optimiser()
        self.emitter = Emitter()

    def compile_crimscript(self, src_code: str) -> str:
        ...
