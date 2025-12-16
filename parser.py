from typing import List
from .tokens import TokenType as TT, Token
from .errors import ParseError
from .ast_nodes import *

OP_MAP = {
    TT.PLUS: '+', TT.MINUS: '-', TT.STAR: '*', TT.SLASH: '/',
    TT.EQEQ: '==', TT.NEQ: '!=', TT.LT: '<', TT.LTE: '<=',
    TT.GT: '>', TT.GTE: '>=',
    TT.EQUAL: '=', TT.BANG: '!'
}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0

    def parse(self) -> Program:
        # program -> 'start' stmt_list 'end'
        self._consume(TT.START, "'start' expected at program start")
        stmts = self._stmt_list()
        self._consume(TT.END, "'end' expected at program end")
        # Yahan pehle strict EOF check tha; newline / extra space pe error aa raha tha
        # self._consume(TT.EOF, "trailing tokens after 'end'")
        return Program(stmts)

    # -------------------------------------------------
    # Statements
    # -------------------------------------------------
    def _stmt_list(self) -> List[Stmt]:
        stmts = []
        while (
            not self._check(TT.END)
            and not self._check(TT.RBRACE)
            and not self._is_at_end()
        ):
            stmts.append(self._stmt())
        return stmts

    def _stmt(self) -> Stmt:
        # int declaration
        if self._match(TT.INT):
            name = self._consume(TT.IDENT, "identifier expected after 'int'")
            init = None
            if self._match(TT.EQUAL):
                init = self._expr()
            self._consume(TT.SEMI, "; expected after declaration")
            return VarDecl('int', name.lexeme, init)

        # float declaration
        if self._match(TT.FLOAT):
            name = self._consume(TT.IDENT, "identifier expected after 'float'")
            init = None
            if self._match(TT.EQUAL):
                init = self._expr()
            self._consume(TT.SEMI, "; expected after declaration")
            return VarDecl('float', name.lexeme, init)

        # print(x);
        if self._match(TT.PRINT):
            self._consume(TT.LPAREN, "( expected after 'print'")
            e = self._expr()
            self._consume(TT.RPAREN, ") expected after print expr")
            self._consume(TT.SEMI, "; expected after print")
            return Print(e)

        # if (...) stmt [else stmt]
        if self._match(TT.IF):
            self._consume(TT.LPAREN, "( after 'if'")
            cond = self._expr()
            self._consume(TT.RPAREN, ") after if condition")
            thenb = self._stmt()
            elseb = None
            if self._match(TT.ELSE):
                elseb = self._stmt()
            return If(cond, thenb, elseb)

        # while (...) stmt
        if self._match(TT.WHILE):
            self._consume(TT.LPAREN, "( after 'while'")
            cond = self._expr()
            self._consume(TT.RPAREN, ") after while condition")
            body = self._stmt()
            return While(cond, body)

        # { ... }
        if self._match(TT.LBRACE):
            stmts = self._stmt_list()
            self._consume(TT.RBRACE, "} to close block")
            return Block(stmts)

        # assignment: IDENT = expr;
        if self._check(TT.IDENT) and self._check_next(TT.EQUAL):
            name = self._advance().lexeme      # IDENT
            self._advance()                    # '='
            e = self._expr()
            self._consume(TT.SEMI, "; expected after assignment")
            return Assign(name, e)

        raise ParseError(
            f"Unexpected token {self._peek().type.name} at "
            f"{self._peek().line}:{self._peek().col}"
        )

    # -------------------------------------------------
    # Expressions
    # -------------------------------------------------
    def _expr(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match(TT.EQEQ, TT.NEQ):
            op = OP_MAP[self._previous().type]
            right = self._comparison()
            expr = Binary(expr, op, right)
        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(TT.LT, TT.LTE, TT.GT, TT.GTE):
            op = OP_MAP[self._previous().type]
            right = self._term()
            expr = Binary(expr, op, right)
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(TT.PLUS, TT.MINUS):
            op = OP_MAP[self._previous().type]
            right = self._factor()
            expr = Binary(expr, op, right)
        return expr

    def _factor(self) -> Expr:
        expr = self._unary()
        while self._match(TT.STAR, TT.SLASH):
            op = OP_MAP[self._previous().type]
            right = self._unary()
            expr = Binary(expr, op, right)
        return expr

    def _unary(self) -> Expr:
        if self._match(TT.BANG, TT.MINUS, TT.PLUS):
            op = OP_MAP[self._previous().type]
            right = self._unary()
            return Unary(op, right)
        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TT.NUMBER):
            return Literal(self._previous().literal)
        if self._match(TT.IDENT):
            return Var(self._previous().lexeme)
        if self._match(TT.LPAREN):
            e = self._expr()
            self._consume(TT.RPAREN, ") expected after expression")
            return e
        t = self._peek()
        raise ParseError(
            f"Expected expression at {t.line}:{t.col}, got {t.type.name}"
        )

    # -------------------------------------------------
    # Utilities
    # -------------------------------------------------
    def _match(self, *types):
        for tp in types:
            if self._check(tp):
                self._advance()
                return True
        return False

    def _consume(self, type_, msg):
        if self._check(type_):
            return self._advance()
        t = self._peek()
        raise ParseError(f"{msg} (found {t.type.name} at {t.line}:{t.col})")

    def _check(self, type_):
        if self._is_at_end():
            return False
        return self._peek().type == type_

    def _check_next(self, type_):
        if self.i + 1 >= len(self.tokens):
            return False
        return self.tokens[self.i + 1].type == type_

    def _advance(self):
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def _previous(self):
        return self.tokens[self.i - 1]

    def _peek(self):
        return self.tokens[self.i]

    def _is_at_end(self):
        # Safe EOF check
        return self.i >= len(self.tokens) or self.tokens[self.i].type == TT.EOF
