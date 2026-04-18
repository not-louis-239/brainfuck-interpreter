# AST node definitions

from dataclasses import dataclass
from typing import TypeAlias

from ..crim_tokens import TokenMetadata


@dataclass
class ASTNode:
    """Base class for Crimscript AST (Abstract Syntax Tree) nodes."""
    metadata: TokenMetadata

@dataclass
class ValueChange(ASTNode):
    amount: int

@dataclass
class PointerChange(ASTNode):
    distance: int

@dataclass
class PrintStmt(ASTNode):
    text: str | None = None

@dataclass
class InputStmt(ASTNode):
    prompt: str | None = None

@dataclass
class ClearStmt(ASTNode):
    pass

@dataclass
class SetStmt(ASTNode):
    value: int

@dataclass
class UntilStmt(ASTNode):
    target: int
    body: list[ASTNode]

@dataclass
class MoveStmt(ASTNode):
    delta_ptr_min: int
    delta_ptr_max: int

@dataclass
class CopyStmt(ASTNode):
    delta_ptr_min: int
    delta_ptr_max: int
    delta_ptr_tmp: int

# A recursive structure of ASTNodes
AbstractSyntaxTree: TypeAlias = list[ASTNode]
