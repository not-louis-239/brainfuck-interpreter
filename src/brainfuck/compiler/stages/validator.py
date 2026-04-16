from ..exceptions import (
    CompilerValueError,
    CompilerTypeError,
    CompilerPtrStabilityError,
    CompilerPtrOutOfBoundsError
)

class Validator:
    """Validates Crimscript source code to catch errors such as potential
    segfaults, value errors or type errors."""

    def __init__(self) -> None:
        pass

    def _check_ptr_deltas(self, code) -> None:
        """Checks pointer deltas for potential segmentation faults caused
        by an out-of-bounds pointer. Throws errors if it finds a liability."""
        ...  # TODO: rest of implementation

    def _check_types_and_vals(self, code) -> None:
        """Checks the types and values, e.g. of macro arguments.
        If it finds an invalid type or value, throws errors."""
        ...  # TODO: rest of implementation

    def validate(self, code):
        ...  # TODO: split/transfer methods as required
