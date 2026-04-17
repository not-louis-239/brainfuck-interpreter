import json
from pathlib import Path

from ..compiler.debug_info import DebugInfo, CrimscriptDebugSymbol


def load_debug(db_path: Path) -> DebugInfo:
    with open(db_path, "r") as f:
        raw_data = json.load(f)

    src_code = raw_data.get("src_code", [])
    symbols: list[CrimscriptDebugSymbol] = []

    for sym in raw_data.get("symbols", []):
        symbols.append(CrimscriptDebugSymbol(start_pos_bf=sym[0], start_pos_cms=sym[1]))

    return DebugInfo(src_code=src_code, symbols=symbols)

def save_debug(debug: DebugInfo, bf_path: Path) -> None:
    db_path = str(bf_path) + ".debug.json"
    tmp_path = db_path + ".tmp"

    serialised_symbols: list[tuple[int, int]] = []
    for sym in debug.symbols:
        serialised_symbols.append((sym.start_pos_bf, sym.start_pos_cms))

    # Write to tmp file to avoid making malformed debug files in case of crashes during writing
    with open(tmp_path, "w") as f:
        json.dump({
            "symbols": serialised_symbols,
            "src_code": debug.src_code
        }, f, indent=4)

    # Atomic overwrite of the debug path
    Path(tmp_path).replace(db_path)
