from typing import Dict, List, Tuple, Any

from .ast_nodes import *          # Program, Stmt, Expr, etc.
from .semantic import type_of_literal, unify_types
from .errors import RuntimeErrorMC


class VM:
    def __init__(self, program):
        self.program = program

    def execute(self, tac):
        """Execute the three-address code."""
        pass
        # har scope ek dict: name -> (type_name, value)
        self.scopes: List[Dict[str, Tuple[str, Any]]] = [dict()]

    # ---------- Public entry ----------

    def run(self) -> None:
        for st in self.program.statements:
            self._exec_stmt(st)

    # ---------- Scope helpers ----------

    def _current_scope(self) -> Dict[str, Tuple[str, Any]]:
        return self.scopes[-1]

    def _declare(self, name: str, type_name: str, value: Any) -> None:
        scope = self._current_scope()
        if name in scope:
            raise RuntimeErrorMC(f"Duplicate declaration of '{name}'")
        scope[name] = (type_name, value)

    def _resolve(self, name: str) -> Tuple[str, Any]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise RuntimeErrorMC(f"Undeclared variable '{name}'")

    def _assign(self, name: str, type_name: str, value: Any) -> None:
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = (type_name, value)
                return
        raise RuntimeErrorMC(f"Undeclared variable '{name}'")

    # ---------- Statement execution ----------

    def _exec_block(self, blk: Block) -> None:
        self.scopes.append({})
        try:
            for s in blk.statements:
                self._exec_stmt(s)
        finally:
            self.scopes.pop()

    def _exec_stmt(self, st: Stmt) -> None:
        if isinstance(st, VarDecl):
            if st.init is not None:
                t, v = self._eval_expr(st.init)
                if st.type_name == 'int' and t != 'int':
                    raise RuntimeErrorMC(
                        f"Type error: cannot assign {t} to int {st.name}"
                    )
                v = int(v) if st.type_name == 'int' else float(v)
                self._declare(st.name, st.type_name, v)
            else:
                # default value
                default = 0 if st.type_name == 'int' else 0.0
                self._declare(st.name, st.type_name, default)

        elif isinstance(st, Assign):
            t, v = self._eval_expr(st.value)
            tt, _oldv = self._resolve(st.name)
            if tt == 'int' and t != 'int':
                raise RuntimeErrorMC(
                    f"Type error: cannot assign {t} to int {st.name}"
                )
            v = int(v) if tt == 'int' else float(v)
            self._assign(st.name, tt, v)

        elif isinstance(st, Print):
            _t, v = self._eval_expr(st.expr)
            print(v)

        elif isinstance(st, Block):
            self._exec_block(st)

        elif isinstance(st, If):
            _t, cond_val = self._eval_expr(st.cond)
            if cond_val:
                self._exec_stmt(st.then_branch)
            elif st.else_branch:
                self._exec_stmt(st.else_branch)

        elif isinstance(st, While):
            while True:
                _t, cond_val = self._eval_expr(st.cond)
                if not cond_val:
                    break
                self._exec_stmt(st.body)

        else:
            raise RuntimeErrorMC("Unknown statement type")

    # ---------- Expression evaluation ----------

    def _eval_expr(self, e: Expr) -> Tuple[str, Any]:
        if isinstance(e, Literal):
            t = type_of_literal(e.value)
            return t, e.value

        if isinstance(e, Var):
            return self._resolve(e.name)

        if isinstance(e, Unary):
            t, v = self._eval_expr(e.right)
            if e.op == '-':
                return t, -v
            if e.op == '+':
                return t, +v
            if e.op == '!':
                # boolean as int 0/1
                return 'int', 0 if not v else 1
            raise RuntimeErrorMC(f"Unknown unary operator {e.op}")

        if isinstance(e, Binary):
            lt, lv = self._eval_expr(e.left)
            rt, rv = self._eval_expr(e.right)

            if e.op in ['+', '-', '*', '/']:
                t = unify_types(lt, rt)
                if t == 'float':
                    lv = float(lv)
                    rv = float(rv)
                else:
                    lv = int(lv)
                    rv = int(rv)

                if e.op == '+':
                    return t, lv + rv
                if e.op == '-':
                    return t, lv - rv
                if e.op == '*':
                    return t, lv * rv
                if e.op == '/':
                    return 'float', lv / rv

            if e.op in ['==', '!=', '<', '<=', '>', '>=']:
                if e.op == '==':
                    return 'int', 1 if lv == rv else 0
                if e.op == '!=':
                    return 'int', 1 if lv != rv else 0
                if e.op == '<':
                    return 'int', 1 if lv < rv else 0
                if e.op == '<=':
                    return 'int', 1 if lv <= rv else 0
                if e.op == '>':
                    return 'int', 1 if lv > rv else 0
                if e.op == '>=':
                    return 'int', 1 if lv >= rv else 0

            raise RuntimeErrorMC(f"Unknown binary operator {e.op}")

        raise RuntimeErrorMC("Unknown expression type")
