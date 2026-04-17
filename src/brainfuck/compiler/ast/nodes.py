# AST node definitions

from dataclasses import dataclass

@dataclass
class Statement:
    pass

@dataclass
class ValueChange(Statement):
    amount: int

@dataclass
class PointerChange(Statement):
    distance: int

@dataclass
class PrintStmt(Statement):
    text: str | None = None

@dataclass
class InputStmt(Statement):
    prompt: str | None = None

@dataclass
class ClearStmt(Statement):
    pass

@dataclass
class SetStmt(Statement):
    value: int

@dataclass
class UntilStmt(Statement):
    target: int
    body: list[Statement]

@dataclass
class MoveStmt(Statement):
    delta_ptr_min: int
    delta_ptr_max: int

@dataclass
class CopyStmt(Statement):
    delta_ptr_min: int
    delta_ptr_max: int
    delta_ptr_tmp: int
