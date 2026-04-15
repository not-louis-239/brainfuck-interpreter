implementation of subtraction in Brainfuck

first initialise some values
> +++++ +++++   +++++ +++++   +++++ +++++   +++++ +++++   +++++ +++++  # 50
> +++++ +++++  # 10

now the mmap looks like:

50 | 10 | 0 | 0 | etc
     ^ we are here

transfer cell_01's value to cell_00 but negative so that we end up
with 40 in cell 0 (50 minus 10 = 40)
[<->-]

now print cell_00
this should print ASCII 40 which is '('
<.

finally end with a newline
[-]++++++++++.
