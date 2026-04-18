import sys

from .exceptions import BFSegmentationFault, BFSyntaxError, BFInterrupt
from .keywords import BrainfuckKeywords

def validate_brainfuck(src_code: list[str]) -> None:
    stack: list[int] = []

    src_code_str = "\n".join(src_code)
    for i, ch in enumerate(src_code_str):
        if ch == BrainfuckKeywords.LOOP_START:
            stack.append(i)

        elif ch == BrainfuckKeywords.LOOP_END:
            if not stack:
                # unmatched loop end
                raise BFSyntaxError(
                    f"unmatched '{BrainfuckKeywords.LOOP_END}'",
                    position=i, src_code=src_code, mem=None
                )
            stack.pop()

    if stack:
        # leftover unmatched loop start
        i = stack[-1]
        raise BFSyntaxError(
            f"unmatched '{BrainfuckKeywords.LOOP_START}'",
            position=i, src_code=src_code, mem=None
        )

# used to allow transmitting info from the function
# globals are usually bad practice and someday
# I want to find a better solution but this will have
# to do for now

# this is used for error reporting in KeyboardInterrupt
# scenarios where somehow it doesn't get caught
# by run_brainfuck's try-except for some reason??
# Note to self: DO NOT USE THIS VARIABLE, OK?!
_ist = 0

def run_brainfuck(src_code: list[str], *, memsize: int = 30_000, wrap: bool = False):
    ist = 0
    ptr = 0
    mem: list[int] = [0] * memsize

    src_code_str: str = "\n".join(src_code)
    prog_len = len(src_code_str)

    try:


        while ist < prog_len:
            global _ist
            _ist = ist

            char = src_code_str[ist]

            if char == BrainfuckKeywords.VAL_INC:
                mem[ptr] = (mem[ptr] + 1) % 256

            elif char == BrainfuckKeywords.VAL_DEC:
                mem[ptr] = (mem[ptr] - 1) % 256

            elif char == BrainfuckKeywords.PTR_INC:
                ptr += 1
                if ptr >= memsize:
                    if wrap:
                        ptr = 0
                    else:
                        raise BFSegmentationFault(
                            f"access violation at far-right of memory",
                            position=ist, src_code=src_code, mem=mem
                        )

            elif char == BrainfuckKeywords.PTR_DEC:
                ptr -= 1
                if ptr < 0:
                    if wrap:
                        ptr = memsize - 1
                    else:
                        raise BFSegmentationFault(
                            f"access violation at far-left of memory",
                            position=ist, src_code=src_code, mem=mem
                        )

            elif char == BrainfuckKeywords.STDOUT:
                print(chr(mem[ptr]), end='', flush=True)

            elif char == BrainfuckKeywords.STDIN:
                ch = sys.stdin.read(1)

                if ch:
                    mem[ptr] = ord(ch) % 256
                else:
                    mem[ptr] = 0

            elif char == BrainfuckKeywords.LOOP_START:
                # If the cell value is zero, jump forward to matching loop ender
                if mem[ptr] == 0:
                    # jump forward to matching ]
                    depth = 1
                    while depth > 0:
                        ist += 1
                        if ist >= prog_len:
                            raise BFSyntaxError(
                                f"unmatched '{BrainfuckKeywords.LOOP_START}'",
                                position=ist, src_code=src_code, mem=mem
                            )
                        if src_code_str[ist] == BrainfuckKeywords.LOOP_START:
                            depth += 1
                        elif src_code_str[ist] == BrainfuckKeywords.LOOP_END:
                            depth -= 1

            elif char == BrainfuckKeywords.LOOP_END:
                # If cell value is non-zero, jump back to matching loop start
                if mem[ptr] != 0:
                    depth = 1
                    while depth > 0:
                        ist -= 1
                        if ist < 0:
                            raise BFSyntaxError(
                                f"unmatched '{BrainfuckKeywords.LOOP_END}'",
                                position=ist, src_code=src_code, mem=mem
                            )
                        if src_code_str[ist] == BrainfuckKeywords.LOOP_END:
                            depth += 1
                        elif src_code_str[ist] == BrainfuckKeywords.LOOP_START:
                            depth -= 1

            # Move forward to next instruction
            ist += 1

    except KeyboardInterrupt:
        raise BFInterrupt(
            "program interrupted by user",
            position=ist, src_code=src_code, mem=mem
        )
