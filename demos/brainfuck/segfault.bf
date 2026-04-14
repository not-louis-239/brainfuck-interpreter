this will trigger a brainfuck segmentation fault if not run with wrap mode
if wrap mode is enabled then nothing will happen

ptr starts at 0 initially so moving left is invalid
>>>,

<<<<<<<<  the 4th 'move left' instruction will move to memory address negative 1 which is invalid
