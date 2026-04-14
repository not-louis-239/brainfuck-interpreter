# Example of Conditions in Crimscript

```js

// let's say for example we want to check if the cell is a 1 (ASCII 49)

// first, read some user input and assign it to the memory cell
input()

// first, subtract 49 from the input because "1" = ASCII 49
-49

// then, set the "is_1" flag in the adjacent right cell
>+<

until 0 {
    // If we get here, it means that the value at the current cell is not zero (i.e., it's not a "1" (ASCII 49))

    // clear the "is_1" flag
    >; clear()

    // then, destroy the input to break the loop
    <; clear()
}

// If it is zero, the "is_1" flag is still there
// Now we can run some logic on that

// The following loop will run if the flag is 1, but will be skipped if it is 0
>  // move to the cell containing the flag first
until 0 {
    >; print("The input was a 1!"); <  // mem offset to avoid tampering
    clear()  // finally, destroy the flag to exit the loop
}

```
