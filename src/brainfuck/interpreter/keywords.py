from enum import StrEnum


class BrainfuckKeywords(StrEnum):
    STDOUT = '.'
    STDIN = ','
    LOOP_START = '['
    LOOP_END = ']'
    VAL_INC = '+'
    VAL_DEC = '-'
    PTR_INC = '>'
    PTR_DEC = '<'
