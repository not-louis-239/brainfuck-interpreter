from typing import Callable, TypeAlias, TypeVar

from ..ast import nodes
from ..ast.nodes import AbstractSyntaxTree, ASTNode
from ..exceptions import CompilerSyntaxError, CompilerInternalError

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
        return self.EMIT_REGISTRY[type(node)](self, node)

    def emit(self, ast: AbstractSyntaxTree, src_code: list[str]) -> str:
        self.src_code = src_code

        bf_code = ""
        for node in ast:
            try:
                bf_code += self.compile_stmt(node)
            except KeyError:
                raise CompilerSyntaxError(f"Unknown statement type: {type(node).__name__}", node.metadata.pos, self.src_code)
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
    return ""  # TODO: rest of implementation
    # This is a stub that returns an empty string so as not to crash
    # the emitter

@Emitter.register(nodes.CopyStmt)
def compile_copy(self: Emitter, node: nodes.CopyStmt) -> str:
    return ""  # TODO: rest of implementation
    # This is a stub that returns an empty string so as not to crash
    # the emitter
