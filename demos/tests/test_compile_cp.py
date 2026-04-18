from typing import Callable

from brainfuck.compiler.ast import nodes
from brainfuck.compiler.crim_tokens import TokenMetadata
from brainfuck.compiler.stages import Emitter


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

test_cases = [
    nodes.CopyStmt(metadata=TokenMetadata(pos=0), delta_ptr_min=1, delta_ptr_max=1, delta_ptr_tmp=2),
    nodes.CopyStmt(metadata=TokenMetadata(pos=1), delta_ptr_min=2, delta_ptr_max=3, delta_ptr_tmp=4),
    nodes.CopyStmt(metadata=TokenMetadata(pos=5), delta_ptr_min=-1, delta_ptr_max=0, delta_ptr_tmp=2)  # invalid
]

for node in test_cases:
    emitter = Emitter()
    print(f"Testing with values: {node.delta_ptr_min = }, {node.delta_ptr_max = }, {node.delta_ptr_tmp = }")
    print(f"BF Code: {compile_copy(emitter, node)}")
