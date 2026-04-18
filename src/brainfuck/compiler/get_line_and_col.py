def get_line_and_col(src_code: list[str], pos: int) -> tuple[int, int]:
    """Returns line and column of a position in the source code. Lines and columns are 1-indexed.
    and adjust for \\n being removed by splitlines()"""

    current_pos = 0

    for line_num, line_content in enumerate(src_code):
        line_len = len(line_content)

        # include newline that was removed by splitlines()
        # splitlines() makes sure that source code buffers
        # are stored as lists like ['line1', 'line2', etc.]
        # without the newlines
        total_len = line_len + 1  # for '\n'

        if current_pos <= pos < current_pos + total_len:
            col = pos - current_pos
            return line_num + 1, col + 1

        current_pos += total_len

    return len(src_code), 1
