import bisect
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

    def get_crim_instruction(self, start_pos_bf: int) -> int:
        """Given a Brainfuck instruction position, return the corresponding Crimscript instruction position."""
        bf_positions = [sym.start_pos_bf for sym in self.symbols]
        idx = bisect.bisect_right(bf_positions, start_pos_bf) - 1
        if idx >= 0:
            return self.symbols[idx].start_pos_cms
        else:
            raise ValueError(f"No debug symbol found for BF position {start_pos_bf}")
