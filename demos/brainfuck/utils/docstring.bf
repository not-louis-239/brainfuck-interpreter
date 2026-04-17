[
    Implementation of a docstring-like pattern in Brainfuck.
    A "trick" or hacky way around Brainfuck's annoying property
    of executing anything that is valid Brainfuck characters
    is to put it inside a loop that you know will never execute
    as the pointer will always be at a 0 when the opening bracket
    is reached.

    To test, we'll print the number 0:
    ++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++ .
    That line shouldn't execute as it is inside the 'docstring'.

    This is the same trick that allows using Brainfuck symbols:
    + - < > [ ] . ,
    in comments, but putting them at the top of the module makes them
    a sort of 'docstring' for the module, especially with indentation inside
    a loop, which separates it from the module's working code.
]

Now we'll print 0 with a newline
If our docstring worked then we should only see one '0' and a newline
in the output
++++++++++ ++++++++++ ++++++++++ ++++++++++ ++++++++ . [-] ++++++++++ .
