# not using warnings.warn() due to need for custom formatting and the fact
# that these warnings are not meant to be ignored by default

class CompilerException(Exception):
    """Base class for compiler exceptions.
    These are fatal and will prevent forming the finished Brainfuck file.
    Punishable by an exit code of 1 and a message to stderr."""
    def __init__(self, msg: str, pos: int, src_code: list[str]):
        super().__init__(msg)
        self.msg = msg
        self.pos = pos
        self.code = src_code

class CompilerWarning(Warning):
    """Base class for compiler warnings.
    These are non-fatal and will not prevent forming the finished Brainfuck file,
    but indicate potential issues in the code that the user should be aware of.
    Should print a warning to stderr, but will not affect the exit code."""
    def __init__(self, msg: str, pos: int, code: list[str]):
        super().__init__(msg)
        self.msg = msg
        self.pos = pos
        self.code = code

class CompilerInternalError(Exception):
    """Base class for internal errors in the compiler.
    These are for "it's the compiler's fault",
    and do not inherit from CompilerException
    as they are not meant to be caught by `except CompilerException` blocks."""
    pass

class CompilerSyntaxError(CompilerException):
    """Raised when there is an error in the syntax of the Crimscript code."""
    pass

class CompilerSemanticError(CompilerException):
    """Raised for semantic errors.
    This is when the syntax is correct but will cause undefined
    behaviour or crashes at runtime."""
    pass

class CompilerTypeError(CompilerSemanticError):
    """Raised when passing an incorrect type in Crimscript code.

    e.g. `print(123)` <- 123 is an integer, not a string."""
    pass

class CompilerValueError(CompilerSemanticError):
    """Raised when a value is detected by the compiler that is of the correct
    type, but invalid.
    e.g. `until -1`, as Brainfuck values can only span 0..255,
    or passing non-ASCII characters into `print()`."""
    pass

class CompilerPtrError(CompilerSemanticError):
    """Base class for all pointer errors."""
    pass

class CompilerPtrOutOfBoundsError(CompilerPtrError):
    """Raised when the compiler detects a pattern that would push
    the pointer out of bounds and cause a segmentation fault."""
    pass

class CompilerPtrStabilityError(CompilerPtrError):
    """Raised when the compiler detects indeterminate pointer movement,
    which may cause a segmentation fault.

    This is caused when displacement of the data pointer
    inside a control structure is != 0 (i.e. number of `>` and `<` are unequal)
    """
    pass
