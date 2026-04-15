import warnings as _w
from typing import NoReturn

class CompilerException(Exception):
    """Base class for compiler exceptions."""
    pass

class CompilerWarning(Warning):
    """Base class for compiler warnings."""
    pass

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

def compiler_err(msg: str, typ: type[CompilerException]) -> NoReturn:
    raise typ(msg)

def compiler_warn(msg: str, typ: type[CompilerWarning]) -> None:
    _w.warn(msg, typ)
