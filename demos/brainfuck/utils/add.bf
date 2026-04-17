implementation of adding two numbers in Brainfuck

# first initalise some numbers
> ++++++++++ ++++++++++ ++++++++++ ++++++++++  # 40

> ++++++++++ ++++++++++ ++++++++++  # 30

# now we use the third cell to add the numbers
# this will destroy the first two cells because of how Brainfuck works
# we "transfer" value from the first two cells into the third cell

# the 30 cell (cell_01)
[>+<-]

# the 40 cell (cell_00)
<[>>+<<-]

# now go to the result cell (cell_02) and print the result (which should be 70)
# ASCII 70 is 'F' so this will print 'F'
>>.

# end with newline
[-]++++++++++.
