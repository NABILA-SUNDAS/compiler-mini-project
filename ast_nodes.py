from dataclasses import dataclass
from typing import List, Optional

# Expressions
class Expr: ...
@dataclass
class Literal(Expr):
    value: object

@dataclass
class Var(Expr):
    name: str

@dataclass
class Unary(Expr):
    op: str
    right: Expr

@dataclass
class Binary(Expr):
    left: Expr
    op: str
    right: Expr

# Statements
class Stmt: ...
@dataclass
class VarDecl(Stmt):
    type_name: str  # 'int' or 'float'
    name: str
    init: Optional[Expr]

@dataclass
class Assign(Stmt):
    name: str
    value: Expr

@dataclass
class Print(Stmt):
    expr: Expr

@dataclass
class Block(Stmt):
    statements: List[Stmt]

@dataclass
class If(Stmt):
    cond: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]

@dataclass
class While(Stmt):
    cond: Expr
    body: Stmt

@dataclass
class Program:
    statements: List[Stmt]
