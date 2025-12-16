# src/semantic.py

from dataclasses import dataclass
from typing import Dict, Optional
from .ast_nodes import *
from .errors import SemanticError


@dataclass
class Symbol:
    name: str
    type_name: str  # 'int' or 'float'


class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self.parent = parent
        self.table: Dict[str, Symbol] = {}

    def declare(self, name: str, type_name: str):
        if name in self.table:
            raise SemanticError(f"Duplicate declaration of '{name}'")
        self.table[name] = Symbol(name, type_name)

    def resolve(self, name: str) -> Symbol:
        if name in self.table:
            return self.table[name]
        if self.parent:
            return self.parent.resolve(name)
        raise SemanticError(f"Undeclared variable '{name}'")


def type_of_literal(value):
    return 'float' if isinstance(value, float) else 'int'


def unify_types(t1: str, t2: str) -> str:
    # arithmetic promotion: float dominates
    if t1 == 'float' or t2 == 'float':
        return 'float'
    return 'int'


class SemanticAnalyzer:
    """
    Proper semantic analyzer class.
    main.py yehi naam import karta hai.
    """

    def __init__(self):
        # future me yahan symbol-table waghera rakh sakti ho
        pass

    def analyze(self, program: Program):
        """Entry point from main.py"""
        self._check_program(program, Scope())

    # -----------------------------
    # Program / Block helpers
    # -----------------------------
    def _check_program(self, prog: Program, scope: Scope):
        for st in prog.statements:
            self._check_stmt(st, scope)

    def _check_block(self, blk: Block, scope: Scope):
        # each block gets its own inner scope
        inner = Scope(scope)
        for st in blk.statements:
            self._check_stmt(st, inner)

    # -----------------------------
    # Statements
    # -----------------------------
    def _check_stmt(self, st: Stmt, scope: Scope):
        if isinstance(st, VarDecl):
            scope.declare(st.name, st.type_name)
            if st.init is not None:
                t = self._check_expr(st.init, scope)
                # assignment compatibility: int <- int; float <- int|float
                if st.type_name == 'int' and t != 'int':
                    raise SemanticError(f"Cannot assign {t} to int '{st.name}'")

        elif isinstance(st, Assign):
            sym = scope.resolve(st.name)
            t = self._check_expr(st.value, scope)
            if sym.type_name == 'int' and t != 'int':
                raise SemanticError(f"Cannot assign {t} to int '{st.name}'")

        elif isinstance(st, Print):
            self._check_expr(st.expr, scope)

        elif isinstance(st, If):
            # condition
            self._check_expr(st.cond, scope)

            # then branch
            if isinstance(st.then_branch, Block):
                self._check_block(st.then_branch, scope)
            else:
                self._check_stmt(st.then_branch, scope)

            # else branch (optional)
            if st.else_branch:
                if isinstance(st.else_branch, Block):
                    self._check_block(st.else_branch, scope)
                else:
                    self._check_stmt(st.else_branch, scope)

        elif isinstance(st, While):
            # condition
            self._check_expr(st.cond, scope)

            # loop body
            if isinstance(st.body, Block):
                self._check_block(st.body, scope)
            else:
                self._check_stmt(st.body, scope)

        elif isinstance(st, Block):
            self._check_block(st, scope)

        else:
            raise SemanticError("Unknown statement type")

    # -----------------------------
    # Expressions
    # -----------------------------
    def _check_expr(self, e: Expr, scope: Scope) -> str:
        if isinstance(e, Literal):
            return type_of_literal(e.value)

        if isinstance(e, Var):
            sym = scope.resolve(e.name)
            return sym.type_name

        if isinstance(e, Unary):
            t = self._check_expr(e.right, scope)
            # unary + - preserve type; ! returns int (0/1) for simplicity
            if e.op == '!':
                return 'int'
            return t

        if isinstance(e, Binary):
            lt = self._check_expr(e.left, scope)
            rt = self._check_expr(e.right, scope)

            if e.op in ['+', '-', '*', '/']:
                return unify_types(lt, rt)

            # comparisons produce int (boolean)
            if e.op in ['==', '!=', '<', '<=', '>', '>=']:
                return 'int'

        raise SemanticError("Unknown expression type")
