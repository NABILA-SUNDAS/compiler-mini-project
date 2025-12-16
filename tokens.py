from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    # Single-char
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    BANG = auto()
    EQUAL = auto()
    LT = auto()
    GT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMI = auto()
    COMMA = auto()

    # Two-char
    EQEQ = auto()
    NEQ = auto()
    LTE = auto()
    GTE = auto()

    # Literals/Identifiers
    IDENT = auto()
    NUMBER = auto()

    # Keywords
    START = auto()
    END = auto()
    INT = auto()
    FLOAT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    PRINT = auto()

    EOF = auto()

KEYWORDS = {
    'start': TokenType.START,
    'end': TokenType.END,
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'print': TokenType.PRINT,
}

@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: object
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.lexeme!r}, {self.literal}, {self.line}:{self.col})"
