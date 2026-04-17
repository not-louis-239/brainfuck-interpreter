from dataclasses import dataclass

from ..exceptions import (
    CompilerInternalError,
    CompilerPtrStabilityError,
    CompilerPtrOutOfBoundsError
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
                    raise CompilerPtrStabilityError(
                        f"Potential segmentation fault detected: non-zero ptr change inside control structure: {bad_sum}",
                        pos=node.metadata.pos,
                        src_code=self.src_code
                    )
                return PtrSummary(
                    s_net=0,
                    s_min=body_sum.s_min,
                    s_max=body_sum.s_max,
                )

            # Move statements (potentially dangerous)
            case nodes.MoveStmt(delta_ptr_min=delta_ptr_min, delta_ptr_max=delta_ptr_max):
                lower = min(0, delta_ptr_min, delta_ptr_max)
                upper = max(0, delta_ptr_min, delta_ptr_max)
                return PtrSummary(
                    s_net=delta_ptr_max,
                    s_min=lower,
                    s_max=upper,
                )

            # Copy statements (potentially dangerous)
            case nodes.CopyStmt(
                delta_ptr_min=delta_ptr_min,
                delta_ptr_max=delta_ptr_max,
                delta_ptr_tmp=delta_ptr_tmp,
            ):
                lower = min(0, delta_ptr_min, delta_ptr_max, delta_ptr_tmp)
                upper = max(0, delta_ptr_min, delta_ptr_max, delta_ptr_tmp)
                return PtrSummary(
                    s_net=0,
                    s_min=lower,
                    s_max=upper,
                )

            # Statements with no protocol for summarising pointer deltas
            case _:
                raise CompilerInternalError(
                    f"Validator cannot analyse pointer deltas for node type {type(node).__name__}"
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

    def _check_ptr_deltas(self, ast: AbstractSyntaxTree) -> None:
        """Checks pointer deltas for potential segmentation faults caused
        by an out-of-bounds pointer. Throws errors if it finds a liability."""

        # create an imaginary pointer for simulation
        s = self._walk_ptr_deltas(ast)
        violation_pos = self._find_bounds_violation_pos(ast)

        if s.s_min < MEMORY_LIMIT_LEFT:
            raise CompilerPtrOutOfBoundsError(
                "Potential segmentation fault detected: access violation to far-left of memory",
                pos=violation_pos,
                src_code=self.src_code
            )
        elif s.s_max >= MEMORY_LIMIT_RIGHT:
            raise CompilerPtrOutOfBoundsError(
                "Potential segmentation fault detected: access violation to far-right of memory",
                pos=violation_pos,
                src_code=self.src_code
            )

    # No need to check types and vals as those are already checked by the parser

    def validate(self, ast: AbstractSyntaxTree, src_code: list[str]) -> None:
        """Validates the AST (WITHOUT MODIFYING IT).
        If a check breaks, throws an error.
        Requires src_code for error reporting."""
        self.src_code = src_code

        for check in (
            self._check_ptr_deltas,
        ):
            check(ast)
