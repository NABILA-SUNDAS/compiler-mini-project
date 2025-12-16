import re
from .tokens import TokenType, Token, KEYWORDS
from .errors import LexError
from .tokens import Token, TokenType   # agar upar already import nahi to add karo

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.col = 1
        self.i = 0
        self.text = source
        self.tokens = []
    # tokens are initialized in __init__, no need for class-level assignment


    def scan_tokens(self):
        """Source se poori token list generate karta hai."""
        return self.lex()

    def lex(self):
        while not self._eof():
            c = self._peek()

            # whitespace
            if c in ' \t\r':
                self._advance()
                continue
            if c == '\n':
                self._advance_line()
                continue

            # comments
            if c == '/':
                if self._match('//'):
                    # line comment
                    while not self._eof() and self._peek() != '\n':
                        self._advance()
                    continue
                if self._match('/*'):
                    # block comment
                    while not self._eof() and not self._match('*/'):
                        ch = self._advance()
                        if ch == '\n':
                            self._advance_line(bump=False)
                    continue

            # two-char operators
            if self._match('=='):
                self._add(TokenType.EQEQ, '=='); continue
            if self._match('!='):
                self._add(TokenType.NEQ, '!='); continue
            if self._match('<='):
                self._add(TokenType.LTE, '<='); continue
            if self._match('>='):
                self._add(TokenType.GTE, '>='); continue

            # single-char tokens
            single = {
                '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.STAR, '/': TokenType.SLASH,
                '!': TokenType.BANG, '=': TokenType.EQUAL, '<': TokenType.LT, '>': TokenType.GT,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN, '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                ';': TokenType.SEMI, ',': TokenType.COMMA
            }
            if c in single:
                self._add(single[c], c)
                self._advance()
                continue

            # number
            if c.isdigit():
                self._number()
                continue

            # identifier/keyword
            if c.isalpha() or c == '_':
                self._ident()
                continue

            raise LexError(f"Unexpected character {c!r} at {self.line}:{self.col}")

        self.tokens.append(Token(TokenType.EOF, '', None, self.line, self.col))
        return self.tokens

    def _number(self):
        start = self.i
        line, col = self.line, self.col
        has_dot = False
        while not self._eof() and (self._peek().isdigit() or (self._peek()=='.' and not has_dot)):
            if self._peek()=='.':
                has_dot = True
            self._advance()
        lex = self.text[start:self.i]
        lit = float(lex) if '.' in lex else int(lex)
        from .tokens import TokenType as TT
        self.tokens.append(Token(TT.NUMBER, lex, lit, line, col))

    def _ident(self):
        start = self.i
        line, col = self.line, self.col
        while not self._eof() and (self._peek().isalnum() or self._peek()=='_'):
            self._advance()
        lex = self.text[start:self.i]
        ttype = KEYWORDS.get(lex, TokenType.IDENT)
        self.tokens.append(Token(ttype, lex, None, line, col))

    # helpers
    def _add(self, ttype, lexeme):
        self.tokens.append(Token(ttype, lexeme, None, self.line, self.col))

    def _peek(self):
        return self.text[self.i]

    def _advance(self):
        ch = self.text[self.i]
        self.i += 1
        self.col += 1
        return ch

    def _advance_line(self, bump=True):
        # move to next line
        self.i += 1
        if bump:
            self.line += 1
            self.col = 1

    def _match(self, s):
        if self.text[self.i:self.i+len(s)] == s:
            return True
        return False

    def _eof(self):
        return self.i >= len(self.text)
