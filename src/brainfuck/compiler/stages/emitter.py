import sys

class Emitter:
    """Emits Brainfuck source code to a file. The final stage."""

    def __init__(self) -> None:
        pass

    def emit(self, code: str, file = sys.stdout):
        print(code, file=file)
