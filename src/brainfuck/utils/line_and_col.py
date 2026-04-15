def get_line_and_col(code: str, pos: int) -> tuple[int, int]:
    line = code.count('\n', 0, pos) + 1
    col = pos - code.rfind('\n', 0, pos)
    return line, col
