from ..compiler.get_line_and_col import get_line_and_col
from ..utils.format_tools import COL_ERR, COL_ERR_HIGHLIGHT, COL_RESET
from .exceptions import (
    BFInterrupt,
    BFSegmentationFault,
    BFSyntaxError,
    BrainfuckException,
)

ERROR_NAMES: dict[type[BrainfuckException], str] = {
    BrainfuckException: "error",
    BFSegmentationFault: "segmentation fault",
    BFSyntaxError: "syntax error",
    BFInterrupt: "interrupted by user",
}

def format_bf_traceback(exc: BrainfuckException) -> str:
    line, col = get_line_and_col(exc.src_code, exc.position)
    src_line = exc.src_code[line - 1] if line - 1 < len(exc.src_code) else ""

    assert not src_line.endswith("\n"), (
        "Line should not end with newline character. Source code buffers are stored without trailing newlines.\n"
        "Please use .splitlines() to ensure source code is stored as ['line 1', 'line 2', ...], not ['line 1\\n', 'line 2\\n', ...]"
    )

    # trim line length
    if len(src_line) > 100:
        src_line = src_line[:100] + "..."

    if col > 100:
        pointer = "(pointer far right)"
    else:
        pointer = " " * (col - 1) + "^"

    src_line_before = f"{COL_ERR}{src_line[:col - 1]}"

    if col - 1 < len(src_line):
        src_line_highlight = f"{COL_ERR_HIGHLIGHT}{src_line[col - 1]}"
    else:
        src_line_highlight = ""

    src_line_after = f"{COL_RESET}{COL_ERR}{src_line[col:]}{COL_RESET}"

    return (
        f"brainfuck: {COL_ERR_HIGHLIGHT}{ERROR_NAMES.get(type(exc), 'error')}{COL_RESET}: {COL_ERR}{exc.message}{COL_RESET}\n"
        f"  at line {line}, column {col}\n"
        f"  (at instruction {exc.position:,})\n\n"

        f"{src_line_before}{src_line_highlight}{src_line_after}\n"
        f"{COL_ERR_HIGHLIGHT}{pointer}{COL_RESET}"
    )
