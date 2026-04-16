from ..utils.format_tools import COL_RESET, COL_ERR, COL_ERR_HIGHLIGHT, COL_WARN, COL_WARN_HIGHLIGHT
from ..utils.line_and_col import get_line_and_col
from .exceptions import (
    CompilerException,
    CompilerWarning,
    CompilerSyntaxError,
    CompilerSemanticError,
    CompilerTypeError,
    CompilerValueError,
    CompilerPtrStabilityError,
    CompilerPtrOutOfBoundsError
)

ERR_NAMES: dict[type[CompilerException] | type[CompilerWarning], str] = {
    CompilerException: "error",
    CompilerWarning: "warning",
    CompilerSyntaxError: "syntax error",
    CompilerSemanticError: "semantic error",
    CompilerTypeError: "type error",
    CompilerValueError: "value error",
    CompilerPtrStabilityError: "pointer stability error",
    CompilerPtrOutOfBoundsError: "pointer out of bounds error"
}

def format_err(err: CompilerException) -> str:
    err_name = ERR_NAMES.get(type(err), "error")
    line, col = get_line_and_col(err.code, err.pos)

    return (
        f"brainfuck: {COL_ERR_HIGHLIGHT}{err_name}{COL_RESET}: {COL_ERR}{err.msg}{COL_RESET}\n"
        f"  at line {line}, column {col}\n"
        f"  (at instruction {err.pos})\n\n"
        f"{COL_ERR_HIGHLIGHT}{err.code.splitlines()[line - 1]}{COL_RESET}\n"
        f"{COL_ERR_HIGHLIGHT}{' ' * (col - 1) + '^'}{COL_RESET}"
    )

def format_warn(warn: CompilerWarning) -> str:
    warn_name = ERR_NAMES.get(type(warn), "warning")
    line, col = get_line_and_col(warn.code, warn.pos)
    return (
        f"brainfuck: {COL_WARN_HIGHLIGHT}{warn_name}{COL_RESET}: {COL_WARN}{warn.msg}{COL_RESET}\n"
        f"  at line {line}, column {col}\n"
        f"  (at instruction {warn.pos})\n\n"
        f"{COL_WARN_HIGHLIGHT}{warn.code.splitlines()[line - 1]}{COL_RESET}\n"
        f"{COL_WARN_HIGHLIGHT}{' ' * (col - 1) + '^'}{COL_RESET}"
    )
