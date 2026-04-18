# Brainfuck Interpreter and Macrolang Compiler

## Out of the Box
This program includes
- a Brainfuck interpreter, and
- a compiler for a simple macro language that compiles to Brainfuck, with an option for debug symbols.
- a debugger for said macro language, which shows a stack trace when the program crashes.

## Crimscript – The Macro Language
The macro language, called Crimscript, is designed to be more human-readable and easier to write than Brainfuck. It includes commands for common operations, such as moving the data pointer, incrementing and decrementing values, and input/output operations. The compiler translates Crimscript code into Brainfuck code, which can then be executed by the interpreter.

## Crimscript Syntax

### Punctuation
- `;`: Statement terminator. Not compulsory, unless to separate multiple instructions on the same line.
- `\`: Line continuation character. If a line ends with `\`, the next line is considered a continuation of the current line, allowing for multi-line statements.
- Braces `{}`: Used to define blocks of code, such as the body of loops.
- Indentation is **not** required, but improves readability. The compiler ignores all whitespace, including newlines and indentation.

### Condensed Operations
- `>`, `<`: Move the data pointer right or left.
- `+`, `-`: Increment or decrement the value at the data pointer.
- `>n`, `<n`: Move the data pointer right or left by `n` positions.
- `+n`, `-n`: Increment or decrement the value at the data pointer by `n`.

### Builtins
- `print()`: Output the value at the data pointer as a character.
- `print(s: str)`: Clear the cell, then for each character in the string `s`, adjust it to the ASCII value of the character, print it, and then clear the cell again.
- `input(p: str = '')`: Print the prompt string `p`, then input one character and store it at the data pointer. If `p` is not given, no prompt is printed.
- `clear()`: Clear the value at the data pointer (set it to zero). Compiles to `[-]`.
- `set(n: int)`: Set the value at the data pointer to `n`. Compiles to `[-]` followed by `+` repeated `n` times, or `-`, repeated `256 - n` times.
- `mv(n: int)`: Move the value at the data pointer to `n` positions left or right. Destroys the original `src` cell. The pointer will end back where it started.
- `mv(destmin: int, destmax: int)`: Distribute the value at the data pointer to all the cells from `destmin` to `destmax` relative to the pointer. Destroys the value at the pointer. Pointer ends where it started.
- `cp(dest: int, tmp: int)`: Copy the value at the data pointer to `dest`, using `tmp` as a temporary cell. Does not destroy the value at the data pointer. The pointer ends where it started.
- `cp(destmin: int, destmax: int, tmp: int)`: Distribute the value at the data pointer to all cells from `destmin` to `destmax` relative to the pointer. Uses `tmp` as a temporary cell during copy and clobbers it. The pointer ends where it started. Does not destroy the original value at the pointer.

#### Notes
- In all `mv` and `cp` macros:
  - The implied `src` cell (0) cannot be inside the destination range (i.e., it cannot be at `destmin`, `destmax`, or any cell in between).
  - The `tmp` cell cannot be inside the destination range.
  - The implied `src` cell cannot be used as the `tmp` cell (for `cp` operations)
  - The destination range must be valid (i.e., `destmin <= destmax`).
- In all `print` and `input` macro usages:
  - Only ASCII characters or characters where `ord(character) <= 255` are allowed.

### Loops
```js
until N {
    // code to repeat until the value at the data pointer is equal to N
}
```

`until` compiles to:
```bf
---  # N '-'s to subtract the offset for checking
[
    +++  # undo offset inside loop

    # rest of loop code...

    ---  # subtract offset to check
]
+++  # N '+'s to undo the offset
```

The number of `+`'s and `-`'s used in an `until N` statement matches the value `N`. For example, for `until 3`, the compiler will generate 3 `+`s and 3 `-`s with which to pad the loop.

### Comments
- `//`: Single-line comments. Everything after `//` on the same line is ignored by the compiler.
- `/* ... */`: Block comments. Everything between `/*` and `*/` is ignored by the compiler.

## Requirements
- Python 3.14.0+ (tested on 3.14.0+, but older versions may or may not work as intended).
- See requirements.txt for further details.

## Licence
Licensed under Apache License 2.0. See LICENCE for more details.

## Footnote

### How was "Crimscript" decided?
The name "Crimscript" is inspired by the Crimson Badlands in Stardew Valley Expanded, as the Crimson Badlands are chaotic, reflective in Brainfuck's chaotic nature.

For the longest time, I have been coding pretty much exclusively in Python, but I wanted to try something different. A while ago I found out about Brainfuck, which is a notoriously difficult-to-read programming language. Experimenting with some Brainfuck coding I was getting increasingly frustrated with how difficult it was to code in raw BF. So I decided to make my own macro-language which I could then compile to Brainfuck to make BF development easier.

The way I thought about it was like this:
- Python is like the rich kid down the street with a massive mansion and a fridge full of snacks and soft drinks (functions and libraries).
- C is like owning your own house. You can get by, but you have to manage your own plumbing (memory) and electricity (pointers), and messing it up can explode the entire building.
- Assembly is like a small cabin in the woods where you must move all the sticks and twigs by hand. You have to manage everything yourself (registers), and the woods are not forgiving.
- Brainfuck is like the nomadic foragers out in the Badlands. You have only a few sticks and a rock, and you're always one bad pointer move away from a segfault.

I made this project as a way to learn about how compilers work and to have fun with my hobby in programming. I hope someone finds this interesting or useful!
