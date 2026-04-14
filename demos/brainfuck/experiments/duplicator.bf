demonstration of how you can duplicate values to nearby cells in Brainfuck

initialise a cell with the value of 65 (ASCII for 'A')
++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++++ +++++

duplicate the value to the two neighbouring cells using a loop
[->+>+>+>+>+<<<<<]


print the value of the two cells to which the value just got duplicated
>.>.>.>.>.  A

end with a newline
[-]++++++++++.

the output of this program should be 'AAAAA' followed by a newline character
