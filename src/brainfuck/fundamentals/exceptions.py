class BrainfuckException(Exception):
    def __init__(self, message: str, position: int, code: str):
        super().__init__(message)
        self.message = message
        self.position = position
        self.code = code

class BFSyntaxError(BrainfuckException):
    """Exception raised for Brainfuck syntax errors."""
    pass

class BFSegmentationFault(BrainfuckException):
    """Exception raised for Brainfuck segmentation fault.
    Triggers if you attempt to access out-of-bounds memory."""
    pass
