import sys
from typing import TYPE_CHECKING

from ..utils.format_tools import (
    COL_ERR,
    COL_ERR_HIGHLIGHT,
    COL_RESET,
    COL_WARN,
    COL_WARN_HIGHLIGHT,
)
from .exceptions import (
    CompilerDepthError,
    CompilerException,
    CompilerPtrOutOfBoundsWarning,
    CompilerPtrStabilityWarning,
    CompilerPtrWarning,
    CompilerSemanticError,
    CompilerSemanticWarning,
    CompilerSyntaxError,
    CompilerTypeError,
    CompilerValueError,
    CompilerWarning,
)
from .get_line_and_col import get_line_and_col

if TYPE_CHECKING:
    from brainfuck.compiler.stages.validator import Validator

ERR_NAMES: dict[type[CompilerException] | type[CompilerWarning], str] = {
    CompilerException: "error",
    CompilerWarning: "warning",
    CompilerSyntaxError: "syntax error",
    CompilerSemanticError: "semantic error",
    CompilerSemanticWarning: "semantic warning",
    CompilerTypeError: "invalid argument type",
    CompilerValueError: "invalid argument value",
    CompilerPtrWarning: "pointer warning",
    CompilerPtrStabilityWarning: "pointer stability warning",
    CompilerPtrOutOfBoundsWarning: "pointer out of bounds warning",
    CompilerDepthError: "depth error"
}

def format_err(err: CompilerException) -> str:
    err_name = ERR_NAMES.get(type(err), "error")
    line, col = get_line_and_col(err.code, err.pos)

    return (
        f"crimpile: {COL_ERR_HIGHLIGHT}{err_name}{COL_RESET}: {COL_ERR}{err.msg}{COL_RESET}\n"
        f"  at line {line}, column {col}\n"
        f"  (at instruction {err.pos})\n\n"
        f"{COL_ERR_HIGHLIGHT}{err.code[line - 1]}{COL_RESET}\n"
        f"{COL_ERR_HIGHLIGHT}{' ' * (col - 1) + '^'}{COL_RESET}"
    )

def format_warn(warn: CompilerWarning) -> str:
    warn_name = ERR_NAMES.get(type(warn), "warning")
    line, col = get_line_and_col(warn.code, warn.pos)
    return (
        f"crimpile: {COL_WARN_HIGHLIGHT}{warn_name}{COL_RESET}: {COL_WARN}{warn.msg}{COL_RESET}\n"
        f"  at line {line}, column {col}\n"
        f"  (at instruction {warn.pos})\n\n"
        f"{COL_WARN_HIGHLIGHT}{warn.code[line - 1]}{COL_RESET}\n"
        f"{COL_WARN_HIGHLIGHT}{' ' * (col - 1) + '^'}{COL_RESET}"
    )

def compiler_warn(
        msg: str, pos: int, src_code: list[str],
        typ: type[CompilerWarning], validator: Validator
    ) -> None:
    """Formats and prints a compiler warning to stderr without crashing the compiler."""
    warn = typ(msg=msg, pos=pos, code=src_code)
    print(format_warn(warn), file=sys.stderr)
    validator.num_warnings_found += 1
