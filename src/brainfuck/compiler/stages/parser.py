from __future__ import annotations

from typing import Callable, TypeAlias

from ..ast import nodes
from ..ast.nodes import AbstractSyntaxTree, ASTNode
from ..crim_tokens import CrimTokenType, Token
from ..exceptions import CompilerDepthError, CompilerSyntaxError, CompilerTypeError

_ParseCallable: TypeAlias = Callable[["Parser"], ASTNode]

class Parser:
    """Converts Crimscript tokens into AST (Abstract Syntax Tree) nodes.
    The second stage. """
    PARSE_REGISTRY: dict[CrimTokenType, _ParseCallable] = {}

    @classmethod
    def register(cls, *types: CrimTokenType):
        def wrapper(fn: Callable[[Parser], ASTNode]) -> _ParseCallable:

            for typ in types:
                cls.PARSE_REGISTRY[typ] = fn

            # Give back the function so the Parser can still use it!
            return fn
        return wrapper

    def peek(self) -> Token:
        """Return the current token without consuming ("eating") it."""
        if self.eof():
            raise CompilerSyntaxError("Unexpected EOF in input", pos=-1, src_code=self.src_code)
        return self.tokens[self.token_pos]

    def advance(self) -> Token:
        """Eats and returns the current token before moving to the next one."""
        token = self.peek()
        self.token_pos += 1
        return token

    def expect(self, expected_type: CrimTokenType) -> Token:
        """Consume a token and verify it matches the expected type."""
        token = self.peek()
        if token.typ != expected_type:
            assert token.metadata is not None
            raise CompilerSyntaxError(f"Expected {expected_type} but got {token.typ}", token.metadata.pos, self.src_code)
        return self.advance()

    def eof(self) -> bool:
        """Return True when the parser has consumed all tokens."""
        return self.token_pos >= len(self.tokens)

    def parse_macro_args(self: Parser) -> tuple[Token, ...]:
        """Parse a comma-separated list of macro arguments inside parentheses.
        So far, the only supported types are ints or strings."""
        if self.peek().typ == CrimTokenType.BRACKET_R:
            return ()

        args: list[Token] = []

        while True:
            # Parse each arg one at a time
            token = self.peek()
            if token.typ in (CrimTokenType.VAL_INC, CrimTokenType.VAL_DEC):
                token = self.advance()
                if not isinstance(token.val, int):
                    assert token.metadata is not None
                    raise CompilerTypeError(f"Invalid macro argument used with value delta: {token}", token.metadata.pos, self.src_code)

                # Cast the token to an integer token if it is being used in the context of a macro argument
                args.append(Token(CrimTokenType.INTEGER, token.val if token.typ == CrimTokenType.VAL_INC else -token.val, token.metadata))
            elif token.typ in (CrimTokenType.STRING, CrimTokenType.INTEGER):
                token = self.advance()
                if not isinstance(token.val, int) or isinstance(token.val, str):
                    assert token.metadata is not None
                    raise CompilerTypeError(f"Invalid macro argument: {token}", token.metadata.pos, self.src_code)
                args.append(token)
            else:
                assert token.metadata is not None
                raise CompilerTypeError(f"Invalid macro argument: {token}", token.metadata.pos, self.src_code)

            if self.peek().typ == CrimTokenType.COMMA:
                self.advance()
                continue
            break

        return tuple(args)

    def parse_statement(self) -> ASTNode:
        """Parse the next top-level Crimscript statement
        from the token stream, without consuming it.
        If multiple tokens were "eaten", it doesn't eat the last one."""
        token = self.peek()
        try:
            return self.PARSE_REGISTRY[token.typ](self)
        except KeyError:
            assert token.metadata is not None
            raise CompilerSyntaxError(f"Unexpected token type: {token.typ}", pos=token.metadata.pos, src_code=self.src_code)
        except RecursionError:
            assert token.metadata is not None
            raise CompilerDepthError("Control structure is too deeply nested", pos=token.metadata.pos, src_code=self.src_code)

    def parse(self, tokens: list[Token], src_code: list[str]) -> AbstractSyntaxTree:
        """Parse a list of tokens into an AST (Abstract Syntax Tree),
        which internally is just a list of ASTNode objects.
        You can imagine that it "eats" the tokens."""

        self.tokens = tokens
        self.token_pos: int = 0
        self.src_code: list[str] = src_code
        ast: AbstractSyntaxTree = []

        while not self.eof():
            if self.peek().typ == CrimTokenType.TERMINATOR:
                self.advance()
                continue

            ast.append(self.parse_statement())
            while not self.eof() and self.peek().typ == CrimTokenType.TERMINATOR:
                self.advance()

        return ast

