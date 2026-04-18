class BrainfuckException(Exception):
    def __init__(
            self, message: str, *, position: int, src_code: list[str],
            mem: list[int] | None = None, ptr: int | None = None
        ) -> None:
        # mem and ptr can be None, for example, for syntax errors
        # where the program didn't even start running.

        super().__init__(message)
        self.message = message
        self.position = position
        self.src_code = src_code
        self.mem = mem
        self.ptr = ptr

class BFSyntaxError(BrainfuckException):
    """Exception raised for Brainfuck syntax errors."""
    pass

class BFSegmentationFault(BrainfuckException):
    """Exception raised for Brainfuck segmentation fault.
    Triggers if you attempt to access out-of-bounds memory."""
    pass

class BFInterrupt(BrainfuckException):
    """Exception raised when the user interrupts the program with Ctrl-C."""
    pass
