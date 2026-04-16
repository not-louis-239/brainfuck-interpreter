class Optimiser:
    """Optimises Brainfuck code to reduce redundant ops."""

    def __init__(self) -> None:
        pass

    def _optimise_ptr_deltas(self, code: str) -> str:
        ...

    def _optimise_val_deltas(self, code: str) -> str:
        ...

    def optimise(self, code: str) -> str:
        """Optimises BF code by removing redundant operations, e.g.
        adjacent `+-` or `<>` pairs that cancel out at runtime.

        Accepts a string of Brainfuck code and returns the optimised version."""

        # First, optimise pointer deltas (e.g. `<<>>>>` -> `>>`)
        code = self._optimise_ptr_deltas(code)
        # Then, optimise value deltas (e.g. `++++--` -> `++`)
        code = self._optimise_val_deltas(code)
        return code
