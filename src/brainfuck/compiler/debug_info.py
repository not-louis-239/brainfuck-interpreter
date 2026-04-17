from dataclasses import dataclass, field
from ..compiler.get_line_and_col import get_line_and_col

@dataclass
class CrimscriptDebugSymbol:
    start_pos_bf: int
    start_pos_cms: int

@dataclass
class DebugInfo:
    src_code: list[str]
    symbols: list[CrimscriptDebugSymbol] = field(default_factory=list)
