class BrainfuckException(Exception):
    """Base exception class for Brainfuck exceptions."""
    pass

class BFSyntaxError(BrainfuckException):
    """Exception raised for Brainfuck syntax errors."""
    pass

class BFSegmentationFault(BrainfuckException):
    """Exception raised for Brainfuck segmentation fault.
    Triggers if you attempt to access out-of-bounds memory."""
    pass
