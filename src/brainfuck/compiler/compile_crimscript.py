from dataclasses import dataclass

from .stages import (
    Lexer,
    Parser,
    Validator,
    Optimiser,
    Emitter
)
from .debug_info import DebugInfo

@dataclass
class CompilerOutput:
    bf_code: str
    debug: DebugInfo | None = None

class CrimscriptDriver:
    def __init__(self) -> None:
        self.lexer = Lexer()
        self.parser = Parser()
        self.validator = Validator()
        self.optimiser = Optimiser()
        self.emitter = Emitter()

    def compile_crimscript(self, src_code: list[str], debug_symbols: bool = False) -> CompilerOutput:
        """Accepts a list of lines of Crimscript code and
        outputs the compiled Brainfuck code and debug info.
        If debug_symbols is False, debug info is simply None."""

        self.src_code = src_code  # used for error reporting

        tokens = self.lexer.tokenise(src_code)
        ast = self.parser.parse(tokens, src_code=src_code)
        self.validator.validate(ast, src_code=src_code)
        compiled_code, debug_info = self.emitter.emit(ast, src_code=src_code, debug_symbols=debug_symbols)

        # TODO: reintegrate optimisation safely with debug info tracking
        # For now, skip optimisation when debug symbols are enabled
        if debug_symbols:
            return CompilerOutput(compiled_code, debug_info)
        else:
            optimised_code = self.optimiser.optimise(compiled_code)
            return CompilerOutput(optimised_code, debug_info)
