from typing import Callable

from brainfuck.compiler.ast import nodes
from brainfuck.compiler.stages.emitter import Emitter
from brainfuck.compiler.crim_tokens import TokenMetadata

@Emitter.register(nodes.MoveStmt)
def compile_move(self: Emitter, node: nodes.MoveStmt) -> str:
    get_ptr_instructions: Callable[[int], str] = lambda displacement: ">" * displacement if displacement > 0 else "<" * -displacement

    dptr_min = node.delta_ptr_min
    dptr_max = node.delta_ptr_max
    diff = dptr_max - dptr_min

    mv_code = "["

    # Move to minimum location
    mv_code += get_ptr_instructions(dptr_min)
    # Copy from the range of min loc to max loc
    mv_code += ">".join("+" for _ in range(diff + 1))
    # Move back to the original location
    mv_code += get_ptr_instructions(-dptr_max)
    # Decrement src location
    mv_code += "-"

    mv_code += "]"
    return mv_code

test_nodes = [
    nodes.MoveStmt(metadata=TokenMetadata(pos=0), delta_ptr_min=-5, delta_ptr_max=3),
    nodes.MoveStmt(metadata=TokenMetadata(pos=1), delta_ptr_min=2, delta_ptr_max=8),
    nodes.MoveStmt(metadata=TokenMetadata(pos=2), delta_ptr_min=-4, delta_ptr_max=-1),
    nodes.MoveStmt(metadata=TokenMetadata(pos=3), delta_ptr_min=1, delta_ptr_max=1)
]

for node in test_nodes:
    emitter = Emitter()
    print(f"Test case: delta_ptr_min={node.delta_ptr_min}, delta_ptr_max={node.delta_ptr_max}")
    result = compile_move(emitter, node)
    print("Generated BF code:", result)
