def get_line_and_col(code: str, pos: int) -> tuple[int, int]:
    """Accepts a source code document as a string, and a character position
    as an integer displacement from the start of the file, and returns
    (line number, column number)."""

    line = code.count('\n', 0, pos) + 1
    col = pos - code.rfind('\n', 0, pos)
    return line, col
