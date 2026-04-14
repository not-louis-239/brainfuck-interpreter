import sys

from .exceptions import BFSegmentationFault, BFSyntaxError, BFInterrupt
from .keywords import BrainfuckKeywords

def validate_brainfuck(code: str) -> None:
    stack: list[int] = []

    for i, ch in enumerate(code):
        if ch == BrainfuckKeywords.LOOP_START:
            stack.append(i)

        elif ch == BrainfuckKeywords.LOOP_END:
            if not stack:
                # unmatched loop end
                raise BFSyntaxError(
                    f"unmatched '{BrainfuckKeywords.LOOP_END}'",
                    position=i, code=code
                )
            stack.pop()

    if stack:
        # leftover unmatched loop start
        i = stack[-1]
        raise BFSyntaxError(
            f"unmatched '{BrainfuckKeywords.LOOP_START}'",
            position=i, code=code
        )

def run_brainfuck(code: str, *, memsize: int, wrap: bool = False):
    membuf: list[int] = [0] * memsize
    pointer_idx = 0
    instruct_idx = 0
    prog_len = len(code)

    while instruct_idx < prog_len:
        char = code[instruct_idx]

        if char == BrainfuckKeywords.VAL_INC:
            membuf[pointer_idx] = (membuf[pointer_idx] + 1) % 256

        elif char == BrainfuckKeywords.VAL_DEC:
            membuf[pointer_idx] = (membuf[pointer_idx] - 1) % 256

        elif char == BrainfuckKeywords.PTR_INC:
            pointer_idx += 1
            if pointer_idx >= memsize:
                if wrap:
                    pointer_idx = 0
                else:
                    raise BFSegmentationFault(
                        f"access violation at far-right of memory",
                        position=instruct_idx, code=code
                    )

        elif char == BrainfuckKeywords.PTR_DEC:
            pointer_idx -= 1
            if pointer_idx < 0:
                if wrap:
                    pointer_idx = memsize - 1
                else:
                    raise BFSegmentationFault(
                        f"access violation at far-left of memory",
                        position=instruct_idx, code=code
                    )

        elif char == BrainfuckKeywords.STDOUT:
            print(chr(membuf[pointer_idx]), end='', flush=True)

        elif char == BrainfuckKeywords.STDIN:
            try:
                ch = sys.stdin.read(1)
            except KeyboardInterrupt:
                raise BFInterrupt(
                    "program interrupted by user",
                    position=instruct_idx, code=code
                )
            if ch:
                membuf[pointer_idx] = ord(ch) % 256
            else:
                membuf[pointer_idx] = 0

        elif char == BrainfuckKeywords.LOOP_START:
            # If the cell value is zero, jump forward to matching loop ender
            if membuf[pointer_idx] == 0:
                # jump forward to matching ]
                depth = 1
                while depth > 0:
                    instruct_idx += 1
                    if instruct_idx >= prog_len:
                        raise BFSyntaxError(
                            f"unmatched '{BrainfuckKeywords.LOOP_START}'",
                            position=instruct_idx, code=code
                        )
                    if code[instruct_idx] == BrainfuckKeywords.LOOP_START:
                        depth += 1
                    elif code[instruct_idx] == BrainfuckKeywords.LOOP_END:
                        depth -= 1

        elif char == BrainfuckKeywords.LOOP_END:
            # If cell value is non-zero, jump back to matching loop start
            if membuf[pointer_idx] != 0:
                depth = 1
                while depth > 0:
                    instruct_idx -= 1
                    if instruct_idx < 0:
                        raise BFSyntaxError(
                            f"unmatched '{BrainfuckKeywords.LOOP_END}'",
                            position=instruct_idx, code=code
                        )
                    if code[instruct_idx] == BrainfuckKeywords.LOOP_END:
                        depth += 1
                    elif code[instruct_idx] == BrainfuckKeywords.LOOP_START:
                        depth -= 1

        # Move forward to next instruction
        instruct_idx += 1
