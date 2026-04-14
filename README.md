# Brainfuck Interpreter and Macrolang Compiler

## Out of the Box
This program includes
- a Brainfuck interpreter, and
- a compiler for a simple macro language that compiles to Brainfuck.

## Crimscript - The Macro Language
The macro language, called Crimscript, is designed to be more human-readable and easier to write than Brainfuck. It includes commands for common operations, such as moving the data pointer, incrementing and decrementing values, and input/output operations. The compiler translates Crimscript code into Brainfuck code, which can then be executed by the interpreter.

The name "Crimscript" is inspired by the Crimson Badlands in Stardew Valley Expanded, as the Crimson Badlands are chaotic, reflective in Brainfuck's chaotic nature.

## Crimscript Syntax

### Punctuation
- `;`: Statement terminator. Not compulsory, unless to separate two instructions on the same line.
- `\`: Line continuation character. If a line ends with `\`, the next line is considered a continuation of the current line, allowing for multi-line statements.
- Braces `{}`: Used to define blocks of code, such as the body of loops.
- Indentation is **not** required, but improves readability. The compiler ignores all whitespace, including newlines and indentation.

### Condensed Operations
- `>`, `<`: Move the data pointer right or left.
- `+`, `-`: Increment or decrement the value at the data pointer.
- `>n`, `<n`: Move the data pointer right or left by n positions.
- `+n`, `-n`: Increment or decrement the value at the data pointer by

### Builtins
- `print()`: Output the value at the data pointer as a character.
- `print(s: str)`: For each character in the string `s`, clear the current cell, increment it up to the ASCII value of the character, print it, and then clear the cell again.
- `input(p: str = '')`: Print the prompt string `p`, then input one character and store it at the data pointer. If `p` is not given, no prompt is printed.
- `clear()`: Clear the value at the data pointer (set it to zero). Compiles to `[-]`.
- `exit(n: int = 0)`: Exit the program with status code `n`. If `n` is not given, exit with status code 0. If `n` is >255 or <0, it will be reduced % 256.
- `set(n: int)`: Set the value at the data pointer to `n`. Compiles to `[-]` followed by `+` repeated `n` times.

### Loops
```
until N {
    // code to repeat until the value at the data pointer is equal to N
}
```

### Comments
- `//`: Single-line comments. Everything after `//` on the same line is ignored by the compiler.
- `/* ... */`: Block comments. Everything between `/*` and `*/` is ignored by the compiler.

# Licence

Licensed under Apache License 2.0. See LICENCE for more details.
