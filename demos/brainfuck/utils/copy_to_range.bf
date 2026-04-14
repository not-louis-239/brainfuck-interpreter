implementation of

copy(destmin:destmax temp)

>  leave one cell to the left as the 'temp' cell


now we are at the src cell
initialise it with a value of 49 (ASCII for '1')
++++++++++ ++++++++++ ++++++++++ ++++++++++ +++++++++

[
    copy to the temp cell first
    <+

    then copy to the cell range
    >  move back to src
    >+>+>+  copy to cells

    then move back to src and decrement it by 1
    <<<-
]

now we are back at the src cell and it is zero
we need to restore the src value from the temp cell
so transfer the contents of temp back to src
<[>+<-]

this should print '1111'
>.>.>.>.

final newline
[-]++++++++++.