@Parser.register(CrimTokenType.VAL_INC, CrimTokenType.VAL_DEC)
def parse_value_change(self: Parser) -> nodes.ValueChange:
    token = self.advance()
    if not isinstance(token.val, int):
        assert token.metadata is not None
        raise CompilerTypeError("Value change token must include an integer count", pos=token.metadata.pos, src_code=self.src_code)

    amount = token.val if token.typ == CrimTokenType.VAL_INC else -token.val

    assert token.metadata is not None
    return nodes.ValueChange(amount=amount, metadata=token.metadata)

@Parser.register(CrimTokenType.PTR_INC, CrimTokenType.PTR_DEC)
def parse_ptr_change(self: Parser) -> nodes.PointerChange:
    """Parse a numeric pointer movement instruction."""
    token = self.advance()
    if not isinstance(token.val, int):
        assert token.metadata is not None
        raise CompilerTypeError("Pointer change token must include an integer distance", pos=token.metadata.pos, src_code=self.src_code)

    distance = token.val if token.typ == CrimTokenType.PTR_INC else -token.val

    assert token.metadata is not None
    return nodes.PointerChange(distance=distance, metadata=token.metadata)

@Parser.register(CrimTokenType.PRINT)
def parse_print(self: Parser) -> nodes.PrintStmt:
    """Parse a print() statement, optionally with a string argument."""

    start_token = self.expect(CrimTokenType.PRINT)
    self.expect(CrimTokenType.BRACKET_L)

    text: str | None = None
    if self.peek().typ == CrimTokenType.STRING:
        str_token = self.advance()
        assert isinstance(str_token.val, str) or str_token.val is None
        text = str_token.val

    self.expect(CrimTokenType.BRACKET_R)

    assert start_token.metadata is not None
    return nodes.PrintStmt(text=text, metadata=start_token.metadata)

@Parser.register(CrimTokenType.INPUT)
def parse_input(self: Parser) -> nodes.InputStmt:
    """Parse an input() statement, optionally with a prompt string."""
    start_token = self.expect(CrimTokenType.INPUT)
    self.expect(CrimTokenType.BRACKET_L)

    prompt: str | None = None
    if self.peek().typ == CrimTokenType.STRING:
        advance = self.advance()
        assert isinstance(advance.val, str) or advance.val is None
        prompt = advance.val

    self.expect(CrimTokenType.BRACKET_R)

    assert start_token.metadata is not None
    return nodes.InputStmt(prompt=prompt, metadata=start_token.metadata)

@Parser.register(CrimTokenType.CLEAR)
def parse_clear(self: Parser) -> nodes.ClearStmt:
    """Parse a clear() statement, which clears the current data cell."""
    start_token = self.expect(CrimTokenType.CLEAR)
    self.expect(CrimTokenType.BRACKET_L)
    self.expect(CrimTokenType.BRACKET_R)

    assert start_token.metadata is not None
    return nodes.ClearStmt(metadata=start_token.metadata)

@Parser.register(CrimTokenType.SET)
def parse_set(self: Parser) -> nodes.SetStmt:
    """Parse a set(n) statement and validate that its argument is an integer."""
    start_token = self.expect(CrimTokenType.SET)
    self.expect(CrimTokenType.BRACKET_L)

    if (bad_token := self.peek()).typ != CrimTokenType.INTEGER:
        assert bad_token.metadata is not None
        raise CompilerTypeError("set() requires an integer argument", bad_token.metadata.pos, self.src_code)

    token = self.advance()
    self.expect(CrimTokenType.BRACKET_R)

    if not isinstance(token.val, int):
        assert token.metadata is not None
        raise CompilerTypeError(f"set() argument must be an integer, got {token.val}", token.metadata.pos, self.src_code)

    assert start_token.metadata is not None
    return nodes.SetStmt(value=token.val, metadata=start_token.metadata)

