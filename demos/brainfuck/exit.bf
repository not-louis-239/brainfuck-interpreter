demonstration of how you can use an exit command by using the first
cell of memory as a flag for exiting the program

it is a "keep alive" flag
that is
if it is 1 the program continues
if it is 0 the program exits

this is tricky as there is no exit() function in native Brainfuck


+  initialise the first cell of memory to 1 (the keep alive flag)



[
    >+++++++++++++++++++++++++++++++++++++++++++.   (example work on cell 1)

    [-]++++++++++.  newline

    <[-]  (move back to cell 0 and clear it leading to exit condition)
]