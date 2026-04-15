from enum import StrEnum
import sys

from .exceptions import BFSegmentationFault, BFSyntaxError, BFInterrupt
from .keywords import BrainfuckKeywords

class BFBytecodeType(StrEnum):
    VAL_CHANGE = 'VAL_CHANGE'
    PTR_CHANGE = 'PTR_CHANGE'
    STDOUT = 'STDOUT'
    STDIN = 'STDIN'
    LOOP_START = 'LOOP_START'
    LOOP_END = 'LOOP_END'

class BFBytecodeToken:
    def __init__(self, typ: BFBytecodeType, val: int | None = None) -> None:
        self.typ = typ
        self.val = val

def convert_bf_to_bytecode(code: str) -> list[BFBytecodeToken]:
    """Converts Brainfuck source to optimized bytecode tokens,
    condensing chained operators into single tokens."""
    bytecode: list[BFBytecodeToken] = []
    ist = 0
    code_len = len(code)

    while ist < code_len:
        char = code[ist]

        # Value changes
        if char in (BrainfuckKeywords.VAL_INC, BrainfuckKeywords.VAL_DEC):
            chain_value = 0
            while ist < code_len and code[ist] in (BrainfuckKeywords.VAL_INC, BrainfuckKeywords.VAL_DEC):
                chain_value += 1 if code[ist] == BrainfuckKeywords.VAL_INC else -1
                ist += 1
            if chain_value != 0:
                chain_value = (chain_value + 128) % 256 - 128
                bytecode.append(BFBytecodeToken(BFBytecodeType.VAL_CHANGE, chain_value))
            continue # Skip the ist += 1 at the bottom because the inner loop advanced it

        # Pointer changes
        elif char in (BrainfuckKeywords.PTR_INC, BrainfuckKeywords.PTR_DEC):
            chain_value = 0
            while ist < code_len and code[ist] in (BrainfuckKeywords.PTR_INC, BrainfuckKeywords.PTR_DEC):
                chain_value += 1 if code[ist] == BrainfuckKeywords.PTR_INC else -1
                ist += 1
            if chain_value != 0:
                chain_value = (chain_value + 128) % 256 - 128
                bytecode.append(BFBytecodeToken(BFBytecodeType.PTR_CHANGE, chain_value))
            continue

        # Static tokens
        elif char == BrainfuckKeywords.STDOUT:
            bytecode.append(BFBytecodeToken(BFBytecodeType.STDOUT))
        elif char == BrainfuckKeywords.STDIN:
            bytecode.append(BFBytecodeToken(BFBytecodeType.STDIN))
        elif char == BrainfuckKeywords.LOOP_START:
            bytecode.append(BFBytecodeToken(BFBytecodeType.LOOP_START))
        elif char == BrainfuckKeywords.LOOP_END:
            bytecode.append(BFBytecodeToken(BFBytecodeType.LOOP_END))

        ist += 1

    return bytecode

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
    mem: list[int] = [0] * memsize
    ptr = 0
    ist = 0
    prog_len = len(code)

    while ist < prog_len:
        char = code[ist]

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
                        position=ist, code=code
                    )

        elif char == BrainfuckKeywords.PTR_DEC:
            ptr -= 1
            if ptr < 0:
                if wrap:
                    ptr = memsize - 1
                else:
                    raise BFSegmentationFault(
                        f"access violation at far-left of memory",
                        position=ist, code=code
                    )

        elif char == BrainfuckKeywords.STDOUT:
            print(chr(mem[ptr]), end='', flush=True)

        elif char == BrainfuckKeywords.STDIN:
            try:
                ch = sys.stdin.read(1)
            except KeyboardInterrupt:
                raise BFInterrupt(
                    "program interrupted by user",
                    position=ist, code=code
                )
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
                            position=ist, code=code
                        )
                    if code[ist] == BrainfuckKeywords.LOOP_START:
                        depth += 1
                    elif code[ist] == BrainfuckKeywords.LOOP_END:
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
                            position=ist, code=code
                        )
                    if code[ist] == BrainfuckKeywords.LOOP_END:
                        depth += 1
                    elif code[ist] == BrainfuckKeywords.LOOP_START:
                        depth -= 1

        # Move forward to next instruction
        ist += 1
