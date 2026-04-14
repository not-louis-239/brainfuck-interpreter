# generate an ascii lookup table
COL_PRINTABLE = "\033[92m"
COL_SPECIAL = "\033[94m"
COL_NON_PRINTABLE = "\033[91m"
COL_RESET = "\033[0m"

# underline included so that spaces are visible
UNDERLINE = "\033[4m"

SPECIAL_CASES: dict[int, str] = {
    0:  r"\0",   # Null
    7:  r"\a",   # Bell (alert)
    8:  r"\b",   # Backspace
    9:  r"\t",   # Horizontal tab
    10: r"\n",   # Line feed (newline)
    11: r"\v",   # Vertical tab
    12: r"\f",   # Form feed
    13: r"\r",   # Carriage return
    127: r"\x7f" # Delete
}

def show_ascii():
    for row_idx in range(16):
        for col_idx in range(8):
            char_idx = col_idx * 16 + row_idx

            if char_idx in SPECIAL_CASES:
                colour = UNDERLINE + COL_SPECIAL
                char = SPECIAL_CASES[char_idx]

            elif char_idx < 32 or char_idx == 127:
                colour = COL_NON_PRINTABLE
                char = f'\\x{char_idx:02x}'

            else:
                colour = UNDERLINE + COL_PRINTABLE
                char = chr(char_idx)

            print(f"{char_idx:3}: {colour}{char}{COL_RESET}{' ' * (4 - len(char))}", end='  ')
        print()

if __name__ == '__main__':
    show_ascii()
