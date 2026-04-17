import re

# break apart Brainfuck code into lines of this size
# to improve readability in the final compiled code
LINESIZE = 80

class Optimiser:
    """Optimises Brainfuck code to reduce redundant ops.
    The final stage before the BF code is ready to use."""

    def __init__(self) -> None:
        pass

    def _optimise_val_deltas(self, match: re.Match) -> str:
        text = match.group(0)
        net = (text.count('+') - text.count('-') + 128) % 256 - 128  # net effect of the sequence, wrapped to [-128...127]
        if net > 0:
            return '+' * net
        elif net < 0:
            return '-' * -net
        else:
            return ''


    def _optimise_ptr_deltas(self, match: re.Match) -> str:
        text = match.group(0)
        net = (text.count('>') - text.count('<'))  # no %256 here since pointer movement can be unbounded
        if net > 0:
            return '>' * net
        elif net < 0:
            return '<' * -net
        else:
            return ''

    def _split_bf_code_to_lines(self, bf_code: str) -> list[str]:
        return [
            bf_code[i:i + LINESIZE]
            for i in range(0, len(bf_code), LINESIZE)
        ]

    def optimise(self, code: str) -> str:
        """Optimises BF code by removing redundant operations, e.g.
        adjacent `+-` or `<>` pairs that cancel out at runtime.
        Accepts a string of Brainfuck code and returns the optimised version."""

        code = re.sub(r'[+-]+', self._optimise_val_deltas, code)
        code = re.sub(r'[<>]+', self._optimise_ptr_deltas, code)
        code = "\n".join(self._split_bf_code_to_lines(code))
        return code
