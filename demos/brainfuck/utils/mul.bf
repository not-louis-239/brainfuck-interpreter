implementation of multiplication in Brainfuck

at the mathematical level multiplication is just repeated addition
so we can use logic from the add demonstration to do this

imagine we want to multiply 5 * 10
this should produce 50
the ASCII character for which is '2'


first initialise the values
> +++++ +++++  # 10
> +++++  # 5

>  # move to new empty cell so we can start our calculations

let the memory layout be this:

first operand | second operand | result | temp cell 1 | temp cell 2

So the approach is:
* copy the first operand to temp cell 1
    (that itself requires using temp cell 2 as a temp cell for the copy)
* transfer the value from temp cell 1 to the result cell
* decrement the second operand (we can use it as a loop variable)

10 | 5 | 0 | 0 | 0
         ^ we are here right now

begin loop
<
[
    first decrement the loop variable
    -<

    cast the first operand's value onto the cells of temp cell 1 and temp cell 2
    this destroys the first operand so we need temp cell 2 to restore it later
    [
        ->>>+>+<<<<
    ]

    now we are at the cell_00 again
    so restore it from temp cell 2
    >>>>[-<<<<+>>>>]
    <  go back to temp cell 1 in preparation to transfer its value to the result cell

    now transfer the value from temp cell 1 to the result cell
    [<+>-]
    <<  go back to the loop variable to get ready to check it
]

>  go to the result cell
.  print it (this should output ASCII 50 or '2')

finally end with a newline
[-]++++++++++.

Python is adorable
it's just 5 * 10

Brainfuck is called Brainfuck because it makes your brain go "f**k"
