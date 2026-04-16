class CrimscriptASTNode:
    """Base class for Crimscript AST (Abstract Syntax Tree) nodes."""
    pass

class Parser:
    """Converts Crimscript tokens into AST (Abstract Syntax Tree) nodes.
    The second stage. """

    def parse(self, code: str) -> list:
        ...  # TODO: transfer methods
