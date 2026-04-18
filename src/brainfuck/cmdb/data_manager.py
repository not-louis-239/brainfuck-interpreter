import json
from pathlib import Path

from ..compiler.debug_info import DebugInfo, CrimscriptDebugSymbol


def load_debug(debug_path: Path) -> DebugInfo | None:
    try:
        with open(debug_path, "r") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("Warning: cannot find debug file. debug info will be unavailable.")
        return None
    except json.JSONDecodeError:
        print("Warning: debug file is malformed. debug info will be unavailable.")
        return None

    src_code = raw_data.get("src_code", [])
    symbols: list[CrimscriptDebugSymbol] = []

    src_crim_path = raw_data.get("src_path", None)

    for sym in raw_data.get("symbols", []):
        symbols.append(CrimscriptDebugSymbol(start_pos_bf=sym[0], start_pos_cms=sym[1]))

    return DebugInfo(src_code=src_code, symbols=symbols, src_crim_path=str(src_crim_path))

def save_debug(debug: DebugInfo, bf_path: Path, src_crim_path: Path) -> None:
    db_path = str(bf_path) + ".debug.json"
    tmp_path = db_path + ".tmp"

    serialised_symbols: list[tuple[int, int]] = []
    for sym in debug.symbols:
        serialised_symbols.append((sym.start_pos_bf, sym.start_pos_cms))

    # Write to tmp file to avoid making malformed debug files in case of crashes during writing
    with open(tmp_path, "w") as f:
        json.dump({
            "symbols": serialised_symbols,
            "src_code": debug.src_code,
            "src_path": str(src_crim_path.absolute())
        }, f, indent=4)

    # Atomic overwrite of the debug path
    Path(tmp_path).replace(db_path)
