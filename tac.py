from typing import List, Tuple
from .ast_nodes import *


class TACGenerator:
   
    def __init__(self):
        pass
    def generate(self, program):
        self.code: List[Tuple] = []
        self.temp_id = 0
        self.label_id = 0

    def new_temp(self):
        self.temp_id += 1
        return f"t{self.temp_id}"

    def new_label(self, base='L'):
        self.label_id += 1
        return f"{base}{self.label_id}"

    def gen(self, prog: Program) -> List[Tuple]:
        for st in prog.statements:
            self._emit_stmt(st)
        return self.code

    def _emit_stmt(self, st: Stmt):
        if isinstance(st, VarDecl):
            if st.init is not None:
                rhs = self._emit_expr(st.init)
                self.code.append(('=', rhs, None, st.name))
            else:
                # declaration no-op for TAC
                pass
        elif isinstance(st, Assign):
            rhs = self._emit_expr(st.value)
            self.code.append(('=', rhs, None, st.name))
        elif isinstance(st, Print):
            v = self._emit_expr(st.expr)
            self.code.append(('print', v, None, None))
        elif isinstance(st, If):
            cond = self._emit_expr(st.cond)
            Ltrue = self.new_label('L')
            Lend = self.new_label('L')
            if st.else_branch:
                Lfalse = self.new_label('L')
                self.code.append(('if_goto', cond, None, Ltrue))
                self.code.append(('goto', None, None, Lfalse))
                self.code.append(('label', None, None, Ltrue))
                self._emit_stmt(st.then_branch)
                self.code.append(('goto', None, None, Lend))
                self.code.append(('label', None, None, Lfalse))
                self._emit_stmt(st.else_branch)
                self.code.append(('label', None, None, Lend))
            else:
                self.code.append(('if_goto', cond, None, Ltrue))
                self.code.append(('goto', None, None, Lend))
                self.code.append(('label', None, None, Ltrue))
                self._emit_stmt(st.then_branch)
                self.code.append(('label', None, None, Lend))
        elif isinstance(st, While):
            Lstart = self.new_label('L')
            Lbody = self.new_label('L')
            Lend = self.new_label('L')
            self.code.append(('label', None, None, Lstart))
            cond = self._emit_expr(st.cond)
            self.code.append(('if_goto', cond, None, Lbody))
            self.code.append(('goto', None, None, Lend))
            self.code.append(('label', None, None, Lbody))
            self._emit_stmt(st.body)
            self.code.append(('goto', None, None, Lstart))
            self.code.append(('label', None, None, Lend))
        elif isinstance(st, Block):
            for s in st.statements:
                self._emit_stmt(s)
        else:
            raise RuntimeError('Unknown statement')

    def _emit_expr(self, e: Expr):
        if isinstance(e, Literal):
            t = self.new_temp()
            self.code.append(('const', e.value, None, t))
            return t
        if isinstance(e, Var):
            return e.name
        if isinstance(e, Unary):
            v = self._emit_expr(e.right)
            t = self.new_temp()
            self.code.append((f'unary_{e.op}', v, None, t))
            return t
        if isinstance(e, Binary):
            l = self._emit_expr(e.left)
            r = self._emit_expr(e.right)
            t = self.new_temp()
            self.code.append((e.op, l, r, t))
            return t
        raise RuntimeError('Unknown expr')
