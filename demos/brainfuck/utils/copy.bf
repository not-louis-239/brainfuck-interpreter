implementation of copy function in Brainfuck

copy(src dst tmp)

>  leave one cell to the left as the 'temp' cell
++++++++++ ++++++++++ ++++++++++ ++++++++++ +++++++++  initialise the value of '1' (ASCII 49)

copy the points from src to dest (right) and temp (left)
[
    >+  add 1 to dest
    <<+  add 1 to temp
    >-  subtract 1 from src
]

now src is zero | dest and temp are both the value we want
now copy the value from temp back to src to restore the original value of src
<[>+<-]

now we are at temp and it is zero
if this worked then we should be able to print the val of src and dest
and see that they are both '1' (ASCII 49)
>.>.

finally end with a newline
[-]++++++++++.
