usually you can't have Brainfuck symbols as comments
so use a different character instead
but in this demo I will show you a hacky approach that allows such chaos

we can do this by moving to a dummy cell far away from our "working cells"
>>>>>>>>>>[
    then enter a loop
    since the loop only runs when the cell is not zero
    and this a dummy cell that we haven't touched, then it will be zero
    so this loop can be guaranteed to never execute.

    here is a comment with Brainfuck symbols:
    + - < > [ ] . ,
    none of these will execute because this loop will never be entered

    just to confirm, here's a segment of code that prints the number '1' (ASCII 49)
    +++++ +++++
    +++++ +++++
    +++++ +++++
    +++++ +++++
    +++++ ++++
    .

    now we move back so we can get back to our working cells.
]<<<<<<<<<<


Now the real code to print a '1'
If our multiline comment worked then we should only see one '1' in the output
+++++ +++++
+++++ +++++
+++++ +++++
+++++ +++++
+++++ ++++
.

finally end with a newline
[-]++++++++++.
