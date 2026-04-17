from ..exceptions import (
    CompilerValueError,
    CompilerTypeError,
    CompilerPtrStabilityError,
    CompilerPtrOutOfBoundsError
)
from ..ast.nodes import ASTNode, AbstractSyntaxTree

class Validator:
    """Validates a Crimscript AST to catch errors such as potential
    segfaults, value errors or type errors."""

    def __init__(self) -> None:
        pass

    def _check_ptr_deltas(self, ast: AbstractSyntaxTree) -> None:
        """Checks pointer deltas for potential segmentation faults caused
        by an out-of-bounds pointer. Throws errors if it finds a liability."""
        pass  # TODO: rest of implementation

    def _check_types_and_vals(self, ast: AbstractSyntaxTree) -> None:
        """Checks the types and values, e.g. of macro arguments.
        If it finds an invalid type or value, throws errors."""
        pass  # TODO: rest of implementation

    def validate(self, ast: AbstractSyntaxTree) -> None:
        """Validates the AST (WITHOUT MODIFYING IT).
        If a check breaks, throws an error."""
        for check in (
            self._check_ptr_deltas,
            self._check_types_and_vals
        ):
            check(ast)
