# not using warnings.warn() due to need for custom formatting and the fact
# that these warnings are not meant to be ignored by default

class CompilerException(Exception):
    """Base class for compiler exceptions.
    These are fatal and will prevent forming the finished Brainfuck file.
    Punishable by an exit code of 1 and a message to stderr."""
    def __init__(self, msg: str, pos: int, code: str):
        super().__init__(msg)
        self.msg = msg
        self.pos = pos
        self.code = code

class CompilerWarning(Warning):
    """Base class for compiler warnings.
    These are non-fatal and will not prevent forming the finished Brainfuck file,
    but indicate potential issues in the code that the user should be aware of.
    Should print a warning to stderr, but will not affect the exit code."""
    def __init__(self, msg: str, pos: int, code: str):
        super().__init__(msg)
        self.msg = msg
        self.pos = pos
        self.code = code

class CompilerSyntaxError(CompilerException):
    """Raised when there is an error in the syntax of the macrolang code."""
    pass

class CompilerTypeError(CompilerException):
    """Raised when there is a type error in the macrolang code."""
    pass

class CompilerMemoryError(CompilerException):
    """Raised when the compiler detects a guaranteed
    out-of-bounds memory access, which would cause a segmentation fault."""
    pass

class CompilerMemoryWarning(CompilerWarning):
    """Raised when the compiler detects a potential out-of-bounds memory access,
    but cannot guarantee it will take effect and cause a segmentation fault."""
    pass
