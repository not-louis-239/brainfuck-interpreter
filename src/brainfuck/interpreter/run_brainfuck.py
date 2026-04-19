import sys

from .exceptions import BFSegmentationFault, BFSyntaxError
from .keywords import BrainfuckKeywords

class BrainfuckInterpreter:
    def __init__(self):
        pass

    def validate_brainfuck(self) -> None:
        stack: list[int] = []

        src_code_str = "\n".join(self.src_code)
        for i, ch in enumerate(src_code_str):
            if ch == BrainfuckKeywords.LOOP_START:
                stack.append(i)

            elif ch == BrainfuckKeywords.LOOP_END:
                if not stack:
                    # unmatched loop end
                    raise BFSyntaxError(
                        f"unmatched '{BrainfuckKeywords.LOOP_END}'",
                        position=i, src_code=self.src_code, mem=None, ptr=None
                    )
                stack.pop()

        if stack:
            # leftover unmatched loop start
            i = stack[-1]
            raise BFSyntaxError(
                f"unmatched '{BrainfuckKeywords.LOOP_START}'",
                position=i, src_code=self.src_code, mem=None, ptr=None
            )

    def execute_brainfuck(self, *, memsize: int = 30_000, wrap: bool = False):
        self.ist = 0
        self.ptr = 0
        self.mem: list[int] = [0] * memsize

        src_code_str: str = "\n".join(self.src_code)
        prog_len = len(src_code_str)

        while self.ist < prog_len:
            char = src_code_str[self.ist]

            if char == BrainfuckKeywords.VAL_INC:
                self.mem[self.ptr] = (self.mem[self.ptr] + 1) % 256

            elif char == BrainfuckKeywords.VAL_DEC:
                self.mem[self.ptr] = (self.mem[self.ptr] - 1) % 256

            elif char == BrainfuckKeywords.PTR_INC:
                self.ptr += 1
                if self.ptr >= memsize:
                    if wrap:
                        self.ptr = 0
                    else:
                        raise BFSegmentationFault(
                            f"access violation: pointer moved right of cell {memsize - 1}",
                            position=self.ist, src_code=self.src_code, mem=self.mem, ptr=self.ptr
                        )

            elif char == BrainfuckKeywords.PTR_DEC:
                self.ptr -= 1
                if self.ptr < 0:
                    if wrap:
                        self.ptr = memsize - 1
                    else:
                        raise BFSegmentationFault(
                            "access violation: pointer moved left of cell 0",
                            position=self.ist, src_code=self.src_code, mem=self.mem, ptr=self.ptr
                        )

            elif char == BrainfuckKeywords.STDOUT:
                print(chr(self.mem[self.ptr]), end='', flush=True)

            elif char == BrainfuckKeywords.STDIN:
                ch = sys.stdin.read(1)

                if ch:
                    self.mem[self.ptr] = ord(ch) % 256
                else:
                    self.mem[self.ptr] = 0

            elif char == BrainfuckKeywords.LOOP_START:
                # If the cell value is zero, jump forward to matching loop ender
                if self.mem[self.ptr] == 0:
                    # jump forward to matching ]
                    depth = 1
                    while depth > 0:
                        self.ist += 1
                        if self.ist >= prog_len:
                            raise BFSyntaxError(
                                f"unmatched '{BrainfuckKeywords.LOOP_START}'",
                                position=self.ist, src_code=self.src_code, mem=self.mem, ptr=self.ptr
                            )
                        if src_code_str[self.ist] == BrainfuckKeywords.LOOP_START:
                            depth += 1
                        elif src_code_str[self.ist] == BrainfuckKeywords.LOOP_END:
                            depth -= 1

            elif char == BrainfuckKeywords.LOOP_END:
                # If cell value is non-zero, jump back to matching loop start
                if self.mem[self.ptr] != 0:
                    depth = 1
                    while depth > 0:
                        self.ist -= 1
                        if self.ist < 0:
                            raise BFSyntaxError(
                                f"unmatched '{BrainfuckKeywords.LOOP_END}'",
                                position=self.ist, src_code=self.src_code, mem=self.mem, ptr=self.ptr
                            )
                        if src_code_str[self.ist] == BrainfuckKeywords.LOOP_END:
                            depth += 1
                        elif src_code_str[self.ist] == BrainfuckKeywords.LOOP_START:
                            depth -= 1

            # Move forward to next instruction
            self.ist += 1

    def run_brainfuck(self, src_code: list[str], *, memsize: int = 30_000, wrap: bool = False) -> None:
        self.src_code = src_code
        self.validate_brainfuck()
        self.execute_brainfuck(memsize=memsize, wrap=wrap)
