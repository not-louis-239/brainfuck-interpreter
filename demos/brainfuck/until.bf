# until

demonstration of an until loop in Brainfuck

this loop will loop until the value in the data pointer is 3

initialise the value of the second cell to 65 (ASCII for 'A')
let's imagine that this is what we want to print some number of times
>
++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ +++++
<

+++++ initialise the value of the first cell to 5


using offsets we can abuse Brainfuck's native "if x != 0" condition for loops
to check inequality against non zero integers

---  if the first cell was 3 then this line would set it to 0 and skip the loop
[
    +++ undo offset
    >.+<  overall this will print 'AB'

    - decrement loop counter (so if it was 5 it would now be 4)
    if the loop starts at 5 and ends at 3 then this would make the loop
    run twice

    --- subtract to prepare to check offset
]
+++  must cancel out the offset if the loop didn't actually run


finally print a newline
[-]++++++++++.

this allows us to compile Crimscript until loops
eg "until 3 { }" to valid Brainfuck code

the importance is in 4 critical steps
    outside the loop:
        subtract the offset when the loop starts
        undo (add) the offset when the loop ends

    inside the loop:
        undo (add) the offset at the start of the loop
        subtract the offset at the end of the loop to prepare it for checking

        or simply make sure that the loop variable cell doesn't get modified
        while the loop is running other than it being updated
