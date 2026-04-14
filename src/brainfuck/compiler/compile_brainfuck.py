class CompilerException(Exception):
    """Base class for compiler exceptions."""
    pass

class CompilerSyntaxError(CompilerException):
    """Raised when there is an error in the syntax of the macrolang code."""
    pass

def compile_brainfuck(code: str) -> str:
    """Accepts a document of macrolang code and converts it to Brainfuck."""

    ...