@Parser.register(CrimTokenType.UNTIL)
def parse_until(self: Parser) -> nodes.UntilStmt:
    """Parse an until N { ... } loop and its nested statement body."""
    start_token = self.expect(CrimTokenType.UNTIL)

    if (bad_token := self.peek()).typ != CrimTokenType.INTEGER:
        assert bad_token.metadata is not None
        raise CompilerTypeError("until target must be an integer", bad_token.metadata.pos, self.src_code)

    target = (token := self.advance()).val
    if not isinstance(target, int):
        assert token.metadata is not None
        raise CompilerTypeError("until target must be an integer", token.metadata.pos, self.src_code)

    self.expect(CrimTokenType.BRACE_L)
    body: list[ASTNode] = []

    while not self.eof() and self.peek().typ != CrimTokenType.BRACE_R:
        if self.peek().typ == CrimTokenType.TERMINATOR:
            self.advance()
            continue
        body.append(self.parse_statement())
        while not self.eof() and self.peek().typ == CrimTokenType.TERMINATOR:
            self.advance()

    self.expect(CrimTokenType.BRACE_R)

    assert start_token.metadata is not None
    return nodes.UntilStmt(target=target, body=body, metadata=start_token.metadata)

@Parser.register(CrimTokenType.MOVE)
def parse_move(self: Parser) -> nodes.MoveStmt:
    """Parse an mv() call, using either mv(dest) or mv(destmin, destmax)."""
    start_token = self.expect(CrimTokenType.MOVE)
    self.expect(CrimTokenType.BRACKET_L)

    args = self.parse_macro_args()
    self.expect(CrimTokenType.BRACKET_R)

    if len(args) == 1:
        start = args[0]
        if not isinstance(start, int):
            assert start.metadata is not None
            raise CompilerTypeError(f"invalid argument: not an integer: {start}", start.metadata.pos, self.src_code)
        end = start
    elif len(args) == 2:
        start, end = args
        if not isinstance(start, int):
            assert start.metadata is not None
            raise CompilerTypeError(f"invalid argument: not an integer: {start}", start.metadata.pos, self.src_code)
        if not isinstance(end, int):
            assert end.metadata is not None
            raise CompilerTypeError(f"invalid argument: not an integer: {end}", end.metadata.pos, self.src_code)
    else:
        assert start_token.metadata is not None
        raise CompilerTypeError(f"mv() requires mv(dest) or mv(destmin, destmax), expected 1 or 2 args but received {len(args)}", start_token.metadata.pos, self.src_code)

    assert start_token.metadata is not None
    return nodes.MoveStmt(delta_ptr_min=min(start, end), delta_ptr_max=max(start, end), metadata=start_token.metadata)

@Parser.register(CrimTokenType.COPY)
def parse_copy(self: Parser) -> nodes.CopyStmt:
    """Parse a cp() call with either cp(dest, tmp) or cp(destmin, destmax, tmp)."""
    start_token = self.expect(CrimTokenType.COPY)
    metadata = start_token.metadata
    assert metadata is not None

    self.expect(CrimTokenType.BRACKET_L)

    args = self.parse_macro_args()
    self.expect(CrimTokenType.BRACKET_R)

    if len(args) == 2:
        dest, tmp = args

        if not isinstance(dest, int):
            assert dest.metadata is not None
            raise CompilerTypeError(f"invalid argument: not an integer: {dest}", pos=dest.metadata.pos, src_code=self.src_code)
        if not isinstance(tmp, int):
            assert tmp.metadata is not None
            raise CompilerTypeError(f"invalid argument: not an integer: {tmp}", pos=tmp.metadata.pos, src_code=self.src_code)

        return nodes.CopyStmt(delta_ptr_min=dest, delta_ptr_max=dest, delta_ptr_tmp=tmp, metadata=metadata)
    if len(args) == 3:
        destmin, destmax, tmp = args

        if not isinstance(destmin, int):
            assert destmin.metadata is not None
            raise CompilerTypeError(f"invalid argument: not an integer: {destmin}", pos=destmin.metadata.pos, src_code=self.src_code)
        if not isinstance(destmax, int):
            assert destmax.metadata is not None
            raise CompilerTypeError(f"invalid argument: not an integer: {destmax}", pos=destmax.metadata.pos, src_code=self.src_code)
        if not isinstance(tmp, int):
            assert tmp.metadata is not None
            raise CompilerTypeError(f"invalid argument: not an integer: {tmp}", pos=tmp.metadata.pos, src_code=self.src_code)

        return nodes.CopyStmt(delta_ptr_min=min(destmin, destmax), delta_ptr_max=max(destmin, destmax), delta_ptr_tmp=tmp, metadata=metadata)

    assert start_token.metadata is not None
    raise CompilerTypeError(f"cp() requires cp(dest, tmp) or cp(destmin, destmax, tmp), expected 2 or 3 args but received {len(args)}", start_token.metadata.pos, self.src_code)
