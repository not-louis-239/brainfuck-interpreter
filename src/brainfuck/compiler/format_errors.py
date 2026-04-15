from .exceptions import CompilerException, CompilerWarning

def format_err(err: CompilerException) -> str:
    ...

def format_warn(warn: CompilerWarning) -> str:
    ...
