from typing import Callable, TypeVar

from ..ast import nodes
from ..ast.nodes import AbstractSyntaxTree, ASTNode
from ..get_line_and_col import get_line_and_col
from ..exceptions import CompilerInternalError

N = TypeVar("N", bound=ASTNode)
_EmitCallable = Callable[["Emitter", N], str]

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

    def compile_stmt(self, node: ASTNode) -> str:
        try:
            line, col = get_line_and_col(src_code=self.src_code, pos=node.metadata.pos)

            # Basic "debug symbols" - right now just line and col number of the symbol
            db_symbol = f"({line}:{col})"
            bf_code = self.EMIT_REGISTRY[type(node)](self, node)

            return f"{db_symbol} {bf_code}"
        except KeyError:
            raise CompilerInternalError(f"No emit function registered for type {type(node).__name__}", node.metadata.pos)

    def emit(self, ast: AbstractSyntaxTree, src_code: list[str], debug_symbols: bool = False) -> str:
        self.src_code = src_code  # required for error reporting

        bf_code = ""
        for node in ast:
            bf_code += self.compile_stmt(node, debug_symbols=debug_symbols)
        return bf_code

# Functions for compiling Crimscript AST nodes into BF

@Emitter.register(nodes.ValueChange)
def compile_value_change(self: Emitter, node: nodes.ValueChange) -> str:
    return '+' * node.amount if node.amount > 0 else '-' * (-node.amount)

@Emitter.register(nodes.PointerChange)
def compile_pointer_change(self: Emitter, node: nodes.PointerChange) -> str:
    return '>' * node.distance if node.distance > 0 else '<' * (-node.distance)

@Emitter.register(nodes.PrintStmt)
def compile_print(self: Emitter, node: nodes.PrintStmt) -> str:
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
def compile_input(self: Emitter, node: nodes.InputStmt) -> str:
    """Compile an input statement to Brainfuck, optionally emitting a prompt first."""
    code: list[str] = []
    if node.prompt is not None:
        code.append(
            Emitter.EMIT_REGISTRY[nodes.PrintStmt](
                self,
                nodes.PrintStmt(text=node.prompt, metadata=node.metadata),
            )
        )
    code.append(',')
    return ''.join(code)

@Emitter.register(nodes.ClearStmt)
def compile_clear(self: Emitter, node: nodes.ClearStmt) -> str:
    # Even though this function returns a constant
    # clear instruction, it helps for consistency.
    return "[-]"

@Emitter.register(nodes.SetStmt)
def compile_set(self: Emitter, node: nodes.SetStmt) -> str:
    # Assuming node.value has already been validated to be non-negative
    return '[-]' + ('+' * node.value)

@Emitter.register(nodes.UntilStmt)
def compile_until(self: Emitter, node: nodes.UntilStmt):
    """Compile an until loop into Brainfuck with offset checking and body code."""
    offset = '-' * node.target
    restore = '+' * node.target
    body = ''.join(self.compile_stmt(child) for child in node.body)
    return f"{offset}[{restore}{body}{offset}]{restore}"

@Emitter.register(nodes.MoveStmt)
def compile_move(self: Emitter, node: nodes.MoveStmt) -> str:
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
def compile_copy(self: Emitter, node: nodes.CopyStmt) -> str:
    # cp() is basically two mv() operations
    # one to cast src to destmin:destmax AND tmp,
    # and one to restore src from tmp

    # we need the second mv() to restore src from tmp
    # because the first mv() destroys src
    # we can reuse compile_move() for this

    get_ptr_instructions: Callable[[int], str] = lambda displacement: ">" * displacement if displacement > 0 else "<" * -displacement

    compile_mv = Emitter.EMIT_REGISTRY[nodes.MoveStmt]

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
    cp_code += compile_mv(self, nodes.MoveStmt(
        metadata=node.metadata,
        delta_ptr_min=-tmp,
        delta_ptr_max=-tmp
    ))

    # Move back from tmp -> src
    cp_code += get_ptr_instructions(-tmp)

    cp_code += "]"

    return cp_code
