from dataclasses import dataclass

from ..exceptions import (
    CompilerInternalError,
    CompilerValueError,
    CompilerPtrStabilityWarning,
    CompilerPtrOutOfBoundsWarning,
    compiler_warn
)

from ..ast import nodes
from ..ast.nodes import ASTNode, AbstractSyntaxTree

@dataclass
class PtrSummary:
    s_net: int
    s_min: int
    s_max: int

MEMORY_LIMIT_LEFT = 0
MEMORY_LIMIT_RIGHT = 30_000

def char_is_invalid(c: str) -> bool:
    return ord(c) > 255

class Validator:
    """Validates a Crimscript AST to catch errors such as potential
    segfaults."""

    def __init__(self) -> None:
        pass

    def _walk_node_ptr_deltas(self, node: ASTNode) -> PtrSummary:
        """Walks through an AST node and checks pointer deltas."""
        match node:
            # No pointer changes (safe)
            case (
                nodes.ValueChange()
                | nodes.PrintStmt()
                | nodes.InputStmt()
                | nodes.ClearStmt()
                | nodes.SetStmt()
            ):
                return PtrSummary(0, 0, 0)

            # Pointer changes (potentially dangerous)
            # We set s_min and s_max to min(*) and max(*) to reflect the "journey" taken by the pointer.
            case nodes.PointerChange(distance=d):
                return PtrSummary(
                    s_net=d,
                    s_min=min(0, d),
                    s_max=max(0, d),
                )

            # Control structures (potentially dangerous, must be checked recursively)
            case nodes.UntilStmt(body=body):
                body_sum = self._walk_ptr_deltas(body)
                if (bad_sum := body_sum.s_net) != 0:
                    assert node.metadata is not None
                    compiler_warn(
                        f"Potential segmentation fault detected: non-zero ptr change inside control structure (total_delta = {bad_sum})",
                        pos=node.metadata.pos,
                        src_code=self.src_code,
                        typ=CompilerPtrStabilityWarning
                    )
                return body_sum

            # Move statements (potentially dangerous)
            case nodes.MoveStmt(delta_ptr_min=delta_ptr_min, delta_ptr_max=delta_ptr_max):
                return PtrSummary(
                    s_net=0,
                    s_min=min(0, delta_ptr_min, delta_ptr_max),
                    s_max=max(0, delta_ptr_min, delta_ptr_max),
                )

            # Copy statements (potentially dangerous)
            case nodes.CopyStmt(
                delta_ptr_min=delta_ptr_min,
                delta_ptr_max=delta_ptr_max,
                delta_ptr_tmp=delta_ptr_tmp,
            ):
                return PtrSummary(
                    s_net=0,
                    s_min=min(0, delta_ptr_min, delta_ptr_max, delta_ptr_tmp),
                    s_max=max(0, delta_ptr_min, delta_ptr_max, delta_ptr_tmp),
                )

            # Statements with no protocol for summarising pointer deltas
            case _:
                raise CompilerInternalError(
                    f"Validator cannot analyse pointer deltas for node type {type(node).__name__}"
                )

    def _walk_ptr_deltas(self, ast: AbstractSyntaxTree) -> PtrSummary:
        """Walks through an AST and collects all pointer deltas."""
        s_cur = 0
        s_min = 0
        s_max = 0

        for node in ast:
            child = self._walk_node_ptr_deltas(node)
            child_min = s_cur + child.s_min
            child_max = s_cur + child.s_max

            if child_min < s_min:
                s_min = child_min

            if child_max > s_max:
                s_max = child_max

            s_cur += child.s_net

        return PtrSummary(
            s_net=s_cur,
            s_min=s_min,
            s_max=s_max,
        )

    def _find_bounds_violation_pos(self, ast: AbstractSyntaxTree, s_cur: int = 0) -> int:
        """Return the position of the first node that pushes the simulated pointer out of bounds."""

        for node in ast:
            child = self._walk_node_ptr_deltas(node)

            if s_cur + child.s_min < MEMORY_LIMIT_LEFT:
                if isinstance(node, nodes.UntilStmt):
                    return self._find_bounds_violation_pos(node.body, s_cur=s_cur)
                assert node.metadata is not None
                return node.metadata.pos

            if s_cur + child.s_max >= MEMORY_LIMIT_RIGHT:
                if isinstance(node, nodes.UntilStmt):
                    return self._find_bounds_violation_pos(node.body, s_cur=s_cur)
                assert node.metadata is not None
                return node.metadata.pos

            s_cur += child.s_net

        return 0

    def _check_ptr_deltas(self, ast: AbstractSyntaxTree) -> None:
        """Checks pointer deltas for potential segmentation faults caused
        by an out-of-bounds pointer. Throws errors if it finds a liability."""

        # create an imaginary pointer for simulation
        s = self._walk_ptr_deltas(ast)
        violation_pos = self._find_bounds_violation_pos(ast)

        if s.s_min < MEMORY_LIMIT_LEFT:
            compiler_warn(
                "Potential segmentation fault detected: access violation to far-left of memory",
                pos=violation_pos,
                src_code=self.src_code,
                typ=CompilerPtrOutOfBoundsWarning
            )
        elif s.s_max >= MEMORY_LIMIT_RIGHT:
            compiler_warn(
                "Potential segmentation fault detected: access violation to far-right of memory",
                pos=violation_pos,
                src_code=self.src_code,
                typ=CompilerPtrOutOfBoundsWarning
            )

    def _check_types_and_vals(self, ast: AbstractSyntaxTree) -> None:
        """Checks that all types and values in the AST are valid. Throws errors if it finds an invalid type or value."""

        # Only check types and values for nodes that the parser can't check.
        # The parser can usually check types using isinstance() or >/==/<,
        # but can't differentiate between say, mv where the src cell is
        # inside the casting range, which would explode at runtime.

        for node in ast:
            match node:
                # Check move statements and copy statements so that:
                # - src is not inside the dest range
                # - src isn't used as the tmp cell (for copy statements)
                # - tmp is not inside the dest range (for copy statements)
                # Any of these would break the program at runtime.
                case nodes.CopyStmt(delta_ptr_min=delta_ptr_min, delta_ptr_max=delta_ptr_max, delta_ptr_tmp=delta_ptr_tmp):
                    # src can't be used as the tmp cell
                    if delta_ptr_tmp == 0:
                        assert node.metadata is not None
                        raise CompilerValueError(
                            f"Invalid CopyStmt: src cell cannot be used as the tmp cell",
                            pos=node.metadata.pos,
                            src_code=self.src_code
                        )

                    # src can't be inside dest range
                    if delta_ptr_min <= 0 <= delta_ptr_max:
                        assert node.metadata is not None
                        raise CompilerValueError(
                            f"Invalid CopyStmt: src cell cannot be inside the destination range",
                            pos=node.metadata.pos,
                            src_code=self.src_code
                        )

                    # tmp can't be inside dest range
                    if delta_ptr_min <= delta_ptr_tmp <= delta_ptr_max:
                        assert node.metadata is not None
                        raise CompilerValueError(
                            f"Invalid CopyStmt: tmp cell cannot be inside the destination range",
                            pos=node.metadata.pos,
                            src_code=self.src_code
                        )

                case nodes.MoveStmt(delta_ptr_min=delta_ptr_min, delta_ptr_max=delta_ptr_max):
                    # src can't be inside the dest range
                    if delta_ptr_min <= 0 <= delta_ptr_max:
                        assert node.metadata is not None
                        raise CompilerValueError(
                            f"Invalid MoveStmt: src cell cannot be inside the destination range",
                            pos=node.metadata.pos,
                            src_code=self.src_code
                        )

                    # No checks for tmp as MoveStmt doesn't have a tmp cell;
                    # as it destroys the src cell.

                # Recursively check until statements for type and value errors.
                case nodes.UntilStmt(target=target):
                    if not 0 <= target <= 255:
                        assert node.metadata is not None
                        raise CompilerValueError(
                            f"Invalid target value for UntilStmt: {target} (must be between 0 and 255 inclusive)",
                            pos=node.metadata.pos,
                            src_code=self.src_code
                        )

                    # Recursively check the body of the UntilStmt for type and value errors.
                    # If the user uses 1,000 loops, this would raise a RecursionError,
                    # but I don't expect anyone to go that far.

                    # If they do, they deserve the RecursionError.
                    # Who the f*ck needs 1,000 loops in Brainfuck anyway?

                    self._check_types_and_vals(node.body)

                case nodes.SetStmt(value=value):
                    if not 0 <= value <= 255:
                        assert node.metadata is not None
                        raise CompilerValueError(
                            f"Invalid value for SetStmt: {value} (must be between 0 and 255 inclusive)",
                            pos=node.metadata.pos,
                            src_code=self.src_code
                        )

                # Print and input statements cannot contain non-ASCII characters
                case nodes.PrintStmt(text=text):
                    if text is not None and any(char_is_invalid(c) for c in text):
                        assert node.metadata is not None
                        raise CompilerValueError(
                            f"Invalid text for PrintStmt: cannot print characters where ord(character) > 255",
                            pos=node.metadata.pos,
                            src_code=self.src_code
                        )

                case nodes.InputStmt(prompt=prompt):
                    if prompt is not None and any(char_is_invalid(c) for c in prompt):
                        assert node.metadata is not None
                        raise CompilerValueError(
                            f"Invalid prompt for InputStmt: cannot contain characters where ord(character) > 255",
                            pos=node.metadata.pos,
                            src_code=self.src_code
                        )

                # Nodes that don't have values to validate
                case _:
                    pass

    def validate(self, ast: AbstractSyntaxTree, src_code: list[str]) -> None:
        """Validates the AST (WITHOUT MODIFYING IT).
        If a check breaks, throws an error.
        Requires src_code for error reporting."""
        self.src_code = src_code

        for check in (
            self._check_ptr_deltas,
            self._check_types_and_vals
        ):
            check(ast)
