from typing import Callable, TypeVar

from ..ast import nodes
from ..ast.nodes import AbstractSyntaxTree, ASTNode
from ..exceptions import CompilerDepthError, CompilerInternalError
from ..debug_info import DebugInfo, CrimscriptDebugSymbol

N = TypeVar("N", bound=ASTNode)
_EmitCallable = Callable[["Emitter", N, DebugInfo | None, int, int], str]

class Emitter:
    """Emits Brainfuck source code from an Abstract Syntax Tree (AST).
    Basically the converter from a Crimscript AST to raw Brainfuck."""

    EMIT_REGISTRY: dict[type[ASTNode], _EmitCallable] = {}

    @classmethod
    def register(cls, node_type: type[ASTNode]):
        def wrapper(fn: _EmitCallable) -> _EmitCallable:
            cls.EMIT_REGISTRY[node_type] = fn
            return fn
        return wrapper

    def __init__(self) -> None:
        pass

    def compile_stmt(self, node: ASTNode, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
        try:
            bf_code = self.EMIT_REGISTRY[type(node)](
                self, node, debug_info, bf_pos, cms_pos
            )
            if debug_info is not None and bf_code:  # Only record debug symbols for nodes that emit actual BF code
                # Record debug symbols
                debug_info.symbols.append(CrimscriptDebugSymbol(start_pos_bf=bf_pos, start_pos_cms=cms_pos))
            return bf_code
        except KeyError:
            raise CompilerInternalError(f"No emit function registered for type {type(node).__name__}", node.metadata.pos)
        except RecursionError as e:
            # I've done my best to prevent the user from getting slapped in the face
            # by Python, but if they write 1,000 nested loops then that's on them.
            raise CompilerDepthError(
                "Maximum recursion depth exceeded during compilation. This likely means your code has too many nested loops or statements.",
                pos=node.metadata.pos, src_code=self.src_code
            ) from e

    def emit(self, ast: AbstractSyntaxTree, src_code: list[str], debug_symbols: bool = False) -> tuple[str, DebugInfo | None]:
        self.src_code = src_code  # required for error reporting

        bf_code = ""
        bf_position = 0  # Track current BF instruction position
        debug_info = DebugInfo(src_code=src_code) if debug_symbols else None

        for cms_node in ast:
            node_bf = self.compile_stmt(
                node=cms_node, debug_info=debug_info,
                bf_pos=bf_position, cms_pos=cms_node.metadata.pos
            )
            bf_code += node_bf
            bf_position += len(node_bf)

        return (bf_code, debug_info)

# Functions for compiling Crimscript AST nodes into BF

@Emitter.register(nodes.ValueChange)
def compile_value_change(self: Emitter, node: nodes.ValueChange, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
    return '+' * node.amount if node.amount > 0 else '-' * (-node.amount)

@Emitter.register(nodes.PointerChange)
def compile_pointer_change(self: Emitter, node: nodes.PointerChange, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
    return '>' * node.distance if node.distance > 0 else '<' * (-node.distance)

@Emitter.register(nodes.PrintStmt)
def compile_print(self: Emitter, node: nodes.PrintStmt, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
    """Compile a print statement to Brainfuck, either '.' or string output."""

    # Use a greedy approach so that instead of clearing then plussing
    # we remember the value from the last character and calculate how
    # many increments/decrements we need to get to the next character.

    if node.text is None:
        return '.'

    result: list[str] = []
    last_val: int = 0

    result.append('[-]')  # initial clear to ensure there is no residue

    for char in node.text:
        new_val = ord(char)
        diff = new_val - last_val

        # We can abuse how Brainfuck wraps values
        # at >255 or <0 to make our print even more efficient
        diff = (diff + 128) % 256 - 128  # this caps diff to [-128...127]

        result.append('+' * diff if diff > 0 else '-' * -diff)
        result.append('.')
        last_val = new_val

    result.append('[-]')  # final clear to leave cell at 0 after printing
    return ''.join(result)

@Emitter.register(nodes.InputStmt)
def compile_input(self: Emitter, node: nodes.InputStmt, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
    """Compile an input statement to Brainfuck, optionally emitting a prompt first."""
    code: list[str] = []
    if node.prompt is not None:
        code.append(
            Emitter.compile_stmt(
                self,
                nodes.PrintStmt(text=node.prompt, metadata=node.metadata),
                None, bf_pos, cms_pos
            )
        )
    code.append(',')
    return ''.join(code)

@Emitter.register(nodes.ClearStmt)
def compile_clear(self: Emitter, node: nodes.ClearStmt, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
    # Even though this function returns a constant
    # clear instruction, it helps for consistency.
    return "[-]"

@Emitter.register(nodes.SetStmt)
def compile_set(self: Emitter, node: nodes.SetStmt, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
    # Assuming node.value has already been validated to be non-negative
    return '[-]' + ('+' * node.value)

@Emitter.register(nodes.UntilStmt)
def compile_until(self: Emitter, node: nodes.UntilStmt, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int):
    """Compile an until loop into Brainfuck with offset checking and body code."""
    offset = '-' * node.target
    restore = '+' * node.target

    body_parts: list[str] = []
    child_bf_pos = bf_pos + len(offset) + 1 + len(restore)
    for child in node.body:
        child_code = self.compile_stmt(
            node=child,
            debug_info=debug_info,
            bf_pos=child_bf_pos,
            cms_pos=child.metadata.pos
        )
        body_parts.append(child_code)
        child_bf_pos += len(child_code)

    body = ''.join(body_parts)
    return f"{offset}[{restore}{body}{offset}]{restore}"

@Emitter.register(nodes.MoveStmt)
def compile_move(self: Emitter, node: nodes.MoveStmt, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
    get_ptr_instructions: Callable[[int], str] = lambda displacement: ">" * displacement if displacement > 0 else "<" * -displacement

    dptr_min = node.delta_ptr_min
    dptr_max = node.delta_ptr_max
    diff = dptr_max - dptr_min

    mv_code = "["

    # Move to minimum location
    mv_code += get_ptr_instructions(dptr_min)
    # Copy from the range of min loc to max loc
    mv_code += ">".join("+" for _ in range(diff + 1))
    # Move back to the original location
    mv_code += get_ptr_instructions(-dptr_max)
    # Decrement src location
    mv_code += "-"

    mv_code += "]"
    return mv_code

@Emitter.register(nodes.CopyStmt)
def compile_copy(self: Emitter, node: nodes.CopyStmt, debug_info: DebugInfo | None, bf_pos: int, cms_pos: int) -> str:
    # cp() is basically two mv() operations
    # one to cast src to destmin:destmax AND tmp,
    # and one to restore src from tmp

    # we need the second mv() to restore src from tmp
    # because the first mv() destroys src
    # we can reuse compile_move() for this

    get_ptr_instructions: Callable[[int], str] = lambda displacement: ">" * displacement if displacement > 0 else "<" * -displacement

    destmin = node.delta_ptr_min
    destmax = node.delta_ptr_max
    tmp = node.delta_ptr_tmp
    diff = destmax - destmin

    cp_code = "["

    # Cast src to destmin:destmax AND tmp
    # We can't use compile_mv() because it doesn't
    # support moving to more than one range

    # Move to minimum location
    cp_code += "[" + get_ptr_instructions(destmin)
    # Copy from the range of min loc to max loc
    cp_code += ">".join("+" for _ in range(diff + 1))
    # Now move to tmp and add one point there
    cp_code += get_ptr_instructions(tmp - destmax) + "+"
    # Move back to src and decrement it by 1
    cp_code += get_ptr_instructions(-tmp) + "-]"

    # Move to tmp
    cp_code += get_ptr_instructions(tmp)

    # Restore src from tmp
    cp_code += self.compile_stmt(
        nodes.MoveStmt(
            metadata=node.metadata,
            delta_ptr_min=-tmp,
            delta_ptr_max=-tmp,
        ),
        None,   # using None when the child statement shouldn't be considered a separate statement
        bf_pos,
        cms_pos
    )

    # Move back from tmp -> src
    cp_code += get_ptr_instructions(-tmp)

    cp_code += "]"

    return cp_code
