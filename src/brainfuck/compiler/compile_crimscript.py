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

    def compile_crimscript(self, src_code: list[str]) -> str:
        """Accepts a list of lines of Crimscript code and
        outputs the compiled Brainfuck code as a single string."""

        self.src_code = src_code  # used for error reporting

        tokens = self.lexer.tokenise(src_code)
        ast = self.parser.parse(tokens, code=src_code)
        self.validator.validate(ast)
        compiled_code = self.emitter.emit(ast)
        optimised_code = self.optimiser.optimise(compiled_code)

        return optimised_code
