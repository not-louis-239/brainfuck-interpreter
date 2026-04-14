number guessing game in Brainfuck

print the prompt "i'm thinking of a number from 1 to 9"

initialise the first cell to 5
++++++++++

for every point in the first cell "exchange" it for 10 points in the next cell using the loop
then print the letters

[>++++++++++<-]>+++++.  i
[-]<[-]+++[>++++++++++<-]>+++++++++.  '
[-]<[-]++++++++++[>++++++++++<-]>+++++++++.  m
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]+++++++++++[>++++++++++<-]>++++++.  t
[-]<[-]++++++++++[>++++++++++<-]>++++.  h
[-]<[-]++++++++++[>++++++++++<-]>+++++.  i
[-]<[-]+++++++++++[>++++++++++<-]>.  n
[-]<[-]++++++++++[>++++++++++<-]>+++++++.  k
[-]<[-]++++++++++[>++++++++++<-]>+++++.  i
[-]<[-]+++++++++++[>++++++++++<-]>.  n
[-]<[-]++++++++++[>++++++++++<-]>+++.  g
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]+++++++++++[>++++++++++<-]>+.  o
[-]<[-]++++++++++[>++++++++++<-]>++.  f
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]+++++++++[>++++++++++<-]>+++++++.  a
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]+++++++++++[>++++++++++<-]>.  n
[-]<[-]+++++++++++[>++++++++++<-]>+++++++.  u
[-]<[-]+++++++++++[>++++++++++<-]>-.  m
[-]<[-]++++++++++[>++++++++++<-]>--.  b
[-]<[-]++++++++++[>++++++++++<-]>+.  e
[-]<[-]+++++++++++[>++++++++++<-]>++++.  r
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]++++++++++[>++++++++++<-]>++.  f
[-]<[-]+++++++++++[>++++++++++<-]>++++.  r
[-]<[-]+++++++++++[>++++++++++<-]>+.  o
[-]<[-]+++++++++++[>++++++++++<-]>-.  m
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]+++++[>++++++++++<-]>-.   1
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]+++++++++++[>++++++++++<-]>++++++.  t
[-]<[-]+++++++++++[>++++++++++<-]>+.  o
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]++++++[>++++++++++<-]>---.  9

newline
[-]++++++++++.  clear cell and newline

prompt "enter your guess"
[-]<[-]++++++++++[>++++++++++<-]>+.  e
[-]<[-]+++++++++++[>++++++++++<-]>.  n
[-]<[-]+++++++++++[>++++++++++<-]>++++++.  t
[-]<[-]++++++++++[>++++++++++<-]>+.  e
[-]<[-]+++++++++++[>++++++++++<-]>++++.  r
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]++++++++++++[>++++++++++<-]>+.  y
[-]<[-]+++++++++++[>++++++++++<-]>+.  o
[-]<[-]+++++++++++[>++++++++++<-]>+++++++.  u
[-]<[-]+++++++++++[>++++++++++<-]>++++.  r
[-]<[-]+++[>++++++++++<-]>++.  space

[-]<[-]++++++++++[>++++++++++<-]>+++.  g
[-]<[-]+++++++++++[>++++++++++<-]>+++++++.  u
[-]<[-]++++++++++[>++++++++++<-]>+.  e
[-]<[-]+++++++++++[>++++++++++<-]>+++++.  s
[-]<[-]+++++++++++[>++++++++++<-]>+++++.  s
[-]<[-]++++++[>++++++++++<-]>--.  :
[-]<[-]+++[>++++++++++<-]>++.  space

read input
,  read from stdin

check if the input is equal to 3 (arbitrary hidden number)
at this point the value of stdin is assigned to the currently active cell

>  move 1 right of where the stdin was assigned
+++++[<---------->-]<-    adjust by the value of 3 (ASCII 51) so remove 51 points

mark the success flag 1 to the right (this will be zeroed if the user actually failed)
>[-]+

right now the pointer is 1 to the right of the stdin read
if the stdin cell is not zero then execute the following code block
<  move back to stdin and check it; if it's not zero then execute the loop
[
    >>[-]+  mark the cell 2 to the right as val 1 to be used as a failure flag
    <[-]>  zero out the success flag to prevent the success branch from triggering

    >>  move a bit more to the right (2 right of the fail flag)
    so we don't tamper with the flag while printing

    print "you failed!"

    at the end of each of these letter lines we're 4 right of stdin
    that is 2 right of the flag

    [-]<[-]++++++++++++[>++++++++++<-]>+.  y
    [-]<[-]+++++++++++[>++++++++++<-]>+.  o
    [-]<[-]+++++++++++[>++++++++++<-]>+++++++.  u
    [-]<[-]+++[>++++++++++<-]>++.  space

    [-]<[-]++++++++++[>++++++++++<-]>++.  f
    [-]<[-]+++++++++[>++++++++++<-]>+++++++.  a
    [-]<[-]++++++++++[>++++++++++<-]>+++++.  i
    [-]<[-]++++++++++[>++++++++++<-]>++++++++.  l
    [-]<[-]++++++++++[>++++++++++<-]>+.  e
    [-]<[-]++++++++++[>++++++++++<-]>.  d
    [-]<[-]+++[>++++++++++<-]>+++.  !

    <<[-]  move back to the fail flag and zero it out to send the signal "we're done"
]

now check the success flag
>  move to it first

if the success flag is not zero then execute this block
[
    >>  give us a bit of room so we don't tamper with the flag

    print "correct!"
    [-]<[-]++++++++++[>++++++++++<-]>-.  c
    [-]<[-]+++++++++++[>++++++++++<-]>+.  o
    [-]<[-]+++++++++++[>++++++++++<-]>++++.  r
    [-]<[-]+++++++++++[>++++++++++<-]>++++.  r
    [-]<[-]++++++++++[>++++++++++<-]>+.  e
    [-]<[-]++++++++++[>++++++++++<-]>-.  c
    [-]<[-]+++++++++++[>++++++++++<-]>++++++.  t
    [-]<[-]+++[>++++++++++<-]>+++.  !

    <<[-]  zero out the success flag to prevent an infinite loop
]

always end with a newline (ASCII 10)
[-]++++++++++.  clear cell and newline
